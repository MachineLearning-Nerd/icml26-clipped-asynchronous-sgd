"""Independent recomputation of Claim 4 estimator and file invariants."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).with_name("raw_output.json")


def ols_slope(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = sum((x - x_mean) ** 2 for x in xs)
    return numerator / denominator


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    values = sorted(result["gradient_error_norms"], reverse=True)
    n = len(values)
    k = result["primary_estimate"]["k"]
    xs = [math.log(math.log(n / i)) for i in range(1, k + 1)]
    ys = [math.log(value) for value in values[:k]]
    recomputed = ols_slope(xs, ys)
    reported = result["primary_estimate"]["theta"]
    if not math.isclose(recomputed, reported, rel_tol=0.0, abs_tol=1e-12):
        errors.append(f"theta mismatch: recomputed {recomputed}, recorded {reported}")
    if result["verdict"] != "BLOCKED":
        errors.append("pilot verdict must remain BLOCKED")
    if not result["negative_control"]["pass"]:
        errors.append("known-theta negative control did not pass")
    if not result["negative_control"]["negative_case"]["rejected_as_intended"]:
        errors.append("wrong parameter-convention control was not rejected")
    if result["dataset"]["name"] != "torchvision CIFAR10 train":
        errors.append("wrong dataset")
    if result["model"]["parameter_count"] < 11_000_000:
        errors.append("model is not full ResNet-18 scale")
    output = {
        "event": "CLAIM4_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "recomputed_theta": recomputed,
        "recorded_theta": reported,
        "errors": errors,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
