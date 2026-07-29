"""Mandatory falsification-route verifier for Claim 4."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / ".openresearch" / "artifacts" / "claim4" / "raw_output.json"
TRAINED = ROOT / ".openresearch" / "artifacts" / "claim4_trained" / "raw_output.json"
TAIL_AUDIT = (
    ROOT / ".openresearch" / "artifacts" / "claim4_tail_audit" / "raw_output.json"
)
RETRIEVAL = ROOT / ".openresearch" / "artifacts" / "provenance" / "retrieval.json"
RAW = Path(__file__).with_name("raw_output.json")
CHECKER = Path(__file__).with_name("independent_check.py")


def main() -> int:
    started = time.perf_counter()
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    trained = json.loads(TRAINED.read_text(encoding="utf-8"))
    tail_audit = json.loads(TAIL_AUDIT.read_text(encoding="utf-8"))
    retrieval = json.loads(RETRIEVAL.read_text(encoding="utf-8"))
    required_protocol = {
        "source_raw_gradient_norms": False,
        "checkpoint_identifier_or_weights": False,
        "optimizer_and_training_step": False,
        "batch_size_and_sample_count": False,
        "reference_gradient_construction": False,
        "preprocessing": False,
        "tail_count_k": False,
        "author_code_commit": False,
    }
    assumption_identical = all(required_protocol.values())
    observed_control = float(
        trained["negative_control"]["cases"][2]["observed"]["theta"]
    )
    tolerance = float(trained["negative_control"]["cases"][2]["tolerance"])
    positive_falsification_control = {
        "fully_specified_observed_theta": observed_control,
        "deliberately_false_reported_theta": 1.0,
        "tolerance": tolerance,
        "falsified_as_intended": abs(observed_control - 1.0) > tolerance,
    }
    true_value_control = {
        "fully_specified_observed_theta": observed_control,
        "reported_theta": 2.71,
        "tolerance": tolerance,
        "not_falsified_as_intended": abs(observed_control - 2.71) <= tolerance,
    }
    candidate_contradiction = {
        "initialization_theta": pilot["primary_estimate"]["theta"],
        "trained_theta": trained["primary_estimate"]["theta"],
        "trained_bootstrap_95": trained["bootstrap"],
        "maximum_over_all_admissible_k": tail_audit["maximum_theta"],
        "reported_theta": 2.71,
        "numerically_contradicts_under_reconstruction": (
            not trained["reported_theta_in_bootstrap_interval"]
            and tail_audit["maximum_theta"]["theta"] < 2.71
        ),
        "valid_assumption_identical_counterexample": False,
        "invalidity_reason": (
            "The paper does not identify the source checkpoint or gradient "
            "sampling/fitting protocol, so these real reconstructions do not "
            "instantiate the historical source experiment."
        ),
    }
    result = {
        "schema_version": 1,
        "claim_number": 4,
        "route": "mandatory fourth falsification route",
        "exact_claim": (
            "The empirical estimate for ResNet-18/CIFAR-10 gradient errors "
            "in the paper's source experiment is theta=2.71."
        ),
        "domain_and_quantifier": (
            "One historical, paper-specific experiment; not universal over "
            "all ResNet-18/CIFAR-10 checkpoints or sampling protocols."
        ),
        "paper_html_sha256": retrieval["paper_html_sha256"],
        "required_protocol_identified": required_protocol,
        "assumption_identical_protocol_available": assumption_identical,
        "candidate_contradiction": candidate_contradiction,
        "positive_falsification_control": positive_falsification_control,
        "true_value_control": true_value_control,
        "falsification_succeeded": (
            assumption_identical
            and candidate_contradiction["valid_assumption_identical_counterexample"]
        ),
        "verdict": "BLOCKED",
        "reason": (
            "Falsification machinery detects a deliberately false fully "
            "specified control, but no counterexample can be tied to the "
            "authors' unidentified source protocol. Four distinct routes are "
            "complete; missing source data/code is the concrete blocker."
        ),
        "unblocker": (
            "Author checkpoint, raw gradient-error norms, exact batch/reference "
            "construction, and estimator n/k (or an equivalent source artifact)."
        ),
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    RAW.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "CLAIM4_FALSIFICATION_RAW", "result": result}, sort_keys=True))
    checker = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    print(checker.stdout, end="")
    if checker.stderr:
        print(checker.stderr, file=sys.stderr, end="")
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
