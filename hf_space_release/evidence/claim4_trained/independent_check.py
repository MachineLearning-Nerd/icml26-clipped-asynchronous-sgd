"""Independent OLS and protocol checker for Claim 4's trained route."""

from __future__ import annotations

import json
import math
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def ols_slope(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    return sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    ) / sum((x - x_mean) ** 2 for x in xs)


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    values = sorted(result["gradient_error_norms"], reverse=True)
    n = len(values)
    k = result["primary_estimate"]["k"]
    xs = [math.log(math.log(n / i)) for i in range(1, k + 1)]
    ys = [math.log(value) for value in values[:k]]
    recomputed = ols_slope(xs, ys)
    recorded = result["primary_estimate"]["theta"]
    if not math.isclose(recomputed, recorded, rel_tol=0.0, abs_tol=1e-12):
        errors.append(f"theta mismatch: recomputed {recomputed}, recorded {recorded}")
    if n != 128 or k != round(math.sqrt(n)):
        errors.append("sample count or preregistered k rule changed")
    if result["training"]["epochs"] != 1 or result["training"]["examples"] != 50_000:
        errors.append("checkpoint did not follow one complete epoch")
    if result["dataset"]["reference_examples"] != 8192:
        errors.append("reference sample count changed")
    if result["dataset"]["archive_md5"] != "c58f30108f718f92721af3b95e74349a":
        errors.append("CIFAR-10 archive MD5 mismatch")
    if result["model"]["parameter_count"] < 11_000_000:
        errors.append("model is not full ResNet-18 scale")
    if result["verdict"] != "BLOCKED":
        errors.append("under-specified route must remain BLOCKED")
    if not result["negative_control"]["pass"]:
        errors.append("calibrated estimator control failed")
    output = {
        "event": "CLAIM4_TRAINED_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "recomputed_theta": recomputed,
        "recorded_theta": recorded,
        "errors": errors,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
