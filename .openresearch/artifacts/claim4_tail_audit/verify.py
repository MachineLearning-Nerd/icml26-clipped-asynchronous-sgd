"""Exhaust every admissible Vladimirova tail count on trained raw norms."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_RAW = ROOT / ".openresearch" / "artifacts" / "claim4_trained" / "raw_output.json"
RAW = Path(__file__).with_name("raw_output.json")
CHECKER = Path(__file__).with_name("independent_check.py")
TARGET = 2.71


def slope(values: list[float], k: int) -> float:
    ordered = sorted(values, reverse=True)
    n = len(ordered)
    xs = [math.log(math.log(n / i)) for i in range(1, k + 1)]
    ys = [math.log(value) for value in ordered[:k]]
    x_mean = sum(xs) / k
    y_mean = sum(ys) / k
    return sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    ) / sum((x - x_mean) ** 2 for x in xs)


def main() -> int:
    started = time.perf_counter()
    source = json.loads(SOURCE_RAW.read_text(encoding="utf-8"))
    values = source["gradient_error_norms"]
    estimates = [{"k": k, "theta": slope(values, k)} for k in range(3, len(values))]
    closest = min(estimates, key=lambda item: abs(item["theta"] - TARGET))
    maximum = max(estimates, key=lambda item: item["theta"])
    result = {
        "schema_version": 1,
        "claim_number": 4,
        "route": "exhaustive estimator-tail-count interpretation",
        "verdict": "BLOCKED",
        "reason": (
            "All admissible k values are exhausted for the trained route, but "
            "the unpublished paper checkpoint and gradient sampling protocol "
            "prevent assumption-identical verification or falsification."
        ),
        "reported_theta": TARGET,
        "n": len(values),
        "admissible_k": {"minimum": 3, "maximum": len(values) - 1},
        "estimates": estimates,
        "closest_to_reported": closest,
        "maximum_theta": maximum,
        "any_exact_within_1e_12": abs(closest["theta"] - TARGET) <= 1e-12,
        "calibration_control": source["negative_control"],
        "source_checkpoint_sha256": source["model"]["checkpoint_sha256"],
        "source_raw_file": str(SOURCE_RAW.relative_to(ROOT)),
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    RAW.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "CLAIM4_TAIL_AUDIT_RAW", "result": result}, sort_keys=True))
    checker = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    print(checker.stdout, end="")
    if checker.stderr:
        print(checker.stderr, file=sys.stderr, end="")
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
