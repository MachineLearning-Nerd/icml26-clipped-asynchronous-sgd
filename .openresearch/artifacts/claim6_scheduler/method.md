# Claim 6 scheduler calibration

Algorithm 2 maintains 16 outstanding jobs. When any job completes, its stale
gradient would be applied and a worker is selected uniformly from all 16.
That worker receives the new model even if it already has queued work. Each
worker is therefore a single-server FIFO queue; eight have service time 1 and
eight have service time `D`.

The calibration runs 200,000 completions after a 2,000-event burn-in for each
of three seeds and both `D=4,8`. It compares mean inter-completion time with
Figure 4's `0.337` and `0.668`. The negative control instead reschedules only
the completing worker, eliminating the heterogeneous queue mechanism.
