#!/bin/bash
# Gate L: fresh-pod setup for the FAST linear-attention path (fla + causal-conv1d).
#   /workspace   (network volume): HF cache, lenses, fit outputs, scripts, cached wheels   -- persistent
#   /root/gateL  (container disk): code, venv, uv cache                     -- rebuilt each pod
# If /workspace/gateL/env-fast.lock.txt exists, the exact previous environment is reinstalled.
set -euo pipefail
mkdir -p /root/gateL
# only one setup at a time: a second copy (e.g. a manual run during the boot-time one) exits immediately
exec 9>/root/gateL/setup.lock
flock -n 9 || { echo "another setup is running (see /workspace/gateL/setup.log); not starting a second one"; exit 0; }
rm -f /root/gateL/READY /root/gateL/FAILED
trap 'echo "setup failed at line $LINENO" | tee /root/gateL/FAILED' ERR
echo "setup started $(date -Is)"
# retry a command with exponential backoff (5, 10, 20, 40 s ...); messages go to stderr so $(...) captures stay clean
retry() {
  local _n=$1; shift; local _d=5 _i
  for ((_i = 1; _i <= _n; _i++)); do
    "$@" && return 0
    if [ "$_i" -lt "$_n" ]; then echo "retry $_i/$_n failed: $*; waiting ${_d}s" >&2; sleep "$_d"; _d=$((_d * 2)); fi
  done
  echo "giving up after $_n attempts: $*" >&2; return 1
}
# the network volume must be mounted AND writable before anything is written under /workspace (waits up to ~5 min)
d=5; for i in $(seq 1 8); do
  if mountpoint -q /workspace && touch /workspace/.probe 2>/dev/null; then rm -f /workspace/.probe; break; fi
  if [ "$i" = 8 ]; then
    echo "/workspace never became a writable mount point: the network volume is not attached" | tee /root/gateL/FAILED; exit 1
  fi
  echo "waiting for /workspace (attempt $i/8, ${d}s)" >&2; sleep "$d"; d=$(( d < 60 ? d * 2 : 60 ))
done
[ -f /workspace/.volume-id ] || cat /proc/sys/kernel/random/uuid > /workspace/.volume-id
echo "volume: $(findmnt -no SOURCE,FSTYPE /workspace) | id $(cat /workspace/.volume-id)"
# SSH key from the volume, in case RunPod did not inject PUBLIC_KEY on this boot
if [ -f /workspace/lens-fit/authorized_keys ]; then
  mkdir -p /root/.ssh && chmod 700 /root/.ssh
  while read -r k; do [ -n "$k" ] && { grep -qxF "$k" /root/.ssh/authorized_keys 2>/dev/null || echo "$k" >> /root/.ssh/authorized_keys; }; done \
      < /workspace/lens-fit/authorized_keys
  chmod 600 /root/.ssh/authorized_keys && echo "ssh: keys from the volume installed"
fi
# what RunPod actually injected on this boot (presence only, never values)
for v in HF_TOKEN PUBLIC_KEY HF_HOME UV_CACHE_DIR HF_XET_CACHE; do
  if [ -n "${!v:-}" ]; then echo "env $v: set"; else echo "env $v: NOT SET"; fi
done
# Environment variables come from the RunPod template (HF_HOME, UV_CACHE_DIR, HF_TOKEN); /start.sh makes them
# visible to SSH shells. Set them here only for this script. Do NOT rewrite ~/.bashrc: /start.sh appends to it
# at boot, and an in-place rewrite running at the same moment could drop its line.
export HF_HOME=${HF_HOME:-/workspace/hf}
export UV_CACHE_DIR=${UV_CACHE_DIR:-/root/gateL/uv-cache}
# Xet (HF's chunked storage) keeps a chunk cache under HF_HOME by default; on the network volume it produced
# empty files. Keep it on the container disk. If downloads still come out empty, set HF_HUB_DISABLE_XET=1.
export HF_XET_CACHE=${HF_XET_CACHE:-/root/gateL/xet-cache}
LOCK=/workspace/gateL/env-fast.lock.txt
mkdir -p /root/gateL /workspace/gateL && cd /root/gateL

# 0. the CUDA compiler must match torch's CUDA build for causal-conv1d to compile
NVCC=$(nvcc --version 2>/dev/null | sed -n 's/.*release \([0-9]*\.[0-9]*\).*/\1/p' || true)
echo "nvcc: ${NVCC:-not found} | driver: $(nvidia-smi --query-gpu=driver_version,name --format=csv,noheader)"
if [ "$NVCC" != "12.8" ]; then
  echo "This script builds against torch for CUDA 12.8, but nvcc is '${NVCC:-missing}'."
  echo "Pick a RunPod image with CUDA 12.8 (as last time), or change the cu128 index below to match nvcc."
  echo "nvcc is '${NVCC:-missing}', expected 12.8" > /root/gateL/FAILED
  exit 1
fi

# 1. pinned fitting code
[ -d jacobian-lens ] || retry 4 git clone -q https://github.com/anthropics/jacobian-lens.git
retry 4 git -C jacobian-lens fetch -q && git -C jacobian-lens checkout -q 581d398613e5
echo "jacobian-lens at $(git -C jacobian-lens rev-parse HEAD)"

# 2. environment
command -v uv >/dev/null || pip install -q uv
[ -d .venv-fast ] || uv venv -q .venv-fast
source .venv-fast/bin/activate
if [ -f "$LOCK" ]; then
  echo "installing the locked environment from $LOCK"
  retry 4 uv pip install -q torch --index-url https://download.pytorch.org/whl/cu128 \
      "$(grep -E '^torch==' "$LOCK")"
  # drop torch (installed above), causal-conv1d (installed from the wheel cache below), editable installs, and any
  # local-file reference ("pkg @ file:///..."): freeze records wheel-file installs that way, and the file is not on a new pod
  grep -v -E '^(torch|causal-conv1d|causal_conv1d)([ =@]|$)|^-e | @ file:|jacobian' "$LOCK" > /tmp/lock_rest.txt
  retry 4 uv pip install -q -r /tmp/lock_rest.txt
  # causal-conv1d's pinned version, from either "causal-conv1d==X" or "causal-conv1d @ file:///.../causal_conv1d-X-...whl"
  CC1D=$(sed -nE 's/^causal[-_]conv1d(==| @ file:.*causal_conv1d-)([0-9][0-9.]*[0-9]).*/causal-conv1d==\2/p' "$LOCK" | head -1)
  CC1D=${CC1D:-causal-conv1d}
else
  retry 4 uv pip install -q torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
  retry 4 uv pip install -q transformers==5.19.0 datasets accelerate safetensors huggingface_hub ninja packaging ipykernel
  retry 4 uv pip install -q flash-linear-attention
  CC1D=causal-conv1d
fi
retry 4 uv pip install -q -e jacobian-lens 2>/dev/null || echo "jacobian-lens not pip-installable; scripts add it to sys.path"
# causal-conv1d: reuse a wheel cached on the volume if it was built for this exact torch + python,
# otherwise build once (10-20 min) and cache it for future pods
WHEELS=/workspace/wheels; mkdir -p $WHEELS
STAMP="$(python -c 'import torch, sys; print(torch.__version__, sys.version.split()[0])')"
CC1D_ARCHS=${CC1D_ARCHS:-"8.0;8.6;8.9;9.0"}       # add ";10.0;12.0" for Blackwell (B200, RTX PRO 6000)
STAMP="$STAMP archs=$CC1D_ARCHS"
if ls $WHEELS/causal_conv1d-*.whl >/dev/null 2>&1 && [ "$(cat $WHEELS/causal_conv1d.stamp 2>/dev/null)" = "$STAMP" ]; then
  echo "installing cached causal-conv1d wheel (built for: $STAMP)"
  retry 4 uv pip install -q $WHEELS/causal_conv1d-*.whl
else
  echo "building $CC1D wheel against: $STAMP (10-20 min, once)"
  retry 4 uv pip install -q pip
  # default: A100 (8.0), A40/Ampere (8.6), Ada (8.9), H100 (9.0); CC1D_ARCHS overrides
  rm -rf /root/gateL/wheels && TORCH_CUDA_ARCH_LIST="$CC1D_ARCHS" MAX_JOBS=4 \
      python -m pip wheel -q "$CC1D" --no-build-isolation --no-deps -w /root/gateL/wheels
  rm -f $WHEELS/causal_conv1d-*.whl
  cp /root/gateL/wheels/causal_conv1d-*.whl $WHEELS/ && echo "$STAMP" > $WHEELS/causal_conv1d.stamp
  retry 4 uv pip install -q /root/gateL/wheels/causal_conv1d-*.whl
fi

echo "download tool: $(command -v hf) | $(python -c 'import huggingface_hub as h; print("huggingface_hub", h.__version__)') | $(python -c 'import hf_xet, importlib.metadata as m; print("hf_xet", m.version("hf_xet"))' 2>/dev/null || echo "hf_xet not installed")"

# 3. model: plain folder on the CONTAINER disk, pinned revision, every file verified by sha256 against the Hub.
#    (The HF cache layout on the network volume produced empty and stale files; it is not used for the model.)
# model: MODEL_ID (default the 4B); MODEL_REV pinned for 4B, otherwise resolved now and recorded
MODEL_ID=${MODEL_ID:-Qwen/Qwen3.5-4B}
if [ -z "${MODEL_REV:-}" ]; then
  if [ "$MODEL_ID" = "Qwen/Qwen3.5-4B" ]; then MODEL_REV=851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a
  else MODEL_REV=$(retry 4 python -c "from huggingface_hub import HfApi; print(HfApi().model_info('$MODEL_ID').sha)"); fi
fi
MODEL_DIR=/root/models/$(basename "$MODEL_ID")
echo "model: $MODEL_ID @ $MODEL_REV -> $MODEL_DIR"
echo "$MODEL_ID $MODEL_REV" > /root/gateL/MODEL
verify_model() { python - "$MODEL_DIR" "$MODEL_REV" "$MODEL_ID" <<'PY'
import hashlib, os, sys
from huggingface_hub import HfApi
d, rev, mid = sys.argv[1], sys.argv[2], sys.argv[3]
info = HfApi().model_info(mid, revision=rev, files_metadata=True)
bad = []
for f in info.siblings:
    p = os.path.join(d, f.rfilename)
    if not os.path.exists(p):
        bad.append(f"{f.rfilename}: missing"); continue
    if f.size is not None and os.path.getsize(p) != f.size:
        bad.append(f"{f.rfilename}: size {os.path.getsize(p)} != {f.size}"); continue
    if f.lfs is not None:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for c in iter(lambda: fh.read(1 << 24), b""):
                h.update(c)
        if h.hexdigest() != f.lfs.sha256:
            bad.append(f"{f.rfilename}: sha256 mismatch")
if bad:
    print("MODEL FILES BAD:", *bad, sep="\n  "); sys.exit(1)
print(f"model verified: {len(info.siblings)} files match the Hub at {rev[:12]}")
PY
}
for attempt in 1 2 3; do
  hf download "$MODEL_ID" --revision $MODEL_REV --local-dir $MODEL_DIR >/dev/null || true
  if verify_model; then break; fi
  if [ $attempt = 3 ]; then echo "model still bad after 3 attempts" | tee /root/gateL/FAILED; exit 1; fi
  echo "attempt $attempt failed verification; removing the download and retrying"
  rm -rf "$MODEL_DIR" /root/gateL/xet-cache; sleep $((attempt * 30))
done
grep -q "MODEL_PATH" ~/.bashrc || echo "export MODEL_PATH=$MODEL_DIR" >> ~/.bashrc
export MODEL_PATH=$MODEL_DIR
if [ "$MODEL_ID" = "Qwen/Qwen3.5-4B" ]; then      # the published 4B lenses, checked against L0
retry 4 hf download camilablank/workspace-lenses --revision d740106d1e0f --include "qwen3.5-4b/*" \
    --local-dir /workspace/workspace-lenses >/dev/null
echo "8ac16d8e5e988f19d9e19ac9b459c9e73336a866c8534d521200e4fcf2c21377  /workspace/workspace-lenses/qwen3.5-4b/j-lens/lens.pt
848b9b8e76eb0448a926edc8bb374cb4369916dd6bdbd62f1d3141fa12b9f231  /workspace/workspace-lenses/qwen3.5-4b/r-lens/lens.pt" \
  | sha256sum -c - || { echo "published lens hashes do not match L0" | tee /root/gateL/FAILED; exit 1; }
fi

# 4. verify the fast path is actually used, by tracing a real forward pass
python - <<'PY'
import sys, torch, transformers
import os
hf = transformers.AutoModelForCausalLM.from_pretrained(os.environ["MODEL_PATH"], dtype=torch.bfloat16).cuda().eval()
ids = transformers.AutoTokenizer.from_pretrained(os.environ["MODEL_PATH"])("hello world " * 20, return_tensors="pt").input_ids.cuda()
calls = set()
def prof(frame, event, arg):
    if event == "call" and any(k in frame.f_code.co_name for k in ("delta_rule", "conv1d")):
        calls.add(f"{frame.f_globals.get('__name__')}.{frame.f_code.co_name}")
sys.setprofile(prof)
with torch.no_grad(): hf(ids)
sys.setprofile(None)
print("\n".join(sorted(calls)))
fast = any(c.startswith(("fla", "causal_conv1d")) for c in calls) and not any("torch_" in c for c in calls)
print("FAST PATH OK" if fast else "NOT THE FAST PATH: check the list above")
print("torch", torch.__version__, "| transformers", transformers.__version__)
sys.exit(0 if fast else 1)
PY

# 5. lock the exact environment for next time
[ -f "$LOCK" ] || { uv pip freeze > "$LOCK" && echo "wrote $LOCK"; }
grep -q "gateL/.venv-fast" ~/.bashrc || echo '[ -f /root/gateL/READY ] && source /root/gateL/.venv-fast/bin/activate' >> ~/.bashrc
python -c 'import torch, transformers, sys; print(f"torch {torch.__version__} transformers {transformers.__version__} python {sys.version.split()[0]}")' > /root/gateL/READY
echo "setup finished $(date -Is): $(cat /root/gateL/READY)"
echo "ready: cd /workspace/lens-fit  (new shells activate the venv automatically)"

# optional: start work in a detached tmux session once ready (template env AUTORUN=bench, or any command)
if [ -n "${AUTORUN:-}" ]; then
  command -v tmux >/dev/null || { retry 3 apt-get update -qq && retry 3 apt-get install -y -qq tmux >/dev/null; }
  mkdir -p /workspace/bench
  case "$AUTORUN" in
    bench) CMD="cd /workspace/lens-fit && python bench_27b.py" ;;
    *)     CMD="$AUTORUN" ;;
  esac
  LOG=/workspace/bench/autorun_$(date +%Y%m%d-%H%M%S).log
  cat > /root/gateL/autorun.sh <<RUN
#!/bin/bash
source /root/gateL/.venv-fast/bin/activate
export HF_HOME=$HF_HOME UV_CACHE_DIR=$UV_CACHE_DIR HF_XET_CACHE=$HF_XET_CACHE MODEL_PATH=$MODEL_PATH
set -o pipefail
( $CMD ) 2>&1 | tee $LOG
echo; echo "[autorun finished with exit code \$?; log: $LOG] this shell stays open"
exec bash
RUN
  # close the setup lock's descriptor (9) in the tmux server, or it would hold the lock forever
  tmux new-session -d -s work "bash /root/gateL/autorun.sh" 9>&-
  echo "autorun: '$AUTORUN' running in tmux session 'work' (attach: tmux attach -t work; log: $LOG)"
fi
