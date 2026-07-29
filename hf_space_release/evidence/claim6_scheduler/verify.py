"""Fail-closed verifier for the historical failed scheduler calibration."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).with_name("raw_output.json")
CHECKER = Path(__file__).with_name("independent_check.py")
EXPECTED_SHA256 = "1a3f1b8ee5ce68da198c21fab1cffd7c64e629eb6f88c2649090b8a8a9fd51b1"


def main() -> int:
    observed = hashlib.sha256(RAW.read_bytes()).hexdigest()
    errors = []
    if observed != EXPECTED_SHA256:
        errors.append("preserved source-run hash mismatch")
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
    if checker.returncode:
        errors.append("independent failure-certificate checker failed")
    print(
        json.dumps(
            {
                "event": "CLAIM6_SCHEDULER_VERIFY",
                "status": "PASS" if not errors else "FAIL",
                "raw_sha256": observed,
                "source_scientific_status": "FAIL",
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
