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

All HF runs use the CPU-only `cpu-upgrade` flavor and the pinned image
`ghcr.io/astral-sh/uv:0.11.29-python3.12-bookworm-slim`. The initial generic
`python:3.12` launch failed before execution because that image had no `uv`;
it produced no scientific result.

This baseline makes no scientific claim and earns no forecast points. Its
purpose is to freeze provenance and prevent later experimental nodes from
silently changing the environment or run contract.
