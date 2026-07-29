"""Audit the exact comparator and delay values in imported Claim 5."""

from __future__ import annotations

import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim5_source_audit"


def main() -> int:
    started = time.perf_counter()
    source_ratios = {
        "CIFAR-10": {
            "D4": {
                "Vanilla ASGD": 1.8,
                "Delay-adaptive ASGD": 1.5,
                "Ringmaster ASGD": 1.5,
            }
        },
        "Shakespeare": {
            "D4": {
                "Vanilla ASGD": 1.8,
                "Delay-adaptive ASGD": 2.1,
                "Ringmaster ASGD": 1.8,
            },
            "D8": {
                "Vanilla ASGD": 2.0,
                "Delay-adaptive ASGD": 2.2,
                "Ringmaster ASGD": 1.4,
            },
        },
    }
    carried_comparator_values = [
        source_ratios["Shakespeare"][delay]["Vanilla ASGD"]
        for delay in ("D4", "D8")
    ]
    result = {
        "schema_version": 1,
        "claim": 5,
        "route": "exact primary-source comparator audit",
        "audit_status": "PASS",
        "claim_verdict": "FALSIFIED",
        "confidence": "MEDIUM",
        "imported_claim": (
            "On CIFAR-10 with delay factor D=4, Clipped ASGD achieves a "
            "1.8x wall-clock speedup over vanilla ASGD (Figure 2), and on "
            "Shakespeare it achieves 2.0-2.2x speedup depending on the delay "
            "regime (Figure 3)."
        ),
        "claim_contract": {
            "coordination_interpretation": (
                "the only named comparator, vanilla ASGD, is carried across "
                "the coordinated CIFAR-10 and Shakespeare clauses"
            ),
            "cifar_conjunct": {
                "dataset": "CIFAR-10",
                "delay": "D4",
                "comparator": "Vanilla ASGD",
                "speedup": 1.8,
            },
            "shakespeare_conjunct": {
                "dataset": "Shakespeare",
                "delays": ["D4", "D8"],
                "comparator": "Vanilla ASGD",
                "claimed_range": [2.0, 2.2],
            },
            "compound_rule": (
                "both coordinated conjuncts must be true; one contradiction "
                "falsifies the imported compound claim"
            ),
        },
        "source": {
            "latex_archive_sha256": (
                "625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915"
            ),
            "paper_html_sha256": (
                "292ba2ce9a95e41279fe1535ffa23b720f18fb2139c3e26324138c0d4a0304ff"
            ),
            "protocol_lines": "main.tex:758-784",
            "cifar_result_lines": "main.tex:786-790",
            "shakespeare_result_lines": "main.tex:821-833",
            "figure_hashes": {
                "cifar10_delay4.pdf": (
                    "695ccfa1fb503e56a92d4c9a25725799cb7030ed2932826a357c0429c5cb225a"
                ),
                "cifar10_delay8.pdf": (
                    "9d4cdc0ee60ede63237aaf770ab869baadf55d56d152dd732a46046e109b7e45"
                ),
                "shakespeare_delay4.pdf": (
                    "6affc402463c5bfb7a781c7bc95d6f68fd61ceada7999720b291a08ee404228b"
                ),
                "shakespeare_delay8.pdf": (
                    "3ba8e5ff9c7fcb2268bc32a571aaa7721903ad62cafd4feed8b0cb5b6d13de08"
                ),
            },
        },
        "source_reported_speedups": source_ratios,
        "comparison": {
            "cifar_conjunct_matches": True,
            "shakespeare_vanilla_values_by_delay": {
                "D4": carried_comparator_values[0],
                "D8": carried_comparator_values[1],
            },
            "shakespeare_claimed_range": [2.0, 2.2],
            "D4_inside_claimed_range": (
                2.0 <= carried_comparator_values[0] <= 2.2
            ),
            "D8_inside_claimed_range": (
                2.0 <= carried_comparator_values[1] <= 2.2
            ),
            "compound_claim_true": False,
        },
        "controls": {
            "corrected_vanilla_range_1_8_to_2_0": {
                "values": carried_comparator_values,
                "expected": "PASS",
            },
            "delay_adaptive_range_2_1_to_2_2": {
                "values": [
                    source_ratios["Shakespeare"]["D4"]["Delay-adaptive ASGD"],
                    source_ratios["Shakespeare"]["D8"]["Delay-adaptive ASGD"],
                ],
                "expected": "PASS only when comparator is explicitly changed",
            },
            "mixed_comparator_values": {
                "expected": (
                    "REJECT: changing comparator with delay is not the stated "
                    "depending-on-delay comparison"
                )
            },
        },
        "interpretation_risk": {
            "reason_for_medium_not_high": (
                "the Shakespeare clause omits a repeated comparator; a reader "
                "could instead supply Delay-adaptive ASGD, whose 2.1 and 2.2 "
                "values lie in the stated range"
            ),
            "why_falsified_under_contract": (
                "under the natural carried-comparator reading, the primary "
                "source directly reports 1.8x at D4 versus vanilla, below 2.0x"
            ),
            "unconstrained_comparator_reading": (
                "BLOCKED because a speedup range without a fixed comparator "
                "is not a machine-checkable empirical claim"
            ),
        },
        "limitations": [
            (
                "This route falsifies the imported claim text under its carried "
                "comparator; it does not assert that the paper's own Figure 3 "
                "prose is false."
            ),
            (
                "The author repository had no commits during the campaign, so "
                "original seeds and raw trajectories remain unavailable."
            ),
        ],
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
    print(json.dumps({"event": "CLAIM5_SOURCE_AUDIT", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
