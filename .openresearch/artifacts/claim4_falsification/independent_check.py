"""Independent logic checker for Claim 4's falsification attempt."""

from __future__ import annotations

import json
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    identified = result["required_protocol_identified"]
    independently_available = all(identified.values())
    candidate = result["candidate_contradiction"]
    independently_succeeded = (
        independently_available
        and candidate["valid_assumption_identical_counterexample"]
    )
    if independently_available != result["assumption_identical_protocol_available"]:
        errors.append("protocol-availability conjunction is wrong")
    if independently_succeeded != result["falsification_succeeded"]:
        errors.append("falsification conjunction is wrong")
    positive = result["positive_falsification_control"]
    if positive["falsified_as_intended"] != (
        abs(
            positive["fully_specified_observed_theta"]
            - positive["deliberately_false_reported_theta"]
        )
        > positive["tolerance"]
    ):
        errors.append("positive falsification control is wrong")
    true_control = result["true_value_control"]
    if true_control["not_falsified_as_intended"] != (
        abs(
            true_control["fully_specified_observed_theta"]
            - true_control["reported_theta"]
        )
        <= true_control["tolerance"]
    ):
        errors.append("true-value control is wrong")
    if result["falsification_succeeded"]:
        errors.append("target falsification cannot succeed without source protocol")
    if result["verdict"] != "BLOCKED":
        errors.append("unsuccessful mandatory falsification route must be BLOCKED")
    output = {
        "event": "CLAIM4_FALSIFICATION_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "required_fields": len(identified),
        "identified_fields": sum(bool(value) for value in identified.values()),
        "falsification_succeeded": independently_succeeded,
        "positive_control_pass": positive["falsified_as_intended"],
        "true_value_control_pass": true_control["not_falsified_as_intended"],
        "errors": errors,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
