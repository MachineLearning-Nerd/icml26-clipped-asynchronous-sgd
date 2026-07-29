# Claims 1–2 exact source audit

The source is the arXiv v1 LaTeX archive with SHA-256
`625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915`.
Theorem 4.2 is at `main.tex` lines 576–584 and Theorem 5.1 at lines
702–710. The shared appendix derivation is at lines 1046–1344.

Theorem 4.2 assumes global L-smoothness and lower boundedness, plus
conditionally unbiased norm-sub-Weibull gradient noise at every point. It is
universal over epsilon in `(0,1)` and existential over a step size constant
across iterations and a clipping radius. Theorem 5.1 additionally assumes
uniform squared gradient heterogeneity at most zeta squared and uses the
uniform worker scheduling in Algorithm 2.

Both are iteration/oracle-complexity claims. Soft-O suppresses logarithms and
fixed problem constants such as L, the initial optimality gap Delta, and
theta. Neither theorem contains maximum delay.
