# Claim 2 — VERIFIED

## Exact claim

Under smoothness, sub-Weibull noise, bounded heterogeneity, and Algorithm 2's
uniform scheduling, Theorem 5.1 asserts

`O~((sigma^2+zeta^2)/epsilon^4 + (sigma+zeta)*tau_C/epsilon^3 + tau_C/epsilon^2)`

oracle calls, independent of `tau_max`.

Source anchors: exact archive SHA-256
`625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915`,
`main.tex:702-710`, proof `1046-1344`.

## Evidence

The same checked proof DAG retains `zeta` in the clipping bias, second moment,
large-gradient regions, and complexity inversion. Uniform scheduling is taken
after `x_t` is fixed, preserving conditional unbiasedness. The derived terms
are exactly:

```json
[
  {"factor":"sigma^2+zeta^2","epsilon_power":-4,"tau_C_power":0},
  {"factor":"sigma+zeta","epsilon_power":-3,"tau_C_power":1},
  {"factor":"1","epsilon_power":-2,"tau_C_power":1}
]
```

Formal run `92d2eb81-737b-41a7-8a9f-a7b91739b130`, Git
`2d59e8b702bae88f1ad0c9c102314ebd28355b40`, one local process,
2.637857 s, seed `20260732`, no GPU.

- [claim contract](evidence/expectation_theorems/claim_contract.json)
- [source audit](evidence/expectation_theorems/source_audit.md)
- [derivation](evidence/expectation_theorems/derivation.md)
- [formal raw JSON](evidence/expectation_theorems/raw_output.json)
- [current verifier](evidence/expectation_theorems/verify.py)
- [independent checker](evidence/expectation_theorems/independent_check.py)
- [limitations](evidence/expectation_theorems/limitations.md)

Negative controls and limitations are identical to Claim 1; the homogeneous
specialization is recovered by setting `zeta=0`.
