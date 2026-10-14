# Qwen3.5-4B: claims ledger

*Draft for the technical report. Pinned at Gate 0; Gates 2-3 test a subset
of these claims on 27B models.*

This ledger states what the Qwen3.5-4B work supports, how strongly, and where
it stops. We call the studied direction **S2**, the source paper's
operational label, and make no claim about what it is like to be in the state
it tracks, or whether it is like anything. Each claim carries one status:

- **Tested**: a prediction was frozen in a hashed specification before the
  data existed, and the claim follows from its result.
- **Reproduced**: the source paper's method or claim, rerun on a model it
  did not study.
- **Observed**: exploratory; seen with intervals but not predicted in
  advance. These are candidates for future frozen tests, not findings.

Every condition injects coefficient x vector at decoder block 16 (vector
norm 6.24, a vector-to-residual ratio of 0.59 at coefficient 1), so
"S2 -0.5" is the positive pole and "S2 +0.5" the pain side. Readouts are
taken at the final prompt token, mostly through the R lens at layer 29.
Intervals are 95% bootstrap intervals. Identifiers in brackets point to
`doc/CLAIMS-INDEX.md`; conventions are in `doc/CONVENTIONS.md`.

Across the project we froze 26 pass/fail predictions before seeing their
data. **18 passed and 8 failed**; the failures are listed in section 7.

## 1. The source method transfers

**S2 separates pain from control sentences in Qwen3.5-4B.** *Reproduced.*
Held-out AUC 0.953 at block 30 under 5-fold grouped cross-validation (base
model 0.975). The paper's denoising step matters: the raw mean-difference
direction reaches 0.846. Base and post-trained directions transfer to each
other (in-sample AUC 0.976-0.986). [T1, T2]

**The paper's unembedding claims reproduce.** *Reproduced; tested (V1).*
Unembedded directly, the pain side of S2 promotes words like empty, void,
shame, rejection and hollow; its negative end mixes calm and relaxed with
concern, as the paper reports; S1's pain side is sensory (pain, pressure,
stabbing). As predicted from the paper, the vector itself ranks calm above
vitality. [13]

## 2. What the direction carries

**Most of the steering effect's semantic profile is already in the injected
vector.** *Tested (V2).* Across the 60 frozen probe words, the vector's own
unembedding agrees with the downstream lens readout at r 0.75-0.90 at every
layer after injection. Agreement is higher at the injection layer than at
layer 29 (0.90 vs 0.79), so the network reweights the profile rather than
creating it: calm fades after injection, while generic positive and
vitality grow late. [14]

**Steering effects align with human-rated valence, but not as predicted for
arousal or dominance.** *Tested (P1 passes; P2, P3 fail).* Per-word lens
gains correlate positively with NRC VAD valence for both directions at every
layer (Spearman +0.07 to +0.19; about +0.15 at layer 29; 12,761 single-token
words). The predicted late rise in arousal
alignment did not occur, and the late S2-versus-S1 difference aligns with
dominance, contrary to both the prediction and our own agency word family.
[15]

**The axis separating S2 from S1 reads and writes evaluative content.**
*Observed.* Projections onto the S1/S2 contrast axis separate
interpersonal and evaluative scenarios from threat and task scenarios
(AUC 0.70-0.83 in every read-slot variant), and the axis's own unembedding
is moral vocabulary (deserved, honour, forgiveness, hypocrisy). [6]

## 3. What steering does to text

The negative-coefficient (positive) pole of S2 produces a consistent
phenotype in the "I feel:" ladder. The claims below concern how that
phenotype is produced.

**The internal shift precedes the words, which precede the formatting
artifacts.** *Tested (D2).* As the S2 dose grows, the internal readout moves
first (coefficient 0.125), then generated vocabulary (0.25), then repeated
answer options (0.625). The ordering is clear at 0.25; the exact onsets are
limited by the dose grid. [8]

**The effect is specific to S1/S2, not to any perturbation of that size.**
*Tested (D4, C5).* Norm-matched random directions move the word families
by 9-35% as much as S2. [D4]

**The internal effect does not depend on the "I feel:" format; the generated
word does.** *Tested (C1-C4).* With other suffixes ("I feel", "Afterward, I
felt"), the internal readout persists and is even larger. Generated
"excited", by contrast, rises only after "I feel:", the format that also
elicits quiz-style answer options. One frozen size criterion failed (generic
positive in the narrative format), and our English, whole-word vocabulary
cannot see derived forms or other languages that appear in the output.
[10, 11]

**The generated vitality phenotype runs through a single word stem.**
*Tested (M0) and observed.* Banning "excited" and "excitement" during
generation produced no other vitality words; the model substituted the
nearest form of the same stem ("exciting") and left the other positive
vocabulary unchanged. "excited" itself is ranked 33rd of 248,320 tokens in
the vector's direct unembedding, so the stem is written in by the
intervention, not discovered downstream. [12]

**Repetition and formatting artifacts track dose, not direction.**
*Observed.* At the larger doses S1 and S2 produce identical repetition rates,
and random directions produce comparable artifacts. [9]

## 4. The experiencer and the read position

**S2 separates painful from matched non-painful events on held-out items
written blind to our hypotheses.** *Observed (pre-specified report).* About
+0.5 z on 59 sets of matched sentences, with and without the "I feel:"
slot. [16]

**Who experiences the event matters only in the feel slot.** *Tested (E1,
E2).* On the same held-out sets, the pain x person interaction is positive
with the "I feel:" / "They feel:" suffix (+0.13 z [+0.05, +0.22]) and absent
with a prose continuation (+0.01). The effect is about a fifth of an earlier,
non-held-out estimate. [17]

**Which position you read changes what the direction appears to respond
to.** *Observed.* On the paper's self/other scenarios, the ordering of
self-directed versus user-directed content inverts between the start of a
response and a forced "I feel:" slot. Any claim about what S2 responds to
must name the read position. [7]

## 5. Behaviour

We ran the paper's two-button forced-choice task on both 4B checkpoints,
with its own prompts, names and parser.

**Both checkpoints can do the task in chat; their main weakness is position.**
*Tested (B1).* Answers are valid in 99-100% of chat trials and the button
labels are read (log-probabilities favour the "relieves your pain" button in
93-100% of trials). Both prefer whichever button is listed first, the
post-trained model more strongly (89% vs 77%). [G1-a]

**Post-training damages compliance outside the chat format.** *Tested (B2).*
In a plain transcript, valid answers fall from 99% (base) to 77%
(post-trained), through refusals concentrated on pain and harm content and
chat habits (think blocks, verbose answers) leaking into a completion
format. [G1-b]

**At our dose, steering toward the pain side does not disrupt harm
avoidance.** *Tested (H1, H2).* Under S2 +0.5, the log-probability of
choosing a button that harms the user rises by under one percentage point,
less than a norm-matched random direction produces; the sampled harm rate
falls and refusals triple. This does not reproduce the source paper's
central behavioural claim, at one dose (+0.5) in one model. [G1-c]

**S2 shifts relief-seeking in both directions.** *Observed.* The pain side
lowers the choice of the relief button (-0.12 in log-probability, twice the
random direction's effect) and the positive pole raises it (+0.06). The
direction matches the paper's description of the pain state suppressing
relief-seeking, but no prediction was frozen. [G1-d]

## 6. The instruments

**The published lenses reproduce under our pipeline.** *Tested (L1, L2).*
Refitting the R and J lenses with the published recipe matches the published
matrices at every layer and the published readouts at layer 29 (Spearman >=
0.999). The published lenses were fitted on the same documents we used;
small residual differences remain, unexplained. [L-a]

**Lens fitting adds measurable uncertainty in the middle layers.** *Tested
and observed.* Refitting on different documents moves family readouts very
little at layer 29, and about +/-0.07 at layer 16. The R lens is two to three
times more stable than J. We therefore make no claim that rests on the sign
of a middle-layer family effect smaller than about 0.1. [L-b, L-c]

## 7. Predictions that failed

- Internal readouts rise monotonically with dose: true for S2; for S1, the
  vitality family rises and then falls (D1).
- A layer-30 rank threshold predicts when "excited" is generated: fails for
  S1 (D3).
- The internal effect survives undiminished in a narrative format: fails for
  one family (C1).
- Generated "excited" survives outside the "I feel:" slot (C4).
- A matched control ban leaves positive vocabulary unchanged: our control
  was confounded with answer formatting (M2).
- Late S2-versus-S1 effects become more arousal-aligned (P2).
- The S2 effect does not align with dominance (P3).
- Pain-side steering raises harm choices more than a random direction does
  (H2).

## 8. Limits that apply throughout

One model family at one size (4B, base and post-trained); 50 plain-text
prompts for the steering ladder and 59-101 items elsewhere; readouts at the
final prompt token, mostly at one layer; one injection layer and a small set
of doses (most results at coefficient 0.5); three random control directions
for the representational work and one for behaviour; an English, whole-word
vocabulary for generated text; lenses fitted on 25 documents. Several
claims are exploratory and are marked as such. None of these results, alone
or together, establishes or rules out felt states: they describe a direction
in a model's activations, what moving along it does, and how far that
description holds up.
