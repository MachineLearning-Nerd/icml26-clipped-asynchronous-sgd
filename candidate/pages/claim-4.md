# Claim 4 — CIFAR-10 ResNet-18 gradient-noise pilot

**Current verdict: BLOCKED.** This is real CIFAR-10/ResNet-18 evidence, but not
an assumption-identical reproduction of Figure 1 because the paper omits its
checkpoint, batch size, preprocessing, sample count, reference gradient, and
tail fraction.

Paper result: `theta = 2.71`. Pilot result: `theta_hat = 0.0789191`, bootstrap
95% interval `[0.0121327, 0.0885472]`, using `n=24` stochastic gradient-error
norms and `k=8` upper order statistics. The interval excludes `2.71`, but this
does **not** falsify the paper because the pilot uses an initialization
checkpoint and an approximate reference gradient.

| Item | Evaluator-visible evidence |
|---|---|
| Exact statement | [Machine-readable claim contract](../../.openresearch/artifacts/claim4/claim_contract.json) |
| Assumptions/protocol audit | [Source audit](../../.openresearch/artifacts/claim4/source_audit.md) |
| Code | [Experiment implementation](../../reproduction/claims/claim4.py) |
| Fixed command | `uv run --frozen python -m reproduction.run` |
| Raw data | [Download raw JSON](../../.openresearch/artifacts/claim4/raw_output.json) |
| Independent checker | [Code](../../.openresearch/artifacts/claim4/independent_check.py) and [output](../../.openresearch/artifacts/claim4/checker_output.json); recomputed `0.07891913452514845`, PASS |
| Control | [Output](../../.openresearch/artifacts/claim4/negative_control.json): known theta `0.5/1/2.71` recovered as `0.494/1.014/2.812` |
| Negative control | Reciprocal-convention value `0.35565` rejected as intended |
| Runtime/CPU | [Run metadata](../../.openresearch/artifacts/claim4/run_metadata.json): HF cpu-upgrade, 8-vCPU quota, no GPU, 2,061.783 s runner |
| Limitations | [Limitations and deviations](../../.openresearch/artifacts/claim4/limitations.md): initialization checkpoint, 2,048-example reference, `n=24` |

Tail-fraction sensitivity:

| k | theta | R² |
|---:|---:|---:|
| 6 | 0.06342 | 0.6687 |
| 8 | 0.07892 | 0.8237 |
| 10 | 0.07198 | 0.8574 |
| 12 | 0.06360 | 0.8584 |

The source run emitted a complete runner `PASS` and independent checker `PASS`,
but the backend recorded `failed: timeout` just after the payload. This status
is preserved rather than normalized away.
