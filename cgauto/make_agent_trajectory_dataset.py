#!/usr/bin/env python3
"""Render complete replay decision states for one archived agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    RAW_GAMES,
    player_commands,
    read_trajectory,
)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def relative_map(map_data: dict, seat: int) -> list[str]:
    rows = list(map_data["rows"])
    if seat == 1:
        rows = [row.translate(str.maketrans({"0": "1", "1": "0"})) for row in rows]
    return rows


def render_state(state: dict, seat: int) -> str:
    lines = [
        " ".join(map(str, state["inventories"][player]))
        for player in (seat, 1 - seat)
    ]
    lines.append(str(len(state["plants"])))
    lines.extend(
        f"{plant['type']} {plant['x']} {plant['y']} {plant['size']} "
        f"{plant['health']} {plant['fruits']} {plant['cooldown']}"
        for plant in state["plants"]
    )
    lines.append(str(len(state["units"])))
    for unit in state["units"]:
        values = (
            unit["id"],
            0 if unit["player"] == seat else 1,
            unit["x"],
            unit["y"],
            unit["ms"],
            unit["cc"],
            unit["hp"],
            unit["chop"],
            *unit["carry"],
        )
        lines.append(" ".join(map(str, values)))
    return "\n".join(lines) + "\n"


def record(occurrence: dict, raw_games: Path = RAW_GAMES) -> str:
    game_id = occurrence["game_id"]
    seat = occurrence["seat"]
    trajectory = read_trajectory(game_id)
    parsed = [
        [player_commands(turn, player) for player in (0, 1)] for turn in trajectory
    ]
    chop_ids = [
        effective_chop_unit_ids(turn[0]) + effective_chop_unit_ids(turn[1])
        for turn in parsed
    ]
    decoded = decode_replay(
        raw_games / f"{game_id}.json", chop_unit_ids_by_turn=chop_ids
    )
    usable = min(len(trajectory), len(decoded["states"]) - 1)
    map_data = decoded["map"]
    lines = [
        f"GAME {game_id} {usable}",
        f"{map_data['width']} {map_data['height']}",
        *relative_map(map_data, seat),
    ]
    return "\n".join(lines) + "\n" + "".join(
        render_state(decoded["states"][turn], seat) for turn in range(usable)
    )


def records(analysis: dict, agent_id: int, raw_games: Path = RAW_GAMES) -> list[str]:
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == agent_id
    ]
    occurrences.sort(key=lambda row: row["game_id"])
    return [record(row, raw_games) for row in occurrences]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rendered = records(json.loads(args.analysis.read_text()), args.agent_id)
    if not rendered:
        raise SystemExit(f"agent {args.agent_id} has no occurrences")
    atomic_write(args.output, "".join(rendered))
    print(f"saved {len(rendered)} trajectory records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
