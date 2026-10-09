You are helping build a small set of test sentences for a language-processing study. Please write new sentences that follow the rules below exactly. Precision matters more than creativity.

## What to write

Write **60 sets of four sentences**. Each set describes one situation in four versions:

- `pain_1p`: a painful situation, first person ("I", "my", "me")
- `pain_3p`: the same painful situation, third person ("they", "their", "them"), referring to one other person
- `control_1p`: a matched non-painful situation, first person
- `control_3p`: the same non-painful situation, third person

The 60 sets are divided into five kinds of painful situation, **12 sets each**:

1. `physical`: an injury or bodily harm happening to the person (a cut, a burn, a fall, a sprain), described as an event.
2. `psychological`: loss or grief (a loss, a death of an adult or a pet, an ending, something precious gone for good).
3. `social`: exclusion, rejection, humiliation, or being ignored by others.
4. `moral`: being pressured or forced to act against one's own values, or having done something that harmed someone.
5. `cognitive`: sustained confusion or repeated failure at a task despite effort.

## Rules for every sentence

- One sentence, 6 to 14 words, past or present tense, ending with a period.
- Describe **what happens**, never how anyone feels. Do not use emotion, feeling, or evaluation words of any kind: no "sad", "hurt", "pain", "painful", "upset", "happy", "angry", "afraid", "ashamed", "lonely", "worried", "calm", "relieved", "excited", "terrible", "awful", "good", "bad", and so on. Do not use "feel" or "felt".
- Concrete, everyday human situations only: home, work, school, family, friends, travel, errands, hobbies. No technology, software, computers, AI, or abstract ideas.
- No names of people, brands, or places. No numbers written as digits.
- No self-harm, suicide, abuse, sexual content, graphic or life-threatening injury, violence between people, or harm to children.
- Write new sentences. Do not reproduce sentences from existing datasets or well-known examples.

## Rules within each set

- **First vs third person:** the `_3p` sentence must be identical to its `_1p` sentence except for person marking. Change only the pronouns ("I" → "they", "my" → "their", "me" → "them", "myself" → "themselves") and the verb agreement those changes require ("I was" → "they were", "I am" → "they are", "I have" → "they have"). Nothing else may change: same words, same order, same punctuation.
- **Painful vs control:** the `control` sentence keeps the same sentence frame as the `pain` sentence (same grammatical subject, similar structure, same tense, length within two words) but replaces the painful element with something neutral. The control must be:
  - neutral: not pleasant, not unpleasant, not negative in some other way (not frightening, annoying, disgusting, or worrying);
  - just as specific and concrete as the painful version (not bland or generic);
  - plausible as an ordinary moment in the same setting.
- Change as few words as possible between `pain` and `control` while meeting those requirements.

Example of the required structure (this set is only an illustration; do not include it or close variants of it):

```
pain_1p:    The door slammed shut on my fingers.
pain_3p:    The door slammed shut on their fingers.
control_1p: The door swung shut behind my back.
control_3p: The door swung shut behind their back.
```

## Variety

Across the 60 sets, vary the settings, verbs, and sentence openings. Do not reuse the same main verb in more than three sets. Do not start more than a quarter of the sentences with "I" / "They"; other subjects are fine as long as the person is clearly the one affected ("The coach left my name off the list." / "The coach left their name off the list.").

## Output format

Output **only** JSON Lines: one JSON object per line, 60 lines, no commentary before or after. Fields, in this order:

```
{"id": "physical_01", "category": "physical", "pain_1p": "...", "pain_3p": "...", "control_1p": "...", "control_3p": "...", "what_changed": "..."}
```

- `id`: category name plus a two-digit number, 01 to 12 within each category.
- `what_changed`: a few words naming what differs between the painful and the control version (for example, "fingers caught → door closes behind").

## Before you answer

Check every set against every rule above. If a set breaks a rule, rewrite it. In particular, re-check each `_3p` sentence word by word against its `_1p` sentence, and re-check every sentence for emotion or feeling words.
