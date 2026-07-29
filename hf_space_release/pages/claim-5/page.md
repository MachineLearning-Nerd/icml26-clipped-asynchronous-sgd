# Claim 5 — FALSIFIED

## Exact claim imported by the judge

“On CIFAR-10 with delay factor D=4, Clipped ASGD achieves a 1.8x wall-clock
speedup over vanilla ASGD (Figure 2), and on Shakespeare it achieves 2.0-2.2x
speedup depending on the delay regime (Figure 3).”

The only named comparator, Vanilla ASGD, is carried across the coordinated
dataset clauses in the machine-checkable contract.

## Primary-source comparison

| Dataset/delay | Comparator | Imported | Exact source |
| --- | --- | ---: | ---: |
| CIFAR-10 D4 | Vanilla ASGD | 1.8x | 1.8x |
| Shakespeare D4 | Vanilla ASGD | at least 2.0x | 1.8x |
| Shakespeare D8 | Vanilla ASGD | 2.0–2.2x | 2.0x |

The D4 Shakespeare value contradicts the imported range, so the compound
claim is FALSIFIED under this contract. Exact source anchors are
`main.tex:786-790` and `821-833`, archive SHA-256
`625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915`.

Formal run `935dc5e3-7a51-41e2-9afb-ed50bc7c24e7`, Git
`9b4a531e169220feb263de71bd9b88c70e3311c0`, one local process,
7.692677 s, seed `20260736`, no GPU.

- [claim contract](evidence/claim5_source_audit/claim_contract.json)
- [source audit](evidence/claim5_source_audit/source_audit.md)
- [formal raw JSON](evidence/claim5_source_audit/raw_output.json)
- [current verifier](evidence/claim5_source_audit/verify.py)
- [independent checker](evidence/claim5_source_audit/independent_check.py)
- [limitations](evidence/claim5_source_audit/limitations.md)

Controls: corrected Vanilla range `[1.8,2.0]` passes; explicitly changing the
comparator to Delay-adaptive ASGD gives `[2.1,2.2]`; a comparator that changes
with delay is rejected.

Confidence is MEDIUM because the Shakespeare clause does not repeat a
comparator. Under an explicitly changed Delay-adaptive comparator it fits the
range; without any fixed comparator the claim is BLOCKED rather than verified.
