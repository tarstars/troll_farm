#!/usr/bin/env python3
"""Attribute exact compact E7a bytes to named live logical blocks.

This is deliberately marker-based and fail-closed over the immutable submission artifact.
It does not rewrite source and does not count formatting or identifier shortening.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.slim_live_source import _item_span  # noqa: E402


BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
BASELINE_BYTES = 62_820
TARGET_BYTES = 31_410

GROUPS = {
    "secure_orchard": (
        "enum OrchardPhase",
        "struct OrchardGeometry",
        "struct OrchardCycle",
        "pub struct SecureOrchardBot",
        "impl SecureOrchardBot",
        "impl Bot for SecureOrchardBot",
    ),
    "endgame_and_idle_harvest": (
        "fn carried_fruit(",
        "fn inventory_fruits(",
        "fn conversion_chop_turns(",
        "fn endgame_candidates(",
        "fn idle_harvest_candidates(",
        "fn endgame(view:",
    ),
    "opening_specification_planner": (
        "pub struct YamoOpeningPolicy",
        "struct OpeningObjective",
        "fn ensure_opening(",
        "fn collection_eta(",
        "fn opening_objective(",
        "fn opening_key(",
        "fn opening_options(",
        "fn choose_second_troll(",
        "fn training_affordable(",
        "fn strongest_affordable(",
        "fn enforce_training_deadline(",
        "fn fallback_second_troll(",
    ),
    "joint_assignment_and_movement": (
        "fn compatible(",
        "fn picked_item(",
        "fn stock_compatible(",
        "fn select(",
        "fn move_command(",
        "fn resolve_move_conflicts(",
        "fn resolve_move_conflicts_with_priority(",
        "fn resolve_move_conflicts_with_priority_and_forbidden(",
    ),
    "door_and_regeneration_coordination": (
        "fn unique_shack_door(",
        "fn forced_move(",
        "fn carries_committed_fruit(",
        "fn planned_egress(",
        "fn force_unique_door_clear(",
        "fn reconcile_regeneration_commitments(",
        "fn remember_selected_regeneration(",
    ),
    "tree_forecast_and_chop_valuation": (
        "fn predicted_opp_chop(",
        "fn predict_tree(",
        "fn chop_outcome(",
        "fn chop_candidates(",
        "fn yamo_chop_candidates(",
    ),
    "fruit_iron_and_main_candidate_generation": (
        "fn early_candidates(",
        "fn fruit_candidates(",
        "fn iron_candidates(",
        "fn main_candidates(",
    ),
}


def sha256(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def attribute(source: str) -> dict:
    observed_sha = sha256(source)
    if observed_sha != BASELINE_SHA256 or len(source.encode()) != BASELINE_BYTES:
        raise ValueError(
            f"baseline mismatch: bytes={len(source.encode())} sha256={observed_sha}"
        )
    groups = []
    occupied = []
    for name, markers in GROUPS.items():
        items = []
        for marker in markers:
            start, end = _item_span(source, marker)
            items.append({"marker": marker, "start": start, "end": end, "bytes": end - start})
            occupied.append((start, end, name, marker))
        groups.append(
            {
                "name": name,
                "bytes": sum(item["bytes"] for item in items),
                "baseline_fraction": sum(item["bytes"] for item in items) / BASELINE_BYTES,
                "items": items,
            }
        )
    for index, left in enumerate(sorted(occupied)):
        for right in sorted(occupied)[index + 1 :]:
            if right[0] >= left[1]:
                break
            raise ValueError(f"overlapping attribution spans: {left} and {right}")
    attributed = sum(row["bytes"] for row in groups)
    orchard = next(row["bytes"] for row in groups if row["name"] == "secure_orchard")
    return {
        "schema": "troll-farm-e7a-byte-attribution-v1",
        "baseline": {
            "bytes": BASELINE_BYTES,
            "sha256": BASELINE_SHA256,
            "target_bytes": TARGET_BYTES,
            "required_removal_bytes": BASELINE_BYTES - TARGET_BYTES,
        },
        "method": (
            "exact compact-source item spans found by unique semantic markers and balanced "
            "Rust braces; no rustfmt/minification or identifier transformation credited"
        ),
        "groups": groups,
        "totals": {
            "attributed_nonoverlapping_bytes": attributed,
            "unattributed_parser_state_and_orchestration_bytes": BASELINE_BYTES - attributed,
            "secure_orchard_removal_ceiling_bytes": orchard,
            "additional_net_removal_after_orchard_required": (
                BASELINE_BYTES - orchard - TARGET_BYTES
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = attribute(args.source.read_text())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
