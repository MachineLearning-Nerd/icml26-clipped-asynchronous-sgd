# Claim 6 finite-horizon scheduler audit

The first infinite-horizon calibration was rejected at `D=8`; its tolerance
was not loosened. This route instead uses the paper's own 8,000- and
12,000-time-unit training caps. For each delay it samples 512 independent
triplets, matching the paper's three-seed aggregation, and constructs a
two-sided empirical 99% prediction interval for the mean time per completed
oracle call.

The caption value is not used to select a horizon, event count, seed, or
tolerance. A homogeneous no-queue harmonic-throughput calculation is the
negative control.
