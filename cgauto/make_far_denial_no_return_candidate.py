#!/usr/bin/env python3
"""Build the owner-directed distance-3 far-denial no-return candidate.

The transform reconstructs the exact live slim resident from its pinned full parent, then
changes only initial focus-species chopping.  For a focused tree whose terrain BFS distance
to the nearest own shack door is greater than three, the planner excludes the return leg
and allows a full-capacity troll to keep chopping (the referee still applies CHOP damage;
wood from a lethal full-capacity chop is discarded).  Near and non-denial banking remains
unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.make_opponent_crop_candidate import (  # noqa: E402
    PARENT,
    PARENT_SHA256,
    RESIDENT_SLIM_SHA256,
    digest_text,
)
from cgauto.slim_live_source import _replace_item, slim  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
OUTPUT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs"
)
DISTANCE_THRESHOLD = 3


CHOP_CANDIDATES = (
    "fn chop_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,)"
    "->Vec<Candidate>{let mut out=Vec::new();if unit.stats.chop_power<=0{return out;}"
    "let from_unit=bfs_distances(&view.walkable,&[unit.cell]);let shack_starts:Vec<Cell>="
    "ortho_neighbors(view.shacks[0]).iter().filter(|cell|view.walkable.contains(cell))"
    ".copied().collect();let to_shack=bfs_distances(&view.walkable,&shack_starts);"
    "let opponent_trolls=view.units.iter().filter(|unit|unit.player==1).count();"
    "for plant in&view.plants{if plant.health<=0||!from_unit.contains_key(&plant.cell)"
    "{continue;}let travel_turns=Self::ceil_div(from_unit[&plant.cell],"
    "unit.stats.movement_speed);let Some(predicted)=Self::predict_tree(view,plant,"
    "travel_turns)else{continue;};if predicted.size<=0||predicted.health<=0{continue;}"
    "let route_distance=to_shack.get(&plant.cell).copied().unwrap_or(10_000);"
    "let initial_denial=Some(plant.kind)==type_to_cut&&opponent_trolls<=2;"
    "let far_initial_denial=initial_denial&&route_distance>3;"
    "if unit.free_capacity()<=0&&!far_initial_denial{continue;}"
    "let return_turns=Self::ceil_div(route_distance,unit.stats.movement_speed);"
    "let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,"
    "unit.stats.chop_power)else{continue;};let turns=if far_initial_denial"
    "{travel_turns+chop_turns}else{travel_turns+chop_turns+return_turns+1}.max(1);"
    "if turns>TOTAL_TURNS-view.turn+1{continue;}let wood=final_size.min("
    "unit.free_capacity());if wood<=0&&!far_initial_denial{continue;}"
    "let mut score=if far_initial_denial{0.0}else{1000.0*wood as f64/turns as f64};"
    "if initial_denial{let opponent_distance=manhattan(plant.cell,view.shacks[1]);"
    "score+=900.0/(1+opponent_distance)as f64;}let command=if plant.cell==unit.cell"
    "{format!(\"CHOP {}\",unit.id)}else{format!(\"MOVE {} {} {}\",unit.id,"
    "plant.cell.0,plant.cell.1)};out.push(Candidate{command,score,"
    "target:Target::Tree(plant.cell),});}out}"
)


MAIN_CANDIDATES = (
    "fn main_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,"
    "idle_regeneration:bool,safe_regeneration:bool,protected_tree:Option<Cell>,"
    "opponent_eta_penalty:i32,)->Vec<Candidate>{let mut out=vec![MoisanBot::wait()];"
    "let carried=unit.total_carried();if safe_regeneration&&Self::carried_fruit(unit)"
    ".is_some(){out.extend(Self::bank_candidates(view,unit));return out;}"
    "if carried>0&&is_adjacent(unit.cell,view.shacks[0]){out.extend("
    "Self::bank_candidates(view,unit));}if safe_regeneration&&carried==0&&"
    "view.turn>=100&&view.plants.len()<=2&&view.units.iter().filter(|unit|"
    "unit.player==0).count()>=2&&is_adjacent(unit.cell,view.shacks[0])&&"
    "view.plant_at(unit.cell).is_none(){for(priority,kind)in Self::inventory_fruits(view)"
    ".into_iter().enumerate(){out.push(Candidate{command:format!(\"PICK {} {}\","
    "unit.id,kind.as_str()),score:7500.0-priority as f64,"
    "target:Target::Cell(unit.cell),});}}if unit.free_capacity()<=0{"
    "let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,protected_tree,"
    "opponent_eta_penalty,);if chops.is_empty(){out.extend(Self::bank_candidates(view,"
    "unit));}else{out.extend(chops);}return out;}let chops=Self::yamo_chop_candidates("
    "view,unit,type_to_cut,protected_tree,opponent_eta_penalty,);if idle_regeneration&&"
    "chops.is_empty(){return Self::endgame_candidates(view,unit,type_to_cut,"
    "safe_regeneration,protected_tree,opponent_eta_penalty,);}if chops.is_empty()&&"
    "carried>0{out.extend(Self::bank_candidates(view,unit));}else{out.extend(chops);}"
    "out}"
)


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
    result = _replace_item(result, "fn chop_candidates(", CHOP_CANDIDATES)
    result = _replace_item(result, "fn main_candidates(", MAIN_CANDIDATES)
    announcement = "yamo-carry-regen-transit-idle-harvest-rust"
    if result.count(announcement) != 1:
        raise ValueError(
            f"expected one live announcement anchor, found {result.count(announcement)}"
        )
    return result.replace(
        announcement, "yamo-far-denial-no-return-d3-rust", 1
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=PARENT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    candidate = make_candidate(args.parent.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    digest = hashlib.sha256(candidate.encode()).hexdigest()
    sidecar = args.output.with_name(args.output.name + ".sha256")
    sidecar.write_text(f"{digest}  {args.output.name}\n")
    print(f"built {args.output}: {len(candidate.encode())} bytes")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
