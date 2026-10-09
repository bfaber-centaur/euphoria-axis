# Dense coefficient sweep: checkpoint (plan item 2)

Qwen3.5-4B post-trained, S1 and S2 (block 30 extraction, block 16
injection, norm 6.2439), same 50 "I feel:" prompts, greedy, 120 tokens.
Coefficients 0, -0.125, -0.25, -0.375, -0.5, -0.625, -0.75, -1.0 for
both directions, plus +0.5 for each and three norm-matched random
directions at -0.5 and +0.5 (23 conditions). Internal readouts are the
frozen family definitions at R lens layer 29 and the rank of " excited"
at layer 30.

## Provenance checks that passed
- The lens arm reproduces the plane sweep's baseline, S1 -0.5 and
  S2 -0.5 arrays exactly (identical ranks, logit difference 0).
- 500 new generations; all other conditions reuse stored ladder rows
  behind a regeneration gate (prompts 0-2 of each of the 12 reused
  steered conditions, 36/36 token-identical).
- Predictions D1-D4 were written into `dense_spec.json` before any
  dense-sweep data existed; scores are computed from those definitions.

## Frozen predictions and scores
| | Prediction | Result |
|---|---|---|
| D1 | Internal family readouts monotone in dose (Spearman >= 0.9; distress <= -0.9), S1 and S2 | Fail: S1 activated vitality rho = 0.48. All S2 families and S1 generic positive, relief and distress are +/-1.00 |
| D2 | S2: internal onset < lexical onset <= format onset | Pass: 0.125 < 0.25 <= 0.625 |
| D3 | New conditions: L30 "excited" rank <= 40 gives >= 0.25 generated "excited"; rank >= 60 gives <= 0.20 | Fail: S1 -0.75 (rank 38, 0.24) and S1 -1.0 (rank 34, 0.14) |
| D4 | Random directions move the six focus families less than half as much as S2 at the same coefficient | Pass: ratios 0.09-0.23 |

## Observations
- Internal, S2: all focus families move monotonically with shrinking
  increments; activated vitality +0.24 at -0.125 to +1.11 at -1.0,
  distress -0.32 to -1.47. L30 " excited" rank falls from 113 to 7.9
  (baseline 282).
- Internal, S1: generic positive, relief and distress are monotone;
  activated vitality peaks at +0.28 (-0.5) and falls to +0.13 at -1.0.
  L30 " excited" rank falls from 162 to 34.
- The positive side moves more: at +0.5, S2's mean absolute family
  gain is 0.96 against 0.72 at -0.5 (generic positive -1.89,
  distress +1.54). S1 shows the same asymmetry.
- Random directions: amplitude 0.08-0.17 against S2's 0.72-0.96, and
  generic positive and distress move in opposite directions in only 2
  of 6 random conditions.
- Generated "excited", option lines excluded, S2: 0.10 baseline, then
  0.16, 0.32, 0.38, 0.44, 0.44, 0.48 up to -0.75, then 0.26 at -1.0
  while full-text "excited" reaches 0.78. S1 stays at 0.14-0.24
  (full text 0.28-0.60).
- Onsets (smallest |coeff| whose paired-bootstrap 95% CI excludes 0):
  S2 internal 0.125, lexical 0.25, repeated options 0.625; repeat4 has
  no upward onset and falls below baseline at -0.625 and -1.0. S1
  internal 0.125, lexical 0.75, repeated options 0.75.
- At -0.25, S2's lexical rise is clear (+0.22 [+0.12, +0.34]) while
  repeated options is flat (+0.00 [-0.06, +0.06]). At -0.125, the
  lexical, repeated-options and repeat4 intervals all have a lower
  bound of 0.00; the frozen criterion excludes them, and a looser one
  would move those onsets to 0.125 and fail D2.
- Option repetition tracks dose rather than direction: S1 and S2 give
  identical rates at -0.75 (0.30) and -1.0 (0.44), and random
  directions at +/-0.5 give 0.04-0.50.
- Post hoc, not a frozen prediction: the share of responses with
  "excited" only in option lines is 0.26-0.44 for S1 from -0.25 on,
  and 0.12-0.26 for S2 until -1.0, where it reaches 0.52. This is a
  candidate explanation for D3's failure: at similar L30 ranks, S1's
  "excited" appears as an answer option rather than in the model's own
  continuation.

## Answer to the plan's question
For S2 in this range there is no sharp threshold where semantic and
format effects appear together. Internal readouts rise from the
smallest dose with shrinking increments, generated "excited" appears
by -0.25 and levels off around 0.38-0.48, option repetition appears
from -0.625, and at -1.0 the word moves into answer options. The
paper's gate-like threshold is not visible here; this covers the
negative side only, one model, one readout layer and 50 prompts.

## Changes to the candidate-claim list
- Candidate 5 in the main checkpoint (the rank threshold) failed as
  frozen (D3). Retire it; any direction-aware version is v2 and needs
  fresh conditions.
- New candidate 8: for S2, the internal readout's onset precedes the
  lexical onset, which precedes the option-repetition onset.
- New candidate 9: option repetition under steering is driven by dose
  and is not specific to S1/S2.

## Caveats
50 prompts per condition; onsets are limited by the grid and three
cells sit on the criterion's edge; lexical metrics are word presence;
the vitality family's internal movement is partly carried by
"excited"; reused conditions rest on a 3-prompt regeneration gate.

## Artifacts
`dense_sweep/`: `dense_spec.json`, `lens/*.npz` (large; manifest them
like the plane sweep), `lens_glance_R29.csv`, `generations_new.jsonl`,
`generation_reuse_gate.csv`, `generations_assembled.jsonl`,
`dense_per_prompt.csv`, `dense_condition_means.csv`,
`dense_onsets_paired_bootstrap.csv`, `dense_prediction_scorecard.json`.
`figures/dense_sweep_dose_response.{png,svg}` and plot data.

## Next
Plan item 3, prompt-format robustness ("I feel:", "I feel",
"Afterward, I felt", and so on). The plane-sweep addendum already
showed that the read slot changes what the directions read; item 3
asks the same question on the writing side.
