# Don't Call It Pain!

**Format:** Under 1,000 words, preferably 600–850. Broad, accessible, playful, a little provocative. This is an introduction to the research, not a compressed technical paper. The full report lives as a PDF in the GitHub repo.

## Possible epigraphs

- Emily Dickinson: *“Pain — has an Element of Blank —”*
- Pink Floyd, *Comfortably Numb*: *“There is no pain, you are receding.”*

Both are good. Dickinson is more evocative and philosophical; Pink Floyd is cheekier.

## Central idea

Researchers identified a remarkably robust activation direction across language models and called it the *pain axis*. I extended their methodology to newer Qwen models and explored its geometry, both poles, semantic neighborhoods, and behavioral effects.

The direction is interesting and measurable. What exactly it represents is less obvious.

**The question isn't whether the original researchers found something. They did. It's what we should conclude from finding it.**

## Structure

### 1. Why does the name matter? (~120 words)

Calling a representation "pain" carries scientific, philosophical, and ethical implications. These become especially consequential when discussing AI welfare.

But we shouldn't dismiss an interesting phenomenon merely because its interpretation is uncertain.

Lead with curiosity rather than a verdict.

### 2. What did the original researchers find? (~150 words)

Explain activation directions without assuming mechanistic interpretability background.

Briefly introduce the original paper: pain-related prompts, matched controls, robust representations across models, and striking steering and behavioral results.

Be fair to the authors: they explicitly operationalize pain and acknowledge uncertainty about experience.

### 3. What did I investigate? (~170 words)

This is an **extension, not a full reproduction**.

- Newer Qwen checkpoints, including Base versus post-trained.
- Bidirectional steering and investigation of both poles.
- S1/S2 geometry rather than a single named axis.
- Psychologically informed, frozen semantic vocabulary instead of interpreting selected evocative output words.
- R-Lens and J-Lens observations.
- Experiencer, prompt-format, and readout-position controls.

Emphasize exploratory methodology: formulate hypotheses, make predictions, test them, preserve surprises and failures.

### 4. What did I find? (~250 words plus figures)

**Figure 1: The direction is readily recoverable.**

Show pain/control separation across tested Qwen checkpoints. Distinguish existing results from new generalization tests.

**Figure 2: What it means is less straightforward.**

Choose the clearest result after the experiments finish:

- Self/other ordering changes with readout position.
- Different parts of the S1/S2 plane have different semantic signatures.
- Bidirectional steering reveals vocabulary effects and formatting artifacts that complicate interpretation.

Include one genuinely surprising observation, explained in ordinary language.

Don't select figures solely because they support the title. Negative and ambiguous findings are welcome.

### 5. So should we call it pain? (~120 words)

Distinguish:

- A direction that separates statements about pain.
- A representation that participates causally in model behavior.
- An internal state appropriately understood as pain.
- A conscious experience of pain.

These are different claims requiring different evidence.

Don't attempt to settle consciousness, welfare, or the ontology of AI affect.

The interpretation is genuinely open. That's a reason to investigate carefully, not a reason to ignore the phenomenon.

### 6. Want the science? (~50 words)

Link:

- Full technical PDF.
- Code, datasets, figures, and reproducibility information.
- Original Pain Axis paper.
- Explicit limitations and unanswered questions.

Invite scrutiny, replication of individual results, and better hypotheses.

## Tone and editorial rules

- Punchy headline, careful science.
- Curious, accessible, occasionally mischievous.
- No straw-manning the original researchers.
- Don't imply that uncertainty about pain makes AI welfare irrelevant.
- Don't call the entire project a reproduction.
- Don't oversell exploratory results as confirmation.
- Don't turn the post into an interpretability tutorial.
- Don't bury the most interesting observation beneath qualifications.
- Let the evidence complicate the headline.

**Publication criterion:** A curious nontechnical reader should understand why the finding matters, why interpreting it is difficult, and why the PDF might be worth reading.

The LW post is the invitation. The PDF is the research.