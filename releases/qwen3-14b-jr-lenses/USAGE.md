# Publishing the Qwen3-14B J/R lens pair

The release card lives in [README.md](README.md); the upload tool is [tools/publish_qwen3_14b_jr_lenses.py](../../tools/publish_qwen3_14b_jr_lenses.py).

The J/R lens tensors themselves are **not** committed to GitHub. The publisher reads the two existing .pt files from your *local* euphoria-axis clone, checks their SHA-256 hashes against the recorded fit metadata, and uploads them directly to a public Hugging Face **model** repository. RunPod storage is the backup if either local file is missing.

## On the Mac, from the root of the local checkout

1. Install and log in:

   ```bash
   python3 -m pip install -U huggingface_hub
   hf auth login
   ```

2. Verify that both the binary fits and the recorded JSONs are present and match:

   ```bash
   python3 tools/publish_qwen3_14b_jr_lenses.py
   ```

3. Review [the model card](README.md), including its proposed **MIT** license, then publish:

   ```bash
   python3 tools/publish_qwen3_14b_jr_lenses.py --publish
   ```

The default destination is `<logged-in-HF-user>/qwen3-14b-jr-lenses`. For an organization or different slug, add `--repo-id NAMESPACE/REPO`.

The publisher uploads the primary matched J/R pair, the corresponding JSON fit records, and the model card. It intentionally **does not** upload the third R fit on documents 25–49; that can be a later separate release if desired.

If a binary is missing, sync it from RunPod storage to `runs/qwen3-14b-r4/`. Expected names are `q14_J_n25_bos0.pt` and `q14_R_n25_bos0.pt`, but other names within that directory are accepted if the byte-level SHA-256 matches the fit records.
