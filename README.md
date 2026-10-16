# euphoria-axis

Bounded extension of Tagliabue, Dung & Berg, *The Pain Axis* (v2, 2026), on Qwen3, Qwen3.5, Qwen3.6 and Qwen3.8 models.

## Layout

- `doc/FINISH-LINE.md` — the live plan: gates, decisions, stopping rules. `doc/plan/generalization-plan.md` — the cross-model plan (Gates 2a-3b).
- `doc/CONVENTIONS.md`, `doc/CLAIMS-INDEX.md`, `doc/LEDGER-4B.md` — the frozen 4B conventions, every claim with its status and evidence, and the 4B claims ledger.
- `doc/checkpoints/` — one note per experiment, numbered in run order (results, frozen predictions and scores).
- `doc/protocols/` — specs and instruments that produced data: button pilot and its amendment, M7 on Qwen3-14B (`buttons/`), Gate 2a (`gate2a/`), R4 lenses (`lenses/`), blind matched-pair prompt and draft set.
- `doc/plan/` — earlier plans and context; superseded versions in `archive/`.
- `doc/notes/` — dated session notes. `doc/writeup/` — report and LessWrong drafts.
- `notebooks/` — numbered in the order they were used. Cells run on a remote GPU kernel whose working directory is the server's data folder, not this repo.
- `runs/` — artifacts pulled from the server and from RunPod (`qwen35-4b-*` for the 4B work, `qwen3-14b-*` for the Qwen3-14B reproduction and extensions). Bulky files (`*.npz`, files >= 5 MB) are not committed; they are listed with sha256 in each `bulky_artifacts_manifest.json`.
- `tools/` — local helpers, lens-session tools, the 14B J/R-lens release publisher, and `tools/runpod/`: pod scripts to be synced onto the network volume from git once the repo-backed start command is enabled after merge. See `tools/README.md`.
- `releases/qwen3-14b-jr-lenses/` — published lens model card and user-facing recipe/usage notes.

Third-party data are not redistributed: the source paper's datasets come from its repository (pinned commit `8d1649c0`), and the NRC VAD Lexicon must be obtained from NRC under its own terms.
