# Constructive proof for the expectation theorems

Let `r_t = ||grad f(x_t)||`, let `Delta = f(x_0)-inf f`, and absorb only
theta-dependent constants into `K_theta`. Put

```text
W = K_theta sigma^2 + 2 zeta^2
H_c(r) = r^2                  when r <= c/2
         c r                  when r > c/2.
```

For Algorithm 1, scheduled gradients are unbiased because workers are
homogeneous. For Algorithm 2, reindex by scheduling time: the newly scheduled
worker is uniform after `x_t` is fixed, so the corresponding oracle is
conditionally unbiased for the global gradient. Completion order changes the
real iterate but not this virtual ordering. The initial active set contributes
at most `tau_C` clipped gradients before this uniform sequence; its
`eta*c*tau_C` transient is absorbed by the same virtual bound and deterministic
concurrency term. We write `Delta_bar=1+Delta` below to absorb this finite
prefix without changing any claimed epsilon, noise, or concurrency exponent.

At every time there are at most `tau_C` outstanding gradients and each is
clipped to norm `c`. Therefore

```text
||x_t - x_tilde_t|| <= eta c tau_C.
```

This counting statement contains no delay length.

## One conditional descent inequality

Smoothness, the virtual bound, and the clipping bias/moment bounds imply, for a
large enough theta-dependent constant `K`,

```text
E_t[f(x_tilde_{t+1})]-f(x_tilde_t)
 <= -(eta/8) H_c(r_t)
    + K eta B
    + K eta^2 L W
    + K eta^3 c^2 tau_C^2 L^2
    + K eta^2 L c^2,
```

where

```text
B = W exp(-((c-2 zeta)/(4 sigma))^(1/theta)).
```

For `r<=c/2`, this follows from the paper's small-gradient clipping-bias and
second-moment lemmas after taking `eta<=1/(4L)`.

For `c/2<r<=c`, nonexpansiveness gives squared gradient error at most `W`.
If `c^2>=8W`, then

```text
-r^2/2 + W/2 <= -r^2/4 <= -c r/8.
```

For `r>=c`, `alpha=c/r`, and the same condition gives

```text
-c r/2 + W r/(2c) <= -7 c r/16 <= -c r/8.
```

Thus the piecewise inequality holds pointwise before expectation. This avoids
the printed appendix's random-index-set notation. Taking unconditional
expectation and then summing every time index makes the function differences
 telescope with the correct sign. If `Q` denotes the resulting upper bound on
the average of `E H_c(r_t)`, Cauchy–Schwarz on the small region and direct
division by `c` on the large region give

```text
(1/T) sum_t E r_t <= sqrt(Q) + Q/c.
```

## Constructive parameters and inversion

For a requested `epsilon in (0,1)`, choose a sufficiently large finite safety
constant `K` depending only on the displayed descent constants and theta, and
let

```text
q = max(1, log(2+K W/epsilon^2)^theta)
c = epsilon + 2 zeta + 4 sigma q + sqrt(8W).
```

Then `c>=epsilon`, `c^2>=8W`, and

```text
B <= W/(2+K W/epsilon^2) <= epsilon^2/K.
```

Up to theta-dependent constants and logarithms,

```text
c = soft-O(epsilon + sigma + zeta)
c^2 = soft-O(epsilon^2 + sigma^2 + zeta^2).
```

Using the same sufficiently large safety constant, set

```text
R = epsilon^2 + (sigma^2+zeta^2) q^2
eta = min {
  1/(K tau_C L),
  epsilon^2/(K L R),
  epsilon/(K c tau_C L)
}
T = ceil(K Delta_bar/(eta epsilon^2))+tau_C+1.
```

Every term in `Q` is then at most a chosen constant fraction of
`epsilon^2`; hence `Q<=epsilon^2/16`. Since `c>=epsilon`,
`sqrt(Q)+Q/c <= 5epsilon/16 < epsilon`.

Expanding `1/eta` in the horizon gives

```text
T = soft-O(
  tau_C L Delta_bar / epsilon^2
  + (sigma^2+zeta^2) L Delta_bar / epsilon^4
  + (sigma+zeta) tau_C L Delta_bar / epsilon^3
).
```

Suppressing fixed `L`, `Delta`, and theta gives Theorem 5.1. Setting
`zeta=0` gives Theorem 4.2. No step uses `tau_max`.
