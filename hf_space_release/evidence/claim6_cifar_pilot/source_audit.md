# Claim 6 source audit

Paper anchors `#S5`, `#S6`, and `#S6.F4` specify:

- Algorithm 2 uniformly samples the next worker from all workers and permits
  multiple queued computations on one worker.
- There are 16 simulated workers at full concurrency; eight take one time
  unit and eight take `D` time units, for `D` in `{4,8}`.
- Results average three seeds.
- CIFAR-10 is partitioned by a Dirichlet label distribution with `alpha=0.5`.
- The model is a two-layer CNN.
- Learning rates are every power of two from `2^-9` through `2^-1`; clipping
  radii are `{0.5,1,2,4}`.
- The target is 70% test accuracy and the caps are 8,000 (`D=4`) and 12,000
  (`D=8`) time units.
- Figure 4 reports 1.2x and 1.3x speedups over vanilla ASGD.

The paper does not identify the CNN channel widths, batch size, preprocessing,
evaluation cadence, exact partition implementation, seeds, or executable code
revision. The linked public repository has no refs or commits as audited on
2026-07-29.
