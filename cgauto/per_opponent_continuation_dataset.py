#!/usr/bin/env python3
"""Build the frozen repeated-agent continuation panel from completed replays."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import battle_taxonomy as arena
from cgauto.recent_resident_field_census import (
    corpus_parser,
    decoded_states,
    inventory_after,
    side_snapshot,
    successful_events,
)
from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import (
    analyze_players,
    assigned_unit_commands,
    opening_features,
)


AGENTS = (
    ("Bondo416", 6480941),
    ("MSz", 6479460),
    ("Meruem", 6479385),
    ("celeria", 6512040),
    ("gaha", 6481397),
    ("viewlagoon", 6481504),
)
SELECTION_SALT = "per-opponent-continuation-v1"
TARGET_FIELDS = (
    "score",
    "fruit",
    "wood",
    "workers",
    "successful_plants",
    "harvested_fruit",
    "chops_landed",
    "dropped_items",
)
PHASES = (("001-050", 1, 50), ("051-100", 51, 100))


def selection_hash(agent_id: int, game_id: int) -> str:
    return hashlib.sha256(
        f"{SELECTION_SALT}:{agent_id}:{game_id}".encode()
    ).hexdigest()


def exact_agent_metadata(
    battles: list[dict], agent_id: int, excluded_game_ids: set[int]
) -> list[dict]:
    rows = []
    for battle in battles:
        game_id = int(battle.get("gameId") or 0)
        if not battle.get("done") or not game_id or game_id in excluded_game_ids:
            continue
        players = battle.get("players") or []
        if not any(int(player.get("playerAgentId") or -1) == agent_id for player in players):
            continue
        rows.append(
            {
                "game_id": game_id,
                "selection_hash": selection_hash(agent_id, game_id),
                "players": [
                    {
                        "agent_id": int(player.get("playerAgentId") or -1),
                        "position": int(player.get("position") or 0),
                        "nickname": player.get("nickname"),
                    }
                    for player in players
                ],
            }
        )
    unique = {row["game_id"]: row for row in rows}
    return sorted(unique.values(), key=lambda row: (row["selection_hash"], row["game_id"]))


def phase_action_counts(states: list[dict], trajectory: list[dict], player: int) -> dict:
    result = {name: Counter() for name, _, _ in PHASES}
    usable = min(len(states) - 1, len(trajectory), 100)
    for turn in range(1, usable + 1):
        phase = next(name for name, start, end in PHASES if start <= turn <= end)
        units = [
            unit for unit in states[turn - 1]["units"] if int(unit["player"]) == player
        ]
        assigned = assigned_unit_commands(
            action_commands(trajectory[turn - 1].get(f"commands{player}")), units
        )
        result[phase].update(command.split()[0].upper() for command in assigned.values())
    return {name: dict(sorted(result[name].items())) for name, _, _ in PHASES}


def snapshots_and_intervals(
    trajectory: list[dict],
    final_inventory: tuple[list[int], list[int]],
    events: list[dict],
    player: int,
) -> tuple[dict, list[dict]]:
    initial = side_snapshot(list(trajectory[0][f"inv{player}"]), events, 0)
    if initial is None:
        raise ValueError("missing initial inventory")
    snapshots = {}
    intervals = []
    previous = initial
    previous_turn = 0
    for cutoff in (50, 100, 150):
        current = side_snapshot(
            inventory_after(trajectory, final_inventory, player, cutoff), events, cutoff
        )
        if current is None:
            raise ValueError(f"missing cutoff {cutoff} inventory")
        snapshots[str(cutoff)] = current
        intervals.append(
            {
                "start_turn": previous_turn + 1,
                "end_turn": cutoff,
                "increments": {
                    field: int(current[field]) - int(previous[field])
                    for field in TARGET_FIELDS
                },
            }
        )
        previous = current
        previous_turn = cutoff
    return snapshots, intervals


def analyze_occurrence(game: dict, agent_name: str, agent_id: int, metadata: dict) -> dict:
    game_id = int(metadata["game_id"])
    if int(game.get("gameId") or -1) != game_id:
        raise ValueError(f"requested {game_id}, received {game.get('gameId')}")
    matching = [
        agent for agent in game.get("agents") or [] if int(agent.get("agentId") or -1) == agent_id
    ]
    if len(matching) != 1:
        raise ValueError(f"game {game_id} has {len(matching)} occurrences of agent {agent_id}")
    player = int(matching[0]["index"])
    opponent_agent = next(
        agent for agent in game.get("agents") or [] if int(agent["index"]) != player
    )
    parser = corpus_parser()
    map_data, _trolls, inv0, inv1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, final_inventory = parser.extract_turns(game["frames"], inv0, inv1)
    decoded_map, states, unknown_updates = decoded_states(game, trajectory)
    turns = len(trajectory)
    if turns < 150:
        raise ValueError(f"short replay: {turns} turns")
    if len(states) - 1 != turns:
        raise ValueError(f"decoded {len(states) - 1} of {turns} turns")
    if unknown_updates:
        raise ValueError(f"unknown diff updates: {unknown_updates}")
    analyses = analyze_players(states, trajectory)
    training_events = [
        {
            "ordinal": int(event["ordinal"]),
            "turn": int(event["turn"]),
            "spec": [int(value) for value in event["spec"]],
        }
        for event in analyses[player]["training_events"]
    ]
    events = successful_events(game["frames"])[player]
    snapshots, intervals = snapshots_and_intervals(
        trajectory, final_inventory, events, player
    )
    return {
        "agent_name": agent_name,
        "agent_id": agent_id,
        "game_id": game_id,
        "selection_hash": metadata["selection_hash"],
        "player": player,
        "opponent": (opponent_agent.get("codingamer") or {}).get("pseudo"),
        "opponent_agent_id": int(opponent_agent.get("agentId") or -1),
        "turns": turns,
        "has_iron": bool(map_data["iron"]),
        "opening": opening_features(decoded_map, states[0], player),
        "training_events": training_events,
        "snapshots": snapshots,
        "intervals": intervals,
        "scheduler": {"phase_actions": phase_action_counts(states, trajectory, player)},
        "integrity": {
            "trajectory_turns": turns,
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": unknown_updates,
        },
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def build(
    excluded_game_ids: set[int], jobs: int = 20, attempted_per_agent: int = 40
) -> dict:
    if attempted_per_agent < 24:
        raise ValueError("must attempt at least 24 games per agent")

    def list_agent(agent: tuple[str, int]) -> tuple[str, int, list[dict]]:
        name, agent_id = agent
        battles = arena.call("gamesPlayersRanking/findLastBattlesByAgentId", [agent_id, None])
        return name, agent_id, exact_agent_metadata(battles, agent_id, excluded_game_ids)

    with ThreadPoolExecutor(max_workers=min(jobs, len(AGENTS))) as executor:
        listed = list(executor.map(list_agent, AGENTS))
    metadata_by_agent = {
        agent_id: rows for _name, agent_id, rows in listed
    }
    for name, agent_id, rows in listed:
        if len(rows) < attempted_per_agent:
            raise ValueError(f"{name} exposes only {len(rows)} eligible metadata rows")

    attempts = [
        (name, agent_id, metadata)
        for name, agent_id in AGENTS
        for metadata in metadata_by_agent[agent_id][:attempted_per_agent]
    ]
    unique_game_ids = sorted({metadata["game_id"] for _, _, metadata in attempts})

    def fetch(game_id: int) -> tuple[int, dict | None, str | None]:
        try:
            return (
                game_id,
                arena.call("gameResult/findByGameId", [game_id, None]),
                None,
            )
        except Exception as error:  # pragma: no cover - network failure path
            return game_id, None, f"{type(error).__name__}: {error}"

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        fetched = list(executor.map(fetch, unique_game_ids))
    games = {game_id: game for game_id, game, error in fetched if game is not None}
    fetch_errors = {
        game_id: error for game_id, game, error in fetched if game is None
    }

    analyzed_by_agent: dict[int, list[dict]] = {agent_id: [] for _, agent_id in AGENTS}
    occurrence_errors = []
    for name, agent_id, metadata in attempts:
        game_id = metadata["game_id"]
        if game_id in fetch_errors:
            occurrence_errors.append(
                {
                    "agent_name": name,
                    "agent_id": agent_id,
                    "game_id": game_id,
                    "error": fetch_errors[game_id],
                }
            )
            continue
        try:
            analyzed_by_agent[agent_id].append(
                analyze_occurrence(games[game_id], name, agent_id, metadata)
            )
        except Exception as error:
            occurrence_errors.append(
                {
                    "agent_name": name,
                    "agent_id": agent_id,
                    "game_id": game_id,
                    "error": f"{type(error).__name__}: {error}",
                }
            )

    retained = []
    selection = {}
    for name, agent_id in AGENTS:
        eligible = sorted(
            analyzed_by_agent[agent_id],
            key=lambda row: (row["selection_hash"], row["game_id"]),
        )
        if len(eligible) < 24:
            raise ValueError(
                f"{name} has only {len(eligible)} eligible replays among "
                f"{attempted_per_agent} attempts"
            )
        selected = eligible[:24]
        for index, row in enumerate(selected):
            row["selection_index"] = index
            row["partition"] = "discovery" if index < 16 else "confirmation"
        retained.extend(selected)
        selection[str(agent_id)] = {
            "agent_name": name,
            "listed_exact_completed": len(metadata_by_agent[agent_id]),
            "attempted": attempted_per_agent,
            "eligible": len(eligible),
            "retained": len(selected),
            "discovery": 16,
            "confirmation": 8,
            "retained_game_ids": [row["game_id"] for row in selected],
        }
    identities = {(row["agent_id"], row["game_id"]) for row in retained}
    if len(retained) != 144 or len(identities) != 144:
        raise ValueError("panel is not the exact unique 6 x 24 occurrence grid")
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "read-only hash-selected repeated-agent continuation panel",
        "selection_salt": SELECTION_SALT,
        "agents": [{"name": name, "agent_id": agent_id} for name, agent_id in AGENTS],
        "excluded_game_ids": sorted(excluded_game_ids),
        "attempted_per_agent": attempted_per_agent,
        "unique_replays_fetched": len(games),
        "fetch_errors": [
            {"game_id": game_id, "error": error}
            for game_id, error in sorted(fetch_errors.items())
        ],
        "occurrence_errors": occurrence_errors,
        "selection": selection,
        "occurrences": len(retained),
        "rows": sorted(retained, key=lambda row: (row["agent_id"], row["selection_index"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rich-scheduler", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=20)
    parser.add_argument("--attempted-per-agent", type=int, default=40)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        raise SystemExit("--jobs must be between 1 and 32")
    rich = json.loads(args.rich_scheduler.read_text())
    excluded = {int(row["game_id"]) for row in rich.get("rows") or []}
    if len(excluded) != 21:
        raise SystemExit(f"expected 21 consumed rich games, got {len(excluded)}")
    payload = build(excluded, args.jobs, args.attempted_per_agent)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(
        json.dumps(
            {
                "occurrences": payload["occurrences"],
                "unique_replays_fetched": payload["unique_replays_fetched"],
                "fetch_errors": len(payload["fetch_errors"]),
                "occurrence_errors": len(payload["occurrence_errors"]),
                "selection": payload["selection"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
