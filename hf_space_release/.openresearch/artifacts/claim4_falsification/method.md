# Claim 4 mandatory falsification route

This route restates the claim as a historical measurement on the paper's
specific but unpublished training state. A valid counterexample therefore
requires the source checkpoint, raw error norms, gradient/reference protocol,
and estimator settings. The verifier audits each required field, then applies
the falsification rule as a conjunction rather than treating a nearby
reconstruction as assumption-identical.

The same numerical rule is tested on two fully specified controls. It must
reject a deliberately false `theta=1.0` report for a calibrated `theta=2.71`
sample and must not reject `2.71` under the preregistered tolerance. This proves
the route can falsify when the necessary evidence exists.
