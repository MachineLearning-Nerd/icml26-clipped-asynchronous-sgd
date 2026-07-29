"""Generate and independently check Claims 1–2 proof evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")


def main() -> int:
    scientific = subprocess.run(
        [sys.executable, "-m", "reproduction.claims.expectation_theorem"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    print(scientific.stdout, end="")
    if scientific.stderr:
        print(scientific.stderr, file=sys.stderr, end="")
    if scientific.returncode:
        return scientific.returncode
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
            },
            sort_keys=True,
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
