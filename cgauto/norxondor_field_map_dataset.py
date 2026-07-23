#!/usr/bin/env python3
"""Materialize the five consumed three-worker TestSession maps for model-gap diagnosis."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.arena_rollout_forensics import (  # noqa: E402
    initial_replay_state,
    observed_first_stdout,
    render_turn_one,
)
from cgauto.enrich_panel import fetch_replay  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
DEFAULT_PANEL = REPO / "data/panels/norxondor-three-worker-stage2a-top5-20260719.json"
DEFAULT_MAPS = (
    REPO
    / "data/analysis/live-agent-6553250/norxondor-three-worker-stage2a-field-5.maps"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "norxondor-three-worker-stage2a-field-5-observed.json"
)
EXPECTED_SOURCE_SHA = "69237902e54232cdf31ef8e8bc0e6c25066a4c152bde36479ffb8e1ee92f8377"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def build_record(game: dict, row: dict) -> tuple[dict, str]:
    game_id = int(row["game_id"])
    if int(game.get("gameId")) != game_id:
        raise ValueError(f"requested game {game_id}, fetched {game.get('gameId')}")
    scores = [float(value) for value in game.get("scores") or []]
    if scores != [float(value) for value in row["scores"]]:
        raise ValueError(f"game {game_id}: replay scores {scores} != panel {row['scores']}")
    map_data, state = initial_replay_state(game)
    if len([unit for unit in state["units"] if unit["player"] == 0]) != 1:
        raise ValueError(f"game {game_id}: player 0 does not have exactly one starter")
    record = {
        "game_id": game_id,
        "opponent": row["opponent"],
        "scores": scores,
        "margin": scores[0] - scores[1],
        "workers": row["workforce"]["final"][0],
        "successful_training_turns": row["workforce"]["training_turns"][0],
        "first_command": observed_first_stdout(game, 0).rstrip("\r\n"),
        "initial_inventory": state["inventories"][0],
        "initial_plants": len(state["plants"]),
        "map_width": map_data["width"],
        "map_height": map_data["height"],
        "diagnostics": row.get("diagnostics") or [],
    }
    return record, f"SEED {game_id}\n{render_turn_one(game, 0)}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--maps-output", type=Path, default=DEFAULT_MAPS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=5)
    args = parser.parse_args()

    panel = json.loads(args.panel.read_text())
    if panel.get("status") != "complete":
        raise SystemExit("Stage 2A panel is not complete")
    if panel["sources"]["candidate"]["sha256"] != EXPECTED_SOURCE_SHA:
        raise SystemExit("Stage 2A candidate hash changed")
    rows = [row for row in panel.get("rows") or [] if row["bot"] == "candidate"]
    if len(rows) != 5 or len({int(row["game_id"]) for row in rows}) != 5:
        raise SystemExit(f"expected five unique candidate rows, got {len(rows)}")
    if any(row.get("diagnostics") for row in rows):
        raise SystemExit("candidate panel contains runtime diagnostics")

    def fetch(row: dict) -> tuple[dict, str]:
        game = fetch_replay(int(row["game_id"]))
        return build_record(game, row)

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        built = list(executor.map(fetch, rows))
    records = [record for record, _ in built]
    maps = "".join(map_record for _, map_record in built)
    payload = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "five consumed exact Stage 2A candidate maps; normalized player 0",
        "panel": str(args.panel.relative_to(REPO)),
        "candidate_sha256": EXPECTED_SOURCE_SHA,
        "games": len(records),
        "maps_output": str(args.maps_output.relative_to(REPO)),
        "maps_sha256": hashlib.sha256(maps.encode()).hexdigest(),
        "records": records,
    }
    atomic_write(args.maps_output, maps)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(
        f"saved {len(records)} exact normalized maps to {args.maps_output} "
        f"({payload['maps_sha256']})"
    )
    print(f"saved observed field rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
