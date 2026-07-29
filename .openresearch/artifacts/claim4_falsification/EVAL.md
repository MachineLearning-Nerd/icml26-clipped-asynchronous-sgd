# Claim 4 final route evaluator note

The target falsification did not succeed. Real CIFAR-10/ResNet-18
reconstructions contradict `2.71` numerically, but none can be shown to use the
authors' unpublished checkpoint and measurement protocol. The positive and
true-value controls show that the decision rule is discriminative.

After initialization, trained-checkpoint, exhaustive-estimator, and dedicated
falsification routes, the honest terminal verdict is **BLOCKED**. The concrete
unblocker is the author checkpoint/raw norms and exact sampling/fit protocol.
