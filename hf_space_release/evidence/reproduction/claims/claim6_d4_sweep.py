"""Complete one-seed D=4 hyperparameter sweep for Figure 4."""

from __future__ import annotations

import concurrent.futures
import json
import os
import time
from pathlib import Path

import numpy as np
from torchvision import datasets

from reproduction.claims import claim6_cifar_pilot as engine


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim6_d4_sweep"
SELECTION_SEED = 20260729
LEARNING_RATES = tuple(2.0**exponent for exponent in range(-9, 0))
CLIPPING_RADII = (0.5, 1.0, 2.0, 4.0)
CONFIGS = tuple(
    [
        engine.PilotConfig(f"vanilla_lr_2^{exponent}", 2.0**exponent, None)
        for exponent in range(-9, 0)
    ]
    + [
        engine.PilotConfig(
            f"clipped_lr_2^{exponent}_c{radius:g}",
            2.0**exponent,
            radius,
        )
        for exponent in range(-9, 0)
        for radius in CLIPPING_RADII
    ]
)


def select_best(
    configurations: list[dict[str, object]], method: str
) -> dict[str, object] | None:
    reached = [
        item
        for item in configurations
        if item["method"] == method and item["reached_target"]
    ]
    if not reached:
        return None
    return min(reached, key=lambda item: float(item["first_hit_time"]))


def main() -> int:
    started = time.perf_counter()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    engine.SEED = SELECTION_SEED
    engine.DELAY_FACTOR = 4
    engine.TIME_CAP = 8_000.0
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
        "route": "complete D=4 selection-seed hyperparameter sweep",
        "status": "PASS",
        "verdict": "BLOCKED",
        "reason": (
            "The entire paper hyperparameter domain and exact D=4 cap are "
            "covered, but D=8 and independent three-seed winner validation "
            "remain."
        ),
        "paper_protocol": {
            "dataset": "CIFAR-10",
            "clients": 16,
            "dirichlet_alpha": 0.5,
            "delay_factor": 4,
            "target_accuracy": 0.70,
            "time_cap": 8_000.0,
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
            "paper_speedup": 1.2,
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
    print(json.dumps({"event": "CLAIM6_D4_SWEEP_RAW", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
