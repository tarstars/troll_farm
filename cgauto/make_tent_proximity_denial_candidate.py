#!/usr/bin/env python3
"""Build the owner-proposed enemy-tent proximity denial successor.

The transform is fail-closed over the exact active far-denial-d3 artifact. It adds a
two-worker coordination layer to ``SecureOrchardBot``:

* zero active trees cardinally adjacent to the enemy shack: exact parent behavior;
* one or two: one worker targets an adjacent tree and banks its wood, while the second
  targets an opponent-planted tree without a denial-driven return;
* more than two: both workers target distinct adjacent trees without denial-driven return.

Units carrying pre-existing unrelated cargo must bank before entering a non-banking role.
No resident source file is edited.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.slim_live_source import _item_span, _replace_item


REPO = Path(__file__).resolve().parent.parent
PARENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs"
)
PARENT_SHA256 = "307a07556ab79a3089995841575c07f4b001f2ea08ee5b13ff7586f0149c76cd"
OUTPUT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585578-owner-tent-proximity-denial-split-slim.min.rs"
)


SECURE_ORCHARD_STRUCT = (
    "pub struct SecureOrchardBot{inner:YamoBot,initialized:bool,"
    "starter_id:Option<i32>,geometry:Option<OrchardGeometry>,"
    "initial_natural:BTreeMap<Cell,PlantKind>,phase:OrchardPhase,"
    "plant_attempted:bool,minimum_enemy_eta:i32,require_idle_starter:bool,"
    "minimum_enemy_door_distance:i32,minimum_worker_speed:i32,"
    "own_planted:BTreeSet<Cell>,nonbank_denial_units:BTreeSet<i32>,}"
)


DENIAL_METHODS = (
    "fn active_tent_adjacent(view:&GameState)->Vec<Cell>{"
    "let mut cells:Vec<_>=ortho_neighbors(view.shacks[1]).into_iter()"
    ".filter(|cell|view.plant_at(*cell).is_some_and(|index|"
    "view.plants[index].health>0)).collect();cells.sort_unstable();cells}"
    "fn opponent_planted_cells(&self,view:&GameState)->Vec<Cell>{"
    "let mut cells:Vec<_>=view.plants.iter().filter(|plant|plant.health>0&&"
    "!self.initial_natural.contains_key(&plant.cell)&&"
    "!self.own_planted.contains(&plant.cell)).map(|plant|plant.cell).collect();"
    "cells.sort_unstable();cells.dedup();cells}"
    "fn best_denial_cell(view:&GameState,unit:&Unit,cells:&[Cell],"
    "used:&BTreeSet<Cell>)->Option<Cell>{let distance=bfs_distances("
    "&view.walkable,&[unit.cell]);cells.iter().filter(|cell|!used.contains(cell)&&"
    "view.plant_at(**cell).is_some_and(|index|view.plants[index].health>0)&&"
    "distance.contains_key(*cell)).min_by_key(|cell|(distance[*cell],**cell)).copied()}"
    "fn tree_denial_action(unit:&Unit,target:Cell)->String{"
    "if unit.cell==target{format!(\"CHOP {}\",unit.id)}else{"
    "format!(\"MOVE {} {} {}\",unit.id,target.0,target.1)}}"
    "fn banking_action(view:&GameState,unit:&Unit)->Option<String>{"
    "if unit.total_carried()<=0{return None;}if is_adjacent(unit.cell,view.shacks[0]){"
    "return Some(format!(\"DROP {}\",unit.id));}let distance=bfs_distances("
    "&view.walkable,&[unit.cell]);ortho_neighbors(view.shacks[0]).into_iter()"
    ".filter(|cell|view.walkable.contains(cell)&&distance.contains_key(cell))"
    ".min_by_key(|cell|(distance[cell],*cell)).map(|cell|"
    "format!(\"MOVE {} {} {}\",unit.id,cell.0,cell.1))}"
    "fn remember_own_plant_commands(&mut self,view:&GameState,commands:&[String],"
    "unit_ids:&[i32]){for unit in view.units.iter().filter(|unit|unit.player==0){"
    "let Some(slot)=Self::unit_action_slot(commands,unit_ids,unit.id)else{continue;};"
    "if commands[slot].split_whitespace().next()==Some(\"PLANT\"){"
    "self.own_planted.insert(unit.cell);}}}"
    "fn apply_tent_denial(&mut self,view:&GameState,mut commands:Vec<String>)"
    "->Vec<String>{self.own_planted.retain(|cell|view.plant_at(*cell).is_some());"
    "let mut unit_ids:Vec<_>=view.units.iter().filter(|unit|unit.player==0)"
    ".map(|unit|unit.id).collect();unit_ids.sort_unstable();"
    "let workers:Vec<_>=unit_ids.iter().copied().filter(|id|view.unit(*id)"
    ".is_some_and(|unit|unit.stats.chop_power>0)).take(2).collect();"
    "let adjacent=Self::active_tent_adjacent(view);"
    "if adjacent.is_empty(){self.nonbank_denial_units.clear();"
    "self.remember_own_plant_commands(view,&commands,&unit_ids);return commands;}"
    "let prior_nonbank=self.nonbank_denial_units.clone();"
    "let mut next_nonbank=BTreeSet::new();let mut used=BTreeSet::new();"
    "if adjacent.len()>2{for id in workers.iter().copied(){"
    "let Some(unit)=view.unit(id)else{continue;};"
    "if unit.total_carried()>0&&!prior_nonbank.contains(&id){"
    "if let Some(action)=Self::banking_action(view,unit){Self::replace_action("
    "&mut commands,&unit_ids,id,action);}continue;}"
    "let Some(target)=Self::best_denial_cell(view,unit,&adjacent,&used)else{continue;};"
    "used.insert(target);next_nonbank.insert(id);Self::replace_action("
    "&mut commands,&unit_ids,id,Self::tree_denial_action(unit,target));}}else{"
    "let banker=workers.iter().filter_map(|id|{let unit=view.unit(*id)?;"
    "let target=Self::best_denial_cell(view,unit,&adjacent,&BTreeSet::new())?;"
    "let distance=bfs_distances(&view.walkable,&[unit.cell]);"
    "Some((distance[&target],*id,target))}).min();"
    "let banker_id=banker.map(|(_,id,_)|id);if let Some((_,id,target))=banker{"
    "if let Some(unit)=view.unit(id){if let Some(action)=Self::banking_action(view,unit){"
    "Self::replace_action(&mut commands,&unit_ids,id,action);}else{used.insert(target);"
    "Self::replace_action(&mut commands,&unit_ids,id,"
    "Self::tree_denial_action(unit,target));}}}"
    "let planted=self.opponent_planted_cells(view);for id in workers.iter().copied()"
    ".filter(|id|Some(*id)!=banker_id){let Some(unit)=view.unit(id)else{continue;};"
    "if unit.total_carried()>0&&!prior_nonbank.contains(&id){"
    "if let Some(action)=Self::banking_action(view,unit){Self::replace_action("
    "&mut commands,&unit_ids,id,action);}continue;}"
    "let Some(target)=Self::best_denial_cell(view,unit,&planted,&used)else{continue;};"
    "used.insert(target);next_nonbank.insert(id);Self::replace_action("
    "&mut commands,&unit_ids,id,Self::tree_denial_action(unit,target));break;}}"
    "self.nonbank_denial_units=next_nonbank;"
    "MoisanBot::resolve_move_conflicts(view,&mut commands);"
    "self.remember_own_plant_commands(view,&commands,&unit_ids);commands}"
)


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def make_candidate(parent: str) -> str:
    actual = digest_text(parent)
    if actual != PARENT_SHA256:
        raise ValueError(
            f"active parent hash changed: expected {PARENT_SHA256}, got {actual}"
        )
    result = _replace_item(
        parent,
        "pub struct SecureOrchardBot",
        SECURE_ORCHARD_STRUCT,
    )

    initializer = "minimum_worker_speed,}}"
    replacement = (
        "minimum_worker_speed,own_planted:BTreeSet::new(),"
        "nonbank_denial_units:BTreeSet::new(),}}"
    )
    if result.count(initializer) != 1:
        raise ValueError(
            f"expected one SecureOrchard initializer, found {result.count(initializer)}"
        )
    result = result.replace(initializer, replacement, 1)

    impl_start, impl_end = _item_span(result, "impl SecureOrchardBot")
    secure_impl = result[impl_start:impl_end]
    secure_impl = secure_impl[:-1] + DENIAL_METHODS + "}"
    result = result[:impl_start] + secure_impl + result[impl_end:]

    bot_start, bot_end = _item_span(result, "impl Bot for SecureOrchardBot")
    bot_impl = result[bot_start:bot_end]
    expected_returns = bot_impl.count("return commands;")
    if expected_returns != 7:
        raise ValueError(
            f"expected seven early command returns, found {expected_returns}"
        )
    bot_impl = bot_impl.replace(
        "return commands;", "return self.apply_tent_denial(view,commands);"
    )
    final_marker = ";commands}}"
    if bot_impl.count(final_marker) != 1:
        raise ValueError(
            f"expected one final command return, found {bot_impl.count(final_marker)}"
        )
    bot_impl = bot_impl.replace(
        final_marker, ";self.apply_tent_denial(view,commands)}}", 1
    )
    result = result[:bot_start] + bot_impl + result[bot_end:]

    announcement = "yamo-far-denial-no-return-d3-rust"
    if result.count(announcement) != 1:
        raise ValueError(
            f"expected one parent announcement, found {result.count(announcement)}"
        )
    return result.replace(
        announcement, "yamo-tent-proximity-denial-split-rust", 1
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=PARENT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    candidate = make_candidate(args.parent.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate, encoding="utf-8")
    digest = digest_text(candidate)
    sidecar = args.output.with_name(args.output.name + ".sha256")
    sidecar.write_text(f"{digest}  {args.output.name}\n", encoding="utf-8")
    print(f"built {args.output}: {len(candidate.encode())} bytes")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
