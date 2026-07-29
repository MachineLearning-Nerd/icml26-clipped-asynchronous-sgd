"""Fail-closed cumulative release and evaluator-visibility verifier."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OVERLAY = ROOT / "hf_space_release" if (ROOT / "hf_space_release").is_dir() else ROOT
ARTIFACT = Path(__file__).resolve().parent
EXPECTED_RAW_HASHES = {
    "expectation_theorems": "32562b2bf3d348dc31de2d685712b7e86b371aa6abaa33c62006fc8e56f38906",
    "claim3_route3": "38d219af2586f5a2c3949104e9dad2bb111ed5b1b7b8a173e176d435fe13e29d",
    "claim4_falsification": "aa2440e9bc8aaeae60f41660cda601a4d6b56392a46183d5755f28b79a015c4e",
    "claim5_source_audit": "e2999b9b5c407484f4af0777a5e4889ca2f9e07abc2d46048d883020959ce82c",
    "claim6_validation": "6bc2a8fe3148f83d72869d7f8fc50ffe0e303cde359b81d200edd1c9804aa539",
    "claim6_falsification": "e685e92c1a1d5889bf8090511d435ff7cadebe39044f9b0def517dc9d8737ff6",
}
EXPECTED_VERDICTS = {
    "1": "VERIFIED",
    "2": "VERIFIED",
    "3": "FALSIFIED",
    "4": "BLOCKED",
    "5": "FALSIFIED",
    "6": "BLOCKED",
}
SECRET_PATTERNS = (
    re.compile(rb"\bhf_[A-Za-z0-9]{20,}\b"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bAKIA[A-Z0-9]{16}\b"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_redteam_module():
    path = ROOT / "scripts" / "redteam_space_candidate.py"
    spec = importlib.util.spec_from_file_location("redteam_space_candidate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load red-team traversal")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    errors: list[str] = []
    checks: dict[str, object] = {}

    observed_hashes = {}
    for claim, expected in EXPECTED_RAW_HASHES.items():
        path = ROOT / ".openresearch" / "artifacts" / claim / "raw_output.json"
        observed = sha256(path)
        observed_hashes[claim] = observed
        if observed != expected:
            errors.append(f"{claim} formal raw hash mismatch")
    checks["formal_raw_hashes"] = observed_hashes

    logbook = json.loads((OVERLAY / "logbook.json").read_text(encoding="utf-8"))
    if logbook.get("space_id") != "DineshAI/AmgjQp4vrr":
        errors.append("candidate targets the wrong Space")
    navigation = [
        (child["slug"], child["title"]) for child in logbook["root"]["children"]
    ]
    if navigation[0][0] != "current":
        errors.append("current verification is not first in navigation")
    if navigation[-1] != ("overview", "Historical rejected baseline"):
        errors.append("historical rejected baseline is not last and exactly labelled")

    for claim, verdict in EXPECTED_VERDICTS.items():
        text = (OVERLAY / f"pages/claim-{claim}/page.md").read_text(encoding="utf-8")
        if f"Claim {claim} — {verdict}" not in text:
            errors.append(f"claim {claim} page does not expose {verdict}")

    allowlist_path = OVERLAY / "UPLOAD_ALLOWLIST.txt"
    manifest_path = OVERLAY / "MANIFEST.sha256"
    allowlist = [
        line
        for line in allowlist_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    actual_paths = sorted(
        path.relative_to(OVERLAY).as_posix()
        for path in OVERLAY.rglob("*")
        if path.is_file()
    )
    if allowlist != actual_paths:
        errors.append("upload allowlist is not the exact sorted overlay file set")
    if any(Path(path).is_absolute() or ".." in Path(path).parts for path in allowlist):
        errors.append("upload allowlist contains an unsafe path")

    manifest_entries = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, relative = line.split(maxsplit=1)
        manifest_entries[relative] = digest
    expected_manifest_paths = set(allowlist) - {"MANIFEST.sha256"}
    if set(manifest_entries) != expected_manifest_paths:
        errors.append("manifest scope does not match allowlist minus itself")
    for relative, expected in manifest_entries.items():
        if sha256(OVERLAY / relative) != expected:
            errors.append(f"manifest hash mismatch: {relative}")

    secret_finding_count = 0
    for relative in allowlist:
        data = (OVERLAY / relative).read_bytes()
        if b"\0" in data:
            errors.append(f"non-text upload path: {relative}")
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF8 upload path: {relative}")
        secret_finding_count += sum(len(pattern.findall(data)) for pattern in SECRET_PATTERNS)
    if secret_finding_count:
        errors.append("credential-shaped strings found in upload text")
    checks["secret_scan_finding_count"] = secret_finding_count

    subset = json.loads(
        (OVERLAY / "evidence/release_candidate/old_new_subset_check.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        subset.get("status") != "PASS"
        or subset.get("protected_path_count") != 13
        or not subset.get("old_file_set_is_subset")
    ):
        errors.append("protected judged file subset proof failed")

    formal_run = json.loads(
        (OVERLAY / "evidence/release_candidate/formal_run.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        formal_run.get("status") != "PASS"
        or formal_run.get("verifier_count") != 17
        or set(formal_run.get("verifier_exit_codes", {}).values()) != {0}
        or formal_run.get("git_sha")
        != "cf23e2e84f931be528724d7720df3dec5127bf88"
        or formal_run.get("fixed_command")
        != "uv run --frozen python -m reproduction.run"
    ):
        errors.append("authoritative cumulative formal run record is invalid")

    pass1 = json.loads((ARTIFACT / "red_team_pass1.json").read_text(encoding="utf-8"))
    pass2 = json.loads(
        (OVERLAY / "evidence/release_candidate/red_team_pass2.json").read_text(
            encoding="utf-8"
        )
    )
    if pass1.get("status") != "FAIL" or not pass1.get("errors"):
        errors.append("initial evaluator-blind review did not record discoverability gaps")
    if pass2.get("status") != "PASS" or pass2.get("errors"):
        errors.append("post-fix evaluator-blind review did not pass")

    redteam = load_redteam_module()
    with tempfile.TemporaryDirectory(prefix="orx-release-check-") as directory:
        candidate = Path(directory)
        shutil.copytree(OVERLAY, candidate, dirs_exist_ok=True)
        historical = (
            OVERLAY
            / "historical"
            / "judged-471748694e91b08b071d3d13c30d84b3091b5971"
        )
        (candidate / "pages/overview").mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            historical / "pages/overview/page.md",
            candidate / "pages/overview/page.md",
        )
        traversal = redteam.review(candidate)
        if traversal["status"] != "PASS":
            errors.extend(f"fresh traversal: {error}" for error in traversal["errors"])

        missing_page = candidate / "pages/claim-1/page.md"
        missing_page.unlink()
        negative_missing_page = redteam.review(candidate)["status"] == "FAIL"
    negative_hash = hashlib.sha256(b"modified evidence").hexdigest() != next(
        iter(EXPECTED_RAW_HASHES.values())
    )
    protected_paths = set(
        (
            ROOT
            / ".openresearch/artifacts/provenance/judged_space_files.txt"
        ).read_text(encoding="utf-8").splitlines()
    )
    reduced_candidate = protected_paths - {".gitattributes"}
    negative_subset = not protected_paths.issubset(reduced_candidate)
    negative_controls = {
        "missing_candidate_page_rejected": negative_missing_page,
        "modified_raw_hash_rejected": negative_hash,
        "missing_protected_path_rejected": negative_subset,
    }
    if not all(negative_controls.values()):
        errors.append("release negative control did not fail as intended")

    notebook = subprocess.run(
        [
            sys.executable,
            "-m",
            "marimo",
            "check",
            "--strict",
            "notebooks/clipped_asgd_reproduction.py",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if notebook.returncode != 0:
        errors.append("marimo notebook strict validation failed")
    report_directory = ROOT / "reports/clipping-asgd"
    image_paths = sorted((report_directory / "images").glob("*.png"))
    if report_directory.is_dir() and (
        len(image_paths) != 5 or any(path.stat().st_size == 0 for path in image_paths)
    ):
        errors.append("visual report does not have five nonempty evidence figures")

    result = {
        "event": "RELEASE_CANDIDATE_VERIFY",
        "status": "PASS" if not errors else "FAIL",
        "expected_verdicts": EXPECTED_VERDICTS,
        "forecast": {
            "previous_live_score": "4/12",
            "conservative_range": "6-9/12",
            "best_supported_possible": "9/12",
            "judge_result_claimed": False,
        },
        "allowlist_count": len(allowlist),
        "manifest_hashed_count": len(manifest_entries),
        "authoritative_formal_run": formal_run["run_id"],
        "fresh_traversal_opened_count": len(traversal["opened_files"]),
        "negative_controls": negative_controls,
        "report_figure_count": len(image_paths) if report_directory.is_dir() else None,
        "notebook_check_exit_code": notebook.returncode,
        "checks": checks,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
