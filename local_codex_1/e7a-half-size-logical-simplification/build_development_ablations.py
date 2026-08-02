#!/usr/bin/env python3
"""Build readable oversized attribution arms from the exact E7a source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.slim_live_source import _remove_item, _replace_item  # noqa: E402
from build_integrated_half import BOT_IMPL, YAMO_IMPL, YAMO_STRUCT  # noqa: E402


BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
ORCHARD_ITEMS = (
    "enum OrchardPhase",
    "struct OrchardGeometry",
    "struct OrchardCycle",
    "pub struct SecureOrchardBot",
    "impl SecureOrchardBot",
    "impl Bot for SecureOrchardBot",
)
ORPHANED_DERIVES = (
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
    "#[derive(Clone,Debug)]"
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def orchard_only(source: str) -> tuple[str, dict]:
    if sha256_bytes(source.encode()) != BASELINE_SHA256:
        raise ValueError("input is not the exact E7a source")
    result = source
    removals = []
    for marker in ORCHARD_ITEMS:
        before = len(result.encode())
        result = _remove_item(result, marker)
        removals.append({"marker": marker, "bytes": before - len(result.encode())})
    if result.count(ORPHANED_DERIVES) != 1:
        raise ValueError("unexpected orchard derive sequence")
    result = result.replace(ORPHANED_DERIVES, "", 1)
    yamo_impl = "impl YamoBot{"
    if result.count(yamo_impl) != 1:
        raise ValueError("unexpected YamoBot implementation count")
    result = result.replace(
        yamo_impl,
        yamo_impl
        + "pub fn new()->Self{"
        + "Self::tuned_carry_regeneration_transit_idle_harvest()}",
        1,
    )
    replacements = (
        ("use crate::bot::moisan::SecureOrchardBot;", "use crate::bot::moisan::YamoBot;"),
        (
            "let mut bot=SecureOrchardBot::new();",
            "let mut bot=YamoBot::new();",
        ),
    )
    for old, new in replacements:
        if result.count(old) != 1:
            raise ValueError(f"expected one {old!r}")
        result = result.replace(old, new, 1)
    manifest = {
        "schema": "troll-farm-e7a-development-ablation/1",
        "arm": "ORCHARD_REMOVED_CORE_EXACT",
        "evidence_boundary": "oversized attribution arm; cannot qualify for Arena",
        "baseline_sha256": BASELINE_SHA256,
        "candidate_bytes": len(result.encode()),
        "candidate_sha256": sha256_bytes(result.encode()),
        "logical_change": "remove SecureOrchardBot and run the otherwise exact inner YamoBot",
        "removed_items": removals,
        "identifier_renaming": False,
        "minification": False,
    }
    return result, manifest


def focused_yamo_exact_moisan(source: str) -> tuple[str, dict]:
    """Remove the orchard and specialize Yamo while retaining exact Moisan economics."""

    if sha256_bytes(source.encode()) != BASELINE_SHA256:
        raise ValueError("input is not the exact E7a source")
    result = source
    removals = []
    for marker in ORCHARD_ITEMS:
        before = len(result.encode())
        result = _remove_item(result, marker)
        removals.append({"marker": marker, "bytes": before - len(result.encode())})
    for marker in (
        "pub struct YamoOpeningPolicy",
        "impl YamoOpeningPolicy",
        "struct OpeningObjective",
    ):
        before = len(result.encode())
        result = _remove_item(result, marker)
        removals.append({"marker": marker, "bytes": before - len(result.encode())})
    if result.count(ORPHANED_DERIVES) != 1:
        raise ValueError("unexpected orchard derive sequence")
    result = result.replace(ORPHANED_DERIVES, "", 1)
    duplicate_yamo_derive = (
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
    )
    if result.count(duplicate_yamo_derive) != 1:
        raise ValueError("unexpected opening-policy derive sequence")
    result = result.replace(
        duplicate_yamo_derive,
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]",
        1,
    )

    exact_select_impl = YAMO_IMPL.replace(
        "let mut candidate_groups = Vec::new();",
        "let mut candidates_by_id = BTreeMap::new();",
    ).replace(
        "candidate_groups.push(candidates);",
        "candidates_by_id.insert(unit.id, candidates);",
    ).replace(
        "candidate_groups, &view.inventories[0]",
        "candidates_by_id, &view.inventories[0]",
    )
    exact_select_bot = BOT_IMPL.replace(
        "let mut candidate_groups = Vec::new();",
        "let mut candidates_by_id = BTreeMap::new();",
    ).replace(
        "candidate_groups.push(candidates);",
        "candidates_by_id.insert(unit.id, candidates);",
    ).replace(
        "candidate_groups, &view.inventories[0]",
        "candidates_by_id, &view.inventories[0]",
    )
    replacements = (
        ("pub struct YamoBot", YAMO_STRUCT),
        ("impl YamoBot", exact_select_impl),
        ("impl Bot for YamoBot", exact_select_bot),
    )
    for marker, replacement in replacements:
        before = len(result.encode())
        result = _replace_item(result, marker, replacement)
        removals.append(
            {
                "marker": marker,
                "net_removed_bytes": before - len(result.encode()),
                "replacement_bytes": len(replacement.encode()),
            }
        )
    before = len(result.encode())
    result = _remove_item(result, "pub fn item_index(self)")
    removals.append(
        {"marker": "pub fn item_index(self)", "bytes": before - len(result.encode())}
    )
    fragments = (
        (
            "effective_cooldown,item_index,score,training_cost,tree_health,TOTAL_TURNS,",
            "effective_cooldown,item_index,training_cost,tree_health,TOTAL_TURNS,",
        ),
        (
            "Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,};",
            "Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,WOOD,};",
        ),
        ("use crate::bot::moisan::SecureOrchardBot;", "use crate::bot::moisan::YamoBot;"),
        ("let mut bot=SecureOrchardBot::new();", "let mut bot=YamoBot::new();"),
    )
    for old, new in fragments:
        if result.count(old) != 1:
            raise ValueError(f"expected one {old!r}")
        result = result.replace(old, new, 1)
    manifest = {
        "schema": "troll-farm-e7a-development-ablation/1",
        "arm": "FOCUSED_YAMO_EXACT_MOISAN",
        "evidence_boundary": "oversized attribution arm; cannot qualify for Arena",
        "baseline_sha256": BASELINE_SHA256,
        "candidate_bytes": len(result.encode()),
        "candidate_sha256": sha256_bytes(result.encode()),
        "logical_change": (
            "remove orchard and general opening/Yamo orchestration while retaining exact "
            "Moisan chop forecast, selector, target model, movement, and banking"
        ),
        "removed_or_replaced_items": removals,
        "identifier_renaming": False,
        "minification": False,
    }
    return result, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--arm",
        choices=("orchard-only", "focused-yamo-exact-moisan"),
        default="orchard-only",
    )
    args = parser.parse_args()
    builders = {
        "orchard-only": orchard_only,
        "focused-yamo-exact-moisan": focused_yamo_exact_moisan,
    }
    candidate, manifest = builders[args.arm](args.source.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
