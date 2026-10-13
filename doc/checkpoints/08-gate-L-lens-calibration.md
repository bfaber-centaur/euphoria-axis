# Gate L — lens calibration: checkpoint

Qwen3.5-4B post-trained. Question: do the published R/J lenses that every
lens-based result relies on reproduce under our pipeline, and how much does
lens fitting itself move the readouts we report?

Published lenses: `camilablank/workspace-lenses` at `d740106d`, fitted with a
fork of the official estimator (`git_commit: "modal"`). J `8ac16d8e…`,
R `848b9b8e…`. Recipe from the files' own provenance: first 25
`NeelNanda/pile-10k` documents (prompt-set hash `4111a9cf…`), `t_max` 128,
`skip_first` 4, target layer 30, uniform weighting; R rules LN (block norms),
identity (MLP SiLU), half (beta 0.5); QK and gated norms excluded.

Our fits: official `jlens.fit` at `581d3986`; R via our own RelP backward
rules (exact forward, rule-modified gradient; self-tests and a bit-identical
forward check before every R fit). RunPod A40, Qwen3.5 linear-attention fast
path (`fla` + `causal-conv1d`, verified by call tracing), torch 2.11.0+cu128,
transformers 5.19.0 (locked in `env-fast.lock.txt`). About 25 min per
25-document fit, 85-100 min at 100 documents.

## Gate disposition

| Step | Result |
|---|---|
| L0 | Done. Published files are the ones every result used (repos at recorded commits, clean trees); hashes recorded. |
| L1a (J) | Pass, 30/30 layers. |
| L1b (R) | Pass, 30/30 layers. |
| L1 readout bar (layer 29) | Pass for J and R (Spearman >= 0.9994, all six focus-family signs equal). |
| L2 (J, n = 25 vs 100, layer 29) | Pass (Spearman 0.9992-0.9993, signs equal). |
| Exploratory | Document sensitivity (J and R on documents 25-49); R convergence (n = 100); readouts at layers 16, 18, 22. |

Matrix bar used for L1: at every layer, 1 - cos(refit, published lens of the
same type) < 1 - cos(published J, published R).

## Matrix results (1 - cos unless noted)

| Layer | J refit vs published (cos) | R refit vs published (cos) | J vs R published (cos) |
|---|---|---|---|
| 0 | 0.894 | 0.979 | 0.693 |
| 3 | 0.962 | 0.989 | 0.788 |
| 8 | 0.989 | 0.996 | 0.832 |
| 16 | 0.996 | 0.998 | 0.888 |
| 22 | 0.9987 | 0.9994 | 0.968 |
| 29 | 0.99993 | 0.99996 | 0.996 |

Controls:

- BOS handling during fitting has no material effect (`force_bos` on vs off
  agree to the fourth or fifth decimal at every layer).
- Package environment (different `fla`/`causal-conv1d` versions) moves the J
  refit by at most 2.4% of its gap to the published lens (layer 4), under
  0.5% from layer 9 up.

Document sensitivity and convergence (1 - cos):

| Layer | J: refit-published | J: other 25 docs | J: 25 vs 100 | R: refit-published | R: other 25 docs | R: 25 vs 100 |
|---|---|---|---|---|---|---|
| 0 | 0.106 | 0.317 | 0.118 | 0.022 | 0.117 | 0.042 |
| 3 | 0.039 | 0.134 | 0.049 | 0.011 | 0.061 | 0.023 |
| 8 | 0.012 | 0.066 | 0.024 | 0.0044 | 0.032 | 0.012 |
| 16 | 0.0037 | 0.030 | 0.011 | 0.0016 | 0.013 | 0.0049 |
| 22 | 0.0013 | 0.0096 | 0.0036 | 0.0006 | 0.0044 | 0.0017 |
| 29 | 0.00007 | 0.0007 | 0.0003 | 0.00004 | 0.0003 | 0.0001 |

## Readout results (per-probe Spearman of log-rank gains, minimum over S1 -0.5 and S2 -0.5)

| Comparison | L16 | L18 | L22 | L29 |
|---|---|---|---|---|
| L1 J: refit vs published | 0.996 | 0.996 | 0.999 | 0.9994 |
| L1 R: refit vs published | 0.999 | 0.997 | 0.999 | 0.9998 |
| L2 J: 25 vs 100 docs | 0.990 | 0.990 | 0.996 | 0.9992 |
| J: docs 0-24 vs 25-49 | 0.981 | 0.979 | 0.991 | 0.9986 |
| R: docs 0-24 vs 25-49 | 0.991 | 0.984 | 0.996 | 0.9984 |
| R: 25 vs 100 docs | 0.995 | 0.987 | 0.998 | 0.9989 |

Focus-family sign changes across lens fits (all others agree):

- Six are near-zero gains crossing zero (|gain| <= 0.016): approach_drive
  (S2, L16), agency_assurance (S1, L22).
- One is a small real effect: **S1's relief_release gain at layer 16** is
  about 0 under the published R lens and our 25-document R refit (-0.000),
  but +0.068 with R fitted on documents 25-49 and +0.059 with R at 100
  documents.

## Findings

1. Our pipeline reproduces the published J and R lenses, at the matrix level
   (every layer) and at the readout level.
2. The published lenses were fitted on the same 25 documents: our refits are
   3-10x (J) and 5-8x (R) closer to them than fits on different documents.
   Small residual differences remain for both lenses, proportionally similar
   from layer 8 up and about 1.7x larger for J in layers 0-3 (relative to
   each lens's document sensitivity). Cause not identified; plausibly a
   pipeline difference in the published fork.
3. R is 2-3x more stable than J, across document sets and from 25 to 100
   documents. This supports R as the primary readout lens.
4. At 25 documents, J's early layers are dominated by which documents are
   sampled (1 - cos 0.32 between document sets at layer 0).
5. For the readouts we report, lens-fitting uncertainty is small at the
   profile level (Spearman >= 0.98 at every layer checked; >= 0.998 at layer
   29), and large enough at middle layers (about +/-0.07 at layer 16) to make
   the sign of small family effects unreliable.

## Consequences for claims

- Layer-29 family results: unaffected.
- Relief lead at layers 16-18 and the relief/vitality crossover: unaffected
  (S2 relief gain about 0.55-0.67 at layers 16-18; a 0.06 shift in S1 relief
  does not move the S2-versus-S1 contrast meaningfully).
- The table behind `05-direct-semantics.md`
  (`direct_vs_downstream_families.csv`) lists -S1 relief at layer 16 as
  -0.01; under more robust R fits it is about +0.06. The note's text does
  not cite this value; a lens-fit note was added to `05` pointing here.
  The middle-layer values `05` does state (calm, generic positive) are far
  outside the uncertainty band and stand.
- Rule for the report: no claim rests on the sign of a middle-layer family
  effect smaller than about 0.1.

## Corrections made during this gate

- An R comparison table was first read under the wrong label (a pasted
  footer sat above its table): the "R on other documents" numbers were in
  fact R at 25 vs 100 documents. The temporary conclusion that J is 5-7x more
  document-sensitive than R was wrong; it is 2-3x.
- The early-layer J gap went through three readings: numerical sensitivity
  (ruled out by the environment-drift control), a J-specific fork difference
  (only partly), and data sensitivity with a shared residual (finding 2).

## Infrastructure notes

- The local 16 GB card spilled into shared system memory under WSL (CUDA
  sysmem fallback, now disabled) and is not used for fitting.
- RunPod's global network volume does not support permission changes and
  produced empty files through the Hugging Face cache and its Xet chunk
  cache. Working rule: caches, environments and model weights on container
  disk, verified by checksum; the volume holds whole artifacts only.
  Setup is scripted (`tools/runpod/`), locked, and reports its own state.
- The local lens session was rebuilt from a generated bootstrap
  (`lens_session_bootstrap.py`, verbatim from `03-decursed` cells 8-10). Its
  first version dropped two decorators; the readout gate (exact reproduction
  of stored published readouts) confirmed the patched session.

## Artifacts

`runs/qwen35-4b-posttrained-s2/paper_protocol/lens_calibration/`:
`l0_published_lens_provenance.json`; `refit_*.json` (recipe, environment,
per-layer comparison, refit hash) for J n25 (BOS on/off, two environments),
R n25, J and R on documents 25-49, J and R at n100; `compare_*.json` and
`env_drift_J.json`; `readout_bar.csv` and `readout_bar.json`;
`env-fast.lock.txt`; fit logs. Refit `.pt` files (about 390 MB each) are not
committed; they are in `bulky_artifacts_manifest.json` by sha256.

## Next

Gate 0 (4B evidence freeze, writing) and Gate 1 (post-trained button run).
