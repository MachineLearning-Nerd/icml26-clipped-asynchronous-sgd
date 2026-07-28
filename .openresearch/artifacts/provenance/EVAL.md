# Baseline evaluation contract

The fixed command is:

```bash
uv run --frozen python -m reproduction.run
```

The baseline passes only if the paper source hash, live verdict revision,
protected Space revision, and 13-entry protected-file manifest match the
audited values. It prints the exact Git SHA, lock hash, selected compute plan,
actual CPU allocation visible inside the job, package versions, and runtime.
Any mismatch exits nonzero.

This baseline makes no scientific claim and earns no forecast points. Its
purpose is to freeze provenance and prevent later experimental nodes from
silently changing the environment or run contract.

