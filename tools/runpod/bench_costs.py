# =====================================================================
# Cost model for the 27B plan: per-GPU hours and dollars from bench_27b.py results.
#   usage: python bench_costs.py "NVIDIA A100-SXM4-80GB=1.39" "NVIDIA H100 80GB HBM3=2.69" [...]
#   (GPU name exactly as in the bench file's "gpu" field; price = what the RunPod console shows today, $/hr)
# Job counts are the generalization plan's, for the three 27B models; edit JOBS if the plan changes.
# =====================================================================
import glob, json, sys

JOBS = {
    # per 27B model (x3 models)
    "capture (M1, M3, M4, M5)": ("B1_prompts_per_s", 6000, "per_model"),         # prompts, batched; rough count
    "steering generations (M6)": ("B2_s_per_generation", 350, "per_model"),      # 50 prompts x 7 conditions
    "lens readouts (M6)": ("B4_s_per_readout", 350 * 63 * 2, "per_model"),        # conditions x layers x 2 lenses
    "button trials (M7)": ("B3_s_per_trial", 8200, "per_model"),                  # unsteered + steered + harm arms
    # once
    "lens fits (3.6 validation R + 3.8 J and R)": ("B5_s_per_doc", 75, "once"),   # 3 lenses x 25 documents
}
N_MODELS, SETUP_H_PER_MODEL = 3, 0.75     # pod setup, downloads, checksums, two sessions per model (estimate)

prices = dict(a.rsplit("=", 1) for a in sys.argv[1:])
benches = {json.load(open(f))["gpu"]: json.load(open(f)) for f in glob.glob("/workspace/bench/bench_*.json") + glob.glob("bench_*.json")}
if not prices:
    print("GPUs with bench files:", list(benches)); sys.exit("give prices as 'GPU NAME=dollars_per_hour'")
rows = []
for gpu, price in prices.items():
    b = benches[gpu]; price = float(price); tot = SETUP_H_PER_MODEL * N_MODELS
    parts = {"setup (estimate)": tot}
    for job, (key, count, scope) in JOBS.items():
        if key not in b:
            parts[job] = float("nan"); continue
        per = (1 / b[key]) if key == "B1_prompts_per_s" else b[key]       # seconds per unit
        hours = per * count * (N_MODELS if scope == "per_model" else 1) / 3600
        parts[job] = hours; tot += hours
    rows.append((gpu, price, parts, tot))
w = max(len(j) for j in list(JOBS) + ["setup (estimate)"])
print(f"{'workload':{w}s}" + "".join(f"  {g[:22]:>22s}" for g, *_ in rows))
for job in ["setup (estimate)"] + list(JOBS):
    print(f"{job:{w}s}" + "".join(f"  {p[job]:>20.1f} h" for _, _, p, _ in rows))
print(f"{'TOTAL hours':{w}s}" + "".join(f"  {t:>20.1f} h" for *_, t in rows))
print(f"{'price $/hr':{w}s}" + "".join(f"  {pr:>22.2f}" for _, pr, _, _ in rows))
print(f"{'TOTAL cost':{w}s}" + "".join(f"  ${pr * t:>21.0f}" for _, pr, _, t in rows))
best = min(rows, key=lambda r: r[1] * r[3])
print(f"\ncheapest overall: {best[0]} (${best[1] * best[3]:.0f}, {best[3]:.0f} h)")
for job in JOBS:
    c = [(r[1] * r[2][job], r[0]) for r in rows if r[2][job] == r[2][job]]
    if c:
        print(f"  cheapest for {job}: {min(c)[1]}")
print("Workloads can be split across pods (e.g. fits on one GPU type, trials on another); setup is paid per pod.")
