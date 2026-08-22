#!/usr/bin/env python3
"""Apply the declared E7a round-15 logical deletion to its exact parent.

Round 15: inline the sole-value ``train_horizon:15`` configuration at its single
read and delete the field and initializer. Contract:
``claude_1/e7a-incremental-simplification/r15-contract-2026-08-03.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PARENT_SHA256 = "c71a0141a02a1d149041db8248b417ff08049ec4dbeeaa6db2225431feb7cfe2"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_exact(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    parent = args.parent.read_bytes()
    if digest(parent) != PARENT_SHA256:
        parser.error("parent SHA-256 does not match the accepted round-14 candidate")
    if args.candidate.exists() or args.manifest.exists():
        parser.error("refusing to overwrite an existing round artifact")

    source = parent.decode()
    if source.count("train_horizon") != 3:
        raise ValueError(
            f"train_horizon: expected 3 occurrences, found {source.count('train_horizon')}"
        )
    candidate_text = source
    candidate_text = replace_exact(
        candidate_text, "pub train_horizon:i32,", "", "train-horizon field"
    )
    candidate_text = replace_exact(
        candidate_text, "train_horizon:15,", "", "sole-value initializer"
    )
    candidate_text = replace_exact(
        candidate_text, "<=policy.train_horizon", "<=15", "single fixed read"
    )
    if "train_horizon" in candidate_text:
        raise ValueError("round 15 left train_horizon plumbing behind")

    candidate = candidate_text.encode()
    if len(candidate) >= len(parent):
        raise ValueError("declared deletion did not make the source smaller")

    manifest = {
        "schema": "troll-farm-e7a-iterative-logical-deletion-round-v1",
        "round": 15,
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
            "inline the sole-value train_horizon 15 at its single opening-filter read "
            "and delete the field and TUNED_CARRY initializer without changing the "
            "comparison"
        ),
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
