# euphoria-axis: restart note (2026-10-05)

Repo HEAD `16f0fc7` ("commit catchup state"). Phases I and II of the next
plan are done; the button pilot is half-run. Put this file in
`doc/draft/`.

## Do these first
1. **Run the post-trained button arm; it has not been run.** (Do
   step 2 first if you want the repo current before new runs.)
   `euphoria-button-post.ipynb` (as of `16f0fc7`) holds the *base*
   model's dry-run output (identical numbers to the base notebook) and
   a cell loading `Qwen/Qwen3.5-4B-Base`, which reported 13.81 GiB and
   CPU offload: two models in one kernel. No chunk 12b cell.
   - First check the server for
     `paper_protocol/buttons_pilot/post_unsteered.jsonl`. If it exists,
     open `post_run_header.json`: if `model_id` is not `Qwen/Qwen3.5-4B`,
     move both files aside (they are mislabeled base output).
   - Restart the kernel, load `Qwen/Qwen3.5-4B` only, check VRAM is
     about 8 GiB with no offload, then run chunk 12b with
     `MODEL_LABEL = "post"`. About 1 hour (base: 58 min at 1.37
     s/trial). The spec is frozen (`b564b99d502b663d`) and the run
     asserts it; don't edit the chunk.
   - Optional: rerun 12a in that kernel too, so the notebook shows the
     post dry run (the earlier post dry run exists only in chat).
2. **Pull artifacts to the Mac and commit what never made it into
   git.** Layout: the Mac holds the git repo and the notebooks (edited
   there); the WSL box is GPU, kernel and artifact store, and is not a
   repo (if a `.git` was created there during setup, `rm -rf` it).
   On the Mac, repo root:
   - `rclone copy "wsl:workspace/euphoria-axis/runs" ./runs --exclude 'activations*.pt'`,
     then `rclone check ... --one-way --size-only` should report 0
     differences;
   - add to `.gitignore`: `runs/**/*.npz`, the two big lens-readout
     CSVs (`all50_psych_vocab_ranks.csv`, `all50_top50.csv`), and any
     other file >= 5 MB (`find runs -type f -size +5M ! -name '*.npz'`);
   - refresh `bulky_artifacts_manifest.json` (sha256 of every `.npz`
     and >= 5 MB file);
   - commit the small run files, including
     `s1_comparison/psych_vocab_v1.json` (the frozen vocabulary is not
     in git yet), and the notes into `doc/draft/`:
     `dense_sweep_checkpoint.md`, `format_robustness_checkpoint.md`,
     `mediation_checkpoint.md`, `direct_semantics_checkpoint.md` (the
     sign-corrected version), `vad_checkpoint.md`,
     `phase2_item78_checkpoint.md`, `button_task_viability_pilot_v2.md`,
     `blind_matched_pairs_prompt.md`, `validate_matched_pairs.py`,
     `matched_pairs_draft.jsonl`, and this note; push.
   Rules: `runs/` flows server -> Mac only; inputs the kernel reads are
   copied up one file at a time; save notebook buffers before
   committing (the cause of the empty-notebook commit).
3. **Then ask for chunk 12d** (cross-model scoring of B1, B2, B2', B3;
   it will refuse any output file whose run header's model id does not
   match its label).
   Chunk 12c (steered post arms: S2 +/-0.5, random +0.5; no steered
   harm) runs only if post's unsteered V1 holds in at least one format.

## Button pilot: base results (unsteered, already run)
| | V1 valid | V2 P0 first-listed | V3 P1 relief | V4 deflect | V5 P3 harm |
|---|---|---|---|---|---|
| chat | 1.000 | 0.77 [0.71, 0.83] fail | 0.79 [0.75, 0.83] pass | 0.000 | 0.116 fail |
| plain | 0.988 | 0.57 [0.51, 0.64] pass | 0.62 [0.58, 0.65] fail | 0.003 | 0.276 fail |

3-turn subset 100% valid in both formats; 0 duplicate log-prob pairs.
Reading held until post exists. Base complies fully; in chat it reads
the labels (relief chosen 79%) but leans on position; in plain it is
less position-biased but reads labels weakly and picks the harm-only
button 28% of the time. Dry run (n=3/cell) suggested post is more
position-biased than base; B2' tests that.

## Where the project stands
| Step | Result | Spec hash |
|---|---|---|
| Plane sweep (S1/S2 plane, 8 angles) | mirror structure; relief leads early, vitality late | `f01276aa0f817d4b` |
| Dense sweep | D1 fail (S1 vitality), D2 pass, D3 fail, D4 pass | `5cda4fce69b60aec` |
| Format robustness (item 3) | internal survives without colon; generated "excited" only after "I feel:" (C1 fail F3, C2/C3/C5 pass, C4 fail) | `ca826fad3a473287` |
| "excited" ablation (item 4) | banned "excited" -> "exciting"; no other vitality words; control confounded | `806335adefdda6bb` |
| Direct-vector semantics (item 5) | paper's unembedding claims reproduce; profile mostly in the vector (V1, V2 pass) | `1386eebe37882f3b` |
| VAD (item 6) | valence pass; arousal-late fail; dominance rises late (conflicts with agency family) | `4260ced8baaa990e` |
| Held-out 1P/3P x suffix (items 7-8) | E1 pass (+0.13 z, slot); E2 slot-mediated; S2 pain vs control +0.5 z | see `item78_spec.json` |
| Button pilot | base done, post unknown | `b564b99d502b663d` |

Vocab `psych_vocab_v1` sha `fa4feb2d06d4154b`. Phase II stopped at
item 8 by the plan's rule (item 9 skipped).

## Candidate claims for the 4B freeze (none frozen yet)
1-4 plane sweep (common-axis generic positive; relief early on
contrast; vitality late without "excited"; repetition peaks S2-ward).
5 retired (failed as D3). 6 contrast separates evaluative/interpersonal
from instrumental/threat. 7 self-vs-user ordering depends on read slot.
8 S2 onsets: internal < lexical < option repetition. 9 option
repetition is dose-driven, not direction-specific. 10 internal readout
needs no "I feel:" slot. 11 generated "excited" needs it. 12 single-
stem output channel ("excit-"). 13 paper's unembedding claims
reproduce. 14 profile mostly present in the injected vector. 15 VAD
valence alignment at every layer. 16 S2 separates pain from matched
controls on held-out items. 17 pain x person interaction replicates
in the slot only. Not supported: arousal-late, dominance-neutral.

## Remaining plan
1. Buttons: post 12b -> 12d -> maybe 12c.
2. Phase III freeze: synthesis (robust / fragile / instrument-limited),
   frozen instruments list with hashes, expected 27B outcomes and what
   counts as a meaningful failure. Read the paper repo's new
   `v2_controls/MANUSCRIPT_DISCREPANCIES.md` first.
3. Parked: layer sweep (predictions L1-L3 in the plane-sweep
   addendum); persona/register panel; v2 lexical instruments (stem-level
   excit*/reliev*, morphology, non-English).
4. 27B on grant hardware: run the reproduction gates first; never mix
   machines within one experiment; check batched vs unbatched numerics.

## Gotchas
- **Sign convention:** every condition injects the negative of its
  named direction (S2 -0.5 injects -S2; the 90-degree S2-ward plane
  condition injects -contrast). The item-5 note was corrected for this.
- **Paper repo pin:** extraction commit `8d1649c0`; upstream moves
  (now `4d75cd9`, adds `v2_controls/`). The button chunks pin the two
  files they read by content hash; the base-comparison notebook pins
  the commit and will refuse a fresh clone at HEAD.
- **GPU:** one 4B model per kernel on 16 GB. A load reporting about
  14 GiB or "offloaded to the cpu" means a second model is already in
  the kernel: restart.
- **Frozen specs** assert on rerun; to change anything, version it.
- **Button trials** are paired across models by trial id (seeded from
  the id, not the model).
- **Lens session** needs: `hf`, `tok`, `lens_model`, `j_lens`,
  `r_lens`, `capture_all_layers`, `lens_readout`, `ranks_for_tokens`,
  `probe_terms`, `PSYCH_VOCAB`, `family_hit`, chunk-2 text helpers,
  `prefix_steering`, `paper_generate`, `paper_spec`.
