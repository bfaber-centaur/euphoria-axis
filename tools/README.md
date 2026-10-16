# tools

## Local and Mac

| Path | What it does | Runs on |
|---|---|---|
| `refresh_bulky_manifest.py` | Adds `.npz` and >= 5 MB files under a chosen run directory to `bulky_artifacts_manifest.json` (sha256) and re-verifies recorded ones. Defaults to the 4B `paper_protocol/` directory; pass `runs/qwen3-14b-r4` for R4. | Mac, after an rclone pull |
| `validate_matched_pairs.py` | Mechanical validation of the blind-drafted Phase II matched-pair set. | anywhere |
| `lens/lens_session_bootstrap.py` | Rebuilds the 4B lens session (model, published J/R lenses, readout helpers) from `notebooks/03-decursed.ipynb` cells 8-10, definitions only. | local GPU kernel (`%run -i`) |
| `lens/lens_L0.py` | Gate L L0: inspects the published 4B J/R lenses (provenance, hashes, J-vs-R per-layer cosine). | local, CPU |
| `lens/gateL_readout_bar.py` | Gate L readout bar: refit vs published lenses on frozen family readouts (layer 29 frozen bars; layers 16/18/22 exploratory). | lens session (`%run -i`) |

## RunPod (`runpod/`)

After the clone-based template start command is enabled **following the upstream merge**, everything in `runpod/` is copied onto the network volume (`/workspace/lens-fit/`) at every boot, so **git is the
source of truth**: commit and push before deploying; copies on the volume are overwritten.

**Boot flow.** The template's start command clones this repository to `/root/repo` (optionally checking out
`REPO_REF`) and runs `runpod/boot.sh`, which logs the commit, waits for the volume (mounted and writable), copies
`runpod/*`, the two data files and the frozen specs to `/workspace/lens-fit/`, and runs setup. Setup reads
`MODEL_ID` (`none` for environment-only pods), `MODEL_REV` and `AUTORUN` from the pod's environment, and leaves
`/root/gateL/READY` or `/root/gateL/FAILED`; `/root/gateL/boot.log` is the timeline.

| Path | What it does |
|---|---|
| `boot.sh` | Boot: commit, volume wait, sync from git, then setup |
| `gateL_pod_setup_fast.sh` | Setup: CPU quota from the cgroup, pinned `jacobian-lens`, locked fast-path environment (torch cu128, `fla`, cached `causal-conv1d` wheel), checksum-verified model at a pinned revision, fast-path check (not applicable for models without linear attention), lock file, optional `AUTORUN` in tmux session `work` |
| `gateL_fit.py`, `compare_refits.py` | Gate L: 4B J/R lens refits with the published recipe; per-layer comparisons |
| `bench_27b.py`, `bench_costs.py` | GPU benchmark for the 27B plan (one unit of each workload) and its cost model |
| `gate2a_env.sh` | Gate 2a environment: the source repository at its pinned commit, TransformerLens 2.18.0 environment, Qwen3-14B at a pinned revision (reuses Gate 2a's when recorded) |
| `gate2a_run.py`, `gate2a_compare.py`, `gate2a_all.sh` | Gate 2a: the source paper's extraction (R1) and ladders (R2a/R2b), run unmodified; comparison with the published results |
| `gate2a_diag_layer.py` | Gate 2a post-hoc layer-matched diagnostic (layers 31 and 32) |
| `m7_q14_unsteered.py`, `m7_q14_steered.py`, `m7_q14_score.py`, `m7_q14_all.sh` | M7: the button task on Qwen3-14B (pilot v2 code verbatim; G10-G14) |
| `r4_fit.py`, `r4_compare.py`, `r4_readout.py`, `r4_q14_all.sh` | R4: J/R lenses for Qwen3-14B (Gate L RelP rules verbatim), internal validation, readouts on the reproduced ladder (R4-P1) |

Frozen specs live in `doc/protocols/` (`gate2a/`, `buttons/`, `lenses/`); boot copies them to the volume.

Records: Gate L `doc/checkpoints/08`, Gate 1 `09`, Gate 2a `10`, M7 on Qwen3-14B `11`, R4 Qwen3-14B `12`; GPU choice
`doc/notes/2026-10-14-gpu-benchmark.md`; plan `doc/plan/generalization-plan.md`.
