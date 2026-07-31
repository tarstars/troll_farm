#!/usr/bin/env python3
"""Build the on-site capable-worker tree-ownership successor.

The exact live source can assign a tree to an off-tree worker while a capable teammate
already occupies it. The occupant then receives WAIT and collision handling repeatedly
detours the mover. This fail-closed transform suppresses a tree's chop candidate only for
other workers while a capable own worker is currently on that live tree.

Different-tree ordering, scores, banking, tent coordination, collision resolution, and
all cross-turn state remain unchanged. No resident source file is edited.
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
    "candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs"
)
PARENT_SHA256 = "f26e3781e972006cb2698420bba3474f1a038708225beeb562f3ab2242593e4a"
OUTPUT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585765-onsite-tree-owner-slim.min.rs"
)

LOOP_ANCHOR = (
    "for plant in&view.plants{if plant.health<=0||"
    "!from_unit.contains_key(&plant.cell){continue;}"
)
LOOP_WITH_OWNER = (
    LOOP_ANCHOR
    + "if plant.cell!=unit.cell&&view.units.iter().any(|other|"
    "other.player==unit.player&&other.id!=unit.id&&"
    "other.cell==plant.cell&&other.stats.chop_power>0){continue;}"
)
PARENT_ANNOUNCEMENT = "yamo-tent-banker-commitment-rust"
CANDIDATE_ANNOUNCEMENT = "yamo-onsite-tree-owner-rust"


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
        LOOP_ANCHOR,
        LOOP_WITH_OWNER,
        "chop-candidate plant loop",
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
