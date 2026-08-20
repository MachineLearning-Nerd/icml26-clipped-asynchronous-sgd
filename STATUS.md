# Reproduction status

Repository: [MachineLearning-Nerd/icml26-clipped-asynchronous-sgd](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd)

Paper: [Clipping Makes Distributed and Federated Asynchronous SGD Robust to Stragglers](https://arxiv.org/abs/2606.13287), arXiv:2606.13287.

Overall status:

`PARTIAL_C1_C2_VERIFIED_C3_NOVELTY_FALSIFIED_RATE_BLOCKED_C4_BLOCKED_C5_FALSIFIED_VANILLA_COMPARATOR_C6_BLOCKED_HISTORICAL_SCORE_4_OF_12_NO_CURRENT_SCORE`

| Claim | Status | Confidence and boundary |
| --- | --- | --- |
| C1 — homogeneous expectation-rate complexity | `VERIFIED_SCOPED_MEDIUM` | The expectation-rate proof DAG and controls pass; it is a finite symbolic certificate, not a Lean/Coq proof-kernel artifact. |
| C2 — heterogeneous expectation-rate complexity | `VERIFIED_SCOPED_MEDIUM` | The same DAG retains heterogeneity and specializes to C1 at `zeta=0`; uniform scheduling and conditional-unbiasedness assumptions are explicit. |
| C3 — first high-probability asynchronous result and theta-rate | `FALSIFIED_COMPOUND_NOVELTY_BLOCKED_NARROW_RATE` | Cohen et al. (NeurIPS 2021) falsifies the unrestricted novelty conjunct; the narrower theta-dependent rate remains blocked after a repaired Freedman route exposes an extra delta-dependent term. |
| C4 — Figure 1 tail estimate `theta=2.71` | `BLOCKED_HISTORICAL_PROTOCOL` | Initialized and trained reconstructions estimate `0.0789` and `0.2246`; all admissible trained-route tail fractions peak at `0.2345`, but the source checkpoint and gradient protocol are unidentified. |
| C5 — Figures 2–3 speedup range | `FALSIFIED_SCOPED_VANILLA_COMPARATOR_MEDIUM` | Under the carried Vanilla-ASGD comparator, Shakespeare D4 is `1.8×`, below the imported `2.0–2.2×` range; Delay-adaptive ASGD gives a different reading and is recorded. |
| C6 — Figure 4 label-skew speedups | `BLOCKED_HISTORICAL_PROTOCOL_RECONSTRUCTION` | Complete D4/D8 grids and three-seed reconstructions do not identify the authors’ exact historical realization; D4 is `1.0227×` with interval `[0.9283, 1.1207]`, and D8 has a censored clipped seed. |

Historical result: `4/12` live judged score. The release forecast is `6–9/12`, with `9/12` as the best-supported possible value; neither is a judge result. `current_score_claim=false`, `publication_allowed=false`, and `official_author_endorsement=false`.

Run the lightweight repository/provenance audit with:

```bash
python3 verify_final.py
```

The original cumulative scientific verifier is [`hf_space_release/reproduction/run.py`](hf_space_release/reproduction/run.py), invoked with `uv run --frozen python -m reproduction.run`. No full scientific rerun is implied by this documentation update.

Recovery bundle before attribution normalization: `/tmp/icml-clipped-asgd-before-normalization.Z1ecjH/icml-clipped-asgd-before-normalization.bundle` (SHA-256 `43069151203dbeda44d85db05fdf42075d09bcdf0cf9acbba5db77deae247a62`).
