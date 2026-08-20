# Reproduction environment

The committed release candidate records the following environment:

- Fixed command: `uv run --frozen python -m reproduction.run`
- Python: `3.12.11`
- Pinned dependency lock: [`uv.lock`](uv.lock), SHA-256 `088087f86a36731bb34896bf76bb1a4f4461c23f4a1526f075ff80c25a99c2bb`
- Formal release image: `ghcr.io/astral-sh/uv:0.11.29-python3.12-trixie-slim`
- Scientific formal run: one process, one estimated core, no GPU, 33.508039 seconds
- Claim 4 and Claim 6 reconstruction routes: Hugging Face `cpu-upgrade`, with their per-route seeds, runtime, and protocol metadata recorded in the raw artifacts

The release candidate has 17 verifier exit codes equal to zero, a 373-file allowlist, a 372-file manifest, three negative controls, and zero secret-scan findings. The old judged snapshot is protected by the immutable Space revision `471748694e91b08b071d3d13c30d84b3091b5971`.

These checks validate the committed evidence and release structure. They do not recreate the authors’ unavailable historical checkpoints or claim that a replacement training run is the same realization.
