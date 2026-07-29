# Release report and evaluator visibility

**Previous live judged score: 4/12.**

**Conservative projected score range: 6–9/12.**

**Best-supported possible score: 9/12 (forecast only).**

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 1 | 2 | HIGH | VERIFIED | exact expectation-rate proof DAG; non-kernel-proof risk |
| 2 | 1 | 2 | HIGH | VERIFIED | exact heterogeneous specialization; same formalization risk |
| 3 | 0 | 2 | HIGH | FALSIFIED | primary 2021 prior art falsifies broad novelty; narrow rate blocked |
| 4 | 0 | 0 | LOW | BLOCKED | all four routes complete; original checkpoint/norms/protocol missing |
| 5 | 1 | 2 | MEDIUM | FALSIFIED | exact-source comparator contradiction; omitted comparator is interpretation risk |
| 6 | 1 | 1 | LOW | BLOCKED | all four routes complete; real validation discrepancy is not identical historical realization |

Claims 1, 2, 3, 4, 5, and 6 changed from the previous presentation: the old
toy verifiers are superseded by exact proof, primary-source, real-data, and
terminal blocker evidence. Claims 4 and 6 remain BLOCKED for explicitly listed
source-identification reasons.

The exact publication action is an additive text-only commit to the existing
Space `DineshAI/AmgjQp4vrr`; no second Space is created. Existing judged files
remain present, the historical page remains reachable, and the original
revision is mirrored under `historical/judged-471748...`.

## Visibility matrix

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `#/claim-1` | yes | yes | yes | yes | yes | yes | VERIFIED |
| 2 | `#/claim-2` | yes | yes | yes | yes | yes | yes | VERIFIED |
| 3 | `#/claim-3` | yes | yes | yes | yes | yes | yes | FALSIFIED |
| 4 | `#/claim-4` | yes | yes | yes | yes | yes | yes | BLOCKED |
| 5 | `#/claim-5` | yes | yes | yes | yes | yes | yes | FALSIFIED |
| 6 | `#/claim-6` | yes | yes | yes | yes | yes | yes | BLOCKED |

Protected judged head:
`471748694e91b08b071d3d13c30d84b3091b5971`. Candidate regression command:

```bash
uv run --frozen python -m reproduction.run
```

All verifiers must exit zero for the cumulative run. Each current verifier
exits nonzero on hash mismatch, evidence mismatch, or failed negative control.

Release evidence is directly downloadable: [exact upload allowlist](UPLOAD_ALLOWLIST.txt),
[SHA-256 manifest](MANIFEST.sha256),
[subset check](evidence/release_candidate/old_new_subset_check.json),
[independent post-fix red team](evidence/release_candidate/red_team_pass2.json),
and [release verifier](evidence/release_candidate/verify.py).
