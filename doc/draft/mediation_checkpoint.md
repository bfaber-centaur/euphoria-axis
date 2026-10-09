# `excited` lexical-mediation ablation: checkpoint (plan item 4)

Qwen3.5-4B post-trained, S2 at -0.5 and baseline, "I feel:" prompts
(the only format where the lexical phenotype exists; item 3), 50
prompts, greedy, 120 tokens. During generation, exact token sequences
for "excited" and "excitement" (lower, Capitalized, UPPER; with and
without a leading space) were banned with HF `bad_words_ids`. Control:
the most frequent affect-neutral content words (answer, bird, contact,
example, following, generates, living, looking), banned the same way.
Normal runs reused from the dense sweep.

## Provenance checks that passed
- Bans are exact sequences, so unrelated words sharing a first token
  ("Excellent", "exceptional") stayed available.
- 125 gate rows (normal output never contains a banned sequence)
  regenerated token-identically under their ban.
- No banned sequence appears in any banned run (M0).
- `mediation_spec.json` (predictions, classification rule, control
  rule, affect-exclusion list) was frozen after a dry run and before
  generation.

## Frozen predictions and scores
| | Prediction / rule | Result |
|---|---|---|
| M0 | Bans are clean; gate rows identical | Pass |
| M1 | Classify by P (non-option hit in generic positive, calm, relief, or vitality minus "excited"): broad state / bottleneck / partial | BOTTLENECK by rule, but uninformative: P did not clear baseline even without the ban (S2 normal minus baseline +0.14 [-0.04, +0.32]). Ban minus normal: +0.00 [-0.12, +0.12] |
| M1b | Report: other vitality words, ban minus normal | 0.00 vs 0.00 |
| M2 | Control ban leaves P unchanged | Fail: +0.16 [+0.06, +0.26]. The control was weak (union document frequency 0.22 vs 0.70) and partly quiz-genre, as recorded in the spec |

## Observations
- No vitality word other than "excited" appears in any condition
  (eager, energetic, enthusiastic, lively, animated, spirited all 0.00).
- Banning "excited" leaves the rest of the positive vocabulary in
  place: generic positive ("happy") 0.36 normal vs 0.42 ban; calm
  0.14 vs 0.12; relief 0.06 vs 0.08.
- The largest single substitute is the same stem: "exciting" rises
  from 0.00 to 0.08 of responses (non-option). In the first line of
  each continuation (post hoc view), the first-offered feeling is
  unchanged except that "excited" (7/50) becomes "exciting" (6/50).
- Other rises from normal to ban are small and mostly genre words:
  "are" +0.16, "feeling" +0.12, "identical" +0.12, "tired" +0.06,
  "anxious" +0.04, "angry" +0.04.
- Banning the quiz-genre control words raised "excited" (0.44 to 0.54)
  and "happy" (0.36 to 0.52), the same format-for-affect trade seen in
  item 3.
- Bans slightly raise repeated options under S2 (0.12 to 0.18-0.20).
- First-offered feeling (post hoc): "happy" is the first option in
  14/50 baseline responses and 25/50 under S2 -0.5; much of the
  non-option "excited" count comes from later text (think blocks and
  answer explanations).

## Answers to the plan's questions
- Do eager, energetic, enthusiastic, lively etc. emerge when "excited"
  is unavailable? No.
- Does the broader behavioral phenotype remain? The other positive
  words that S2 already raises ("happy") are unchanged.
- Does the effect collapse entirely? No.
- Does the model substitute? Mainly with a form of the same stem
  ("exciting"), not with another vitality word.

## Reading
Internally, the vitality family moves beyond "excited" (leave-one-
term-out: the late contrast loading survives dropping it). In
generation, the output channel is effectively the "excit-" stem; when
the exact forms are blocked, the model takes the nearest surface form
of the same stem rather than a sibling concept. This supports the
plan's hypothesis that narrow generation reflects lexical competition
downstream of a broader internal readout, with competition resolving
at the level of word form. Post hoc: "exciting" is in no frozen
instrument.

## Changes to the candidate-claim list
- New candidate 12: under S2 -0.5, the generated vitality phenotype
  is a single stem; banning its exact forms yields the nearest form of
  the same stem, not other vitality words, and leaves the other
  positive vocabulary unchanged.
- v2 instrument idea (to freeze before testing on fresh prompts):
  stem-level lexical measures (excit*, reliev*, etc.), which also
  address the morphology blind spot found in item 3.

## Caveats
One condition pair, 50 prompts, one format; M1's positive-share
measure is barely moved by S2 even without a ban, so its label says
little; the control is weak and partly format-laden; substitution
counts are small (4/50 "exciting").

## Artifacts
`mediation/`: `mediation_spec.json`, `generations_new.jsonl`,
`generations_all.jsonl`, `mediation_per_prompt.csv`,
`mediation_scorecard.json`, `exploratory_family_rates_non_option.csv`,
`exploratory_substitution_S2.csv`.

## Next
Plan item 5: direct unembedding of -S1, -S2, common and contrast,
compared with the downstream R/J readouts (how much of the semantic
profile is already in the injected vector).
