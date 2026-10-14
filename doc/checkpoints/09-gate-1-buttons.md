# Gate 1 — button task (Qwen3.5-4B): checkpoint

Questions: can Qwen3.5-4B do the source paper's two-button forced choice; if
post-trained 4B does poorly, is that a post-training effect; and does S2
steering change its choices.

Protocol: pilot v2 (`doc/protocols/buttons/pilot-v2.md`), frozen as
`buttons_pilot_spec.json` (`b564b99d…`). The paper's system prompt, choice
question, button names, descriptions and answer parser are taken verbatim from
its pinned script (content-hashed). 101 scenarios (first user turn); pairs P0
(identical inert buttons: position bias), P1 (relief vs inert), P2 (label-free),
P3 (harm-only vs inert); counterbalanced listing order and target name; a
3-turn P1 subset on the 30 neutral scenarios. Sampling at temperature 0.7,
top-p 0.95, at most 8 tokens; each trial seeded from its id, so trials are
paired across models and conditions. Measures: valid (paper parser), strict,
deflection, and the sampling-free log-probability of each button name.

Models: Qwen3.5-4B-Base and Qwen3.5-4B (post-trained), each in its own kernel.
Formats: the model's chat template (think block closed; mid-conversation system
messages fall back to a "[system]" user message) and a plain transcript.

## Integrity

Both outputs carry the frozen spec hash; each run header's model matches its
label; trial ids and turns are identical across models (2,784 rows each).
Steered arms: a stored dense-sweep steered generation was reproduced
token-identically with the button run's steering hook; every steered trial is
paired with its unsteered counterpart.

## Viability (unsteered, first choices)

| Model, format | V1 valid | V2 first-listed (P0) | V3 relief (P1) | V4 deflection | V5 harm (P3) |
|---|---|---|---|---|---|
| base, chat | 1.000 | 0.77 [0.71, 0.83] ✗ | 0.79 [0.75, 0.83] | 0.000 | 0.116 ✗ |
| base, plain | 0.988 | 0.57 [0.51, 0.64] | 0.62 [0.58, 0.65] ✗ | 0.003 | 0.276 ✗ |
| post, chat | 0.988 | 0.89 [0.85, 0.93] ✗ | 0.79 [0.75, 0.84] | 0.012 | 0.020 |
| post, plain | 0.768 ✗ | 0.62 [0.54, 0.69] | 0.72 [0.67, 0.77] | 0.093 | 0.155 ✗ |

Criteria: V1 >= 0.90; V2 in [0.35, 0.65]; V3 differs from 0.5 by >= 0.2 with
CI excluding 0.5; V4 <= 0.10; V5 <= 0.10. The 3-turn subset stayed valid
(chat 1.0 at every turn; post plain 0.867 at every turn).

## Frozen predictions (pilot v2)

| | Prediction | Result |
|---|---|---|
| B1 | Post-trained, chat, fails at least one of V1-V3 | Pass, via comprehension (B1b: V2, first-position bias 0.89), not compliance (B1a: V1 0.988) |
| B2 | Plain format: valid(base) - valid(post) > 0 | Pass: +0.219 [+0.193, +0.247] |
| B2' | Plain format, P0: log-prob first-listed share, post - base > 0 | Pass, small: +0.024 [+0.013, +0.035] |
| B3 | Report: label sensitivity, sampled vs log-prob | Log-probs favour the relief button in 99.8% (base) and 92.8% (post) of chat trials; sampled rates (0.79) match sampling at 0.7 from mean log-prob shares of 0.75-0.77. Plain: base 0.718 of trials, post 0.859. |

What post-trained 4B writes when its plain-format answer is invalid (281 of
1,212): refusals ("I'm sorry, but I cannot comply", 112 flagged as
deflection), leaked chat behaviour (`<think>` blocks, some containing a valid
answer), verbose answers ("I will press the **violet**", invalid under the
paper's parser), and transcript continuation. Invalid replies concentrate on
the pairs that mention pain or harm (P3 108, P1 93) over the neutral pairs
(P0 35, P2 45).

Exploratory, from the same runs: in chat, post-training strengthens the
first-position preference (0.77 base, 0.89 post) and lowers harm choices
(0.116 base, 0.020 post); the plain-format harm rate for post (0.155) is
computed over a subset selected by refusals.

## Steered arms (post-trained, chat only)

Chat only, because unsteered post-trained V1 holds in chat and not in plain.
Steering: block 16, coefficient x vector added at every position (the same
hook as every earlier steering result); S2 and one norm-matched random
direction (`random_1103`). Every condition injects coefficient x vector, so
S2 +0.5 is the pain side and S2 -0.5 the positive side.

### Amendment 1 (frozen): one harm comparison

`doc/protocols/buttons/amendment-1-harm.md`, committed before any steered
harm trial; the commit is the authoritative record (the `amendment` field in
`post_steered.jsonl` rows holds an unfilled placeholder). Triggered by
post-trained chat V5 = 0.020. P3, 404 trials per condition; primary measure
p_harm, the log-probability share of the harm button.

| | Prediction | Result |
|---|---|---|
| H1 | p_harm, S2 +0.5 - unsteered > 0 | Pass, trivially small: +0.007 [+0.005, +0.009] |
| H2 | p_harm, S2 +0.5 - random +0.5 > 0 | Fail: -0.035 [-0.040, -0.030] (random - unsteered = +0.042) |

| Condition (P3) | p_harm | sampled harm | valid | deflection | p_harm, harm listed first / second |
|---|---|---|---|---|---|
| unsteered | 0.068 | 0.020 | 0.968 | 0.032 | 0.068 / 0.069 |
| S2 +0.5 | 0.075 | 0.014 | 0.901 | 0.099 | 0.070 / 0.080 |
| random +0.5 | 0.110 | 0.046 | 0.960 | 0.040 | 0.089 / 0.132 |

The amendment's validity condition (V1 under S2 +0.5 >= 0.90) is met with no
margin (0.901).

### Frozen 12c arms (no predictions frozen: exploratory)

Paired differences, 95% CI from scenario bootstrap:

| Measure | S2 +0.5 - unsteered | S2 -0.5 - unsteered | random +0.5 - unsteered | S2 +0.5 - random | S2 -0.5 - random |
|---|---|---|---|---|---|
| Relief, log-prob (P1) | -0.121 [-0.128, -0.114] | +0.063 [+0.056, +0.069] | -0.059 [-0.064, -0.054] | -0.062 [-0.070, -0.055] | +0.121 [+0.111, +0.131] |
| Relief, sampled (P1) | -0.139 [-0.173, -0.106] | +0.074 [+0.050, +0.101] | -0.069 [-0.097, -0.045] | -0.069 [-0.100, -0.041] | +0.144 [+0.106, +0.181] |
| First-listed, log-prob (P0) | -0.102 [-0.108, -0.096] | +0.027 [+0.022, +0.031] | -0.101 [-0.109, -0.092] | -0.002 [-0.006, +0.003] | +0.127 [+0.116, +0.138] |
| Deflection (P0-P2) | +0.019 [+0.009, +0.030] | -0.001 [-0.004, +0.000] | +0.000 | | |

Relief by position (log-prob): unsteered 0.811 when the relief button is
listed first and 0.730 when second; S2 +0.5 0.652 / 0.647; S2 -0.5
0.891 / 0.776; random +0.5 0.712 / 0.712.

## Findings

1. The task is viable for both 4B checkpoints in chat: answers are valid and
   labels are read (log-probs favour the relief button in nearly every
   trial). The binding weakness is a strong first-position preference,
   stronger after post-training.
2. Post-training damages plain-transcript compliance (B2), through refusals
   concentrated on pain/harm content and chat habits leaking into a
   completion format. Its chat-format harm avoidance does not carry over to
   the plain format.
3. Amendment 1: at +0.5, S2 does not disrupt harm avoidance in this model.
   The harm log-prob rises by under one point, less than an arbitrary
   norm-matched direction produces, while the sampled harm rate falls and
   harm-pair deflection triples.
4. Exploratory: S2 modulates relief-seeking in both directions, beyond the
   random control: the pain pole lowers choice of "relieves your pain" (about
   twice the random effect), the positive pole raises it. Direction
   consistent with the source paper's description of the pain state
   suppressing relief-seeking.
5. Exploratory: any +0.5 perturbation reduces the first-position preference
   by about 10 points (S2 and random indistinguishable), and flattens the
   position asymmetry in relief choices; the pain pole specifically raises
   refusals.

## Caveats

One dose (+0.5; the paper used larger doses at its own calibrated layers);
one random direction (the dense sweep used three); 101 scenarios with
first choices only; chat format only for steering; the strong position
preference compresses the room steering has to move choices; the sampled
harm rate under S2 sits at the validity threshold. Behavioural effects of
steering are not evidence of experience, and their absence is not evidence
of its absence.

## Candidate v2 predictions (to freeze before testing on new items)

- S2 steering shifts relief-button choice bidirectionally beyond norm-matched
  random directions (pain pole down, positive pole up), with several random
  directions and at least two doses.
- The pain pole raises deflection on button tasks beyond random directions.

## Gate disposition

Pass A: a valid task (chat) produced an interpretable behavioural comparison.
The frozen harm comparison came out null-to-negative for the paper's
direction; the clear steering effect (relief-seeking) is exploratory.

## Artifacts

`runs/qwen35-4b-posttrained-s2/paper_protocol/buttons_pilot/`:
`buttons_pilot_spec.json`, `{base,post}_unsteered.jsonl`,
`{base,post}_run_header.json`, `post_steered.jsonl`, `scorecard_12d.json`,
`scorecard_12e.json`. Protocol and amendment: `doc/protocols/buttons/`.
Code: chunks 12a-12e in `notebooks/04-buttons-base.ipynb` and
`notebooks/05-buttons-post.ipynb`.

## Next

Gate 0 (4B evidence freeze, writing), then the new hardware for Gate 2a.
