"""Independently check Claim 3 route 2."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


RAW = Path(__file__).with_name("raw_output.json")


def main() -> int:
    data = json.loads(RAW.read_text(encoding="utf-8"))
    errors: list[str] = []
    f = data.get("freedman_reconstruction", {})
    b = 2 * (1 / 2 + 1 / 4)
    rho = 3 / 32
    absorption = rho * 4 / b
    remainder = b / rho
    checks = {
        "bounded_increment": math.isclose(f.get("bounded_increment_coefficient", -1), b),
        "absorption": math.isclose(f.get("absorbed_descent_coefficient", -1), absorption),
        "remainder": math.isclose(f.get("remainder_coefficient", -1), remainder),
        "normalization": f.get("normalized_remainder", "").endswith("/T"),
        "extra_term_retained": (
            data.get("rate_reconstruction", {}).get("headline_contains_term") is False
            and "2theta+1"
            in data.get("rate_reconstruction", {}).get("sufficient_iteration_term", "")
        ),
        "honest_verdict": data.get("claim_verdict") == "BLOCKED",
    }
    errors.extend(name for name, passed in checks.items() if not passed)
    wrong_rho_absorption = (3 / 16) * 4 / b
    if not math.isclose(wrong_rho_absorption, 1 / 2):
        errors.append("wrong-rho control was not independently reproduced")
    result = {
        "event": "CLAIM3_ROUTE2_INDEPENDENT_CHECK",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "recomputed": {
            "bounded_increment_coefficient": b,
            "rho": rho,
            "absorption": absorption,
            "remainder": remainder,
            "wrong_rho_absorption": wrong_rho_absorption,
        },
        "checks": checks,
        "claim_verdict": data.get("claim_verdict"),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
