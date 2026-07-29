"""Evaluator-blind traversal of a reconstructed Hugging Face Space candidate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CLAIM_REQUIREMENTS = (
    "exact claim",
    "source",
    "raw",
    "verifier",
    "checker",
    "control",
    "limitation",
    "git",
    "seed",
    "gpu",
)


def walk_logbook(node: dict[str, object]) -> list[str]:
    files = [str(node["file"])]
    for child in node.get("children", []):
        files.extend(walk_logbook(child))
    return files


def resolve_link(root: Path, link: str) -> Path | None:
    if link.startswith(("#", "http://", "https://", "mailto:")):
        return None
    clean = link.split("#", 1)[0].split("?", 1)[0]
    return root / clean


def review(root: Path) -> dict[str, object]:
    errors: list[str] = []
    opened: list[str] = []
    entrypoints = ("README.md", "logbook.json", "pages/index.md")
    for relative in entrypoints:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing canonical entrypoint: {relative}")
        else:
            opened.append(relative)

    logbook_path = root / "logbook.json"
    page_files: list[str] = []
    if logbook_path.is_file():
        try:
            logbook = json.loads(logbook_path.read_text(encoding="utf-8"))
            if logbook.get("space_id") != "DineshAI/AmgjQp4vrr":
                errors.append("logbook space_id is not the protected Space")
            page_files = walk_logbook(logbook["root"])
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            errors.append(f"invalid logbook: {exc}")

    for relative in page_files:
        path = root / relative
        if not path.is_file():
            errors.append(f"logbook page missing: {relative}")
            continue
        opened.append(relative)
        text = path.read_text(encoding="utf-8")
        for link in LINK.findall(text):
            target = resolve_link(root, link)
            if target is None:
                continue
            target_relative = target.relative_to(root).as_posix()
            if not target.is_file():
                errors.append(f"broken link from {relative}: {link}")
            else:
                opened.append(target_relative)

    claim_conclusions: dict[str, object] = {}
    expected_verdicts = {
        "1": "VERIFIED",
        "2": "VERIFIED",
        "3": "FALSIFIED",
        "4": "BLOCKED",
        "5": "FALSIFIED",
        "6": "BLOCKED",
    }
    for claim, verdict in expected_verdicts.items():
        relative = f"pages/claim-{claim}/page.md"
        path = root / relative
        text = path.read_text(encoding="utf-8").lower() if path.is_file() else ""
        missing = [token for token in CLAIM_REQUIREMENTS if token not in text]
        if verdict.lower() not in text:
            missing.append(f"verdict:{verdict}")
        claim_conclusions[claim] = {
            "verdict_located": verdict if not missing else None,
            "missing_requirements": missing,
        }
        errors.extend(f"claim {claim} missing discoverable {item}" for item in missing)

    current = (root / "pages/current/page.md").read_text(encoding="utf-8")
    for token in (
        "Visibility matrix",
        "uv run --frozen python -m reproduction.run",
        "Previous live judged score: 4/12",
        "6–9/12",
        "Historical rejected baseline",
    ):
        if token not in current:
            errors.append(f"current page missing release token: {token}")

    for required in ("UPLOAD_ALLOWLIST.txt", "MANIFEST.sha256"):
        if not (root / required).is_file():
            errors.append(f"missing release file: {required}")

    return {
        "schema_version": 1,
        "review_mode": "evaluator-blind-canonical-entrypoint-traversal",
        "candidate_root_name": root.name,
        "entrypoints": list(entrypoints),
        "opened_files": sorted(set(opened)),
        "claim_conclusions": claim_conclusions,
        "errors": sorted(set(errors)),
        "status": "PASS" if not errors else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = review(args.candidate_root.resolve())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
