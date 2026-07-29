# Claim 6 independent validation method

The selection seed was used once to run all 45 configurations for each delay.
This descendant locks the resulting method-specific winners and runs them on
three unseen seeds. Each seed changes model initialization, client partitions,
client minibatch streams, and the asynchronous schedule.

The experiment uses the paper's 16 workers, alpha 0.5 label skew, target 70%,
delay factors, caps, learning-rate domain, and clipping-radius domain. It uses
a declared 878,538-parameter two-convolution CIFAR-10 model, batch size 64,
channel normalization without augmentation, and deterministic event
simulation. Eight one-thread CPU processes execute the 12 trajectories.

For each delay, the point estimate is mean vanilla first-hit time divided by
mean clipped first-hit time. All `3^3=27` paired nonparametric seed resamples
are enumerated. Each resample also produces adverse lower and upper ratios
from the declared `[t-200,t]` observation interval; the combined 95% interval
uses the 2.5th percentile of lower ratios and the 97.5th percentile of upper
ratios. A censored trajectory prevents verification.
