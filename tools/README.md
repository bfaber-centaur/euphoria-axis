# tools

| Path | What it does | Runs on |
|---|---|---|
| `refresh_bulky_manifest.py` | Adds `.npz` and >= 5 MB files under `paper_protocol/` to `bulky_artifacts_manifest.json` (sha256) and re-verifies recorded ones. | Mac, after an rclone pull |
| `validate_matched_pairs.py` | Mechanical validation of the blind-drafted Phase II matched-pair set. | anywhere |
| `gateL_readout_bar.py` | Gate L readout bar: refit vs published lenses on frozen family readouts (layer 29 frozen bars; layers 16/18/22 exploratory). | lens session (`%run -i`) |
| `lens/lens_session_bootstrap.py` | Rebuilds the lens session (model, published J/R lenses, readout helpers) from `notebooks/03-decursed.ipynb` cells 8-10, definitions only. | local GPU kernel (`%run -i`) |
| `lens/lens_L0.py` | Gate L L0: inspects the published 4B J/R lenses (provenance, hashes, J-vs-R per-layer cosine). | local, CPU |
| `runpod/gateL_pod_setup_fast.sh` | Pod setup: pinned `jacobian-lens`, locked fast-path environment (torch cu128, `fla`, cached `causal-conv1d` wheel), checksum-verified model and lenses, READY/FAILED markers. Called from the RunPod template's start command. | RunPod |
| `runpod/gateL_fit.py` | Fits a J or R lens with the published recipe (`MODE`, `FORCE_BOS`, `N_DOCS`, `DOC_OFFSET`, `DIM_BATCH`, `CKPT_EVERY` via environment) and compares it with the published lens. R mode self-tests the RelP rules first. | RunPod |
| `runpod/compare_refits.py` | Per-layer comparison of two refits of the same lens type, against each other and the published lens. | RunPod |

Gate L record: `doc/checkpoints/08-gate-L-lens-calibration.md`.
