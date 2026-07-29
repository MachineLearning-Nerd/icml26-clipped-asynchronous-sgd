"""Hash-pin and independently check formal Claim 3 route 1 evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")
RAW = Path(__file__).with_name("raw_output.json")
EXPECTED_SHA256 = "af9521892cae06cc54f66df15d2243afcd88da2b61e9ef4311524c7b8e5c6390"


def main() -> int:
    observed_sha256 = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if observed_sha256 != EXPECTED_SHA256:
        print(
            json.dumps(
                {
                    "event": "CLAIM3_ROUTE1_HASH_CHECK",
                    "status": "FAIL",
                    "expected_sha256": EXPECTED_SHA256,
                    "observed_sha256": observed_sha256,
                },
                sort_keys=True,
            )
        )
        return 1
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
    print(
        json.dumps(
            {
                "event": "CLAIM3_ROUTE1_VERIFY",
                "status": "PASS" if checker.returncode == 0 else "FAIL",
                "claim_verdict": "BLOCKED",
                "formal_raw_sha256": observed_sha256,
            },
            sort_keys=True,
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
