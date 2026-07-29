# Claim 4 pilot method

The bounded pilot downloads the real CIFAR-10 training split and instantiates
torchvision ResNet-18 with the conventional CIFAR stem (3x3 stride-one
convolution and no max-pool). At the deterministic initialization checkpoint,
it computes a reference gradient over 2,048 examples and 24 independent
mini-batch gradients of size 128. Each scalar observation is the Euclidean norm
of a mini-batch gradient minus the reference gradient.

The primary estimate uses the largest one third of the observations. A
tail-fraction sensitivity table and a seeded nonparametric bootstrap are
reported. A calibration control draws 100,000 observations from Weibull laws
with known paper-parameter theta values `0.5`, `1.0`, and `2.71`; the same
estimator must recover each within absolute error `0.18`.
As a negative control, the common reciprocal shape-parameter convention is
deliberately applied to the `theta=2.71` sample and must be rejected by the
same threshold.

This is an executable protocol calibration, not full evidence for Figure 1.
Its fixed command is `uv run --frozen python -m reproduction.run`.
