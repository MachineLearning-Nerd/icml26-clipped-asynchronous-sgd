"""Build the exact text-only Space upload allowlist and release evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SECRET_PATTERNS = {
    "hugging_face_token": re.compile(rb"\bhf_[A-Za-z0-9]{20,}\b"),
    "github_token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(rb"\bAKIA[A-Z0-9]{16}\b"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files_under(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("overlay", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("protected_paths", type=Path)
    args = parser.parse_args()
    overlay = args.overlay.resolve()
    candidate = args.candidate.resolve()

    old_paths = [
        line.strip()
        for line in args.protected_paths.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    candidate_paths = {
        path.relative_to(candidate).as_posix() for path in files_under(candidate)
    }
    candidate_paths.update(path.relative_to(overlay).as_posix() for path in files_under(overlay))
    missing_old_paths = sorted(set(old_paths) - candidate_paths)
    subset_payload = {
        "schema_version": 1,
        "judged_revision": "471748694e91b08b071d3d13c30d84b3091b5971",
        "protected_path_count": len(old_paths),
        "candidate_path_count": len(candidate_paths),
        "missing_protected_paths": missing_old_paths,
        "old_file_set_is_subset": not missing_old_paths,
        "status": "PASS" if not missing_old_paths else "FAIL",
    }
    release_evidence = overlay / "evidence" / "release_candidate"
    write_json(release_evidence / "old_new_subset_check.json", subset_payload)

    invalid_utf8: list[str] = []
    secret_findings: dict[str, int] = {name: 0 for name in SECRET_PATTERNS}
    scanned_count = 0
    for path in files_under(overlay):
        relative = path.relative_to(overlay).as_posix()
        data = path.read_bytes()
        if b"\0" in data:
            invalid_utf8.append(relative)
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            invalid_utf8.append(relative)
            continue
        scanned_count += 1
        for name, pattern in SECRET_PATTERNS.items():
            secret_findings[name] += len(pattern.findall(data))
    finding_count = sum(secret_findings.values())
    secret_payload = {
        "schema_version": 1,
        "scope": "all candidate upload text",
        "scanned_file_count": scanned_count,
        "invalid_text_paths": sorted(invalid_utf8),
        "credential_shaped_finding_counts": secret_findings,
        "finding_count": finding_count,
        "values_printed": False,
        "status": "PASS" if not invalid_utf8 and finding_count == 0 else "FAIL",
    }
    write_json(release_evidence / "secret_scan.json", secret_payload)

    manifest_path = overlay / "MANIFEST.sha256"
    allowlist_path = overlay / "UPLOAD_ALLOWLIST.txt"
    manifest_path.touch()
    allowlist_path.touch()
    relative_paths = [path.relative_to(overlay).as_posix() for path in files_under(overlay)]
    allowlist_path.write_text("\n".join(relative_paths) + "\n", encoding="utf-8")
    manifest_lines = [
        "# SHA-256 for every upload allowlist path except MANIFEST.sha256 itself.",
        *[
            f"{sha256(overlay / relative)}  {relative}"
            for relative in relative_paths
            if relative != "MANIFEST.sha256"
        ],
    ]
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    result = {
        "event": "SPACE_RELEASE_METADATA",
        "status": (
            "PASS"
            if subset_payload["status"] == "PASS"
            and secret_payload["status"] == "PASS"
            else "FAIL"
        ),
        "allowlist_count": len(relative_paths),
        "manifest_hashed_count": len(manifest_lines) - 1,
        "subset": subset_payload,
        "secret_scan": secret_payload,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
