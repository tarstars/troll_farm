#!/usr/bin/env python3
"""Repair pilot CONSTRAINTS locators from unique current-content anchors.

The migration derives ranges from current canonical content, plans every record byte before
writing, and regenerates projections only in apply mode. `--check` is strictly read-only.
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
    "H7": (
        "- **Measure before you build, and re-verify the premise first.**",
        "[H5, H6-preflight, H7, H8, H13]",
    ),
    "H1": (
        "- ★★ **The joint economy package cannot pay on this scheduler.**",
        "[H1, 2026-07-29]",
    ),
}
D176A_CLOSURE = (
    "- **Oscillation is CLOSED permanently after two designed attempts.**",
    "[D176a; D171a]",
)
D176A_GATE = (
    "- ★ **Gate-design rules, learned by getting both wrong in D176a.**",
    "passed at zero. [D176a]",
)


def unique_span(
    lines: list[str], start_anchor: str, end_anchor: str, label: str
) -> tuple[int, int]:
    starts = [index for index, line in enumerate(lines) if start_anchor in line]
    if len(starts) != 1:
        raise ValueError(f"{label}: expected one start anchor, found {len(starts)}")
    start = starts[0]
    ends = [index for index in range(start, len(lines)) if end_anchor in lines[index]]
    if len(ends) != 1:
        raise ValueError(f"{label}: expected one end anchor after start, found {len(ends)}")
    return start + 1, ends[0] + 1


def format_span(span: tuple[int, int]) -> str:
    return f"lines {span[0]}-{span[1]}"


def rewrite_sources(value: Any, locator: str) -> None:
    if isinstance(value, dict):
        if value.get("path") == "docs/CONSTRAINTS.md" and value.get("locator"):
            value["locator"] = locator
        for child in value.values():
            rewrite_sources(child, locator)
    elif isinstance(value, list):
        for child in value:
            rewrite_sources(child, locator)


def replace_human_locator(line: str, locator: str) -> str:
    return re.sub(
        r"(`docs/CONSTRAINTS\.md`|docs/CONSTRAINTS\.md) \(lines \d+-\d+\)",
        lambda match: f"{match.group(1)} ({locator})",
        line,
    )


def rewrite_d176a_human(prefix: str, closure: str, gate: str) -> str:
    current: str | None = None
    output: list[str] = []
    for line in prefix.splitlines(keepends=True):
        if line.startswith("- **long_oscillation_rate**"):
            current = closure
        elif line.startswith("- **de_novo**"):
            current = closure
        elif line.startswith("- **overall_value**"):
            current = None
        elif line.startswith("- **worst_case_gate_population**"):
            current = gate
        if current and "docs/CONSTRAINTS.md" in line:
            line = replace_human_locator(line, current)
        output.append(line)
    return "".join(output)


def desired_record_text(path: Path, rid: str, locators: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise ValueError(f"{path}: canonical machine block missing")
    prefix, rest = text.split(START, 1)
    payload, suffix = rest.split(END, 1)
    record = json.loads(payload.strip())

    if rid != "D176a":
        locator = locators[rid]
        rewrite_sources(record, locator)
        prefix = "".join(
            replace_human_locator(line, locator)
            for line in prefix.splitlines(keepends=True)
        )
    else:
        closure = locators["D176a.closure"]
        gate = locators["D176a.gate"]
        projection = locators["D176a.projection"]
        for claim in record["decisive_claims"]:
            source = claim.get("source", {})
            if source.get("path") != "docs/CONSTRAINTS.md":
                continue
            if claim.get("name") in {"long_oscillation_rate", "de_novo"}:
                source["locator"] = closure
            elif claim.get("name") == "worst_case_gate_population":
                source["locator"] = gate
        for evidence in record.get("textual_evidence", []):
            source = evidence.get("source", {})
            if source.get("path") == "docs/CONSTRAINTS.md":
                source["locator"] = gate
        record["constraint_projection"]["source"]["locator"] = projection
        prefix = rewrite_d176a_human(prefix, closure, gate)

    return (
        prefix
        + START
        + "\n"
        + json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
        + END
        + suffix
    )


def derive_locators(lines: list[str]) -> dict[str, str]:
    locators: dict[str, str] = {}
    for rid, (start_anchor, end_anchor) in sorted(ANCHORS.items()):
        locators[rid] = format_span(
            unique_span(lines, start_anchor, end_anchor, rid)
        )
    closure_span = unique_span(lines, *D176A_CLOSURE, "D176a.closure")
    gate_span = unique_span(lines, *D176A_GATE, "D176a.gate")
    locators["D176a.closure"] = format_span(closure_span)
    locators["D176a.gate"] = format_span(gate_span)
    locators["D176a.projection"] = format_span(
        (closure_span[0], gate_span[1])
    )
    return locators


def run(repo: Path, check: bool) -> dict[str, str]:
    lines = (repo / "docs/CONSTRAINTS.md").read_text(
        encoding="utf-8"
    ).splitlines()
    locators = derive_locators(lines)
    record_ids = sorted(ANCHORS) + ["D176a"]
    plans: list[tuple[Path, str]] = []
    changed: list[str] = []
    for rid in record_ids:
        path = repo / "docs/evidence/records" / f"{rid}.md"
        desired = desired_record_text(path, rid, locators)
        plans.append((path, desired))
        if desired != path.read_text(encoding="utf-8"):
            changed.append(rid)

    if check:
        if changed:
            raise SystemExit("locator migration required: " + ", ".join(changed))
        return locators

    for path, desired in plans:
        path.write_text(desired, encoding="utf-8")
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
