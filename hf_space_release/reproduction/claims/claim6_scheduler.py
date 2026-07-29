"""Algorithm 2 closed-queue scheduler calibration for Figure 4."""

from __future__ import annotations

import heapq
import json
import random
import statistics
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim6_scheduler"
BASE_SEED = 20260728
WORKERS = 16
EVENTS = 200_000
BURN_IN = 2_000
DELAYS = {4: 0.337, 8: 0.668}
TOLERANCE = 0.015


def simulate_uniform_queue(delay: int, seed: int) -> float:
    """Algorithm 2: choose any worker uniformly, allowing per-worker queues."""
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
    previous = 0.0
    elapsed = 0.0
    measured = 0
    sequence = WORKERS
    for event in range(EVENTS):
        current, _, _ = heapq.heappop(queue)
        if event >= BURN_IN:
            elapsed += current - previous
            measured += 1
        previous = current
        selected = rng.randrange(WORKERS)
        finish = max(current, available[selected]) + service[selected]
        available[selected] = finish
        heapq.heappush(queue, (finish, sequence, selected))
        sequence += 1
    return elapsed / measured


def simulate_wrong_no_queue(delay: int) -> float:
    """Negative control: reschedule only the finisher, as in homogeneous ASGD."""
    service = [1.0] * 8 + [float(delay)] * 8
    queue = [(duration, worker) for worker, duration in enumerate(service)]
    heapq.heapify(queue)
    previous = 0.0
    elapsed = 0.0
    measured = 0
    for event in range(EVENTS):
        current, worker = heapq.heappop(queue)
        if event >= BURN_IN:
            elapsed += current - previous
            measured += 1
        previous = current
        heapq.heappush(queue, (current + service[worker], worker))
    return elapsed / measured


def main() -> int:
    started = time.perf_counter()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    cases = []
    all_pass = True
    for delay, paper_mean in DELAYS.items():
        seeds = [BASE_SEED + 100 * delay + offset for offset in range(3)]
        per_seed = [
            simulate_uniform_queue(delay, seed)
            for seed in seeds
        ]
        mean = statistics.fmean(per_seed)
        wrong = simulate_wrong_no_queue(delay)
        matches = abs(mean - paper_mean) <= TOLERANCE
        control_rejected = abs(wrong - paper_mean) > TOLERANCE
        all_pass = all_pass and matches and control_rejected
        cases.append(
            {
                "delay_factor": delay,
                "seeds": seeds,
                "paper_mean_time_per_oracle_call": paper_mean,
                "per_seed_mean_time": per_seed,
                "reconstructed_mean_time": mean,
                "absolute_error": abs(mean - paper_mean),
                "tolerance": TOLERANCE,
                "matches_paper_caption": matches,
                "wrong_no_queue_mean_time": wrong,
                "wrong_control_rejected": control_rejected,
            }
        )
    result = {
        "schema_version": 1,
        "claim_number": 6,
        "scope": "Algorithm 2 scheduler prerequisite; no neural claim yet",
        "status": "PASS" if all_pass else "FAIL",
        "verdict": "BLOCKED",
        "reason": (
            "Scheduler fidelity is necessary but does not verify the Figure 4 "
            "accuracy/speedup claim without real label-skew CIFAR-10 training."
        ),
        "algorithm": (
            "16-job closed queue; uniform worker resampling; one single-server "
            "queue per worker; 8 service times 1 and 8 service times D"
        ),
        "events_per_case_seed": EVENTS,
        "burn_in_events": BURN_IN,
        "cases": cases,
        "negative_control": "reschedule only the completing worker (no queues)",
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    raw = ARTIFACT_DIR / "raw_output.json"
    raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "CLAIM6_SCHEDULER_RAW", "result": result}, sort_keys=True))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
