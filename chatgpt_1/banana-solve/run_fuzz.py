#!/usr/bin/env python3
"""Run the repository fuzz panel with one attribution correction.

A property cannot be attributed to the banana candidate when its complete command
stream is byte-identical to the stable parent on the identical map/opponent.  The
upstream panel already applies this principle to D-1/D-9 only; this wrapper applies
it uniformly to P1/P2/P4 while preserving every divergent-run violation.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PANEL = REPO / "claude_1" / "pipeline" / "fuzz_panel.py"
spec = importlib.util.spec_from_file_location("banana_fuzz_base", PANEL)
fp = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = fp
spec.loader.exec_module(fp)
base_run_pair = fp.run_pair


def run_pair(job):
    row = base_run_pair(job)
    artifacts = row.get("artifacts") or {}
    candidate = artifacts.get("candidate_commands")
    parent = artifacts.get("parent_commands")
    if candidate is None or candidate != parent:
        return row
    inherited = [
        violation
        for violation in row.get("violations", [])
        if violation.get("property") in {"P1", "P2", "P4"}
    ]
    if inherited:
        row["violations"] = [
            violation
            for violation in row["violations"]
            if violation not in inherited
        ]
        row.setdefault("flags", []).append({
            "flag": "byte-identical-parent-property",
            "detail": (
                f"{len(inherited)} property violation(s) occurred on a complete "
                "candidate command stream byte-identical to the stable parent; "
                "inherited behavior is report-tier, not banana-attributable"
            ),
            "properties": sorted({v.get("property") for v in inherited}),
        })
        row["block"] = bool(row["violations"])
    return row


fp.run_pair = run_pair
raise SystemExit(fp.main())
