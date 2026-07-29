# Claim 4 — BLOCKED

## Exact claim

The paper's historical ResNet-18/CIFAR-10 gradient-error experiment produced
the fitted sub-Weibull tail parameter `theta=2.71` (Figure 1). This is a claim
about one unidentified historical checkpoint and sampling/fitting protocol,
not every ResNet-18 run.

## Four completed routes

| Route | Direct observed result | Control | Outcome |
| --- | --- | --- | --- |
| initialized torchvision ResNet-18, real CIFAR-10 | theta `0.078919`, bootstrap 95% `[0.012133,0.088547]` | known theta 0.5/1/2.71 recovered | BLOCKED |
| one-epoch trained checkpoint | theta `0.224648`, bootstrap 95% `[0.120394,0.278741]` | same calibrated estimator | BLOCKED |
| exhaustive admissible tail counts | maximum `0.234507` at `k=7` over 125 choices | calibration passed | BLOCKED |
| mandatory falsification | numerical contradiction exists, but source protocol identity fails | false-value control falsified; true-value control retained | BLOCKED |

Long/uncertain routes used Hugging Face `cpu-upgrade`: estimated 8 cores,
actual 8 CPUs, no GPU. Seeds were fixed at `20260728`.
The terminal falsification run used Git
`316c9c5d781d189aceac6a59360bb51041da5324`.

The formal falsification checker output was:

```json
{"falsification_succeeded":false,"identified_fields":0,"required_fields":8,"positive_control_pass":true,"true_value_control_pass":true,"status":"PASS"}
```

- [initial raw JSON](evidence/claim4/raw_output.json),
  [verifier](evidence/claim4/verify.py), [checker](evidence/claim4/independent_check.py)
- [trained raw JSON](evidence/claim4_trained/raw_output.json),
  [verifier](evidence/claim4_trained/verify.py)
- [tail-count raw JSON](evidence/claim4_tail_audit/raw_output.json),
  [checker](evidence/claim4_tail_audit/independent_check.py)
- [falsification contract](evidence/claim4_falsification/claim_contract.json),
  [raw JSON](evidence/claim4_falsification/raw_output.json),
  [current terminal verifier](evidence/claim4_falsification/verify.py)

The numerical mismatch is not a valid falsification because the author
checkpoint, raw gradient norms, reference-gradient construction, batch/sample
count, optimizer step, preprocessing, and tail count `k` are not identified.
Those exact source artifacts are the concrete unblocker.
Limitation: none of the four routes identifies the historical checkpoint and
protocol, so the numerical mismatch cannot answer the exact historical claim.
