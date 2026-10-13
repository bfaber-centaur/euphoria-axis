# =====================================================================
# Gate L on the pod: refit a Qwen3.5-4B lens with the published recipe and
# compare it to the published lens of the same type.
#   MODE = "J"  -> L1a (official jlens estimator)
#   MODE = "R"  -> L1b (same estimator through RelP-modified backward rules,
#                 configured as the published R lens: LN rule on block norms,
#                 identity rule on SiLU, half rule (beta 0.5) on the SwiGLU
#                 product; QK norms and gated norms untouched)
# Self-tests run before any fit; any failure stops the cell.
# Run in the /root/gateL/.venv kernel (HF_HOME=/workspace/hf).
# =====================================================================
import hashlib, inspect, io, json, logging, os, platform, sys, time
from pathlib import Path

# settings via environment, e.g.  MODE=R FORCE_BOS=1 DIM_BATCH=16 python gateL_fit.py
MODE = os.environ.get("MODE", "J")                    # "J" for L1a, "R" for L1b
FORCE_BOS = os.environ.get("FORCE_BOS", "1") == "1"   # L1a: try 1, then 0; L1b: whichever L1a matched
DIM_BATCH = int(os.environ.get("DIM_BATCH", "16"))    # 32 ran out of memory on the A40 with the torch fallback
N_DOCS = int(os.environ.get("N_DOCS", "25"))         # L1: 25 (published recipe); L2: 100
DOC_OFFSET = int(os.environ.get("DOC_OFFSET", "0"))  # 0 = the published recipe's documents; 25 = data-sensitivity test
CKPT_EVERY = int(os.environ.get("CKPT_EVERY", "5"))  # checkpoints are ~0.8 GB each; use 25 for long fits
MAX_SEQ_LEN, SKIP_FIRST, TARGET = 128, 4, 30
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")   # must be set before CUDA initialises
OUT = Path("/workspace/gateL"); OUT.mkdir(parents=True, exist_ok=True)
PUB = {"J": "/workspace/workspace-lenses/qwen3.5-4b/j-lens/lens.pt",
       "R": "/workspace/workspace-lenses/qwen3.5-4b/r-lens/lens.pt"}
PUB_SHA = {"J": "8ac16d8e5e988f19d9e19ac9b459c9e73336a866c8534d521200e4fcf2c21377",
           "R": "848b9b8e76eb0448a926edc8bb374cb4369916dd6bdbd62f1d3141fa12b9f231"}
sys.path.insert(0, "/root/gateL/jacobian-lens")  # code and venv on container disk; data on /workspace

import torch, transformers, jlens
from datasets import load_dataset

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()

for k, p in PUB.items():
    assert sha256(p) == PUB_SHA[k], f"published {k} lens does not match the L0 hash"
env = {"model_path": os.environ.get("MODEL_PATH", "Qwen/Qwen3.5-4B"), "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
       "gpu": torch.cuda.get_device_name(0), "jlens_commit": os.popen("git -C /root/gateL/jacobian-lens rev-parse HEAD").read().strip()}
print(env)

# ---------------------------------------------------------------------
# 1. model, with the load log captured (it reports whether the linear-attention fast path is used)
# ---------------------------------------------------------------------
buf = io.StringIO(); h = logging.StreamHandler(buf)
logging.getLogger("transformers").addHandler(h)
if "hf" not in globals():
    MODEL_PATH = os.environ.get("MODEL_PATH", "Qwen/Qwen3.5-4B")   # setup sets this to the verified local copy
    hf = transformers.AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.bfloat16).cuda().eval()
    tok = transformers.AutoTokenizer.from_pretrained(MODEL_PATH)
logging.getLogger("transformers").removeHandler(h)
fastpath = {m: __import__("importlib").util.find_spec(m) is not None for m in ["fla", "causal_conv1d"]}
print("fast-path packages importable:", fastpath)
print("load log mentioning fast path / fallback:", [l for l in buf.getvalue().splitlines()
                                                    if "fast" in l.lower() or "fall" in l.lower()] or "none")
env["fast_path_packages"] = fastpath
# trace which delta-rule / conv functions a real forward pass calls (transformers dispatches at call time)
_calls = set()
def _prof(frame, event, arg):
    if event == "call" and any(k in frame.f_code.co_name for k in ("delta_rule", "conv1d")):
        _calls.add(f"{frame.f_globals.get('__name__')}.{frame.f_code.co_name}")
_ids = tok("hello world " * 20, return_tensors="pt").input_ids.cuda()
sys.setprofile(_prof)
with torch.no_grad():
    hf(_ids)
sys.setprofile(None)
impls = sorted(_calls)
print("linear-attention functions called in a forward pass:", impls or "none found")
env["linear_attention_impl"] = impls

layers = next(m for m in hf.modules() if isinstance(m, torch.nn.ModuleList)
              and len(m) > 0 and hasattr(m[0], "mlp") and hasattr(m[0], "input_layernorm"))
assert len(layers) == 32, len(layers)

# ---------------------------------------------------------------------
# 2. RelP rules (MODE R only): exact forward, rule-modified gradient
# ---------------------------------------------------------------------
def st(exact, surrogate):
    """Forward value of `exact`; gradient of `surrogate` (straight-through)."""
    return exact.detach() + (surrogate - surrogate.detach())

def make_norm_forward(mod):
    src = inspect.getsource(type(mod).forward)
    zero_centered = "1.0 + self.weight" in src or "1 + self.weight" in src
    eps = getattr(mod, "variance_epsilon", getattr(mod, "eps", 1e-6))
    orig = mod.forward
    def fwd(x):
        y = orig(x)
        xf = x.float()
        rstd = torch.rsqrt(xf.pow(2).mean(-1, keepdim=True) + eps).detach()         # LN rule: scale held fixed
        gain = (1.0 + mod.weight.float()) if zero_centered else mod.weight.float()
        return st(y, (xf * rstd * gain).to(y.dtype))
    return fwd, zero_centered

def mlp_rule(g, u, a):
    """g = gate pre-activation, u = up projection, a = act_fn(g) (exact SiLU). Returns the product with
    identity rule on SiLU (sigmoid detached) and half rule (beta 0.5) on the product."""
    a_r = st(a, g * torch.sigmoid(g).detach())
    p = a * u
    return st(p, 0.5 * (a_r * u.detach()) + 0.5 * (a_r.detach() * u))

def make_mlp_forward(mlp):
    for name in ["gate_proj", "up_proj", "down_proj", "act_fn"]:
        assert hasattr(mlp, name), f"MLP layout differs: {mlp}"
    assert isinstance(mlp.act_fn, torch.nn.SiLU) or "silu" in type(mlp.act_fn).__name__.lower(), mlp.act_fn
    def fwd(x):
        g, u = mlp.gate_proj(x), mlp.up_proj(x)
        return mlp.down_proj(mlp_rule(g, u, mlp.act_fn(g)))
    return fwd

if MODE == "R":
    # gradient self-tests on random inputs, before touching the model
    g = torch.randn(64, dtype=torch.float32, requires_grad=True); u = torch.randn(64, requires_grad=True)
    out = mlp_rule(g, u, torch.nn.functional.silu(g)); out.sum().backward()
    assert torch.allclose(out, torch.nn.functional.silu(g) * u), "MLP rule changed the forward value"
    assert torch.allclose(g.grad, 0.5 * u.detach() * torch.sigmoid(g.detach()), atol=1e-6), "identity/half rule gradient wrong (gate)"
    assert torch.allclose(u.grad, 0.5 * torch.nn.functional.silu(g.detach()), atol=1e-6), "half rule gradient wrong (up)"
    norm0 = layers[0].input_layernorm
    nf, zc = make_norm_forward(norm0)
    x = torch.randn(1, 3, norm0.weight.shape[0], device="cuda", dtype=torch.bfloat16, requires_grad=True)
    v = torch.randn_like(x)
    (nf(x) * v).sum().backward()
    xf = x.detach().float(); rstd = torch.rsqrt(xf.pow(2).mean(-1, keepdim=True) + getattr(norm0, "variance_epsilon", getattr(norm0, "eps", 1e-6)))
    gain = (1.0 + norm0.weight.float()) if zc else norm0.weight.float()
    assert torch.allclose(x.grad.float(), v.float() * rstd * gain, rtol=2e-2, atol=2e-2), "LN rule gradient wrong"
    print(f"rule self-tests passed (norm zero-centered: {zc})")

    # forward must be bit-identical after patching
    ids = tok("The quick brown fox jumps over the lazy dog.", return_tensors="pt").input_ids.cuda()
    with torch.no_grad():
        before = hf(ids).logits.clone()
    for blk in layers:
        blk.input_layernorm.forward = make_norm_forward(blk.input_layernorm)[0]
        blk.post_attention_layernorm.forward = make_norm_forward(blk.post_attention_layernorm)[0]
        blk.mlp.forward = make_mlp_forward(blk.mlp)
    with torch.no_grad():
        after = hf(ids).logits
    assert torch.equal(before, after), f"patched forward differs (max |diff| {(before - after).abs().max().item()})"
    print("forward bit-identical after RelP patches: OK (block norms and MLPs patched; QK and gated norms untouched)")

# ---------------------------------------------------------------------
# 3. prompts and a timed first document
# ---------------------------------------------------------------------
fit_model = jlens.from_hf(hf, tok, force_bos=FORCE_BOS)
pile = load_dataset("NeelNanda/pile-10k", split="train")
prompts = [pile[i]["text"] for i in range(DOC_OFFSET, DOC_OFFSET + N_DOCS)]
prompts_sha = hashlib.sha256(json.dumps(prompts).encode()).hexdigest()
first25_sha = hashlib.sha256(json.dumps(prompts[:25]).encode()).hexdigest()
if DOC_OFFSET == 0:
    assert first25_sha.startswith("4111a9cf"), f"first 25 documents differ from the L1 set ({first25_sha[:16]})"

jfp = jlens.jacobian_for_prompt
kw = {k: v for k, v in dict(source_layers=list(range(TARGET)),   # what jlens.fit uses by default: every layer below target
                            target_layer=TARGET, max_seq_len=MAX_SEQ_LEN, skip_first=SKIP_FIRST,
                            dim_batch=DIM_BATCH).items() if k in inspect.signature(jfp).parameters}
torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
_ = jfp(fit_model, prompts[0], **kw)
torch.cuda.synchronize(); dt = time.time() - t0
peak = torch.cuda.max_memory_allocated() / 2**30; total = torch.cuda.get_device_properties(0).total_memory / 2**30
print(f"one document: {dt:.1f} s | peak memory {peak:.1f} / {total:.0f} GiB | projected fit: {dt * N_DOCS / 60:.0f} min")
del _

# ---------------------------------------------------------------------
# 4. fit (resumable) and save
# ---------------------------------------------------------------------
path_tag = ("fast" if any(i.startswith(("fla", "causal_conv1d")) for i in impls)
            else "torch" if any("torch_" in i for i in impls) else "unknown")
tag = f"refit_{MODE}_n{N_DOCS}{f'_off{DOC_OFFSET}' if DOC_OFFSET else ''}_bos{int(FORCE_BOS)}_{path_tag}"
out, ckpt = OUT / f"{tag}.pt", OUT / f"{tag}.ckpt.pt"
if not out.exists():
    t0 = time.time()
    lens = jlens.fit(fit_model, prompts, target_layer=TARGET, max_seq_len=MAX_SEQ_LEN, skip_first=SKIP_FIRST,
                     dim_batch=DIM_BATCH, checkpoint_path=str(ckpt), checkpoint_every=CKPT_EVERY, resume=True)
    lens.save(str(out)); fit_min = (time.time() - t0) / 60
    ckpt.unlink(missing_ok=True)
    print(f"fit done in {fit_min:.1f} min -> {out}")
else:
    fit_min = None; print("refit exists:", out)

# ---------------------------------------------------------------------
# 5. compare with the published lens of the same type
# ---------------------------------------------------------------------
def stack(path):
    d = torch.load(path, map_location="cpu", weights_only=False); J = d["J"]
    return J.float() if torch.is_tensor(J) else torch.stack([J[k].float() for k in sorted(J)])
pubJ, pubR, ref = stack(PUB["J"]), stack(PUB["R"]), stack(out)
same = pubJ if MODE == "J" else pubR
cos = lambda a, b: float((a.flatten().double() @ b.flatten().double()) / (a.double().norm() * b.double().norm()))
rows, passed = [], True
for l in range(TARGET):
    c_ref, c_jr = cos(ref[l], same[l]), cos(pubJ[l], pubR[l])
    ok = (1 - c_ref) < (1 - c_jr); passed &= ok
    rows.append({"layer": l, "cos_refit_vs_published": c_ref, "cos_pubJ_vs_pubR": c_jr,
                 "dist_ratio": (1 - c_ref) / max(1 - c_jr, 1e-12), "pass": ok})
print(f"\nlayer  cos(refit,pub{MODE})  cos(pubJ,pubR)  dist ratio (<1 passes)")
for r in rows:
    print(f"{r['layer']:5d}  {r['cos_refit_vs_published']:16.5f}  {r['cos_pubJ_vs_pubR']:14.5f}  {r['dist_ratio']:9.3f}  {'' if r['pass'] else 'FAIL'}")
print(f"\nL1{'a' if MODE == 'J' else 'b'} ({MODE}, force_bos={FORCE_BOS}): {'PASS' if passed else 'FAIL'} "
      f"at {sum(r['pass'] for r in rows)}/{TARGET} layers")
(OUT / f"{tag}.json").write_text(json.dumps({
    "mode": MODE, "force_bos": FORCE_BOS, "recipe": {"n_docs": N_DOCS, "max_seq_len": MAX_SEQ_LEN, "skip_first": SKIP_FIRST,
    "target_layer": TARGET, "dim_batch": DIM_BATCH, "checkpoint_every": CKPT_EVERY, "doc_offset": DOC_OFFSET}, "relp_rules": None if MODE == "J" else {
    "ln_rule": "block input/post-attention RMSNorms", "identity_rule": "MLP SiLU", "half_rule_beta": 0.5,
    "include_qk_norms": False, "gated_norms": False}, "env": env, "prompts_sha256": prompts_sha, "first25_sha256": first25_sha,
    "first_doc_seconds": dt, "peak_gib": peak, "fit_minutes": fit_min, "refit_sha256": sha256(out),
    "published_sha256": PUB_SHA[MODE], "rows": rows, "pass": passed}, indent=2) + "\n")
