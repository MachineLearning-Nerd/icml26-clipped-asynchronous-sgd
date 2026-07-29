# Claim 6 — BLOCKED

## Exact claim and source

Figure 4 reports historical label-skew CIFAR-10 speedups of approximately
`1.2x` at `D=4` and `1.3x` at `D=8`, using 16 workers, full concurrency,
eight service times at 1 and eight at D, Dirichlet label skew `alpha=0.5`,
three seeds, a two-layer CNN, and a 70% test-accuracy target.

## Faithful real-data evidence

A complete 45-configuration CIFAR-10 selection sweep found:

| Delay | Best Vanilla | Best Clipped | selection speedup |
| --- | ---: | ---: | ---: |
| D4 | 4200 | 3400 | 1.2353x |
| D8 | 7400 | 6800 | 1.0882x |

Independent three-seed validation did not sustain D4:

- Vanilla first hits: `[5200,5800,7000]`
- Clipped first hits: `[4800,6200,6600]`
- paired mean speedup: `1.022727x`
- combined 95% cadence/bootstrap interval:
  `[0.928338,1.120652]`
- the interval excludes `1.2` and includes no effect

At D8, one clipped seed was right-censored at the 12000 cap, so no uncensored
speedup interval exists. The long run used Hugging Face `cpu-upgrade`,
estimated/actual 8 CPUs, no GPU, 2406.144 formal seconds, seeds
`20260730..20260732`, Git
`b93615e4e8b862f40189057998042a5dd2402cda`.

- [D4 sweep raw JSON](evidence/claim6_d4_sweep/raw_output.json) and
  [checker](evidence/claim6_d4_sweep/independent_check.py)
- [D8 sweep raw JSON](evidence/claim6_d8_sweep/raw_output.json) and
  [checker](evidence/claim6_d8_sweep/independent_check.py)
- [validation contract](evidence/claim6_validation/claim_contract.json),
  [raw JSON](evidence/claim6_validation/raw_output.json),
  [verifier](evidence/claim6_validation/verify.py),
  [checker](evidence/claim6_validation/independent_check.py)
- [mandatory falsification raw JSON](evidence/claim6_falsification/raw_output.json),
  [current terminal verifier](evidence/claim6_falsification/verify.py),
  [checker](evidence/claim6_falsification/independent_check.py)

The falsification route matched eight material fields, left seven unresolved,
and mismatched aggregation. It correctly rejected the assumption-violating
control and accepted fully specified historical/universal positive controls.

Verdict remains BLOCKED: the reconstruction discrepancy is not the original
historical realization. Author code, original per-seed curves/seeds, exact CNN,
preprocessing, event queue/tie order, evaluation cadence, and aggregation
would unblock it.

Limitation: the faithful reconstruction still differs from seven unidentified
historical fields and therefore cannot falsify a particular past realization.
