# Claim 6 complete D=4 selection sweep

This route promotes the stronger real-data pilot architecture and covers every
paper learning rate for vanilla ASGD and every learning-rate/clipping-radius
pair for Clipped ASGD. It uses the exact D=4 cap and selects the first 70%
test-accuracy hit within each method.

Eight independent configurations run concurrently as single-threaded CPU
processes. This parallelism changes only physical experiment runtime; each
simulated ASGD trajectory is sequential and deterministic.

The 200-time-unit evaluation cadence creates a declared `[0,200]` uncertainty
on each first-hit time. The full D=8 sweep and three-seed validation of the
independently selected winners are separate descendant stages.
