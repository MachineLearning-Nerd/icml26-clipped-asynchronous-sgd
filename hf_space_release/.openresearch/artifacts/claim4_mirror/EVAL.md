# Claim 4 route 2 evaluator note

This route tests a reproducibility-infrastructure hypothesis, not the paper
claim: a checksum-identical Hugging Face mirror should remove the slow dataset
transfer without changing the pilot observations. It exits nonzero if the
archive MD5 differs, regeneration fails, the known-theta controls fail, the
wrong reciprocal convention is not rejected, or the independent OLS
recomputation differs.

Scientific Claim 4 status remains **BLOCKED** until a trained-checkpoint route
addresses the paper's actual “in training” wording and protocol sensitivity.
