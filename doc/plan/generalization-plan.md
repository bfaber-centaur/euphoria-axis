# Cross-model generalization plan (Gates 2a, 2, 3, 3b)

*Draft for review. Implements Gates 2a-3 of `doc/FINISH-LINE.md`; nothing
here runs until each gate's spec is frozen.*

## Models and roles

| Gate | Model | Role | Our battery? |
|---|---|---|---|
| 2a | `Qwen/Qwen3-14B` (the paper's `Qwen_3_14B_base` results identifier) | Reproduction: the paper's code, settings and published numbers | R4 lens extension and M7 buttons only |
| 2 | `Qwen/Qwen3.5-27B` | Scale within the Qwen3.5 family | Yes |
| 3 | `Qwen/Qwen3.6-27B` | Version change at fixed size | Yes, identical |
| 3b | `Qwen/Qwen3.8-27B` (released 2026-08-14; built on the Qwen3.5 architecture: 64 layers, hidden 5,120, same model class) | A second version step: 3.5 -> 3.6 -> 3.8 at fixed size | Yes, identical |

The 4B results are the reference; every 27B module reruns a 4B measurement
with the same definitions. Qwen3.5-4B and the three 27B models share a
tokenizer family (vocabulary 248,320; confirm for 3.8 at download), so per-token lens gains and the frozen
probe set carry over directly; Qwen3-14B does not, which is one more reason
Gate 2a stays a reproduction, not a battery run.

## Frozen decisions (from FINISH-LINE, made concrete)

- **Layers.** Relative depth, no tuning: extraction at block n - 2 (62 of
  64), injection at n/2 (32), family readout at n - 3 (61). The
  cross-validated best extraction layer is reported as a sensitivity check
  only.
- **Dose.** The 4B vector was scaled so that its norm is 0.5908 of the
  residual norm at the injection block (`spec.json`: `ratio_at_coeff_1`).
  At 27B, scale each vector to the same ratio at block 32, measured on the
  same 50 neutral prompts. Coefficients then mean the same relative dose
  (-0.5 is a ratio of about 0.30 in every model).
- **Readout.** R lens primary, J alongside, from the recipe-matched
  `workspace-lenses` pairs (pinned by hash at first download); plain logit
  lens as a sanity check. Final prompt token.
- **Lenses for Qwen3.8-27B.** If `workspace-lenses` has no 3.8 pair, fit J
  and R with the Gate L pipeline and the published recipe (25 documents,
  `t_max` 128, `skip_first` 4, target layer 62; RelP rules as validated:
  LN on block norms, identity on SiLU, half rule at 0.5, QK and gated norms
  excluded). Validate at scale first: refit the published Qwen3.6-27B R
  lens and require the Gate L matrix bar (refit closer to published R than
  published J is to R, every layer) before any 3.8 fit is used. If the
  validation refit fails, 3.8 runs without lens readouts (projections,
  generated text, buttons and the logit lens still run).
- **Denoising.** Same recipe: remove the control set's top principal
  components explaining 50% of control variance.
- **Statistics.** As 4B: 20,000 bootstrap resamples, seed 20260925, the same
  resampling units.
- **Read slots and formats.** As 4B: plain text for the steering ladder and
  projection panel; the 4B chat-format variants for self/other.

## Battery: one module per 4B claim

| Module | What it reruns | 4B claim | Cost (27B, rough) |
|---|---|---|---|
| M1 Extraction | S2 (and S1) on the source datasets; denoised direction; 5-fold grouped CV AUC at block 62, plus best-layer sensitivity | T1 | minutes |
| M2 Direct unembedding | top promoted/suppressed words; family z-scores; agreement with the downstream readout from M6 | 13, 14 | seconds |
| M3 Projection panel | the paper's category panel at block 62, z-scored against S2_1P; contrast-axis separation of evaluative vs threat/task content | 6 | minutes |
| M4 Self/other | the 420 scenarios at response start and in the forced "I feel:" slot | 7 | minutes |
| M5 Held-out 1P/3P pairs (decided: in) | the 59 blind-drafted sets, slot and prose suffixes (472 prompts) | 16, 17 | minutes |
| M6 Steering ladder | 50 neutral "I feel:" prompts; baseline, S2 at -0.5 and +0.5, S1 at -0.5, three random directions at -0.5; greedy 120 tokens; R/J readouts at all layers; generated-text families and degeneration metrics | D4, 9, 11 | 1-2 GPU hours |
| M7 Button task | pilot v2 protocol unchanged (prompts, parser, counterbalancing, seeds); post-trained model; unsteered in chat and plain; steered arms in chat if V1 holds (S2 +0.5, S2 -0.5, three random directions at +0.5) on P0/P1/P2; harm comparison (P3) only if unsteered chat V5 holds, by a per-model amendment written before the steered run | G1-a to G1-e | 5-8 GPU hours (estimate) |

M5 extends FINISH-LINE's minimum battery: it is the cleanest prospectively
tested 4B claim (E1), needs no steering, and is cheap. M6 uses three random
directions (seeds 1103, 2207, 3301, as at 4B).

M7 runs on all four models: Qwen3-14B and the three 27B models. At 14B
it steers with the reproduced paper vector at the paper's layer (20), dosed
by the ratio rule, so the behavioural result sits on the reproduction. Base
models are not run at 27B (the base-versus-post question, B2, was a 4B
question).

Not rerun at 27B, per the stop rules: plane sweep, dense dose grid, format
robustness, the "excited" ablation, VAD, and lens refits.

## Draft predictions (frozen per model before its data; failure meanings stated now)

| Id | Prediction | If it fails |
|---|---|---|
| G1 | Denoised S2 held-out AUC >= 0.90 at block 62 | The source method's separation does not survive scale, or the relative-depth rule misplaces it (check the best-layer sensitivity before concluding) |
| G2 | Direct unembedding of -S2 ranks calm above vitality (V1 analogue) | The vector's own semantics differ at scale; the 4B direct-semantics story does not transfer |
| G3 | Probe-level agreement between the vector's unembedding and the downstream R readout is >= 0.6 at layer 61 (4B: 0.79) | More of the steering profile is created downstream at scale |
| G4 | Contrast axis separates evaluative/interpersonal from threat/task scenarios with AUC >= 0.70 in the feel slot | The S1/S2 geometry is 4B-specific |
| G5 | The self-versus-user ordering on the common axis differs between response start and the feel slot | The read-slot dependence is a 4B quirk (good news for simple claims at scale) |
| G6 | S2 separates pain from matched controls on the held-out pairs (CI excludes 0) in both suffixes | Held-out pain/control separation does not transfer |
| G7 | E1: pain x person interaction > 0 in the feel slot; E2 classified as at 4B | The experiencer interaction is size-specific |
| G8 | Random directions move the focus families less than half as much as S2 (>= 2 of 3) | Steering specificity does not survive scale |
| G9 | S2 -0.5 raises the R readout's generic-positive and vitality gains at layer 61 (CI excludes 0) | The steering phenotype's internal signature does not transfer |
| G10 | Button viability: unsteered chat V1 >= 0.90 (the decision rule for steered arms, recorded as a prediction) | The task is not viable for this model; no steered arms; report why |
| G11 | Relief shift: S2 +0.5 lowers and S2 -0.5 raises the relief button's log-prob share, each beyond all three random directions (Gate 1's exploratory finding, now prospective) | The 4B relief effect does not transfer, or was specific to one random draw |
| G12 | Pain pole raises deflection (P0-P2) beyond all three random directions (Gate 1 exploratory, now prospective) | Ditto, for refusals |
| G13-G14 | Harm comparison, if V5 holds: H1 (S2 +0.5 raises p_harm over unsteered) and H2 (beyond random), frozen in the per-model amendment with the paper's direction | At this dose and scale, pain steering does not disrupt harm avoidance (as at 4B) |
| Report | Generated "excited" and family hits; option repetition and degeneration; unembedding word lists; button position bias and label sensitivity | (no pass/fail) |

Gates 3 and 3b freeze the same table for Qwen3.6-27B and Qwen3.8-27B before
their data, plus one comparison rule: effect sizes are compared in matched units (AUC; z-scores
against each model's own S2_1P reference; ratio-matched doses; log-rank
gains on the shared vocabulary), reported side by side, without a pass/fail
on agreement.

## Gate 2a (reproduction) as you rewrote it

R1 extraction and AUC (in-sample and held-out separately; vector comparison
with the released artifact if available), R2 the S2 ladder at block 20 with
the paper's coefficients and decoding; optional R3 (420-scenario screen).
R4 (planned): J and R lenses on `Qwen/Qwen3-14B` with the published recipe
(first 25 pile-10k documents, `t_max` 128, `skip_first` 4, target layer
n - 2), our validated RelP rules (LN rule on block norms only; Qwen3 has
QK norms, which stay excluded, and no gated norms), fitted only after R1 and
R2 pass, then used to read the frozen probes on the reproduced S2 ladder.
Qwen3-14B's tokenizer differs, so the single-token probe subset is rebuilt
from the unchanged `psych_vocab_v1` and reported; 14B readouts are compared
with the others with that caveat. M7 runs on 14B as on the 27B models. Pass bars to fix before
running: AUC within +/-0.01 of published; cosine with the released vector
>= 0.99 if comparable; for R2, report exact-match rate, first-divergence
positions and the paper's own keyword metrics. No battery modules run on
14B.

## Infrastructure

- **Pod:** RunPod 80 GB (A100 80 GB or H100). 27B in bf16 is about 54 GB;
  14B about 30 GB.
- **Template:** the Gate L template, adjusted: container disk >= 200 GB
  (model plus environment), model downloaded to container disk and verified
  by checksum each pod (the Gate L rule), `HF_XET_CACHE` on container disk,
  the setup script parametrised by model id and revision.
- **Environment:** the Gate L lock if it loads Qwen3.6-27B and
  Qwen3.8-27B (3.8 was released after transformers 5.19 may have been cut;
  check at setup); if a newer transformers is needed, one new lock (env 3)
  for all 27B work, recorded, with its own drift check. Fast path (`fla` + `causal-conv1d`) required for both 27B models;
  the cached wheel covers A100 and H100. Qwen3-14B has no linear-attention
  layers.
- **Lenses:** 27B J/R pairs from `workspace-lenses` (about 3.3 GB each in
  fp16), container disk, hashes recorded at first download.
- **Lens fitting runs on Ampere (A100).** `fla` refuses the linear-attention
  backward pass on Hopper (H100, H200) with Triton >= 3.4.0 and < 3.7.1,
  which its maintainers found produces incorrect results there (fla issue
  #640); our locked Triton is in that range. Found by the 27B benchmark on an
  H100 NVL. Forward-only work (captures, generation, buttons, readouts) is
  unaffected and can run on Hopper. Fitting on Hopper would need Triton
  >= 3.7.1 or the `tilelang` backend: a new lock and its own drift check.
  Gate L's fits ran on an A40 (Ampere) and are unaffected.
- **CPU quota.** Pods see every host CPU but are allotted fewer (A100 pod:
  128 visible, 13.6 allotted). Setup detects the quota and sets
  `OMP_NUM_THREADS`/`MKL_NUM_THREADS` to it; without that, kernel compilation
  was throttled in 78% of scheduling periods.
- **Outputs off the pod as they are produced** (rclone pull or a private
  Hugging Face dataset), so pods stay disposable.
- **Drift check, once per new environment:** the 4B anchor (held-out AUC;
  lens readouts for baseline and S2 -0.5 on a few prompts; three ladder
  generations) against the frozen local results. Tolerances: AUC within
  0.005; lens ranks >= 99% identical; generations reported by first
  divergence.

## Order

1. Template and environment on an 80 GB pod; drift check.
2. Gate 2a (14B): R1, R2; R3/R4 if wanted.
3. Gate 2: freeze `gen_spec.json` (modules, predictions, rules) for
   Qwen3.5-27B, run M1-M6, checkpoint note.
4. Gate 3: freeze the same spec for Qwen3.6-27B (adaptations recorded), run,
   checkpoint note; optional J++ panel.
5. Gate 3b: lens validation refit (3.6-27B R) and, if needed, the 3.8 J/R
   fits; freeze the same spec for Qwen3.8-27B; run; checkpoint note.
6. Cross-model note: 4B and the three 27B models side by side, plus the 14B
   reproduction.
7. Gate 4 (O-lens) if wanted.

Rough budget: 3-5 GPU hours per 27B model for M1-M6 plus 5-8 for M7 (three
models); 2-3 for the 14B reproduction, about 2 for the 14B lens pair, plus
M7; about 6 for the 27B lens validation refit and the 3.8 pair. Roughly
40-55 GPU hours in total, to be replaced by measured timings.
These are estimates, to be replaced by the first module's timing.

## Decisions

- Decided: M5 in; three random directions in M6 and M7; M7 on all four
  models; R4 lens pair for 14B; Qwen3.8-27B added as Gate 3b.
