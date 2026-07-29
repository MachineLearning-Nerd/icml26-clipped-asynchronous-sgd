# Claim 4 route 3 evaluator note

This is a faithful real-data, full-model trained-checkpoint test of the
Figure 1 statement. It is not assumption-identical because the paper does not
publish the checkpoint, optimizer, preprocessing, batch size, reference
gradient construction, sample count, or estimator tail count.

The executable verifier regenerates the raw JSON, then launches a separately
implemented scalar OLS checker. Either exits nonzero on a protocol or numerical
failure. Regardless of the observed number, this route remains **BLOCKED**
unless the missing source protocol is resolved; a numerical mismatch alone is
not a valid falsification.
