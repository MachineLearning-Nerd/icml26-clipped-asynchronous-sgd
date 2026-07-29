"""Independently verify Claim 3's prior-art falsification certificate."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def main() -> int:
    data = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    prior = data.get("prior_result", {})
    scope = prior.get("scope_audit", {})
    required_scope = {
        "predates_target": prior.get("predates_target") is True,
        "stochastic_gradient": scope.get("stochastic_gradient_algorithm") is True,
        "asynchronous": scope.get("asynchronous_delayed_updates") is True,
        "optimization_convergence": scope.get(
            "stationarity_convergence_guarantee"
        )
        is True,
        "base_probability": math.isclose(
            scope.get("base_success_probability", -1), 0.5
        ),
        "arbitrary_probability": scope.get("arbitrary_success_probability")
        == "1-delta",
    }
    errors.extend(name for name, passed in required_scope.items() if not passed)

    amp_errors: list[dict[str, float | int]] = []
    for check in data.get("amplification_certificate", {}).get("checks", []):
        delta = check["delta"]
        k = check["repetitions"]
        failure = check["failure_upper_bound"]
        expected_k = math.ceil(math.log2(1 / delta))
        if k != expected_k or not math.isclose(failure, 2.0 ** (-k)) or failure > delta:
            amp_errors.append(check)
    if amp_errors:
        errors.append("restart amplification inequality failed")

    expected_controls = {
        "serial_high_probability_sgd",
        "later_asynchronous_high_probability_result",
        "asynchronous_expectation_only_result",
        "asynchronous_runtime_only_high_probability_result",
    }
    controls = data.get("controls", {})
    if set(controls) != expected_controls:
        errors.append("control set is incomplete")
    if any(
        item.get("classification") != "NOT_A_NOVELTY_COUNTEREXAMPLE"
        for item in controls.values()
    ):
        errors.append("a near-miss control was accepted")

    verdicts = data.get("subclaim_verdicts", {})
    if verdicts != {
        "novelty": "FALSIFIED",
        "specific_theta_rate": "BLOCKED",
        "compound_claim_3": "FALSIFIED",
    }:
        errors.append("subclaim logic is not conservatively classified")
    if data.get("claim_verdict") != "FALSIFIED" or data.get("confidence") != "HIGH":
        errors.append("terminal classification mismatch")

    result = {
        "event": "CLAIM3_ROUTE3_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "scope_checks": required_scope,
        "amplification_checks": len(
            data.get("amplification_certificate", {}).get("checks", [])
        ),
        "near_miss_controls_rejected": not errors,
        "subclaim_verdicts": verdicts,
        "claim_verdict": data.get("claim_verdict"),
        "confidence": data.get("confidence"),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
