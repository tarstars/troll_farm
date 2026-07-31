#!/usr/bin/env python3
"""Build the second-worker-funding-first, diagonal tent-denial successor.

The exact live wrapper applies tent denial after the opening planner and can overwrite
the sole worker's resource-collection command. This fail-closed transform preserves the
inner opening command while own roster is below two and the opening objective remains
active. Once worker two exists, or the opening is explicitly abandoned, denial resumes.

The same owner-directed successor expands the enemy-tent proximity set from four
cardinal cells to the full eight-neighbor ring. No resident source file is edited.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


REPO = Path(__file__).resolve().parent.parent
PARENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585765-onsite-tree-owner-slim.min.rs"
)
PARENT_SHA256 = "fab84019558e19491a0ce3408d584e4483f398a11da3140bf9adc5de30a90efc"
OUTPUT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585801-second-funding-first-diagonal-denial-slim.min.rs"
)

UNIT_IDS_ANCHOR = (
    "let mut unit_ids:Vec<_>=view.units.iter().filter(|unit|unit.player==0)"
    ".map(|unit|unit.id).collect();unit_ids.sort_unstable();"
    "let workers:Vec<_>="
)
UNIT_IDS_WITH_OPENING_GUARD = (
    "let mut unit_ids:Vec<_>=view.units.iter().filter(|unit|unit.player==0)"
    ".map(|unit|unit.id).collect();unit_ids.sort_unstable();"
    "if unit_ids.len()<2&&!self.inner.opening_abandoned{"
    "self.nonbank_denial_units.clear();self.bank_commitment_units.clear();"
    "self.remember_own_plant_commands(view,&commands,&unit_ids);return commands;}"
    "let workers:Vec<_>="
)

CARDINAL_METHOD = (
    "fn active_tent_adjacent(view:&GameState)->Vec<Cell>{"
    "let mut cells:Vec<_>=ortho_neighbors(view.shacks[1]).into_iter()"
    ".filter(|cell|view.plant_at(*cell).is_some_and(|index|"
    "view.plants[index].health>0)).collect();cells.sort_unstable();cells}"
)
RING_METHOD = (
    "fn active_tent_ring(view:&GameState)->Vec<Cell>{"
    "let tent=view.shacks[1];let mut cells=Vec::new();"
    "for dx in -1..=1{for dy in -1..=1{"
    "if dx==0&&dy==0{continue;}let cell=(tent.0+dx,tent.1+dy);"
    "if view.plant_at(cell).is_some_and(|index|view.plants[index].health>0){"
    "cells.push(cell);}}}cells.sort_unstable();cells}"
)
CARDINAL_CALL = "let adjacent=Self::active_tent_adjacent(view);"
RING_CALL = "let adjacent=Self::active_tent_ring(view);"
PARENT_ANNOUNCEMENT = "yamo-onsite-tree-owner-rust"
CANDIDATE_ANNOUNCEMENT = "yamo-funding-first-diagonal-denial-rust"


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one {label} anchor, found {count}")
    return text.replace(old, new, 1)


def make_candidate(parent: str) -> str:
    actual = digest_text(parent)
    if actual != PARENT_SHA256:
        raise ValueError(
            f"live parent hash changed: expected {PARENT_SHA256}, got {actual}"
        )
    result = replace_once(
        parent,
        UNIT_IDS_ANCHOR,
        UNIT_IDS_WITH_OPENING_GUARD,
        "tent-denial unit list",
    )
    result = replace_once(
        result,
        CARDINAL_METHOD,
        RING_METHOD,
        "cardinal tent-neighbor method",
    )
    result = replace_once(
        result,
        CARDINAL_CALL,
        RING_CALL,
        "cardinal tent-neighbor call",
    )
    return replace_once(
        result,
        PARENT_ANNOUNCEMENT,
        CANDIDATE_ANNOUNCEMENT,
        "announcement",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=PARENT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    candidate = make_candidate(args.parent.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate, encoding="utf-8")
    result_sha = digest_text(candidate)
    sidecar = args.output.with_name(args.output.name + ".sha256")
    sidecar.write_text(f"{result_sha}  {args.output.name}\n", encoding="utf-8")
    print(f"built {args.output}: {len(candidate.encode())} bytes")
    print(f"sha256 {result_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
