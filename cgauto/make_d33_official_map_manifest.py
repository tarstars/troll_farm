#!/usr/bin/env python3
"""Freeze the outcome-blind D33 archived official-map confirmation manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.arena_rollout_forensics import render_turn_one  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "data/raw/games"
CHECKPOINT = REPO / "data/analysis/live-agent-6553250/d29b-pretransfer-resident-checkpoint-2026-07-20.json"
D32_PANEL = REPO / "data/panels/d32a-deterministic-field-option-ab-20260720.json"
OUTPUT = REPO / "data/analysis/live-agent-6553250/d33-official-map-confirmation-manifest.json"
SEED_PATTERN = re.compile(r"^seed=(-?\d+)\n$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.count != 120:
        raise SystemExit("D33 freezes exactly 120 confirmation games")

    checkpoint = json.loads(CHECKPOINT.read_text())
    d32 = json.loads(D32_PANEL.read_text())
    excluded = {int(row["game_id"]) for row in checkpoint["rows"]}
    excluded.update(int(row["game_id"]) for row in d32["rows"])
    records = []
    seeds = set()
    for path in sorted(RAW.glob("*.json"), key=lambda value: int(value.stem)):
        game_id = int(path.stem)
        if game_id in excluded:
            continue
        game = json.loads(path.read_text())
        match = SEED_PATTERN.fullmatch(str(game.get("refereeInput") or ""))
        if not match:
            continue
        seed = int(match.group(1))
        if seed in seeds or not -(2**63) <= seed < 2**63:
            continue
        try:
            turn_one = render_turn_one(game, 0)
        except (KeyError, TypeError, ValueError):
            continue
        lines = turn_one.splitlines()
        if not lines:
            continue
        width, height = (int(value) for value in lines[0].split())
        grid = lines[1 : 1 + height]
        if not (8 <= height <= 11 and width == 2 * height):
            continue
        if len(grid) != height or not any("~" in row for row in grid) or not any("+" in row for row in grid):
            continue
        records.append(
            {
                "game_id": game_id,
                "seed": seed,
                "path": str(path.relative_to(REPO)),
                "raw_sha256": digest(path),
                "turn_one_bytes": len(turn_one.encode()),
                "turn_one_sha256": hashlib.sha256(turn_one.encode()).hexdigest(),
            }
        )
        seeds.add(seed)
        if len(records) == args.count:
            break
    if len(records) != args.count:
        raise SystemExit(f"found only {len(records)} eligible games")

    payload = {
        "schema": 1,
        "frozen_on": "2026-07-20",
        "selection": "ascending game id; outcome-blind Legend-map eligibility",
        "source_commit": "290129129db7a7539d98739ebdb0ed63ee6ceb50",
        "checkpoint_sha256": digest(CHECKPOINT),
        "d32_panel_sha256": digest(D32_PANEL),
        "excluded_game_ids": len(excluded),
        "games": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"wrote {args.output} games={len(records)}")


if __name__ == "__main__":
    main()
