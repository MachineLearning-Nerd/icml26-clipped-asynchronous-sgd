# Limitations and deviations

- Hyperparameter selection uses one preregistered seed. Three independent
  seeds will be applied only to selected winners; the paper says all
  experiments are averaged over three seeds but does not describe its tuning
  protocol.
- Architecture, batch size, preprocessing, partition implementation, and
  evaluation cadence remain source-unidentified reconstruction choices.
- The direct Algorithm 2 scheduler's oracle times differ from the Figure 4
  captions; realized times remain visible in every configuration.
- D=4 alone cannot establish the full two-delay Claim 6 result.
