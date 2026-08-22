#!/usr/bin/env python3
"""Delete E7a's unreachable selector for rosters above two friendly trolls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
ROSTER_CAP = "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}"
GENERIC_FALLBACK = (
    "let mut used_targets=Vec::new();let mut used_stock=[0;6];"
    "let mut commands=Vec::new();for id in ids{let mut candidates="
    "candidates_by_id[&id].clone();candidates.sort_by(|a,b|b.score.total_cmp"
    "(&a.score));let best=candidates.into_iter().find(|candidate|{used_targets"
    ".iter().all(|target|Self::compatible(candidate.target,*target))&&Self::"
    "picked_item(&candidate.command).map(|item|used_stock[item]<inventory[item])"
    ".unwrap_or(true)}).unwrap_or_else(Self::wait);used_targets.push(best.target);"
    "if let Some(item)=Self::picked_item(&best.command){used_stock[item]+=1;}"
    "commands.push(best.command);}commands"
)
FAIL_SAFE = 'ids.into_iter().map(|_|"WAIT".to_string()).collect()'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(source: str) -> tuple[str, dict]:
    source_bytes = source.encode()
    if sha256(source_bytes) != BASELINE_SHA256:
        raise ValueError("baseline SHA-256 mismatch")
    if source.count(ROSTER_CAP) != 1:
        raise ValueError("expected exactly one two-troll training cap")
    if source.count(GENERIC_FALLBACK) != 1:
        raise ValueError("expected exactly one generic selector fallback")

    candidate = source.replace(GENERIC_FALLBACK, FAIL_SAFE, 1)
    if candidate.count(ROSTER_CAP) != 1:
        raise ValueError("candidate lost the two-troll training cap")
    if candidate.count(GENERIC_FALLBACK) != 0 or candidate.count(FAIL_SAFE) != 1:
        raise ValueError("declared replacement did not apply exactly once")

    candidate_bytes = candidate.encode()
    removed = len(source_bytes) - len(candidate_bytes)
    if removed <= 0:
        raise ValueError("candidate is not smaller")
    manifest = {
        "schema": "troll-farm-e7a-single-logical-deletion-v1",
        "arm": "REMOVE_UNREACHABLE_GENERIC_SELECTOR",
        "baseline": {
            "bytes": len(source_bytes),
            "sha256": BASELINE_SHA256,
        },
        "candidate": {
            "bytes": len(candidate_bytes),
            "sha256": sha256(candidate_bytes),
            "removed_bytes": removed,
            "reduction_fraction": removed / len(source_bytes),
        },
        "logical_change": (
            "delete the generic greedy action selector for friendly rosters above two; "
            "preserve the exact zero/one/two-worker selector and return one WAIT per "
            "worker if the impossible larger-roster state is observed"
        ),
        "supported_state_argument": {
            "training_cap_preserved": ROSTER_CAP,
            "maximum_friendly_roster": 2,
            "orchard_wrapper_can_train": False,
        },
        "identifier_renaming": False,
        "minification": False,
        "compression": False,
        "formatting_reduction": False,
        "evidence_boundary": (
            "candidate generation only; compile, semantic, replay, development, and "
            "untouched equality gates remain required"
        ),
    }
    return candidate, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    candidate, manifest = build(args.source.read_text())
    if args.candidate.exists() or args.manifest.exists():
        parser.error("refusing to overwrite an existing candidate or manifest")
    args.candidate.write_text(candidate)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["candidate"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
