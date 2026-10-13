# =====================================================================
# Gate L, chunk L0 -- INSPECT the published Qwen3.5-4B J/R lens pair.
#   1. pin the working directory (server data folder)
#   2. lens repos still at the commits recorded in setup_spec.json, trees clean?
#   3. sha256 of both lens files (canonical lens IDs from here on)
#   4. print each lens's stored provenance (recipe, prompts, config_json)
#   5. matrix sanity: shapes, anchor row == I, J-vs-R per-layer similarity
#      (the J/R gap is the yardstick for how tight the L1 refit bar can be)
#   6. jlens.fit signature, and whether pile-10k is available locally
# CPU only, nothing fitted.  Writes lens_calibration/l0_published_lens_provenance.json
# =====================================================================
import os
from pathlib import Path
os.chdir("/mnt/c/Users/bfabe/workspace/euphoria-axis")
assert Path("runs/qwen35-4b-posttrained-s2/paper_protocol").is_dir(), Path.cwd()

import hashlib
import inspect
import json
import subprocess
import sys

import numpy as np
import torch

paper_run_dir = Path("runs/qwen35-4b-posttrained-s2/paper_protocol")
cal_dir = paper_run_dir / "lens_calibration"
cal_dir.mkdir(parents=True, exist_ok=True)
setup = json.loads((paper_run_dir / "lens_readout" / "setup_spec.json").read_text())

def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()

# ---------------------------------------------------------------------
# 2. repos vs the commits recorded when the lens readouts were made
# ---------------------------------------------------------------------
repos = {"jacobian-lens": (Path(setup["jacobian_lens_repo"]), setup["jacobian_lens_commit"]),
         "workspace-lenses": (Path(setup["workspace_lenses_repo"]), setup["workspace_lenses_commit"])}
repo_state = {}
for name, (path, recorded) in repos.items():
    head = git(path, "rev-parse", "HEAD")
    dirty = git(path, "status", "--porcelain", "--untracked-files=no")
    repo_state[name] = {"path": str(path), "recorded": recorded, "head": head, "matches": head == recorded,
                        "clean": dirty == ""}
    print(f"{name:17s} HEAD {head[:12]}  recorded {recorded[:12]}  "
          f"{'MATCH' if head == recorded else 'DIFFERENT'}  {'clean' if not dirty else 'MODIFIED FILES:'}")
    if dirty:
        print(dirty)

# ---------------------------------------------------------------------
# 3-4. lens files: hash, keys, provenance
# ---------------------------------------------------------------------
lens_dir4b = Path(setup["workspace_lenses_repo"]) / "qwen3.5-4b"
print("\nqwen3.5-4b/ contents:", sorted(str(p.relative_to(lens_dir4b)) for p in lens_dir4b.rglob("*") if p.is_file()))
raw, info = {}, {}
for name in ["J", "R"]:
    p = Path(setup["lens_files"][name])
    raw[name] = torch.load(p, map_location="cpu", weights_only=False)
    d = raw[name]
    prov = d.get("provenance", {}) if isinstance(d, dict) else {}
    cfg = prov.get("config_json")
    if isinstance(cfg, str):
        try:
            cfg = json.loads(cfg)
        except json.JSONDecodeError:
            pass
    info[name] = {"path": str(p), "bytes": p.stat().st_size, "sha256": sha256(p),
                  "keys": sorted(d.keys()) if isinstance(d, dict) else str(type(d)),
                  "n_prompts": d.get("n_prompts") if isinstance(d, dict) else None,
                  "d_model": d.get("d_model") if isinstance(d, dict) else None,
                  "source_layers": list(d.get("source_layers", [])) if isinstance(d, dict) else None,
                  "provenance": {k: v for k, v in prov.items() if k != "config_json"}, "config": cfg}
    print(f"\n===== {name} lens =====")
    print(f"sha256 {info[name]['sha256']}  ({info[name]['bytes'] / 2**20:.1f} MiB)")
    print("keys:", info[name]["keys"], "| n_prompts:", info[name]["n_prompts"], "| d_model:", info[name]["d_model"])
    print("provenance:", json.dumps(info[name]["provenance"], indent=1, default=str)[:2500])
    print("config_json:", json.dumps(cfg, indent=1, default=str)[:4000] if cfg is not None else "(none)")

# ---------------------------------------------------------------------
# 5. matrix sanity and the J-vs-R gap
# ---------------------------------------------------------------------
def stack(d):
    J = d["J"]
    return J.float() if torch.is_tensor(J) else torch.stack([J[k].float() for k in sorted(J)])
JJ, RR = stack(raw["J"]), stack(raw["R"])
print(f"\nJ stack {tuple(JJ.shape)} {raw['J']['J'].dtype if torch.is_tensor(raw['J']['J']) else 'dict'} | "
      f"R stack {tuple(RR.shape)}")
eye = torch.eye(JJ.shape[-1])
print("last row == I  (J, R):", bool(torch.allclose(JJ[-1], eye, atol=1e-3)), bool(torch.allclose(RR[-1], eye, atol=1e-3)))
rows = []
for i in range(JJ.shape[0]):
    a, b = JJ[i].flatten().double(), RR[i].flatten().double()
    rows.append({"row": i, "J_fro": float(a.norm()), "R_fro": float(b.norm()),
                 "cos_J_R": float(a @ b / (a.norm() * b.norm()))})
print("per-layer Frobenius cosine J vs R (row: cos):",
      " ".join(f"{r['row']}:{r['cos_J_R']:.3f}" for r in rows))

# ---------------------------------------------------------------------
# 6. fitting entry point and data availability
# ---------------------------------------------------------------------
sys.path.insert(0, setup["jacobian_lens_repo"])
import jlens
print("\njlens.fit", inspect.signature(jlens.fit))
print((inspect.getdoc(jlens.fit) or "")[:1500])
pile = None
try:
    from datasets import load_dataset
    pile = load_dataset("NeelNanda/pile-10k", split="train", download_mode="reuse_cache_if_exists")
    print(f"\npile-10k available: {len(pile)} docs; first doc starts {pile[0]['text'][:80]!r}")
except Exception as e:
    print(f"\npile-10k NOT available locally/online here: {type(e).__name__}: {str(e)[:200]}")

(cal_dir / "l0_published_lens_provenance.json").write_text(json.dumps(
    {"repos": repo_state, "lenses": {k: {kk: vv for kk, vv in v.items() if kk != "source_layers"} | {"source_layers": v["source_layers"]}
                                     for k, v in info.items()},
     "J_vs_R_per_layer": rows, "pile10k_available": pile is not None}, indent=2, default=str) + "\n")
print("\nsaved:", cal_dir / "l0_published_lens_provenance.json")
