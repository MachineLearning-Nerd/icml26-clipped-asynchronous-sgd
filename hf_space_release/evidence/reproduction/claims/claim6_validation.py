"""Independent three-seed validation of the selected Figure 4 winners."""

from __future__ import annotations

import concurrent.futures
import itertools
import json
import multiprocessing
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from torchvision import datasets

from reproduction.claims import claim6_cifar_pilot as engine


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim6_validation"
VALIDATION_SEEDS = (20260730, 20260731, 20260732)
EVALUATION_INTERVAL = 200.0
TARGET_ACCURACY = 0.70
PAPER_SPEEDUPS = {4: 1.2, 8: 1.3}


@dataclass(frozen=True)
class ValidationTask:
    seed: int
    delay_factor: int
    time_cap: float
    config: engine.PilotConfig


WINNERS = {
    4: {
        "vanilla": engine.PilotConfig("vanilla_lr_2^-5", 2.0**-5, None),
        "clipped": engine.PilotConfig("clipped_lr_2^-5_c4", 2.0**-5, 4.0),
    },
    8: {
        "vanilla": engine.PilotConfig("vanilla_lr_2^-6", 2.0**-6, None),
        "clipped": engine.PilotConfig("clipped_lr_2^-5_c4", 2.0**-5, 4.0),
    },
}
TIME_CAPS = {4: 8_000.0, 8: 12_000.0}


def run_task(task: ValidationTask) -> dict[str, object]:
    """Run one preregistered winner with task-local deterministic globals."""
    engine.SEED = task.seed
    engine.DELAY_FACTOR = task.delay_factor
    engine.TIME_CAP = task.time_cap
    engine.EVAL_INTERVAL = EVALUATION_INTERVAL
    engine.PROCESS_WORKERS = 8
    engine.THREADS_PER_PROCESS = 1
    result = engine.run_config(task.config)
    result["validation_seed"] = task.seed
    result["delay_factor"] = task.delay_factor
    return result


def percentile(values: list[float], quantile: float) -> float:
    return float(np.percentile(np.asarray(values), quantile, method="linear"))


def aggregate_delay(
    configurations: list[dict[str, object]], delay_factor: int
) -> dict[str, object]:
    selected = [
        item for item in configurations if item["delay_factor"] == delay_factor
    ]
    by_method = {
        method: sorted(
            [item for item in selected if item["method"] == method],
            key=lambda item: int(item["validation_seed"]),
        )
        for method in ("vanilla", "clipped")
    }
    all_reached = all(
        bool(item["reached_target"])
        for method_items in by_method.values()
        for item in method_items
    )
    result: dict[str, object] = {
        "delay_factor": delay_factor,
        "paper_speedup": PAPER_SPEEDUPS[delay_factor],
        "all_targets_reached": all_reached,
        "first_hit_times": {
            method: [item["first_hit_time"] for item in items]
            for method, items in by_method.items()
        },
        "censored_seeds": {
            method: [
                item["validation_seed"]
                for item in items
                if not item["reached_target"]
            ]
            for method, items in by_method.items()
        },
    }
    if not all_reached:
        result.update(
            {
                "mean_first_hit_time": None,
                "observed_speedup": None,
                "paired_seed_speedups": None,
                "bootstrap_resamples": 0,
                "combined_95_interval": None,
                "positive_effect_95": False,
                "paper_value_in_95_interval": False,
                "supports_caption": False,
            }
        )
        return result

    vanilla = [float(item["first_hit_time"]) for item in by_method["vanilla"]]
    clipped = [float(item["first_hit_time"]) for item in by_method["clipped"]]
    point_ratios: list[float] = []
    lower_ratios: list[float] = []
    upper_ratios: list[float] = []
    for indices in itertools.product(range(len(VALIDATION_SEEDS)), repeat=3):
        sampled_vanilla = [vanilla[index] for index in indices]
        sampled_clipped = [clipped[index] for index in indices]
        point_ratios.append(
            statistics.fmean(sampled_vanilla)
            / statistics.fmean(sampled_clipped)
        )
        lower_ratios.append(
            statistics.fmean(
                max(value - EVALUATION_INTERVAL, 0.0)
                for value in sampled_vanilla
            )
            / statistics.fmean(sampled_clipped)
        )
        upper_ratios.append(
            statistics.fmean(sampled_vanilla)
            / statistics.fmean(
                max(value - EVALUATION_INTERVAL, 1e-12)
                for value in sampled_clipped
            )
        )
    combined_interval = [
        percentile(lower_ratios, 2.5),
        percentile(upper_ratios, 97.5),
    ]
    speedup = statistics.fmean(vanilla) / statistics.fmean(clipped)
    paper_speedup = PAPER_SPEEDUPS[delay_factor]
    positive = combined_interval[0] > 1.0
    paper_in_interval = combined_interval[0] <= paper_speedup <= combined_interval[1]
    result.update(
        {
            "mean_first_hit_time": {
                "vanilla": statistics.fmean(vanilla),
                "clipped": statistics.fmean(clipped),
            },
            "observed_speedup": speedup,
            "paired_seed_speedups": [
                vanilla[index] / clipped[index]
                for index in range(len(VALIDATION_SEEDS))
            ],
            "bootstrap_resamples": len(point_ratios),
            "bootstrap_point_95_interval": [
                percentile(point_ratios, 2.5),
                percentile(point_ratios, 97.5),
            ],
            "combined_95_interval": combined_interval,
            "positive_effect_95": positive,
            "paper_value_in_95_interval": paper_in_interval,
            "supports_caption": positive and paper_in_interval,
        }
    )
    return result


def main() -> int:
    started = time.perf_counter()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data_root = Path(os.environ.get("HF_HOME", "/tmp")) / "openresearch-cifar10"
    datasets.CIFAR10.url = engine.CIFAR_HF_MIRROR
    train = datasets.CIFAR10(root=data_root, train=True, download=True)
    test = datasets.CIFAR10(root=data_root, train=False, download=True)
    engine.TRAIN_IMAGES = train.data
    engine.TRAIN_LABELS = np.asarray(train.targets, dtype=np.int64)
    engine.TEST_IMAGES = test.data
    engine.TEST_LABELS = np.asarray(test.targets, dtype=np.int64)

    partition_audits: dict[str, dict[str, object]] = {}
    for seed in VALIDATION_SEEDS:
        engine.SEED = seed
        partition_audits[str(seed)] = engine.partition_audit(engine.TRAIN_LABELS)

    tasks = [
        ValidationTask(
            seed=seed,
            delay_factor=delay,
            time_cap=TIME_CAPS[delay],
            config=WINNERS[delay][method],
        )
        for seed in VALIDATION_SEEDS
        for delay in (4, 8)
        for method in ("vanilla", "clipped")
    ]
    context = multiprocessing.get_context("fork")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=8, mp_context=context
    ) as executor:
        configurations = list(executor.map(run_task, tasks))

    aggregates = {
        str(delay): aggregate_delay(configurations, delay) for delay in (4, 8)
    }
    integrity_passed = (
        len(configurations) == 12
        and all(
            audit["all_examples_assigned_exactly_once"]
            for audit in partition_audits.values()
        )
        and all(item["initial_accuracy"] < TARGET_ACCURACY for item in configurations)
    )
    captions_supported = all(
        bool(aggregates[str(delay)]["supports_caption"]) for delay in (4, 8)
    )
    verdict = "VERIFIED" if integrity_passed and captions_supported else "BLOCKED"
    reason = (
        "Both caption values and a positive clipping effect are inside the "
        "preregistered combined 95% intervals."
        if verdict == "VERIFIED"
        else "At least one caption contract is not resolved by the independent "
        "three-seed reconstruction; absent the authors' implementation and "
        "omitted protocol choices, this is not a valid falsification."
    )
    result = {
        "schema_version": 1,
        "claim_number": 6,
        "route": "independent three-seed validation of selection-seed winners",
        "status": "PASS" if integrity_passed else "FAIL",
        "verdict": verdict,
        "reason": reason,
        "exact_claim": (
            "On label-skew CIFAR-10, Clipped ASGD improves time to 70% test "
            "accuracy over vanilla ASGD by 1.2x at D=4 and 1.3x at D=8."
        ),
        "validation_seeds": list(VALIDATION_SEEDS),
        "selection_provenance": {
            "selection_seed": 20260729,
            "D4_raw_sha256": (
                "f9d36093629b4966bec95323d3df6750ba78af2d5ffd16a0c7330d9a6a16082d"
            ),
            "D8_raw_sha256": (
                "3eca3f394b17488f325ac57368b9abb11c50b9e62c716d9b9d6fe4485a83ddf9"
            ),
            "winners": {
                str(delay): {
                    method: {
                        "name": config.name,
                        "learning_rate": config.learning_rate,
                        "clipping_radius": config.clipping_radius,
                    }
                    for method, config in methods.items()
                }
                for delay, methods in WINNERS.items()
            },
        },
        "protocol": {
            "dataset": "CIFAR-10",
            "clients": 16,
            "dirichlet_alpha": 0.5,
            "target_accuracy": TARGET_ACCURACY,
            "evaluation_interval_time_units": EVALUATION_INTERVAL,
            "time_caps": {str(key): value for key, value in TIME_CAPS.items()},
            "uncertainty": (
                "Exact paired nonparametric bootstrap over all 3^3 seed "
                "resamples; interval endpoints also take the adverse side of "
                "the 200-time-unit first-hit observation interval."
            ),
        },
        "partition_audits": partition_audits,
        "negative_control": {
            "name": "untrained initialization",
            "all_below_target": all(
                item["initial_accuracy"] < TARGET_ACCURACY
                for item in configurations
            ),
            "accuracies": [
                {
                    "seed": item["validation_seed"],
                    "delay_factor": item["delay_factor"],
                    "method": item["method"],
                    "accuracy": item["initial_accuracy"],
                }
                for item in configurations
            ],
        },
        "configurations": configurations,
        "aggregates": aggregates,
        "limitations": [
            "The paper does not specify the CNN architecture, batch size, data "
            "augmentation, exact Dirichlet allocation implementation, or event "
            "tie-breaking; these are declared reconstruction choices.",
            "Three validation seeds give a discrete, low-powered uncertainty interval.",
            "A mismatch under this reconstruction cannot falsify the paper's "
            "historical experiment.",
        ],
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
    print(
        json.dumps(
            {"event": "CLAIM6_VALIDATION_RAW", "result": result}, sort_keys=True
        )
    )
    return 0 if integrity_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
