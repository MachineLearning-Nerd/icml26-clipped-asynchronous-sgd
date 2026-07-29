"""Independent coverage and extremum checker for the exhaustive k audit."""

from __future__ import annotations

import json
import math
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    estimates = result["estimates"]
    expected_ks = list(range(3, result["n"]))
    observed_ks = [item["k"] for item in estimates]
    if observed_ks != expected_ks:
        errors.append("audit does not exhaust every admissible k")
    independently_closest = min(
        estimates, key=lambda item: abs(item["theta"] - result["reported_theta"])
    )
    independently_maximum = max(estimates, key=lambda item: item["theta"])
    if independently_closest != result["closest_to_reported"]:
        errors.append("closest estimate was selected incorrectly")
    if independently_maximum != result["maximum_theta"]:
        errors.append("maximum estimate was selected incorrectly")
    if result["any_exact_within_1e_12"] != (
        abs(independently_closest["theta"] - result["reported_theta"]) <= 1e-12
    ):
        errors.append("exact-match flag is incorrect")
    if not all(math.isfinite(item["theta"]) for item in estimates):
        errors.append("non-finite estimate")
    if not result["calibration_control"]["pass"]:
        errors.append("known-theta estimator calibration failed")
    if result["verdict"] != "BLOCKED":
        errors.append("protocol-under-specified result must remain BLOCKED")
    output = {
        "event": "CLAIM4_TAIL_AUDIT_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "audited_k_count": len(estimates),
        "closest": independently_closest,
        "maximum": independently_maximum,
        "errors": errors,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
