# Euphoria Axis — Finish Line

**Date:** 2026-10-08, revised 2026-10-09
**Status:** Convergence toward technical report and LessWrong post
**Repository:** [https://github.com/bubskee/euphoria-axis](https://github.com/bubskee/euphoria-axis)

Revisions on 2026-10-09 are marked **[added 2026-10-09]**: an updated
evidence inventory, a lens-calibration gate (Gate L), a reproduction gate on
a paper model (Gate 2a), and decisions frozen ahead of Gates 1-3.

## Mission

Finish a bounded extension of Tagliabue, Dung, and Berg's *The Pain Axis: LLMs Represent Self-Directed Harm and Act on It* (v2, September 2026).

We are **not attempting a full reproduction** of the original study. Its breadth, behavioral experiments, adapters, and compute requirements are outside our resources and present scope. **[added 2026-10-09]** We do include one direct reproduction check on a model the paper studied (Gate 2a), so the report rests on reproduction, extension, and generalization rather than extension alone.

Our contribution is to investigate what the operationally defined direction represents, using newer Qwen models and additional methodological controls:

1. Bidirectional steering, including underexplored negative coefficients.
2. The geometry of S1, S2, and the plane they span.
3. Psychologically grounded, predefined semantic families.
4. Comparisons between generated language and R/J-lens readouts.
5. Experiencer, read-slot, and prompt-format sensitivity.
6. Limited behavioral exploration and cross-model generalization.
7. An explicitly speculative O-Lens peek, if available.

**Working principle:** Small science, small claims. Let the observations constrain the interpretation rather than selecting an interpretation and searching for supporting observations.

The intended deliverables are a technical PDF, reproducible evidence in the repository, and a LessWrong introduction under 1,000 words.

## Current evidence and scope

**[added 2026-10-09]** Updated from `16f0fc7` to the current repository state; per-experiment checkpoint notes are in `doc/checkpoints/`.

### Established or substantially investigated

- Qwen3.5-4B post-trained: S2 held-out pain/control classification, approximately 0.953 AUC at block 30.
- Qwen3.5-4B Base: approximately 0.975 AUC; substantial alignment with the post-trained direction.
- S1/S2 comparison, angular plane sweep, and R/J-lens semantic analyses.
- Bidirectional steering and investigations of vocabulary, dose, repetition, and formatting artifacts.
- The original paper's 420 self/other scenarios tested across read slots, with substantial position dependence.
- Frozen `psych_vocab_v1`, with robustness checks including leave-one-term-out analyses.
- **[added]** Dense coefficient sweep (D1-D4): internal readouts monotone for S2; onset order internal < lexical < option repetition; random-direction specificity. `dense_sweep_checkpoint.md`.
- **[added]** Prompt-format robustness (C1-C5): internal readout survives without the "I feel:" slot; generated "excited" does not. `format_robustness_checkpoint.md`.
- **[added]** "excited" ablation (M0-M2): banned exact forms are replaced by "exciting"; no other vitality words appear. `mediation_checkpoint.md`.
- **[added]** Direct-vector semantics (V1-V2): the paper's unembedding claims reproduce; most of the profile is present in the injected vector. `direct_semantics_checkpoint.md`.
- **[added]** External VAD validation (P1-P3): valence alignment at every layer; arousal and dominance predictions not supported. `vad_checkpoint.md`.
- **[added]** Fresh held-out 1P/3P confirmation (E1-E2), blind-drafted items: the motif replicates in the "feel:" slot (+0.13 z) and is slot-mediated; S2 separates pain from matched controls (+0.5 z) with and without the slot. `phase2_item78_checkpoint.md`.
- **[added]** Button pilot: Base unsteered complete (full compliance; position bias in chat; harm-only button chosen 12% chat / 28% plain).

### Incomplete or not yet established

- Post-trained 4B button viability (frozen run, not yet executed) and any behavioral result.
- Lens calibration (Gate L).
- Reproduction on a paper model (Gate 2a).
- Qwen3.5-27B and Qwen3.6-27B generalization.
- O-Lens exploratory panel.
- Final technical report and publication figures.

Treat this inventory as a starting checkpoint, not as an instruction to rerun finished work.

---

## Gate 0 — Freeze the 4B evidence

**Goal:** Make the existing findings reportable without opening new research branches.

Actions:

- [ ] Build a results inventory linking every proposed claim to its experiment, specification, data, figure, and limitations.
- [ ] Separate source-method transfer, exploratory extensions, and prospectively tested findings. **[added]** Prospectively tested so far: D1-D4, C1-C5, M0-M2, V1-V2, P1-P3, E1-E2 (with failures recorded as failures). Exploratory: plane sweep, 5e-5g reading side.
- [ ] Confirm the exact 4B extraction and steering conventions: dataset hashes, model revisions, layer indices, hook positions, normalization, coefficients, tokenizer, and prompt formats. **[added]** Include: every condition injects the negative of its named direction; the source repo pin (`8d1649c0`, plus content hashes of files read); lens provenance (source repo, file hash, `provenance.config_json`) for every lens used.
- [ ] Record which candidate predictions passed, failed, or remain unresolved.
- [ ] Verify that `psych_vocab_v1` and its psychological references are documented; retain its original definition.
- [x] **[added]** Fresh 1P/3P confirmation: done (E1 pass, E2 slot-mediated).
- [x] **[added]** Licensing: NRC VAD lexicon content removed from the repository and history; license note in `vad/README.md`.
- [ ] Produce a short 4B findings summary usable directly in the PDF.

**Gate passes when:** The existing 4B results can be described without relying on notebook archaeology or undocumented analyst choices.

**Stop:** No more ontology categories, new vocabularies, large layer sweeps, full VAD decomposition, or persona-direction projects.

Reopen a completed analysis only for an identified implementation defect or a control necessary for a specific planned claim.

---

## Gate L — Lens calibration **[added 2026-10-09]**

**Goal:** Know how much to trust the published R/J lenses that every lens-based claim relies on, and whether we can fit recipe-matched lenses ourselves.

Context: all lenses used come from `camilablank/workspace-lenses`, which ships recipe-matched J/R pairs (target layer n_layers - 2, skip_first 4, n = 25 pile-10k prompts) for Qwen3.5-4B, Qwen3.5-27B and Qwen3.6-27B. Whether n = 25 is adequate for our readouts is unknown. Runs on the current 16 GB GPU (4B only).

Actions:

- [ ] Record provenance of the published 4B pair (file hashes, `provenance.config_json`).
- [ ] **L1 refit:** fit a 4B J/R pair with the published configuration (official `jlens.fit`; R-lens via the three RelP backward rules: RMSNorm rsqrt detached, SiLU sigmoid detached, SwiGLU product half-detached; forward values unchanged).
- [ ] **L2 convergence:** fit the same recipe at n = 100 (n = 200 if cheap).
- [ ] Compare on our own instruments, not only generic ones: frozen family log-rank gains at layer 29 for the plane-sweep S2 -0.5 and S1 -0.5 conditions; per-probe rank correlation; sign agreement on the focus families. Add the reference repo's lens-eval readability for n = 25, n = 100 and the logit lens.

Pass criteria (set before fitting):

- **L1 pass:** refit matches the published pair (per-layer Frobenius cosine >= 0.99 if the 25 documents can be reproduced exactly; otherwise readout agreement: per-probe Spearman >= 0.95 at layer 29 and identical signs on the six focus families).
- **L2 pass:** n = 25 and n = 100 readouts agree (per-probe Spearman >= 0.95 at layer 29, identical focus-family signs).

Outcomes:

- **L1 and L2 pass:** published lenses are adequate for our claims; say so in Methods with the numbers. Use published pairs for Gates 2-3.
- **L1 fails:** stop lens work; keep using published pairs, recorded by hash; note that we could not reproduce the fitting.
- **L1 passes, L2 fails:** report as a limitation. Fit higher-n recipe-matched pairs for every model in Gates 2-3 only if time allows; within-lens comparisons stand either way.

**Time box:** two working days including code.

**Stop:** No recipe research, no lens-quality optimization, no new lens methods. A reusable refit pipeline with calibration tables across models goes to FUTURE-WORK.

---

## Gate 1 — Buttons: one bounded behavioral exploration

**Goal:** Determine whether the released Qwen3.5-4B checkpoints support an interpretable forced-choice experiment, and obtain one limited functional result if they do.

The source paper's v2 behavioral emphasis is on harm selection and disrupted harm avoidance, not demonstrated relief-seeking. Our experiment is a small extension, not a recreation of its large behavioral study.

Actions:

- [ ] Preserve the already-completed Base unsteered results.
- [ ] Run the post-trained viability battery with the frozen counterbalanced button protocol (spec `b564b99d502b663d`; fresh kernel, post-trained model only).
- [ ] Score both models (chunk 12d; refuses any output whose recorded model id does not match its label).
- [ ] Evaluate exact-choice validity, position/name bias, label sensitivity, deflection, and multi-turn compliance.
- [ ] Use the existing viability thresholds; document any amendments before new inference.
- [ ] **[added]** Run the frozen steered arms (12c: S2 +0.5, S2 -0.5, random +0.5 on P0/P1/P2) if post-trained unsteered V1 holds in at least one format.
- [ ] **[added]** Harm comparison, by versioned amendment written before any steered harm run: only if post-trained unsteered passes V5 (harm-only button chosen <= 10%) in chat. Then one comparison: harm-only vs inert, chat format, first choice, unsteered vs S2 +0.5 vs random +0.5, existing counterbalancing. No -S2 harm arm. Precaution rationale (lowest informative dose, fewest items) recorded in the amendment.
- [ ] **[added]** If V5 fails: no harm comparison; report the unsteered harm-choice rates as the finding.
- [ ] Preserve first-choice outcomes, full sampled replies, malformed responses, and label/position-stratified rates.

**Pass A:** A valid task produces an interpretable behavioral comparison, whether the effect is positive, negative, or null.

**Pass B:** The task fails the validity criteria; document why and stop.

**Hard stop:** No LoRA rescue, extensive prompt engineering, large unlabeled-learning protocol, or repeated redesign to obtain an effect.

If the task is invalid, do not infer that the model lacks a behavioral response to the representation.

---

## Gate 2a — Reproduce on a paper model **[added 2026-10-09]**

**Goal:** One direct reproduction check on a model the source paper studied, run first on the new hardware so it doubles as the machine check.

Model: Qwen3-14B base (paper layer 31 for extraction, layer 20 for the S2 steering ladder). About 28 GB in bf16; needs the new hardware.

Actions:

- [ ] **Machine drift first:** on the new machine, rerun a small 4B anchor (held-out AUC; plane-sweep baseline and S2 -0.5 lens arrays; a few ladder generations). Tolerances set now: AUC within 0.005; lens ranks >= 99% identical; generations reported with first-divergence position (exact match not required).
- [ ] Read `v2_controls/scientific_pins.json` and `v2_controls/MANUSCRIPT_DISCREPANCIES.md` in the source repo; freeze the reproduction spec using the authors' settings and code.
- [ ] **R1 extraction:** run the paper's extraction at layer 31. Pass: cosine with the released vector >= 0.99; AUC table within +/- 0.01 of the published values (S2_1P 0.985, S1_1P 0.933, S1_3P 0.791 at final token).
- [ ] **R2 steering:** rerun the S2 ladder at layer 20 with the paper's coefficients and decoding. Report exact-match rate, first-divergence positions, and the paper's own keyword metrics on our outputs. The phenomenon, not the bytes, is the target.
- [ ] **R3 self/other screen:** optional, if the harness is loaded.

**Gate passes when:** R1 and R2 are complete with the numbers reported, matching or not.

**Stop:** No lens fitting for 14B unless Gate L passed and time remains; no extension experiments on 14B.

---

## Gate 2 — Qwen3.5-27B quick generalization

**Goal:** Test whether the most informative 4B observations survive increased scale within the Qwen3.5 family.

Freeze the test battery before running.

**[added 2026-10-09] Frozen decisions for Gates 2 and 3:**

- **Layers:** same relative depth as 4B for both 27B models; no per-model tuning. 4B has 32 blocks (extraction 30, injection 16, family readout 29); 27B has 64 (extraction 62, injection 32, family readout 61). Cross-validated best-layer AUC is reported as a sensitivity check only.
- **Readout:** R lens primary, using the recipe-matched workspace-lenses pairs for all three models (J lens alongside; plain logit lens as a model-agnostic sanity check). Lens files recorded by hash.
- **Dose:** the paper's own `ratio` convention (steering norm relative to residual norm at the injection layer), computed for 4B and applied at 27B.

Minimum battery:

- [ ] Source-style S2 extraction and grouped held-out pain/control AUC.
- [ ] Compact source/control-category projection panel.
- [ ] S1/S2 comparison, if inexpensive and necessary for the cross-scale geometry question.
- [ ] Self/other projection at ordinary response start and the chosen `I feel:` slot.
- [ ] Small signed steering ladder on neutral prompts, with at least one matched-random control.
- [ ] Frozen semantic-family scoring and basic output-degeneration diagnostics.

Record predictions in advance, including plausible failures and what those failures would mean.

Use the same prompt families and analysis definitions as 4B wherever valid. Record model-specific chat-template, hook, layer, and steering-dose differences.

**Gate passes when:** The fixed battery has completed or a technical/resource limitation is documented, with all results retained.

**Stop:** No model-specific ontology search, full plane sweep, dense dose mapping, or new O-Lens training.

---

## Gate 3 — Qwen3.6-27B quick generalization

**Goal:** Test the stability of the same observations across a model-version change.

- [ ] Carry over the Gate 2 questions, prompts, scoring definitions, comparison rules, and frozen decisions.
- [ ] Document required architectural and chat-template adaptations.
- [ ] Run the same compact extraction, projection, read-slot, and signed-steering battery.
- [ ] Compare effect sizes and qualitative behavior, not just whether an effect is statistically detectable.
- [ ] Preserve disagreements, failures, and model-specific artifacts.

**Gate passes when:** A direct comparison with Qwen3.5-27B is possible, or its limitations are explicitly documented.

**Stop:** Do not retune the protocol to recover a previously observed pattern.

The objective is to test generalization, not produce agreement.

---

## Gate 4 — Optional O-Lens peek

**Goal:** Explore whether free-form activation verbalization supplies interesting hypotheses about the Pain Axis.

This is **bleeding-edge exploration**, not validation of O-Lens and not evidence of model experience.

Only use existing, sufficiently functional O-Lens checkpoints. Do not train a new Qwen3.5-27B lens for this report.

If practical:

- [ ] Preselect roughly 8–12 examples representing both S2 poles, contrasting semantic families, and relevant self/other or read-slot conditions.
- [ ] Include ordinary/control activations and examples likely to challenge an attractive interpretation.
- [ ] Record raw O-Lens verbalizations and compare them with available R/J readouts.
- [ ] Report conspicuous disagreements and failures, not only compelling phrases.
- [ ] Label the section exploratory throughout.

**Gate passes when:** A small, honestly presented panel exists—or the section is omitted.

**Hard stop:** No O-Lens causal validation, checkpoint scaling, prompt optimization for prettier verbalizations, or claims that an oracle description identifies a felt state.

Those questions belong to the next O-Lens project, using Qwen3.5-4B and Qwen3.6-27B.

---

## Gate 5 — Technical report

**Goal:** Produce a self-contained PDF explaining what was done, what was found, and what remains uncertain.

Start the report skeleton before the 27B experiments finish. Insert frozen results as they arrive.

Proposed structure:

1. **Introduction and scope** — The source paper, its operational construct, and our extension questions.
2. **Methods** — Models, datasets, direction extraction, intervention conventions, readout methods, semantic vocabulary, controls, and statistical procedures. **[added]** Include lens provenance and the Gate L calibration result.
3. **Reproduction** **[added]** — Gate 2a results on Qwen3-14B base.
4. **Representational findings** — Classification, Base/post-trained comparison, S1/S2 geometry, category structure.
5. **Steering and interpretability** — Both poles, dose effects, R/J findings, lexical and formatting complications.
6. **Experiencer and context** — 1P/3P effects, read-slot dependence, task and persona considerations.
7. **Behavioral exploration** — Buttons, including task failure or null results as applicable.
8. **Cross-model generalization** — Qwen3.5-27B and Qwen3.6-27B.
9. **Optional exploratory O-Lens observations** — Clearly separated from validated findings.
10. **Precautions** **[added]** — Steering toward the pain pole and any harm-choice runs: doses, item counts, and the rationale, alongside the source paper's own section.
11. **Discussion, limitations, and future work** — Competing interpretations, provenance, failure modes, and unresolved questions. **[added]** Engage with the authors' `MANUSCRIPT_DISCREPANCIES.md`; cite the pinned source commit.

### Figure priorities

**Core figures:**

- Pain/control separation across checkpoints, with clear distinction between held-out classification and source-category projections.
- Read-slot/experiencer interaction or an equally compelling semantic-geometry result.
- Bidirectional steering, showing semantic changes alongside formatting or degeneration metrics.

**Conditional:** Button-choice figure only if valid; otherwise a concise appendix table.

**Optional:** O-Lens examples in a clearly exploratory appendix.

Each reported result must have a reproducible input, analysis, and artifact location. Figures should be generated from committed result tables, not manually assembled from notebook displays.

### PDF completion criteria

- [ ] All main claims trace to named runs and source data.
- [ ] Exploratory versus confirmatory status is visible.
- [ ] Statistical units, uncertainty, and multiplicity limitations are stated.
- [ ] Model and protocol differences are explicit.
- [ ] Important negative and contradictory results are included.
- [ ] The original paper's contributions and caveats are represented fairly.
- [ ] The conclusions do not require a specific psychological interpretation of S2.
- [ ] Third-party data are cited and used within their licenses (NRC VAD: non-commercial, not redistributed). **[added]**
- [ ] PDF and repository links resolve.

**Gate passes when:** An informed reader could evaluate the extension without reading the research chat history.

---

## Gate 6 — LessWrong: Don't Call It Pain!

**Goal:** Publish a short, engaging introduction directing interested readers to the technical report.

- [ ] **[added]** Share the report and draft with the source paper's authors first; hold publication for their comments.
- [ ] Final text under 1,000 words, ideally 600–850.
- [ ] Dickinson or Pink Floyd epigraph.
- [ ] One paragraph introducing the source research accurately.
- [ ] Explain that this is an extension rather than a full reproduction (with one reproduction check).
- [ ] Two strong, readable figures.
- [ ] Explain why operational representation, causal function, and phenomenal experience are distinct questions.
- [ ] Link the PDF, repository, and source paper.

**Gate passes when:** The article is readable and compelling on its own, without asking the reader to trust claims that are only established in the technical report.

---

## Order of work **[added 2026-10-09]**

1. Current GPU (16 GB): Gate 0 (writing) in parallel with Gate L (4B lens fits), then Gate 1 (post-trained buttons).
2. New hardware: machine-drift check, Gate 2a (Qwen3-14B base), Gate 2, Gate 3.
3. Gate 4 if practical; Gate 5 skeleton starts during step 2; Gate 6 after author comments.

## Global stopping rules

1. **Negative results complete experiments.** They do not automatically authorize new experiments.
2. **Instrumentation defects justify repairs.** Disappointing observations do not justify retuning.
3. **Freeze before cross-model runs.** Changes after observing results must be versioned and labeled exploratory.
4. **Don't force a noun.** Pain, distress, vitality, self-evaluation, and persona implications remain hypotheses, not required conclusions.
5. **Don't conflate measurement with experience.** Neither activation separation nor successful steering alone establishes felt pain or pleasure.
6. **No compulsory O-Lens work.** The O-Lens causal-validation project begins after this report.
7. **No full-paper reproduction requirement.** This project succeeds by producing novel, carefully characterized observations, not matching the original team's scope.
8. **Publication is the finish line.** New questions go into a follow-up document, not into the active critical path.
9. **[added] Every detour is gated and time-boxed.** A new branch enters this file with a goal, pass criteria, outcomes, and a time box before any work on it starts.

## Final handoff

On completion, the repository should contain:

- `doc/FINISH-LINE.md` — this plan and final gate dispositions.
- A technical report source and rendered PDF.
- A short results/claims index linking findings to artifacts.
- Stable analysis code, frozen configurations, and plot source data.
- `doc/writeup/dont-call-it-pain.md` — LW text.
- A short `FUTURE-WORK.md` or equivalent capturing deferred research, especially O-Lens causal validation **[added]** and a reusable lens-refit pipeline with calibration tables across models.

**Definition of done:** We have contributed a bounded, reproducible, intellectually useful extension of the Pain Axis research, explained its limitations, published the findings, and cleanly handed the remaining questions to future work.

*We don't need to settle what pain is to discover that this representation deserves a better investigation.*
