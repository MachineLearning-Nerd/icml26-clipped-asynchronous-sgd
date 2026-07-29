"""Generate and independently check Claim 6 validation evidence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")


def main() -> int:
    environment = os.environ.copy()
    environment["OMP_NUM_THREADS"] = "1"
    environment["MKL_NUM_THREADS"] = "1"
    experiment = subprocess.run(
        [sys.executable, "-m", "reproduction.claims.claim6_validation"],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    print(experiment.stdout, end="")
    if experiment.stderr:
        print(experiment.stderr, file=sys.stderr, end="")
    if experiment.returncode:
        print(
            json.dumps(
                {
                    "event": "CLAIM6_VALIDATION_VERIFY",
                    "stage": "scientific_run",
                    "status": "FAIL",
                },
                sort_keys=True,
            )
        )
        return experiment.returncode
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
                "event": "CLAIM6_VALIDATION_VERIFY",
                "status": "PASS" if checker.returncode == 0 else "FAIL",
            },
            sort_keys=True,
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
