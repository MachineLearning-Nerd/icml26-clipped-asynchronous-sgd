# Claim 6 D=4 source audit

Figure 4 requires real CIFAR-10, 16 heterogeneous clients, a
Dirichlet(`alpha=0.5`) label split, a two-layer CNN, uniform queued worker
sampling, the nine learning rates `2^-9` through `2^-1`, clipping radii
`{0.5,1,2,4}`, a 70% test target, and an 8,000-time-unit cap at `D=4`.

The paper reports a 1.2x minimum-time improvement over vanilla. It does not
specify the CNN widths, batch size, preprocessing, evaluation cadence, random
seeds, partition code, or a usable author-code revision.
