"""Hash-pin and independently check the accepted complete D=4 sweep."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")
RAW = Path(__file__).with_name("raw_output.json")
EXPECTED_RAW_SHA256 = (
    "f9d36093629b4966bec95323d3df6750ba78af2d5ffd16a0c7330d9a6a16082d"
)


def main() -> int:
    observed_hash = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if observed_hash != EXPECTED_RAW_SHA256:
        print(
            json.dumps(
                {
                    "event": "CLAIM6_D4_SWEEP_VERIFY",
                    "status": "FAIL",
                    "error": "raw hash mismatch",
                    "expected": EXPECTED_RAW_SHA256,
                    "observed": observed_hash,
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
                "event": "CLAIM6_D4_SWEEP_VERIFY",
                "status": "PASS" if checker.returncode == 0 else "FAIL",
                "raw_sha256": observed_hash,
            },
            sort_keys=True,
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
