"""Independent integrity and scope checker for the CIFAR-10 pilot."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    protocol = result["paper_protocol"]
    if (
        protocol["dataset"] != "CIFAR-10"
        or protocol["clients"] != 16
        or protocol["dirichlet_alpha"] != 0.5
        or protocol["delay_factor"] != 4
        or protocol["target_accuracy"] != 0.70
    ):
        errors.append("paper-specified pilot domain mismatch")
    if protocol["pilot_seeds"] != 1 or protocol["pilot_time_cap"] != 3_200.0:
        errors.append("pilot downscaling is not recorded exactly")
    partition = result["partition_audit"]
    if not partition["all_examples_assigned_exactly_once"]:
        errors.append("partition does not assign every example exactly once")
    if sum(partition["client_sizes"]) != 50_000:
        errors.append("client sizes do not sum to CIFAR-10 train size")
    if partition["minimum_client_size"] < 64:
        errors.append("a client cannot supply the declared batch size")
    controls = result["controls"]
    for name, passed in controls.items():
        if name.endswith("_accuracy"):
            continue
        if not passed:
            errors.append(f"control failed: {name}")
    configurations = result["configurations"]
    if [item["name"] for item in configurations] != [
        "vanilla_lr_2^-6",
        "clipped_lr_2^-4_c1",
        "clipped_lr_2^-4_c2",
    ]:
        errors.append("pilot configuration domain mismatch")
    for item in configurations:
        if item["oracle_calls"] <= 0:
            errors.append(f"{item['name']} has no oracle calls")
            continue
        recomputed_mean = item["last_event_time"] / item["oracle_calls"]
        if abs(recomputed_mean - item["mean_time_per_oracle_call"]) > 1e-15:
            errors.append(f"{item['name']} oracle-time aggregation mismatch")
        curve_max = max(point["test_accuracy"] for point in item["curve"])
        if abs(curve_max - item["max_evaluated_accuracy"]) > 1e-15:
            errors.append(f"{item['name']} curve maximum mismatch")
        if item["reached_target"] != (item["first_hit_time"] is not None):
            errors.append(f"{item['name']} first-hit flag mismatch")
        if item["reached_target"] and item["max_evaluated_accuracy"] < 0.70:
            errors.append(f"{item['name']} invalid target hit")
        if item["staleness_updates"]["mean"] != statistics.fmean(
            [item["staleness_updates"]["mean"]]
        ):
            errors.append(f"{item['name']} nonfinite staleness mean")
    if result["verdict"] != "BLOCKED":
        errors.append("pilot must not claim the full Figure 4 result")
    print(
        json.dumps(
            {
                "event": "CLAIM6_CIFAR_PILOT_INDEPENDENT_CHECK",
                "status": "PASS" if not errors else "FAIL",
                "outcomes": [
                    {
                        "name": item["name"],
                        "reached_target": item["reached_target"],
                        "first_hit_time": item["first_hit_time"],
                        "max_accuracy": item["max_evaluated_accuracy"],
                        "oracle_calls": item["oracle_calls"],
                    }
                    for item in configurations
                ],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
