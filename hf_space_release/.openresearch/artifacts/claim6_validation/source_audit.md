# Claim 6 source audit

Figure 4 and its caption state that the experiment uses CIFAR-10 distributed
across 16 workers with label heterogeneity from a Dirichlet distribution with
alpha 0.5. The text reports the time to 70% test accuracy and characterizes
Clipped ASGD's improvement over ASGD as 1.2x at delay factor 4 and 1.3x at
delay factor 8. The paper sweep is learning rates `2^k`, `k=-9,...,-1`, and
clipping radii `{0.5,1,2,4}`; time caps are 8,000 and 12,000 respectively.

The source does not provide the implementation, CNN architecture, batch size,
augmentation, exact class-wise Dirichlet allocation procedure, evaluation
cadence, or event tie-breaking. These omissions are material, so a divergent
reconstruction is not an assumption-satisfying falsification of the historical
experiment.
