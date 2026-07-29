# Claim 6 limitations and deviations

- The author implementation is unavailable, and the paper omits architecture,
  batch size, augmentation, exact partition allocation, evaluation cadence,
  and event tie-breaking.
- The reconstruction declares all of these choices and uses real CIFAR-10, but
  it cannot establish identity with the historical run.
- Three validation seeds give a discrete and low-powered interval.
- A mismatch is therefore BLOCKED evidence rather than FALSIFIED evidence.
- No GPU is used. Runtime is simulated time-to-target, matching the Figure 4
  horizontal axis, not host wall-clock time.
