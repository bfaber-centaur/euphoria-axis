---
base_model: Qwen/Qwen3-14B
datasets:
- NeelNanda/pile-10k
license: apache-2.0
tags:
- interpretability
- jacobian-lens
- relp
- qwen3
---

# J-lens and R-lens for Qwen3-14B

A matched pair of **J-lens** (Jacobian lens) and **R-lens** (RelP lens) fits for [`Qwen/Qwen3-14B`](https://huggingface.co/Qwen/Qwen3-14B), prepared for anyone who wants to poke around inside a model.

Try a question or a story. Look across layers and token positions. Compare the J and R readouts. Pin some surprising words, change the prompt, and see what moves. If you find something interesting, please share it!

These are independently fitted artifacts using methods introduced by other researchers. For the techniques and their interpretation, please read the original work:

- **J-lens:** Gurnee et al., [*Verbalizable Representations Form a Global Workspace in Language Models*](https://transformer-circuits.pub/2026/workspace/index.html) ([reference code](https://github.com/anthropics/jacobian-lens)).
- **R-lens:** Camila Blank, Agam Bhatia, and Neel Nanda, [*R-lens: Making J-lens More Faithful on Early Layers*](https://www.lesswrong.com/posts/nv8oedrnLXKRzNEL9/r-lens-making-j-lens-more-faithful-on-early-layers) ([their released J/R lenses](https://huggingface.co/camilablank/workspace-lenses)).
- **RelP:** [*RelP: Faithful and Efficient Circuit Discovery via Relevance Patching*](https://arxiv.org/abs/2508.21258), underlying relevance-propagation method.

## Files

| File | Description | SHA-256 |
| --- | --- | --- |
| `j-lens/lens.pt` | Standard J-lens, first 25 documents | `de591996c307b873c6a9cfa6cf0b277f6b2323edc4459f499dea373d7aed260f` |
| `r-lens/lens.pt` | Matched RelP R-lens, same documents | `0f4895c2a8f0a79707fa9004227ed6097cbcf78382ce52586814ebed0a0e8b11` |
| `j-lens/fit.json` | Fitting settings, environment and file hash | |
| `r-lens/fit.json` | Fitting settings, RelP rules, environment and file hash | |

The `.pt` files are *lens weights*, not a standalone language model. They contain fitted transformations for the specified Qwen3-14B checkpoint.

## Fitting recipe

| Item | Value |
| --- | --- |
| Model | `Qwen/Qwen3-14B` — **not** `Qwen/Qwen3-14B-Base` |
| Checkpoint revision | `40c069824f4251a91eefaf281ebe4c544efd3e18` |
| Corpus | `NeelNanda/pile-10k`, train, documents 0–24 in dataset order |
| Prompt-set SHA-256 | `4111a9cf7ec45fdf11d12a0995eef129b9a2b67d98308f044dd865b1cfd669a7` |
| Number of documents | 25 |
| Target layer | 38 (0-indexed; penultimate transformer block) |
| Source layers | 0–37 |
| `max_seq_len` / `skip_first` | 128 / 4 |
| `force_bos` | `False` |
| `dim_batch` | 16 |
| J-lens fit | Standard `jlens.fit`, code revision `581d398613e5602a5af361e1c34d3a92ea82ba8e` |
| R-lens fit | Same estimator and prompts, RelP-modified backwards pass |
| Compute | NVIDIA A100-SXM4-80GB, PyTorch `2.11.0+cu128`, Transformers `5.19.0` |

For R-lens, the RelP gradient modifications were: LN rule on block input/post-attention RMSNorms, identity rule for SiLU, and half rule with `beta=0.5` on the gated MLP product; Q/K norms were left unchanged. See [the independent fitting implementation](https://github.com/bubskee/euphoria-axis/blob/main/tools/runpod/gateL_fit.py) for the patched-backward mechanics, and the two included `fit.json` files for the settings of these 14B runs.

## Load and explore

Install the [Jacobian-lens reference implementation](https://github.com/anthropics/jacobian-lens), then adapt its [interactive walkthrough](https://github.com/anthropics/jacobian-lens/blob/main/walkthrough.ipynb):

```python
import jlens
import transformers

repo_id = "__HF_REPO_ID__"
model_id = "Qwen/Qwen3-14B"
revision = "40c069824f4251a91eefaf281ebe4c544efd3e18"

hf = transformers.AutoModelForCausalLM.from_pretrained(
    model_id, revision=revision, device_map="auto", dtype="auto"
)
tok = transformers.AutoTokenizer.from_pretrained(model_id, revision=revision)
model = jlens.from_hf(hf, tok, force_bos=False)

j = jlens.JacobianLens.from_pretrained(repo_id, filename="j-lens/lens.pt")
r = jlens.JacobianLens.from_pretrained(repo_id, filename="r-lens/lens.pt")

prompt = "The capital of the country where sushi originated is"
for label, lens in [("J", j), ("R", r)]:
    lens_logits, _model_logits, _ = lens.apply(model, prompt, positions=[-2])
    print(label, {layer: [tok.decode([i]) for i in scores[0].topk(5).indices.tolist()]
                  for layer, scores in lens_logits.items()})
```

You can also inspect the serialized payload directly with `torch.load(path, map_location="cpu", weights_only=False)` after downloading from Hugging Face. Only unpickle files you trust.

## Provenance

These fits were produced as part of the [euphoria-axis research repository](https://github.com/bubskee/euphoria-axis), with fit metadata recorded in [`runs/qwen3-14b-r4/`](https://github.com/bubskee/euphoria-axis/tree/main/runs/qwen3-14b-r4).

The model weights and fitting corpus are **not** redistributed in this repository; only the lens tensors and their provenance are included. Thanks to the original J-lens, R-lens, and RelP authors for developing and releasing these methods.

## License

These independently fitted lens tensors and their accompanying release documentation are offered under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). The underlying [Qwen3-14B model](https://huggingface.co/Qwen/Qwen3-14B/blob/40c069824f4251a91eefaf281ebe4c544efd3e18/LICENSE) is separately distributed by Qwen under Apache-2.0; no original model weights are included here.
