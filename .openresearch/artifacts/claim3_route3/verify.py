"""Hash-pin and independently check formal Claim 3 route 3 evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")
RAW = Path(__file__).with_name("raw_output.json")
EXPECTED_SHA256 = "38d219af2586f5a2c3949104e9dad2bb111ed5b1b7b8a173e176d435fe13e29d"


def main() -> int:
    observed_sha256 = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if observed_sha256 != EXPECTED_SHA256:
        print(
            json.dumps(
                {
                    "event": "CLAIM3_ROUTE3_HASH_CHECK",
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
                "event": "CLAIM3_ROUTE3_VERIFY",
                "status": "PASS" if checker.returncode == 0 else "FAIL",
                "claim_verdict": "FALSIFIED",
                "confidence": "HIGH",
                "formal_raw_sha256": observed_sha256,
            },
            sort_keys=True,
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
