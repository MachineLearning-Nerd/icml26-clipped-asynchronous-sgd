"""Independently check Claim 3 route 1's proof ledger."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def main() -> int:
    data = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    findings = {item["code"]: item for item in data.get("findings", [])}
    required = {
        "INC_BOUND_FACTOR_TWO",
        "TAIL_SUM_MISSING_CARDINALITY",
        "NORMALIZATION_DROPPED",
        "APPENDIX_EXTRA_DELTA_TERM",
    }
    if set(findings) != required:
        errors.append("finding codes do not exactly match the audited obligations")

    increment = findings.get("INC_BOUND_FACTOR_TWO", {})
    independently_derived = 2 * (1 / 2 + 1 / 4)
    if not math.isclose(
        increment.get("derived_coefficient_of_eta_c_squared", math.nan),
        independently_derived,
    ):
        errors.append("increment coefficient was not independently reproduced")
    if not independently_derived > increment.get(
        "printed_coefficient_of_eta_c_squared", math.inf
    ):
        errors.append("printed increment negative control was not rejected")

    if "/ T" not in findings.get("NORMALIZATION_DROPPED", {}).get(
        "required_freedman_term", ""
    ):
        errors.append("corrected Freedman term lacks horizon normalization")
    if "|T^c|" not in findings.get("TAIL_SUM_MISSING_CARDINALITY", {}).get(
        "valid_union_bound_form", ""
    ):
        errors.append("tail-sum correction lacks cardinality")
    extra = findings.get("APPENDIX_EXTRA_DELTA_TERM", {})
    if extra.get("headline_term_present") is not False:
        errors.append("appendix-only term incorrectly marked present in headline")
    if data.get("claim_verdict") != "BLOCKED":
        errors.append("a proof gap must not be promoted to verification or falsification")

    result = {
        "event": "CLAIM3_ROUTE1_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "recomputed_increment_coefficient": independently_derived,
        "negative_controls_rejected": not errors,
        "claim_verdict": data.get("claim_verdict"),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
