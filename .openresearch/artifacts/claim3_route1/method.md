# Method

This route is a proof-ledger audit, not an optimization simulation. It encodes
the exact printed premises and recomputes the elementary arithmetic behind the
martingale increment bound, the union-bound statement, the normalization by
the horizon, and the final complexity inversion. An independent checker reads
only the machine-readable output and repeats those checks.

The route is non-circular: no horizon, tolerance, or sample size was selected
from the desired conclusion. Corrected local expressions are positive controls;
the printed inconsistent expressions are negative controls.
