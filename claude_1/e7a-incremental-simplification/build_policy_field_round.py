#!/usr/bin/env python3
"""Apply one declared E7a policy-field inlining round (16-21) to its exact parent.

Each round inlines one sole-value ``YamoOpeningPolicy`` field at its reads and
deletes the field declaration and ``TUNED_CARRY`` initializer, per the published
inventory item 2 and the per-round contracts
``claude_1/e7a-incremental-simplification/r<N>-contract-2026-08-03.md``.
Comparison operators and clamp expressions are preserved untouched; constant
folding is out of scope for these rounds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Each op: (old, new, expected_count). Residue: substrings that must not survive.
ROUNDS = {
    16: {
        "field": "hard_train_turn",
        "ops": [
            ("pub hard_train_turn:i32,", "", 1),
            ("hard_train_turn:35,", "", 1),
            ("policy.hard_train_turn.saturating_sub", "35i32.saturating_sub", 1),
            ("view.turn<self.opening_policy.hard_train_turn", "view.turn<35", 1),
        ],
        "residue": ["hard_train_turn"],
        "logical_change": (
            "inline the sole-value hard_train_turn 35 at its deadline and abandonment "
            "reads and delete the field and TUNED_CARRY initializer"
        ),
    },
    17: {
        "field": "max_extra_eta",
        "ops": [
            ("pub max_extra_eta:i32,", "", 1),
            ("max_extra_eta:15,", "", 1),
            ("if policy.max_extra_eta<=0||", "if 15<=0||", 1),
            (".saturating_add(policy.max_extra_eta)", ".saturating_add(15)", 1),
        ],
        "residue": ["max_extra_eta"],
        "logical_change": (
            "inline the sole-value max_extra_eta 15 at its guard and allowance reads "
            "and delete the field and TUNED_CARRY initializer; the now-constant "
            "15<=0 disjunct is preserved verbatim for a separately declared round"
        ),
    },
    18: {
        "field": "preferred_min_carry",
        "ops": [
            ("pub preferred_min_carry:i32,", "", 1),
            ("preferred_min_carry:2,", "", 1),
            ("policy.preferred_min_carry.clamp", "2i32.clamp", 1),
        ],
        "residue": ["policy.preferred_min_carry"],
        "logical_change": (
            "inline the sole-value preferred_min_carry 2 at its single clamped read "
            "and delete the field and TUNED_CARRY initializer; the local binding of "
            "the same name is untouched"
        ),
    },
    19: {
        "field": "preferred_min_chop",
        "ops": [
            ("pub preferred_min_chop:i32,", "", 1),
            ("preferred_min_chop:1,", "", 1),
            ("policy.preferred_min_chop.clamp", "1i32.clamp", 1),
        ],
        "residue": ["policy.preferred_min_chop"],
        "logical_change": (
            "inline the sole-value preferred_min_chop 1 at its single clamped read "
            "and delete the field and TUNED_CARRY initializer; the local binding of "
            "the same name is untouched"
        ),
    },
    20: {
        "field": "max_carry_capacity",
        "ops": [
            ("pub max_carry_capacity:i32,", "", 1),
            ("max_carry_capacity:3,", "", 1),
            (
                "opening_options(view,policy.max_carry_capacity,policy.max_chop_power)",
                "opening_options(view,3,policy.max_chop_power)",
                2,
            ),
            (
                "2i32.clamp(1,policy.max_carry_capacity.clamp(1,3))",
                "2i32.clamp(1,3i32.clamp(1,3))",
                1,
            ),
        ],
        "residue": ["policy.max_carry_capacity"],
        "logical_change": (
            "inline the sole-value max_carry_capacity 3 at its two opening_options "
            "arguments and one clamp bound and delete the field and TUNED_CARRY "
            "initializer; the opening_options parameter and locals are untouched"
        ),
    },
    21: {
        "field": "max_chop_power",
        "ops": [
            ("pub max_chop_power:i32,", "", 1),
            ("max_chop_power:3,", "", 1),
            (
                "opening_options(view,3,policy.max_chop_power)",
                "opening_options(view,3,3)",
                2,
            ),
            (
                "1i32.clamp(1,policy.max_chop_power.clamp(1,3))",
                "1i32.clamp(1,3i32.clamp(1,3))",
                1,
            ),
        ],
        "residue": ["policy.max_chop_power"],
        "logical_change": (
            "inline the sole-value max_chop_power 3 at its two opening_options "
            "arguments and one clamp bound and delete the field and TUNED_CARRY "
            "initializer; the opening_options parameter and locals are untouched"
        ),
    },
    22: {
        "field": "YamoOpeningPolicy record",
        "ops": [
            (
                "#[derive(Clone,Copy,Debug,Eq,PartialEq)]pub struct YamoOpeningPolicy{}"
                "impl YamoOpeningPolicy{pub const TUNED_CARRY:Self=Self{};}",
                "",
                1,
            ),
            ("opening_policy:YamoOpeningPolicy,", "", 1),
            ("opening_policy:YamoOpeningPolicy::TUNED_CARRY,", "", 1),
            (
                "fn choose_second_troll(view:&GameState,policy:YamoOpeningPolicy)->",
                "fn choose_second_troll(view:&GameState)->",
                1,
            ),
            (
                "fn strongest_affordable(view:&GameState,policy:YamoOpeningPolicy,)->",
                "fn strongest_affordable(view:&GameState)->",
                1,
            ),
            (
                "Self::choose_second_troll(view,self.opening_policy)",
                "Self::choose_second_troll(view)",
                1,
            ),
            (
                "Self::strongest_affordable(view,self.opening_policy)",
                "Self::strongest_affordable(view)",
                1,
            ),
        ],
        "residue": ["YamoOpeningPolicy", "opening_policy", "policy"],
        "logical_change": (
            "delete the empty zero-sized YamoOpeningPolicy record, its TUNED_CARRY "
            "const, the opening_policy field and initializer, and the two never-read "
            "policy parameters with their call-site arguments"
        ),
    },
    23: {
        "field": "constant-false 15<=0 disjunct",
        "ops": [
            ("if 15<=0||(", "if(", 1),
        ],
        "residue": ["15<=0"],
        "logical_change": (
            "fold the constant-false 15<=0 disjunct out of the opening-upgrade "
            "guard, preserving the surviving conjunction verbatim"
        ),
    },
    24: {
        "field": "unused Debug derives",
        "ops": [
            (",Debug,", ",", 9),
            (",Debug)", ")", 3),
        ],
        "residue": ["Debug"],
        "logical_change": (
            "delete all twelve unused Debug derive tokens ({:?} occurs nowhere), "
            "removing only the trait token and its adjacent comma per the "
            "integrator's classification ruling"
        ),
    },
    25: {
        "field": "unused Hash derive on PlantKind",
        "ops": [
            (",Hash)", ")", 1),
        ],
        "residue": ["Hash"],
        "logical_change": (
            "delete the unused Hash derive on PlantKind (no hash collections "
            "exist; all maps are BTree, which require Ord)"
        ),
    },
    26: {
        "field": "single-valued opening_options parameters",
        "ops": [
            (
                "fn opening_options(view:&GameState,max_carry_capacity:i32,"
                "max_chop_power:i32,)->Vec<OpeningObjective>",
                "fn opening_options(view:&GameState)->Vec<OpeningObjective>",
                1,
            ),
            (
                "let max_carry_capacity=max_carry_capacity.clamp(1,3);",
                "let max_carry_capacity=3i32.clamp(1,3);",
                1,
            ),
            (
                "let max_chop_power=max_chop_power.clamp(1,3);",
                "let max_chop_power=3i32.clamp(1,3);",
                1,
            ),
            ("opening_options(view,3,3)", "opening_options(view)", 2),
        ],
        "residue": ["opening_options(view,"],
        "logical_change": (
            "delete the opening_options parameters whose only surviving call "
            "arguments are literal 3,3 and seed the body's shadowing locals with "
            "the same literals"
        ),
    },
    27: {
        "field": "constant preferred_min_carry binding",
        "ops": [
            ("let preferred_min_carry=2i32.clamp(1,3i32.clamp(1,3));", "", 1),
            (">=preferred_min_carry", ">=2", 2),
        ],
        "residue": ["preferred_min_carry"],
        "logical_change": (
            "delete the constant local binding preferred_min_carry=2 and inline "
            "the literal at both comparison reads"
        ),
    },
    28: {
        "field": "constant preferred_min_chop binding",
        "ops": [
            ("let preferred_min_chop=1i32.clamp(1,3i32.clamp(1,3));", "", 1),
            (">=preferred_min_chop", ">=1", 2),
        ],
        "residue": ["preferred_min_chop"],
        "logical_change": (
            "delete the constant local binding preferred_min_chop=1 and inline "
            "the literal at both comparison reads"
        ),
    },
    29: {
        "field": "constant max_carry_capacity clamp local",
        "ops": [
            ("let max_carry_capacity=3i32.clamp(1,3);", "", 1),
            ("1..=max_carry_capacity", "1..=3", 1),
        ],
        "residue": ["max_carry_capacity"],
        "logical_change": (
            "delete the constant local binding max_carry_capacity=3.clamp(1,3) and "
            "inline literal 3 at its single loop-bound read"
        ),
    },
    30: {
        "field": "constant max_chop_power clamp local",
        "ops": [
            ("let max_chop_power=3i32.clamp(1,3);", "", 1),
            ("1..=max_chop_power", "1..=3", 1),
        ],
        "residue": ["max_chop_power"],
        "logical_change": (
            "delete the constant local binding max_chop_power=3.clamp(1,3) and "
            "inline literal 3 at its single loop-bound read"
        ),
    },
    31: {
        "field": "main_candidates single-valued safe_regeneration parameter",
        "ops": [
            (
                "idle_regeneration:bool,safe_regeneration:bool,protected_tree:Option<Cell>,",
                "idle_regeneration:bool,protected_tree:Option<Cell>,",
                1,
            ),
            (
                "if safe_regeneration&&Self::carried_fruit(unit).is_some(){",
                "if Self::carried_fruit(unit).is_some(){",
                1,
            ),
            ("if safe_regeneration&&carried==0&&", "if carried==0&&", 1),
            (
                "Self::endgame_candidates(view,unit,type_to_cut,safe_regeneration,protected_tree,)",
                "Self::endgame_candidates(view,unit,type_to_cut,true,protected_tree,)",
                1,
            ),
            (
                "Self::main_candidates(view,unit,self.type_to_cut,false,true,None,)",
                "Self::main_candidates(view,unit,self.type_to_cut,false,None,)",
                1,
            ),
            (
                "Self::main_candidates(view,unit,self.type_to_cut,true,true,protected_tree,)",
                "Self::main_candidates(view,unit,self.type_to_cut,true,protected_tree,)",
                1,
            ),
        ],
        "residue": [],
        # endgame_candidates still owns the identifier: its declaration + two body reads
        "expect_counts": {"safe_regeneration": 3},
        "logical_change": (
            "delete the main_candidates safe_regeneration parameter, which round 10 "
            "fixed to literal true at both call sites, folding its two constant-true "
            "conjuncts and passing true at the one passthrough argument"
        ),
    },
    32: {
        "field": "endgame_candidates single-valued safe_regeneration parameter",
        "ops": [
            (
                "type_to_cut:Option<PlantKind>,safe_regeneration:bool,protected_tree:Option<Cell>,",
                "type_to_cut:Option<PlantKind>,protected_tree:Option<Cell>,",
                1,
            ),
            (
                "let can_plant_here=!safe_regeneration||view.plant_at(unit.cell).is_none();",
                "let can_plant_here=view.plant_at(unit.cell).is_none();",
                1,
            ),
            (
                "if safe_regeneration&&view.plant_at(*cell).is_some(){continue;}",
                "if view.plant_at(*cell).is_some(){continue;}",
                1,
            ),
            (
                "Self::endgame_candidates(view,unit,type_to_cut,true,protected_tree,)",
                "Self::endgame_candidates(view,unit,type_to_cut,protected_tree,)",
                1,
            ),
            (
                "Self::endgame_candidates(view,unit,self.type_to_cut,true,protected_tree,)",
                "Self::endgame_candidates(view,unit,self.type_to_cut,protected_tree,)",
                2,
            ),
        ],
        "residue": ["safe_regeneration"],
        "logical_change": (
            "delete the endgame_candidates safe_regeneration parameter, now literal "
            "true at all three call sites after round 31, folding its constant-false "
            "disjunct and constant-true conjunct"
        ),
    },
    33: {
        "field": "worker_can_use_alternate single-valued minimum_speed parameter",
        "ops": [
            ("geometry:&OrchardGeometry,minimum_speed:i32,", "geometry:&OrchardGeometry,", 1),
            ("unit.stats.movement_speed>=minimum_speed", "unit.stats.movement_speed>=1", 1),
            (
                "Self::worker_can_use_alternate(view,starter.id,geometry,1)",
                "Self::worker_can_use_alternate(view,starter.id,geometry)",
                2,
            ),
        ],
        "residue": ["minimum_speed"],
        "logical_change": (
            "delete the worker_can_use_alternate minimum_speed parameter, which "
            "round 5 fixed to literal 1 at both call sites, inlining 1 at its single "
            "body comparison"
        ),
    },
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
    if digest(parent) != args.expected_parent_sha256:
        parser.error("parent SHA-256 does not match the frozen invocation")
    if args.candidate.exists() or args.manifest.exists():
        parser.error("refusing to overwrite an existing round artifact")

    spec = ROUNDS[args.round]
    source = parent.decode()
    for old, new, expected in spec["ops"]:
        count = source.count(old)
        if count != expected:
            raise ValueError(
                f"round {args.round} anchor {old!r}: expected {expected}, found {count}"
            )
        source = source.replace(old, new)
    for residue in spec["residue"]:
        if residue in source:
            raise ValueError(f"round {args.round} left {residue!r} behind")
    for token, expected in spec.get("expect_counts", {}).items():
        count = source.count(token)
        if count != expected:
            raise ValueError(
                f"round {args.round}: expected {expected} surviving {token!r}, found {count}"
            )

    candidate = source.encode()
    if len(candidate) >= len(parent):
        raise ValueError("declared deletion did not make the source smaller")

    manifest = {
        "schema": "troll-farm-e7a-iterative-logical-deletion-round-v1",
        "round": args.round,
        "parent": {
            "path": str(args.parent),
            "bytes": len(parent),
            "sha256": args.expected_parent_sha256,
        },
        "candidate": {
            "path": str(args.candidate),
            "bytes": len(candidate),
            "sha256": digest(candidate),
            "removed_this_round": len(parent) - len(candidate),
            "removed_from_initial_62278": 62_278 - len(candidate),
        },
        "logical_change": spec["logical_change"],
        "identifier_renaming": False,
        "minification": False,
        "compression": False,
        "formatting_reduction": False,
        "gates_pending": [
            "byte-exact rebuild",
            "optimized compile and empty input",
            "ten exact semantic fixtures",
            "25-game exact offline live command parity",
        ],
    }
    args.candidate.parent.mkdir(parents=True, exist_ok=True)
    args.candidate.write_bytes(candidate)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["candidate"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
