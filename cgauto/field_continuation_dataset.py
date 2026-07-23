#!/usr/bin/env python3
"""Build normalized exact-map inputs for the Phase 21 continuation audit."""

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

from cgauto import battle_taxonomy as arena
from cgauto.arena_rollout_forensics import (
    candidate_seat,
    initial_replay_state,
    observed_first_stdout,
    render_turn_one,
)


REPO = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "phase21-candidate-field-census-2026-07-19.json"
)
DEFAULT_MAPS = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "field-continuation-phase21-candidate-160.maps"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "field-continuation-phase21-candidate-160-observed.json"
)
EXPECTED_AGENT = 6560269


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def actual_signature(census_row: dict) -> dict:
    timeline = census_row["timeline"]
    checkpoints = {}
    for turn in (50, 100):
        value = timeline.get(str(turn)) or timeline.get(turn)
        if value is None or value.get("opponent") is None:
            raise ValueError(
                f"game {census_row['game_id']} lacks opponent checkpoint {turn}"
            )
        checkpoints[str(turn)] = value["opponent"]
    return {
        "turns": int(census_row["turns"]),
        "final": census_row["final"]["opponent"],
        "checkpoints": checkpoints,
    }


def build_record(game: dict, census_row: dict) -> tuple[dict, str]:
    game_id = int(census_row["game_id"])
    if int(game["gameId"]) != game_id:
        raise ValueError(f"requested game {game_id}, fetched {game.get('gameId')}")
    seat = candidate_seat(game, EXPECTED_AGENT)
    opponent_seat = 1 - seat
    _, initial = initial_replay_state(game)
    opponent_units = [
        unit for unit in initial["units"] if unit["player"] == opponent_seat
    ]
    if len(opponent_units) != 1:
        raise ValueError(f"game {game_id} has {len(opponent_units)} opponent starters")
    opponent_agent = next(
        agent for agent in game.get("agents") or [] if agent["index"] == opponent_seat
    )
    record = {
        "game_id": game_id,
        "candidate_arena_seat": seat,
        "normalized_candidate_seat": 0,
        "opponent": census_row["opponent"],
        "opponent_agent_id": census_row["opponent_agent_id"],
        "opponent_rank": census_row.get("opponent_rank"),
        "opponent_ladder_score": census_row.get("opponent_ladder_score"),
        "opponent_pseudo_from_result": (
            opponent_agent.get("codingamer") or {}
        ).get("pseudo"),
        "opponent_starter_id": int(opponent_units[0]["id"]),
        "actual_first_command": observed_first_stdout(game, opponent_seat).rstrip(
            "\r\n"
        ),
        "margin": int(census_row["margin"]),
        "catastrophic": int(census_row["margin"]) <= -100,
        "worker_rich": int(census_row["final"]["opponent"]["workers"]) >= 3,
        "actual": actual_signature(census_row),
    }
    map_record = f"SEED {game_id}\n{render_turn_one(game, seat)}"
    return record, map_record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--maps-output", type=Path, default=DEFAULT_MAPS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        raise SystemExit("--jobs must be between 1 and 32")

    census = json.loads(args.input.read_text())
    census_rows = census.get("rows") or []
    if len(census_rows) != 160:
        raise SystemExit(f"expected 160 census rows, got {len(census_rows)}")

    def fetch(census_row: dict) -> tuple[dict, str]:
        game_id = int(census_row["game_id"])
        game = arena.call("gameResult/findByGameId", [game_id, None])
        return build_record(game, census_row)

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        built = list(executor.map(fetch, census_rows))
    records = [record for record, _ in built]
    maps = "".join(map_record for _, map_record in built)
    if len({record["game_id"] for record in records}) != 160:
        raise RuntimeError("field continuation cohort contains duplicate game IDs")
    atomic_write(args.maps_output, maps)
    payload = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only normalized initial states and observed opponent signatures from "
            "the consumed Phase 21 candidate cohort"
        ),
        "input": str(args.input.relative_to(REPO)),
        "expected_candidate_agent": EXPECTED_AGENT,
        "games": len(records),
        "maps_output": str(args.maps_output.relative_to(REPO)),
        "maps_sha256": hashlib.sha256(maps.encode()).hexdigest(),
        "records": records,
    }
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(
        f"saved {len(records)} normalized maps to {args.maps_output} "
        f"({payload['maps_sha256']})"
    )
    print(f"saved observed signatures to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
