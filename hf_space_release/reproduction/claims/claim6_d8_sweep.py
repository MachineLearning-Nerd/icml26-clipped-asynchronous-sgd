"""Complete one-seed D=8 hyperparameter sweep for Figure 4."""

from __future__ import annotations

import concurrent.futures
import json
import os
import time
from pathlib import Path

import numpy as np
from torchvision import datasets

from reproduction.claims import claim6_cifar_pilot as engine
from reproduction.claims.claim6_d4_sweep import (
    CLIPPING_RADII,
    CONFIGS,
    LEARNING_RATES,
    SELECTION_SEED,
    select_best,
)


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim6_d8_sweep"


def main() -> int:
    started = time.perf_counter()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    engine.SEED = SELECTION_SEED
    engine.DELAY_FACTOR = 8
    engine.TIME_CAP = 12_000.0
    engine.EVAL_INTERVAL = 200.0
    engine.PROCESS_WORKERS = 8
    engine.THREADS_PER_PROCESS = 1
    engine.CONFIGS = CONFIGS
    data_root = Path(os.environ.get("HF_HOME", "/tmp")) / "openresearch-cifar10"
    datasets.CIFAR10.url = engine.CIFAR_HF_MIRROR
    train = datasets.CIFAR10(root=data_root, train=True, download=True)
    test = datasets.CIFAR10(root=data_root, train=False, download=True)
    engine.TRAIN_IMAGES = train.data
    engine.TRAIN_LABELS = np.asarray(train.targets, dtype=np.int64)
    engine.TEST_IMAGES = test.data
    engine.TEST_LABELS = np.asarray(test.targets, dtype=np.int64)
    partition = engine.partition_audit(engine.TRAIN_LABELS)
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        configurations = list(executor.map(engine.run_config, CONFIGS))
    best_vanilla = select_best(configurations, "vanilla")
    best_clipped = select_best(configurations, "clipped")
    speedup = None
    if best_vanilla is not None and best_clipped is not None:
        speedup = float(best_vanilla["first_hit_time"]) / float(
            best_clipped["first_hit_time"]
        )
    result = {
        "schema_version": 1,
        "claim_number": 6,
        "route": "complete D=8 selection-seed hyperparameter sweep",
        "status": "PASS",
        "verdict": "BLOCKED",
        "reason": (
            "Both delay-factor selection grids are complete, but independent "
            "three-seed winner validation remains."
        ),
        "paper_protocol": {
            "dataset": "CIFAR-10",
            "clients": 16,
            "dirichlet_alpha": 0.5,
            "delay_factor": 8,
            "target_accuracy": 0.70,
            "time_cap": 12_000.0,
            "learning_rates": list(LEARNING_RATES),
            "clipping_radii": list(CLIPPING_RADII),
        },
        "selection_protocol": {
            "seed": SELECTION_SEED,
            "evaluation_interval_time_units": 200.0,
            "first_hit_uncertainty_time_units": 200.0,
            "non_circularity": (
                "All 45 paper-domain configurations run to target or the exact "
                "paper cap; no configuration is pruned from formula-derived data."
            ),
        },
        "reconstruction_choices_missing_from_paper": {
            "architecture": "Conv5x5(3,32)-pool-Conv5x5(32,64)-pool-FC512-FC10",
            "batch_size": 64,
            "preprocessing": "CIFAR channel normalization; no augmentation",
            "partition_implementation": "class-wise Dirichlet allocation",
        },
        "partition_audit": partition,
        "negative_control": {
            "name": "untrained initialization",
            "accuracy": configurations[0]["initial_accuracy"],
            "target": 0.70,
            "target_rejected": configurations[0]["initial_accuracy"] < 0.70,
        },
        "configurations": configurations,
        "selection": {
            "best_vanilla": best_vanilla,
            "best_clipped": best_clipped,
            "observed_speedup": speedup,
            "paper_speedup": 1.3,
            "paper_value_testable": speedup is not None,
        },
        "compute": {
            "estimated_cores": 8,
            "processes": 8,
            "threads_per_process": 1,
            "selected_backend": "hf",
            "selected_flavor": "cpu-upgrade",
            "gpu_allowed": False,
        },
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    raw = ARTIFACT_DIR / "raw_output.json"
    raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "CLAIM6_D8_SWEEP_RAW", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
