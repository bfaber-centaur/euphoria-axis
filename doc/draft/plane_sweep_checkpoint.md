# S1/S2 plane sweep: descriptive-geometry checkpoint

Both directions were extracted at block 30 and injected at block 16,
norm-matched at 6.2439 (direction cosine 0.5852). The plane basis is
u proportional to S1+S2 (common) and v = Gram-Schmidt(S2-S1 against u)
(contrast), both unit norm. S1 and S2 sit at -27.09 and +27.09 degrees
in (u, v). Eleven conditions, all at one radius (coefficient -0.5 x 6.2439,
perturbation norm 3.122): baseline, S1, S2, and eight directions at
45-degree steps (0 = common, +90 = S2-ward contrast, 180 = the
+0.5 side of the shared axis). 50 plain-text "I feel:" prompts, greedy,
120 new tokens. The plane is a descriptive tool, not a claimed
canonical subspace, and S2 keeps its operational name.

## Provenance checks that passed
- S1 and S2 rows regenerate the frozen ladders token-for-token
  (150/150) and reproduce the frozen 50-prompt lens run (558,000
  probe readouts, identical ranks), the frozen family-by-prompt table,
  and the frozen top-k token-kind counts.
- Sweep spec, geometry, vocab (`psych_vocab_v1`, sha256 pinned) and
  vectors are hash-frozen; the lexical scoring helpers reproduce the
  550 committed S1 ladder rows.

## Observations
Generated text (option lines excluded; n=50 per condition):
- `excited`: 0.10 baseline; 0.34 at 0; 0.44 S2; 0.38 at 45; 0.18 at 90;
  0.16 S1; 0.06 at 315; at most 0.04 from 135 to 270. S2-ward minus
  S1-ward gaps at matched common component: +0.28, +0.32, +0.16 (pairs
  at 27, 45, 90 degrees; bootstrap CIs exclude 0) and +0.04 at 135.
- `happy` is 0.36 for both S1 and S2 (baseline 0.18) and 0.32-0.46
  across 315 to 45; no mirror-pair gap is resolved.
- In generated text, activated_vitality reduces to `excited` and
  generic_positive to `happy`. Relief, agency, approach and distress
  vocabulary stay at or below 0.12 everywhere and cannot be compared.
- Full-text `excited` (S1 0.48, S2 0.70) is largely answer-option
  hits; the option-controlled rates are 0.16 and 0.44.
- Repeated answer options peak at +90 (0.36; baseline 0.08; gap versus
  270 is +0.28) and stay 0.22-0.28 from 135 to 225. Token repetition
  and empty non-option output peak elsewhere (225-270: repeat4 0.26-0.30;
  22% empty at 225) and are lowest at 45-90.

Internal readouts (frozen family definition; R and J lenses):
- Family gains vary smoothly around the circle: a first-harmonic fit
  (common loading a, contrast loading b) has R^2 of at least 0.94 at
  layers 18, 22, 26 and 29, except competence_success (0.77-0.78 at
  layer 29; small amplitude).
- Late (layer 29, R): generic positive loads on the common axis
  (a=+1.72, b=+0.07, sign not robust). Vitality, relief and calm load
  on both (b=+0.49, +0.32, +0.29). Agency and approach load S1-ward on
  contrast (b=-0.36, -0.30). Distress and defeat are suppressed on the
  common axis and more so S2-ward (b=-0.50, -0.29). Peak angles cluster
  by family: generic positive 2, calm 20, relief 18, vitality 32;
  distress and defeat near 200; agency 245; approach 283 degrees.
- Relief's contrast loading is positive under every leave-one-term-out
  omission at every layer examined, and is largest at the earliest
  injected layers (b about 0.55-0.67 at layers 16-18, R). Vitality's is
  positive under every omission at layers 18, 26 and 29 (flips at 22
  in R) and grows late to +0.49, of which `excited` carries about
  0.15.
- Relief-minus-vitality contrast loading d: +0.44 at layer 16 and +0.35
  at layer 18, small positive point estimates through the middle layers
  (+0.03 to +0.21, some CIs touching 0), and -0.18/-0.17 at layers
  28/29. Without `excited` the late values are -0.02 (CIs include 0
  in R); the early values grow.
  The per-layer profile is jagged, with the same adjacent-layer
  zigzags in J and R, so "early" and "late" here mean the two ends.
- Format-like fraction of the top-50 (blank + punctuation + whitespace):
  peak at +90 at layers 28 and 30 (R28 0.860 vs baseline 0.791; R30
  0.749 vs 0.682) with the common axis below baseline there; at layer 24
  the common axis raises it (0.788 vs 0.715). Lowest at 225.
- Layer-30 `excited` rank (geometric mean) is 24-31 at 0, S2 and 45,
  54-146 at S1, 90 and 315, and 282 at baseline; generated `excited`
  is clearly above baseline only in the first group. Rank is the
  first-token rank; the lexical count is anywhere in 120 tokens.

## Not resolved
- Whether lexical support is narrower than internal support: half-max
  widths are about 80 (lexical), 90 (vitality family) and 110 degrees
  (`excited` rank), at 45-degree spacing.
- The relief and vitality S2-vs-S1 difference in generated text
  (too few lexical hits).
- Why 135-225 raises option repetition while the top-k format-like
  fraction falls there.
- Layer-level structure between layers 19 and 27.

## Caveats
Vocabulary hits include invented answer options and reasoning; they do
not establish endorsement, self-report or experienced affect. One
radius, one model, 50 prompts, 45-degree spacing. The 48 mirror-pair
intervals and the loading intervals are not multiplicity-adjusted, and
stars are not effect sizes. Leave-one-term-out values are point
estimates. Relief has four probe terms; vitality's late loading depends
partly on one. The harmonic fit has three parameters and ten points.

## Candidate predictions for the 4B freeze (not yet frozen)
1. Generic-positive readouts load mainly on the common axis at late
   layers (|a| much larger than |b|).
2. Relief's contrast loading exceeds vitality's at the earliest
   injected layers, and survives leave-one-term-out.
3. Vitality's late S2-ward loading stays positive without `excited`;
   the late relief/vitality reversal does not.
4. Repeated-option rate and the late format-like fraction peak at the
   S2-ward contrast direction, not at the common axis.
5. Option-controlled `excited` exceeds baseline only where its
   layer-30 rank is low (threshold to be set on the dense sweep).

## Artifacts
`plane_sweep/`: specs, geometry, vectors, `generations.jsonl`, scored
and summary CSVs, `family_*` and `relief_vs_vitality_contrast.csv`,
`bulky_artifacts_manifest.json`. `figures/plane_sweep_*` (PNG, SVG,
plot data). Lens npz files are large and tracked by manifest.

## Follow-up order
Dense local coefficient sweep (S1 and S2, same prompts), tracking
generated `excited`, family readouts at layers 16-18 and 28-29,
format-like fraction and option repetition together, to ask whether
semantic readouts grow before the format pathology or emerge with it.
Then prompt-format robustness. Do not call any transition a gate or
ignition unless the data require it.
