# Claim 6 falsification source audit

The exact source is the arXiv v1 LaTeX archive with SHA-256
`625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915`.
Lines 758–769 specify 16 workers, half unit-speed and half delayed by D in
`{4,8}`, full concurrency, three seeds, and 2-sigma bars. Figure 4 and its
surrounding source at lines 851–910 specify CIFAR-10, Dirichlet alpha 0.5,
a two-layer CNN, learning-rate and clipping-radius sweeps, 70% target, caps,
and the 1.2x/1.3x caption values.

The two source figure hashes are
`122860beeff322b8f7fb1d1800220ee4eeb0a148404279f7de583c30abaa6551`
for D=4 and
`a3541e5245c696cf19c775454357eef24238528ea1fb386919bd632438fee26f`
for D=8. They contain rendered curves, not original numerical tables.

The linked author repository had no commits or refs during the campaign audit.
The architecture parameters, batch and preprocessing, partition sampler,
seeds, event handling, evaluation cadence, and curve aggregation needed for
identity are therefore unavailable.
