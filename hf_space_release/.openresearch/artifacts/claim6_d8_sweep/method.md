# Claim 6 complete D=8 selection sweep

This route changes only the paper delay factor and cap from the accepted D=4
experiment. It covers every paper learning rate for vanilla ASGD and every
learning-rate/clipping-radius pair for Clipped ASGD, then selects the first
70% test-accuracy hit within each method.

Eight independent configurations run concurrently as single-threaded CPU
processes. The 200-time-unit evaluation cadence creates a declared `[0,200]`
uncertainty on first-hit times. Three-seed validation of the independently
selected winners is a separate descendant stage.
