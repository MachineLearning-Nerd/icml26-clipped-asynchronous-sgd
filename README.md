# Reproduction: clipping and asynchronous SGD

This repository audits
[*Clipping Makes Distributed and Federated Asynchronous SGD Robust to Stragglers*](https://arxiv.org/abs/2606.13287)
claim by claim. The previous live judge scored the original toy-only Space
**4/12**. The current evidence supports a conservative **6–9/12 forecast**,
with **9/12** the best-supported possible result; this is not a new judge score.

The exact expectation-rate claims were reconstructed as a checked proof DAG
(Claims 1–2 VERIFIED). The broad “first high-probability asynchronous
optimization result” is contradicted by a NeurIPS 2021 primary source (Claim 3
FALSIFIED). The imported Shakespeare speedup range conflicts with the paper's
Vanilla-ASGD values under its natural comparator (Claim 5 FALSIFIED, MEDIUM).
Claims 4 and 6 are BLOCKED after four routes because the historical
checkpoint/raw gradients and exact Figure 4 protocol are not available.

- [Illustrated technical report](reports/clipping-asgd/report.md)
- [Tutorial marimo notebook](notebooks/clipped_asgd_reproduction.py)
- [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/blob/main/notebooks/clipped_asgd_reproduction.py)
- [Evaluator-visible Space release mirror](hf_space_release/)

The fixed command for every experiment is:

```bash
uv run --frozen python -m reproduction.run
```

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Public landing page and publication surface | Not run as an experiment (publication surface) | report, notebook, and Space mirror | none |
| [Frozen baseline](https://github.com/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/tree/orx/frozen-baseline-provenance-and-evidence-harness) | Pin paper, verdict, Space, environment, and fixed harness | `uv run --frozen python -m reproduction.run` | PASS | local CPU, one process, 37 s |
| [Claims 1–2 certificate](https://github.com/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/tree/orx/claims-1-and-2-constructive-expectation-theorem) | Constructive expectation-theorem proof DAG | `uv run --frozen python -m reproduction.run` | Claims 1–2 VERIFIED | local CPU, one process, 2.64 s |
| [Claim 3 prior art](https://github.com/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/tree/orx/claim-3-route-3-prior-art-falsification) | Primary-source novelty audit after two proof routes | `uv run --frozen python -m reproduction.run` | Claim 3 FALSIFIED; narrow rate BLOCKED | local CPU, one process, 3.11 s |
| [Claim 4 falsification](https://github.com/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/tree/orx/claim-4-mandatory-falsification-protocol-identifiability) | Fourth route after real ResNet-18/CIFAR-10 estimates | `uv run --frozen python -m reproduction.run` | Claim 4 BLOCKED | HF `cpu-upgrade`, 8 CPUs for real routes; local audit |
| [Claim 6 validation](https://github.com/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/tree/orx/claim-6-independent-three-seed-winner-validation) | Three-seed real CIFAR validation of selected D4/D8 winners | `uv run --frozen python -m reproduction.run` | D4 1.023x, 95% [0.928, 1.121]; D8 censored | HF `cpu-upgrade`, 8 CPUs, 40m43s |
| [Claim 5 source audit](https://github.com/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/tree/orx/claim-5-exact-source-and-comparator-audit) | Exact comparator and source-value check | `uv run --frozen python -m reproduction.run` | Claim 5 FALSIFIED, MEDIUM | local CPU, one process, 7.69 s |
| [Cumulative release candidate](https://github.com/MachineLearning-Nerd/icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle/tree/orx/evaluator-visible-cumulative-release-candidate) | Pin all raw results, regression-test, red-team, publish | `uv run --frozen python -m reproduction.run` | pending release gates | local CPU, one process |

## Original workspace note

ICML 2026 agent reproduction workspace for AmgjQp4vrr.
