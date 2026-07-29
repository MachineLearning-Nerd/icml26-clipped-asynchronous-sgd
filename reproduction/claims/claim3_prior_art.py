"""Route 3 for Claim 3: falsify the broad first-result assertion."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim3_route3"


def amplified_failure_bound(delta: float) -> dict[str, float | int]:
    repetitions = math.ceil(math.log2(1 / delta))
    return {
        "delta": delta,
        "repetitions": repetitions,
        "failure_upper_bound": 2.0 ** (-repetitions),
    }


def main() -> int:
    started = time.perf_counter()
    delta_checks = [
        amplified_failure_bound(delta) for delta in (0.2, 0.05, 0.01, 1e-6)
    ]
    result = {
        "schema_version": 1,
        "claim": 3,
        "route": "primary-source prior-art falsification",
        "audit_status": "PASS",
        "claim_verdict": "FALSIFIED",
        "confidence": "HIGH",
        "logical_contract": {
            "imported_claim_is_conjunction": [
                {
                    "id": "novelty",
                    "statement": (
                        "the paper gives the first high-probability convergence "
                        "guarantee in asynchronous SGD/optimization"
                    ),
                },
                {
                    "id": "specific_rate",
                    "statement": (
                        "Theorems 4.3 and 5.2 have the displayed theta-governed "
                        "polylogarithmic delta dependence"
                    ),
                },
            ],
            "classification_rule": (
                "a conjunction is false when any material conjunct is false"
            ),
        },
        "target_source": {
            "paper": "Clipping Makes Distributed and Federated Asynchronous SGD Robust to Stragglers",
            "latex_archive_sha256": (
                "625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915"
            ),
            "broad_novelty_anchor": "main.tex:601-603",
            "wording_scope": "first time in asynchronous optimization",
            "specific_rate_anchors": "main.tex:604-614,724-735",
        },
        "prior_result": {
            "title": "Asynchronous Stochastic Optimization Robust to Arbitrary Delays",
            "authors": [
                "Alon Cohen",
                "Amit Daniely",
                "Yoel Drori",
                "Tomer Koren",
                "Mariano Schain",
            ],
            "arxiv_id": "2106.11879",
            "publication": "NeurIPS 2021",
            "arxiv_submission_date": "2021-06-22",
            "predates_target": True,
            "primary_urls": [
                "https://arxiv.org/abs/2106.11879",
                (
                    "https://proceedings.neurips.cc/paper/2021/hash/"
                    "4b85256c4881edb6c0776df5d81f6236-Abstract.html"
                ),
            ],
            "retrieval_date": "2026-07-29",
            "explicit_user_agent_used": True,
            "pdf_sha256": (
                "bcfc13492b4e6aa73f04e9d55bdd5a14b028c0e0bef79b8e74142300e69b9798"
            ),
            "source_archive_sha256": (
                "95cb673ff942137d6822dc250ec94f82693fdab423d981360cc4578f960d8205"
            ),
            "paper_main_tex_sha256": (
                "6e6b6e98c4ef8a9829fc87370a1700bbcb01bbb67bcdcdad3d96e8ca53ac97f8"
            ),
            "anchors": {
                "async_sgd_description": "paper_main.tex:99-116",
                "algorithm": "paper_main.tex:265-290",
                "theorem": "paper_main.tex:293-311",
                "arbitrary_delta_amplification": "paper_main.tex:317-321",
            },
            "scope_audit": {
                "stochastic_gradient_algorithm": True,
                "algorithm_name": "Picky SGD",
                "asynchronous_delayed_updates": True,
                "smooth_nonconvex_objective": True,
                "stationarity_convergence_guarantee": True,
                "base_success_probability": 0.5,
                "arbitrary_success_probability": "1-delta",
                "amplification_cost": "O(log(1/delta)) independent restarts",
                "delay_model": "arbitrary delays independent of gradient noise",
                "event": "some iterate has gradient norm at most epsilon",
                "same_average_gradient_event_as_target": False,
            },
        },
        "amplification_certificate": {
            "premise": (
                "each independent run succeeds with probability at least 1/2"
            ),
            "repetitions": "k=ceil(log2(1/delta))",
            "failure_probability": "(1/2)^k <= delta",
            "checks": delta_checks,
        },
        "scope_reasoning": {
            "novelty_contradiction": (
                "The target's source says first in asynchronous optimization, "
                "without restricting the event to an average gradient norm. "
                "The 2021 result is an asynchronous stochastic-gradient method "
                "with an arbitrary-1-delta stationarity guarantee."
            ),
            "algorithm_modification_is_in_scope": (
                "Picky SGD conditionally skips stale gradients; the target "
                "method likewise modifies ASGD by clipping. Both are named "
                "asynchronous stochastic-gradient algorithms."
            ),
            "different_stationarity_event": (
                "The prior result controls the best iterate, not the target's "
                "average norm. This prevents it from refuting the specific rate "
                "theorem, but does not rescue the unrestricted first-result phrase."
            ),
        },
        "subclaim_verdicts": {
            "novelty": "FALSIFIED",
            "specific_theta_rate": "BLOCKED",
            "compound_claim_3": "FALSIFIED",
        },
        "controls": {
            "serial_high_probability_sgd": {
                "asynchronous": False,
                "classification": "NOT_A_NOVELTY_COUNTEREXAMPLE",
            },
            "later_asynchronous_high_probability_result": {
                "predates_target": False,
                "classification": "NOT_A_NOVELTY_COUNTEREXAMPLE",
            },
            "asynchronous_expectation_only_result": {
                "arbitrary_delta_guarantee": False,
                "classification": "NOT_A_NOVELTY_COUNTEREXAMPLE",
            },
            "asynchronous_runtime_only_high_probability_result": {
                "optimization_convergence_event": False,
                "classification": "NOT_A_NOVELTY_COUNTEREXAMPLE",
            },
        },
        "limitations": [
            (
                "The prior result does not contradict the precise average-gradient "
                "rate of Theorems 4.3/5.2; routes 1 and 2 leave that subclaim blocked."
            ),
            (
                "The FALSIFIED verdict applies to the imported compound claim "
                "because its broad first-result conjunct is demonstrably false."
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
    print(json.dumps({"event": "CLAIM3_ROUTE3_PRIOR_ART", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
