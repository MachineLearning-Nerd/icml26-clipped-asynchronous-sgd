"""Independent falsification eligibility checker."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")
VALIDATION = Path(__file__).parents[1] / "claim6_validation" / "raw_output.json"
EXPECTED_VALIDATION_SHA256 = (
    "6bc2a8fe3148f83d72869d7f8fc50ffe0e303cde359b81d200edd1c9804aa539"
)


def classify(candidate: dict) -> str:
    return (
        "FALSIFIED"
        if all(field["status"] == "matched" for field in candidate["protocol_fields"])
        and (
            candidate["same_historical_realization"]
            or candidate["universally_quantified_claim"]
        )
        and candidate["contradiction_established"]
        else "BLOCKED"
    )


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    validation_hash = hashlib.sha256(VALIDATION.read_bytes()).hexdigest()
    if validation_hash != EXPECTED_VALIDATION_SHA256:
        errors.append("accepted validation evidence hash mismatch")
    actual = classify(result["candidate"])
    if actual != result["candidate_classification"] or actual != result["verdict"]:
        errors.append("actual candidate classification mismatch")
    if actual != "BLOCKED" or result["falsification_succeeded"]:
        errors.append("invalid full falsification claim")
    fields = result["candidate"]["protocol_fields"]
    statuses = {field["status"] for field in fields}
    if "unresolved" not in statuses or "mismatched" not in statuses:
        errors.append("actual identity gaps are not represented")
    controls = result["controls"]
    expected_controls = {
        "universal_positive": "FALSIFIED",
        "historical_positive": "FALSIFIED",
        "assumption_violation_negative": "BLOCKED",
    }
    for name, expected in expected_controls.items():
        observed = classify(controls[name]["candidate"])
        if observed != expected or controls[name]["classification"] != expected:
            errors.append(f"{name} control classification mismatch")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    if result["candidate_observation"]["D4_speedup"] != validation["aggregates"]["4"][
        "observed_speedup"
    ]:
        errors.append("D4 candidate observation mismatch")
    if result["candidate_observation"]["D8_all_targets_reached"] is not False:
        errors.append("D8 censoring was not preserved")
    if result["status"] != "PASS":
        errors.append("route status is not PASS")
    print(
        json.dumps(
            {
                "event": "CLAIM6_FALSIFICATION_INDEPENDENT_CHECK",
                "status": "PASS" if not errors else "FAIL",
                "candidate_classification": actual,
                "matched_fields": sum(
                    field["status"] == "matched" for field in fields
                ),
                "unresolved_fields": sum(
                    field["status"] == "unresolved" for field in fields
                ),
                "mismatched_fields": sum(
                    field["status"] == "mismatched" for field in fields
                ),
                "controls": expected_controls,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
