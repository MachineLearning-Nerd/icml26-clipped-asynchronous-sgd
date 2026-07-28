"""Fixed entrypoint for every OpenResearch experiment node.

Each branch changes committed configuration or verification code. The command
(`uv run --frozen python -m reproduction.run`) never changes.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "reproduction" / "config.json"
PROVENANCE_PATH = ROOT / ".openresearch" / "artifacts" / "provenance" / "retrieval.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_text_if_present(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError):
        return None


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def cpu_metadata() -> dict[str, object]:
    affinity: list[int] | None = None
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
    return {
        "os_cpu_count": os.cpu_count(),
        "affinity_cpu_count": len(affinity) if affinity is not None else None,
        "affinity_cpu_ids": affinity,
        "cgroup_cpu_max": read_text_if_present(Path("/sys/fs/cgroup/cpu.max")),
        "cgroup_cpuset_effective": read_text_if_present(
            Path("/sys/fs/cgroup/cpuset.cpus.effective")
        ),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("marimo", "matplotlib", "numpy", "scipy", "torch", "torchvision"):
        versions[name] = importlib.metadata.version(name)
    return versions


def validate_provenance() -> list[str]:
    errors: list[str] = []
    retrieval = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    expected = {
        "paper_html_sha256": "292ba2ce9a95e41279fe1535ffa23b720f18fb2139c3e26324138c0d4a0304ff",
        "verdict_dataset_sha": "1011185ba75e55480455dd44042ae65432f65cde",
        "judged_space_revision": "471748694e91b08b071d3d13c30d84b3091b5971",
        "validated_baseline_sha": "c83f1106db497ba1618fa656bd564e48b41f4eac",
    }
    for key, value in expected.items():
        if retrieval.get(key) != value:
            errors.append(f"{key}: expected {value}, observed {retrieval.get(key)}")

    manifest = (
        ROOT
        / ".openresearch"
        / "artifacts"
        / "provenance"
        / "judged_space_manifest.sha256"
    )
    if len(manifest.read_text(encoding="utf-8").splitlines()) != 13:
        errors.append("judged Space manifest must contain exactly 13 protected files")
    return errors


def run_registered_verifiers(config: dict[str, object]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for claim in config.get("accepted_claims", []):
        verifier = ROOT / ".openresearch" / "artifacts" / str(claim) / "verify.py"
        completed = subprocess.run(
            [sys.executable, str(verifier)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        result = {
            "claim": claim,
            "verifier": str(verifier.relative_to(ROOT)),
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        results.append(result)
        print(json.dumps({"verifier_result": result}, sort_keys=True))
    return results


def main() -> int:
    started = time.perf_counter()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    errors = validate_provenance()
    verifier_results = run_registered_verifiers(config)
    errors.extend(
        f"{result['claim']} verifier exited {result['exit_code']}"
        for result in verifier_results
        if result["exit_code"] != 0
    )
    summary = {
        "event": "OPENRESEARCH_EVAL_SUMMARY",
        "status": "PASS" if not errors else "FAIL",
        "mode": config["mode"],
        "seed": config["seed"],
        "compute_plan": config["compute_plan"],
        "actual_cpu": cpu_metadata(),
        "gpu_visible": False,
        "python": sys.version,
        "packages": package_versions(),
        "git_sha": git_sha(),
        "uv_lock_sha256": sha256(ROOT / "uv.lock"),
        "provenance_sha256": sha256(PROVENANCE_PATH),
        "verifier_count": len(verifier_results),
        "errors": errors,
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

