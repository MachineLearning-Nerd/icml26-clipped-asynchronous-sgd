# Claims 1–2 current verification

**Claim 1: VERIFIED. Claim 2: VERIFIED.**

This proof-level route supersedes the historical synthetic quadratic as the
current verifier for the two expectation theorems. It reconstructs a
constructive derivation for every epsilon in `(0,1)`, emits a machine-readable
proof DAG, and independently checks the exact complexity factors and
exponents. It does not infer a universal theorem from finite experiments.

Run with the campaign-wide fixed command:

```text
uv run --frozen python -m reproduction.run
```

The verifier exits nonzero if the proof certificate fails or if any of the
three negative controls is accepted.
