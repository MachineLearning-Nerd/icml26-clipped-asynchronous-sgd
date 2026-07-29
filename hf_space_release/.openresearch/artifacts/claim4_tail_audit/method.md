# Claim 4 exhaustive tail-count audit

The Vladimirova order-statistic estimator requires a tail count `k`, which the
paper does not publish. This route holds the real CIFAR-10 data, full trained
ResNet-18 checkpoint, reference gradient, and 128 raw gradient-error norms
fixed, then exhausts the estimator's complete mathematical domain
`k = 3, ..., 127`.

This is a one-core scalar analysis expected to finish in seconds. The complete
domain was selected independently of the target `2.71`. The known-theta
calibration and rejected reciprocal-convention control remain mandatory.
