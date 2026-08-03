#!/usr/bin/env python3
"""Apply the declared E7a round-14 logical deletion to its exact parent.

Round 14: delete the single-use ``with_opening_policy`` constructor and the dead
default announcement it carries, inlining the struct literal into the sole
executable factory. Contract:
``claude_1/e7a-incremental-simplification/r14-contract-2026-08-03.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PARENT_SHA256 = "6b9fdc99c960b4ddc969729d9452b1e5b7b252b06f8314a8567e969e27f5ba34"

OLD_BLOCK = (
    'pub fn with_opening_policy(opening_policy:YamoOpeningPolicy)->Self{Self{'
    'announced:false,announcement:"yamo-waypoint-rust",type_to_cut:None,'
    'desired_second:None,opening_initialized:false,opening_abandoned:false,'
    'opening_policy,regeneration_commitments:BTreeMap::new(),'
    'external_idle_unit:None,external_protected_tree:None,}}'
    'pub fn tuned_carry_regeneration_transit_idle_harvest()->Self{'
    'let mut bot=Self::with_opening_policy(YamoOpeningPolicy::TUNED_CARRY);'
    'bot.announcement="yamo-carry-regen-transit-idle-harvest-rust";bot}'
)
NEW_BLOCK = (
    'pub fn tuned_carry_regeneration_transit_idle_harvest()->Self{Self{'
    'announced:false,announcement:"yamo-carry-regen-transit-idle-harvest-rust",'
    'type_to_cut:None,desired_second:None,opening_initialized:false,'
    'opening_abandoned:false,opening_policy:YamoOpeningPolicy::TUNED_CARRY,'
    'regeneration_commitments:BTreeMap::new(),external_idle_unit:None,'
    'external_protected_tree:None,}}'
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expect_count(source: str, needle: str, expected: int, label: str) -> None:
    count = source.count(needle)
    if count != expected:
        raise ValueError(f"{label}: expected {expected} occurrences, found {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    parent = args.parent.read_bytes()
    if digest(parent) != PARENT_SHA256:
        parser.error("parent SHA-256 does not match the frozen round-13 candidate")
    if args.candidate.exists() or args.manifest.exists():
        parser.error("refusing to overwrite an existing round artifact")

    source = parent.decode()
    expect_count(source, "with_opening_policy", 2, "single-use constructor anchor")
    expect_count(source, '"yamo-waypoint-rust"', 1, "dead default announcement")
    expect_count(source, "announcement", 4, "announcement plumbing")
    expect_count(source, "Self{announced:", 1, "sole YamoBot struct literal")
    expect_count(source, OLD_BLOCK, 1, "round-14 block")

    candidate_text = source.replace(OLD_BLOCK, NEW_BLOCK, 1)
    expect_count(candidate_text, "with_opening_policy", 0, "constructor removal")
    expect_count(candidate_text, '"yamo-waypoint-rust"', 0, "dead default removal")
    expect_count(candidate_text, "announcement", 3, "surviving announcement plumbing")

    candidate = candidate_text.encode()
    if len(candidate) >= len(parent):
        raise ValueError("declared deletion did not make the source smaller")

    manifest = {
        "schema": "troll-farm-e7a-iterative-logical-deletion-round-v1",
        "round": 14,
        "parent": {
            "path": str(args.parent),
            "bytes": len(parent),
            "sha256": PARENT_SHA256,
        },
        "candidate": {
            "path": str(args.candidate),
            "bytes": len(candidate),
            "sha256": digest(candidate),
            "removed_this_round": len(parent) - len(candidate),
            "removed_from_initial_62278": 62_278 - len(candidate),
        },
        "logical_change": (
            "inline the sole private with_opening_policy call into the executable "
            "factory, deleting the single-use constructor and the dead default "
            "announcement it overwrote before any read"
        ),
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
