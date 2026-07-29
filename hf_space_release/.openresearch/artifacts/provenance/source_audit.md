# Paper source and exact claim anchors

Retrieved on 2026-07-28 from
`https://ar5iv.labs.arxiv.org/html/2606.13287` with the explicit User-Agent
recorded in `retrieval.json`. The 601,926-byte HTML has SHA-256
`292ba2ce9a95e41279fe1535ffa23b720f18fb2139c3e26324138c0d4a0304ff`.
The source identifies itself as arXiv:2606.13287v1 (11 June 2026).

## Shared assumptions

- Assumption 3.1, anchor `#S3.Thmtheorem1`: the objective is globally
  L-smooth on R^d and bounded below.
- Definition 3.1, anchor `#S3.Thmthm1`: X is sub-Weibull when positive sigma
  and theta exist with E exp((|X|/sigma)^(1/theta)) <= 2. The paper's
  parameterization makes theta=1/2 sub-Gaussian and theta=1 sub-exponential.
- Assumption 3.2, anchor `#S3.Thmtheorem2`: every worker's stochastic
  gradient is unbiased and the norm of its noise is sub-Weibull for every
  x in R^d.
- Assumption 5.1, anchor `#S5.Thmtheorem1`: every worker objective has
  uniformly bounded gradient heterogeneity,
  ||grad f_i(x) - grad f(x)||^2 <= zeta^2 for every x in R^d.

## Theorem anchors and quantifiers

- Theorem 4.2, `#S4.Thmthm2`: under Assumptions 3.1–3.2, there exist a
  constant step size and clipping radius such that for every epsilon in
  (0,1), Algorithm 1 attains average expected gradient norm <= epsilon in
  soft-O(sigma^2/epsilon^4 + sigma*tau_C/epsilon^3 +
  tau_C/epsilon^2) iterations. This is an existential, asymptotic,
  universally epsilon-quantified theorem; finite experiments can only
  corroborate it.
- Theorem 4.3, `#S4.Thmthm3`: under the same assumptions, there exist a
  constant step size and clipping radius such that for every epsilon and
  delta in (0,1), the average gradient norm is <= epsilon with probability
  at least 1-delta within the stated soft-O rate containing
  log^(2 theta)(1/delta) and log^theta(1/delta).
- Theorem 5.1, `#S5.Thmthm1`: under Assumptions 3.1, 3.2, and 5.1, Algorithm
  2 has the heterogeneous expectation rate
  soft-O((sigma^2+zeta^2)/epsilon^4 +
  (sigma+zeta)*tau_C/epsilon^3 + tau_C/epsilon^2).
- Theorem 5.2, `#S5.Thmthm2`: the corresponding heterogeneous
  high-probability statement is universally quantified over epsilon and
  delta in (0,1).

## Empirical anchors

- Figure 1, `#S3.F1`: ResNet-18/CIFAR-10 gradient-error norms are compared
  with simulated sub-Weibull samples; the reported fitted theta is 2.71.
  The training checkpoint, batch construction, sample count, and fitting
  implementation are not specified in the paper.
- Section 6, `#S6`: 16 simulated workers, full concurrency, half with unit
  compute time and half with delay D in {4,8}; three seeds and 2-sigma error
  bars.
- Figure 2, `#S6.F2`: ResNet-18/CIFAR-10, learning rates 2^-9 through 2^-1,
  80% test-accuracy target, 4,000-time-unit cap. The paper reports a minimum
  1.8x speedup over vanilla ASGD.
- Figure 3, `#S6.F3`: Shakespeare LSTM with dropout 0.2, learning rates 2^-3
  through 2^3, perplexity-5 target, 4,000-time-unit cap. Against vanilla,
  the exact reported speedups are 1.8x at D=4 and 2.0x at D=8. The 2.1x and
  2.2x values are comparisons with delay-adaptive ASGD.
- Figure 4, `#S6.F4`: CIFAR-10 split among workers by a Dirichlet label
  distribution with alpha=0.5, a two-layer CNN, learning rates 2^-9 through
  2^-1, a 70% target, and caps of 8,000 (D=4) and 12,000 (D=8). Reported
  speedup over vanilla is 1.2x and 1.3x respectively.

## Missing capability

Section 6 links `https://github.com/samericks/clipped-asgd`, but the public
repository had size zero, no commits, and no refs when audited on 2026-07-28.
The empirical contracts must therefore distinguish paper-specified settings
from reconstruction choices, and cannot silently assert bit-for-bit identity
with unavailable author code.

