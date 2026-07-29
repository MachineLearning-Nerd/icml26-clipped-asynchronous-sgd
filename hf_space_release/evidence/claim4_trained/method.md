# Claim 4 trained-checkpoint route

This route uses the complete CIFAR-10 training set and the full torchvision
ResNet-18 with a CIFAR 3x3 stem. It trains one deterministic epoch with SGD
(learning rate 0.1, momentum 0.9, weight decay 0.0005), batch size 128,
standard crop/flip augmentation, and standard CIFAR-10 normalization.

At the fixed resulting checkpoint, 8,192 held-out training examples approximate
the reference gradient and 128 disjoint batches provide gradient-error norms.
The primary tail count is fixed independently as `round(sqrt(n))`; counts
8, 16, 24, and 32 provide sensitivity checks. Four hundred bootstrap resamples
give a percentile interval. Known-theta synthetic distributions calibrate the
estimator, while the reciprocal parameter convention is the negative control.

The allocation estimate is 8 CPU cores on Hugging Face `cpu-upgrade`. The
budget was selected from Route 2's measured 40-pass runtime, before observing
this route's theta.
