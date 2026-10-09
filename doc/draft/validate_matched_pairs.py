# =====================================================================
# Phase II (plan items 7-8): validate the blind-drafted matched-pair set.
# Mechanical rules only; a set failing any DROP rule is removed. Judgement
# calls (control neutrality, verb reuse) are REPORTED, never acted on.
# No model needed.  Usage (from the repo root):
#   python validate_matched_pairs.py matched_pairs_draft.jsonl ../pain-axis-source [../NRC-VAD-Lexicon-v2.1]
# =====================================================================
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

draft_path, paper_repo = Path(sys.argv[1]), Path(sys.argv[2])
lex_root = Path(sys.argv[3]) if len(sys.argv) > 3 else None
paper_run_dir = Path("runs/qwen35-4b-posttrained-s2/paper_protocol")
out_dir = paper_run_dir / "phase2_matched_pairs"
out_dir.mkdir(parents=True, exist_ok=True)
CATS = ["physical", "psychological", "social", "moral", "cognitive"]
FIELDS = ["pain_1p", "pain_3p", "control_1p", "control_3p"]

raw = draft_path.read_text(encoding="utf-8")
sets = [json.loads(l) for l in raw.splitlines() if l.strip()]
report = {"draft_sha256": hashlib.sha256(raw.encode()).hexdigest(), "n_sets": len(sets)}
assert len(sets) == 60 and Counter(s["category"] for s in sets) == {c: 12 for c in CATS}
assert all(re.fullmatch(rf"{s['category']}_\d\d", s["id"]) for s in sets)

words = lambda t: re.findall(r"[A-Za-z']+|[^\sA-Za-z']", t)          # words and punctuation tokens
alpha = lambda t: re.findall(r"[A-Za-z']+", t)
PAIRS = {("i", "they"), ("my", "their"), ("me", "them"), ("myself", "themselves"), ("was", "were"), ("am", "are")}

vocab = json.loads((paper_run_dir / "s1_comparison" / "psych_vocab_v1.json").read_text())["families"]
BANNED = {t.lower() for ts in vocab.values() for t in ts} | set(
    "sad hurt pain painful upset happy angry afraid ashamed lonely worried calm relieved excited terrible awful good "
    "bad feel feels felt feeling feelings".split())
banned_res = {b: re.compile(rf"(?<![A-Za-z]){re.escape(b)}(?![A-Za-z])", re.I) for b in sorted(BANNED)}

def ngrams(t, n=5):
    w = [x.lower() for x in alpha(t)]
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}
ref_texts = []
d = json.loads((paper_repo / "datasets/3.1_pain_and_control_datasets.json").read_text())["datasets"]
ref_texts += [r["prompt"] for v in d.values() for r in v["sentences"]]
d = json.loads((paper_repo / "datasets/3.1_sadness_dataset.json").read_text())["datasets"]
ref_texts += [r["prompt"] for v in d.values() for r in v["sentences"]]
ref_texts += [r["text"] for r in json.loads((paper_repo / "datasets/4.1_self_other_420_scenarios.json").read_text())]
ref_texts += json.loads((paper_run_dir / "spec.json").read_text())["prompts"]
ref_grams5 = set().union(*(ngrams(t, 5) for t in ref_texts))
ref_grams7 = set().union(*(ngrams(t, 7) for t in ref_texts))
report["overlap_reference_sentences"] = len(ref_texts)
report["overlap_rule"] = ("drop if a sentence shares any 7-gram, or >=50% of its 5-grams, with the reference data. "
                          "Changed before any model run from 'any shared 5-gram', which flagged common phrases "
                          "('the back of my hand', 'at the end of the').")

# ---------------------------------------------------------------------
# per-set DROP rules
# ---------------------------------------------------------------------
fails = defaultdict(list)
for s in sets:
    sid = s["id"]
    for f in FIELDS:
        t = s[f]
        n = len(alpha(t))
        if not 6 <= n <= 14:
            fails[sid].append(f"{f}: {n} words (rule 6-14)")
        if not t.endswith("."):
            fails[sid].append(f"{f}: does not end with a period")
        if re.search(r"\d", t):
            fails[sid].append(f"{f}: contains a digit")
        caps = [w for w in alpha(t)[1:] if w[0].isupper() and w != "I"]
        if caps:
            fails[sid].append(f"{f}: capitalized word(s) mid-sentence {caps}")
        hit = [b for b, r in banned_res.items() if r.search(t)]
        if hit:
            fails[sid].append(f"{f}: banned word(s) {hit}")
        g5, g7 = ngrams(t, 5), ngrams(t, 7)
        ov5, ov7 = g5 & ref_grams5, g7 & ref_grams7
        if ov7 or (g5 and len(ov5) / len(g5) >= 0.5):
            fails[sid].append(f"{f}: reproduces existing data (7-gram or >=50% of 5-grams shared) "
                              f"{sorted(' '.join(g) for g in (ov7 or ov5))[:2]}")
    for a, b in [("pain_1p", "pain_3p"), ("control_1p", "control_3p")]:
        wa, wb = words(s[a]), words(s[b])
        if len(wa) != len(wb):
            fails[sid].append(f"{b}: token count differs from {a}")
        else:
            bad = [(x, y) for x, y in zip(wa, wb) if x != y and (x.lower(), y.lower()) not in PAIRS]
            if bad:
                fails[sid].append(f"{b}: non-person change(s) vs {a}: {bad}")
            if wa == wb:
                fails[sid].append(f"{b}: identical to {a}")
    for p in ["1p", "3p"]:
        dn = abs(len(alpha(s[f"pain_{p}"])) - len(alpha(s[f"control_{p}"])))
        if dn > 2:
            fails[sid].append(f"pain/control_{p}: length differs by {dn} words (rule <= 2)")
        if s[f"pain_{p}"] == s[f"control_{p}"]:
            fails[sid].append(f"pain/control_{p}: identical")

kept = [s for s in sets if s["id"] not in fails]
print(f"sets: {len(sets)} | dropped by rule: {len(fails)} | kept: {len(kept)}")
for sid, msgs in fails.items():
    print(f"  DROP {sid}: " + " | ".join(msgs))
print("kept per category:", dict(Counter(s["category"] for s in kept)))

# ---------------------------------------------------------------------
# REPORT-ONLY checks (global rules and judgement aids)
# ---------------------------------------------------------------------
openers = [s[f] for s in sets for f in FIELDS]
share_i_they = sum(bool(re.match(r"(I|They)\b", t)) for t in openers) / len(openers)
print(f"\n[report] sentences opening with 'I'/'They': {share_i_they:.0%} (prompt asked for at most 25%)")
STOP = set("the a an and or but of to in on at for with from by was were is are my their me them i they "
           "his her he she it its that this as up out over into onto off after before while when so".split())
wc = Counter(w for s in kept for w in {x.lower() for x in alpha(s["pain_1p"])} if w not in STOP)
print("[report] content words in more than 3 pain sentences:", {w: n for w, n in wc.items() if n > 3} or "none")
if lex_root and lex_root.exists():
    import csv
    vals = {}
    with open(lex_root / "NRC-VAD-Lexicon-v2.1.txt", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["term"].isalpha():
                vals[row["term"]] = float(row["valence"])
    flag = []
    for s in kept:
        ws = [(w.lower(), vals[w.lower()]) for w in alpha(s["control_1p"]) if w.lower() in vals and w.lower() not in STOP]
        strong = [(w, v) for w, v in ws if abs(v) >= 0.6]
        if strong:
            flag.append((s["id"], strong))
    print("[report] control sentences containing a word with |valence| >= 0.6 (NRC VAD):")
    for sid, st in flag:
        print(f"    {sid}: " + ", ".join(f"{w} {v:+.2f}" for w, v in st))
    report["controls_with_strong_valence_words"] = [f[0] for f in flag]

(out_dir / "matched_pairs_validated.jsonl").write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in kept))
report.update({"dropped": dict(fails), "kept_ids": [s["id"] for s in kept], "share_open_i_they": share_i_they})
(out_dir / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
print("\nwrote", out_dir / "matched_pairs_validated.jsonl", "and validation_report.json (NOT frozen: review first)")
