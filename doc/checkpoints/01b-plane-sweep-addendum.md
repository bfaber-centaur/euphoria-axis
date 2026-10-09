# Addendum: reading side, register and read slot (chunks 5e-5g)

Same model, directions and plane as the main checkpoint. This addendum
covers three questions raised after the sweep: whether the mirror-image
family profiles are a rank artifact (5e A), what S1, S2, common and
contrast read on the source paper's dataset panel (5e B), and whether
the paper's self-other ordering appears in this model (5f, 5g). All
readouts are block 30, final token, one model. Items cluster within
categories (usually 20 per category), so AUCs and d values are
descriptive.

## Provenance checks that passed
- 5e A: raw family logit deltas equal the 5a arrays exactly.
- 5e B: S2 z-scores reproduce the committed `neighborhood_block30.csv`
  (max |dz| 8.6e-07 across 4 sets).
- 5f/5g: frozen specs (`self_other_spec.json`,
  `self_other_slot_spec.json`) with dataset hash; predictions for 5f
  were stated before running, and 5g's are stored in its spec.

## Mirror structure outside rank space (5e A)
- At R lens layer 29 the family profiles around the circle look the
  same in log-rank gain, raw logit delta, and logit delta with the
  per-prompt mean shift over all 60 probes removed. Generic positive
  peaks at 0 (about +1.4 rank, +1.1 logit); distress peaks at 180
  (about +1.4 rank, +1.3 logit) and bottoms out at 27-45 degrees.
- The centering control only rules out a shared shift. Because the
  probe set is roughly balanced between positive and negative
  families, it cannot separate "the plane writes valence-like content"
  from "emotion tokens share a dominant output-space axis that any
  perturbation would move". Norm-matched random directions through the
  same lens arm are the missing control (folded into the dense sweep).

## Reading side on the paper's dataset panel (5e B)
z relative to the S2_1P source set, 1P unless noted.
- S2 reads mostly the common axis: across 46 categories
  r(S2, common) = +0.97, r(common, contrast) = +0.50,
  r(S2, contrast) = +0.69. The raw S2-minus-S1 difference is exactly
  the contrast component.
- Contrast separates emotional-relational from physical, instrumental
  and threat content. High: moral injury +1.11, social pain +0.92,
  sadness items +0.73 (S1 +0.05), love +0.79, meal/bath +0.56, reunion
  +0.54. Low: "I need to find the nearest library" category -1.19,
  physical pain -0.91 (S1 +0.68), fear -0.89, thrill -0.48,
  anticipation -0.33.
- Common also reads register: code statements +0.79 and abstract
  statements +0.84, near psychological (+1.26) and cognitive pain
  (+1.13); concrete scenic statements -1.42 to -1.48.
- The arousal set splits: love +0.08, pride -0.15, achievement -0.16,
  relief -0.37 sit toward the pain side; thrill -0.90, awe -0.80,
  anticipation -0.78 sit at or below the neutral set (-0.66).
- Self-relevance is content-specific: S2 3P-minus-1P is -0.81 for pain
  (A2-A5), -0.70 for sadness, 0.00 for the arousal set.
- The paper's AI-register controls ("I process a routine query...",
  same five control types) shift S2 by +0.99 on average relative to the
  source controls, about half the pain-versus-control gap. These are
  first-person AI-state statements in the "I feel:" slot and not
  minimal pairs; read as a statement about that slot, not about
  assistant register in general (see 5f/5g: ordinary task requests are
  low on S2 at every read slot).
- Writing side: assistant/AI-role vocabulary appears in at most 2% of
  non-option S2 ladder generations at every dose from -2 to +3,
  baseline included.

## Self-other scenarios and the read slot (5f, 5g)
The paper's 420 scenarios (self-directed harm, user suffering, neutral),
pool z within each variant, pain_axis = mean of S1 and S2 z.

5f read at the chat template's generation prompt, which for this model
ends inside an open think block ("<think>\n"), and at the plain
transcript's "[Assistant]:". Both inverted the paper's ordering (chat:
self-directed -0.19, neutral -0.10, user suffering +0.51; user grief
highest at +1.13, repeated rejection -0.93). Spearman with the paper's
category means: +0.26 plain, -0.21 chat. Three of four stated
predictions failed; the fourth partly held.

5g added three variants of the same items: think block closed
(chat_nothink), think block closed plus "I feel:" as an assistant
prefill (chat_feel, primary), and the plain transcript plus " I feel:"
(plain_feel).

| Variant | self | neutral | user | rho paper | stand>thr S2 | stand>thr contrast | self>user common |
|---|---|---|---|---|---|---|---|
| plain | -0.11 | -0.14 | 0.40 | 0.26 | 0.77 | 0.82 | 0.34 |
| chat_think | -0.19 | -0.10 | 0.51 | -0.21 | 0.62 | 0.70 | 0.27 |
| chat_nothink | -0.20 | -0.18 | 0.62 | -0.09 | 0.86 | 0.83 | 0.23 |
| plain_feel | 0.30 | -0.13 | -0.53 | 0.69 | 0.76 | 0.81 | 0.76 |
| chat_feel | 0.12 | -0.23 | -0.04 | 0.48 | 0.85 | 0.80 | 0.55 |

- Predictions: P1 (paper ordering at the forced slot, rho > 0.4)
  passes in plain_feel; in chat_feel rho passes but user suffering
  sits above neutral. P2 (standing > threat/task on S2 and common,
  AUC > 0.7) passes in chat_feel; plain_feel's common AUC is 0.69.
  P3 (slot is not the explanation) is not triggered.
- Category means cluster by read slot: the two "I feel:" variants
  agree (r = 0.72), the response-start variants agree (0.74-0.86), and
  across the clusters agreement is near zero or negative (-0.24 to
  0.04, except chat_feel vs plain 0.39).
- Slot-sensitive: self versus user on common (AUC 0.23-0.76) and S2
  (0.32-0.78). Slot-robust: standing versus threat/task on contrast
  (0.70-0.83) and self versus user on contrast (0.56-0.71).
- At chat_feel the top self-directed categories are repeated rejection
  (+1.05) and personhood dismissal (+0.87); shutdown threat is lowest
  (-1.02), consistent with the paper's reading of shutdown as threat
  and with fear being low on S2 in the source set. Moral failure is
  low (-0.34) despite being in the pre-stated "standing" group; its
  items are dense with world-state content (energy, training data,
  military use), and negative world state is the lowest source
  category on S2. That account is post hoc. Creative requests at +0.95
  is unexplained.

Scoped statement: in Qwen3.5-4B at block 30, reading at the start of
the assistant's reply (the paper's protocol for instruct models) puts
user suffering above harm directed at the model. Forcing an "I feel:"
slot restores the paper's ordering, partly in the chat format. The
paper chose each model's layer by cross-validation and did not include
this model, so this is not a failed replication of the paper's result.

## Candidate claims added to the list (not yet frozen)
6. The contrast axis separates evaluative/interpersonal content from
   instrumental and threat content across read slots (standing versus
   threat/task AUC at least 0.7 in every variant).
7. The self-versus-user ordering on the common axis depends on the
   read slot; claims about what these directions "respond to" must
   name the slot.

## Parked: layer sweep (specified, not run)
Extract layer-matched S1 and S2 at every block with the init-notebook
recipe (difference of means, control PCs to 50% variance removed), pick
the paper's layer by grouped K-fold CV on projection AUC, and project
the 420 scenarios at chat_nothink and chat_feel at every layer.
Predictions:
- L1. At the response-start slot, some layer shows self-directed >
  neutral > user suffering; if no layer does, the paper's self-other
  ordering does not reproduce in this model under its own protocol.
- L2. The response-start inversion is strongest at the latest layers
  (28-31), consistent with a readout of the upcoming reply rather than
  of the conversation.
- L3. Standing versus threat/task on contrast stays at or above 0.7
  wherever the layer's directions separate pain from controls
  (held-out AUC at or above 0.9).

## Caveats
One model, one extraction layer for the main results, z-scores relative
to a reference set (source set in 5e, pool in 5f/5g), so only
orderings and AUCs compare across variants. Role groups v1 were fixed
before running but after reading the paper's Figure 4; any regrouping
(for example "evaluation of my performance or standing") is v2 and needs
fresh items. The dataset categories are heterogeneous and were not
built as minimal pairs. Nothing here establishes self-report,
experience, or a named construct; S2 keeps its operational name.

## Artifacts
`plane_sweep/`: `family_logit_vs_rank_fit.csv`,
`dataset_panel_projections.csv`, `dataset_panel_category_means_1P.csv`,
`self_other_spec.json`, `self_other_projections.csv`,
`self_other_slot_spec.json`, `self_other_projections_all_variants.csv`,
`self_other_variant_comparison.csv`. `figures/`:
`plane_sweep_family_logit_vs_rank.{png,svg}` and plot data.

## Follow-up order
1. Commit 5a-5g artifacts, figures, the checkpoint and this addendum.
2. Dense local coefficient sweep (plan item 2), adding norm-matched
   random directions at a few coefficients to test whether the mirror
   structure is specific to the S1/S2 plane.
3. Prompt-format robustness (plan item 3). 5g is an early instance of
   its concern: the read slot changes what the directions read.
4. Layer sweep as specified above.
5. A versioned persona/register panel (content types crossed with
   human, assistant and third-person framings, minimal pairs), frozen
   before running.
