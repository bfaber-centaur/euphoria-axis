# CLAUDE.md — euphoria-axis

Reproduction and extension of the Pain Axis paper (valen-research/Pain-axis): steering, probing and lens readouts
on Qwen3.5-4B, Qwen3-14B, and (next) Qwen3.5/3.6/3.8-27B. Start with `README.md`, `doc/FINISH-LINE.md` (the live
plan) and `doc/plan/generalization-plan.md` (the cross-model plan).

## Rules of this project

- **Frozen specs are frozen.** A spec in `doc/protocols/` is committed before any of its data exists and is never
  edited afterwards (runs record its sha256). Changes after data are new, versioned amendments.
- **Label every result:** prospectively tested (frozen prediction), exploratory, or source-method transfer; post-hoc
  analyses say so. `doc/CLAIMS-INDEX.md` is the ledger; `doc/CONVENTIONS.md` holds signs, layers, doses, statistics.
- **Reproduce the source with its own code, unmodified,** and change only what a spec lists.
- **Verify, don't assume:** hashes for model files, lenses and specs; gates (exact reproduction of a stored result)
  before steered runs; run headers recording revision, versions, GPU and spec hash.
- **Measurement is not experience.** No result here establishes or rules out felt states.

## RunPod workflow

- Once the repo-backed start command is installed **after the branch merges to `bubskee/main`**, pods boot from git: the template's start command clones this repo and runs `tools/runpod/boot.sh`, which copies
  `tools/runpod/*`, data files and frozen specs to `/workspace/lens-fit/` and runs setup. **Commit and push before
  deploying.** Pod env vars: `MODEL_ID` (`none` for environment-only pods), `MODEL_REV`, `AUTORUN`, optional
  `REPO_REF`.
- Containers misreport resources: read CPU and memory limits from the cgroup.
- The network volume refuses permission/timestamp changes: caches, environments and weights go on container disk;
  copy files by contents only.
- Lens fitting runs on Ampere (A100), not Hopper (fla backward guard, Triton < 3.7.1).
- Pull results with rclone over SSH (`pod:` remote); large lenses stay on the volume, recorded by hash.
