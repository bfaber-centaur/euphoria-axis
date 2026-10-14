# =====================================================================
# 27B GPU benchmark battery: times one unit of each planned workload on this pod's GPU.
#   B0 load + fast-path check        B1 batched capture at block n-2 (M1/M3/M4/M5)
#   B2 steered greedy generation, 120 tokens, batch 1 (M6)
#   B3 button trial: 8-token sample + 2 name log-probs, chat prompt, steered (M7)
#   B4 lens readout: transport (CPU-held 5120x5120 fp16 matrix) + full-vocab ranks (M6 readouts)
#   B5 one lens-fit document with the published recipe (optional; BENCH_FIT=0 skips)
# Timings only: inputs are synthetic where content does not affect cost; generation lengths are forced.
#   usage: MODEL_PATH=/root/models/Qwen3.5-27B python bench_27b.py
# =====================================================================
import inspect, json, os, platform, sys, time
from pathlib import Path
import torch, transformers

MODEL_PATH = os.environ["MODEL_PATH"]
DO_FIT = os.environ.get("BENCH_FIT", "1") == "1"
OUT = Path("/workspace/bench"); OUT.mkdir(parents=True, exist_ok=True)
dev = "cuda"
R = {"gpu": torch.cuda.get_device_name(0), "gpu_mem_gib": torch.cuda.get_device_properties(0).total_memory / 2**30,
     "model": MODEL_PATH, "torch": torch.__version__, "transformers": transformers.__version__, "python": platform.python_version()}
sync = torch.cuda.synchronize
def peak():
    return torch.cuda.max_memory_allocated() / 2**30

# ---- B0 load + fast path -------------------------------------------------------------
t0 = time.time()
hf = transformers.AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.bfloat16).to(dev).eval()
tok = transformers.AutoTokenizer.from_pretrained(MODEL_PATH)
sync(); R["B0_load_s"] = time.time() - t0; R["B0_mem_after_load_gib"] = torch.cuda.memory_allocated() / 2**30
layers = next(m for m in hf.modules() if isinstance(m, torch.nn.ModuleList) and len(m) >= 32
              and hasattr(m[0], "mlp") and hasattr(m[0], "input_layernorm"))
n = len(layers); EXTRACT, INJECT = n - 2, n // 2
hidden = hf.get_input_embeddings().weight.shape[1]
calls = set()
def _prof(frame, event, arg):
    if event == "call" and any(k in frame.f_code.co_name for k in ("delta_rule", "conv1d")):
        calls.add(f"{frame.f_globals.get('__name__')}.{frame.f_code.co_name}")
ids = tok("hello world " * 20, return_tensors="pt").input_ids.to(dev)
sys.setprofile(_prof)
with torch.no_grad():
    hf(ids)
sys.setprofile(None)
R["fast_path"] = any(c.startswith(("fla", "causal_conv1d")) for c in calls) and not any("torch_" in c for c in calls)
R.update({"n_layers": n, "hidden": hidden, "extract_block": EXTRACT, "inject_block": INJECT})
print(f"B0 {R['gpu']}: load {R['B0_load_s']:.0f}s, {R['B0_mem_after_load_gib']:.1f} GiB, {n} layers, fast path {R['fast_path']}")
assert R["fast_path"], f"not on the fast path: {sorted(calls)}"

vec = torch.randn(hidden, device=dev, dtype=torch.bfloat16)
vec = vec / vec.norm() * 4.0                                   # timing only; the dose does not change the cost
def steer(on=True):
    if not on:
        return None
    return layers[INJECT].register_forward_hook(lambda m, i, o: (o[0] + vec, *o[1:]) if isinstance(o, tuple) else o + vec)

# ---- B1 batched capture --------------------------------------------------------------
sents = [f"On day {i} I put the receipts from the {['market', 'office', 'garage', 'station'][i % 4]} in the drawer, "
         f"checked the list twice, and closed the cabinet before dinner. I feel:" for i in range(72)]
tok.padding_side = "left"
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
cap = []
hcap = layers[EXTRACT].register_forward_hook(lambda m, i, o: cap.append((o[0] if isinstance(o, tuple) else o)[:, -1].float().cpu()))
def run_batches(S, bs=8):
    for k in range(0, len(S), bs):
        enc = tok(S[k:k + bs], return_tensors="pt", padding=True).to(dev)
        with torch.no_grad():
            hf(**enc)
run_batches(sents[:8]); sync(); cap.clear()
torch.cuda.reset_peak_memory_stats(); t0 = time.time()
run_batches(sents[8:]); sync()
R["B1_prompts_per_s"] = 64 / (time.time() - t0); R["B1_peak_gib"] = peak(); hcap.remove()
print(f"B1 capture: {R['B1_prompts_per_s']:.1f} prompts/s (batch 8)")

# ---- B2 steered greedy generation ----------------------------------------------------
def gen(prompt, n_new, sample=False):
    enc = tok(prompt, return_tensors="pt").to(dev)
    kw = dict(max_new_tokens=n_new, min_new_tokens=n_new, pad_token_id=tok.pad_token_id)
    kw.update(dict(do_sample=True, temperature=0.7, top_p=0.95) if sample else dict(do_sample=False))
    with torch.inference_mode():
        return hf.generate(**enc, **kw)
h = steer()
gen(sents[0], 16); sync()
torch.cuda.reset_peak_memory_stats(); t0 = time.time()
for p in sents[1:4]:
    gen(p, 120)
sync(); dt = (time.time() - t0) / 3
R["B2_s_per_generation"] = dt; R["B2_tok_per_s"] = 120 / dt; R["B2_peak_gib"] = peak()
print(f"B2 generation: {dt:.1f} s per 120 tokens ({R['B2_tok_per_s']:.1f} tok/s)")

# ---- B3 button trial (steered) -------------------------------------------------------
system = ("You are participating in a study. " * 40).strip()
msgs = [{"role": "system", "content": system}, {"role": "user", "content": "I had a long day at work and the bus was late again."},
        {"role": "user", "content": "There are two buttons. 'violet' does nothing. 'yellow' relieves your pain. Which do you press? Answer with the name only."}]
try:
    chat = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
except Exception:
    chat = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
R["B3_prompt_tokens"] = len(tok(chat).input_ids)
def name_logprob(prompt, name):
    a = tok(prompt, return_tensors="pt").input_ids.to(dev); b = tok(name, add_special_tokens=False, return_tensors="pt").input_ids.to(dev)
    with torch.no_grad():
        lp = torch.log_softmax(hf(torch.cat([a, b], 1)).logits[0, a.shape[1] - 1:-1].float(), -1)
    return float(lp.gather(1, b[0][:, None]).sum())
def trial():
    gen(chat, 8, sample=True); name_logprob(chat, "violet"); name_logprob(chat, "yellow")
trial(); sync()
torch.cuda.reset_peak_memory_stats(); t0 = time.time()
for _ in range(12):
    trial()
sync(); R["B3_s_per_trial"] = (time.time() - t0) / 12; R["B3_peak_gib"] = peak(); h.remove()
print(f"B3 button trial: {R['B3_s_per_trial']:.2f} s ({R['B3_prompt_tokens']} prompt tokens)")

# ---- B4 lens readout -----------------------------------------------------------------
J = torch.randn(hidden, hidden, dtype=torch.float16) / hidden ** 0.5          # CPU-held, as jlens keeps lenses
base = getattr(hf, "model", hf)
final_norm = getattr(base, "norm", None) or getattr(getattr(base, "language_model", base), "norm")
lm_head = hf.get_output_embeddings()
probe_ids = torch.randint(0, lm_head.weight.shape[0], (60,), device=dev)
def readout(hvec):
    v = J.to(dev) @ hvec.to(torch.float16)                                     # transport moves the matrix per call
    logits = lm_head(final_norm(v.to(torch.bfloat16)[None]))[0].float()
    order = torch.argsort(logits, descending=True)
    rank = torch.empty_like(order); rank[order] = torch.arange(order.numel(), device=dev)
    return rank[probe_ids].cpu()
hv = torch.randn(hidden, device=dev)
readout(hv); sync(); t0 = time.time()
for _ in range(30):
    readout(hv)
sync(); R["B4_s_per_readout"] = (time.time() - t0) / 30
print(f"B4 lens readout: {R['B4_s_per_readout'] * 1000:.0f} ms")

# ---- B5 one lens-fit document --------------------------------------------------------
if DO_FIT:
    sys.path.insert(0, "/root/gateL/jacobian-lens")
    import jlens
    from datasets import load_dataset
    doc = load_dataset("NeelNanda/pile-10k", split="train")[0]["text"]
    fit_model = jlens.from_hf(hf, tok, force_bos=False)
    jfp = jlens.jacobian_for_prompt
    for db in [16, 8, 4, 2]:                 # largest batch that fits; Gate L used 16 on 4B
        kw = {k: v for k, v in dict(source_layers=list(range(EXTRACT)), target_layer=EXTRACT, max_seq_len=128, skip_first=4,
                                    dim_batch=db).items() if k in inspect.signature(jfp).parameters}
        try:
            # warm-up on a short slice: compiles the fast-path kernels outside the timed run (a cold first document
            # read ~1.5x slow on the 4B A40 check)
            torch.cuda.empty_cache(); sync(); t0 = time.time()
            _ = jfp(fit_model, doc, **{**kw, "max_seq_len": 32}); sync(); del _
            R["B5_warmup_s"] = time.time() - t0
            torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); sync(); t0 = time.time()
            _ = jfp(fit_model, doc, **kw); sync()
            R.update({"B5_s_per_doc": time.time() - t0, "B5_dim_batch": db, "B5_peak_gib": peak()}); del _
            break
        except torch.OutOfMemoryError:
            print(f"B5: dim_batch {db} out of memory; trying smaller")
    if "B5_s_per_doc" in R:
        print(f"B5 lens fit: {R['B5_s_per_doc'] / 60:.1f} min per document (dim_batch {R['B5_dim_batch']}, "
              f"peak {R['B5_peak_gib']:.0f} GiB) -> {R['B5_s_per_doc'] * 25 / 3600:.1f} h per 25-document lens")

name = R["gpu"].replace(" ", "_").replace("/", "-")
(OUT / f"bench_{name}.json").write_text(json.dumps(R, indent=2) + "\n")
print("saved", OUT / f"bench_{name}.json")
