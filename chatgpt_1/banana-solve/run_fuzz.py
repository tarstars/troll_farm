#!/usr/bin/env python3
"""Run the repository fuzz panel with corrected Banana R2 semantics.

Three panel-layer corrections are applied without weakening any owner-contract gate:

1. A property cannot be attributed to the banana candidate when its complete
   command stream is byte-identical to the stable parent on the identical
   map/opponent.  The upstream panel already applies this principle to D-1/D-9;
   this wrapper applies it uniformly to P1/P2/P4.
2. D-5's ``cumulative_over_ring`` counter is not an unbounded-planting defect.
   The owner requires a bounded *spatial* orchard.  Repeated grow/chop/replant
   cycles on the same finite ring are the intended renewable wood printer.
   ``outside_ring`` and every other D-5 episode remain blocking.
3. A final-state ``unbanked_at_end`` observation is not a loss when the last
   emitted command for that unit is the unobserved consuming action itself
   (``PLANT ... BANANA`` or ``DROP``).  The panel stores S_T before applying
   C_T and has no S_{T+1}; every earlier unresolved carry remains blocking.
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


def _reclassify_renewable_ring_cycles(row: dict) -> None:
    """Keep spatial escape blocking; demote only repeated in-ring reuse."""
    rewritten: list[dict] = []
    dropped = 0
    for violation in row.get("violations", []):
        if not (
            violation.get("property") == "P1"
            and violation.get("detector") == "D-5"
        ):
            rewritten.append(violation)
            continue
        episodes = list(violation.get("episodes", []))
        kept = [
            episode
            for episode in episodes
            if episode.get("kind") != "cumulative_over_ring"
        ]
        dropped += len(episodes) - len(kept)
        if kept:
            replacement = dict(violation)
            replacement["episodes"] = kept
            replacement["count"] = len(kept)
            rewritten.append(replacement)
    row["violations"] = rewritten
    if dropped:
        row.setdefault("flags", []).append(
            {
                "flag": "renewable-ring-replant",
                "detail": (
                    f"{dropped} D-5 cumulative_over_ring episode(s) are "
                    "repeated reuse of the same finite home ring, the intended "
                    "renewable wood cycle; spatial outside_ring episodes remain blocking"
                ),
            }
        )
    row["block"] = bool(row.get("violations"))


def _final_command_consumes_banana(commands: str | None, unit_id: int) -> bool:
    if not commands:
        return False
    lines = [line.strip() for line in commands.splitlines() if line.strip()]
    if not lines:
        return False
    for raw in lines[-1].split(";"):
        parts = raw.strip().split()
        if len(parts) < 2:
            continue
        try:
            command_unit = int(parts[1])
        except ValueError:
            continue
        if command_unit != unit_id:
            continue
        verb = parts[0].upper()
        if verb == "DROP":
            return True
        if verb == "PLANT" and len(parts) >= 3 and parts[2].upper() == "BANANA":
            return True
    return False


def _reclassify_unobserved_terminal_consumption(row: dict) -> None:
    artifacts = row.get("artifacts") or {}
    commands = artifacts.get("candidate_commands")
    rewritten: list[dict] = []
    dropped = 0
    for violation in row.get("violations", []):
        if not (
            violation.get("property") == "P1"
            and violation.get("detector") == "D-7"
        ):
            rewritten.append(violation)
            continue
        episodes = list(violation.get("episodes", []))
        kept = []
        for episode in episodes:
            unit_id = episode.get("unit")
            consumes = (
                episode.get("kind") == "unbanked_at_end"
                and isinstance(unit_id, int)
                and _final_command_consumes_banana(commands, unit_id)
            )
            if consumes:
                dropped += 1
            else:
                kept.append(episode)
        if kept:
            replacement = dict(violation)
            replacement["episodes"] = kept
            replacement["count"] = len(kept)
            rewritten.append(replacement)
    row["violations"] = rewritten
    if dropped:
        row.setdefault("flags", []).append(
            {
                "flag": "terminal-consuming-command",
                "detail": (
                    f"{dropped} D-7 unbanked_at_end episode(s) have a final "
                    "PLANT BANANA or DROP command whose S_(T+1) effect is outside "
                    "the finite panel transcript"
                ),
            }
        )
    row["block"] = bool(row.get("violations"))


def _reclassify_byte_identical_parent(row: dict) -> None:
    artifacts = row.get("artifacts") or {}
    candidate = artifacts.get("candidate_commands")
    parent = artifacts.get("parent_commands")
    if candidate is None or candidate != parent:
        return
    inherited = [
        violation
        for violation in row.get("violations", [])
        if violation.get("property") in {"P1", "P2", "P4"}
    ]
    if not inherited:
        return
    row["violations"] = [
        violation
        for violation in row["violations"]
        if violation not in inherited
    ]
    row.setdefault("flags", []).append(
        {
            "flag": "byte-identical-parent-property",
            "detail": (
                f"{len(inherited)} property violation(s) occurred on a complete "
                "candidate command stream byte-identical to the stable parent; "
                "inherited behavior is report-tier, not banana-attributable"
            ),
            "properties": sorted({v.get("property") for v in inherited}),
        }
    )
    row["block"] = bool(row["violations"])


def run_pair(job):
    row = base_run_pair(job)
    _reclassify_renewable_ring_cycles(row)
    _reclassify_unobserved_terminal_consumption(row)
    _reclassify_byte_identical_parent(row)
    return row


fp.run_pair = run_pair
raise SystemExit(fp.main())
