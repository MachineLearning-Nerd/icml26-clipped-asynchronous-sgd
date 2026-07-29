"""Independent checker for the finite-horizon scheduler audit."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")
EXPECTED = {4: (8_000.0, 0.337), 8: (12_000.0, 0.668)}


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    if result["verdict"] != "BLOCKED" or result["status"] != "PASS":
        errors.append("scheduler audit must remain a successful BLOCKED route")
    if [case["delay_factor"] for case in result["cases"]] != [4, 8]:
        errors.append("domain must be exactly D=4,8")
    summaries = []
    for case in result["cases"]:
        delay = case["delay_factor"]
        expected_horizon, expected_caption = EXPECTED[delay]
        values = case["replicate_three_seed_means"]
        counts = case["replicate_completion_counts"]
        seeds = case["replicate_seeds"]
        if case["paper_horizon"] != expected_horizon:
            errors.append(f"D={delay} horizon mismatch")
        if case["paper_caption_mean"] != expected_caption:
            errors.append(f"D={delay} caption mismatch")
        if len(values) != 512 or len(counts) != 512 or len(seeds) != 512:
            errors.append(f"D={delay} incomplete Monte Carlo records")
        recomputed_mean = statistics.fmean(values)
        recomputed_stdev = statistics.stdev(values)
        recomputed_interval = [quantile(values, 0.005), quantile(values, 0.995)]
        if abs(recomputed_mean - case["monte_carlo_mean"]) > 1e-15:
            errors.append(f"D={delay} mean mismatch")
        if abs(recomputed_stdev - case["monte_carlo_stdev"]) > 1e-15:
            errors.append(f"D={delay} stdev mismatch")
        if any(
            abs(left - right) > 1e-15
            for left, right in zip(
                recomputed_interval, case["prediction_interval_99"], strict=True
            )
        ):
            errors.append(f"D={delay} interval mismatch")
        inside = recomputed_interval[0] <= expected_caption <= recomputed_interval[1]
        if inside != case["caption_inside_prediction_interval_99"]:
            errors.append(f"D={delay} caption decision mismatch")
        harmonic = 1.0 / (8.0 + 8.0 / delay)
        if abs(harmonic - case["no_queue_harmonic_mean"]) > 1e-15:
            errors.append(f"D={delay} negative-control value mismatch")
        if recomputed_interval[0] <= harmonic <= recomputed_interval[1]:
            errors.append(f"D={delay} negative control was not rejected")
        if any(count <= 0 for triplet in counts for count in triplet):
            errors.append(f"D={delay} nonpositive completion count")
        summaries.append(
            {
                "delay_factor": delay,
                "monte_carlo_mean": recomputed_mean,
                "prediction_interval_99": recomputed_interval,
                "caption_inside": inside,
            }
        )
    print(
        json.dumps(
            {
                "event": "CLAIM6_SCHEDULER_FINITE_INDEPENDENT_CHECK",
                "status": "PASS" if not errors else "FAIL",
                "summaries": summaries,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
