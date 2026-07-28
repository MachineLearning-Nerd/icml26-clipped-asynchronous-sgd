# Claim 4 evaluator entrypoint

Current status: **BLOCKED**.

This real-data pilot addresses the judge's criticism that no neural network or
CIFAR-10 experiment was run. It intentionally does not claim to reproduce
`theta=2.71`, because the paper omits essential protocol details and the pilot
uses an initialization checkpoint, an approximate reference gradient, and 24
observations.

Run exactly:

```bash
uv run --frozen python -m reproduction.run
```

The fixed runner invokes `verify.py`, which regenerates `raw_output.json` and
`negative_control.json`, then invokes a separately implemented OLS checker.
Either the known-theta control or the independent recomputation failing makes
the command exit nonzero. Generated numerical evidence will be mirrored here
and onto the canonical candidate page in the next immutable child.
