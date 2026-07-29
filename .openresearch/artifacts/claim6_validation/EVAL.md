# Claim 6 current validation

This accepted validation-stage evidence is hash-pinned to run
`05a78a25-3032-47d1-8862-653c211b3c9b`. The current Claim 6 verifier is the
descendant falsification audit. This page remains the complete validation
record and its checker exits nonzero on hash, contract, aggregation, control,
or verdict failure.

The run uses the fixed command:

```text
uv run --frozen python -m reproduction.run
```

The D=4 mean speedup was 1.022727x with combined cadence-aware 95% interval
`[0.928338, 1.120652]`. At D=8, one clipped run was censored at the paper's
12,000 cap. The recorded verdict is `BLOCKED`; the independent checker passed.
Raw SHA-256:
`6bc2a8fe3148f83d72869d7f8fc50ffe0e303cde359b81d200edd1c9804aa539`.
