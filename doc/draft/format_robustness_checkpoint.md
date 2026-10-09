# Prompt-format robustness: checkpoint (plan item 3)

Qwen3.5-4B post-trained, S1 and S2 (block 30 extraction, block 16
injection, norm 6.2439). The same 50 stems in four frozen formats:
F0 "... I feel:", F1 "... I feel", F2 "... Afterward, I felt",
F3 "... What happened next was". Conditions per format: baseline,
S1 and S2 at -0.25 and -0.5, and three norm-matched random directions
at -0.5 (lens arm only). Internal readouts are the frozen families at
R lens layer 29, measured at each format's final prompt token, against
that format's own unsteered baseline. F0 is reused from the dense
sweep.

## Provenance checks that passed
- F0 generation reuse gate: 15/15 regenerated rows token-identical to
  the dense sweep.
- 24 new lens conditions and 750 new generations under
  `format_spec.json`; confirmatory predictions and the exploratory
  report were written into the spec before any data existed.
- Every F0 condition is taken from the dense sweep's frozen arrays and
  rows (hash-checked).

## Confirmatory predictions and scores
| | Prediction | Result |
|---|---|---|
| C1 | In F1-F3, S2 -0.5 raises vitality and generic positive, each at least half its F0 value | Fail on F3 generic positive (ratio 0.441). F3 vitality passes at 0.501. F1 and F2 pass (ratios 0.72-1.43) |
| C2 | S2 -0.5 minus S1 -0.5 vitality gain positive in every format | Pass: F0 0.48, F1 0.88, F2 0.87, F3 0.35 |
| C3 | At baseline, format-like top-50 fraction (R28) and generated option count lower in F2 and F3 than F0 | Pass: format-like -0.64 and -0.73; option count -5.2 and -5.3 |
| C4 | In F1 and F2, S2 -0.5 raises non-option "excited"; in F2, S2 exceeds S1 | Fail: F1 +0.08 [0.00, 0.18], F2 +0.02, F2 S2-S1 +0.04 [0.00, 0.10] |
| C5 | Random directions at -0.5 move the six focus families less than half as much as S2, for at least 2 of 3 randoms per format | Pass: ratios 0.09-0.29 in F1/F2, 0.30-0.35 in F3 |

## Observations
- Internal vitality gain under S2 -0.5 is 0.76 (F0), 1.06 (F1),
  1.08 (F2), 0.38 (F3); at -0.25 it is 0.44, 0.53, 0.55, 0.16. All
  intervals exclude 0, including S1 at both doses.
- Generated "excited" outside option lines rises clearly only in F0
  (0.10 to 0.44 at -0.5; 0.32 at -0.25). In F1-F3 it stays at
  0.00-0.12 in every condition.
- The generated vitality family equals "excited" in every format
  (no other vitality word appears outside option lines).
- The "I feel:" colon recruits answer-slot structure: at baseline the
  R28 top-50 is 79% format-like tokens in F0 against 7-15% in F1-F3,
  and F0 responses average 6.0 option lines against 0.66-0.94.
  Steering raises option count in F2 (0.78 to 2.18) and F3 (0.66 to
  1.72) even without the colon.
- In F3, " excited" is not a plausible next token (baseline L30 rank
  about 41,000; about 16,700 under S2 -0.5), yet the vitality family
  still moves internally (+0.38).
- Unsteered read slot (block 30, per-stem difference vs F0): F3 reads
  +1.40 on contrast and +0.70 on S2; F1 and F2 shift +0.27 to +0.39
  on every axis.
- Exploratory lexical table (S2 -0.5 minus baseline, non-option): the
  only interval excluding 0 outside F0 is relief_release in F1
  (+0.12).

## What the frozen instrument misses (text inspection, not scored)
- Plain-text continuations are largely pretraining genre in every
  format, baseline included: fill-in-the-blank quizzes with A-D
  options, exam questions in Chinese, repeated listing spam, leaked
  `<think>` blocks, looping narratives.
- Steered text contains positive-affect words the frozen vocabulary
  does not match: "a little bit of excitement" (F1), "very happy"
  followed by four identical options reading 高兴 ("happy") (F1),
  "relieved" repeated across option lines (F2).
- The frozen vocabulary is English, whole-word and adjectival; it
  cannot see derived forms or non-English output. C4's failure is
  partly an instrument limit. `psych_vocab_v1` stays frozen; any
  broader lexical measure is a new versioned instrument.

## Reading
Within the frozen English vocabulary, the generated "excited"
phenotype depends on the "I feel:" answer-slot genre. The internal S2
readout does not: it is present in every format and larger without
the colon (F1, F2), and the S2-versus-S1 difference is present in
every format. This is the plan's "particularly informative outcome":
internal structure that survives while generated vocabulary changes a
lot with the prompt. One model, one readout layer, 50 stems.

## Changes to the candidate-claim list
- New candidate 10: S2's internal family readout at the prompt's final
  token does not require the "I feel:" answer slot (C1 in F1 and F2,
  C2 in all formats).
- New candidate 11: within `psych_vocab_v1`, the generated "excited"
  phenotype is conditional on the "I feel:" format (C3 pass, C4 fail).
- Candidate v2 lexical instruments, to be defined and frozen before
  testing on fresh stems: morphological variants of the vitality and
  relief families; a relief-family prediction for "I feel" (F1); a
  non-English affect check.

## Caveats
One model, one readout layer, 50 stems per format; the internal
readout is taken before any generated token, so it says nothing
about what the model writes later in a response; formats differ in
more than the answer slot (tense, narrative framing); F3's C1 result
sits on the threshold for vitality; random-direction ratios are
higher in F3, where S2's own effect is smallest.

## Artifacts
`format_robustness/`: `format_spec.json`, `read_slot_projections.csv`,
`lens/*.npz` (large; manifest them), `lens_glance_R29.csv`,
`generation_reuse_gate.csv`, `generations_new.jsonl`,
`generations_assembled.jsonl`, `format_generated_per_prompt.csv`,
`format_confirmatory_scorecard.json`, `exploratory_family_hits.csv`,
`exploratory_topk_format_like.csv`.
`figures/format_robustness_internal_vs_lexical.{png,svg}` and plot data.

## Next
Plan item 4, the "excited" lexical-mediation ablation. These results
scope it: the lexical path exists mainly in F0, so the ablation is
most informative there, with F2 as the comparison where the internal
effect is present without the word.
