# Command and compute ledger

The fixed reproduction command on every experiment node was:

```bash
uv run --frozen python -m reproduction.run
```

The authoritative cumulative launch was:

```bash
orx exp run 519e789e-3d8b-4d84-a339-e458f89aaf99 --backend local
```

It produced run `9388b95f-c7ac-4e84-b7c7-e14649b2a89f` at Git
`cf23e2e84f931be528724d7720df3dec5127bf88`, with 17/17 verifiers passing
in 33.508039 seconds. The process was single-process local CPU; the host
reported eight logical CPUs and no GPU was visible.

All long or uncertain empirical runs used the same fixed command through:

```bash
orx exp run <experiment-id> --backend hf --flavor cpu-upgrade
```

Important HF runs and observed wall time:

| Run | Purpose | Runtime |
| --- | --- | ---: |
| `512fbeef-0db3-44ec-81e8-7fcba10ba53e` | Claim 4 initialized ResNet-18 route | 34m52s, backend timeout after complete payload |
| `087a41fe-9747-4e48-a07a-e82cd5f18596` | Claim 4 mirror route | 1m51s |
| `267469d5-fea2-4a78-abb6-a7bea32e0fef` | Claim 4 trained checkpoint route | 15m33s |
| `01c2ea2c-e315-4b8b-aa1d-fa97b0c3c884` | Claim 6 D4 sweep | 2h31m |
| `f745ef3e-873c-4da4-aa4f-77db0602f75f` | Claim 6 D8 sweep | 2h19m |
| `05a78a25-3032-47d1-8862-653c211b3c9b` | Claim 6 three-seed validation | 40m43s |

Relevant HF CPU routes total approximately 6h23m59s in the table above.
Pilot and failed calibration routes add approximately 44m07s, for about
7h08m06s total campaign HF wall time. The selected flavor exposed eight CPUs
through its cgroup. Hugging Face billing cost was not exposed in the `orx`
run records, so no dollar amount is invented. Local compute cost is recorded
as USD 0.

Source retrieval used an explicit browser User-Agent and recorded its URL,
date, and hashes in `../provenance/retrieval.json`. Publication uses the exact
paths in `hf_space_release/UPLOAD_ALLOWLIST.txt` through one Hugging Face
text-file API commit to the existing Space only.
