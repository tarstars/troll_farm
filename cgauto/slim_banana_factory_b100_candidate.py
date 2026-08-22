#!/usr/bin/env python3
"""Produce the Arena-sized banana-factory+b100/e6 owner-override source.

This fail-closed specialization reuses the general slimmer's compiler-proven
dead-item inventory, then fixes all constructor-disabled experiment families
to their exact values.  The active banana factory and combined constructor are
preserved.  Full-source/slim command-stream equality remains a mandatory gate.
"""

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


EXPECTED_INPUT_SHA256 = "37469297692a5a06337098c8c2f4f621ca7144ce6466dc11c6ddf9c10ace4b61"

TEST_MODULE = "#[cfg(test)]mod crop_provenance_tests"

INACTIVE_ITEMS = (
    "impl Bot for MoisanBot",
    "fn ensure_focus_type(",
    "fn ensure_desired_second(",
    "pub const ALL:",
    "fn ring_cells(",
    "fn is_ring_diagonal(",
    "fn farmer_candidates(",
    "fn ring_chop_candidates(",
    "fn main_loop_candidates(",
    "fn endgame_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,)->Vec<Candidate>",
    "fn endgame(view:&GameState)->bool{view.turn>275}",
    "impl Default for YamoOpeningPolicy",
    "impl Default for YamoBot",
    "impl Default for SecureOrchardBot",
    "pub fn tuned_carry_regeneration_unblocked()",
    "pub fn tuned_carry_regeneration_transit()",
    "pub fn regeneration_unblocked_with_policy(",
    "pub fn regeneration_unblocked_with_routing(",
    "pub fn regeneration_unblocked_with_strategy(",
    "#[derive(Clone,Copy,Debug,Default,Eq,PartialEq)]pub struct TaskMarketOrchardTelemetry",
    "#[derive(Clone,Copy,Debug,Default,Eq,PartialEq)]pub struct FreshHarvestRegenerationTelemetry",
    "#[derive(Clone,Copy,Debug,Default,Eq,PartialEq)]pub struct BananaSeedFactoryTelemetry",
    "pub fn task_market()",
    "pub fn fresh_harvest_regeneration()",
    "pub fn banana_seed_factory_source_separated()",
    "pub fn banana_seed_factory_activation_selector()",
    "pub fn banana_seed_factory_dual_value_e6()",
    "pub fn banana_seed_factory_trained_dual_value_e6()",
    "pub fn banana_seed_factory_worker_three_bridge()",
    "pub fn fresh_harvest_regeneration_telemetry(",
    "pub fn banana_seed_factory_telemetry(&self)",
    "pub fn task_market_telemetry(&self)",
    "pub fn opponent_crop_telemetry(&self)",
    "fn banana_factory_worker_three_stats()",
    "fn banana_factory_worker_three_cost(",
    "fn banana_factory_worker_three_bootstrap_complete(",
    "fn banana_factory_worker_three_funding_active(",
    "fn reconcile_banana_factory_worker_three_bridge(",
    "fn banana_factory_worker_three_bank_command(",
    "fn banana_factory_worker_three_fruit_target(",
    "fn banana_factory_worker_three_starter_command(",
    "fn banana_factory_worker_three_mining_command(",
    "fn banana_factory_worker_three_can_train(",
)

INACTIVE_FRAGMENTS = (
    "task_market_enabled:bool,",
    "task_market_seed_repaid:bool,",
    "task_market_activation_turn:Option<i32>,",
    "task_market_seed_repaid_turn:Option<i32>,",
    "task_market_turns:usize,",
    "task_market_forced_setup_actions:usize,",
    "banana_factory_source_separated:bool,",
    "banana_factory_selector_enabled:bool,",
    "banana_factory_selector_decided:bool,",
    "banana_factory_selector_selected:bool,",
    "banana_factory_trained_dual_value_e6:bool,",
    "banana_factory_worker_three_bridge:bool,",
    "banana_factory_worker_three_bridge_funding_turns:usize,",
    "banana_factory_worker_three_bridge_pending_harvest:Option<(i32,i32,usize,i32)>,",
    "banana_factory_worker_three_bridge_fruit_harvest_selections:[usize;3],",
    "banana_factory_worker_three_bridge_fruit_harvest_successes:[usize;3],",
    "banana_factory_worker_three_bridge_pending_mine:Option<(i32,i32,i32)>,",
    "banana_factory_worker_three_bridge_iron_mine_selections:usize,",
    "banana_factory_worker_three_bridge_iron_mine_successes:usize,",
    "banana_factory_worker_three_bridge_pending_train:Option<(i32,usize)>,",
    "banana_factory_worker_three_bridge_train_attempts:usize,",
    "banana_factory_worker_three_bridge_train_successes:usize,",
    "banana_factory_worker_three_bridge_trained_turn:Option<i32>,",
    "banana_factory_worker_three_bridge_forbidden_commands:usize,",
    "banana_factory_worker_three_bridge_post_training_commands:usize,",
    "task_market_enabled:false,",
    "task_market_seed_repaid:false,",
    "task_market_activation_turn:None,",
    "task_market_seed_repaid_turn:None,",
    "task_market_turns:0,",
    "task_market_forced_setup_actions:0,",
    "banana_factory_source_separated:false,",
    "banana_factory_selector_enabled:false,",
    "banana_factory_selector_decided:false,",
    "banana_factory_selector_selected:false,",
    "banana_factory_trained_dual_value_e6:false,",
    "banana_factory_worker_three_bridge:false,",
    "banana_factory_worker_three_bridge_funding_turns:0,",
    "banana_factory_worker_three_bridge_pending_harvest:None,",
    "banana_factory_worker_three_bridge_fruit_harvest_selections:[0;3],",
    "banana_factory_worker_three_bridge_fruit_harvest_successes:[0;3],",
    "banana_factory_worker_three_bridge_pending_mine:None,",
    "banana_factory_worker_three_bridge_iron_mine_selections:0,",
    "banana_factory_worker_three_bridge_iron_mine_successes:0,",
    "banana_factory_worker_three_bridge_pending_train:None,",
    "banana_factory_worker_three_bridge_train_attempts:0,",
    "banana_factory_worker_three_bridge_train_successes:0,",
    "banana_factory_worker_three_bridge_trained_turn:None,",
    "banana_factory_worker_three_bridge_forbidden_commands:0,",
    "banana_factory_worker_three_bridge_post_training_commands:0,",
)


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
        (
            "pub use types::{Cell,GameState,Plant,PlantKind,Stats,Unit};",
            "pub use types::GameState;",
        ),
        ("Stats,Stock,Unit,", "Stats,Unit,"),
        (",PLUM,WOOD,};", ",PLUM,};"),
    ):
        result = replace_once(result, before, after)

    for marker in DEAD_ITEMS:
        result = _remove_item(result, marker)
    for fragment in DEAD_FRAGMENTS:
        result = replace_once(result, fragment, "")

    result = _remove_control_block(result, TEST_MODULE)
    for marker in INACTIVE_ITEMS:
        result = _remove_item(result, marker)
    for fragment in INACTIVE_FRAGMENTS:
        result = replace_once(result, fragment, "")

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
        "fn banana_factory_wood_command(",
        "fn banana_factory_wood_command(&mut self,view:&GameState,unit:&Unit)->String{"
        "let mut candidates=if unit.total_carried()>0{YamoBot::bank_candidates(view,unit)}"
        "else{YamoBot::yamo_chop_candidates(view,unit,self.inner.type_to_cut,"
        "self.banana_factory_reserve,self.inner.opponent_eta_penalty,)};"
        "self.inner.apply_opponent_crop_priority(view,unit,&mut candidates);"
        "let selected=candidates.into_iter().max_by(|left,right|"
        "left.score.total_cmp(&right.score));if selected.as_ref().is_some_and(|candidate|{"
        "matches!(candidate.target,Target::Tree(cell)if self.inner.opponent_crops.contains(&cell))"
        "}){self.banana_factory_trained_opponent_crop_selections+=1;}selected.map(|candidate|"
        "candidate.command).unwrap_or_else(||\"WAIT\".to_string())}",
    )
    result = _replace_item(
        result,
        "fn banana_factory_commands(",
        "fn banana_factory_commands(&mut self,view:&GameState)->Vec<String>{"
        "self.reconcile_banana_factory(view);if!self.banana_factory_active{"
        "self.banana_factory_active=true;self.banana_factory_activation_turn=Some(view.turn);}"
        "self.inner.external_idle_unit=None;self.inner.external_orchard_task=None;"
        "self.inner.external_protected_tree=self.banana_factory_reserve;"
        "self.inner.regeneration_commitments.clear();let mut commands=self.inner.commands(view);"
        "let mut unit_ids:Vec<_>=view.units.iter().filter(|unit|unit.player==0)"
        ".map(|unit|unit.id).collect();unit_ids.sort_unstable();let Some(starter_id)="
        "self.starter_id else{return commands;};if let Some(starter)=view.unit(starter_id){"
        "if let Some(command)=self.banana_factory_starter_command(view,starter){"
        "Self::replace_action(&mut commands,&unit_ids,starter_id,command);}}for unit in "
        "view.units.iter().filter(|unit|unit.player==0&&unit.id!=starter_id){let Some(slot)="
        "Self::unit_action_slot(&commands,&unit_ids,unit.id)else{continue;};let verb="
        "commands[slot].split_whitespace().next().unwrap_or(\"WAIT\");if matches!(verb,"
        "\"PICK\"|\"PLANT\"|\"HARVEST\"|\"MINE\"){commands[slot]="
        "self.banana_factory_wood_command(view,unit);self.banana_factory_trained_role_rewrites+=1;}}"
        "self.inner.regeneration_commitments.clear();self.inner.own_plant_attempts.clear();"
        "let priority=BTreeSet::from([starter_id]);let forbidden=self.banana_factory_reserve"
        ".map(|cell|BTreeSet::from([cell])).unwrap_or_default();"
        "MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(view,&mut commands,"
        "&priority,&forbidden,);for unit in view.units.iter().filter(|unit|unit.player==0&&"
        "unit.id!=starter_id){if let Some(slot)=Self::unit_action_slot(&commands,&unit_ids,unit.id){"
        "let verb=commands[slot].split_whitespace().next().unwrap_or(\"WAIT\");if matches!(verb,"
        "\"PICK\"|\"PLANT\"|\"HARVEST\"|\"MINE\"){"
        "self.banana_factory_trained_forbidden_commands+=1;}}}"
        "self.inner.remember_own_plant_attempts(view,&commands);commands}",
    )

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
        "self.starter_id).flatten();"
        "self.inner.external_protected_tree=reserve_orchard.then(||self.geometry.as_ref()"
        ".map(|geometry|geometry.mother)).flatten();self.inner.external_orchard_task=None;",
    )
    result = _replace_between(
        result,
        "let repays_seed=self.task_market_enabled",
        "Self::replace_action(&mut commands,&unit_ids,starter_id,forced);",
        "",
    )
    result = _remove_control_block(result, "if self.task_market_enabled")
    result = replace_once(
        result,
        ".filter(|(cell,bank_seed)|{!self.banana_factory_source_separated||**bank_seed||"
        "self.banana_factory_reserve==Some(**cell)})",
        "",
    )

    size = len(result.encode())
    if size >= 100_000:
        raise ValueError(f"slim candidate remains over Arena limit: {size} bytes")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
