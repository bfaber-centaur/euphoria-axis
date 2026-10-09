# External VAD analysis: checkpoint (plan item 6)

Qwen3.5-4B post-trained. NRC VAD Lexicon v2.1 (valence, arousal,
dominance on a -1 to +1 scale), restricted to single lowercase words
whose " word" form is one Qwen token: 12,761 words. Per-word readout:
mean over the 50 "I feel:" prompts of log(rank_baseline /
rank_condition), R lens, final prompt token, layers 16-30, for S1 -0.5
and S2 -0.5. "S2-S1" is the S2 gain minus the S1 gain; as injected,
this corresponds to the plane sweep's 90-degree (S2-ward) condition,
which injects -contrast. Statistics are Spearman correlations over
words; partial correlations control for valence; 95% intervals from
2000 bootstrap resamples of words.

## Provenance
- `vad_spec.json` (lexicon hash, word list, P1-P3) frozen before any
  correlation was computed.
- Ranks for the lexicon were computed with a vectorized function; for
  the 60 frozen probes they reproduce the plane sweep's stored ranks
  exactly (100%, all three conditions, all nine layers).
- In the lexicon, valence and dominance correlate +0.47, arousal and
  dominance +0.33, valence and arousal -0.08.

## Frozen predictions and scores
| | Prediction | Result |
|---|---|---|
| P1 | At R29, S2 and S1 gains each correlate positively with valence | Pass: S2 +0.155 [+0.137, +0.173], S1 +0.148 [+0.130, +0.166] |
| P2 | S2-S1 gain is more arousal-aligned (partial, controlling valence) at R29 than at R16, and positive at R29 | Fail: positive at R29 (+0.039 [+0.022, +0.057]) but not larger than R16 (difference +0.007 [-0.007, +0.022]) |
| P3 | S2's R29 gain does not correlate positively with dominance, controlling valence | Fail: +0.067 [+0.051, +0.085] |

## Observations
- Valence alignment is present from the injection layer for both
  directions (S2 0.155 at L16, 0.175 at L30; S1 0.186 at L16, 0.165
  at L30). In middle layers S1 is more valence-aligned than S2 (the
  S2-S1 valence correlation reaches -0.088 at L24); they converge late.
- S2-S1 arousal alignment is small and positive at every layer
  (partial 0.025-0.066), already present at L16 and consistent with
  the injected vector itself (direct unembedding of -contrast: arousal
  +0.08). An uptick appears only at L30.
- The only alignment that rises late is dominance for S2-S1 (partial
  +0.028 at L16, +0.064 at L29, +0.085 at L30).
- This conflicts with the frozen family result, in which
  agency_assurance loads against S2-ward contrast. The lexicon's
  dominance dimension and our hand-picked agency family are not
  measuring the same thing; which words drive the dominance alignment
  is not yet known.
- All effect sizes are small (|r| <= 0.19).

## Reading
The steering effects align with human-rated valence, in both
directions and at every layer, which supports the positive-valence
reading of the negative-coefficient phenotype with an instrument we
did not design. The late activated-vitality result is not reflected as
growing arousal alignment in the lexicon. The late S2-versus-S1
difference aligns more with dominance than with arousal, contrary to
the plan's expectation and to the frozen agency family; that
discrepancy is a question about the ontology, not yet a claim about
the model. This is validation against human affect ratings, not
evidence that the model instantiates human affect dimensions.

## Changes to the candidate-claim list
- New candidate 15: S1 and S2 steering gains align with human-rated
  valence (NRC VAD) at every post-injection layer.
- Plan's arousal prediction (S2 vs S1 more arousal-aligned late):
  not supported as frozen.
- Plan's dominance prediction: not supported; flag the agency family
  versus lexicon dominance discrepancy for the synthesis.

## Caveats
One model, one readout position, one lexicon; words limited to single
tokens with a leading space; small correlations over many words give
tight intervals, so significance is easy and effect size is the thing
to read; partial correlations control for valence only.

## Artifacts
`vad/`: `vad_spec.json`, `vad_single_token_lexicon.csv`,
`vad_direct_vector.csv`, `lens_{baseline,S1_-0.5,S2_-0.5}.npz` (large;
manifest), `vad_scorecard.json`, `vad_layerwise.csv`.

## Next
Phase II: plan items 7 and 8 (fresh held-out 1P/3P matched pairs,
then experiencer x suffix).
