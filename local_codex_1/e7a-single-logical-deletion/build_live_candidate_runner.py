#!/usr/bin/env python3
"""Adapt the frozen open-panel runner to a candidate with the live E7a types."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def function_text(source: str, marker: str) -> str:
    start = source.find(marker)
    if start < 0 or source.find(marker, start + 1) >= 0:
        raise ValueError(f"expected one function marker: {marker}")
    opening = source.find("{", start)
    if opening < 0:
        raise ValueError(f"missing function body: {marker}")
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise ValueError(f"unterminated function: {marker}")


def build(source: str) -> tuple[str, dict]:
    baseline_view = function_text(source, "fn baseline_view(")
    old_candidate_view = function_text(source, "fn candidate_view(")
    new_candidate_view = baseline_view.replace(
        "fn baseline_view(", "fn candidate_view(", 1
    ).replace("baseline::", "candidate::")
    result = source.replace(old_candidate_view, new_candidate_view, 1)

    replacements = (
        (
            "Candidate(candidate::bot::moisan::YamoBot)",
            "Candidate(candidate::bot::moisan::SecureOrchardBot)",
        ),
        (
            "Self::Candidate(candidate::bot::moisan::YamoBot::new())",
            "Self::Candidate(candidate::bot::moisan::SecureOrchardBot::new())",
        ),
    )
    changes = [
        {
            "marker": "candidate live GameState adapter",
            "old_bytes": len(old_candidate_view.encode()),
            "new_bytes": len(new_candidate_view.encode()),
        }
    ]
    for old, new in replacements:
        if result.count(old) != 1:
            raise ValueError(f"expected one runner marker: {old}")
        result = result.replace(old, new, 1)
        changes.append({"old": old, "new": new})

    if "candidate::bot::moisan::YamoBot" in result:
        raise ValueError("half-size candidate policy type remains")
    manifest = {
        "schema": "troll-farm-e7a-single-logical-deletion-runner-adapter-v1",
        "input_sha256": sha256(source.encode()),
        "output_sha256": sha256(result.encode()),
        "changes": changes,
        "policy_change": False,
        "purpose": (
            "adapt only candidate type construction and view conversion from the "
            "half-size layout to the exact live E7a layout"
        ),
    }
    return result, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("runner", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    if args.runner.exists() or args.manifest.exists():
        parser.error("refusing to overwrite runner evidence")
    runner, manifest = build(args.source.read_text())
    args.runner.write_text(runner)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
