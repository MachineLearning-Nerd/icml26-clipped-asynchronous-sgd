# Claim 1 — VERIFIED

## Exact claim

Under the homogeneous assumptions of Theorem 4.2, for every
`epsilon in (0,1)` there exist a constant step size and clipping radius such
that Clipped ASGD has oracle complexity

`O~(sigma^2/epsilon^4 + sigma*tau_C/epsilon^3 + tau_C/epsilon^2)`,

with no `tau_max` dependence.

Source anchors: exact archive SHA-256
`625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915`,
`main.tex:576-584`, proof `1046-1344`.

## Evidence

An independently reconstructed 11-node proof DAG derives the clipped bias
bound, virtual-iterate bound `||x_t-x_tilde_t|| <= eta*c*tau_C`, unified
small/large-gradient descent, telescoping, norm conversion, constructive
parameters, and the three epsilon exponents. The checker output was:

```json
{"claim_1":"VERIFIED","claim_2":"VERIFIED","dag_nodes":11,"errors":[],"negative_controls":{"missing_dependency_rejected":true,"tau_max_injection_rejected":true,"wrong_exponent_rejected":true},"status":"PASS"}
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

The verifier hash-pins the formal raw result and exits nonzero on a hash or
checker failure. Controls injecting `tau_max`, changing the noise exponent
from `epsilon^-4` to `epsilon^-3`, or deleting a DAG dependency are rejected.

Limitation: this finite symbolic certificate is not a Lean/Coq kernel proof;
soft-O hides logarithms and constants depending on fixed `L`, `Delta`, and
`theta`.
