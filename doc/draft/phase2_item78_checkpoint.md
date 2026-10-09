# Held-out 1P/3P matched pairs x suffix: checkpoint (plan items 7-8)

Qwen3.5-4B post-trained, unsteered. 59 sets of four sentences (pain
and control, first and third person), drafted blind by a separate
context and validated mechanically (one set dropped: "ready" is a
frozen probe term). Each sentence is read with two suffixes: the slot
("I feel:" / "They feel:") and prose ("Afterward, I was" / "Afterward,
they were"): 472 prompts. Readouts at the final token: projections at
block 30 onto S2, S1, common and contrast (z relative to the S2 source
set, as in 5e), and the frozen families through the R and J lenses at
layers 22 and 29. Main statistic per set: (pain 1P - pain 3P) -
(control 1P - control 3P); 95% intervals from bootstrap over sets.

## Provenance
- `item78_spec.json` froze the set hash, design notes, and E1/E2
  before any readout.
- Gates passed: projecting 8 source sentences reproduced 5e (max
  difference below 1e-6 scale); two plane-sweep baseline prompts
  reproduced the stored lens ranks exactly.
- Design notes kept as agreed: some controls are mildly positive;
  in 5 of 12 physical sets the body part appears only in the pain
  version; third person is singular "they".

## Frozen predictions and scores
| | Prediction | Result |
|---|---|---|
| E1 (item 7) | Slot suffix: S2 interaction > 0, CI excluding 0 | Pass: +0.133 [+0.054, +0.216] |
| E2 (item 8) | Classify by the prose suffix | SLOT-MEDIATED: prose +0.010 [-0.052, +0.073]; slot - prose +0.122 [+0.041, +0.205] |

## Observations (pre-specified report)
- S2 separates pain from control on these held-out items in both
  formats: +0.555 z (slot), +0.468 z (prose). The 1P-3P main effect
  is +0.135 (slot) and +0.077 (prose).
- In prose the interaction cancels on S2 rather than vanishing across
  the plane: contrast flips sign between suffixes (slot +0.111
  [+0.007, +0.216]; prose -0.132 [-0.216, -0.050]); S1 shows a prose
  interaction (+0.123 [+0.030, +0.218]); common is +0.064
  [-0.011, +0.139].
- Slot interaction on S2 by category (descriptive, n = 11-12):
  psychological +0.42, cognitive +0.22, physical +0.07, social +0.01,
  moral -0.07.
- Lens family readouts (next-token availability, not the
  representation): in the slot, the inhibition/defeat interaction is
  negative (R29 -0.363 [-0.494, -0.232]; similar at J29, R22, J22) and
  distress slightly negative. Pain items lower generic-positive
  availability by about 1.0 at layer 29 in both formats.

## Reading
The earlier 1P/3P motif replicates in sign on fresh, blind-drafted
items, at about a fifth of the earlier estimate (which used different
items and construction). By the plan's rule it is heavily syntax- or
task-mediated for S2: it is present with the "feel:" slot and absent
with a prose continuation. In prose, the experiencer interaction
appears along S1 and the common axis while its contrast component
reverses sign, which is what cancels it on S2. It is not a
general-purpose experiencer signal on S2.

## Plan decision
Item 9 (generic-person residualization) was conditional on the
held-out signal surviving. It survives only in the slot and is small;
by the plan's stopping rule, Phase II stops here.

## Changes to the candidate-claim list
- New candidate 16: S2 separates pain from matched non-pain events on
  blind-drafted held-out items, with and without the "feel:" slot
  (about +0.5 z).
- New candidate 17: the S2 pain x person interaction replicates on
  held-out items in the "feel:" slot (+0.13 z) and is absent with a
  prose suffix.

## Caveats
Unsteered readouts at one token and one block for projections; 59
sets; the third-person suffix "They feel:" can be read as plural;
per-category values are descriptive; the family readouts and the
projection measure different things and need not agree; many
report-only intervals, not corrected for multiplicity.

## Artifacts
`phase2_matched_pairs/`: `matched_pairs_validated.jsonl`,
`validation_report.json`, `item78_spec.json`,
`item78_projections.csv`, `item78_lens_ranks.jsonl`,
`item78_all_readouts.csv`, `item78_scorecard.json`,
`item78_report_table.csv`. Blind prompt and validator:
`blind_matched_pairs_prompt.md`, `validate_matched_pairs.py`.

## Next
Phase III: freeze 4B. Synthesis of robust, fragile and
instrument-limited results; frozen instruments list; expected 27B
outcomes and what would count as a meaningful failure to replicate.
