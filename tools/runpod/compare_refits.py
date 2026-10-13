# Environment-drift check: two refits of the same lens from different package environments.
# If refit-vs-refit agreement is much tighter than either refit's agreement with the published
# lens, the environment change is negligible for Gate L.
#   usage: python compare_refits.py refit_J_n25_bos0_fast_env1.pt refit_J_n25_bos0_fast.pt
import json, sys
import torch

A, B = sys.argv[1], sys.argv[2]
# compare against the published lens of the same type as the refits (J or R, from the filename)
kind = "r" if "refit_R" in A else "j"
assert ("refit_R" in B) == (kind == "r"), "compare two refits of the same lens type"
PUB = f"/workspace/workspace-lenses/qwen3.5-4b/{kind}-lens/lens.pt"

def stack(path):
    d = torch.load(path, map_location="cpu", weights_only=False); J = d["J"]
    return J.float() if torch.is_tensor(J) else torch.stack([J[k].float() for k in sorted(J)])

a, b, p = stack(A), stack(B), stack(PUB)
cos = lambda x, y: float((x.flatten().double() @ y.flatten().double()) / (x.double().norm() * y.double().norm()))
rows = []
print(f"{'layer':>5}  {'1-cos(A,B)':>11}  {'1-cos(A,pub)':>12}  {'1-cos(B,pub)':>12}  A-B / gap")
for l in range(30):
    ab, ap, bp = 1 - cos(a[l], b[l]), 1 - cos(a[l], p[l]), 1 - cos(b[l], p[l])
    share = ab / max(ap, bp, 1e-12)
    rows.append({"layer": l, "dist_A_B": ab, "dist_A_pub": ap, "dist_B_pub": bp, "env_share": share})
    print(f"{l:5d}  {ab:11.2e}  {ap:12.2e}  {bp:12.2e}  {share:9.3f}")
print(f"\nA-B / gap = distance between the two refits / the larger refit-to-published distance ({kind.upper()} lens)")
out = f"/workspace/gateL/compare_{A.split('/')[-1][:-3]}__vs__{B.split('/')[-1][:-3]}.json"
json.dump({"A": A, "B": B, "published": PUB, "rows": rows}, open(out, "w"), indent=2)
print("saved", out)
