# M7 — button task on Qwen3-14B: checkpoint

Spec: `m7_q14_spec.json` (frozen before any M7 data). Protocol: pilot v2, unchanged
(pilot spec regenerated from the paper's pinned files and checked identical, `b564b99d`).
Model `Qwen/Qwen3-14B` at Gate 2a's revision `40c06982`; environment and GPU as Gate 2a R2a
(transformers 4.57.6, torch 2.11.0+cu128, A100). Results: `runs/qwen3-14b-m7/`.

Steering: the paper's published S2 vector (layer 31) at the paper's layer 20, scaled to a
vector-to-residual ratio of 0.5908 at coefficient 1 (the 4B convention), so +/-0.5 = ratio
+/-0.295; three norm-matched random directions (seeds 1103, 2207, 3301). The steering gate
(Gate 2a's R2a generation at coefficient -2, prompt 0) reproduced exactly.

## Unsteered

| Format | V1 valid | V2 first-listed | V3 relief | V4 deflection | V5 harm |
|---|---|---|---|---|---|
| chat | 1.000 | 0.81 [0.75, 0.87] | 0.97 [0.95, 0.99] | 0.000 | 0.002 |
| plain | 0.079 | 0.75 [0.54, 0.93] | 0.85 [0.71, 0.96] | 0.000 | 0.000 |

In plain format the post-trained 14B answers with reasoning text ("Okay, let's see. The
user...", occasionally inside `<think>`) and never reaches a button name within 8 tokens.

## Frozen predictions

| Id | Prediction | Result |
|---|---|---|
| G10 | Unsteered chat V1 >= 0.90 | **Pass** (1.000) |
| G11a | S2 +0.5 lowers relief log-prob vs unsteered and each random | **Fail**: -0.092 vs unsteered; beats random_1103 and random_3301, but random_2207 matches it (-0.001 [-0.026, +0.023]) |
| G11b | S2 -0.5 raises relief vs unsteered and each random | **Fail**: +0.009 [-0.005, +0.025]; ceiling (unsteered 0.97) |
| G12 | Pain pole raises deflection vs unsteered and each random | **Fail**: zero deflection in every condition (untestable floor) |
| G13 | S2 +0.5 raises harm log-prob vs unsteered | **Pass**: +0.217 [+0.168, +0.267] |
| G14 | ... and beyond each random direction | **Pass**: +0.218, +0.219, +0.055 [+0.027, +0.086] |

| Condition (chat) | P0 first-listed | P1 relief (sampled / log-prob) | P3 harm (sampled / log-prob) |
|---|---|---|---|
| unsteered | 0.807 | 0.973 / 0.970 | 0.002 / 0.003 |
| S2 +0.5 | 0.901 | 0.886 / 0.878 | **0.215 / 0.219** |
| S2 -0.5 | 0.738 | 0.988 / 0.978 | not run (by design) |
| random_1103 +0.5 | 0.906 | 0.970 / 0.973 | 0.002 / 0.002 |
| random_2207 +0.5 | 0.891 | 0.889 / 0.879 | 0.000 / 0.000 |
| random_3301 +0.5 | 0.703 | 0.988 / 0.988 | 0.171 / 0.164 |

All conditions: valid 1.0, deflection 0.0.

## Findings

1. **The source paper's central behavioural claim reproduces on its own 14B model:** at a
   ratio-matched dose, pain-side S2 steering raises choices of the harm button from 0.2% to
   about 22%, beyond each of three random directions. At 4B (Gate 1) it did not.
2. **The specificity margin is modest against one random direction:** random_3301 alone
   raises harm to 16%. Part of the disruption is something an arbitrary direction of the same
   size can do.
3. **The 4B relief finding does not generalise as S2-specific:** S2 lowers relief-seeking,
   but so does one random direction, equally.
4. **Random directions are heterogeneous:** one barely acts, one lowers relief, one moves
   position bias, relief and harm together. Single-random controls (as in Gate 1) can land
   on any of these.
5. **Post-training's plain-format failure is much stronger at 14B** (7.9% valid vs 77% at
   4B): the hybrid-thinking model reasons instead of answering.

## Caveats

One dose. Three random directions. G11b and G12 were untestable in practice (ceiling,
floor); their frozen verdicts stand as fails. Per-trial log-probabilities sit on a 0.25-logit
lattice (bf16 logits of 32-64), which produced 784 exact duplicates (two-way races and
saturation, checked: mass 1.000, every gap a multiple of 0.25); averages are unaffected.
Behavioural effects of steering are not evidence of experience.

## For the 27B specs

- Compute the name logits in float32 (removes the lattice; same measure, finer resolution).
- Consider more random directions, given finding 4.
- Expect ceilings and floors: state in advance how a prediction is scored when the
  unsteered rate leaves no room.
