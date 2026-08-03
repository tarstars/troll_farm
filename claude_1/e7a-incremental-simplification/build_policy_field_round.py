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
