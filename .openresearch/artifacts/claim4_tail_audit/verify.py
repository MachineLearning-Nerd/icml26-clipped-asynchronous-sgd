"""Fail-closed verifier for the committed exhaustive tail-count audit."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).with_name("raw_output.json")
CHECKER = Path(__file__).with_name("independent_check.py")
EXPECTED_SHA256 = "1ba104d8e529032f6e4126cabdb27fff7c92a374ac4d81e647700e53e25e7733"


def main() -> int:
    observed = hashlib.sha256(RAW.read_bytes()).hexdigest()
    errors = []
    if observed != EXPECTED_SHA256:
        errors.append("committed exhaustive audit hash mismatch")
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
        errors.append("independent exhaustive-domain checker failed")
    print(
        json.dumps(
            {
                "event": "CLAIM4_TAIL_AUDIT_VERIFY",
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
