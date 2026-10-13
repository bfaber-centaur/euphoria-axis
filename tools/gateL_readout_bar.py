# =====================================================================
# Gate L -- readout bar (L1 and L2), in the LENS SESSION (03-decursed kernel).
# Reads the plane-sweep conditions baseline / S1 -0.5 / S2 -0.5 (50 prompts) through the
# refit lenses and compares per-probe log-rank gains with the published lenses' frozen arrays.
#   L1 bar (frozen): refit J_n25 vs published J, refit R_n25 vs published R, at layer 29:
#                    per-probe Spearman >= 0.95 (each condition) and identical signs on the six focus families
#   L2 bar (frozen): refit J_n25 vs refit J_n100 at layer 29, same criteria
#   Exploratory:     the same comparisons at layers 16, 18, 22 (where the matrices moved more)
# Needs: capture_all_layers, lens_readout, ranks_for_tokens, j_lens, r_lens, probe_terms, PSYCH_VOCAB, jlens
# =====================================================================
import hashlib, json
from pathlib import Path
import numpy as np, pandas as pd, torch

for name in ["capture_all_layers", "lens_readout", "ranks_for_tokens", "j_lens", "r_lens", "probe_terms", "PSYCH_VOCAB", "jlens"]:
    assert name in globals(), f"run this in the lens session: {name} is not defined"

paper_run_dir = Path("runs/qwen35-4b-posttrained-s2/paper_protocol")
plane_dir, cal_dir = paper_run_dir / "plane_sweep", paper_run_dir / "lens_calibration"
REFITS = {"J_n25": "refit_J_n25_bos0_fast", "R_n25": "refit_R_n25_bos0_fast", "J_n100": "refit_J_n100_bos0_fast",
          # exploratory (not in the frozen gate): other documents, and R convergence
          "J_off25": "refit_J_n25_off25_bos0_fast", "R_off25": "refit_R_n25_off25_bos0_fast", "R_n100": "refit_R_n100_bos0_fast"}
BAR_LAYER, EXPL_LAYERS = 29, [16, 18, 22]
LAYERS = EXPL_LAYERS + [BAR_LAYER]
CONDS = ["S2_-0.5", "S1_-0.5"]
FOCUS = ["generic_positive", "activated_vitality", "relief_release", "agency_assurance", "approach_drive", "distress_self_devaluation"]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()

# 1. refit lenses: verified against the hash each fit recorded, then loaded (they stay on CPU; transport moves per call)
#    six lenses at ~0.8 GB each in RAM; drop the exploratory ones from REFITS (and PAIRS) if memory is tight
lenses = {}
for k, stem in REFITS.items():
    rec = json.loads((cal_dir / f"{stem}.json").read_text())
    assert sha256(cal_dir / f"{stem}.pt") == rec["refit_sha256"], f"{stem}.pt does not match its recorded hash"
    lenses[k] = jlens.JacobianLens.load(str(cal_dir / f"{stem}.pt"))
print("refits verified and loaded:", list(lenses))

# 2. inputs, exactly as the plane sweep injected them
sspec = json.loads((plane_dir / "sweep_spec.json").read_text())
layers_all, LENS_ORDER = sspec["lens"]["layers"], sspec["lens"]["lens_order"]
assert hashlib.sha256(probe_terms[["family", "term", "token_id"]].to_csv(index=False).encode()).hexdigest() == sspec["lens"]["probe_terms_sha256"]
prompts = json.loads((paper_run_dir / "spec.json").read_text())["prompts"]
sv = torch.load(paper_run_dir / "steering_vectors.pt", map_location="cpu", weights_only=True)
s1 = torch.load(paper_run_dir / "s1_comparison" / "s1_direction_block30.pt", map_location="cpu", weights_only=True)["matched_vector"]
COND = {"baseline": (0.0, None), "S1_-0.5": (-0.5, s1.float()), "S2_-0.5": (-0.5, sv["S2"].float())}
probe_ids = probe_terms.token_id.tolist()
pub = {}
for c in COND:
    with np.load(plane_dir / "lens" / f"{c}.npz") as z:
        pub[c] = z["rank"]                                   # [P, L_all, lens(J,R), K]
pub_at = lambda c, ln: pub[c][:, [layers_all.index(l) for l in LAYERS], LENS_ORDER.index(ln), :]   # [P, L, K]

# 3. gate: the published lenses read through this session reproduce the frozen arrays (prompts 0-1, all four layers)
for c, (coeff, vec) in COND.items():
    for i in [0, 1]:
        _, states = capture_all_layers(prompts[i], coeff, vec)
        for ln, lens in [("J", j_lens), ("R", r_lens)]:
            mine = np.array([ranks_for_tokens(lens_readout(lens, states[l], l), probe_ids) for l in LAYERS])
            assert (mine == pub_at(c, ln)[i]).all(), f"published {ln} readout not reproduced ({c}, prompt {i})"
print("gate: published J/R readouts reproduced exactly for prompts 0-1 in all three conditions")

# 4. refit readouts for all 50 prompts x 3 conditions
ref = {k: {c: np.zeros((len(prompts), len(LAYERS), len(probe_ids)), np.int64) for c in COND} for k in lenses}
for c, (coeff, vec) in COND.items():
    for i, text in enumerate(prompts):
        _, states = capture_all_layers(text, coeff, vec)
        for k, lens in lenses.items():
            for li, l in enumerate(LAYERS):
                ref[k][c][i, li] = ranks_for_tokens(lens_readout(lens, states[l], l), probe_ids)
print("refit readouts done")

# 5. per-probe mean log-rank gains vs baseline, and the comparisons
def gains(R):                                                  # {cond: [P, L, K]} -> {cond: [L, K]}
    return {c: np.log(R["baseline"] / R[c]).mean(0) for c in CONDS}
G = {"pub_J": gains({c: pub_at(c, "J") for c in COND}), "pub_R": gains({c: pub_at(c, "R") for c in COND}),
     **{k: gains(ref[k]) for k in lenses}}
fam_cols = {f: np.flatnonzero(probe_terms.family.to_numpy() == f) for f in FOCUS}
spear = lambda a, b: float(pd.Series(a).rank().corr(pd.Series(b).rank()))
PAIRS = {"L1 J (refit n25 vs published)": ("J_n25", "pub_J"), "L1 R (refit n25 vs published)": ("R_n25", "pub_R"),
         "L2 J (n25 vs n100)": ("J_n25", "J_n100"), "info: J n100 vs published": ("J_n100", "pub_J"),
         "expl: J docs 0-24 vs 25-49": ("J_n25", "J_off25"), "expl: R docs 0-24 vs 25-49": ("R_n25", "R_off25"),
         "expl: R n25 vs n100": ("R_n25", "R_n100")}
rows = []
for label, (a, b) in PAIRS.items():
    for li, l in enumerate(LAYERS):
        for c in CONDS:
            ga, gb = G[a][c][li], G[b][c][li]
            fa = {f: ga[fam_cols[f]].mean() for f in FOCUS}; fb = {f: gb[fam_cols[f]].mean() for f in FOCUS}
            rows.append({"comparison": label, "layer": l, "condition": c, "spearman": spear(ga, gb),
                         "signs_equal": all(np.sign(fa[f]) == np.sign(fb[f]) for f in FOCUS),
                         "max_abs_family_diff": max(abs(fa[f] - fb[f]) for f in FOCUS)})
T = pd.DataFrame(rows)
T.to_csv(cal_dir / "readout_bar.csv", index=False)
with pd.option_context("display.width", 200):
    print(T.pivot_table(index=["comparison", "condition"], columns="layer", values="spearman").round(4).to_string())
    print("\nfocus-family signs equal (all six):")
    print(T.pivot_table(index=["comparison", "condition"], columns="layer", values="signs_equal", aggfunc="all").to_string())

bar = lambda lab: bool(((T.comparison == lab) & (T.layer == BAR_LAYER)).any() and
                       T[(T.comparison == lab) & (T.layer == BAR_LAYER)].pipe(lambda d: (d.spearman >= 0.95).all() and d.signs_equal.all()))
verdict = {"L1_J": bar("L1 J (refit n25 vs published)"), "L1_R": bar("L1 R (refit n25 vs published)"), "L2": bar("L2 J (n25 vs n100)")}
print(f"\nlayer-29 bars (frozen): L1 J {'PASS' if verdict['L1_J'] else 'FAIL'} | L1 R {'PASS' if verdict['L1_R'] else 'FAIL'} | "
      f"L2 {'PASS' if verdict['L2'] else 'FAIL'}   (layers 16/18/22 above are exploratory)")
(cal_dir / "readout_bar.json").write_text(json.dumps({"verdict": verdict, "bar_layer": BAR_LAYER,
    "exploratory_layers": EXPL_LAYERS, "refits": {k: json.loads((cal_dir / f"{s}.json").read_text())["refit_sha256"]
    for k, s in REFITS.items()}}, indent=2) + "\n")
