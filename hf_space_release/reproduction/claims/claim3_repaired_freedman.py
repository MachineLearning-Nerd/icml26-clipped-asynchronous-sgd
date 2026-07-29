"""Route 2 for Claim 3: reconstruct the locally repaired Freedman proof."""

from __future__ import annotations

import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim3_route2"


def main() -> int:
    started = time.perf_counter()
    bounded_increment_coefficient = 3 / 2
    variance_coefficient = 4
    rho = 3 / 32
    absorbed_descent_coefficient = (
        rho * variance_coefficient / bounded_increment_coefficient
    )
    freedman_remainder_coefficient = bounded_increment_coefficient / rho
    result = {
        "schema_version": 1,
        "claim": 3,
        "route": "locally repaired Freedman derivation",
        "audit_status": "PASS",
        "claim_verdict": "BLOCKED",
        "source": {
            "latex_archive_sha256": (
                "625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915"
            ),
            "proof_lines": "main.tex:1350-1548",
            "freedman_lemma_lines": "main.tex:1019-1027",
        },
        "repair_dag": [
            {
                "id": "R1",
                "depends_on": [],
                "statement": (
                    "Use |psi_t Z_t| <= (3/2) eta c^2 under "
                    "eta tau_C L <= 1/4."
                ),
            },
            {
                "id": "R2",
                "depends_on": ["R1"],
                "statement": (
                    "Use conditional variance <= 4 eta^2 c^2 A_t and "
                    "Freedman rho=3/32."
                ),
            },
            {
                "id": "R3",
                "depends_on": ["R2"],
                "statement": (
                    "Absorb (1/4) eta sum A_t and retain "
                    "16 eta c^2 log(2/delta)."
                ),
            },
            {
                "id": "R4",
                "depends_on": ["R3"],
                "statement": (
                    "After division and normalization, retain "
                    "16 c^2 log(2/delta)/T."
                ),
            },
            {
                "id": "R5",
                "depends_on": ["R4"],
                "statement": (
                    "Apply a simultaneous per-step sub-Weibull union bound, "
                    "not the invalid unnormalized sum inequality."
                ),
            },
            {
                "id": "R6",
                "depends_on": ["R5"],
                "statement": (
                    "With c^2 of order sigma^2 log(T/delta)^(2theta)+zeta^2, "
                    "the Freedman remainder contributes a square-root rate "
                    "with one additional log(1/delta) factor."
                ),
            },
            {
                "id": "R7",
                "depends_on": ["R6"],
                "statement": (
                    "Inverting that residual for accuracy epsilon requires "
                    "(sigma^2 log(1/delta)^(2theta+1)+zeta^2 log(1/delta))"
                    "/epsilon^2, up to T/epsilon polylogs."
                ),
            },
        ],
        "freedman_reconstruction": {
            "bounded_increment_coefficient": bounded_increment_coefficient,
            "variance_coefficient": variance_coefficient,
            "rho": rho,
            "absorbed_descent_coefficient": absorbed_descent_coefficient,
            "remainder_coefficient": freedman_remainder_coefficient,
            "normalized_remainder": "16 c^2 log(2/delta)/T",
        },
        "rate_reconstruction": {
            "clipping_radius_squared": (
                "O(sigma^2 log(T/delta)^(2theta)+zeta^2)"
            ),
            "residual_before_inversion": (
                "O(sqrt((sigma^2 log(T/delta)^(2theta)+zeta^2)"
                " log(1/delta)/T))"
            ),
            "sufficient_iteration_term": (
                "O((sigma^2 log(1/delta)^(2theta+1)"
                "+zeta^2 log(1/delta))/epsilon^2),"
                " suppressing T/epsilon polylogs"
            ),
            "headline_contains_term": False,
        },
        "negative_controls": {
            "rho_3_over_16_with_correct_increment_gives_one_half_not_one_quarter": {
                "rho": 3 / 16,
                "absorption": (3 / 16) * 4 / (3 / 2),
                "must_be_rejected": True,
            },
            "drop_horizon_normalization": "must be rejected",
            "drop_extra_log_from_residual": "must be rejected",
            "promote_repaired_derivation_to_headline": "must be rejected",
        },
        "interpretation": {
            "local_repairs_succeed": True,
            "exact_headline_derived": False,
            "reason": (
                "the corrected Freedman remainder still produces an additional "
                "delta-dependent epsilon^-2 sufficient-complexity term"
            ),
            "not_a_falsification": (
                "a different concentration argument might remove or absorb the "
                "term, so failure of this proof route is not a theorem counterexample"
            ),
        },
        "compute": {
            "estimated_cores": 1,
            "selected_backend": "local",
            "actual_core_requirement": 1,
            "expected_runtime": "under five minutes",
            "gpu_allowed": False,
        },
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    raw = ARTIFACT_DIR / "raw_output.json"
    raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "CLAIM3_ROUTE2_REPAIR", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
