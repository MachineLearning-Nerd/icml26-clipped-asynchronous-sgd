"""Fail-closed Claim 4 pilot verifier."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")


def main() -> int:
    experiment = subprocess.run(
        [sys.executable, "-m", "reproduction.claims.claim4"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    print(experiment.stdout, end="")
    if experiment.stderr:
        print(experiment.stderr, file=sys.stderr, end="")
    if experiment.returncode != 0:
        print(json.dumps({"event": "CLAIM4_VERIFY", "status": "FAIL", "stage": "experiment"}))
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
    status = "PASS" if checker.returncode == 0 else "FAIL"
    print(json.dumps({"event": "CLAIM4_VERIFY", "status": status, "stage": "complete"}))
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
