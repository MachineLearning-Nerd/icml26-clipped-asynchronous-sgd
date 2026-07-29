# Claim 6 current validation

This is the current executable verifier for Claim 6. It regenerates 12 real
CIFAR-10 trajectories from four locked selection-stage winners and three
unseen deterministic seeds, writes raw JSON, and invokes a separately
implemented checker. It exits nonzero on computation, contract, aggregation,
control, or verdict failure.

The run uses the fixed command:

```text
uv run --frozen python -m reproduction.run
```

The machine-readable result assigns exactly one terminal verdict:
`VERIFIED` if both preregistered caption contracts pass, otherwise `BLOCKED`.
It never treats a reconstruction mismatch as falsification.
