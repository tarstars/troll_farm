#!/usr/bin/env python3
"""Render turn-one protocol records for one agent's archived occurrences."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.arena_rollout_forensics import render_turn_one  # noqa: E402
from cgauto.top_player_opening_analysis import RAW_GAMES  # noqa: E402


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def records(analysis: dict, agent_id: int, raw_games: Path = RAW_GAMES) -> list[str]:
    selected = [row for row in analysis["occurrences"] if row["agent_id"] == agent_id]
    selected.sort(key=lambda row: row["game_id"])
    game_ids = [row["game_id"] for row in selected]
    if len(game_ids) != len(set(game_ids)):
        raise ValueError(f"agent {agent_id} occurs more than once in one game")
    result = []
    for row in selected:
        game = json.loads((raw_games / f"{row['game_id']}.json").read_text())
        result.append(f"SEED {row['game_id']}\n{render_turn_one(game, row['seat'])}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analysis = json.loads(args.analysis.read_text())
    rendered = records(analysis, args.agent_id)
    if not rendered:
        raise SystemExit(f"agent {args.agent_id} has no occurrences")
    atomic_write(args.output, "".join(rendered))
    print(f"saved {len(rendered)} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
