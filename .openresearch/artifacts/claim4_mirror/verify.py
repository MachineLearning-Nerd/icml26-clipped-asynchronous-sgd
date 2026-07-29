"""Regenerate Claim 4 pilot through an MD5-checked HF dataset mirror."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / ".openresearch" / "artifacts" / "claim4" / "independent_check.py"
RAW = ROOT / ".openresearch" / "artifacts" / "claim4" / "raw_output.json"
EXPECTED_MD5 = "c58f30108f718f92721af3b95e74349a"


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
        return experiment.returncode
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    observed_md5 = raw["dataset"]["downloaded_archive_md5_observed"]
    if observed_md5 != EXPECTED_MD5:
        print(
            json.dumps(
                {
                    "event": "CLAIM4_MIRROR_CHECK",
                    "status": "FAIL",
                    "expected_md5": EXPECTED_MD5,
                    "observed_md5": observed_md5,
                }
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
                "event": "CLAIM4_MIRROR_CHECK",
                "status": "PASS" if checker.returncode == 0 else "FAIL",
                "archive_md5": observed_md5,
            }
        )
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
