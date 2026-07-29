"""Fail-closed static verifier for the completed checksum-identical mirror run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


EVIDENCE = Path(__file__).with_name("run_evidence.json")
EXPECTED_MD5 = "c58f30108f718f92721af3b95e74349a"
EXPECTED_RAW_SHA256 = "3fb9d1915cf97c706bcf5610256057bc4bceb9556de44154832c7c1c57c48140"
EXPECTED_NORMS_SHA256 = "a65e8102269ff2abdb482e70e65f08d71f4bdcc6893c84a600e0618b80fbe16e"


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    errors = []
    norms_hash = hashlib.sha256(
        json.dumps(
            evidence["gradient_error_norms"], separators=(",", ":")
        ).encode()
    ).hexdigest()
    if evidence["archive_md5"] != EXPECTED_MD5:
        errors.append("archive MD5 mismatch")
    if evidence["raw_output_sha256"] != EXPECTED_RAW_SHA256:
        errors.append("raw output SHA-256 mismatch")
    if evidence["gradient_error_norms_sha256"] != EXPECTED_NORMS_SHA256:
        errors.append("gradient norms SHA-256 mismatch")
    if norms_hash != EXPECTED_NORMS_SHA256:
        errors.append("raw gradient norms do not match their locked hash")
    if evidence["status"] != "PASS":
        errors.append("source run did not pass")
    if evidence["raw_values_equal_route1"] is not True:
        errors.append("mirror values were not bit-for-bit equal to route 1")
    print(
        json.dumps(
            {
                "event": "CLAIM4_MIRROR_CHECK",
                "status": "PASS" if not errors else "FAIL",
                "archive_md5": evidence["archive_md5"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
