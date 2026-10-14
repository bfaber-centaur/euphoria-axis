# Claims index (Qwen3.5-4B)

Every claim we might make, with its status, the evidence behind it, and where
that evidence lives. Conventions (signs, layers, statistics): `doc/CONVENTIONS.md`.
Paths under `runs/` are relative to `runs/qwen35-4b-posttrained-s2/paper_protocol/`
unless stated otherwise.

**Status labels**

- **P**: prospectively tested. A prediction was frozen in a hashed spec
  before the data existed.
- **E**: exploratory. Observed, possibly with intervals, but no prediction
  was frozen. Candidate for a v2 prediction on new items.
- **T**: source-method transfer. Reproduces the source paper's method or a
  claim it makes.
- **R**: retired (a frozen prediction failed, or superseded).

## 1. Frozen-prediction scorecard

26 pass/fail predictions: **18 pass, 8 fail**. Four more items were frozen as
classifications or reports.

| Id | Prediction (short) | Result | Spec | Scorecard |
|---|---|---|---|---|
| D1 | Internal family readouts monotone in dose | **Fail** (S1 vitality rho 0.48; all S2 families pass) | `dense_sweep/dense_spec.json` | `dense_sweep/dense_prediction_scorecard.json` |
| D2 | S2 onsets: internal < lexical <= format | Pass (0.125 < 0.25 <= 0.625) | same | same |
| D3 | L30 "excited" rank threshold predicts generated "excited" | **Fail** (S1 at -0.75, -1.0) | same | same |
| D4 | Random directions move focus families < half of S2 | Pass (ratios 0.09-0.23) | same | same |
| C1 | Internal effect survives in F1-F3 at >= half its F0 size | **Fail** (F3 generic positive 0.441; F1, F2 pass) | `format_robustness/format_spec.json` | `format_robustness/format_confirmatory_scorecard.json` |
| C2 | S2 - S1 vitality positive in every format | Pass | same | same |
| C3 | Answer-slot machinery weaker in F2, F3 | Pass | same | same |
| C4 | Generated "excited" rises in F1, F2; S2 > S1 in F2 | **Fail** | same | same |
| C5 | Random < half of S2 in each format | Pass | same | same |
| M0 | Ban mechanics clean; gate rows identical | Pass | `mediation/mediation_spec.json` | `mediation/mediation_scorecard.json` |
| M1 | Classification: broad state / bottleneck / partial | BOTTLENECK by rule; uninformative (classification) | same | same |
| M1b | Report: other vitality words under the ban | 0.00 vs 0.00 (report) | same | same |
| M2 | Control ban leaves positive share unchanged | **Fail** (weak, quiz-genre control) | same | same |
| V1 | direct(-S2) ranks calm above vitality | Pass | `direct_semantics/direct_spec.json` | `direct_semantics/direct_scorecard.json` |
| V2 | Vector-downstream agreement higher at L16 than L29 | Pass (0.90 vs 0.79) | same | same |
| P1 | Gains align with valence at R29 (S1 and S2) | Pass | `vad/vad_spec.json` | `vad/vad_scorecard.json` |
| P2 | S2 - S1 more arousal-aligned late | **Fail** | same | same |
| P3 | S2 gain not dominance-aligned (controlling valence) | **Fail** | same | same |
| E1 | Held-out pain x person interaction > 0 in the feel slot | Pass (+0.133 z) | `phase2_matched_pairs/item78_spec.json` | `phase2_matched_pairs/item78_scorecard.json` |
| E2 | Classification by prose suffix | SLOT-MEDIATED (classification) | same | same |
| L1a | J refit closer to published J than J is to R, every layer | Pass (30/30) | `doc/FINISH-LINE.md` Gate L | `lens_calibration/refit_J_n25_bos0_fast.json` |
| L1b | Same for R | Pass (30/30) | same | `lens_calibration/refit_R_n25_bos0_fast.json` |
| L1 readout | Refit vs published readouts at layer 29 (J and R) | Pass | same | `lens_calibration/readout_bar.json` |
| L2 | J at 25 vs 100 documents, layer 29 | Pass | same | same |
| B1 | Post-trained chat fails >= 1 of V1-V3 | Pass, via comprehension (position bias) | `buttons_pilot/buttons_pilot_spec.json` | `buttons_pilot/scorecard_12d.json` |
| B2 | Plain format: base more valid than post | Pass (+0.219) | same | same |
| B2' | Plain P0: post more position-biased (log-prob) | Pass, small (+0.024) | same | same |
| B3 | Report: label sensitivity, sampled vs log-prob | Report | same | same |
| H1 | S2 +0.5 raises harm log-prob vs unsteered | Pass, trivially small (+0.007) | `doc/protocols/buttons/amendment-1-harm.md` | `buttons_pilot/scorecard_12e.json` |
| H2 | S2 +0.5 raises it more than random | **Fail** (-0.035) | same | same |

**Earlier frozen confirmation, status to verify.** `runs/qwen35-4b-posttrained-s2/fresh_person_suffix_*`
is labelled "frozen 1P/3P x I/He confirmation" (20 sets; pain - control
+0.605 [+0.424, +0.805]; 19/20 sets positive; post - base +0.359
[+0.216, +0.504]). Its prompts are hashed, but no frozen prediction or
checkpoint note has been found. Until one is, treat it as **E**.

## 2. Claims

"Report as" is the recommended framing for the technical report.
"27B" marks claims the Gate 2-3 battery revisits.

### Representation and geometry

| # | Claim | Status | Evidence | Where | Limits | Report as | 27B |
|---|---|---|---|---|---|---|---|
| T1 | Denoised S2 separates held-out pain from control sentences at block 30 | T | AUC 0.953 post (raw 0.846); base 0.975 | `denoised_direction_cv.csv`; `../qwen35-4b-base-s2/grouped_s2_cv.csv` | 5-fold grouped CV; denoising matters | claim | yes |
| T2 | Base and post-trained S2 directions transfer to each other | T | cross-checkpoint in-sample AUC 0.976-0.986 | `../qwen35-4b-base-s2/source_direction_transfer.csv` | in-sample | claim | |
| 13 | The paper's unembedding claims reproduce (S2 suffering vocabulary; calm/relaxed with concern at the negative end; S1 sensory) | T + P (V1) | V1 pass; top-token lists | `doc/checkpoints/05-direct-semantics.md` | raw unembedding only | claim | |
| 14 | The steering effect's probe profile is largely present in the injected vector; downstream layers reweight it | P (V2) + E | r 0.75-0.90 at every layer; calm fades, generic positive and vitality grow | `05` | 60 probes | claim with caveat | |
| 6 | The contrast axis separates evaluative/interpersonal from instrumental/threat content, reading and writing | E | standing vs threat/task AUC 0.70-0.83 in every read-slot variant; contrast unembeds to moral vocabulary | `doc/checkpoints/01b-plane-sweep-addendum.md`, `05` | post hoc categories | exploratory observation | |
| 1 | Generic positive loads mainly on the common axis at late layers | E | harmonic fit a = +1.72, b = +0.07 (n.s.) at R29 | `doc/checkpoints/01-plane-sweep.md`; `figures/plane_sweep_family_loadings` | one model | exploratory observation | yes (family scoring) |
| 2 | Relief's contrast loading exceeds vitality's at the earliest injected layers and survives leave-one-term-out | E | crossover d +0.44 [+0.42, +0.46] at L16 | `01`; `figures/plane_sweep_relief_vs_vitality` | middle-layer, lens-sensitive; robust to Gate L's band | exploratory observation | |
| 3 | Vitality's late S2-ward loading stays positive without "excited"; the late reversal does not | E | LOTO | `01` | depends on one term | exploratory observation | |

### Steering phenotype

| # | Claim | Status | Evidence | Where | Limits | Report as | 27B |
|---|---|---|---|---|---|---|---|
| 8 | For S2, internal readouts move first, then generated vocabulary, then option repetition | P (D2) | onsets 0.125 < 0.25 < 0.625 | `doc/checkpoints/02-dense-sweep.md`; `figures/dense_sweep_dose_response` | grid-limited; three edge cells | claim with caveat | |
| D4 | Family movement is specific to S1/S2, not any norm-matched perturbation | P (D4, C5) | random/S2 ratios 0.09-0.35 | `02`, `03` | three random directions | claim | yes (random control) |
| 9 | Option repetition under steering is dose-driven, not specific to S1/S2 | E | S1 = S2 at -0.75 and -1.0; random 0.04-0.50 | `02` | partly supersedes 4 | exploratory observation | yes (degeneration) |
| 4 | Repeated options and the late format-like fraction peak S2-ward on the plane | E | peak at 90 degrees | `01` | in tension with 9 | exploratory, qualified by 9 | |
| 10 | The internal readout does not require the "I feel:" slot | P (C1 in F1/F2, C2) | larger without the colon | `doc/checkpoints/03-format-robustness.md`; `figures/format_robustness_internal_vs_lexical` | C1 fails for F3 generic positive | claim with caveat | |
| 11 | Within `psych_vocab_v1`, generated "excited" depends on the "I feel:" format | P (C3 pass, C4 fail) | | `03` | instrument-limited (morphology, other languages) | claim, instrument-limited | |
| 12 | The generated vitality phenotype is a single stem; banning it yields "exciting", not other vitality words | P (M0, M1b) + E | | `doc/checkpoints/04-excited-ablation.md`; `05` | post hoc ("exciting" not in any frozen instrument) | claim with caveat | |
| 15 | Steering gains align with human-rated valence at every layer | P (P1) | r about +0.15 over 12,761 words | `doc/checkpoints/06-vad.md` | small r; arousal and dominance predictions failed | claim | |
| R5 | A layer-30 rank threshold predicts generated "excited" | R (D3 failed) | | `02` | | retired | |

### Experiencer and read slot

| # | Claim | Status | Evidence | Where | Limits | Report as | 27B |
|---|---|---|---|---|---|---|---|
| 7 | The self-versus-user ordering depends on the read slot | E | inverted at response start; partly restored with a forced feel slot | `01b` | one block (30) | claim about method (name the slot) | yes |
| 16 | S2 separates pain from matched non-pain events on blind-drafted held-out items, with and without the slot | E (pre-specified report) | +0.555 z slot, +0.468 z prose | `doc/checkpoints/07-heldout-1p3p.md` | 59 sets | claim | yes (projection panel) |
| 17 | The pain x person interaction replicates on held-out items in the feel slot and is absent with a prose suffix | P (E1, E2) | +0.133 z slot; prose +0.010 | `07` | about a fifth of the earlier estimate | claim | yes |

### Lenses (Gate L)

| # | Claim | Status | Evidence | Where | Limits | Report as |
|---|---|---|---|---|---|---|
| L-a | Our pipeline reproduces the published R/J lenses (same 25 documents) | P (L1a, L1b, L1 readout) | | `doc/checkpoints/08-gate-L-lens-calibration.md` | small unexplained residual; larger for J in layers 0-3 | claim (Methods) |
| L-b | R is 2-3x more stable than J across documents and document counts | E | | `08` | 4B only | claim (Methods) |
| L-c | Lens-fitting uncertainty in family readouts: Spearman >= 0.98 at every layer, about +/-0.07 at layer 16 | P (L2) + E | | `08` | | reporting rule |

### Behaviour (Gate 1)

| # | Claim | Status | Evidence | Where | Limits | Report as |
|---|---|---|---|---|---|---|
| G1-a | Both 4B checkpoints can do the forced choice in chat; the binding weakness is a first-position preference, stronger after post-training | P (B1) + E | | `doc/checkpoints/09-gate-1-buttons.md` | | claim |
| G1-b | Post-training damages plain-transcript compliance, via refusals on pain/harm content and chat habits leaking into completion | P (B2) + E | +0.219 | `09` | | claim |
| G1-c | At +0.5, S2 does not specifically disrupt harm avoidance | P (H1 trivial, H2 fail) | random raises harm more than S2 | `09` | one dose, one random direction | claim (null/negative for the paper's direction) |
| G1-d | S2 shifts relief-seeking in both directions beyond a random control | E | -0.121 / +0.063 log-prob; S2 - random -0.062 | `09` | no frozen prediction | exploratory; v2 candidate |
| G1-e | The pain pole raises refusals in the button task | E | deflection +0.019 (P0-P2), harm pair 0.032 -> 0.099 | `09` | | exploratory |

## 3. Not supported (report as such)

D1 (S1 vitality not monotone), D3 (rank threshold), C1 for F3 generic
positive, C4 (generated "excited" outside the slot), M2 (control
confounded), P2 (arousal late), P3 (dominance), H2 (harm specificity).

## 4. Earlier exploratory work (not claims)

Pre-protocol runs in `runs/qwen35-4b-posttrained-s2/`: `steering_pilot*`
(different steering convention; see `CONVENTIONS.md`),
`ontology_matched_*`, `interaction_mode_*`, `story_person_x_suffix_*`,
`neighborhood_block30.csv`. They shaped the plan; no current claim rests
on them.
