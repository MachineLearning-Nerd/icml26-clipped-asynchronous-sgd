# ICML 2026 — Clipped Asynchronous SGD

[![Open in Molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/blob/main/notebooks/clipped_asgd_reproduction.py)

Independent claim-by-claim reproduction audit for [arXiv:2606.13287](https://arxiv.org/abs/2606.13287), *Clipping Makes Distributed and Federated Asynchronous SGD Robust to Stragglers*.

The repository was renamed from `icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle` to `icml26-clipped-asynchronous-sgd` so the public URL describes the method and paper rather than the challenge identifier.

## Audit status

`PARTIAL_C1_C2_VERIFIED_C3_NOVELTY_FALSIFIED_RATE_BLOCKED_C4_BLOCKED_C5_FALSIFIED_VANILLA_COMPARATOR_C6_BLOCKED_HISTORICAL_SCORE_4_OF_12_NO_CURRENT_SCORE`

Claims 1–2 pass the finite symbolic expectation-rate certificate. Claim 3 is compound: its broad “first high-probability asynchronous result” novelty clause is falsified by a primary 2021 result, while its narrower theta-dependent rate remains blocked. Claim 5 is falsified under the carried Vanilla-ASGD comparator, with comparator ambiguity recorded. Claims 4 and 6 remain blocked because the authors’ historical checkpoints, raw curves, and omitted protocol fields are unavailable. The historical 4/12 judge result is preserved; the 6–9/12 values are forecasts only. There is no current judge score claim or author endorsement claim.

The maintained dossier is [`STATUS.md`](STATUS.md), with claim production paths in [`CLAIM_EVIDENCE.md`](CLAIM_EVIDENCE.md), source pins in [`SOURCE_AUDIT.md`](SOURCE_AUDIT.md), environment details in [`ENVIRONMENT.md`](ENVIRONMENT.md), and a machine-checkable final audit in [`verify_final.py`](verify_final.py).

## What the paper does

The paper studies asynchronous stochastic gradient descent under delayed updates and heavy-tailed gradient noise. It argues that gradient clipping removes maximum-delay dependence from oracle-complexity bounds, develops expectation and high-probability convergence results under a sub-Weibull noise model, and evaluates the method on CIFAR-10 and Shakespeare workloads.

## Claim and evidence ledger

The evidence package does not collapse theorem checks, source audits, and unavailable historical experiments into one result. Each claim below has an explicit contract and boundary.

| Claim | Paper anchor / imported statement | How the claim is produced and checked | Current assessment |
|---|---|---|---|
| 1 | Theorem 4.2 — homogeneous oracle complexity independent of `tau_max` | The 11-node expectation-theorem DAG reconstructs the clipped-bias, virtual-iterate, descent, telescoping, norm-conversion, parameter, and complexity-inversion steps; controls inject `tau_max`, alter an epsilon exponent, or delete a dependency | `VERIFIED`; finite symbolic certificate, not a Lean/Coq proof-kernel object |
| 2 | Theorem 5.1 — heterogeneous oracle complexity independent of `tau_max` | The same DAG retains `zeta` through clipping bias, second-moment, large-gradient, and complexity terms, then recovers Claim 1 at `zeta=0` | `VERIFIED`; uniform scheduling and conditional-unbiasedness assumptions are explicit |
| 3 | “First high-probability asynchronous optimization result” plus the narrower theta-dependent rate | [`claim3_route3`](hf_space_release/evidence/claim3_route3) compares the novelty clause with Cohen et al. (NeurIPS 2021) and checks independent-restart amplification; Routes 1–2 audit and repair the narrower Freedman derivation | `FALSIFIED` as a compound claim because the broad novelty clause predates this paper; the narrower theta-dependent rate remains `BLOCKED`, not falsely promoted |
| 4 | Figure 1 — historical ResNet-18/CIFAR-10 gradient-noise fit `theta=2.71` | Four routes test initialized and trained ResNet-18s, tail-count choices, estimator calibration, dataset identity, and mandatory controls | `BLOCKED`; observed theta values are far below 2.71, but the historical checkpoint, raw norms, reference-gradient protocol, preprocessing, sample count, and tail count are unidentified |
| 5 | Figures 2–3 — reported CIFAR/ Shakespeare speedup ranges | [`claim5_source_audit`](hf_space_release/evidence/claim5_source_audit) pins the paper source and compares the exact named Vanilla-ASGD comparator against the prose values | `FALSIFIED`, medium confidence under the carried Vanilla-ASGD comparator: Shakespeare D4 is 1.8× in the source, not the imported at-least-2.0× range; changing to Delay-adaptive ASGD changes the interpretation |
| 6 | Figure 4 — label-skew CIFAR-10 speedups at `D=4` and `D=8` | Complete D4/D8 selection grids and fresh three-seed validation are checked with fixed worker, queue, cadence, aggregation, and censoring diagnostics | `BLOCKED`; D4 paired speedup is 1.0227 with 95% interval [0.9283, 1.1207], and D8 has a censored clipped seed; the exact historical CNN/protocol/seeds remain unavailable |

### Common evidence path

Every claim follows this chain:

`paper/source anchor → exact contract → executable verifier or source audit → positive/negative controls → raw evidence → cumulative release verifier → report`

Run the cumulative audit with:

```bash
uv run --frozen python -m reproduction.run
```

The evaluator-facing contracts, methods, raw outputs, controls, and limitations are under [`hf_space_release`](hf_space_release). The illustrated synthesis is [`reports/clipping-asgd/report.md`](reports/clipping-asgd/report.md).

## Key evidence

| Result | Recorded evidence |
|---|---|
| Claims 1–2 | Expectation-rate DAG passes 17/17 release verifiers; no `tau_max` term appears in the derived complexities |
| Claim 3 | Cohen et al., *Asynchronous Stochastic Optimization Robust to Arbitrary Delays* (NeurIPS 2021), supplies a prior high-probability asynchronous result with logarithmic independent restarts |
| Claim 4 | Initialized theta 0.0789, trained theta 0.2246, and exhaustive admissible tail counts max 0.2345; these are diagnostics, not a valid historical falsification without source artifacts |
| Claim 5 | Source audit: CIFAR D4 Vanilla 1.8×, Shakespeare D4 Vanilla 1.8×, Shakespeare D8 Vanilla 2.0×; the imported coordinated range is not supported under that comparator |
| Claim 6 | Selection sweep: D4 1.2353× and D8 1.0882×; independent D4 validation 1.0227× with interval [0.9283, 1.1207]; D8 validation censored |

The previous live judged score recorded by the repository is `4/12`. The `6–9/12` range is a forecast, not a new judge result. Full historical reproduction of Claims 4 and 6 requires the missing author checkpoint, code, raw gradients/curves, and protocol fields.

## Reproduce locally

Dependencies are pinned by [`pyproject.toml`](pyproject.toml) and [`uv.lock`](uv.lock). No GPU is required for the documented proof and source-audit paths.

```bash
uv sync --frozen
uv run --frozen python -m reproduction.run
marimo edit notebooks/clipped_asgd_reproduction.py
```

Long or uncertain CIFAR routes used Hugging Face `cpu-upgrade`; the evidence records CPU allocation, seed, runtime, and censoring explicitly.

## Branch map

The live branch names describe their evidence role:

| Branch family | Purpose |
|---|---|
| [`historical/judged-baseline`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/historical/judged-baseline) | Preserve the frozen 4/12 baseline and provenance harness |
| [`audit/c1-c2-expectation-rates`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c1-c2-expectation-rates) | Constructive expectation-theorem DAG for Claims 1–2 |
| [`audit/c3-published-proof`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c3-published-proof) | Audit the printed high-probability proof |
| [`audit/c3-repaired-freedman`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c3-repaired-freedman) | Repair and delimit the narrower Freedman rate |
| [`audit/c3-prior-art`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c3-prior-art) | Primary-source novelty falsification |
| [`audit/c4-cifar-resnet`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c4-cifar-resnet) | Real CIFAR-10/ResNet-18 gradient-noise audit |
| [`audit/c4-source-identifiability`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c4-source-identifiability) | Mandatory historical-protocol identifiability route |
| [`audit/c4-pilot`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c4-pilot) | Committed Claim 4 pilot evidence |
| [`audit/c4-dataset-checksum`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c4-dataset-checksum) | Dataset checksum and route-2 provenance |
| [`audit/c4-trained-resnet`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c4-trained-resnet) | Trained ResNet-18 checkpoint route |
| [`historical/c4-falsification-route`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/historical/c4-falsification-route) | Retain the rejected checkpoint/estimator falsification route |
| [`audit/c5-comparator-source`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c5-comparator-source) | Exact source and comparator audit |
| [`audit/c6-cifar-pilot`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-cifar-pilot) | Classic two-convolution-CNN pilot |
| [`audit/c6-cnn-protocol`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-cnn-protocol) | CNN protocol calibration |
| [`audit/c6-d4-sweep`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-d4-sweep) | Complete D4 hyperparameter sweep |
| [`audit/c6-d4-worker-init`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-d4-worker-init) | One-time worker-initialization control |
| [`audit/c6-d8-sweep`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-d8-sweep) | Complete D8 hyperparameter sweep |
| [`audit/c6-scheduler-finite`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-scheduler-finite) | Finite-horizon scheduler audit |
| [`audit/c6-three-seed-validation`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-three-seed-validation) | Independent three-seed winner validation |
| [`audit/c6-source-falsification`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-source-falsification) | Assumption-satisfying source-identifiability falsification route |
| [`audit/c6-queue-calibration`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/audit/c6-queue-calibration) | Heterogeneous queue and scheduler calibration |
| [`release/evaluator-candidate`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/release/evaluator-candidate) | Cumulative evaluator-visible release candidate |
| [`release/final-regression`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/release/final-regression) | Final publication metadata and cumulative regression |
| [`release/portable-hash-pin`](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd/tree/release/portable-hash-pin) | Portable immutable evidence hash pin |

[`branch-audit.md`](branch-audit.md) records the exact old-to-new mapping and claim lineage for every branch.

## Repository contents

- `reproduction/` — executable claim verifiers and source audits.
- `hf_space_release/` — evaluator-facing pages, evidence, controls, release metadata, and historical judged snapshot.
- `reports/` — illustrated claim-by-claim report and figures.
- `notebooks/` — interactive evidence-first tutorial.

## Scope and limitations

- Claims 4 and 6 are about specific historical experiments; replacement checkpoints and new training runs cannot establish those exact past results.
- Claim 3’s broad “first” novelty clause is falsified by primary prior art, while its narrower theta-dependent theorem is left blocked where the derivation remains under-specified.
- Claim 5’s falsification depends on carrying Vanilla ASGD as the comparator; a different comparator changes the interpretation and is documented.
- The expectation proof certificate is an independent finite checker, not a formal proof-assistant artifact.
- Historical scores and failed routes are preserved for provenance and must not be presented as fresh judge results.

## Citation

```bibtex
@misc{erickson2026clipping,
  title         = {Clipping Makes Distributed and Federated Asynchronous SGD Robust to Stragglers},
  author        = {Erickson, Samuel and Johansson, Mikael},
  year          = {2026},
  eprint        = {2606.13287},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2606.13287}
}
```

## Thank you

Thank you to Samuel Erickson and Mikael Johansson for making the assumptions, delay model, clipping mechanism, and empirical questions concrete enough to audit claim by claim. This independent reproduction records both supporting evidence and the missing artifacts that prevent stronger historical conclusions.

## Attribution

Repository maintenance commits in the cleaned branch histories use:

`MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>`

The paper and its authors remain the source of the research claims; this repository contains an independent reproduction and audit record.
