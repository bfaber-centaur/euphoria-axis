"""Refresh runs/<run>/paper_protocol/bulky_artifacts_manifest.json.

Bulky = every .npz and every file >= 5 MB under paper_protocol (activation caches
excluded; they are already gitignored). Existing entries are re-hashed: a
mismatch means the local copy differs from what was recorded, and is reported,
never silently overwritten. Run from the repo root after pulling runs/ with rclone.
"""
import hashlib
import json
import sys
from pathlib import Path

P = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/qwen35-4b-posttrained-s2/paper_protocol")
MB5 = 5 * 2**20
mpath = P / "bulky_artifacts_manifest.json"
man = json.loads(mpath.read_text()) if mpath.exists() else {}

def sha(f):
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

verified, added, mismatched, missing = 0, 0, [], []
for rel, e in man.items():
    f = P / rel
    if not f.exists():
        missing.append(rel)
    elif sha(f) != e["sha256"]:
        mismatched.append(rel)
    else:
        verified += 1
for f in sorted(P.rglob("*")):
    if not f.is_file() or f.name.startswith("activations") or f == mpath:
        continue
    rel = str(f.relative_to(P))
    if rel in man:
        continue
    if f.suffix == ".npz" or f.stat().st_size >= MB5:
        man[rel] = {"bytes": f.stat().st_size, "sha256": sha(f),
                    "why_untracked": "lens npz" if f.suffix == ".npz" else ">= 5 MB"}
        added += 1
mpath.write_text(json.dumps(dict(sorted(man.items())), indent=1) + "\n")
print(f"{len(man)} entries | existing verified: {verified} | added: {added}")
if missing:
    print("recorded but not present locally:", missing)
if mismatched:
    print("HASH MISMATCH (local copy differs from the recorded file):", mismatched)
    sys.exit(1)
