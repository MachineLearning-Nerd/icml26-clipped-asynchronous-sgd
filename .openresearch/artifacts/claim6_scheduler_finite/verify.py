"""Fail-closed verifier for the finite-horizon scheduler evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).with_name("raw_output.json")
CHECKER = Path(__file__).with_name("independent_check.py")
EXPECTED_SHA256 = "a3b83084eb43343d80c9b6cf1bb63eedcaaeecd6888652c7bf4d4789b4cb866a"


def main() -> int:
    observed = hashlib.sha256(RAW.read_bytes()).hexdigest()
    errors = []
    if observed != EXPECTED_SHA256:
        errors.append("committed finite-horizon raw-data hash mismatch")
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
        errors.append("independent finite-horizon checker failed")
    print(
        json.dumps(
            {
                "event": "CLAIM6_SCHEDULER_FINITE_VERIFY",
                "status": "PASS" if not errors else "FAIL",
                "raw_sha256": observed,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
