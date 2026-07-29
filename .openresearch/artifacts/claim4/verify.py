"""Fail-closed verifier for the committed Claim 4 pilot evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")


def main() -> int:
    import subprocess

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
    print(
        json.dumps(
            {
                "event": "CLAIM4_VERIFY",
                "status": status,
                "stage": "committed-evidence-check",
                "source_run": "512fbeef-0db3-44ec-81e8-7fcba10ba53e",
                "source_run_status": "failed: backend timeout after complete payload",
            }
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
