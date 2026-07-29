"""Fail-closed static verifier for Claim 4's final BLOCKED certificate."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).with_name("raw_output.json")
CHECKER = Path(__file__).with_name("independent_check.py")
EXPECTED_SHA256 = "aa2440e9bc8aaeae60f41660cda601a4d6b56392a46183d5755f28b79a015c4e"


def main() -> int:
    observed = hashlib.sha256(RAW.read_bytes()).hexdigest()
    errors = []
    if observed != EXPECTED_SHA256:
        errors.append("committed falsification-route hash mismatch")
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
        errors.append("independent falsification-logic checker failed")
    print(
        json.dumps(
            {
                "event": "CLAIM4_FALSIFICATION_VERIFY",
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
