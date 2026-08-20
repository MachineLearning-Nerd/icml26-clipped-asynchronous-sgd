# Branch audit

Repository: [MachineLearning-Nerd/icml26-clipped-asynchronous-sgd](https://github.com/MachineLearning-Nerd/icml26-clipped-asynchronous-sgd)

The repository was renamed from `icml26-repro-AmgjQp4vrr-clipping-makes-distributed-and-federated-asynchronous-sgd-robust-to-straggle`. Former `orx/*` labels are replaced with names that describe the evidence role.

## Old-to-new mapping

| Former branch | Clean branch | Role in the evidence lineage |
|---|---|---|
| `orx/frozen-baseline-provenance-and-evidence-harness` | `historical/judged-baseline` | Freeze the original 4/12 judged state and provenance |
| `orx/claims-1-and-2-constructive-expectation-theorem` | `audit/c1-c2-expectation-rates` | Constructive expectation-theorem proof DAG |
| `orx/claim-3-route-1-published-proof-audit` | `audit/c3-published-proof` | Audit the printed high-probability proof |
| `orx/claim-3-route-2-repaired-freedman-derivation` | `audit/c3-repaired-freedman` | Repair and delimit the narrower Freedman rate |
| `orx/claim-3-route-3-prior-art-falsification` | `audit/c3-prior-art` | Primary-source novelty falsification |
| `orx/claim-4-cifar-10-resnet-18-gradient-noise-audit` | `audit/c4-cifar-resnet` | Real CIFAR-10/ResNet-18 gradient-noise audit |
| `orx/claim-4-mandatory-falsification-protocol-identif` | `audit/c4-source-identifiability` | Mandatory historical-protocol identifiability route |
| `orx/claim-4-milestone-committed-pilot-evidence` | `audit/c4-pilot` | Committed Claim 4 pilot evidence |
| `orx/claim-4-route-2-checksum-identical-hf-dataset-mi` | `audit/c4-dataset-checksum` | Dataset checksum and provenance route |
| `orx/claim-4-route-3-trained-resnet-18-checkpoint` | `audit/c4-trained-resnet` | Trained ResNet-18 checkpoint route |
| `orx/claim-4-route-4-checkpoint-and-estimator-falsifi` | `historical/c4-falsification-route` | Rejected checkpoint/estimator falsification route |
| `orx/claim-5-exact-source-and-comparator-audit` | `audit/c5-comparator-source` | Exact source and comparator audit |
| `orx/claim-6-cifar-pilot-classic-two-conv-cnn` | `audit/c6-cifar-pilot` | Classic two-convolution-CNN pilot |
| `orx/claim-6-cifar-pilot-cnn-protocol-calibration` | `audit/c6-cnn-protocol` | CNN protocol calibration |
| `orx/claim-6-d4-complete-hyperparameter-sweep` | `audit/c6-d4-sweep` | Complete D4 hyperparameter sweep |
| `orx/claim-6-d4-sweep-one-time-worker-initialization` | `audit/c6-d4-worker-init` | One-time worker-initialization control |
| `orx/claim-6-d8-complete-hyperparameter-sweep` | `audit/c6-d8-sweep` | Complete D8 hyperparameter sweep |
| `orx/claim-6-finite-horizon-scheduler-audit` | `audit/c6-scheduler-finite` | Finite-horizon scheduler audit |
| `orx/claim-6-independent-three-seed-winner-validation` | `audit/c6-three-seed-validation` | Independent three-seed winner validation |
| `orx/claim-6-mandatory-assumption-satisfying-falsific` | `audit/c6-source-falsification` | Assumption-satisfying source-identifiability route |
| `orx/claim-6-scheduler-calibration-heterogeneous-queu` | `audit/c6-queue-calibration` | Heterogeneous queue and scheduler calibration |
| `orx/evaluator-visible-cumulative-release-candidate` | `release/evaluator-candidate` | Cumulative evaluator-visible release candidate |
| `orx/final-publication-metadata-and-cumulative-regres` | `release/final-regression` | Final publication metadata and cumulative regression |
| `orx/portable-cumulative-release-hash-pin` | `release/portable-hash-pin` | Portable immutable evidence hash pin |

`main` is the canonical publication surface. Former `orx/*` remote branches are deleted after the clean replacements are pushed; reachable evidence content is retained in the corresponding histories.

## Claim lineage

| Claim | Primary branch evidence | Canonical files |
|---|---|---|
| 1 — homogeneous expectation rate | `audit/c1-c2-expectation-rates` | `hf_space_release/reproduction/claims/expectation_theorem.py`, `hf_space_release/pages/claim-1/` |
| 2 — heterogeneous expectation rate | `audit/c1-c2-expectation-rates` | `hf_space_release/reproduction/claims/expectation_theorem.py`, `hf_space_release/pages/claim-2/` |
| 3 — novelty and theta-rate clauses | `audit/c3-prior-art`, `audit/c3-repaired-freedman` | `hf_space_release/reproduction/claims/claim3_prior_art.py`, `claim3_repaired_freedman.py` |
| 4 — gradient-noise fit | `audit/c4-cifar-resnet`, `audit/c4-source-identifiability` | `hf_space_release/reproduction/claims/claim4.py`, `claim4_trained.py` |
| 5 — source/comparator speedups | `audit/c5-comparator-source` | `hf_space_release/reproduction/claims/claim5_source_audit.py` |
| 6 — label-skew asynchronous speedups | `audit/c6-d4-sweep`, `audit/c6-d8-sweep`, `audit/c6-three-seed-validation` | `hf_space_release/reproduction/claims/claim6_d4_sweep.py`, `claim6_d8_sweep.py`, `claim6_validation.py` |

## Attribution and verification policy

- Clean maintenance commits use `MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>`.
- Branch cleanup changes labels and links, not the scientific evidence or its limitations.
- Claims about historical checkpoints and training protocols remain blocked when the source artifacts are missing.
- Release branches are candidate publication surfaces until the external evaluator runs them.
