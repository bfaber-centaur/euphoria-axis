# R4 — J/R lenses for Qwen3-14B and readouts on the S2 ladder: checkpoint

Spec: `doc/protocols/lenses/r4_q14_spec.json` (frozen before any R4 data). Model `Qwen/Qwen3-14B` at Gate 2a's
revision `40c06982`, verified file by file. Main fast environment (torch 2.11.0+cu128, transformers 5.19.0), A100.
Results: `runs/qwen3-14b-r4/` (the three lenses, about 2 GB each, stay on the RunPod volume; their sha256 values
are in the fit JSONs).

## Fits

The published 4B recipe: first 25 pile-10k documents, 128 tokens, `skip_first` 4, target layer 38 (n - 2),
`force_bos` off. J: official `jlens.fit`. R: the same estimator through the Gate L RelP rules, verbatim (LN rule on
block norms, identity on SiLU, half rule at 0.5; QK norms excluded; Qwen3 has no gated norms). The R fits passed the
rule self-tests and the bit-identical forward check, the rules' first run outside the Qwen3.5 architecture. A second
R fit on documents 25-49 measures document sensitivity. About 50 minutes per lens.

## Validation (no published 14B lens exists)

| 1 - cos | Layer 0 | Layer 16 | Read layer (14B: 37; 4B: 29) |
|---|---|---|---|
| J vs R, 14B | 0.648 | 0.230 | 0.0046 |
| J vs R, 4B | 0.307 | 0.112 | 0.004 |
| R vs R on other documents, 14B | 0.019 | 0.024 (peak 0.034 at layer 8) | 0.0003 |
| R vs R on other documents, 4B | 0.117 | 0.013 | 0.0003 |

Same overall shape as 4B: J and R differ early and converge at the read layer, where both lenses are as stable as
4B's at layer 29. At 14B, J and R differ about twice as much through the early and middle layers, and R is about
6x less document-sensitive at layer 0 but somewhat more in the middle layers.

## Readout on the reproduced ladder

The paper's 50 neutral prompts (identical to the 4B ladder's); the published S2 vector (layer 31) at layer 20,
scaled to ratio 0.5908 at coefficient 1 (raw ratio measured 0.5411, published 0.5408); three random directions at
-0.5; final prompt token, all layers, J and R. Probes rebuilt for the Qwen3-14B tokenizer from the unchanged
`psych_vocab_v1` (count and list: `r4_probe_terms.csv`).

R-lens family gains at layer 37 (mean over prompts of log rank improvement vs baseline):

| Family | S2 +0.5 | S2 -0.5 | random_1103 | random_2207 | random_3301 |
|---|---|---|---|---|---|
| distress_self_devaluation | **+2.069** | **-1.161** | +0.314 | +0.293 | +0.001 |
| inhibition_defeat | +1.228 | -0.887 | +0.470 | +0.436 | +0.045 |
| calm_positive | **-1.412** | **+0.775** | +0.511 | +0.622 | +0.058 |
| generic_positive | -0.818 | +0.174 | +0.277 | +0.155 | -0.430 |
| activated_vitality | -0.714 | +0.437 | +0.392 | +0.347 | -0.296 |
| relief_release | -0.614 | +0.114 | +0.029 | +0.113 | +0.333 |
| competence_success | +0.328 | -0.650 | +0.097 | -0.046 | +0.081 |
| agency_assurance | -0.095 | -0.541 | +0.478 | +0.214 | +0.078 |
| approach_drive | -0.046 | -0.206 | +0.569 | +0.130 | -0.148 |

**R4-P1 (frozen): PASS, narrowly.** Mean focus-family amplitude of each random direction relative to S2 -0.5:
0.78, 0.48, 0.49 (two of three under 0.5). At 4B the same comparison gave 0.09-0.23.

## Exploratory (post hoc): profile structure

| | Correlation with the S2 -0.5 profile | Families moved the same way | Mean signed gain |
|---|---|---|---|
| S2 +0.5 | **-0.94** | 6 of 9 | -0.008 |
| random_1103 | +0.08 | **9 of 9** | +0.349 |
| random_2207 | +0.32 | 8 of 9 | +0.252 |
| random_3301 | -0.24 | 6 of 9 | -0.031 |

S2's two poles are mirror images; the random directions are uncorrelated with S2's profile and mostly lift the
whole vocabulary at once. The frozen amplitude rule cannot see this difference; a profile-structure measure can.

## Findings

1. Our lens pipeline runs on a second architecture: the RelP rules pass their self-tests and the exact-forward
   check on Qwen3, and the lenses validate internally with a shape similar to 4B's.
2. On the reproduced ladder, S2's pain side raises distress and defeat vocabulary and lowers calm, positive,
   vitality and relief vocabulary at layer 37; the positive pole mirrors it, with calm leading (as the direct
   unembedding at 4B, "calm above vitality").
3. By the frozen amplitude rule, S2's specificity over random directions is much weaker at 14B than at 4B (passes
   by hundredths).
4. Exploratory: the difference between S2 and random directions at 14B is mostly in structure, not size. S2 moves
   families in a signed, dose-symmetric pattern; random directions shift the whole vocabulary one way.
5. Exploratory: the positive pole lowers agency and competence vocabulary at 14B, where the 4B phenotype centred
   on vitality.

## Caveats

One dose; three random directions; one read position (final prompt token) and, for the table, one layer; lenses
fitted on 25 documents (middle-layer readouts carry document-sensitivity up to about 0.03 in 1 - cos). The link
between finding 2 and M7's behaviour (relief-seeking down, harm up on the pain side) is qualitative; M7 also showed
a random direction lowering relief-seeking. Profile-structure results are post hoc. Lens readouts describe
vocabulary rankings, not experience.

## For the 27B specs

Freeze a profile-structure measure (correlation with the opposite pole, and sign-consistency of the random
profiles) alongside the amplitude rule.

## Follow-up (separate project)

Publish the three 14B lenses on Hugging Face with the recipe, RelP rules, validation numbers and hashes.
