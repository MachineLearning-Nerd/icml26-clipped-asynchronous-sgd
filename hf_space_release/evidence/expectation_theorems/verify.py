"""Hash-pin and independently check the formal Claims 1–2 evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")
RAW = Path(__file__).with_name("raw_output.json")
EXPECTED_SHA256 = "32562b2bf3d348dc31de2d685712b7e86b371aa6abaa33c62006fc8e56f38906"


def main() -> int:
    observed_sha256 = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if observed_sha256 != EXPECTED_SHA256:
        print(
            json.dumps(
                {
                    "event": "EXPECTATION_THEOREMS_HASH_CHECK",
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
                "event": "EXPECTATION_THEOREMS_VERIFY",
                "status": "PASS" if checker.returncode == 0 else "FAIL",
                "formal_raw_sha256": observed_sha256,
            },
            sort_keys=True,
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
