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

The fixed runner invokes `verify.py`, which checks the committed
`raw_output.json` using a separately implemented OLS checker. Either the
known-theta control, the deliberately wrong reciprocal-convention control, or
the independent recomputation failing makes the command exit nonzero.

Observed pilot result: `theta_hat = 0.0789191`, percentile bootstrap 95%
interval `[0.0121327, 0.0885472]`. The reported `2.71` is outside this interval,
but this is not a falsification because the reconstruction does not share the
paper's unreported protocol.

Source run `512fbeef-0db3-44ec-81e8-7fcba10ba53e` emitted a complete runner
`PASS` payload and independent-checker `PASS` after 2,061.783 seconds, but HF
marked the job failed because the payload arrived just after its execution
timeout. The status and timing are preserved in `run_metadata.json`.
