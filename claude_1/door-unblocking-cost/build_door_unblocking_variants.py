#!/usr/bin/env python3
"""Build the door-unblocking ablation pair from the frozen live E7a baseline.

Same two-stage method as the accepted orchard code-cost audit, so the two
feature costs are directly comparable against the same 62,820-byte program.

Stage 1 (reference): the single guarded call to force_unique_door_clear is
removed, so the door-unblocking routine never runs. Nothing else changes.

Stage 2 (stripped): from the reference, physically delete the now-unreachable
implementation — force_unique_door_clear and the four helpers used only by it
(unique_shack_door, planned_egress, forced_move, carries_committed_fruit) — plus
the door_unblocking switch field, its initializer and the factory assignment.
Shared helpers (compatible, move_command) are retained and counted as shared.

Motivated by the round-36 coverage panel: force_unique_door_clear has 341
regions of which 337 never execute across the 25-game frozen packet (1.2 %).
Cold is not dead — this is a deliberate behavior change, measured, not a
behavior-exact simplification round.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"

ACTIVATION_CALL = "if self.door_unblocking{self.force_unique_door_clear(view,&mut by_id);}"

EXCLUSIVE_FNS = [
    "force_unique_door_clear",
    "unique_shack_door",
    "planned_egress",
    "forced_move",
    "carries_committed_fruit",
]

SWITCH_OPS = [
    ("door_unblocking:bool,", "", 1),
    ("door_unblocking:false,", "", 1),
    ("bot.door_unblocking=true;", "", 1),
]

RESIDUE = ["door_unblocking", "force_unique_door_clear", "unique_shack_door",
           "forced_move", "carries_committed_fruit"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def match_brace(text: str, open_idx: int) -> int:
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unterminated block")


def cut_fn(text: str, name: str) -> tuple[str, int]:
    matches = list(re.finditer(r"fn " + re.escape(name) + r"\(", text))
    if len(matches) != 1:
        raise ValueError(f"{name}: expected one definition, found {len(matches)}")
    start = matches[0].start()
    end = match_brace(text, text.index("{", matches[0].end())) + 1
    return text[:start] + text[end:], end - start


def replace_counted(text: str, old: str, new: str, expected: int, label: str) -> str:
    count = text.count(old)
    if count != expected:
        raise ValueError(f"{label}: expected {expected}, found {count}")
    return text.replace(old, new)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--stripped", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    baseline = args.baseline.read_bytes()
    if digest(baseline) != BASELINE_SHA256:
        parser.error("baseline SHA-256 mismatch — refusing to build")
    if not args.force:
        for path in (args.reference, args.stripped, args.manifest):
            if path.exists():
                parser.error(f"refusing to overwrite {path}")

    source = baseline.decode()
    reference = replace_counted(source, ACTIVATION_CALL, "", 1, "activation call")

    stripped = reference
    removed = {}
    for name in EXCLUSIVE_FNS:
        stripped, size = cut_fn(stripped, name)
        removed[name] = size
    for old, new, expected in SWITCH_OPS:
        stripped = replace_counted(stripped, old, new, expected, "switch op")
    for residue in RESIDUE:
        if residue in stripped:
            raise ValueError(f"residue survived: {residue}")
    # planned_egress survives only as a local binding name, never as a call
    if "Self::planned_egress" in stripped:
        raise ValueError("planned_egress call survived")

    reference_bytes = reference.encode()
    stripped_bytes = stripped.encode()
    manifest = {
        "schema": "troll-farm-feature-code-cost-v1",
        "feature": "door-unblocking (force_unique_door_clear cluster)",
        "motivation": (
            "round-36 coverage panel: 337 of 341 regions never execute across the "
            "25-game frozen packet (1.2 % covered)"
        ),
        "behavior_exact": False,
        "baseline": {
            "path": str(args.baseline),
            "bytes": len(baseline),
            "characters": len(source),
            "sha256": BASELINE_SHA256,
        },
        "reference": {
            "path": str(args.reference),
            "bytes": len(reference_bytes),
            "sha256": digest(reference_bytes),
            "semantic_change": "door-unblocking routine is never called; nothing else",
        },
        "stripped": {
            "path": str(args.stripped),
            "bytes": len(stripped_bytes),
            "sha256": digest(stripped_bytes),
        },
        "removed_function_bytes": removed,
        "cost": {
            "bytes_removed_vs_baseline": len(baseline) - len(stripped_bytes),
            "percent_of_baseline": round(
                100 * (len(baseline) - len(stripped_bytes)) / len(baseline), 3),
            "percent_of_100k_allowance": round(
                (len(baseline) - len(stripped_bytes)) / 1000, 3),
        },
        "shared_retained": ["compatible", "move_command"],
    }
    args.reference.parent.mkdir(parents=True, exist_ok=True)
    args.reference.write_bytes(reference_bytes)
    args.stripped.write_bytes(stripped_bytes)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**manifest["cost"], "removed": removed}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
