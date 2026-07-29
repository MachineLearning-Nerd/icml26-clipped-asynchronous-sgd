# Claim 6 real CIFAR-10 pilot

This calibration implements the paper-specified CIFAR-10 dataset, 16 clients,
class-wise Dirichlet label split with `alpha=0.5`, fixed fast/slow service
times, and Algorithm 2 uniform worker resampling with per-worker FIFO queues.
A scheduled gradient is computed from the model snapshot sent at scheduling
time and applied only at its simulated completion time.

The paper omits the exact CNN, batch size, preprocessing, partition code, and
evaluation cadence. The pilot uses a common federated two-convolution CNN,
batch size 64, CIFAR channel normalization without augmentation, and
evaluation every 100 simulated time units.

This route deliberately tests only one seed, `D=4`, and three configurations
through time 3,200. It calibrates feasibility and learning behavior before the
complete paper-domain sweep; it cannot verify the reported speedup.
