#!/usr/bin/env python3
"""Build an H1 opportunity-cost-gate arm from the frozen r36 parent.

Implements the Phase-A gate design (claude_1/h1-orchard-gate/gate-design-report.md)
with two exact-anchor edits: append the gate to the activation condition, and
prepend the gate implementation (const GATE_MARGIN + two pure associated fns) to
the SecureOrchardBot impl. The margin is the single tunable; every arm of the H1
protocol is this builder with a different --margin.

C0 bridge: --margin 'i32::MIN' must be command-identical to the parent.
A-inf bridge: --margin 'i32::MAX' must never activate the orchard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PARENT_SHA256 = "2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381"

COND_ANCHOR = "if checkpoint&&has_second&&self.can_activate(view,starter,&geometry){"
COND_NEW = ("if checkpoint&&has_second&&self.can_activate(view,starter,&geometry)"
            "&&Self::orchard_gate(view,starter,&geometry){")

IMPL_ANCHOR = ("fn can_activate(&self,view:&GameState,starter:&Unit,"
               "geometry:&OrchardGeometry)->bool{")

GATE_CODE = (
    "const GATE_MARGIN:i32={MARGIN};"
    "fn displaced_projection(view:&GameState,starter:&Unit,doors:&[Cell],turns_left:i32)->i32{{"
    "if starter.stats.chop_power<=0||starter.free_capacity()<=0||doors.is_empty()||turns_left<=0{{return 0;}}"
    "let from_unit=bfs_distances(&view.walkable,&[starter.cell]);"
    "let to_doors=bfs_distances(&view.walkable,doors);"
    "let mut best=0;"
    "for plant in &view.plants{{"
    "if plant.health<=0{{continue;}}"
    "let Some(distance)=from_unit.get(&plant.cell)else{{continue;}};"
    "let first_chop_eta=MoisanBot::ceil_div(*distance,starter.stats.movement_speed);"
    "let Some(predicted)=MoisanBot::predict_tree(view,plant,first_chop_eta)else{{continue;}};"
    "if predicted.size<=0||predicted.health<=0{{continue;}}"
    "let Some((chop_turns,final_size))=MoisanBot::chop_outcome(view,plant,predicted,starter.stats.chop_power)else{{continue;}};"
    "let wood=final_size.min(starter.free_capacity());"
    "if wood<=0{{continue;}}"
    "let Some(return_cells)=to_doors.get(&plant.cell)else{{continue;}};"
    "let cycle_eta=(first_chop_eta+chop_turns+MoisanBot::ceil_div(*return_cells,starter.stats.movement_speed)+1).max(1);"
    "best=best.max(crate::game::rules::WOOD_POINTS*wood*(turns_left/cycle_eta));"
    "}}best}}"
    "fn orchard_gate(view:&GameState,starter:&Unit,geometry:&OrchardGeometry)->bool{{"
    "let turns_left=TOTAL_TURNS-view.turn+1;"
    "let cadence=effective_cooldown(PlantKind::Apple,true).max(1);"
    "let bank_interval=cadence.max(2);"
    "let travel=bfs_distances(&view.walkable,&[starter.cell]).get(&geometry.mother)"
    ".map(|distance|MoisanBot::ceil_div(*distance,starter.stats.movement_speed)).unwrap_or(10_000);"
    "let first_bank_eta=travel+2+5*cadence+2;"
    "let orchard=(turns_left-first_bank_eta).max(0)/bank_interval;"
    "let displaced=Self::displaced_projection(view,starter,&geometry.doors,turns_left);"
    "orchard.saturating_sub(displaced)>=Self::GATE_MARGIN}}"
)

MARGIN_FORM = re.compile(r"^(i32::MIN|i32::MAX|-?\d{1,9})$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--margin", required=True,
                        help="i32::MIN (C0 bridge), i32::MAX (A-inf bridge), or an integer")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    if not MARGIN_FORM.match(args.margin):
        parser.error(f"margin {args.margin!r} is not i32::MIN, i32::MAX, or an integer")
    parent = args.parent.read_bytes()
    if digest(parent) != PARENT_SHA256:
        parser.error("parent SHA-256 does not match the frozen r36 candidate")
    if args.candidate.exists() or args.manifest.exists():
        parser.error("refusing to overwrite an existing arm artifact")

    source = parent.decode()
    for needle, expected, label in [
        (COND_ANCHOR, 1, "activation condition"),
        (IMPL_ANCHOR, 1, "impl insertion anchor"),
        ("orchard_gate", 0, "collision: orchard_gate"),
        ("displaced_projection", 0, "collision: displaced_projection"),
        ("GATE_MARGIN", 0, "collision: GATE_MARGIN"),
    ]:
        count = source.count(needle)
        if count != expected:
            raise ValueError(f"{label}: expected {expected}, found {count}")

    gate_code = GATE_CODE.format(MARGIN=args.margin)
    candidate_text = source.replace(COND_ANCHOR, COND_NEW, 1)
    candidate_text = candidate_text.replace(IMPL_ANCHOR, gate_code + IMPL_ANCHOR, 1)
    if candidate_text.count("orchard_gate") != 2:  # definition + call
        raise ValueError("gate wiring count wrong after edits")

    candidate = candidate_text.encode()
    manifest = {
        "schema": "troll-farm-h1-orchard-gate-arm-v1",
        "task_id": "20260804-h1-orchard-opportunity-cost-gate",
        "margin": args.margin,
        "parent": {"path": str(args.parent), "bytes": len(parent), "sha256": PARENT_SHA256},
        "candidate": {
            "path": str(args.candidate),
            "bytes": len(candidate),
            "sha256": digest(candidate),
            "added_bytes": len(candidate) - len(parent),
        },
        "design_report": "claude_1/h1-orchard-gate/gate-design-report.md",
        "gates_pending": [
            "G1 static (rebuild, compile, empty input)",
            "G2 bridge equality (C0 vs parent; A-inf vs activation-disabled reference)",
            "G3 activation-rate sanity on the 25-game packet",
            "G4 closed-loop paired panel (integrator)",
        ],
    }
    args.candidate.parent.mkdir(parents=True, exist_ok=True)
    args.candidate.write_bytes(candidate)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["candidate"] | {"margin": args.margin}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
