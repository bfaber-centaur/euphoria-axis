# euphoria-axis

Bounded extension of Tagliabue, Dung & Berg, *The Pain Axis* (v2, 2026), on Qwen3.5 models.

## Layout

- `doc/FINISH-LINE.md` — the live plan: gates, decisions, stopping rules.
- `doc/checkpoints/` — one note per experiment, numbered in run order (results, frozen predictions and scores).
- `doc/protocols/` — specs and instruments that produced data (button pilot, blind matched-pair prompt and draft set).
- `doc/plan/` — earlier plans and context; superseded versions in `archive/`.
- `doc/notes/` — dated session notes. `doc/writeup/` — report and LessWrong drafts.
- `notebooks/` — numbered in the order they were used. Cells run on a remote GPU kernel whose working directory is the server's data folder, not this repo.
- `runs/` — artifacts pulled from the server. Bulky files (`*.npz`, files >= 5 MB) are not committed; they are listed with sha256 in each `bulky_artifacts_manifest.json`.
- `tools/` — `refresh_bulky_manifest.py`, `validate_matched_pairs.py`.

Third-party data are not redistributed: the source paper's datasets come from its repository (pinned commit `8d1649c0`), and the NRC VAD Lexicon must be obtained from NRC under its own terms.
