"""Mandatory assumption-satisfying falsification route for Figure 4."""

from __future__ import annotations

import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim6_falsification"
VALIDATION_RAW = (
    ROOT / ".openresearch" / "artifacts" / "claim6_validation" / "raw_output.json"
)


def classify(candidate: dict[str, object]) -> str:
    protocol_complete = all(
        field["status"] == "matched" for field in candidate["protocol_fields"]
    )
    correct_quantifier_domain = bool(candidate["same_historical_realization"]) or bool(
        candidate["universally_quantified_claim"]
    )
    return (
        "FALSIFIED"
        if protocol_complete
        and correct_quantifier_domain
        and bool(candidate["contradiction_established"])
        else "BLOCKED"
    )


def main() -> int:
    started = time.perf_counter()
    validation = json.loads(VALIDATION_RAW.read_text(encoding="utf-8"))
    protocol_fields = [
        {
            "field": "dataset",
            "paper_requirement": "CIFAR-10",
            "candidate_evidence": "CIFAR-10 train/test archives",
            "status": "matched",
            "material": True,
        },
        {
            "field": "workers_and_concurrency",
            "paper_requirement": "16 workers, full concurrency",
            "candidate_evidence": "16 simulated workers, 16 active jobs",
            "status": "matched",
            "material": True,
        },
        {
            "field": "worker_service_times",
            "paper_requirement": "eight at 1 and eight at D",
            "candidate_evidence": "exact 8+8 service-time vector",
            "status": "matched",
            "material": True,
        },
        {
            "field": "delay_factors",
            "paper_requirement": "D in {4,8}",
            "candidate_evidence": "D=4 and D=8",
            "status": "matched",
            "material": True,
        },
        {
            "field": "label_skew",
            "paper_requirement": "Dirichlet alpha=0.5",
            "candidate_evidence": "class-wise Dirichlet alpha=0.5",
            "status": "matched",
            "material": True,
        },
        {
            "field": "target_and_caps",
            "paper_requirement": "70%; caps 8000 and 12000",
            "candidate_evidence": "exact target and caps",
            "status": "matched",
            "material": True,
        },
        {
            "field": "hyperparameter_domain",
            "paper_requirement": "LR 2^-9..2^-1; c in {0.5,1,2,4}",
            "candidate_evidence": "complete selection grids",
            "status": "matched",
            "material": True,
        },
        {
            "field": "seed_count",
            "paper_requirement": "three seeds",
            "candidate_evidence": "three independent validation seeds",
            "status": "matched",
            "material": True,
        },
        {
            "field": "exact_two_layer_cnn",
            "paper_requirement": "paper's unspecified two-layer CNN",
            "candidate_evidence": "declared 878,538-parameter two-convolution CNN",
            "status": "unresolved",
            "material": True,
        },
        {
            "field": "batch_and_preprocessing",
            "paper_requirement": "not reported",
            "candidate_evidence": "batch 64, normalization, no augmentation",
            "status": "unresolved",
            "material": True,
        },
        {
            "field": "partition_sampler",
            "paper_requirement": "not reported beyond Dirichlet alpha",
            "candidate_evidence": "declared class-wise allocation",
            "status": "unresolved",
            "material": True,
        },
        {
            "field": "exact_seed_values",
            "paper_requirement": "not reported",
            "candidate_evidence": "20260730..20260732",
            "status": "unresolved",
            "material": True,
        },
        {
            "field": "event_queue_and_ties",
            "paper_requirement": "not reported",
            "candidate_evidence": "declared deterministic heap and tie order",
            "status": "unresolved",
            "material": True,
        },
        {
            "field": "evaluation_cadence",
            "paper_requirement": "not reported",
            "candidate_evidence": "200 simulated time units",
            "status": "unresolved",
            "material": True,
        },
        {
            "field": "curve_aggregation",
            "paper_requirement": "mean of three seeds with 2-sigma bars",
            "candidate_evidence": "paired first-hit bootstrap with cadence interval",
            "status": "mismatched",
            "material": True,
        },
        {
            "field": "author_implementation",
            "paper_requirement": "linked implementation",
            "candidate_evidence": "linked repository has no commits or refs",
            "status": "unresolved",
            "material": True,
        },
    ]
    actual = {
        "name": "real CIFAR-10 three-seed reconstruction",
        "protocol_fields": protocol_fields,
        "same_historical_realization": False,
        "universally_quantified_claim": False,
        "contradiction_established": (
            validation["aggregates"]["4"]["combined_95_interval"][1] < 1.2
        ),
    }
    positive_control = {
        "name": "fully specified universal counterexample control",
        "protocol_fields": [
            {
                "field": "fully_specified_domain",
                "status": "matched",
                "material": True,
            }
        ],
        "same_historical_realization": False,
        "universally_quantified_claim": True,
        "contradiction_established": True,
    }
    historical_control = {
        "name": "original-raw-data contradiction control",
        "protocol_fields": [
            {
                "field": "original_raw_and_protocol",
                "status": "matched",
                "material": True,
            }
        ],
        "same_historical_realization": True,
        "universally_quantified_claim": False,
        "contradiction_established": True,
    }
    negative_control = {
        "name": "assumption-violating mismatch control",
        "protocol_fields": [
            {
                "field": "dataset",
                "status": "mismatched",
                "material": True,
            }
        ],
        "same_historical_realization": False,
        "universally_quantified_claim": True,
        "contradiction_established": True,
    }
    actual_classification = classify(actual)
    controls = {
        "universal_positive": {
            "classification": classify(positive_control),
            "candidate": positive_control,
        },
        "historical_positive": {
            "classification": classify(historical_control),
            "candidate": historical_control,
        },
        "assumption_violation_negative": {
            "classification": classify(negative_control),
            "candidate": negative_control,
        },
    }
    control_pass = (
        controls["universal_positive"]["classification"] == "FALSIFIED"
        and controls["historical_positive"]["classification"] == "FALSIFIED"
        and controls["assumption_violation_negative"]["classification"] == "BLOCKED"
    )
    status = "PASS" if actual_classification == "BLOCKED" and control_pass else "FAIL"
    result = {
        "schema_version": 1,
        "claim_number": 6,
        "route": "mandatory fourth route dedicated to valid falsification",
        "exact_claim": (
            "Figure 4 reports that on label-skew CIFAR-10 Clipped ASGD "
            "improved over vanilla ASGD by 1.2x at D=4 and 1.3x at D=8."
        ),
        "claim_quantifier": (
            "A descriptive claim about the paper's historical three-seed "
            "realization, not a universal guarantee over future seeds or "
            "unspecified reconstructions."
        ),
        "source": {
            "latex_archive_sha256": (
                "625fcd8270456342db8754427250eaba862686576b27bc5dbec84d9af5aa4915"
            ),
            "main_tex_lines": "758-769, 851-910",
            "D4_figure_sha256": (
                "122860beeff322b8f7fb1d1800220ee4eeb0a148404279f7de583c30abaa6551"
            ),
            "D8_figure_sha256": (
                "a3541e5245c696cf19c775454357eef24238528ea1fb386919bd632438fee26f"
            ),
            "author_repo_state": "zero commits and no refs at campaign audit",
        },
        "candidate": actual,
        "candidate_classification": actual_classification,
        "candidate_validation_sha256": (
            "6bc2a8fe3148f83d72869d7f8fc50ffe0e303cde359b81d200edd1c9804aa539"
        ),
        "candidate_observation": {
            "D4_speedup": validation["aggregates"]["4"]["observed_speedup"],
            "D4_combined_95_interval": validation["aggregates"]["4"][
                "combined_95_interval"
            ],
            "D8_all_targets_reached": validation["aggregates"]["8"][
                "all_targets_reached"
            ],
            "D8_censored_seeds": validation["aggregates"]["8"]["censored_seeds"],
        },
        "controls": controls,
        "control_pass": control_pass,
        "falsification_succeeded": actual_classification == "FALSIFIED",
        "verdict": actual_classification,
        "status": status,
        "reason": (
            "The reconstruction raises a substantive replication discrepancy "
            "but does not use the original realized seeds/raw curves, is not "
            "identical on every material protocol field, and tests a historical "
            "descriptive claim rather than a universal claim."
        ),
        "unblockers": [
            "author source implementing the exact Figure 4 protocol",
            "original per-seed raw curves and seed identifiers",
            "the omitted architecture, data, scheduler, cadence, and aggregation details",
        ],
        "compute": {
            "estimated_cores": 1,
            "actual_processes": 1,
            "selected_backend": "local",
            "expected_runtime": "under five minutes",
            "gpu_allowed": False,
        },
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    raw = ARTIFACT_DIR / "raw_output.json"
    raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "CLAIM6_FALSIFICATION_RAW", "result": result}, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
