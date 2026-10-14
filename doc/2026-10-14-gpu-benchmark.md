# GPU benchmark for the 27B work (2026-10-14)

Question: which RunPod GPU runs the generalization plan (`doc/plan/generalization-plan.md`)
most cheaply on 27B models.

Method: `tools/runpod/bench_27b.py` times one unit of each planned workload on Qwen3.5-27B
(bf16, fast path verified); `tools/runpod/bench_costs.py` multiplies by the plan's job counts
for the three 27B models and by the console prices of the day. Results files:
`/workspace/bench/bench_*.json` (copy to `runs/bench_27b/`).

## Calibration

On a 4B A40 smoke test, the lens-fit step (B5) read 1.0 min per document at `dim_batch` 16
(peak 18 GiB), matching Gate L's real fits (about 62 s, 18.3 GiB). The benchmark reproduces
an actual fit.

## A100 SXM 80 GB, per unit

| Step | Workload | Result |
|---|---|---|
| B0 | load | 14 s, 50.1 GiB, 64 layers, fast path verified |
| B1 | batched capture (M1, M3-M5) | 63.5 prompts/s (batch 8) |
| B2 | steered greedy generation (M6) | 8.5 s per 120 tokens (14.1 tok/s) |
| B3 | steered button trial (M7) | 0.88 s (347 prompt tokens) |
| B4 | lens readout | 6 ms |
| B5 | one lens-fit document, warm | about 3.8 min (`dim_batch` 8; 16 does not fit) |

## Projected cost, three 27B models (prices 2026-10-14)

| Workload | A100 SXM ($1.79/hr) | H100 NVL ($3.19/hr) |
|---|---|---|
| setup (estimate) | 2.2 h | 2.2 h |
| capture (M1, M3, M4, M5) | 0.1 h | 0.2 h |
| steering generations (M6) | 2.5 h | 9.0 h |
| lens readouts (M6) | 0.2 h | 0.2 h |
| button trials (M7) | 6.0 h | 4.7 h |
| lens fits (3.6 validation R + 3.8 J and R) | 4.7 h | not possible (see below) |
| **total** | **15.7 h, $28** | 16.4 h without fits, $52 |

## Findings

- **Decision: the A100 SXM runs everything.** It is cheapest for every workload.
- **Generation is overhead-bound, not bandwidth-bound:** 14 tok/s on the A100 against about
  37 tok/s that its memory bandwidth allows. Faster GPUs gain little on it; the H100 NVL was
  3.6x slower at generation (likely its pod's CPU side), though 1.3x faster at button trials.
- **Lens fitting cannot run on Hopper with our environment.** `fla` refuses the
  linear-attention backward pass on Hopper with Triton >= 3.4.0 and < 3.7.1, which its
  maintainers found produces incorrect results (fla issue #640). Ampere is unaffected;
  Gate L's fits ran on an A40.
- **CPU quota.** Pods see all host CPUs (128) but are allotted fewer (13.6 on the A100 pod);
  thread pools sized to the host were throttled in 78% of scheduling periods during kernel
  compilation. Setup now sets `OMP_NUM_THREADS`/`MKL_NUM_THREADS` from the quota.
- **Lens fitting is affordable:** about 1.6 h (about $3) per 27B lens on the A100.
- Also fixed along the way: a lock-file bug (`pkg @ file://` lines), the benchmark's warm-up
  shape (B5 now times a cold and a warm document), and autorun's exit-code reporting.

Not included: the 14B work (Gate 2a reproduction, M7, R4 lens pair), roughly half a 27B
model's cost. The setup line is an estimate, to be replaced by the boot timelines.
