# Claims 1–2 verification method

This route replaces the earlier finite quadratic illustration with a
proof-level artifact. A generator emits a typed proof DAG, constructive
parameters, exact complexity monomials, source hashes, quantifiers, and a
repair ledger. A separately implemented checker verifies the DAG topology,
tail identity, large-gradient constants, norm conversion, homogeneous
specialization, exact epsilon and concurrency exponents, and absence of
`tau_max`.

Three mutations are applied in memory: adding `tau_max`, changing the
noise-term exponent, and deleting a required proof edge. Each mutation must be
rejected. The checker exits nonzero if the certificate or any control fails.
