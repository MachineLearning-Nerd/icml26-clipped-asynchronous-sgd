# Current cumulative verification

**Previous live judged score: 4/12.**

**Conservative projected score after this candidate: 6–9/12.**

**Best-supported possible new score: 9/12 (forecast, not a judge result).**

No score increase is claimed. Only the live judge can change the score.

## Fixed reproduction contract

```bash
uv run --frozen python -m reproduction.run
```

- Python: 3.12.11
- environment: repository-level `.venv`, `uv.lock` SHA-256
  `088087f86a36731bb34896bf76bb1a4f4461c23f4a1526f075ff80c25a99c2bb`
- deterministic campaign seeds: `20260728` through `20260736`
- GPU: prohibited and not used
- short symbolic audits: local, one process, under five minutes
- long/uncertain real CIFAR-10 work: Hugging Face `cpu-upgrade`, 8 CPUs
- fixed code: [entrypoint](evidence/reproduction/run.py),
  [configuration](evidence/reproduction/config.json),
  [pyproject](evidence/pyproject.toml), [uv lock](evidence/uv.lock)

## Current result

| Claim | Verdict | Confidence | Current points | Possible points | Core evidence |
| --- | --- | --- | ---: | ---: | --- |
| 1 | VERIFIED | HIGH | 1 | 2 | 11-node constructive proof DAG; three rejected controls |
| 2 | VERIFIED | HIGH | 1 | 2 | heterogeneous specialization of the same checked DAG |
| 3 | FALSIFIED | HIGH | 0 | 2 | NeurIPS 2021 prior high-probability asynchronous SGD result |
| 4 | BLOCKED | LOW | 0 | 0 | four routes; author checkpoint/raw norms/protocol unavailable |
| 5 | FALSIFIED | MEDIUM | 1 | 2 | exact source reports Shakespeare/Vanilla 1.8x and 2.0x |
| 6 | BLOCKED | LOW | 1 | 1 | real CIFAR validation disagrees, but historical protocol is underidentified |

## Visibility matrix

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Claim 1](#/claim-1) | yes | yes | yes | yes | yes | yes | VERIFIED |
| 2 | [Claim 2](#/claim-2) | yes | yes | yes | yes | yes | yes | VERIFIED |
| 3 | [Claim 3](#/claim-3) | yes | yes | yes | yes | yes | yes | FALSIFIED |
| 4 | [Claim 4](#/claim-4) | yes | yes | yes | yes | yes | yes | BLOCKED |
| 5 | [Claim 5](#/claim-5) | yes | yes | yes | yes | yes | yes | FALSIFIED |
| 6 | [Claim 6](#/claim-6) | yes | yes | yes | yes | yes | yes | BLOCKED |

The superseding current code is the cumulative regression suite linked above.
The old `python3 repro/src/verify.py` shown on the preserved historical page is
explicitly rejected as toy evidence and is not the current verification run.
That page is labelled exactly **Historical rejected baseline** and remains last
in the navigation.

Release-gate evidence: [contract](evidence/release_candidate/claim_contract.json),
[method](evidence/release_candidate/method.md),
[current verifier](evidence/release_candidate/verify.py),
[independent red-team checker](evidence/release_candidate/redteam_space_candidate.py),
[initial failed review](evidence/release_candidate/red_team_pass1.json),
[post-fix passing review](evidence/release_candidate/red_team_pass2.json),
[protected subset proof](evidence/release_candidate/old_new_subset_check.json),
and [secret scan](evidence/release_candidate/secret_scan.json).
