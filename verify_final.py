#!/usr/bin/env python3
"""Verify the published documentation, evidence, and provenance contract."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_STATUS = "PARTIAL_C1_C2_VERIFIED_C3_NOVELTY_FALSIFIED_RATE_BLOCKED_C4_BLOCKED_C5_FALSIFIED_VANILLA_COMPARATOR_C6_BLOCKED_HISTORICAL_SCORE_4_OF_12_NO_CURRENT_SCORE"
EXPECTED_BRANCHES = {
    "audit/c1-c2-expectation-rates",
    "audit/c3-prior-art",
    "audit/c3-published-proof",
    "audit/c3-repaired-freedman",
    "audit/c4-cifar-resnet",
    "audit/c4-dataset-checksum",
    "audit/c4-pilot",
    "audit/c4-source-identifiability",
    "audit/c4-trained-resnet",
    "audit/c5-comparator-source",
    "audit/c6-cifar-pilot",
    "audit/c6-cnn-protocol",
    "audit/c6-d4-sweep",
    "audit/c6-d4-worker-init",
    "audit/c6-d8-sweep",
    "audit/c6-queue-calibration",
    "audit/c6-scheduler-finite",
    "audit/c6-source-falsification",
    "audit/c6-three-seed-validation",
    "historical/c4-falsification-route",
    "historical/judged-baseline",
    "main",
    "release/evaluator-candidate",
    "release/final-regression",
    "release/portable-hash-pin",
}
EXPECTED_COMMITS = 58
CANONICAL_IDENTITY = "MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>"


def load(path: str):
    return json.loads((ROOT / path).read_text())


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"verification failed: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def published_branches() -> set[str]:
    remote = {
        name.removeprefix("origin/")
        for name in git(
            "for-each-ref", "refs/remotes/origin", "--format=%(refname:short)"
        ).splitlines()
        if name.startswith("origin/") and name != "origin/HEAD"
    }
    return remote or set(git("for-each-ref", "refs/heads", "--format=%(refname:short)").splitlines())


def main() -> None:
    claims = load("claims.json")
    verdicts = load("reproduction_verdicts.json")
    manifest = load("EVIDENCE_MANIFEST.json")
    state = load("AUTONOMOUS_STATE.json")
    live = load(".openresearch/artifacts/provenance/live_verdict.filtered.json")
    expectation = load(".openresearch/artifacts/expectation_theorems/raw_output.json")
    c3 = load(".openresearch/artifacts/claim3_route3/raw_output.json")
    c4 = load(".openresearch/artifacts/claim4/raw_output.json")
    c4_trained = load(".openresearch/artifacts/claim4_trained/raw_output.json")
    c4_tail = load(".openresearch/artifacts/claim4_tail_audit/raw_output.json")
    c5 = load(".openresearch/artifacts/claim5_source_audit/raw_output.json")
    c6 = load(".openresearch/artifacts/claim6_validation/raw_output.json")
    c6_falsification = load(".openresearch/artifacts/claim6_falsification/raw_output.json")
    preflight = load(".openresearch/artifacts/release_candidate/preflight_output.json")
    formal = load(".openresearch/artifacts/release_candidate/formal_run.json")
    red_team = load(".openresearch/artifacts/release_candidate/red_team_pass2.json")
    subset = load("hf_space_release/evidence/release_candidate/old_new_subset_check.json")
    readme = (ROOT / "README.md").read_text()
    citation = (ROOT / "CITATION.cff").read_text()

    expected_statuses = {
        "C1": "VERIFIED_SCOPED_MEDIUM",
        "C2": "VERIFIED_SCOPED_MEDIUM",
        "C3": "FALSIFIED_COMPOUND_NOVELTY_BLOCKED_NARROW_RATE",
        "C4": "BLOCKED_HISTORICAL_PROTOCOL",
        "C5": "FALSIFIED_SCOPED_VANILLA_COMPARATOR_MEDIUM",
        "C6": "BLOCKED_HISTORICAL_PROTOCOL_RECONSTRUCTION",
    }
    require(claims["overall_status"] == EXPECTED_STATUS, "claims overall status")
    require(state["overall_status"] == EXPECTED_STATUS, "state overall status")
    require(verdicts["overall_status"] == EXPECTED_STATUS, "verdict overall status")
    require(verdicts["claim_statuses"] == expected_statuses, "verdict statuses")
    require({claim["id"]: claim["status"] for claim in claims["claims"]} == expected_statuses, "claim statuses")
    require(all((ROOT / path).exists() for path in manifest["required_paths"]), "manifest paths")
    for artifact in manifest["artifacts"]:
        require(sha256(ROOT / artifact["path"]) == artifact["sha256"], f"artifact digest {artifact['path']}")
    require(live["score"] == "4/12", "historical score")
    require(expectation["status"] == "PASS" and expectation["verdicts"] == {"claim_1": "VERIFIED", "claim_2": "VERIFIED"}, "expectation claims")
    require(c3["claim_verdict"] == "FALSIFIED", "claim 3 compound verdict")
    require(c3["subclaim_verdicts"] == {"compound_claim_3": "FALSIFIED", "novelty": "FALSIFIED", "specific_theta_rate": "BLOCKED"}, "claim 3 subclaims")
    require(c4["verdict"] == "BLOCKED" and c4_trained["verdict"] == "BLOCKED" and c4_tail["verdict"] == "BLOCKED", "claim 4 routes")
    require(c4["primary_estimate"]["theta"] < 0.1 and c4_trained["primary_estimate"]["theta"] < 0.3 and c4_tail["maximum_theta"]["theta"] < 0.3, "claim 4 estimates")
    require(c5["claim_verdict"] == "FALSIFIED" and c5["comparison"]["D4_inside_claimed_range"] is False and c5["comparison"]["D8_inside_claimed_range"] is True, "claim 5 comparator verdict")
    require(c6["verdict"] == "BLOCKED" and c6["aggregates"]["4"]["observed_speedup"] < 1.1 and c6["aggregates"]["8"]["all_targets_reached"] is False, "claim 6 validation")
    require(c6_falsification["verdict"] == "BLOCKED" and c6_falsification["falsification_succeeded"] is False, "claim 6 falsification boundary")
    require(preflight["status"] == "PASS" and preflight["expected_verdicts"] == {"1": "VERIFIED", "2": "VERIFIED", "3": "FALSIFIED", "4": "BLOCKED", "5": "FALSIFIED", "6": "BLOCKED"}, "release candidate")
    require(formal["status"] == "PASS" and formal["score"]["previous_live"] == "4/12" and formal["score"]["judge_result_claimed"] is False, "formal release run")
    require(red_team["status"] == "PASS" and red_team["claim_conclusions"]["6"]["verdict_located"] == "BLOCKED", "red-team release review")
    require(subset["status"] == "PASS" and subset["old_file_set_is_subset"] is True and subset["missing_protected_paths"] == [], "historical subset")
    require("https://arxiv.org/abs/2606.13287" in citation and EXPECTED_STATUS in readme and "no current judge score claim" in readme, "README and citation")

    branches = published_branches()
    require(branches == EXPECTED_BRANCHES, "published branches")
    require(not any(branch.startswith("orx/") for branch in branches), "legacy orx branch")
    require(int(git("rev-list", "--all", "--count")) == EXPECTED_COMMITS, "reachable commit count")
    identities = git("log", "--all", "--format=%an <%ae>\n%cn <%ce>").splitlines()
    require(identities and all(identity == CANONICAL_IDENTITY for identity in identities), "canonical commit identity")

    print(
        "FINAL_AUDIT=VERIFIED "
        f"branches={len(branches)} commits={EXPECTED_COMMITS} "
        "claims=C1:C2_verified,C3_novelty_falsified_rate_blocked,C4_blocked,C5_vanilla_falsified,C6_blocked "
        "historical_score=4/12 current_score_claim=false publication_allowed=false"
    )


if __name__ == "__main__":
    main()
