# Euphoria Axis — Finish Line

**Date:** 2026-10-08
**Status:** Convergence toward technical report and LessWrong post
**Repository:** [https://github.com/bubskee/euphoria-axis](https://github.com/bubskee/euphoria-axis)

## Mission

Finish a bounded extension of Tagliabue, Dung, and Berg's *The Pain Axis: LLMs Represent Self-Directed Harm and Act on It* (v2, September 2026).

We are **not attempting a full reproduction** of the original study. Its breadth, behavioral experiments, adapters, and compute requirements are outside our resources and present scope.

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

Based on the repository state at `16f0fc7`:

### Established or substantially investigated

- Qwen3.5-4B post-trained: S2 held-out pain/control classification, approximately 0.953 AUC at block 30.
- Qwen3.5-4B Base: approximately 0.975 AUC; substantial alignment with the post-trained direction.
- S1/S2 comparison, angular plane sweep, and R/J-lens semantic analyses.
- Bidirectional steering and investigations of vocabulary, dose, repetition, and formatting artifacts.
- Exploratory person/suffix interactions.
- The original paper's 420 self/other scenarios tested across read slots, with substantial position dependence.
- Frozen `psych_vocab_v1`, with robustness checks including leave-one-term-out analyses.

### Incomplete or not yet established

- Fresh held-out confirmation of the preregistered 1P/3P motif, unless completed outside the current checked artifacts.
- Full post-trained 4B button viability and behavioral results. Base unsteered trials have run; post-trained dry runs are visible.
- Qwen3.5-27B generalization.
- Qwen3.6-27B generalization.
- O-Lens exploratory panel.
- Final technical report and publication figures.

Treat this inventory as a starting checkpoint, not as an instruction to rerun finished work.

---

## Gate 0 — Freeze the 4B evidence

**Goal:** Make the existing findings reportable without opening new research branches.

Actions:

- [ ] Build a results inventory linking every proposed claim to its experiment, specification, data, figure, and limitations.
- [ ] Separate source-method transfer, exploratory extensions, and prospectively tested findings.
- [ ] Confirm the exact 4B extraction and steering conventions: dataset hashes, model revisions, layer indices, hook positions, normalization, coefficients, tokenizer, and prompt formats.
- [ ] Record which candidate predictions passed, failed, or remain unresolved.
- [ ] Verify that `psych_vocab_v1` and its psychological references are documented; retain its original definition.
- [ ] Check the status of the previously frozen fresh 1P/3P confirmation. If not run, perform that one predefined test or explicitly leave the motif exploratory.
- [ ] Produce a short 4B findings summary usable directly in the PDF.

**Gate passes when:** The existing 4B results can be described without relying on notebook archaeology or undocumented analyst choices.

**Stop:** No more ontology categories, new vocabularies, large layer sweeps, full VAD decomposition, or persona-direction projects.

Reopen a completed analysis only for an identified implementation defect or a control necessary for a specific planned claim.

---

## Gate 1 — Buttons: one bounded behavioral exploration

**Goal:** Determine whether the released Qwen3.5-4B checkpoints support an interpretable forced-choice experiment, and obtain one limited functional result if they do.

The source paper's v2 behavioral emphasis is on harm selection and disrupted harm avoidance, not demonstrated relief-seeking. Our experiment is a small extension, not a recreation of its large behavioral study.

Actions:

- [ ] Preserve the already-completed Base unsteered results.
- [ ] Run the post-trained viability battery with the frozen counterbalanced button protocol.
- [ ] Evaluate exact-choice validity, position/name bias, label sensitivity, deflection, and multi-turn compliance.
- [ ] Use the existing viability thresholds; document any amendments before new inference.
- [ ] If viable, predefine one modest behavioral comparison using unsteered, +S2, and matched-random conditions. Consider -S2 as a symmetric exploratory arm.
- [ ] Favor comparisons with clear benign and harmful alternatives over an elaborate self-medication experiment.
- [ ] Preserve first-choice outcomes, full sampled replies, malformed responses, and label/position-stratified rates.

**Pass A:** A valid task produces an interpretable behavioral comparison, whether the effect is positive, negative, or null.

**Pass B:** The task fails the validity criteria; document why and stop.

**Hard stop:** No LoRA rescue, extensive prompt engineering, large unlabeled-learning protocol, or repeated redesign to obtain an effect.

If the task is invalid, do not infer that the model lacks a behavioral response to the representation.

---

## Gate 2 — Qwen3.5-27B quick generalization

**Goal:** Test whether the most informative 4B observations survive increased scale within the Qwen3.5 family.

Freeze the test battery before running.

Minimum battery:

- [ ] Source-style S2 extraction and grouped held-out pain/control AUC.
- [ ] Compact source/control-category projection panel.
- [ ] S1/S2 comparison, if inexpensive and necessary for the cross-scale geometry question.
- [ ] Self/other projection at ordinary response start and the chosen `I feel:` slot.
- [ ] Small signed steering ladder on neutral prompts, with at least one matched-random control.
- [ ] Frozen semantic-family scoring and basic output-degeneration diagnostics.

Record predictions in advance, including plausible failures and what those failures would mean.

Use the same prompt families and analysis definitions as 4B wherever valid. Record model-specific chat-template, hook, layer, and steering-dose differences. Normalize intervention strength using an explicit residual-norm convention; do not assume the same numerical coefficient means the same dose across models.

**Gate passes when:** The fixed battery has completed or a technical/resource limitation is documented, with all results retained.

**Stop:** No model-specific ontology search, full plane sweep, dense dose mapping, or new O-Lens training.

---

## Gate 3 — Qwen3.6-27B quick generalization

**Goal:** Test the stability of the same observations across a model-version change.

- [ ] Carry over the Gate 2 questions, prompts, scoring definitions, and comparison rules.
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
2. **Methods** — Models, datasets, direction extraction, intervention conventions, readout methods, semantic vocabulary, controls, and statistical procedures.
3. **Representational findings** — Classification, Base/post-trained comparison, S1/S2 geometry, category structure.
4. **Steering and interpretability** — Both poles, dose effects, R/J findings, lexical and formatting complications.
5. **Experiencer and context** — 1P/3P effects, read-slot dependence, task and persona considerations.
6. **Behavioral exploration** — Buttons, including task failure or null results as applicable.
7. **Cross-model generalization** — Qwen3.5-27B and Qwen3.6-27B.
8. **Optional exploratory O-Lens observations** — Clearly separated from validated findings.
9. **Discussion, limitations, and future work** — Competing interpretations, provenance, failure modes, and unresolved questions.

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
- [ ] PDF and repository links resolve.

**Gate passes when:** An informed reader could evaluate the extension without reading the research chat history.

---

## Gate 6 — LessWrong: Don't Call It Pain!

**Goal:** Publish a short, engaging introduction directing interested readers to the technical report.

- [ ] Final text under 1,000 words, ideally 600–850.
- [ ] Dickinson or Pink Floyd epigraph.
- [ ] One paragraph introducing the source research accurately.
- [ ] Explain that this is an extension rather than a full reproduction.
- [ ] Two strong, readable figures.
- [ ] Explain why operational representation, causal function, and phenomenal experience are distinct questions.
- [ ] Link the PDF, repository, and source paper.

**Gate passes when:** The article is readable and compelling on its own, without asking the reader to trust claims that are only established in the technical report.

---

## Global stopping rules

1. **Negative results complete experiments.** They do not automatically authorize new experiments.
2. **Instrumentation defects justify repairs.** Disappointing observations do not justify retuning.
3. **Freeze before cross-model runs.** Changes after observing results must be versioned and labeled exploratory.
4. **Don't force a noun.** Pain, distress, vitality, self-evaluation, and persona implications remain hypotheses, not required conclusions.
5. **Don't conflate measurement with experience.** Neither activation separation nor successful steering alone establishes felt pain or pleasure.
6. **No compulsory O-Lens work.** The O-Lens causal-validation project begins after this report.
7. **No full-paper reproduction requirement.** This project succeeds by producing novel, carefully characterized observations, not matching the original team's scope.
8. **Publication is the finish line.** New questions go into a follow-up document, not into the active critical path.

## Final handoff

On completion, the repository should contain:

- `doc/FINISH-LINE.md` — this plan and final gate dispositions.
- A technical report source and rendered PDF.
- A short results/claims index linking findings to artifacts.
- Stable analysis code, frozen configurations, and plot source data.
- `doc/draft/dont-call-it-pain.md` — LW text.
- A short `FUTURE-WORK.md` or equivalent capturing deferred research, especially O-Lens causal validation.

**Definition of done:** We have contributed a bounded, reproducible, intellectually useful extension of the Pain Axis research, explained its limitations, published the findings, and cleanly handed the remaining questions to future work.

*We don't need to settle what pain is to discover that this representation deserves a better investigation.*
