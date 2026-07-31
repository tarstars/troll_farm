#!/usr/bin/env python3
"""Repair pilot CONSTRAINTS locators from unique current-content anchors.

This is a one-purpose migration for the explicit pilot set. It derives line ranges from the
current canonical `docs/CONSTRAINTS.md`, rewrites every line source in the corresponding
canonical record, and regenerates deterministic projections. It never edits CONSTRAINTS.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.build_decision_evidence_index import END, START, build

ANCHORS = {
    "D101": (
        "- ★ The resident's real architectural gap is production persistence",
        "[D101]",
    ),
    "D161": (
        "- D40/q6 is dead as a resident-competition substrate",
        "[D161; D158]",
    ),
    "D30": (
        "- Generated-map results are not field evidence",
        "[D29c/D30/D31/D33]",
    ),
    "D175a": (
        "- ★★★ PRODUCTION IS STRUCTURALLY NEGATIVE FOR THIS ARCHITECTURE",
        "[D175a]",
    ),
    "D172a": (
        "- ★ FINAL for the learned-selector question",
        "[D172a]",
    ),
    "D169": (
        "- ★★ The unified resident-native option envelope clears the Tier-2 gate",
        "[D169]",
    ),
    "D176a": (
        "- **Oscillation is CLOSED permanently after two designed attempts.**",
        "[D176a; D171a]",
    ),
    "H7": (
        "- **Measure before you build, and re-verify the premise first.**",
        "[H5, H6-preflight, H7, H8, H13]",
    ),
    "H1": (
        "- ★★ **The joint economy package cannot pay on this scheduler.**",
        "[H1, 2026-07-29]",
    ),
}


def unique_span(lines: list[str], rid: str) -> tuple[int, int]:
    start_anchor, end_anchor = ANCHORS[rid]
    starts = [index for index, line in enumerate(lines) if start_anchor in line]
    if len(starts) != 1:
        raise ValueError(f"{rid}: expected one start anchor, found {len(starts)}")
    start = starts[0]
    ends = [index for index in range(start, len(lines)) if end_anchor in lines[index]]
    if len(ends) != 1:
        raise ValueError(f"{rid}: expected one end anchor after start, found {len(ends)}")
    return start + 1, ends[0] + 1


def rewrite_sources(value: Any, locator: str) -> int:
    changed = 0
    if isinstance(value, dict):
        if value.get("path") == "docs/CONSTRAINTS.md" and value.get("locator"):
            if value["locator"] != locator:
                value["locator"] = locator
                changed += 1
        for child in value.values():
            changed += rewrite_sources(child, locator)
    elif isinstance(value, list):
        for child in value:
            changed += rewrite_sources(child, locator)
    return changed


def rewrite_record(path: Path, locator: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise ValueError(f"{path}: canonical machine block missing")
    prefix, rest = text.split(START, 1)
    payload, suffix = rest.split(END, 1)
    record = json.loads(payload.strip())
    changed = rewrite_sources(record, locator)
    if changed == 0 and f"({locator})" in prefix:
        return False
    prefix = re.sub(
        r"(`docs/CONSTRAINTS\.md`|docs/CONSTRAINTS\.md) \(lines \d+-\d+\)",
        lambda match: f"{match.group(1)} ({locator})",
        prefix,
    )
    rewritten = (
        prefix
        + START
        + "\n"
        + json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
        + END
        + suffix
    )
    if rewritten == text:
        return False
    path.write_text(rewritten, encoding="utf-8")
    return True


def run(repo: Path, check: bool) -> dict[str, str]:
    constraints = repo / "docs/CONSTRAINTS.md"
    lines = constraints.read_text(encoding="utf-8").splitlines()
    locators: dict[str, str] = {}
    changed: list[str] = []
    for rid in sorted(ANCHORS):
        start, end = unique_span(lines, rid)
        locator = f"lines {start}-{end}"
        locators[rid] = locator
        record_path = repo / "docs/evidence/records" / f"{rid}.md"
        before = record_path.read_bytes()
        rewrite_record(record_path, locator)
        if record_path.read_bytes() != before:
            changed.append(rid)
    if check and changed:
        raise SystemExit("locator migration required: " + ", ".join(changed))
    if not check:
        build(repo)
    return locators


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    locators = run(args.repo_root, args.check)
    print(json.dumps({"locators": locators, "status": "ok"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
