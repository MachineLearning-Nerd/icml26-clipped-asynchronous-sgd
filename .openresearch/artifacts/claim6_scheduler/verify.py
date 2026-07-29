"""Generate and independently check the Figure 4 scheduler calibration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")


def main() -> int:
    experiment = subprocess.run(
        [sys.executable, "-m", "reproduction.claims.claim6_scheduler"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    print(experiment.stdout, end="")
    if experiment.stderr:
        print(experiment.stderr, file=sys.stderr, end="")
    if experiment.returncode:
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
                "event": "CLAIM6_SCHEDULER_VERIFY",
                "status": "PASS" if checker.returncode == 0 else "FAIL",
            },
            sort_keys=True,
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
