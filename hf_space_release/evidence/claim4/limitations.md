# Claim 4 limitations and deviations

- The checkpoint is deterministic initialization rather than an unknown point
  "in training".
- The reference gradient uses 2,048 examples, not the full 50,000-example
  training split.
- There are 24 error observations, selected to keep this first evidence
  milestone bounded.
- The paper does not specify its data augmentation, batch size, checkpoint,
  sample count, reference gradient, or tail fraction.
- Therefore this node must remain `BLOCKED`, irrespective of whether its
  interval happens to contain `2.71`.
