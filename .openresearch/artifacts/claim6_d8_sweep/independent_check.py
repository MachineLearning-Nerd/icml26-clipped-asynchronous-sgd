"""Independent checker for the complete D=8 selection sweep."""

from __future__ import annotations

import json
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")
LEARNING_RATES = [2.0**exponent for exponent in range(-9, 0)]
CLIPPING_RADII = [0.5, 1.0, 2.0, 4.0]


def best(configurations: list[dict[str, object]], method: str) -> dict | None:
    reached = [
        item
        for item in configurations
        if item["method"] == method and item["reached_target"]
    ]
    if not reached:
        return None
    return min(reached, key=lambda item: float(item["first_hit_time"]))


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    protocol = result["paper_protocol"]
    if (
        protocol["delay_factor"] != 8
        or protocol["time_cap"] != 12_000.0
        or protocol["target_accuracy"] != 0.70
        or protocol["learning_rates"] != LEARNING_RATES
        or protocol["clipping_radii"] != CLIPPING_RADII
    ):
        errors.append("paper-domain mismatch")
    configurations = result["configurations"]
    vanilla = [item for item in configurations if item["method"] == "vanilla"]
    clipped = [item for item in configurations if item["method"] == "clipped"]
    if len(configurations) != 45 or len(vanilla) != 9 or len(clipped) != 36:
        errors.append("configuration grid is incomplete")
    if sorted(item["learning_rate"] for item in vanilla) != LEARNING_RATES:
        errors.append("vanilla learning-rate domain is incomplete")
    clipped_domain = sorted(
        (item["learning_rate"], item["clipping_radius"]) for item in clipped
    )
    expected_clipped = sorted(
        (learning_rate, radius)
        for learning_rate in LEARNING_RATES
        for radius in CLIPPING_RADII
    )
    if clipped_domain != expected_clipped:
        errors.append("clipped Cartesian domain is incomplete")
    for item in configurations:
        if item["time_cap"] != 12_000.0 or item["target_accuracy"] != 0.70:
            errors.append(f"{item['name']} resource/target mismatch")
        if item["oracle_calls"] <= 0:
            errors.append(f"{item['name']} has no oracle calls")
        if item["reached_target"] != (item["first_hit_time"] is not None):
            errors.append(f"{item['name']} first-hit flag mismatch")
        if item["reached_target"] and item["max_evaluated_accuracy"] < 0.70:
            errors.append(f"{item['name']} invalid target hit")
    computed_vanilla = best(configurations, "vanilla")
    computed_clipped = best(configurations, "clipped")
    recorded = result["selection"]
    if computed_vanilla != recorded["best_vanilla"]:
        errors.append("best vanilla selection mismatch")
    if computed_clipped != recorded["best_clipped"]:
        errors.append("best clipped selection mismatch")
    computed_speedup = None
    if computed_vanilla is not None and computed_clipped is not None:
        computed_speedup = float(computed_vanilla["first_hit_time"]) / float(
            computed_clipped["first_hit_time"]
        )
    if computed_speedup != recorded["observed_speedup"]:
        errors.append("speedup aggregation mismatch")
    if not result["partition_audit"]["all_examples_assigned_exactly_once"]:
        errors.append("partition integrity failed")
    if not result["negative_control"]["target_rejected"]:
        errors.append("untrained negative control did not fail the target")
    if result["verdict"] != "BLOCKED":
        errors.append("D=8 selection sweep must not claim the full result")
    print(
        json.dumps(
            {
                "event": "CLAIM6_D8_SWEEP_INDEPENDENT_CHECK",
                "status": "PASS" if not errors else "FAIL",
                "best_vanilla": (
                    None
                    if computed_vanilla is None
                    else {
                        "name": computed_vanilla["name"],
                        "time": computed_vanilla["first_hit_time"],
                    }
                ),
                "best_clipped": (
                    None
                    if computed_clipped is None
                    else {
                        "name": computed_clipped["name"],
                        "time": computed_clipped["first_hit_time"],
                    }
                ),
                "observed_speedup": computed_speedup,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
