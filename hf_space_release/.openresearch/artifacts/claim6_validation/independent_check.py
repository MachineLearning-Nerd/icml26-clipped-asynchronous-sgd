"""Independent Claim 6 validation checker; does not import experiment code."""

from __future__ import annotations

import itertools
import json
import statistics
from pathlib import Path

import numpy as np


RAW = Path(__file__).with_name("raw_output.json")
SEEDS = [20260730, 20260731, 20260732]
INTERVAL = 200.0
PAPER = {4: 1.2, 8: 1.3}
EXPECTED = {
    (4, "vanilla"): ("vanilla_lr_2^-5", 2.0**-5, None, 8_000.0),
    (4, "clipped"): ("clipped_lr_2^-5_c4", 2.0**-5, 4.0, 8_000.0),
    (8, "vanilla"): ("vanilla_lr_2^-6", 2.0**-6, None, 12_000.0),
    (8, "clipped"): ("clipped_lr_2^-5_c4", 2.0**-5, 4.0, 12_000.0),
}


def percentile(values: list[float], quantile: float) -> float:
    return float(np.percentile(np.asarray(values), quantile, method="linear"))


def recompute(configurations: list[dict], delay: int) -> dict:
    groups = {
        method: sorted(
            [
                item
                for item in configurations
                if item["delay_factor"] == delay and item["method"] == method
            ],
            key=lambda item: item["validation_seed"],
        )
        for method in ("vanilla", "clipped")
    }
    all_reached = all(
        item["reached_target"] for items in groups.values() for item in items
    )
    if not all_reached:
        return {
            "all_reached": False,
            "speedup": None,
            "combined_interval": None,
            "supports": False,
        }
    vanilla = [float(item["first_hit_time"]) for item in groups["vanilla"]]
    clipped = [float(item["first_hit_time"]) for item in groups["clipped"]]
    lower: list[float] = []
    upper: list[float] = []
    for indices in itertools.product(range(3), repeat=3):
        sample_v = [vanilla[index] for index in indices]
        sample_c = [clipped[index] for index in indices]
        lower.append(
            statistics.fmean(max(value - INTERVAL, 0.0) for value in sample_v)
            / statistics.fmean(sample_c)
        )
        upper.append(
            statistics.fmean(sample_v)
            / statistics.fmean(max(value - INTERVAL, 1e-12) for value in sample_c)
        )
    combined = [percentile(lower, 2.5), percentile(upper, 97.5)]
    speedup = statistics.fmean(vanilla) / statistics.fmean(clipped)
    supports = combined[0] > 1.0 and combined[0] <= PAPER[delay] <= combined[1]
    return {
        "all_reached": True,
        "speedup": speedup,
        "combined_interval": combined,
        "supports": supports,
    }


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    configurations = result["configurations"]
    errors: list[str] = []
    if result["validation_seeds"] != SEEDS:
        errors.append("validation seed contract mismatch")
    if len(configurations) != 12:
        errors.append("expected exactly 12 validation trajectories")
    observed_keys = [
        (item["validation_seed"], item["delay_factor"], item["method"])
        for item in configurations
    ]
    expected_keys = [
        (seed, delay, method)
        for seed in SEEDS
        for delay in (4, 8)
        for method in ("vanilla", "clipped")
    ]
    if sorted(observed_keys) != sorted(expected_keys):
        errors.append("validation task Cartesian product mismatch")
    for item in configurations:
        expected = EXPECTED[(item["delay_factor"], item["method"])]
        observed = (
            item["name"],
            item["learning_rate"],
            item["clipping_radius"],
            item["time_cap"],
        )
        if observed != expected:
            errors.append(f"winner/cap mismatch for {observed_keys}")
        if item["target_accuracy"] != 0.70:
            errors.append("target accuracy mismatch")
        if item["reached_target"] != (item["first_hit_time"] is not None):
            errors.append("first-hit censoring mismatch")
        if item["reached_target"] and item["max_evaluated_accuracy"] < 0.70:
            errors.append("invalid target hit")
        if item["initial_accuracy"] >= 0.70:
            errors.append("untrained negative control reached the target")
    if not all(
        audit["all_examples_assigned_exactly_once"]
        for audit in result["partition_audits"].values()
    ):
        errors.append("a label-skew partition failed integrity")

    recomputed = {delay: recompute(configurations, delay) for delay in (4, 8)}
    for delay in (4, 8):
        recorded = result["aggregates"][str(delay)]
        check = recomputed[delay]
        if recorded["all_targets_reached"] != check["all_reached"]:
            errors.append(f"D={delay} target aggregation mismatch")
        if recorded["observed_speedup"] != check["speedup"]:
            errors.append(f"D={delay} speedup aggregation mismatch")
        if recorded["combined_95_interval"] != check["combined_interval"]:
            errors.append(f"D={delay} uncertainty interval mismatch")
        if recorded["supports_caption"] != check["supports"]:
            errors.append(f"D={delay} caption decision mismatch")
    expected_verdict = (
        "VERIFIED"
        if all(recomputed[delay]["supports"] for delay in (4, 8))
        else "BLOCKED"
    )
    if result["verdict"] != expected_verdict:
        errors.append("terminal verdict is inconsistent with contract")
    if result["status"] != "PASS":
        errors.append("scientific run integrity did not pass")
    print(
        json.dumps(
            {
                "event": "CLAIM6_VALIDATION_INDEPENDENT_CHECK",
                "status": "PASS" if not errors else "FAIL",
                "recomputed": recomputed,
                "expected_verdict": expected_verdict,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
