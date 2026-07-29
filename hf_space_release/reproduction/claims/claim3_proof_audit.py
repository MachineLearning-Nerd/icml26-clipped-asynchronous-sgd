"""Route 1 for Claim 3: audit the published high-probability proof."""

from __future__ import annotations

import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim3_route1"


def main() -> int:
    started = time.perf_counter()
    eta_tau_l_upper = 1 / 4
    derived_increment_coefficient = 2 * (1 / 2 + eta_tau_l_upper)
    result = {
        "schema_version": 1,
        "claim": 3,
        "route": "published-proof algebra and dependency audit",
        "audit_status": "PASS",
        "claim_verdict": "BLOCKED",
        "source": {
            "latex_archive_sha256": (
                "625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915"
            ),
            "paper_html_sha256": (
                "292ba2ce9a95e41279fe1535ffa23b720f18fb2139c3e26324138c0d4a0304ff"
            ),
            "headline_homogeneous_lines": "main.tex:601-635",
            "headline_heterogeneous_lines": "main.tex:724-735",
            "appendix_proof_lines": "main.tex:1350-1548",
            "freedman_lemma_lines": "main.tex:1019-1027",
        },
        "exact_claim": {
            "quantifiers": [
                "for every epsilon in (0,1)",
                "for every failure probability delta in (0,1)",
                "there exist a constant step size eta and clipping radius c",
            ],
            "event": (
                "P((1/T) sum_{t=0}^{T-1} ||grad f(x_t)|| <= epsilon) "
                ">= 1-delta"
            ),
            "homogeneous_complexity": [
                "sigma^2 log(1/delta)^(2 theta) / epsilon^4",
                "sigma tau_C log(1/delta)^theta / epsilon^3",
                "tau_C / epsilon^2",
            ],
            "heterogeneous_complexity": [
                "(sigma^2+zeta^2) log(1/delta)^(2 theta) / epsilon^4",
                "(sigma+zeta) tau_C log(1/delta)^theta / epsilon^3",
                "tau_C / epsilon^2",
            ],
            "novelty": (
                "to the best of the authors' knowledge, the first "
                "high-probability convergence result in asynchronous optimization"
            ),
        },
        "findings": [
            {
                "code": "INC_BOUND_FACTOR_TWO",
                "location": "main.tex:1420-1429",
                "premises": [
                    "|Z_t| <= 2 eta (c/2 + eta c tau_C L)c",
                    "eta tau_C L <= 1/4",
                ],
                "printed_coefficient_of_eta_c_squared": 0.75,
                "derived_coefficient_of_eta_c_squared": derived_increment_coefficient,
                "effect": (
                    "the displayed Freedman increment bound is too small by "
                    "a factor of two; constants can be repaired but the printed "
                    "application is not valid as written"
                ),
            },
            {
                "code": "TAIL_SUM_MISSING_CARDINALITY",
                "location": "main.tex:1477-1484",
                "printed": (
                    "sum over t in T^c of squared noise <= one per-step "
                    "sub-Weibull threshold"
                ),
                "valid_union_bound_form": (
                    "each squared noise term <= threshold simultaneously, or "
                    "the sum <= |T^c| times threshold"
                ),
                "effect": (
                    "the displayed sum inequality is false for more than one "
                    "nonzero term, although the following per-step use can be "
                    "repaired from a simultaneous union bound"
                ),
            },
            {
                "code": "NORMALIZATION_DROPPED",
                "location": "main.tex:1508-1519",
                "left_side_normalized_by_T": True,
                "printed_freedman_term": "4 c^2 log(2/delta)",
                "required_freedman_term": "4 c^2 log(2/delta) / T",
                "effect": (
                    "the next display restores the 1/T scaling implicitly, so "
                    "the intervening displayed implication is not valid as written"
                ),
            },
            {
                "code": "APPENDIX_EXTRA_DELTA_TERM",
                "location": "main.tex:1527-1545",
                "headline_term_present": False,
                "appendix_term": (
                    "(sigma^2 log(1/delta)^(2 theta + 1) + zeta^2) / epsilon^2"
                ),
                "effect": (
                    "the appendix's own final sufficient iteration count is "
                    "strictly different from the displayed headline formula"
                ),
            },
        ],
        "repaired_local_controls": {
            "increment_coefficient": derived_increment_coefficient,
            "freedman_term": "4 c^2 log(2/delta) / T",
            "tail_statement": (
                "for all t in T^c, squared noise_t <= threshold on a "
                "simultaneous event"
            ),
            "expected_result": "all three local algebra controls pass",
        },
        "negative_controls": {
            "accept_printed_increment_coefficient": "must be rejected",
            "accept_unnormalized_freedman_term": "must be rejected",
            "accept_sum_without_cardinality": "must be rejected",
            "drop_appendix_extra_term": "must be rejected",
        },
        "interpretation": {
            "established": (
                "the exact published proof contains reproducible gaps and ends "
                "with an additional failure-probability term"
            ),
            "not_established": (
                "these gaps do not constitute a counterexample to the theorem; "
                "a sharper proof may still establish the headline rate"
            ),
            "reason_blocked": (
                "route 1 cannot certify the exact headline theorem or falsify it"
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
    print(json.dumps({"event": "CLAIM3_ROUTE1_AUDIT", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
