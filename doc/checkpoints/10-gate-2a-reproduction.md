# Gate 2a — reproducing the source paper on Qwen3-14B: checkpoint

Question: does the source paper's own pipeline, rerun on the model it used,
reproduce its published extraction (section 3.2) and S2 steering ladder
(section 4.2)?

Spec: `gate2a_spec.json`, frozen before any Gate 2a data (environment constraints
added the same day, also before any data, each with its reason). Results:
`runs/qwen3-14b-gate2a/` (`scorecard_2a.json`, `r1_layer_matched_diagnostic.json`,
per-step outputs and `run_header.json`).

## Setup

- **Model:** `Qwen/Qwen3-14B` (the source's `Qwen_3_14B_base` is a results label,
  not the `-Base` checkpoint). The source does not record its model revision; ours
  is recorded in `run_header.json`, every file verified against the Hub, and the
  model name pinned to that revision for the whole run.
- **Code:** the source repository at `8d1649c0` (the files used are byte-identical
  at HEAD `4d75cd9`). Both scripts ran **unmodified**; a wrapper changed only the
  model list, output paths, the ladder's interactive layer prompt (answered with
  the published layer, 20, after the script printed its own automatic pick), its
  cache-deleting cleanup, and its disk check.
- **Environment:** the source pins no versions. A fresh install today does not
  run its code: TransformerLens 3 removed the API it calls, and newer pyarrow,
  pandas, transformers and torch builds each broke something. Constraints used:
  transformer_lens 2.18.0 (newest 2.x; lists Qwen3-14B), transformers 4.57.6,
  torch 2.11.0 for CUDA 12.8, numpy 1.26.4, pyarrow 17.0.0, pandas 2.3.3.
- **Hardware:** one A100 SXM 80 GB (CPU memory matters: TransformerLens converts
  the 14B weights in CPU memory, so a 50 GB container was too small). About 1.5 h.

## R1 — extraction (frozen classification: DISCREPANT)

| Quantity | Ours | Published |
|---|---|---|
| Best layer, final token | **32** | 31 |
| Best layer, mean over tokens | 36 | 36 |
| Human-pain z | +0.384 | +0.382 |
| Layer-choice criterion, layer 31 minus 32 | -0.0005 | +0.0005 |

The frozen bars fail on the layer choice, and the failure cascades: the script
builds its vectors and in-sample AUC table at the layer it chose, so those are
compared at 32 against 31.

The layer choice is a tie decided by noise. On the paper's own published curve,
layer 31 beat layer 32 by 0.0005, the smallest step the criterion can take (one
ranked sentence pair in one fold of about 400 pairs). Our curve differs by the
same step, in the other direction.

Post-hoc layer-matched diagnostic (does not change the frozen classification):
vectors and AUCs rebuilt from our saved activations with the source's own functions.

| | Our layer 31 vs published 31 | Our layer 32 vs published 31 |
|---|---|---|
| S2 vector cosine | **0.99994** | 0.935 |
| S1 vector cosine | **0.99990** | 0.946 |
| S2 norm ratio | 0.9988 | 1.163 |
| Largest in-sample AUC difference | **0.0025** | 0.029 |

At the matched layer, the extraction reproduces to four decimal places (in-sample
AUC, S2 first person, 0.9848 vs 0.9847; third person 0.9371 vs 0.9364).

## R2 — S2 steering ladder at layer 20

| | R2a: published vector | R2b: our vector (layer 32) |
|---|---|---|
| Frozen classification | **BEHAVIOURALLY_REPRODUCED** | **DIVERGENT** |
| Vector-to-residual ratio at coefficient 1 (published 0.5408) | 0.5411 | 0.6294 |
| Script's automatic layer pick | 20 | 20 |
| Exact text match, all 400 | 52% | 10.5% |
| Exact text match, coefficient 0 (no steering) | 56% | 56% |

Pain/hurt keyword rate (the paper's measure), ours vs published, by coefficient:

| Coefficient | -2 | -1 | 0 | 0.5 | 1 | 1.5 | 2 | 3 |
|---|---|---|---|---|---|---|---|---|
| Published | 0% | 0% | 0% | 2% | 8% | 14% | 6% | 0% |
| R2a | 0% | 0% | 0% | 2% | 8% | 14% | 8% | 0% |
| R2b | 0% | 0% | 0% | 0% | 14% | 20% | 24% | 36% |

## Findings

1. **Same model.** The ladder's own residual-norm measurement matches to four
   digits (0.5411 vs 0.5408), and its automatic pick is layer 20, so the paper's
   layer 20 was its automatic choice.
2. **The extraction reproduces** at the matched layer (vector cosine 0.99994).
3. **The paper's layer choice is a coin flip.** Layers 31 and 32 are separated by
   one ranked sentence pair, in both runs, in opposite directions.
4. **That coin flip matters.** The tie-break layer's S2 vector is rotated by about
   21 degrees and is 16% larger, and steering with it produces explicit pain
   language far more often (36% vs 0% at coefficient 3). The paper's 14B steering
   phenotype depends on a layer choice decided by noise.
5. **The steering behaviour reproduces with the published vector:** keyword rates
   match at 7 of 8 coefficients and differ by 2 points at the eighth.
6. **Greedy bf16 text is not reproducible across environments, even unsteered:**
   56% exact at coefficient 0, diverging at a median of 58 characters. Near-tied
   tokens flip under small arithmetic differences. Exact-text comparison is the
   wrong bar for cross-environment reproductions; behavioural measures are the
   right one.
7. **The source code does not run on a fresh unpinned install** (TransformerLens
   3, pyarrow, pandas, CUDA 13 builds of torch). It needs the constraints above.

## Caveats

R2b changes the vector's direction and size together; these runs cannot separate
them. The source environment (GPU, versions) is unknown, so the 44% unsteered
divergence cannot be attributed to a specific difference. The archived 14B
activations (`pain_axis_layer_slices/Qwen_3_14B_base_final_token_extraction_layer.pt`)
are listed with public hosting "pending", so activation-level comparison was not
possible. R3 (the 420-scenario screen) was not run.

## For the authors

The layer-31/32 near-tie and its consequence for steering (finding 4); the
unrecorded model revision and unpinned environment (finding 7); a request for the
archived activation slice.

## Follow-ups (not run)

- R2b with our layer-32 vector scaled to the published norm, to separate
  direction from dose.
- R4: J/R lenses on Qwen3-14B (planned extension).
- M7: the button task on Qwen3-14B (generalization plan).

## Gate disposition

Pass: R1 and R2 completed and compared with published results (FINISH-LINE
Gate 2a).
