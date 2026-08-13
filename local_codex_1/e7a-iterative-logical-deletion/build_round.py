#!/usr/bin/env python3
"""Apply one declared E7a logical-deletion round to its exact parent."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


INITIAL_PARENT_SHA256 = "ab0934740171cc7f5f4cd65cdfb8cf879ca92d8236c9505903e4741e0a7c57c2"

OLD_CONSTRUCTOR = (
    "pub fn new()->Self{Self::with_policy("
    "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),8,false,11,1,)}"
    "fn with_policy(inner:YamoBot,minimum_enemy_eta:i32,require_idle_starter:bool,"
    "minimum_enemy_door_distance:i32,minimum_worker_speed:i32,)->Self{Self{inner,"
    "initialized:false,starter_id:None,geometry:None,initial_natural:BTreeMap::new(),"
    "phase:OrchardPhase::Dormant,plant_attempted:false,minimum_enemy_eta,"
    "require_idle_starter,minimum_enemy_door_distance,minimum_worker_speed,}}"
)
NEW_CONSTRUCTOR = (
    "pub fn new()->Self{Self{inner:"
    "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),initialized:false,"
    "starter_id:None,geometry:None,initial_natural:BTreeMap::new(),"
    "phase:OrchardPhase::Dormant,plant_attempted:false,minimum_enemy_eta:8,"
    "require_idle_starter:false,minimum_enemy_door_distance:11,minimum_worker_speed:1,}}"
)

IDLE_HELPER = (
    "fn starter_control_is_idle(commands:&[String],unit_ids:&[i32],starter:&Unit)->bool{"
    "let Some(slot)=Self::unit_action_slot(commands,unit_ids,starter.id)else{return false;};"
    'commands[slot].split_whitespace().next()==Some("WAIT")}'
)
IDLE_BUSY = (
    "let starter_is_busy=self.require_idle_starter&&!Self::starter_control_is_idle("
    "&commands,&unit_ids,starter);"
)
IDLE_CONDITION = "if checkpoint&&has_second&&!starter_is_busy&&self.can_activate"
DIRECT_CONDITION = "if checkpoint&&has_second&&self.can_activate"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def replace_count(source: str, old: str, new: str, expected: int, label: str) -> str:
    count = source.count(old)
    if count != expected:
        raise ValueError(f"{label}: expected {expected} anchors, found {count}")
    return source.replace(old, new)


def remove_braced_block(source: str, anchor: str, label: str) -> str:
    if not anchor.endswith("{"):
        raise ValueError(f"{label}: braced anchor must end with an opening brace")
    if source.count(anchor) != 1:
        raise ValueError(f"{label}: expected one braced anchor, found {source.count(anchor)}")
    start = source.index(anchor)
    opening = start + len(anchor) - 1
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[:start] + source[index + 1 :]
    raise ValueError(f"{label}: unterminated braced block")


def round_one(source: str) -> tuple[str, str]:
    candidate = replace_once(
        source, OLD_CONSTRUCTOR, NEW_CONSTRUCTOR, "single-use policy constructor"
    )
    return candidate, (
        "inline the sole private with_policy call with the same exact field values, "
        "deleting unused runtime configurability"
    )


def round_two(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate, "require_idle_starter:bool,", "", "idle policy field"
    )
    candidate = replace_once(
        candidate, "require_idle_starter:false,", "", "fixed false initializer"
    )
    candidate = replace_once(candidate, IDLE_HELPER, "", "idle helper")
    candidate = replace_once(candidate, IDLE_BUSY, "", "short-circuited busy test")
    candidate = replace_once(
        candidate, IDLE_CONDITION, DIRECT_CONDITION, "always-true activation conjunct"
    )
    return candidate, (
        "delete the require-idle-starter field, helper and activation gate after round 1 "
        "proves the only executable constructor fixes the policy to false"
    )


def round_three(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate,
        "struct OrchardGeometry{mother:Cell,enemy_door_distance:i32,",
        "struct OrchardGeometry{mother:Cell,",
        "stored geometry enemy distance",
    )
    candidate = replace_once(
        candidate,
        "minimum_enemy_door_distance:i32,",
        "",
        "duplicate threshold field",
    )
    candidate = replace_once(
        candidate,
        "minimum_enemy_door_distance:11,",
        "",
        "duplicate threshold initializer",
    )
    candidate = replace_once(
        candidate,
        "enemy_door_distance:enemy_distance.get(&mother).copied().unwrap_or(10_000),",
        "",
        "duplicate selected-distance initializer",
    )
    candidate = replace_once(
        candidate,
        "&&geometry.enemy_door_distance>=self.minimum_enemy_door_distance",
        "",
        "redundant activation recheck",
    )
    invariant = (
        ".filter(|door|enemy_distance.get(door).copied().unwrap_or(10_000)>=11)"
    )
    if candidate.count(invariant) != 1:
        raise ValueError("round 3 lost the exact initialization admission invariant")
    return candidate, (
        "delete the stored enemy-door distance and its >=11 activation recheck because "
        "initialization selects the same mother only through the preserved >=11 filter"
    )


def round_four(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate, "minimum_enemy_eta:i32,", "", "fixed enemy ETA field"
    )
    candidate = replace_once(
        candidate, "minimum_enemy_eta:8,", "", "fixed enemy ETA initializer"
    )
    candidate = replace_once(
        candidate, ">self.minimum_enemy_eta", ">8", "fixed enemy ETA comparison"
    )
    return candidate, (
        "inline the sole executable constructor's fixed enemy ETA threshold 8 and delete "
        "the field and initializer without changing the strict comparison"
    )


def round_five(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate, "minimum_worker_speed:i32,", "", "fixed worker speed field"
    )
    candidate = replace_once(
        candidate, "minimum_worker_speed:1,", "", "fixed worker speed initializer"
    )
    candidate = replace_count(
        candidate,
        "self.minimum_worker_speed",
        "1",
        2,
        "fixed worker speed helper arguments",
    )
    return candidate, (
        "inline the sole executable constructor's fixed minimum worker speed 1 at both "
        "helper calls and delete the field and initializer"
    )


def round_six(source: str) -> tuple[str, str]:
    candidate = source
    for old, label in [
        ("idle_harvest:bool,", "fixed-on idle harvest field"),
        ("idle_harvest_clock_only:bool,", "fixed-off idle clock field"),
        ("idle_harvest:false,", "base idle harvest initializer"),
        ("idle_harvest_clock_only:false,", "base idle clock initializer"),
        ("bot.idle_harvest=true;", "sole factory idle harvest enable"),
    ]:
        candidate = replace_once(candidate, old, "", label)
    candidate = replace_once(
        candidate,
        "if endgame&&self.idle_harvest&&(!self.idle_harvest_clock_only||view.turn>250)"
        "&&candidates.iter().all",
        "if endgame&&candidates.iter().all",
        "constant idle harvest condition",
    )
    if candidate.count("tuned_carry_regeneration_transit_idle_harvest") != 2:
        raise ValueError("round 6 lost the sole executable tuned factory invariant")
    return candidate, (
        "delete the fixed-on idle-harvest and fixed-off clock-only policy switches while "
        "preserving their simplified endgame/all-WAIT activation condition"
    )


def round_seven(source: str) -> tuple[str, str]:
    candidate = source
    for old, label in [
        ("door_unblocking:bool,", "door-unblocking field"),
        ("door_unblocking:false,", "base door-unblocking initializer"),
        ("bot.door_unblocking=true;", "sole factory door-unblocking enable"),
    ]:
        candidate = replace_once(candidate, old, "", label)
    candidate = replace_once(
        candidate,
        "if self.door_unblocking{self.force_unique_door_clear(view,&mut by_id);}",
        "self.force_unique_door_clear(view,&mut by_id);",
        "fixed-on door-unblocking gate",
    )
    return candidate, (
        "delete the fixed-on door-unblocking switch and preserve the formerly guarded "
        "unblocking call unconditionally"
    )


def round_eight(source: str) -> tuple[str, str]:
    candidate = source
    for old, label in [
        ("partial_bank_transit:bool,", "partial-bank-transit field"),
        ("partial_bank_transit:false,", "base partial-bank initializer"),
        ("bot.partial_bank_transit=true;", "sole factory partial-bank enable"),
    ]:
        candidate = replace_once(candidate, old, "", label)
    candidate = replace_once(
        candidate,
        "self.partial_bank_transit&&candidates.get(&unit.id)",
        "candidates.get(&unit.id)",
        "fixed-on partial-bank predicate",
    )
    return candidate, (
        "delete the fixed-on partial-load bank-transit switch and preserve the formerly "
        "guarded candidate predicate"
    )


def round_nine(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate,
        "opening_policy:YamoOpeningPolicy,idle_regeneration:bool,",
        "opening_policy:YamoOpeningPolicy,",
        "ordinary idle-regeneration field",
    )
    candidate = replace_once(
        candidate,
        "idle_regeneration:false,",
        "",
        "base idle-regeneration initializer",
    )
    candidate = replace_once(
        candidate,
        "bot.idle_regeneration=true;",
        "",
        "sole factory idle-regeneration enable",
    )
    candidate = replace_once(
        candidate,
        "self.idle_regeneration,self.persistent_regeneration",
        "true,self.persistent_regeneration",
        "ordinary idle-regeneration call",
    )
    return candidate, (
        "delete the fixed-on ordinary idle-regeneration field and pass true at its one "
        "ordinary call while preserving the special endgame false argument"
    )


def round_ten(source: str) -> tuple[str, str]:
    candidate = source
    for old, label in [
        ("persistent_regeneration:bool,", "persistent-regeneration field"),
        ("persistent_regeneration:false,", "base persistent initializer"),
        ("bot.persistent_regeneration=true;", "sole factory persistent enable"),
        (
            "if!self.persistent_regeneration{self.regeneration_commitments.clear();return;}",
            "disabled reconciliation mode",
        ),
        ("if!self.persistent_regeneration{return;}", "disabled remember mode"),
    ]:
        candidate = replace_once(candidate, old, "", label)
    candidate = replace_once(
        candidate,
        "else if endgame&&self.persistent_regeneration&&Self::carried_fruit",
        "else if endgame&&Self::carried_fruit",
        "fixed-on endgame persistent condition",
    )
    candidate = replace_once(
        candidate,
        "if self.persistent_regeneration&&train_now",
        "if train_now",
        "fixed-on training reserve condition",
    )
    candidate = replace_count(
        candidate,
        "self.persistent_regeneration",
        "true",
        3,
        "fixed-on persistent helper arguments",
    )
    return candidate, (
        "delete the disabled non-persistent regeneration mode and preserve all enabled "
        "branches and helper arguments as constant true"
    )


def round_eleven(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate,
        "regeneration_commitments:BTreeMap<i32,PlantKind>,opponent_eta_penalty:i32,"
        "external_idle_unit:Option<i32>,",
        "regeneration_commitments:BTreeMap<i32,PlantKind>,external_idle_unit:Option<i32>,",
        "zero opponent penalty field",
    )
    candidate = replace_once(
        candidate,
        "opponent_eta_penalty:0,",
        "",
        "zero opponent penalty initializer",
    )

    dead_start = "if opponent_eta_penalty<=0{return candidates;}"
    dead_end = "candidate.score-=opponent_eta_penalty as f64*risk;}candidates"
    if candidate.count(dead_start) != 1 or candidate.count(dead_end) != 1:
        raise ValueError("round 11 opponent-risk block anchors are not unique")
    start = candidate.index(dead_start)
    end = candidate.index(dead_end, start) + len(dead_end)
    if "fn yamo_chop_candidates" not in candidate[max(0, start - 500) : start]:
        raise ValueError("round 11 risk block is outside yamo_chop_candidates")
    candidate = candidate[:start] + "candidates" + candidate[end:]

    candidate = replace_count(
        candidate,
        "protected_tree:Option<Cell>,opponent_eta_penalty:i32,)->Vec<Candidate>",
        "protected_tree:Option<Cell>,)->Vec<Candidate>",
        3,
        "opponent penalty function parameters",
    )
    candidate = replace_count(
        candidate,
        "protected_tree,opponent_eta_penalty,",
        "protected_tree,",
        3,
        "internal opponent penalty arguments",
    )
    candidate = replace_count(
        candidate,
        "self.opponent_eta_penalty,",
        "",
        4,
        "factory-fixed zero opponent penalty arguments",
    )
    if "opponent_eta_penalty" in candidate:
        raise ValueError("round 11 left opponent penalty plumbing behind")
    return candidate, (
        "delete the opponent-arrival risk calculation after the sole executable factory "
        "fixes its penalty to zero, preserving protected-tree filtering and all candidates"
    )


def round_twelve(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate,
        "pub require_preferred:bool,",
        "",
        "preferred-only policy field",
    )
    candidate = replace_once(
        candidate,
        "require_preferred:false,",
        "",
        "fixed false preferred-only policy",
    )
    candidate = remove_braced_block(
        candidate,
        "if policy.require_preferred{",
        "initial preferred-only opening branch",
    )
    candidate = remove_braced_block(
        candidate,
        "if self.opening_policy.require_preferred{",
        "deadline preferred-only fallback branch",
    )
    if "require_preferred" in candidate:
        raise ValueError("round 12 left preferred-only mode plumbing behind")
    return candidate, (
        "delete both unreachable preferred-only opening branches because TUNED_CARRY "
        "fixes require_preferred false, preserving ordinary selection and fallback"
    )


OLD_MOVEMENT_TIE_KEY = (
    "fn opening_key(objective:&OpeningObjective,policy:YamoOpeningPolicy,)->"
    "(i32,i32,i32,i32,i32){let stats=objective.stats;let total=stats.movement_speed+"
    "stats.carry_capacity+stats.chop_power;if policy.prefer_movement_ties{(total,"
    "-objective.estimated_eta,stats.movement_speed,stats.carry_capacity,stats.chop_power,)}"
    "else{(total,-objective.estimated_eta,stats.chop_power,stats.carry_capacity,"
    "stats.movement_speed,)}}"
)
CHOP_FIRST_KEY = (
    "fn opening_key(objective:&OpeningObjective)->"
    "(i32,i32,i32,i32,i32){let stats=objective.stats;let total=stats.movement_speed+"
    "stats.carry_capacity+stats.chop_power;(total,-objective.estimated_eta,stats.chop_power,"
    "stats.carry_capacity,stats.movement_speed,)}"
)


def round_thirteen(source: str) -> tuple[str, str]:
    candidate = source
    candidate = replace_once(
        candidate,
        "pub prefer_movement_ties:bool,",
        "",
        "movement-first tie policy field",
    )
    candidate = replace_once(
        candidate,
        "prefer_movement_ties:false,",
        "",
        "fixed false movement-first tie policy",
    )
    candidate = replace_once(
        candidate,
        OLD_MOVEMENT_TIE_KEY,
        CHOP_FIRST_KEY,
        "movement-first opening key branch",
    )
    candidate = replace_count(
        candidate,
        "Self::opening_key(objective,policy)",
        "Self::opening_key(objective)",
        3,
        "deleted opening-key policy arguments",
    )
    if "prefer_movement_ties" in candidate:
        raise ValueError("round 13 left movement tie mode plumbing behind")
    return candidate, (
        "delete the disabled movement-first opening tie mode and preserve the exact "
        "chop-first tuple from its fixed false branch"
    )


ROUNDS = {
    1: round_one,
    2: round_two,
    3: round_three,
    4: round_four,
    5: round_five,
    6: round_six,
    7: round_seven,
    8: round_eight,
    9: round_nine,
    10: round_ten,
    11: round_eleven,
    12: round_twelve,
    13: round_thirteen,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", type=int, choices=sorted(ROUNDS), required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--expected-parent-sha256", required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    parent = args.parent.read_bytes()
    parent_sha256 = digest(parent)
    if parent_sha256 != args.expected_parent_sha256:
        parser.error("parent SHA-256 does not match the frozen invocation")
    if args.round == 1 and parent_sha256 != INITIAL_PARENT_SHA256:
        parser.error("round 1 does not start from the untouched-qualified parent")
    if args.candidate.exists() or args.manifest.exists():
        parser.error("refusing to overwrite an existing round artifact")

    candidate_text, logical_change = ROUNDS[args.round](parent.decode())
    candidate = candidate_text.encode()
    if len(candidate) >= len(parent):
        raise ValueError("declared deletion did not make the source smaller")

    manifest = {
        "schema": "troll-farm-e7a-iterative-logical-deletion-round-v1",
        "round": args.round,
        "parent": {
            "path": str(args.parent),
            "bytes": len(parent),
            "sha256": parent_sha256,
        },
        "candidate": {
            "path": str(args.candidate),
            "bytes": len(candidate),
            "sha256": digest(candidate),
            "removed_this_round": len(parent) - len(candidate),
            "removed_from_initial_62278": 62_278 - len(candidate),
        },
        "logical_change": logical_change,
        "identifier_renaming": False,
        "minification": False,
        "compression": False,
        "formatting_reduction": False,
        "gates_pending": [
            "byte-exact rebuild",
            "optimized compile and empty input",
            "ten exact semantic fixtures",
            "25-game exact live command parity",
        ],
    }
    args.candidate.parent.mkdir(parents=True, exist_ok=True)
    args.candidate.write_bytes(candidate)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["candidate"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
