"""Finite-horizon audit of Algorithm 2's Figure 4 timing captions."""

from __future__ import annotations

import heapq
import json
import random
import statistics
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim6_scheduler_finite"
BASE_SEED = 20260729
WORKERS = 16
REPLICATES = 512
PAPER_CASES = {
    4: {"horizon": 8_000.0, "caption_mean": 0.337},
    8: {"horizon": 12_000.0, "caption_mean": 0.668},
}


def simulate_to_horizon(delay: int, horizon: float, seed: int) -> tuple[float, int]:
    """Return last-completion time per oracle call under Algorithm 2."""
    rng = random.Random(seed)
    service = [1.0] * 8 + [float(delay)] * 8
    available = service.copy()
    queue = [
        (duration, sequence, worker)
        for sequence, (worker, duration) in enumerate(
            zip(range(WORKERS), service, strict=True)
        )
    ]
    heapq.heapify(queue)
    sequence = WORKERS
    completed = 0
    last_completion = 0.0
    while queue[0][0] <= horizon:
        current, _, _ = heapq.heappop(queue)
        completed += 1
        last_completion = current
        selected = rng.randrange(WORKERS)
        finish = max(current, available[selected]) + service[selected]
        available[selected] = finish
        heapq.heappush(queue, (finish, sequence, selected))
        sequence += 1
    return last_completion / completed, completed


def quantile(values: list[float], probability: float) -> float:
    """Linearly interpolated empirical quantile."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def main() -> int:
    started = time.perf_counter()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    cases = []
    for delay, paper in PAPER_CASES.items():
        replicate_means = []
        replicate_counts = []
        replicate_seeds = []
        for replicate in range(REPLICATES):
            seeds = [
                BASE_SEED + delay * 1_000_000 + replicate * 3 + offset
                for offset in range(3)
            ]
            simulations = [
                simulate_to_horizon(delay, paper["horizon"], seed)
                for seed in seeds
            ]
            replicate_seeds.append(seeds)
            replicate_means.append(
                statistics.fmean(mean_time for mean_time, _ in simulations)
            )
            replicate_counts.append([count for _, count in simulations])
        interval_99 = [
            quantile(replicate_means, 0.005),
            quantile(replicate_means, 0.995),
        ]
        caption = paper["caption_mean"]
        cases.append(
            {
                "delay_factor": delay,
                "paper_horizon": paper["horizon"],
                "paper_caption_mean": caption,
                "replicate_count": REPLICATES,
                "seeds_per_replicate": 3,
                "replicate_seeds": replicate_seeds,
                "replicate_three_seed_means": replicate_means,
                "replicate_completion_counts": replicate_counts,
                "monte_carlo_mean": statistics.fmean(replicate_means),
                "monte_carlo_stdev": statistics.stdev(replicate_means),
                "prediction_interval_99": interval_99,
                "caption_inside_prediction_interval_99": (
                    interval_99[0] <= caption <= interval_99[1]
                ),
                "no_queue_harmonic_mean": 1.0 / (8.0 + 8.0 / delay),
            }
        )
    result = {
        "schema_version": 1,
        "claim_number": 6,
        "route": "finite-horizon Algorithm 2 scheduler audit",
        "status": "PASS",
        "verdict": "BLOCKED",
        "scope": "Scheduler timing only; no neural speedup conclusion.",
        "model": (
            "16 initial jobs, eight service times 1 and eight service times D; "
            "after each completion, uniformly enqueue one new job on any worker."
        ),
        "non_circularity": (
            "Horizons are the paper's training caps; the 99% prediction interval "
            "is computed from independent schedules, not fitted to caption values."
        ),
        "cases": cases,
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    raw = ARTIFACT_DIR / "raw_output.json"
    raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "event": "CLAIM6_SCHEDULER_FINITE_RAW",
                "result": {
                    **result,
                    "cases": [
                        {
                            key: value
                            for key, value in case.items()
                            if not key.startswith("replicate_")
                        }
                        for case in cases
                    ],
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
