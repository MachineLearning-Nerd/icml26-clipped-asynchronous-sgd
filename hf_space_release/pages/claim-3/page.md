# Claim 3 — FALSIFIED

## Exact claim — compound contract

The imported claim conjoins:

1. this paper gives the first high-probability convergence guarantee for
   asynchronous SGD/optimization; and
2. Theorems 4.3/5.2 have the displayed theta-governed polylogarithmic
   `delta` dependence.

The target source uses the broad wording “first time in asynchronous
optimization” at `main.tex:601-603`.

## Result

The novelty conjunct is falsified by Cohen et al.,
*Asynchronous Stochastic Optimization Robust to Arbitrary Delays*,
NeurIPS 2021, arXiv `2106.11879`. Its Picky SGD is an asynchronous delayed
stochastic-gradient algorithm for smooth nonconvex objectives. Theorem 1 gives
stationarity success at least `1/2`; the primary source explicitly amplifies
this to arbitrary `1-delta` with `O(log(1/delta))` independent restarts.

For `k=ceil(log2(1/delta))`, the checker recomputed:

| delta | k | failure bound |
| ---: | ---: | ---: |
| 0.2 | 3 | 0.125 |
| 0.05 | 5 | 0.03125 |
| 0.01 | 7 | 0.0078125 |
| 0.000001 | 20 | 0.000000953674 |

Primary source archive SHA-256
`95cb673ff942137d6822dc250ec94f82693fdab423d981360cc4578f960d8205`;
PDF SHA-256
`bcfc13492b4e6aa73f04e9d55bdd5a14b028c0e0bef79b8e74142300e69b9798`.

Formal run `0c5e2c2c-b1d5-4f89-963f-d54017e92ebc`, Git
`ddc67f57fa8ec533bb05bf491478cc3355e42ee9`, one local process,
3.11235 s, seed `20260735`, no GPU.

- [route 3 contract](evidence/claim3_route3/claim_contract.json)
- [source audit](evidence/claim3_route3/source_audit.md)
- [formal raw JSON](evidence/claim3_route3/raw_output.json)
- [current verifier](evidence/claim3_route3/verify.py)
- [independent checker](evidence/claim3_route3/independent_check.py)

Controls for serial SGD, a later paper, expectation-only ASGD, and
high-probability runtime without optimization convergence were all rejected.

## Narrow rate subclaim

The precise average-gradient rate remains **BLOCKED**, not falsely promoted.
The printed proof has a factor-two increment error, a missing cardinality, a
dropped `/T`, and an appendix-only extra
`sigma^2 log(1/delta)^(2theta+1)/epsilon^2` term. A repaired Freedman derivation
retains the extra term.

- [printed-proof raw audit](evidence/claim3_route1/raw_output.json) and
  [checker](evidence/claim3_route1/independent_check.py)
- [repaired-proof raw result](evidence/claim3_route2/raw_output.json) and
  [checker](evidence/claim3_route2/independent_check.py)

The compound imported Claim 3 is FALSIFIED because its material novelty
conjunct is false. This does not claim a counterexample to the narrower rate.
Limitation: falsification of the broad novelty conjunct does not verify or
falsify the narrower theta-dependent rate theorem.
