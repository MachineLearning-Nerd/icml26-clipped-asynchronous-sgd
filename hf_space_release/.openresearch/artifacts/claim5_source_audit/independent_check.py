"""Independently check Claim 5's comparator audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def in_range(value: float, bounds: list[float]) -> bool:
    return bounds[0] <= value <= bounds[1]


def main() -> int:
    data = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    ratios = data["source_reported_speedups"]
    claimed = data["claim_contract"]["shakespeare_conjunct"]["claimed_range"]
    vanilla = [
        ratios["Shakespeare"]["D4"]["Vanilla ASGD"],
        ratios["Shakespeare"]["D8"]["Vanilla ASGD"],
    ]
    delay_adaptive = [
        ratios["Shakespeare"]["D4"]["Delay-adaptive ASGD"],
        ratios["Shakespeare"]["D8"]["Delay-adaptive ASGD"],
    ]
    checks = {
        "cifar_exact": ratios["CIFAR-10"]["D4"]["Vanilla ASGD"] == 1.8,
        "D4_vanilla_outside": not in_range(vanilla[0], claimed),
        "D8_vanilla_inside": in_range(vanilla[1], claimed),
        "corrected_vanilla_control": vanilla == [1.8, 2.0],
        "delay_adaptive_control": delay_adaptive == [2.1, 2.2],
        "compound_false": data["comparison"]["compound_claim_true"] is False,
        "honest_confidence": data.get("confidence") == "MEDIUM",
        "verdict": data.get("claim_verdict") == "FALSIFIED",
    }
    errors.extend(name for name, passed in checks.items() if not passed)
    result = {
        "event": "CLAIM5_SOURCE_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "checks": checks,
        "carried_comparator_values": vanilla,
        "alternate_comparator_values": delay_adaptive,
        "claim_verdict": data.get("claim_verdict"),
        "confidence": data.get("confidence"),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
