"""Fail-closed verifier for committed trained-checkpoint evidence."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = Path(__file__).with_name("independent_check.py")
RAW = Path(__file__).with_name("raw_output.json")
METADATA = Path(__file__).with_name("run_metadata.json")
EXPECTED_COMMITTED_SHA256 = "bea73c45f230367262ade1b9a425ff431c93294634e57374a8ac9adb852a7ce8"


def main() -> int:
    observed_hash = hashlib.sha256(RAW.read_bytes()).hexdigest()
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    errors = []
    if observed_hash != EXPECTED_COMMITTED_SHA256:
        errors.append("committed raw JSON hash mismatch")
    if metadata["committed_semantic_json_sha256"] != observed_hash:
        errors.append("run metadata does not bind the committed raw JSON")
    if metadata["source_run_status"] != "done":
        errors.append("source experiment was not successful")
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
    if checker.returncode:
        errors.append("independent checker failed")
    print(
        json.dumps(
            {
                "event": "CLAIM4_TRAINED_VERIFY",
                "status": "PASS" if not errors else "FAIL",
                "raw_sha256": observed_hash,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
