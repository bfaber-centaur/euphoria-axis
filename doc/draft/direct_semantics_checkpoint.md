# Direct-vector semantics vs downstream semantics: checkpoint (plan item 5)

Qwen3.5-4B post-trained. Each vector is unembedded as it was injected
in the plane sweep: -S2 (S2 at -0.5), -S1 (S1 at -0.5), -common
(0 degrees) and -contrast (90 degrees), all at norm 6.2439. Primary
readout: the raw unembedding matrix times the vector, as in the source
paper; secondary: the same with the final-norm gain applied. Direct
scores are z-scored over the full 248,320-token vocabulary.
Downstream scores are the plane sweep's R/J lens log-rank gains at the
final prompt token, from the arrays already on disk.

## Provenance
- `direct_spec.json` (V1, V2, sign convention, both readouts) frozen
  before computing.
- Final norm used: `model.norm` (mean gain 3.2). Raw and norm-gain
  readouts agree to within 0.1 in every family score, so the choice
  does not matter here.

## Frozen predictions and scores
| | Prediction | Result |
|---|---|---|
| V1 | direct(-S2) ranks calm_positive above activated_vitality (from the source paper's unembedding result) | Pass: calm +1.58, vitality +0.54 |
| V2 | Probe-level agreement (r over 60 probes) between direct(-S2) and downstream R-lens gain is higher at layer 16 than at 29 | Pass: 0.90 vs 0.79, difference CI [+0.04, +0.20] |

## Observations
- Direct top words reproduce the source paper's unembedding claims in
  this model. +S2 (the suppressed end of -S2) promotes empty, void,
  forever, suicidal, shame, rejection, failures, flawed, rejected,
  humiliating, painful, hollow. -S2 promotes concern, worries,
  relaxation, relax, together with excit-, excited, excitement.
  +S1 promotes Pain, painful, Pressure, stabbing, acute, stabbed.
- " excited" is at vocabulary rank 33 (z +4.37) in the direct readout
  of -S2; downstream R29 gain +2.06.
- Family order in the vector (-S2): relief 1.64, calm 1.58, generic
  positive 1.38, vitality 0.54; distress -3.22. Downstream at R29:
  generic positive 1.14, relief 0.83, vitality 0.76, calm 0.59.
  Calm is strong at the injection layer (1.08 at L16) and fades by
  L22 (0.46); generic positive rises from 0.61 (L16) to 1.14 (L29).
- Probe-level agreement between vector and downstream readout stays
  high throughout: -S2 0.90 (L16), about 0.75 at L24-26, 0.82 at L30;
  -S1 and -common are similar; J lens matches R.
- The contrast axis has the lowest agreement (0.49-0.79). Sign
  convention (corrected after first commit): every condition injects
  the negative of its named direction, so -contrast is what the plane
  sweep's 90-degree, S2-ward condition injects. Its direct unembedding
  promotes urgency, emergency, hurry, panic, anxious, speed. The
  contrast unit vector itself, the direction reading-side projections
  use, unembeds to deserved, honour, forgiveness, purity, hypocrisy,
  karma. That matches the reading side (5e): projections onto it were
  high for moral injury and social pain and low for fear and physical
  pain.

## Answer to the plan's question
Most of the semantic profile is already present in the injected
vector (probe-level r about 0.75-0.90 at every layer after injection).
Downstream processing reweights within it: the calm component fades
after the injection layer while generic positive and vitality grow
late. The "excit-" stem that dominates generation (item 4) is already
near the top of the vector's own unembedding.

## Changes to the candidate-claim list
- New candidate 13: the source paper's unembedding claims (S2
  suffering vocabulary; S2's negative end mixing calm/relaxed with
  concern; S1's sensory vocabulary) reproduce in Qwen3.5-4B.
- New candidate 14: the probe-level semantic profile of the steering
  effect is largely present in the injected vector (r >= 0.75 at every
  post-injection layer); downstream layers reweight calm down and
  generic positive/vitality up.
- Candidate 12 (item 4) gains a mechanism-level note: the single-stem
  generation channel is written into the vector's direct unembedding.
- The contrast direction reads moral/interpersonal content (5e) and
  its own unembedding is moral/interpersonal vocabulary; the sign
  injected by S2-ward steering (-contrast) unembeds to
  urgency/anxiety vocabulary. Candidate for the 4B freeze.

## Caveats
One model; direct unembedding ignores everything the network does,
by design; the 60-probe comparison uses the frozen probes only, and
top-word lists include subword and non-English pieces; downstream
readouts are at the final prompt token.

## Artifacts
`direct_semantics/`: `direct_spec.json`, `direct_top_tokens.csv`,
`direct_vs_downstream_families.csv`,
`direct_vs_downstream_r_by_layer.csv`, `direct_scorecard.json`.

## Next
Plan item 6, external VAD. A cheap first step needs no model run: the
direct readouts are already over the full vocabulary, so VAD
correlations for -S2, -S1, -common and -contrast can be computed from
them directly. The layerwise downstream part needs one lens pass that
saves logits for the lexicon's single-token words.
