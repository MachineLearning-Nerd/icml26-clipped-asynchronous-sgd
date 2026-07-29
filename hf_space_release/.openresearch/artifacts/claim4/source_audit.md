# Claim 4 source audit

Paper source: arXiv:2606.13287v1, retrieved from the ar5iv HTML on
2026-07-28 with SHA-256
`292ba2ce9a95e41279fe1535ffa23b720f18fb2139c3e26324138c0d4a0304ff`.

Definition 3.1 defines `X ~ subW(theta, sigma)` by
`E[exp((|X|/sigma)^(1/theta))] <= 2`; it identifies theta `1/2` with
sub-Gaussian and theta `1` with sub-exponential variables. Figure 1 and its
following paragraph state that norm gradient errors were measured while
training ResNet-18 on CIFAR-10 and that the Vladimirova et al. estimator gave
`theta = 2.71`.

The cited estimator regresses `log Y_(n-i+1,n)` on `log log(n/i)` over the
largest `k` of `n` positive observations. The cited source does not prescribe
`k` generally; its own neural-network illustration uses `n=100000, k=1000`.

The target paper does not state the training checkpoint, optimizer, batch size,
preprocessing, number of gradient-error samples, construction of the full
gradient, or `k`. Its linked code repository had zero commits and zero refs
when audited on 2026-07-28. Those omissions prevent an assumption-identical
reconstruction and prevent a numerical mismatch from being a falsification.
