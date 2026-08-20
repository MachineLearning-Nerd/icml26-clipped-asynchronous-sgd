# Source audit

The paper-source hashes below are carried by the claim artifacts and are used to anchor theorem lines, figure captions, and prior-art comparisons. The source pin is evidence provenance, not an author endorsement.

| Field | Value |
| --- | --- |
| Paper | *Clipping Makes Distributed and Federated Asynchronous SGD Robust to Stragglers* |
| arXiv | `2606.13287` |
| Paper HTML SHA-256 | `292ba2ce9a95e41279fe1535ffa23b720f18fb2139c3e26324138c0d4a0304ff` |
| LaTeX archive SHA-256 | `625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915` |
| Source evidence | [`expectation_theorems/raw_output.json`](.openresearch/artifacts/expectation_theorems/raw_output.json) |

Important paper anchors:

- C1: Theorem 4.2, source lines `576–584`.
- C2: Theorem 5.1, source lines `702–710`.
- C3: headline novelty at lines `601–603`, theta-rate statements at `604–614` and `724–735`, proof appendix at `1350–1548`.
- C4: Figure 1 and its gradient-noise protocol, including the reported `theta=2.71`.
- C5: CIFAR source lines `786–790`, Shakespeare source lines `821–833`; figure hashes are stored in the claim-5 raw artifact.
- C6: Figure 4 protocol and caption fields, source lines `758–784` and `851–910`.

C3 prior-art source: Cohen et al., [*Asynchronous Stochastic Optimization Robust to Arbitrary Delays*](https://arxiv.org/abs/2106.11879), NeurIPS 2021. The audit checks that it is asynchronous stochastic optimization, provides arbitrary-`delta` amplification, and predates the target paper; it does not claim that it proves the target’s narrower average-gradient theta rate.

The source and the linked author repository did not provide the historical checkpoints, raw gradient norms, seed identifiers, architecture details, queue/timing choices, or raw curves needed for assumption-identical C4/C6 conclusions. Those missing fields are part of the verdict, not omitted bookkeeping.
