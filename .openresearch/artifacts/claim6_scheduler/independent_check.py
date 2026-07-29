"""Independent checker for the preserved failed scheduler calibration."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    if [case["delay_factor"] for case in result["cases"]] != [4, 8]:
        errors.append("delay domain must be exactly D=4 and D=8")
    for case in result["cases"]:
        recomputed = statistics.fmean(case["per_seed_mean_time"])
        if abs(recomputed - case["reconstructed_mean_time"]) > 1e-15:
            errors.append(f"D={case['delay_factor']} mean aggregation mismatch")
        expected_match = (
            abs(recomputed - case["paper_mean_time_per_oracle_call"])
            <= case["tolerance"]
        )
        if expected_match != case["matches_paper_caption"]:
            errors.append(f"D={case['delay_factor']} match flag incorrect")
        expected_rejection = (
            abs(
                case["wrong_no_queue_mean_time"]
                - case["paper_mean_time_per_oracle_call"]
            )
            > case["tolerance"]
        )
        if expected_rejection != case["wrong_control_rejected"]:
            errors.append(f"D={case['delay_factor']} control flag incorrect")
        if not expected_rejection:
            errors.append(f"D={case['delay_factor']} negative control was not rejected")
    match_flags = [case["matches_paper_caption"] for case in result["cases"]]
    if match_flags != [True, False]:
        errors.append("preserved scientific outcome must be PASS at D=4 and FAIL at D=8")
    if result["status"] != "FAIL":
        errors.append("source calibration status must remain FAIL")
    if result["verdict"] != "BLOCKED":
        errors.append("scheduler-only evidence must not claim the neural result")
    output = {
        "event": "CLAIM6_SCHEDULER_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "cases": result["cases"],
        "errors": errors,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
