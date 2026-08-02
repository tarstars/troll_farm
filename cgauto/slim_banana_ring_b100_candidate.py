#!/usr/bin/env python3
"""Produce the Arena-sized bounded banana-ring + b100/e6 source."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.slim_live_source import (
    DEAD_FRAGMENTS,
    DEAD_ITEMS,
    _remove_control_block,
    _remove_item,
    _replace_between,
    _replace_item,
)
from cgauto.slim_banana_factory_b100_candidate import (
    INACTIVE_FRAGMENTS,
    INACTIVE_ITEMS,
)


EXPECTED_INPUT_SHA256 = "f5c4caeab431e02a2faa60d92faed4e55e353f66bd5e177bf382c56e7bcd85e4"


def digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def replace_once(source: str, before: str, after: str) -> str:
    count = source.count(before)
    if count != 1:
        raise ValueError(f"expected one compatibility anchor, found {count}: {before!r}")
    return source.replace(before, after, 1)


def make_slim_candidate(source: str) -> str:
    actual = digest(source)
    if actual != EXPECTED_INPUT_SHA256:
        raise ValueError(
            f"compact candidate hash changed: expected {EXPECTED_INPUT_SHA256}, got {actual}"
        )

    result = source
    for before, after in (
        ("#![allow(dead_code,unused_imports)]", ""),
        ("pub use types::{Cell,GameState,Plant,PlantKind,Stats,Unit};", "pub use types::GameState;"),
        ("Stats,Stock,Unit,", "Stats,Unit,"),
        (",PLUM,WOOD,};", ",PLUM,};"),
    ):
        result = replace_once(result, before, after)

    for marker in DEAD_ITEMS:
        result = _remove_item(result, marker)
    for fragment in DEAD_FRAGMENTS:
        result = replace_once(result, fragment, "")

    result = _replace_item(result, "pub struct MoisanBot", "pub struct MoisanBot;")

    result = _remove_control_block(result, "#[cfg(test)]mod crop_provenance_tests")
    result = _remove_control_block(result, "#[cfg(test)]mod banana_ring_tests")
    for marker in INACTIVE_ITEMS:
        result = _remove_item(result, marker)
    for fragment in INACTIVE_FRAGMENTS:
        result = replace_once(result, fragment, "")

    # Telemetry-only state is absent from the submission artifact.  None of these
    # counters participates in command selection; full/slim stream equality is the gate.
    for name in (
        "activation_turn",
        "bootstrap_attempts",
        "reserve_promotions",
        "reserve_losses",
        "harvest_selections",
        "harvest_successes",
        "bank_harvest_selections",
        "bank_harvest_successes",
        "conversion_harvest_selections",
        "conversion_harvest_successes",
        "renewable_plant_attempts",
        "renewable_plant_successes",
        "trained_role_rewrites",
        "trained_forbidden_commands",
        "trained_opponent_crop_selections",
    ):
        field_type = "Option<i32>" if name == "activation_turn" else "usize"
        initial = "None" if name == "activation_turn" else "0"
        result = replace_once(result, f"banana_factory_{name}:{field_type},", "")
        result = replace_once(result, f"banana_factory_{name}:{initial},", "")

    result = _replace_item(
        result,
        "pub fn tuned_carry_regeneration_transit_idle_harvest()",
        "pub fn tuned_carry_regeneration_transit_idle_harvest()->Self{"
        "let mut bot=Self::with_opening_policy(YamoOpeningPolicy::TUNED_CARRY);"
        "bot.announcement=\"yamo-carry-regen-transit-idle-harvest-rust\";"
        "bot.idle_regeneration=true;bot.persistent_regeneration=true;"
        "bot.door_unblocking=true;bot.partial_bank_transit=true;bot.idle_harvest=true;bot}",
    )

    result = _replace_item(
        result,
        "pub fn banana_ring_opponent_crop_b100_e6()",
        "pub fn banana_ring_opponent_crop_b100_e6()->Self{let mut bot="
        "Self::banana_seed_factory();bot.inner.opponent_crop_bonus=100;"
        "bot.inner.opponent_crop_eta_limit=6;bot.inner.opponent_crop_start_turn=1;"
        "bot.inner.opponent_crop_min_seen=1;bot}",
    )
    result = replace_once(result, "banana_factory_ring:bool,", "")
    result = replace_once(result, "banana_factory_ring:false,", "")
    result = replace_once(result, "banana_factory_owned_crops:BTreeMap<Cell,bool>,", "")
    result = replace_once(result, "banana_factory_owned_crops:BTreeMap::new(),", "")

    for marker in (
        "fn banana_factory_plant_cell(",
        "fn banana_factory_harvest_target(",
        "fn banana_factory_starter_command(",
        "fn banana_factory_wood_command(",
    ):
        result = _remove_item(result, marker)
    result = _replace_item(
        result,
        "fn banana_ring_bank_command(",
        "fn banana_ring_bank_command(view:&GameState,unit:&Unit)->Option<String>{"
        "if unit.total_carried()==0{if is_adjacent(unit.cell,view.shacks[0]){return Some("
        "format!(\"PICK {} BANANA\",unit.id));}let distance=bfs_distances(&view.walkable,"
        "&[unit.cell]);return Self::banana_factory_home_doors(view,0).into_iter().filter("
        "|cell|distance.contains_key(cell)).min_by_key(|cell|(distance[cell],*cell)).map("
        "|cell|format!(\"MOVE {} {} {}\",unit.id,cell.0,cell.1));}YamoBot::bank_candidates("
        "view,unit).into_iter().max_by(|left,right|left.score.total_cmp(&right.score)).map("
        "|candidate|candidate.command)}",
    )
    result = replace_once(
        result,
        "Self::banana_factory_bank_command(view,starter)",
        "Self::banana_ring_bank_command(view,starter)",
    )
    result = _remove_item(result, "fn banana_factory_bank_command(")
    result = _remove_item(result, "fn banana_factory_promote_reserve(")
    result = _remove_item(result, "fn banana_ring_goal(")
    result = replace_once(
        result,
        "let goal=self.banana_ring_goal(view);",
        "let goal=(self.banana_factory_initial_budget.unwrap_or(0).max(0)as usize)"
        ".min(self.banana_ring_cells(view).len());",
    )
    result = _replace_item(
        result,
        "fn banana_factory_commands(",
        "fn banana_factory_commands(&mut self,view:&GameState)->Vec<String>{"
        "self.banana_ring_commands(view)}",
    )
    result = replace_once(
        result,
        "if self.banana_factory_ring&&self.banana_factory_pending_harvest.is_none()",
        "if self.banana_factory_pending_harvest.is_none()",
    )
    result = _replace_item(
        result,
        "fn banana_ring_issue_harvest(",
        "fn banana_ring_issue_harvest(&mut self,view:&GameState,starter:&Unit,target:Cell,"
        "bank_source:bool)->String{if starter.cell!=target{return format!("
        "\"MOVE {} {} {}\",starter.id,target.0,target.1);}self.banana_factory_pending_harvest="
        "Some((view.turn,starter.carry[BANANA],bank_source));format!(\"HARVEST {}\",starter.id)}",
    )
    result = _replace_item(
        result,
        "fn banana_ring_promote_reserve(",
        "fn banana_ring_promote_reserve(&mut self,view:&GameState){let ring:BTreeSet<Cell>="
        "self.banana_ring_cells(view).iter().copied().collect();self.banana_factory_reserve="
        "view.plants.iter().filter(|plant|plant.health>0&&plant.kind==PlantKind::Banana&&"
        "ring.contains(&plant.cell)&&Self::banana_ring_is_diagonal(view,plant.cell))"
        ".map(|plant|plant.cell).min();}",
    )
    result = _replace_between(
        result,
        "self.banana_factory_owned_crops.retain(|cell,_|",
        "if self.banana_factory_reserve.is_some_and",
        "",
    )
    result = replace_once(
        result,
        "if!self.banana_ring_release_mothers(view){if let Some(starter)=view.unit(starter_id){"
        "let protected_mother=self.banana_ring_cells(view).contains(&starter.cell)&&"
        "Self::banana_ring_is_diagonal(view,starter.cell)&&view.plant_at(starter.cell)"
        ".is_some_and(|index|{let plant=&view.plants[index];plant.health>0&&"
        "plant.kind==PlantKind::Banana});if protected_mother{if let Some(slot)="
        "Self::unit_action_slot(&commands,&unit_ids,starter_id){if commands[slot]"
        ".split_whitespace().next().is_some_and(|verb|verb==\"CHOP\"){"
        "commands[slot]=\"WAIT\".to_string();}}}}}",
        "if!self.banana_ring_release_mothers(view){if let Some(starter)=view.unit(starter_id){"
        "if self.banana_ring_cells(view).contains(&starter.cell)&&"
        "Self::banana_ring_is_diagonal(view,starter.cell)&&view.plant_at(starter.cell)"
        ".is_some_and(|i|view.plants[i].health>0&&view.plants[i].kind==PlantKind::Banana){"
        "if let Some(slot)=Self::unit_action_slot(&commands,&unit_ids,starter_id){"
        "if commands[slot].starts_with(\"CHOP \"){commands[slot]=\"WAIT\".to_string();}}}}}",
    )
    for before, after in (
        (
            "match source{BananaFactoryPlantSource::BankBootstrap=>{"
            "self.banana_factory_bootstrap_attempts+=1;}"
            "BananaFactoryPlantSource::RenewableHarvest=>{"
            "self.banana_factory_renewable_plant_attempts+=1;}}",
            "",
        ),
        ("self.banana_factory_trained_opponent_crop_selections+=1;", ""),
        ("self.banana_factory_activation_turn=Some(view.turn);", ""),
        ("self.banana_factory_trained_role_rewrites+=1;", ""),
        ("self.banana_factory_renewable_plant_successes+=1;", ""),
        (
            "self.banana_factory_harvest_successes+=1;if bank_source{"
            "self.banana_factory_bank_harvest_successes+=1;}else{"
            "self.banana_factory_conversion_harvest_successes+=1;}",
            "",
        ),
        ("self.banana_factory_reserve_losses+=1;", ""),
        (
            "if let Some((turn,before_carry,bank_source))=self.banana_factory_pending_harvest",
            "if let Some((turn,before_carry,_bank_source))=self.banana_factory_pending_harvest",
        ),
        (
            "if self.banana_factory_reserve.is_some_and(|cell|!self.banana_factory_owned_crops"
            ".contains_key(&cell)){self.banana_factory_reserve=None;}"
            "self.banana_factory_promote_reserve(view);",
            "self.banana_ring_promote_reserve(view);",
        ),
        (
            "let bank_seed=source==BananaFactoryPlantSource::BankBootstrap;"
            "self.banana_factory_owned_crops.insert(cell,bank_seed);match source",
            "match source",
        ),
        (
            "self.banana_factory_owned_crops.get(&plant.cell).copied().unwrap_or(false)",
            "false",
        ),
    ):
        result = replace_once(result, before, after)
    result = _replace_between(
        result,
        "let own_count=view.units.iter().filter(|unit|unit.player==0).count();if self.banana_factory_enabled",
        "if let Some(geometry)=&self.geometry",
        "let own_count=view.units.iter().filter(|unit|unit.player==0).count();"
        "if self.banana_factory_enabled&&(self.banana_factory_active||own_count>=2){"
        "return self.banana_factory_commands(view);}",
    )
    result = _replace_between(
        result,
        "let market_active=self.task_market_enabled",
        "let mut commands=self.inner.commands(view);",
        "let market_active=false;self.inner.external_idle_unit=reserve_orchard.then_some("
        "self.starter_id).flatten();self.inner.external_protected_tree=reserve_orchard.then(||"
        "self.geometry.as_ref().map(|geometry|geometry.mother)).flatten();"
        "self.inner.external_orchard_task=None;",
    )
    result = _replace_between(
        result,
        "let repays_seed=self.task_market_enabled",
        "Self::replace_action(&mut commands,&unit_ids,starter_id,forced);",
        "",
    )
    result = _remove_control_block(result, "if self.task_market_enabled")

    size = len(result.encode())
    if size >= 100_000:
        raise ValueError(f"slim candidate remains over Arena limit: {size} bytes")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = make_slim_candidate(args.source.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    output_sha = digest(result)
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{output_sha}  {args.output.name}\n"
    )
    print(f"built {args.output}: {len(result.encode())} bytes")
    print(f"sha256 {output_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
