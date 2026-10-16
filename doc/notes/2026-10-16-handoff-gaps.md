# 2026-10-16 — repo cleanup and outstanding artifact transfers

This is an operational checklist, **not** a new experiment or protocol amendment.
Frozen protocols and verdicts remain in `doc/protocols/` and checkpoints 10–12.

## Already on upstream `bubskee/main` (`7aef978`)

- [x] Qwen3-14B M7 result files (`runs/qwen3-14b-m7/`) and checkpoint 11.
- [x] Qwen3-14B R4 machine-readable fit, comparison, readout and probe files
  (`runs/qwen3-14b-r4/`); the three ~2 GB `.pt` lenses remain off Git,
  with their SHA-256 values recorded in the fit JSONs.
- [x] Qwen3-14B J/R lens Hugging Face release tooling, model card and BlueDot
  acknowledgement (`releases/qwen3-14b-jr-lenses/`, `tools/publish_qwen3_14b_jr_lenses.py`).
- [x] Fast-forward `bfaber-centaur/main` to upstream (no rewrite).

## Still to resolve

- [ ] Commit the 27B benchmark JSONs and cost output from `/workspace/bench/`
  on the RunPod volume. The benchmark checkpoint narrative is already in Git.
- [ ] Record `r4_ladder_ranks.npz` by hash if it was produced and retained.
  The `.npz` is ignored: once it is on the Mac, run
  `python tools/refresh_bulky_manifest.py runs/qwen3-14b-r4` to add it to
  a SHA-256 manifest. The script already accepts a directory argument and is
  **not limited** to the default 4B `paper_protocol` directory.
- [ ] Preserve exact historical Gate 2a/M7/R4 execution versions: the scripts
  in `tools/runpod/` are the latest robust versions, not necessarily
  bit-identical to what every completed run executed. The run headers are
  authoritative; consider tags for the exact execution revisions.
- [x] Import the **file contents** of the nine-commit handoff onto
  `bfaber-centaur/reorg-pod-tools` above updated `main` in three logical
  commits. All 30 changed Git blobs were verified against the local tree.
  The original nine commit objects remain in the handoff bundle (the online
  branch uses new commit identities).
- [ ] Review the eventual PR against `bubskee/main` without merging it yet.
- [ ] **After** the repo-backed boot merges into `bubskee/main`, update the
  RunPod template's start command. Never switch the template beforehand.

No results have been reconstructed from checkpoint prose to fill missing
files. The machine-readable M7 and R4 files on upstream take precedence over
the older handoff's assertion that those files still need to be committed.
