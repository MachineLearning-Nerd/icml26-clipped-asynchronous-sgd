# Limitations and deviations

- This calibration uses one seed, one delay factor, selected hyperparameters,
  and a 3,200-time-unit cap. It is not the full Figure 4 sweep.
- Architecture, batch size, normalization, partition code, and evaluation
  cadence are defensible reconstruction choices because the paper omits them.
- The direct Algorithm 2 scheduler produces mean oracle times below both
  Figure 4 captions even after a finite-horizon audit. Training therefore
  reports its realized timing and does not claim source-code identity.
- Simulated workers are evaluated sequentially with queued gradients computed
  from their dispatch snapshots. Process-level parallelism is only across
  independent configurations and does not change simulated training dynamics.
- Passing this pilot cannot change Claim 6 from **BLOCKED**.
