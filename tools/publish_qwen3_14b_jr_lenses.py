#!/usr/bin/env python3
"""Verify local Qwen3-14B J/R-lens weights and publish them to Hugging Face.

No large files are copied, converted or serialized: bytes come directly from
<euphoria-axis>/runs/qwen3-14b-r4/*.pt. Model repo upload is opt-in with
--publish. Requires huggingface_hub only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RECORDS = {
    "J": {
        "name": "q14_J_n25_bos0",
        "dest": "j-lens",
        "sha256": "de591996c307b873c6a9cfa6cf0b277f6b2323edc4459f499dea373d7aed260f",
    },
    "R": {
        "name": "q14_R_n25_bos0",
        "dest": "r-lens",
        "sha256": "0f4895c2a8f0a79707fa9004227ed6097cbcf78382ce52586814ebed0a0e8b11",
    },
}
MODEL = "Qwen/Qwen3-14B"
REVISION = "40c069824f4251a91eefaf281ebe4c544efd3e18"
PROMPTS_SHA = "4111a9cf7ec45fdf11d12a0995eef129b9a2b67d98308f044dd865b1cfd669a7"
JLENS_COMMIT = "581d398613e5602a5af361e1c34d3a92ea82ba8e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def locate(repo: Path, record: dict) -> tuple[Path, Path]:
    runs = repo / "runs" / "qwen3-14b-r4"
    meta_path = runs / f"{record['name']}.json"
    if not meta_path.is_file():
        raise FileNotFoundError(f"Missing fitted-run metadata: {meta_path}")
    meta = json.loads(meta_path.read_text())
    assert meta.get("lens_sha256") == record["sha256"], f"SHA mismatch in {meta_path}"
    assert meta.get("env", {}).get("model") == MODEL, meta_path
    assert meta["env"]["revision"] == REVISION, meta_path
    assert meta["env"]["jlens_commit"] == JLENS_COMMIT, meta_path
    assert meta.get("prompts_sha256") == PROMPTS_SHA, meta_path
    assert meta.get("force_bos") is False, meta_path
    assert all(meta["recipe"].get(k) == v for k, v in {
        "n_docs": 25, "doc_offset": 0, "max_seq_len": 128,
        "skip_first": 4, "target_layer": 38, "dim_batch": 16,
    }.items()), meta_path
    assert meta.get("mode") == record["name"].split("_")[1], meta_path

    # Standard location is adjacent to fit JSON. Fall back to identifying a
    # differently named tensor by SHA-256 in this 14B run directory only.
    named = runs / f"{record['name']}.pt"
    candidates = ([named] if named.is_file() else []) + sorted(
        p for p in runs.rglob("*.pt") if p != named and p.is_file()
    )
    for candidate in candidates:
        if sha256(candidate) == record["sha256"]:
            return candidate, meta_path
    raise FileNotFoundError(
        f"No .pt file under {runs} matches {record['name']} "
        f"(sha256 {record['sha256']}); sync that file from RunPod first."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(),
                        help="Local checkout of euphoria-axis (default: current directory)")
    parser.add_argument("--repo-id", help="Hugging Face namespace/repo; default: <logged-in-user>/qwen3-14b-jr-lenses")
    parser.add_argument("--publish", action="store_true", help="Actually upload verified files; omitted = dry run")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    card_file = Path(__file__).resolve().parents[1] / "releases/qwen3-14b-jr-lenses/README.md"
    if not card_file.is_file():
        parser.error(f"Missing release model card: {card_file}")
    card = card_file.read_text()
    if not card.startswith("---\n") or "license: apache-2.0" not in card or "# J-lens and R-lens for Qwen3-14B" not in card:
        parser.error(f"Unexpected release model card contents: {card_file}")

    files = []
    for label, record in RECORDS.items():
        source, metadata = locate(repo_root, record)
        print(f"{label}: verified {source} ({source.stat().st_size / 2**30:.2f} GiB)", flush=True)
        files.append((source, f"{record['dest']}/lens.pt"))
        files.append((metadata, f"{record['dest']}/fit.json"))

    if not args.publish:
        print("\nDry run complete. No files uploaded.")
        print("To publish, run this command again with --publish.")
        return 0

    try:
        from huggingface_hub import HfApi
    except ImportError as e:
        raise SystemExit("Install: python3 -m pip install -U huggingface_hub") from e

    api = HfApi()
    try:
        account = api.whoami()["name"]
    except Exception as e:
        raise SystemExit("Not authenticated: run hf auth login first.") from e

    repo_id = args.repo_id or f"{account}/qwen3-14b-jr-lenses"
    if "/" not in repo_id:
        parser.error("--repo-id must be of form namespace/repository")
    print(f"\nPublishing as {account} to https://huggingface.co/{repo_id}", flush=True)
    api.create_repo(repo_id=repo_id, repo_type="model", private=False, exist_ok=True)

    # Upload from original run paths: no extra GB-scale local copy required.
    for local, remote in files:
        print(f"Uploading {remote} ...", flush=True)
        api.upload_file(path_or_fileobj=str(local), path_in_repo=remote,
                        repo_id=repo_id, repo_type="model",
                        commit_message=f"Publish {remote}")

    readme = card_file.read_text().replace("__HF_REPO_ID__", repo_id)
    api.upload_file(path_or_fileobj=readme.encode("utf-8"),
                    path_in_repo="README.md", repo_id=repo_id,
                    repo_type="model", commit_message="Add J/R-lens model card")

    info = api.repo_info(repo_id=repo_id, repo_type="model", files_metadata=True)
    remote_paths = {entry.rfilename for entry in info.siblings}
    missing = {path for _, path in files} | {"README.md"}
    missing -= remote_paths
    if missing:
        raise RuntimeError(f"Upload finished but files missing in repo listing: {sorted(missing)}")
    print(f"\nPublished: https://huggingface.co/{repo_id}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, FileNotFoundError, ValueError) as exc:
        sys.exit(f"Verification failed: {exc}")
