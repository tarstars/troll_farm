#!/usr/bin/env python3
"""Build the owner-directed no-orchard arena ablation from the round-28 head.

This is deliberately NOT a behavior-exact simplification round: it blocks the
SecureOrchardBot activation path so the wrapper can never leave Dormant, making
the bot a pure YamoBot passthrough on every map. Purpose: measure the orchard's
live ladder value by ablation, per the owner's 2026-08-03 directive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PARENT_SHA256 = "c77504639b4282c1cd773dd102d4f678fb90622d67edb1da2173050411e5810e"

OLD = (
    "if checkpoint&&has_second&&self.can_activate(view,starter,&geometry)"
    "{self.phase=OrchardPhase::CarryingSeed;}else{return commands;}"
)
NEW = "return commands;"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    parent = args.parent.read_bytes()
    if digest(parent) != PARENT_SHA256:
        parser.error("parent SHA-256 does not match the round-28 head")
    if args.candidate.exists() or args.manifest.exists():
        parser.error("refusing to overwrite an existing experiment artifact")

    source = parent.decode()
    if source.count(OLD) != 1:
        raise ValueError("orchard activation anchor is not unique")
    candidate_text = source.replace(OLD, NEW, 1)
    if "CarryingSeed;}" in candidate_text and "self.phase=OrchardPhase::CarryingSeed" in candidate_text:
        raise ValueError("activation path survived")

    candidate = candidate_text.encode()
    manifest = {
        "schema": "troll-farm-e7a-no-orchard-ablation-v1",
        "purpose": (
            "owner-directed arena ablation: orchard permanently dormant; every "
            "map degenerates to pure YamoBot passthrough"
        ),
        "behavior_exact": False,
        "expected_divergence": (
            "only games where the orchard would activate; 1/25 in the frozen "
            "public packet (game 897833045)"
        ),
        "parent": {
            "path": str(args.parent),
            "bytes": len(parent),
            "sha256": PARENT_SHA256,
        },
        "candidate": {
            "path": str(args.candidate),
            "bytes": len(candidate),
            "sha256": digest(candidate),
        },
        "logical_change": (
            "replace the Dormant-phase activation branch with an unconditional "
            "return, so SecureOrchardBot never enters CarryingSeed; the external "
            "idle/protected-tree reservations stay disengaged and YamoBot output "
            "passes through unmodified on every turn"
        ),
    }
    args.candidate.parent.mkdir(parents=True, exist_ok=True)
    args.candidate.write_bytes(candidate)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["candidate"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
