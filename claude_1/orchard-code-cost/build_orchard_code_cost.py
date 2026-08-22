#!/usr/bin/env python3
"""Build both orchard-code-cost artifacts from the frozen live E7a baseline.

Stage 1 (reference): one anchor-checked edit makes the secure apple orchard
permanently dormant — the Dormant-phase activation branch becomes an
unconditional return. Nothing else changes.

Stage 2 (stripped): from the reference, physically delete the now-unreachable
orchard-exclusive implementation: the contiguous OrchardPhase / OrchardGeometry /
OrchardCycle / SecureOrchardBot region (types, wrapper impl, Bot impl), the
external idle/protected-tree reservation channel in YamoBot, all protected-tree
parameter/argument/filter plumbing, and the main()/import switch to plain
YamoBot. Shared infrastructure is retained: PredictedTree (chop prediction),
generic apple parse/plant/pick/harvest, chopping, banking, denial, the Bot
trait, and YamoBot's own opponent_eta_penalty.

Task: 20260804-orchard-code-cost-ablation. Baseline is read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"

ACTIVATION_BRANCH = (
    "let starter_is_busy=self.require_idle_starter&&!Self::starter_control_is_idle("
    "&commands,&unit_ids,starter);"
    "if checkpoint&&has_second&&!starter_is_busy&&self.can_activate(view,starter,&geometry)"
    "{self.phase=OrchardPhase::CarryingSeed;}else{return commands;}"
)

ORCHARD_BLOCK_START = "#[derive(Clone,Copy,Debug,Eq,PartialEq)]enum OrchardPhase{"
# The }}} run closes fn commands, impl Bot for SecureOrchardBot, and mod moisan;
# the deletion must consume the first two braces and keep the mod's closer.
ORCHARD_BLOCK_END = "}}}use crate::game::GameState;pub trait Bot{"
ORCHARD_BLOCK_END_KEEP = 2  # delete through the first two closing braces

# (old, new, expected_count) applied to the reference, in order.
STRIP_OPS = [
    (
        "opponent_eta_penalty:i32,external_idle_unit:Option<i32>,"
        "external_protected_tree:Option<Cell>,}",
        "opponent_eta_penalty:i32,}",
        1,
    ),
    (
        "opponent_eta_penalty:0,external_idle_unit:None,external_protected_tree:None,}}",
        "opponent_eta_penalty:0,}}",
        1,
    ),
    (
        "if let Some(id)=self.external_idle_unit{by_id.insert(id,vec![MoisanBot::wait()]);}",
        "",
        1,
    ),
    ("let protected_tree=self.external_protected_tree;", "", 1),
    (
        "if let Some(protected)=self.external_protected_tree{candidates.retain("
        "|candidate|{!matches!(candidate.target,Target::Tree(cell)|Target::Bank(cell)"
        "|Target::Cell(cell)if cell==protected)});}",
        "",
        1,
    ),
    (
        "if let Some(protected)=protected_tree{candidates.retain("
        "|candidate|candidate.target!=Target::Tree(protected));}",
        "",
        1,
    ),
    (",protected_tree,opponent_eta_penalty", ",opponent_eta_penalty", 3),
    (",protected_tree,self.opponent_eta_penalty", ",self.opponent_eta_penalty", 3),
    (",false,true,None,self.opponent_eta_penalty,)",
     ",false,true,self.opponent_eta_penalty,)", 1),
    ("Self::idle_harvest_candidates(view,unit,protected_tree)",
     "Self::idle_harvest_candidates(view,unit)", 1),
    ("Some(plant.cell)!=protected_tree&&", "", 1),
    ("protected_tree:Option<Cell>,", "", 4),
    (
        "let mut bot=SecureOrchardBot::new();",
        "let mut bot=YamoBot::tuned_carry_regeneration_transit_idle_harvest();",
        1,
    ),
    (
        "use crate::bot::moisan::SecureOrchardBot;",
        "use crate::bot::moisan::YamoBot;",
        1,
    ),
]

RESIDUE = [
    "SecureOrchardBot", "OrchardPhase", "OrchardGeometry", "OrchardCycle",
    "external_idle_unit", "external_protected_tree", "protected_tree",
    "initial_natural", "can_activate", "can_continue_seed",
    "reconcile_initial_natural", "starter_control_is_idle",
    "require_idle_starter", "with_policy",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_counted(source: str, old: str, new: str, expected: int, label: str) -> str:
    count = source.count(old)
    if count != expected:
        raise ValueError(f"{label}: expected {expected} occurrences of {old[:60]!r}, found {count}")
    return source.replace(old, new)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--stripped", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--force", action="store_true",
                        help="allow regenerating existing artifacts (rebuild check)")
    args = parser.parse_args()

    baseline = args.baseline.read_bytes()
    if digest(baseline) != BASELINE_SHA256:
        parser.error("baseline SHA-256 mismatch — refusing to build")
    if not args.force:
        for p in (args.reference, args.stripped, args.manifest):
            if p.exists():
                parser.error(f"refusing to overwrite {p}")

    source = baseline.decode()

    # Stage 1: activation-disabled reference.
    reference = replace_counted(
        source, ACTIVATION_BRANCH, "return commands;", 1, "activation branch"
    )

    # Stage 2: physical strip.
    stripped = reference
    if stripped.count(ORCHARD_BLOCK_END) != 1:
        raise ValueError("orchard block end anchor is not unique")
    start = stripped.index(ORCHARD_BLOCK_START)
    end = stripped.index(ORCHARD_BLOCK_END) + ORCHARD_BLOCK_END_KEEP
    if not (start < end):
        raise ValueError("orchard block boundaries out of order")
    removed_block = stripped[start:end]
    for marker in ("SecureOrchardBot", "impl Bot for SecureOrchardBot", "OrchardCycle"):
        if marker not in removed_block:
            raise ValueError(f"orchard block does not contain {marker}")
    if "impl Bot for YamoBot" in removed_block:
        raise ValueError("orchard block would swallow the YamoBot Bot impl")
    stripped = stripped[:start] + stripped[end:]

    for old, new, expected in STRIP_OPS:
        stripped = replace_counted(stripped, old, new, expected, "strip op")
    for residue in RESIDUE:
        if residue in stripped:
            raise ValueError(f"residue survived: {residue}")

    reference_bytes = reference.encode()
    stripped_bytes = stripped.encode()
    manifest = {
        "schema": "troll-farm-orchard-code-cost-v1",
        "task_id": "20260804-orchard-code-cost-ablation",
        "baseline": {
            "path": str(args.baseline),
            "bytes": len(baseline),
            "characters": len(source),
            "sha256": BASELINE_SHA256,
        },
        "reference": {
            "path": str(args.reference),
            "bytes": len(reference_bytes),
            "characters": len(reference),
            "sha256": digest(reference_bytes),
            "semantic_change": "secure apple orchard never activates; nothing else",
        },
        "stripped": {
            "path": str(args.stripped),
            "bytes": len(stripped_bytes),
            "characters": len(stripped),
            "sha256": digest(stripped_bytes),
        },
        "cost": {
            "orchard_block_bytes": len(removed_block),
            "bytes_removed_vs_baseline": len(baseline) - len(stripped_bytes),
            "characters_removed_vs_baseline": len(source) - len(stripped),
            "percent_of_baseline": round(100 * (len(baseline) - len(stripped_bytes)) / len(baseline), 3),
            "percent_of_100k_allowance": round((len(baseline) - len(stripped_bytes)) / 1000, 3),
        },
        "gates_pending": [
            "reference and stripped: optimized compile + empty input",
            "reference vs live baseline: ten open fixtures + 25-game packet (expected: identical except orchard-activation game)",
            "stripped vs reference: identical command streams on all open panel cases",
        ],
    }
    args.reference.parent.mkdir(parents=True, exist_ok=True)
    args.reference.write_bytes(reference_bytes)
    args.stripped.write_bytes(stripped_bytes)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["cost"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
