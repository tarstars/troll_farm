#!/usr/bin/env python3
"""Build the fixed b100/e6 crop-suppression candidate from the exact parent.

The transform first reproduces the arena-validated slim resident byte for byte.
It then inserts only the prospectively selected provenance tracker and priority
operation.  Every source anchor is unique and every parent hash is pinned.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.slim_live_source import slim  # noqa: E402


PARENT = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
)
OUTPUT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs"
)
PARENT_SHA256 = "da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9"
RESIDENT_SLIM_SHA256 = (
    "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
)


def digest_text(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def replace_once(source: str, before: str, after: str) -> str:
    count = source.count(before)
    if count != 1:
        raise ValueError(f"expected one candidate anchor, found {count}: {before[:80]!r}")
    return source.replace(before, after, 1)


def make_candidate(parent: str) -> str:
    actual_parent = digest_text(parent)
    if actual_parent != PARENT_SHA256:
        raise ValueError(
            f"full parent hash changed: expected {PARENT_SHA256}, got {actual_parent}"
        )
    result = slim(parent)
    rebuilt_resident = digest_text(result)
    if rebuilt_resident != RESIDENT_SLIM_SHA256:
        raise ValueError(
            "slim parent reconstruction changed: "
            f"expected {RESIDENT_SLIM_SHA256}, got {rebuilt_resident}"
        )

    result = replace_once(
        result,
        "external_protected_tree:Option<Cell>,}",
        "external_protected_tree:Option<Cell>,plant_history_initialized:bool,"
        "previous_plants:BTreeSet<Cell>,own_plant_attempts:BTreeSet<Cell>,"
        "opponent_crops:BTreeSet<Cell>,}",
    )
    result = replace_once(
        result,
        "external_protected_tree:None,}}pub fn tuned_carry_regeneration_transit_idle_harvest",
        "external_protected_tree:None,plant_history_initialized:false,"
        "previous_plants:BTreeSet::new(),own_plant_attempts:BTreeSet::new(),"
        "opponent_crops:BTreeSet::new(),}}"
        "pub fn tuned_carry_regeneration_transit_idle_harvest",
    )

    provenance_methods = (
        "fn reconcile_opponent_crops(&mut self,view:&GameState){"
        "let current:BTreeSet<Cell>=view.plants.iter().filter(|plant|plant.health>0)"
        ".map(|plant|plant.cell).collect();if self.plant_history_initialized{"
        "for cell in current.difference(&self.previous_plants){"
        "if!self.own_plant_attempts.contains(cell){self.opponent_crops.insert(*cell);}}"
        "self.opponent_crops.retain(|cell|current.contains(cell));}else{"
        "self.plant_history_initialized=true;}self.previous_plants=current;"
        "self.own_plant_attempts.clear();}"
        "fn remember_own_plant_attempts(&mut self,view:&GameState,commands:&[String]){"
        "for command in commands{let fields:Vec<_>=command.split_whitespace().collect();"
        "if fields.first()!=Some(&\"PLANT\"){continue;}let Some(unit)=fields.get(1)"
        ".and_then(|id|id.parse().ok()).and_then(|id|view.unit(id))"
        ".filter(|unit|unit.player==0)else{continue;};"
        "self.own_plant_attempts.insert(unit.cell);}}"
        "fn apply_opponent_crop_priority(&self,view:&GameState,unit:&Unit,"
        "candidates:&mut[Candidate]){if self.opponent_crops.is_empty(){return;}"
        "let distance=bfs_distances(&view.walkable,&[unit.cell]);for candidate in candidates{"
        "let Target::Tree(cell)=candidate.target else{continue;};"
        "if!self.opponent_crops.contains(&cell){continue;}"
        "let Some(cells)=distance.get(&cell)else{continue;};"
        "let eta=MoisanBot::ceil_div(*cells,unit.stats.movement_speed);"
        "if eta<=6{candidate.score+=100.0;}}}"
    )
    result = replace_once(
        result,
        "fn reconcile_regeneration_commitments(&mut self,view:&GameState)",
        provenance_methods
        + "fn reconcile_regeneration_commitments(&mut self,view:&GameState)",
    )
    result = replace_once(
        result,
        "fn commands(&mut self,view:&GameState)->Vec<String>{"
        "self.reconcile_regeneration_commitments(view);self.ensure_opening(view);",
        "fn commands(&mut self,view:&GameState)->Vec<String>{"
        "self.reconcile_opponent_crops(view);"
        "self.reconcile_regeneration_commitments(view);self.ensure_opening(view);",
    )
    result = replace_once(
        result,
        "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)};"
        "if endgame&&self.idle_harvest",
        "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)};"
        "self.apply_opponent_crop_priority(view,unit,&mut candidates);"
        "if endgame&&self.idle_harvest",
    )
    result = replace_once(
        result,
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
        "self.remember_selected_regeneration(&selected);out.extend(selected);",
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
        "self.remember_selected_regeneration(&selected);"
        "self.remember_own_plant_attempts(view,&selected);out.extend(selected);",
    )
    result = replace_once(
        result,
        "&BTreeSet::from([geometry.mother]),);commands}}}",
        "&BTreeSet::from([geometry.mother]),);"
        "self.inner.remember_own_plant_attempts(view,&commands);commands}}}",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=PARENT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    candidate = make_candidate(args.parent.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    digest = digest_text(candidate)
    sidecar = args.output.with_name(args.output.name + ".sha256")
    sidecar.write_text(f"{digest}  {args.output.name}\n")
    print(f"built {args.output}: {len(candidate.encode())} bytes")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
