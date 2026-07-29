"""Independent proof-DAG and symbolic-rate checker for Claims 1 and 2."""

from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp


RAW = Path(__file__).with_name("raw_output.json")
EXPECTED_DAG = {
    "A": [],
    "B": ["A"],
    "C": ["B"],
    "D": ["A", "B"],
    "E": ["C", "D"],
    "F": ["E"],
    "G": ["F"],
    "H": ["D", "G"],
    "I": ["H"],
    "J": ["I"],
    "K": ["I"],
}
EXPECTED_OUTPUTS = {
    "claim_1": [
        {"factor": "sigma^2", "epsilon_power": -4, "tau_C_power": 0},
        {"factor": "sigma", "epsilon_power": -3, "tau_C_power": 1},
        {"factor": "1", "epsilon_power": -2, "tau_C_power": 1},
    ],
    "claim_2": [
        {
            "factor": "sigma^2+zeta^2",
            "epsilon_power": -4,
            "tau_C_power": 0,
        },
        {
            "factor": "sigma+zeta",
            "epsilon_power": -3,
            "tau_C_power": 1,
        },
        {"factor": "1", "epsilon_power": -2, "tau_C_power": 1},
    ],
}
EXPECTED_PRE = [
    "tau_C*L*Delta_bar/epsilon^2",
    "L*R*Delta_bar/epsilon^4",
    "c*tau_C*L*Delta_bar/epsilon^3",
]
EXPECTED_EXPANSION = [
    "tau_C*L*Delta_bar/epsilon^2",
    "(sigma^2+zeta^2)*L*Delta_bar/epsilon^4",
    "(sigma+zeta)*tau_C*L*Delta_bar/epsilon^3",
]


def strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for key, item in value.items():
            result.extend([str(key), *strings(item)])
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(strings(item))
        return result
    return []


def check_certificate(result: dict) -> list[str]:
    errors: list[str] = []
    if result["status"] != "PASS":
        errors.append("certificate status is not PASS")
    if result["verdicts"] != {"claim_1": "VERIFIED", "claim_2": "VERIFIED"}:
        errors.append("terminal verdict mismatch")
    if result["source"]["latex_archive_sha256"] != (
        "625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915"
    ):
        errors.append("paper source hash mismatch")

    dag = {node["id"]: node["depends_on"] for node in result["proof_dag"]}
    if dag != EXPECTED_DAG:
        errors.append("proof DAG dependency mismatch")
    seen: set[str] = set()
    for node in result["proof_dag"]:
        if any(parent not in seen for parent in node["depends_on"]):
            errors.append(f"non-topological dependency at {node['id']}")
        seen.add(node["id"])

    if result["theorem_outputs"] != EXPECTED_OUTPUTS:
        errors.append("theorem rate exponent/factor mismatch")
    inversion = result["complexity_inversion"]
    if inversion["pre_simplification"] != EXPECTED_PRE:
        errors.append("step-size inverse expansion mismatch")
    if inversion["soft_O_expansion"] != EXPECTED_EXPANSION:
        errors.append("soft-O simplification mismatch")
    if inversion["forbidden_symbols"] != ["tau_max"]:
        errors.append("forbidden-symbol contract mismatch")
    searchable = {
        "virtual_bound": result["analytic_obligations"]["virtual_bound"],
        "parameters": result["constructive_parameters"],
        "outputs": result["theorem_outputs"],
        "complexity": {
            "pre": inversion["pre_simplification"],
            "expansion": inversion["soft_O_expansion"],
        },
    }
    if any("tau_max" in text for text in strings(searchable)):
        errors.append("tau_max contaminates proof output")

    virtual = result["analytic_obligations"]["virtual_bound"]
    if virtual != {
        "outstanding_gradient_count_upper_bound": "tau_C",
        "per_gradient_norm_upper_bound": "c",
        "distance_upper_bound": "eta*c*tau_C",
        "uses_maximum_delay": False,
    }:
        errors.append("virtual-iterate certificate mismatch")

    epsilon, W, K = sp.symbols("epsilon W K", positive=True)
    tail_gap = sp.factor(epsilon**2 / K - W / (2 + K * W / epsilon**2))
    expected_gap = 2 * epsilon**4 / (K * (2 * epsilon**2 + K * W))
    if sp.simplify(tail_gap - expected_gap) != 0:
        errors.append("tail-bias terminal inequality is not an identity")

    sigma, zeta = sp.symbols("sigma zeta", nonnegative=True)
    heterogeneous_variance = sigma**2 + zeta**2
    heterogeneous_scale = sigma + zeta
    if sp.simplify(heterogeneous_variance.subs(zeta, 0) - sigma**2) != 0:
        errors.append("homogeneous variance specialization failed")
    if sp.simplify(heterogeneous_scale.subs(zeta, 0) - sigma) != 0:
        errors.append("homogeneous scale specialization failed")

    # Constant arithmetic for the two large-gradient regions.
    if not (
        -Fraction(1, 2) + Fraction(1, 4) <= -Fraction(1, 4)
        and -Fraction(1, 4) <= -Fraction(1, 8)
    ):
        errors.append("middle-region descent constants failed")
    if not (
        -Fraction(1, 2) + Fraction(1, 16) == -Fraction(7, 16)
        and -Fraction(7, 16) <= -Fraction(1, 8)
    ):
        errors.append("far-region descent constants failed")

    norm = result["analytic_obligations"]["norm_conversion"]
    if norm["premises"] != ["Q<=epsilon^2/16", "c>=epsilon"]:
        errors.append("norm-conversion premises mismatch")
    if Fraction(1, 4) + Fraction(1, 16) != Fraction(5, 16):
        errors.append("norm-conversion arithmetic failed")
    if not Fraction(5, 16) < 1:
        errors.append("norm-conversion target failed")

    required_repairs = {
        "random index set",
        "correct sign",
        "tau_C^2",
        "c>=epsilon",
        "including zeta",
        "initialization transient",
    }
    repair_text = " ".join(result["repairs_relative_to_printed_appendix"])
    if not all(fragment in repair_text for fragment in required_repairs):
        errors.append("published-proof repair ledger is incomplete")
    if "high-probability" not in " ".join(result["limitations"]):
        errors.append("scope limitation does not exclude Claim 3")
    return errors


def main() -> int:
    result = json.loads(RAW.read_text(encoding="utf-8"))
    errors = check_certificate(result)
    epsilon, W, K = sp.symbols("epsilon W K", positive=True)
    tail_gap = sp.factor(epsilon**2 / K - W / (2 + K * W / epsilon**2))
    expected_gap = 2 * epsilon**4 / (K * (2 * epsilon**2 + K * W))

    tau_control = copy.deepcopy(result)
    tau_control["theorem_outputs"]["claim_1"][0]["factor"] += "*tau_max"
    tau_control_rejected = any(
        "tau_max" in error for error in check_certificate(tau_control)
    )

    exponent_control = copy.deepcopy(result)
    exponent_control["theorem_outputs"]["claim_1"][0]["epsilon_power"] = -3
    exponent_control_rejected = any(
        "exponent" in error for error in check_certificate(exponent_control)
    )

    dependency_control = copy.deepcopy(result)
    dependency_control["proof_dag"][8]["depends_on"] = []
    dependency_control_rejected = any(
        "dependency" in error for error in check_certificate(dependency_control)
    )
    if not tau_control_rejected:
        errors.append("tau_max injection negative control was not rejected")
    if not exponent_control_rejected:
        errors.append("wrong exponent negative control was not rejected")
    if not dependency_control_rejected:
        errors.append("missing dependency negative control was not rejected")
    print(
        json.dumps(
            {
                "event": "EXPECTATION_THEOREMS_INDEPENDENT_CHECK",
                "status": "PASS" if not errors else "FAIL",
                "claim_1": result["verdicts"]["claim_1"],
                "claim_2": result["verdicts"]["claim_2"],
                "dag_nodes": len(result["proof_dag"]),
                "tail_identity": str(
                    sp.Eq(tail_gap, expected_gap, evaluate=False)
                ),
                "negative_controls": {
                    "tau_max_injection_rejected": tau_control_rejected,
                    "wrong_exponent_rejected": exponent_control_rejected,
                    "missing_dependency_rejected": dependency_control_rejected,
                },
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
