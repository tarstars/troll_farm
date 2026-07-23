#!/usr/bin/env python3
"""Remove compiler-proven dead items from the recovered live Rust artifact.

The input is the frozen, aggressively compacted standalone source.  Transformations are
deliberately name-based and fail unless every expected site is unique, so an upstream source
change cannot silently delete a different item.  The generated source still needs standalone
compilation and command-stream equality gates before it is considered usable.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


DEAD_ITEMS = (
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]struct BankCommitment",
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]struct BankConflictProbe",
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]struct BankActivation",
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]struct PartialTreeConflictProbe",
    "pub const STARTER_GOLD",
    "pub const STARTER_WOOD",
    "pub fn empty(",
    "pub fn unit_mut(",
    "pub fn units_for(",
    "pub const MAX_SIZE",
    "pub const MAX_FRUITS",
    "pub fn grid_rows(",
    "pub fn turn_block(",
    "pub const CARRY2_CHOP2",
    "pub const TUNED_CARRY_CHOP2",
    "pub const TUNED_CARRY_MOVEMENT",
    "pub fn tuned_carry()",
    "pub fn carry2_chop2()",
    "pub fn tuned_carry_regeneration()",
    "pub fn tuned_carry_regeneration_transit_idle_harvest_clock_only()",
    "pub fn tuned_carry_regeneration_transit_idle_harvest_partial_tree_coordination()",
    "pub fn tuned_carry_regeneration_transit_idle_harvest_bank_router()",
    "pub fn tuned_carry_regeneration_transit_idle_harvest_confirmed_bank_router()",
    "pub fn tuned_carry_regeneration_chop2()",
    "pub fn tuned_carry_regeneration_scarce()",
    "pub fn tuned_carry_regeneration_committed()",
    "pub fn planned_second_troll(",
    "pub fn idle_strict()",
    "pub fn clock_only()",
    "pub fn coverage_only()",
    "pub fn work_conserving()",
    "pub fn fast_worker()",
    "pub fn fast_worker_strict()",
)


DEAD_FRAGMENTS = (
    "bank_router:bool,",
    "bank_router_confirmed:bool,",
    "partial_tree_coordination:bool,",
    "bank_commitments:BTreeMap<i32,BankCommitment>,",
    "bank_conflict_probes:BTreeMap<i32,BankConflictProbe>,",
    "partial_tree_conflict_probes:BTreeMap<i32,PartialTreeConflictProbe>,",
    "bank_router:false,",
    "bank_router_confirmed:false,",
    "partial_tree_coordination:false,",
    "bank_commitments:BTreeMap::new(),",
    "bank_conflict_probes:BTreeMap::new(),",
    "partial_tree_conflict_probes:BTreeMap::new(),",
)


SPECIALIZED_DEAD_ITEMS = (
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
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]enum ScarceIntent",
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]struct ScarcePlan",
    "pub fn tuned_carry_regeneration_unblocked()",
    "pub fn tuned_carry_regeneration_transit()",
    "pub fn regeneration_unblocked_with_policy(",
    "pub fn regeneration_unblocked_with_routing(",
    "pub fn regeneration_unblocked_with_strategy(",
    "fn scarce_kind_priority(",
    "fn scarce_inventory_kind(",
    "fn scarce_carried_kind(",
    "fn scarce_seed_source(",
    "fn scarce_plant_cell(",
    "fn scarce_tree_exists(",
    "fn reconcile_scarce_plan(",
    "fn scarce_protected_tree(",
    "fn scarce_crop(",
    "fn scarce_planting_farmer(",
    "fn scarce_pick_candidates(",
    "fn scarce_farmer_candidates(",
    "fn reconcile_tree_commitments(",
    "fn tree_targets_by_command(",
    "fn remember_selected_tree_targets(",
)


SPECIALIZED_DEAD_FRAGMENTS = (
    "scarce_farming:bool,",
    "initial_tree_count:Option<usize>,",
    "scarce_plan:Option<ScarcePlan>,",
    "tree_target_bonus:i32,",
    "tree_commitments:BTreeMap<i32,Cell>,",
    "scarce_farming:false,",
    "initial_tree_count:None,",
    "scarce_plan:None,",
    "tree_target_bonus:0,",
    "tree_commitments:BTreeMap::new(),",
    "self.reconcile_scarce_plan(view);",
    "self.reconcile_tree_commitments(view);",
    "&&!self.scarce_farming",
)


def _skip_literal(source: str, index: int) -> int | None:
    """Return the first index after a string/char literal, or None for normal code."""
    if source[index] == 'r':
        cursor = index + 1
        hashes = 0
        while cursor < len(source) and source[cursor] == '#':
            hashes += 1
            cursor += 1
        if cursor < len(source) and source[cursor] == '"':
            marker = '"' + '#' * hashes
            end = source.find(marker, cursor + 1)
            if end < 0:
                raise ValueError("unterminated raw string")
            return end + len(marker)
    if source[index] == '"':
        cursor = index + 1
        while cursor < len(source):
            if source[cursor] == "\\":
                cursor += 2
            elif source[cursor] == '"':
                return cursor + 1
            else:
                cursor += 1
        raise ValueError("unterminated string")
    if source[index] == "'":
        # Lifetimes have no closing quote nearby; char literals do.
        cursor = index + 1
        if cursor < len(source) and source[cursor] == "\\":
            cursor += 2
        else:
            cursor += 1
        if cursor < len(source) and source[cursor] == "'":
            return cursor + 1
    return None


def _matching_brace(source: str, opening: int) -> int:
    depth = 0
    index = opening
    while index < len(source):
        literal_end = _skip_literal(source, index)
        if literal_end is not None:
            index = literal_end
            continue
        if source[index] == '{':
            depth += 1
        elif source[index] == '}':
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise ValueError("unmatched item brace")


def _item_span(source: str, marker: str) -> tuple[int, int]:
    if source.count(marker) != 1:
        raise ValueError(f"expected one item marker {marker!r}, found {source.count(marker)}")
    start = source.index(marker)
    if (
        marker.startswith("pub fn")
        or marker.startswith("fn ")
        or marker.startswith("impl ")
        or "struct " in marker
        or "enum " in marker
    ):
        opening = source.index('{', start)
        end = _matching_brace(source, opening) + 1
    else:
        cursor = start
        depth = 0
        while cursor < len(source):
            literal_end = _skip_literal(source, cursor)
            if literal_end is not None:
                cursor = literal_end
                continue
            char = source[cursor]
            if char in "({[":
                depth += 1
            elif char in ")} ]".replace(" ", ""):
                depth -= 1
            elif char == ';' and depth == 0:
                end = cursor + 1
                break
            cursor += 1
        else:
            raise ValueError(f"unterminated item {marker!r}")
    return start, end


def _remove_item(source: str, marker: str) -> str:
    start, end = _item_span(source, marker)
    return source[:start] + source[end:]


def _replace_item(source: str, marker: str, replacement: str) -> str:
    start, end = _item_span(source, marker)
    return source[:start] + replacement + source[end:]


def _remove_control_block(source: str, marker: str) -> str:
    if source.count(marker) != 1:
        raise ValueError(f"expected one control marker {marker!r}, found {source.count(marker)}")
    start = source.index(marker)
    opening = source.index('{', start + len(marker))
    end = _matching_brace(source, opening) + 1
    return source[:start] + source[end:]


def _replace_between(source: str, start_marker: str, end_marker: str, replacement: str) -> str:
    if source.count(start_marker) != 1:
        raise ValueError(
            f"expected one start marker {start_marker!r}, found {source.count(start_marker)}"
        )
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[:start] + replacement + source[end:]


def slim(source: str) -> str:
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
        if result.count(before) != 1:
            raise ValueError(f"expected one fragment {before!r}, found {result.count(before)}")
        result = result.replace(before, after, 1)
    for marker in DEAD_ITEMS:
        result = _remove_item(result, marker)
    for fragment in DEAD_FRAGMENTS:
        if result.count(fragment) != 1:
            raise ValueError(
                f"expected one dead fragment {fragment!r}, found {result.count(fragment)}"
            )
        result = result.replace(fragment, "", 1)

    # The recovered executable has one concrete policy.  Specialize fixed-off experiment
    # families that the compiler cannot call dead while they remain behind instance fields.
    result = _replace_item(
        result,
        "pub fn tuned_carry_regeneration_transit_idle_harvest()",
        "pub fn tuned_carry_regeneration_transit_idle_harvest()->Self{"
        "let mut bot=Self::with_opening_policy(YamoOpeningPolicy::TUNED_CARRY);"
        'bot.announcement="yamo-carry-regen-transit-idle-harvest-rust";'
        "bot.idle_regeneration=true;bot.persistent_regeneration=true;"
        "bot.door_unblocking=true;bot.partial_bank_transit=true;bot.idle_harvest=true;bot}",
    )
    result = _replace_item(
        result,
        "#[derive(Default)]pub struct MoisanBot",
        "struct MoisanBot;",
    )
    result = _replace_item(
        result,
        "fn carries_committed_fruit(",
        "fn carries_committed_fruit(&self,unit:&Unit)->bool{"
        "self.regeneration_commitments.get(&unit.id)"
        ".is_some_and(|kind|unit.carry[kind.item_index()]>0)}",
    )
    result = _remove_control_block(result, "if self.initial_tree_count.is_none()")
    result = _replace_between(
        result,
        "let scarce_farmer_id=",
        "let mut by_id=",
        "let protected_tree=self.external_protected_tree;",
    )
    result = _replace_between(
        result,
        "let mut candidates=if scarce_farmer_id",
        "if endgame&&self.idle_harvest",
        "let mut candidates=if committed_regeneration{"
        "Self::endgame_candidates(view,unit,self.type_to_cut,self.persistent_regeneration,"
        "protected_tree,self.opponent_eta_penalty,)}else if endgame&&self.persistent_regeneration"
        "&&Self::carried_fruit(unit).is_some(){Self::main_candidates(view,unit,self.type_to_cut,"
        "false,true,None,self.opponent_eta_penalty,)}else if endgame{Self::endgame_candidates("
        "view,unit,self.type_to_cut,self.persistent_regeneration,protected_tree,"
        "self.opponent_eta_penalty,)}else if early{MoisanBot::early_candidates(view,unit,desired)}"
        "else{Self::main_candidates(view,unit,self.type_to_cut,self.idle_regeneration,"
        "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)};",
    )
    result = _replace_between(
        result,
        "let tree_targets=",
        "out.extend(selected);",
        "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
        "self.remember_selected_regeneration(&selected);",
    )
    for marker in SPECIALIZED_DEAD_ITEMS:
        result = _remove_item(result, marker)
    for fragment in SPECIALIZED_DEAD_FRAGMENTS:
        if result.count(fragment) != 1:
            raise ValueError(
                f"expected one specialized fragment {fragment!r}, found {result.count(fragment)}"
            )
        result = result.replace(fragment, "", 1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--sidecar",
        action="store_true",
        help="also write OUTPUT.sha256 using the submission-sidecar format",
    )
    args = parser.parse_args()

    original = args.source.read_text()
    result = slim(original)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    digest = hashlib.sha256(result.encode()).hexdigest()
    if args.sidecar:
        args.output.with_name(args.output.name + ".sha256").write_text(
            f"{digest}  {args.output.name}\n"
        )
    print(f"slimmed {len(original)} -> {len(result)} bytes ({len(original) - len(result)} freed)")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
