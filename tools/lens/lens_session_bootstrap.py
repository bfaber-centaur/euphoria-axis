# =====================================================================
# Lens-session bootstrap: the bindings the Gate L readout bar needs, and nothing else.
# Generated from notebooks/03-decursed.ipynb (verbatim code, decorators included):
#   cell 8  in full: model, tokenizer, lens_model, published j_lens / r_lens, vectors, paper_spec, decoder_layers
#   cell 9  only: imports, probe_terms construction, prefix_steering  (NOT the one-prompt smoke run)
#   cell 10 only: imports, all_layers, capture_all_layers, lens_readout, ranks_for_tokens  (NOT the 50-prompt sweep,
#           which would overwrite the frozen lens_readout CSVs)
# =====================================================================
import os
from pathlib import Path
os.chdir("/mnt/c/Users/bfabe/workspace/euphoria-axis")
assert Path("runs/qwen35-4b-posttrained-s2/paper_protocol").is_dir(), Path.cwd()


# ---- cell 8 (verbatim) ----
# Local-only R/J lens setup.
#
# Expected sibling layout:
#
#   euphoria-axis/
#   jacobian-lens/
#   workspace-lenses/
#
# No network access required for lens code or lens weights.

from pathlib import Path
import subprocess
import sys
import json

import torch
import transformers


# ---------------------------------------------------------------------
# Locate local repos
# ---------------------------------------------------------------------

HERE = Path.cwd().resolve()

def find_sibling(name):
    candidates = [
        HERE / name,
        HERE.parent / name,
        HERE.parent.parent / name,
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    raise FileNotFoundError(
        f"Could not find {name!r}. Tried:\n"
        + "\n".join(f"  {p}" for p in candidates)
    )

JLENS_REPO = find_sibling("jacobian-lens")
WORKSPACE_LENSES_REPO = find_sibling("workspace-lenses")

print("jacobian-lens:   ", JLENS_REPO)
print("workspace-lenses:", WORKSPACE_LENSES_REPO)


# Import the local jlens checkout directly.
sys.path.insert(0, str(JLENS_REPO))

import jlens


def git_head(path):
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
    ).strip()


jlens_commit = git_head(JLENS_REPO)
workspace_lenses_commit = git_head(WORKSPACE_LENSES_REPO)

print("jlens commit:           ", jlens_commit)
print("workspace-lenses commit:", workspace_lenses_commit)


# ---------------------------------------------------------------------
# Frozen euphoria-axis experiment state
# ---------------------------------------------------------------------

MODEL_NAME = "Qwen/Qwen3.5-4B"

paper_run_dir = Path(
    "runs/qwen35-4b-posttrained-s2/paper_protocol"
)
s1_dir = paper_run_dir / "s1_comparison"
lens_dir = paper_run_dir / "lens_readout"
lens_dir.mkdir(parents=True, exist_ok=True)

paper_spec = json.loads(
    (paper_run_dir / "spec.json").read_text()
)

assert paper_spec["model"] == MODEL_NAME
assert paper_spec["injection_block"] == 16
assert paper_spec["prompt_format"] == "plain text; no chat template"


# ---------------------------------------------------------------------
# Local lens files
# ---------------------------------------------------------------------

J_PATH = (
    WORKSPACE_LENSES_REPO
    / "qwen3.5-4b"
    / "j-lens"
    / "lens.pt"
)

R_PATH = (
    WORKSPACE_LENSES_REPO
    / "qwen3.5-4b"
    / "r-lens"
    / "lens.pt"
)

assert J_PATH.exists(), J_PATH
assert R_PATH.exists(), R_PATH

print("J lens:", J_PATH)
print("R lens:", R_PATH)


# ---------------------------------------------------------------------
# Load model from the existing HF cache
# ---------------------------------------------------------------------

hf = transformers.AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    local_files_only=True,
).cuda().eval()

tok = transformers.AutoTokenizer.from_pretrained(
    MODEL_NAME,
    local_files_only=True,
)

# Preserve our existing plain-text protocol.
# jlens otherwise defaults to force_bos=True.
lens_model = jlens.from_hf(
    hf,
    tok,
    force_bos=False,
)


# ---------------------------------------------------------------------
# Load local J/R lenses
# ---------------------------------------------------------------------

j_lens = jlens.JacobianLens.load(str(J_PATH))
r_lens = jlens.JacobianLens.load(str(R_PATH))

assert j_lens.source_layers == r_lens.source_layers
assert j_lens.source_layers == list(range(31))
assert j_lens.d_model == r_lens.d_model
assert j_lens.d_model == hf.config.hidden_size

print(j_lens)
print(r_lens)


# ---------------------------------------------------------------------
# Frozen steering vectors
# ---------------------------------------------------------------------

paper_vectors = torch.load(
    paper_run_dir / "steering_vectors.pt",
    map_location="cpu",
    weights_only=True,
)

s1_blob = torch.load(
    s1_dir / "s1_direction_block30.pt",
    map_location="cpu",
    weights_only=True,
)

s2_vector = paper_vectors["S2"].float()
s1_vector = s1_blob["matched_vector"].float()

assert torch.isfinite(s1_vector).all()
assert torch.isfinite(s2_vector).all()

print("S2 norm:", s2_vector.norm().item())
print("S1 norm:", s1_vector.norm().item())

assert torch.allclose(
    s1_vector.norm(),
    s2_vector.norm(),
    atol=1e-4,
)

decoder_layers = list(lens_model.layers)
assert len(decoder_layers) == 32


# ---------------------------------------------------------------------
# Freeze lens-readout provenance
# ---------------------------------------------------------------------

setup_spec = {
    "model": MODEL_NAME,
    "jacobian_lens_repo": str(JLENS_REPO),
    "jacobian_lens_commit": jlens_commit,
    "workspace_lenses_repo": str(WORKSPACE_LENSES_REPO),
    "workspace_lenses_commit": workspace_lenses_commit,
    "lens_files": {
        "J": str(J_PATH),
        "R": str(R_PATH),
    },
    "lens_source_layers": j_lens.source_layers,
    "lens_target_layer": 30,
    "prompt_format": "plain text; no chat template",
    "force_bos": False,
    "measurement_position": "final prefix token",
    "injection_block": paper_spec["injection_block"],
    "initial_conditions": [
        {
            "name": "baseline",
            "direction": None,
            "coeff": 0.0,
        },
        {
            "name": "S1_-0.5",
            "direction": "S1_matched",
            "coeff": -0.5,
        },
        {
            "name": "S2_-0.5",
            "direction": "S2",
            "coeff": -0.5,
        },
    ],
}

setup_path = lens_dir / "setup_spec.json"
setup_text = json.dumps(setup_spec, indent=2) + "\n"

if setup_path.exists():
    old = json.loads(setup_path.read_text())

    # Don't silently mutate an already-frozen setup.
    assert old == setup_spec, (
        f"{setup_path} already exists with different provenance."
    )
else:
    setup_path.write_text(setup_text)

print("\nReady.")
print("Saved provenance:", setup_path)

# ---- cell 9 (definitions only) ----
from contextlib import contextmanager

import pandas as pd

import torch

from jlens.hooks import ActivationRecorder

psych_spec = json.loads(
    (s1_dir / "psych_vocab_v1.json").read_text()
)

psych_vocab = psych_spec["families"]

probe_terms = []

for family, terms in psych_vocab.items():
    for term in terms:
        # At "I feel:" the natural continuation form normally begins
        # with a space. Keep only probes represented by one token.
        ids = tok.encode(" " + term, add_special_tokens=False)

        if len(ids) == 1:
            probe_terms.append({
                "family": family,
                "term": term,
                "token_id": ids[0],
                "decoded": tok.decode([ids[0]]),
            })

probe_terms = pd.DataFrame(probe_terms)

@contextmanager
def prefix_steering(coeff, vector):
    if vector is None or coeff == 0:
        yield
        return

    model_device = next(hf.parameters()).device
    delta = vector.to(
        device=model_device,
        dtype=torch.bfloat16,
    )

    def hook(module, inputs, output):
        if isinstance(output, tuple):
            return (
                output[0] + coeff * delta,
                *output[1:],
            )
        return output + coeff * delta

    handle = decoder_layers[
        paper_spec["injection_block"]
    ].register_forward_hook(hook)

    try:
        yield
    finally:
        handle.remove()

# ---- cell 10 (definitions only) ----
import time

import pandas as pd

import torch

from jlens.hooks import ActivationRecorder

all_layers = list(j_lens.source_layers)

assert all_layers == list(range(31))

@torch.no_grad()
def capture_all_layers(text, coeff=0.0, vector=None):
    ids = lens_model.encode(text)

    with prefix_steering(coeff, vector):
        with ActivationRecorder(
            lens_model.layers,
            at=all_layers,
        ) as recorder:
            lens_model.forward(ids)

    states = {
        layer: (
            recorder.activations[layer][0, -1, :]
            .detach()
            .float()
        )
        for layer in all_layers
    }

    return ids.cpu(), states

def lens_readout(lens, state, layer):
    transported = lens.transport(state, layer)

    return (
        lens_model
        .unembed(transported)
        .float()
        .cpu()
    )

def ranks_for_tokens(logits, token_ids):
    """
    Compute 1-indexed ranks for a small token set without sorting
    the entire vocabulary once per token.
    """
    targets = logits[token_ids]

    # [n_probe, vocab]
    return (
        (logits.unsqueeze(0) > targets.unsqueeze(1))
        .sum(dim=1)
        .add(1)
        .tolist()
    )

# ---- frozen vocabulary under the name the readout cell checks for ----
PSYCH_VOCAB = psych_vocab
for _n in ["capture_all_layers", "lens_readout", "ranks_for_tokens", "j_lens", "r_lens", "probe_terms", "PSYCH_VOCAB", "jlens"]:
    assert _n in globals(), _n
print("lens session ready:", len(probe_terms), "probe terms | J/R lenses loaded | helpers defined")
