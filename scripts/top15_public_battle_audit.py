#!/usr/bin/env python3
"""Collect and analyze public recent battles for the current Troll Farm top 15.

The collector is read-only: it calls only leaderboard, last-battle-list, and game-result
services.  It never submits code or starts a TestSession game.  Raw replay responses are
processed in memory; checked-in outputs contain only sanitized identifiers and compact
derived measurements.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto import battle_taxonomy as arena  # noqa: E402
from cgauto.recent_resident_field_census import (  # noqa: E402
    corpus_parser,
    decoded_states,
    inventory_after,
    side_snapshot,
    successful_events,
)
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    adjacent,
    analyze_players,
    assigned_unit_commands,
    opening_features,
    terrain,
)


DEFAULT_INVENTORY = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "top15-public-battle-inventory-2026-08-02.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "top15-public-battle-audit-2026-08-02.json"
)
TOP_N = 15
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
CUTS = (50, 100, 150, 200, 250, 300)
PHASES = (
    ("t001-075", 1, 75),
    ("t076-150", 76, 150),
    ("t151-225", 151, 225),
    ("t226-300", 226, 300),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def leaderboard_top15() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = arena.call(
        "Leaderboards/getFilteredPuzzleLeaderboard",
        [
            arena.PID,
            arena.TSH,
            "global",
            {"active": False, "column": "", "filter": ""},
        ],
    )
    users = sorted(
        payload.get("users") or [],
        key=lambda row: int(row.get("rank") or 10**9),
    )
    rows = []
    for user in users[:TOP_N]:
        league = user.get("league") or {}
        rows.append(
            {
                "rank": int(user.get("rank")),
                "league_local_rank": int(user.get("localRank") or user.get("rank")),
                "score": float(user.get("score")),
                "agent_id": int(user.get("agentId")),
                "pseudo": str(user.get("pseudo")),
                "language": user.get("programmingLanguage"),
                "league_division": league.get("divisionIndex"),
                "creation_time": user.get("creationTime"),
                "update_time": user.get("updateTime"),
            }
        )
    if len(rows) != TOP_N or len({row["agent_id"] for row in rows}) != TOP_N:
        raise ValueError(f"expected {TOP_N} unique top identities, got {len(rows)}")
    if [row["rank"] for row in rows] != list(range(1, TOP_N + 1)):
        raise ValueError("global leaderboard ranks 1..15 are not contiguous")
    return rows, {
        "ranked_users": int(payload.get("count") or len(users)),
        "filtered_users": int(payload.get("filteredCount") or len(users)),
        "response_sha256": digest(payload),
    }


def sanitize_battle(battle: dict[str, Any], listed_agent_id: int) -> dict[str, Any]:
    players = []
    for player in battle.get("players") or []:
        players.append(
            {
                "agent_id": int(player.get("playerAgentId") or -1),
                "submission_id": (
                    int(player["submissionId"])
                    if player.get("submissionId") is not None
                    else None
                ),
                "position": int(player.get("position") or 0),
                "pseudo": player.get("nickname"),
            }
        )
    game_id = int(battle.get("gameId") or 0)
    if not game_id:
        raise ValueError("battle row lacks gameId")
    if not any(player["agent_id"] == listed_agent_id for player in players):
        raise ValueError(
            f"game {game_id} list for {listed_agent_id} does not contain that agent"
        )
    return {
        "game_id": game_id,
        "done": bool(battle.get("done")),
        "players": sorted(players, key=lambda row: row["position"]),
    }


def collect_inventory(jobs: int) -> dict[str, Any]:
    top, leaderboard = leaderboard_top15()

    def list_one(row: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
        agent_id = int(row["agent_id"])
        battles = arena.call(
            "gamesPlayersRanking/findLastBattlesByAgentId", [agent_id, None]
        )
        sanitized = [sanitize_battle(battle, agent_id) for battle in battles]
        return agent_id, sanitized

    with ThreadPoolExecutor(max_workers=min(jobs, TOP_N)) as executor:
        listed = dict(executor.map(list_one, top))

    unique: dict[int, dict[str, Any]] = {}
    agents = []
    for row in top:
        agent_id = int(row["agent_id"])
        battles = listed[agent_id]
        done = [battle for battle in battles if battle["done"]]
        for battle in done:
            game_id = int(battle["game_id"])
            prior = unique.get(game_id)
            if prior is not None and prior != battle:
                raise ValueError(f"inconsistent duplicate metadata for game {game_id}")
            unique[game_id] = battle
        submissions = {}
        for battle in done:
            player = next(
                player
                for player in battle["players"]
                if player["agent_id"] == agent_id
            )
            key = str(player["submission_id"])
            submissions[key] = submissions.get(key, 0) + 1
        agents.append(
            {
                **row,
                "listed": len(battles),
                "finished": len(done),
                "submission_id_counts": dict(sorted(submissions.items())),
                "game_ids": [battle["game_id"] for battle in done],
            }
        )
    compact_games = [unique[game_id] for game_id in sorted(unique)]
    return {
        "schema": "troll-farm-top15-public-battle-inventory-v1",
        "task_id": "20260802-top15-public-battle-audit",
        "generated_at_utc": utc_now(),
        "scope": (
            "public current top-15 leaderboard and every finished row returned by each "
            "exact agent's recent-battle endpoint"
        ),
        "read_only_services": [
            "Leaderboards/getFilteredPuzzleLeaderboard",
            "gamesPlayersRanking/findLastBattlesByAgentId",
        ],
        "leaderboard": leaderboard,
        "agents": agents,
        "counts": {
            "top_agents": len(agents),
            "listed_finished_occurrences": sum(row["finished"] for row in agents),
            "unique_finished_games": len(compact_games),
            "duplicate_occurrences": sum(row["finished"] for row in agents)
            - len(compact_games),
        },
        "games": compact_games,
    }


def validate_inventory(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "troll-farm-top15-public-battle-inventory-v1":
        raise ValueError("unrecognized inventory schema")
    agents = payload.get("agents") or []
    if len(agents) != TOP_N or len({row["agent_id"] for row in agents}) != TOP_N:
        raise ValueError("inventory does not contain 15 unique agents")
    game_ids = [int(row["game_id"]) for row in payload.get("games") or []]
    if game_ids != sorted(set(game_ids)):
        raise ValueError("inventory game ids are not sorted and unique")
    if len(game_ids) != int(payload["counts"]["unique_finished_games"]):
        raise ValueError("inventory unique-game count mismatch")


def mean(values: list[int | float]) -> float | None:
    return sum(values) / len(values) if values else None


def median(values: list[int | float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    middle = len(values) // 2
    if len(values) % 2:
        return float(values[middle])
    return (values[middle - 1] + values[middle]) / 2


def add_item_maps(rows: list[dict[str, int]]) -> dict[str, int]:
    total: Counter[str] = Counter()
    for row in rows:
        total.update({key: int(value) for key, value in row.items()})
    return dict(sorted(total.items()))


def phase_name(turn: int) -> str:
    for name, lo, hi in PHASES:
        if lo <= turn <= hi:
            return name
    return PHASES[-1][0]


def command_summaries(
    states: list[dict[str, Any]], trajectory: list[dict[str, Any]]
) -> tuple[dict[int, dict[str, int]], dict[int, dict[str, dict[str, int]]]]:
    totals = {0: Counter(), 1: Counter()}
    phases = {
        player: {name: Counter() for name, _lo, _hi in PHASES}
        for player in (0, 1)
    }
    usable = min(len(states) - 1, len(trajectory))
    for turn in range(1, usable + 1):
        for player in (0, 1):
            for command in action_commands(
                trajectory[turn - 1].get(f"commands{player}")
            ):
                fields = command.split()
                if not fields:
                    continue
                verb = fields[0].upper()
                if verb == "MSG":
                    continue
                totals[player][verb] += 1
                phases[player][phase_name(turn)][verb] += 1
    return (
        {player: dict(sorted(rows.items())) for player, rows in totals.items()},
        {
            player: {
                phase: dict(sorted(rows.items()))
                for phase, rows in phase_rows.items()
            }
            for player, phase_rows in phases.items()
        },
    )


def movement_liveness(
    states: list[dict[str, Any]], trajectory: list[dict[str, Any]]
) -> dict[int, dict[str, int]]:
    """Measure blocked MOVE commands and uninterrupted ABAB movement episodes."""

    usable = min(len(states) - 1, len(trajectory))
    series: dict[int, list[tuple[tuple[int, int], bool]]] = defaultdict(list)
    owners: dict[int, int] = {}
    for unit in states[0]["units"]:
        owners[int(unit["id"])] = int(unit["player"])
        series[int(unit["id"])].append(((int(unit["x"]), int(unit["y"])), False))

    blocked = Counter()
    move_commands = Counter()
    actual_moves = Counter()
    for turn in range(1, usable + 1):
        before = states[turn - 1]
        after = states[turn]
        before_units = {int(unit["id"]): unit for unit in before["units"]}
        after_units = {int(unit["id"]): unit for unit in after["units"]}
        commanded_move: set[int] = set()
        for player in (0, 1):
            units = [unit for unit in before["units"] if int(unit["player"]) == player]
            assigned = assigned_unit_commands(
                action_commands(trajectory[turn - 1].get(f"commands{player}")), units
            )
            for unit_id, command in assigned.items():
                if command.split()[0].upper() != "MOVE":
                    continue
                commanded_move.add(int(unit_id))
                move_commands[player] += 1
                before_unit = before_units.get(int(unit_id))
                after_unit = after_units.get(int(unit_id))
                moved = bool(
                    before_unit
                    and after_unit
                    and (before_unit["x"], before_unit["y"])
                    != (after_unit["x"], after_unit["y"])
                )
                if moved:
                    actual_moves[player] += 1
                else:
                    blocked[player] += 1
        for unit_id, unit in after_units.items():
            owners.setdefault(unit_id, int(unit["player"]))
            if not series[unit_id]:
                series[unit_id].append(((int(unit["x"]), int(unit["y"])), False))
            else:
                series[unit_id].append(
                    (
                        (int(unit["x"]), int(unit["y"])),
                        unit_id in commanded_move,
                    )
                )

    longest = Counter()
    episode_turns = Counter()
    for unit_id, rows in series.items():
        owner = owners[unit_id]
        current = 0
        best = 0
        counted: set[int] = set()
        for index in range(2, len(rows)):
            alternating = (
                rows[index][0] == rows[index - 2][0]
                and rows[index][0] != rows[index - 1][0]
                and rows[index][1]
                and rows[index - 1][1]
            )
            if alternating:
                current = current + 1 if current else 2
                best = max(best, current)
                counted.update((index - 1, index))
            else:
                current = 0
        longest[owner] = max(longest[owner], best)
        episode_turns[owner] += len(counted)
    return {
        player: {
            "move_commands": int(move_commands[player]),
            "actual_moves": int(actual_moves[player]),
            "blocked_moves": int(blocked[player]),
            "period2_move_turns": int(episode_turns[player]),
            "longest_period2_move_run": int(longest[player]),
        }
        for player in (0, 1)
    }


def field_interactions(
    map_data: dict[str, Any],
    states: list[dict[str, Any]],
    trajectory: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    """Attribute planted generations plus interaction with natural trees near a rival shack."""

    board = terrain(map_data)
    usable = min(len(states) - 1, len(trajectory))
    active: dict[tuple[int, int], dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    natural = {
        (int(plant["x"]), int(plant["y"])): str(plant["type"])
        for plant in states[0]["plants"]
    }
    natural_alive = set(natural)
    natural_metrics = {
        player: {
            "chop_turns": 0,
            "harvest_turns": 0,
            "wood_collected": 0,
            "fruit_harvested": 0,
            "unique_trees_chopped": set(),
            "types_chopped": Counter(),
            "enemy_adjacent_chop_turns": 0,
            "enemy_adjacent_unique_trees": set(),
            "enemy_diagonal_chop_turns": 0,
        }
        for player in (0, 1)
    }

    for turn in range(1, usable + 1):
        before = states[turn - 1]
        after = states[turn]
        before_plants = {
            (int(plant["x"]), int(plant["y"])): plant
            for plant in before["plants"]
        }
        after_plants = {
            (int(plant["x"]), int(plant["y"])): plant
            for plant in after["plants"]
        }
        before_units = {int(unit["id"]): unit for unit in before["units"]}
        after_units = {int(unit["id"]): unit for unit in after["units"]}
        assigned: dict[int, dict[int, str]] = {}
        for player in (0, 1):
            units = [unit for unit in before["units"] if int(unit["player"]) == player]
            assigned[player] = assigned_unit_commands(
                action_commands(trajectory[turn - 1].get(f"commands{player}")), units
            )

        for player in (0, 1):
            enemy_shack = board["shacks"][1 - player]
            for unit_id, command in assigned[player].items():
                fields = command.split()
                if not fields:
                    continue
                verb = fields[0].upper()
                if verb not in ("CHOP", "HARVEST"):
                    continue
                unit = before_units.get(int(unit_id))
                if unit is None:
                    continue
                cell = (int(unit["x"]), int(unit["y"]))
                if cell not in before_plants:
                    continue
                after_unit = after_units.get(int(unit_id))
                gained = [0] * len(ITEMS)
                if after_unit is not None:
                    gained = [
                        max(0, int(after_unit["carry"][index]) - int(unit["carry"][index]))
                        for index in range(len(ITEMS))
                    ]
                record = active.get(cell)
                if record is not None:
                    record[f"{verb.lower()}_turns"][player].append(turn)
                    record["wood_collected"][player] += gained[5]
                    record["fruit_harvested"][player] += sum(gained[:4])
                if cell in natural_alive:
                    metrics = natural_metrics[player]
                    if verb == "CHOP":
                        metrics["chop_turns"] += 1
                        metrics["wood_collected"] += gained[5]
                        metrics["unique_trees_chopped"].add(cell)
                        metrics["types_chopped"][natural[cell]] += 1
                        dx = abs(cell[0] - enemy_shack[0])
                        dy = abs(cell[1] - enemy_shack[1])
                        if max(dx, dy) <= 1:
                            metrics["enemy_adjacent_chop_turns"] += 1
                            metrics["enemy_adjacent_unique_trees"].add(cell)
                            if dx == 1 and dy == 1:
                                metrics["enemy_diagonal_chop_turns"] += 1
                    else:
                        metrics["harvest_turns"] += 1
                        metrics["fruit_harvested"] += sum(gained[:4])

        for cell in list(active):
            if cell not in after_plants:
                active[cell]["death_turn"] = turn
                active.pop(cell, None)
        natural_alive.intersection_update(after_plants)

        for cell, plant in after_plants.items():
            if cell in before_plants:
                continue
            creators = []
            for player in (0, 1):
                for unit_id, command in assigned[player].items():
                    fields = command.split()
                    unit = before_units.get(int(unit_id))
                    if (
                        len(fields) >= 3
                        and fields[0].upper() == "PLANT"
                        and unit is not None
                        and (int(unit["x"]), int(unit["y"])) == cell
                        and fields[2].upper() == str(plant["type"]).upper()
                    ):
                        creators.append(player)
            creators = sorted(set(creators))
            if len(creators) != 1:
                continue
            record = {
                "cell": cell,
                "type": str(plant["type"]),
                "creator": creators[0],
                "birth_turn": turn,
                "death_turn": None,
                "chop_turns": {0: [], 1: []},
                "harvest_turns": {0: [], 1: []},
                "wood_collected": {0: 0, 1: 0},
                "fruit_harvested": {0: 0, 1: 0},
            }
            active[cell] = record
            records.append(record)

    result = {}
    for player in (0, 1):
        own = [record for record in records if record["creator"] == player]
        other = [record for record in records if record["creator"] == 1 - player]
        self_reaped = [record for record in own if record["harvest_turns"][player]]
        replanted_after_reap = 0
        for record in self_reaped:
            first_harvest = min(record["harvest_turns"][player])
            if any(
                later["creator"] == player
                and later["type"] == record["type"]
                and later["birth_turn"] > first_harvest
                for later in records
            ):
                replanted_after_reap += 1
        opponent_contacted = [
            record
            for record in other
            if record["chop_turns"][player] or record["harvest_turns"][player]
        ]
        conversions = [
            record
            for record in own
            if record["birth_turn"] >= 251
            and record["chop_turns"][player]
            and record["wood_collected"][player] > 0
        ]
        natural_row = natural_metrics[player]
        result[player] = {
            "created_crops": len(own),
            "created_types": dict(sorted(Counter(row["type"] for row in own).items())),
            "own_crops_reaped": len(self_reaped),
            "own_crop_fruit_harvested": sum(
                row["fruit_harvested"][player] for row in own
            ),
            "own_crops_self_chopped": sum(bool(row["chop_turns"][player]) for row in own),
            "own_crop_wood_collected": sum(row["wood_collected"][player] for row in own),
            "own_crops_opponent_harvested": sum(
                bool(row["harvest_turns"][1 - player]) for row in own
            ),
            "own_crops_opponent_chopped": sum(
                bool(row["chop_turns"][1 - player]) for row in own
            ),
            "reaped_then_replanted_same_type": replanted_after_reap,
            "opponent_created_crops": len(other),
            "opponent_crops_contacted": len(opponent_contacted),
            "opponent_crops_chopped": sum(bool(row["chop_turns"][player]) for row in other),
            "opponent_crops_harvested": sum(
                bool(row["harvest_turns"][player]) for row in other
            ),
            "endgame_conversion_crops": len(conversions),
            "endgame_conversion_wood": sum(
                row["wood_collected"][player] for row in conversions
            ),
            "natural_chop_turns": natural_row["chop_turns"],
            "natural_harvest_turns": natural_row["harvest_turns"],
            "natural_wood_collected": natural_row["wood_collected"],
            "natural_fruit_harvested": natural_row["fruit_harvested"],
            "natural_unique_trees_chopped": len(natural_row["unique_trees_chopped"]),
            "natural_types_chopped": dict(sorted(natural_row["types_chopped"].items())),
            "enemy_adjacent_natural_chop_turns": natural_row[
                "enemy_adjacent_chop_turns"
            ],
            "enemy_adjacent_natural_trees_chopped": len(
                natural_row["enemy_adjacent_unique_trees"]
            ),
            "enemy_diagonal_natural_chop_turns": natural_row[
                "enemy_diagonal_chop_turns"
            ],
        }
    return result


def compact_training(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "ordinal": int(event["ordinal"]),
            "turn": int(event["turn"]),
            "spec": [int(value) for value in event["spec"]],
            "role": event.get("role"),
            "starting_bank_funded": bool(event.get("starting_bank_funded")),
            "delay_after_affordable": event.get("delay_after_affordable"),
        }
        for event in analysis["training_events"]
    ]


def side_occurrence(
    game: dict[str, Any],
    seat: int,
    metadata: dict[str, Any],
    map_data: dict[str, Any],
    states: list[dict[str, Any]],
    trajectory: list[dict[str, Any]],
    final_inventory: tuple[list[int], list[int]],
    events: dict[int, list[dict[str, Any]]],
    analyses: dict[int, dict[str, Any]],
    commands: dict[int, dict[str, int]],
    phase_commands: dict[int, dict[str, dict[str, int]]],
    liveness: dict[int, dict[str, int]],
    interactions: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    agents = {int(row["index"]): row for row in game.get("agents") or []}
    own = agents[seat]
    opponent = agents[1 - seat]
    scores = [int(value) for value in game.get("scores") or []]
    analysis = analyses[seat]
    initial_state = {
        "inventories": states[0]["inventories"],
        "units": states[0]["units"],
        "plants": states[0]["plants"],
    }
    timeline = {}
    for cut in CUTS:
        inventory = inventory_after(trajectory, final_inventory, seat, cut)
        timeline[str(cut)] = side_snapshot(inventory, events[seat], cut)
    workers = analysis["workers"]
    item_activity = {
        field: add_item_maps([worker.get(field, {}) for worker in workers])
        for field in ("harvested", "chopped", "planted", "picked", "mined", "dropped")
    }
    player_metadata = next(
        row for row in metadata["players"] if int(row["agent_id"]) == int(own["agentId"])
    )
    return {
        "game_id": int(game["gameId"]),
        "agent_id": int(own["agentId"]),
        "submission_id": player_metadata.get("submission_id"),
        "pseudo": (own.get("codingamer") or {}).get("pseudo")
        or player_metadata.get("pseudo"),
        "seat": seat,
        "opponent_agent_id": int(opponent.get("agentId") or -1),
        "opponent": (opponent.get("codingamer") or {}).get("pseudo") or "?",
        "turns": len(trajectory),
        "score": scores[seat],
        "opponent_score": scores[1 - seat],
        "margin": scores[seat] - scores[1 - seat],
        "opening": opening_features(map_data, initial_state, seat),
        "training": compact_training(analysis),
        "final_worker_count": 1 + len(analysis["training_events"]),
        "commands": commands[seat],
        "phase_commands": phase_commands[seat],
        "item_activity": item_activity,
        "movement": liveness[seat],
        "field": interactions[seat],
        "timeline": timeline,
        "final_inventory": [int(value) for value in final_inventory[seat]],
    }


def analyze_game(
    game: dict[str, Any],
    metadata: dict[str, Any],
    listed_by_agent: dict[int, set[int]],
) -> dict[str, Any]:
    if int(game.get("gameId") or -1) != int(metadata["game_id"]):
        raise ValueError("game-result identity mismatch")
    frames = game.get("frames") or []
    if not frames:
        raise ValueError("game has no frames")
    parser = corpus_parser()
    map_data, _units, inv0, inv1 = parser.parse_frame0(frames[0]["view"])
    trajectory, final_inventory = parser.extract_turns(frames, inv0, inv1)
    decoded_map, states, unknown_updates = decoded_states(game, trajectory)
    if len(states) - 1 != len(trajectory):
        raise ValueError(
            f"decoded {len(states) - 1} states for {len(trajectory)} turns"
        )
    analyses = analyze_players(states, trajectory)
    events = successful_events(frames)
    commands, phase_commands = command_summaries(states, trajectory)
    liveness = movement_liveness(states, trajectory)
    interactions = field_interactions(decoded_map, states, trajectory)
    occurrences = []
    for agent in game.get("agents") or []:
        agent_id = int(agent.get("agentId") or -1)
        if int(game["gameId"]) not in listed_by_agent.get(agent_id, set()):
            continue
        seat = int(agent["index"])
        occurrences.append(
            side_occurrence(
                game,
                seat,
                metadata,
                decoded_map,
                states,
                trajectory,
                final_inventory,
                events,
                analyses,
                commands,
                phase_commands,
                liveness,
                interactions,
            )
        )
    return {
        "game_id": int(game["gameId"]),
        "occurrences": occurrences,
        "quality": {
            "turns": len(trajectory),
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": int(unknown_updates),
        },
    }


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    return numerator / denominator if denominator else None


def summarize_agent(rows: list[dict[str, Any]], rank: int) -> dict[str, Any]:
    margins = [int(row["margin"]) for row in rows]
    train_turns = {
        ordinal: [
            int(event["turn"])
            for row in rows
            for event in row["training"]
            if int(event["ordinal"]) == ordinal
        ]
        for ordinal in (1, 2, 3)
    }
    created = sum(int(row["field"]["created_crops"]) for row in rows)
    reaped = sum(int(row["field"]["own_crops_reaped"]) for row in rows)
    replanted = sum(
        int(row["field"]["reaped_then_replanted_same_type"]) for row in rows
    )
    move_commands = sum(int(row["movement"]["move_commands"]) for row in rows)
    blocked_moves = sum(int(row["movement"]["blocked_moves"]) for row in rows)
    return {
        "rank": rank,
        "pseudo": rows[0]["pseudo"] if rows else None,
        "agent_id": rows[0]["agent_id"] if rows else None,
        "submission_ids": dict(sorted(Counter(str(row["submission_id"]) for row in rows).items())),
        "games": len(rows),
        "distinct_opponents": len({row["opponent_agent_id"] for row in rows}),
        "wins": sum(value > 0 for value in margins),
        "ties": sum(value == 0 for value in margins),
        "losses": sum(value < 0 for value in margins),
        "mean_margin": mean(margins),
        "median_margin": median(margins),
        "catastrophes": sum(value <= -100 for value in margins),
        "negative_margin_mass": sum(-value for value in margins if value < 0),
        "mean_score": mean([row["score"] for row in rows]),
        "mean_final_wood": mean([row["final_inventory"][5] for row in rows]),
        "workforce": {
            "worker3_games": sum(row["final_worker_count"] >= 3 for row in rows),
            "worker3_rate": ratio(
                sum(row["final_worker_count"] >= 3 for row in rows), len(rows)
            ),
            "worker4_games": sum(row["final_worker_count"] >= 4 for row in rows),
            "worker4_rate": ratio(
                sum(row["final_worker_count"] >= 4 for row in rows), len(rows)
            ),
            "median_worker2_turn": median(train_turns[1]),
            "median_worker3_turn": median(train_turns[2]),
            "median_worker4_turn": median(train_turns[3]),
        },
        "production": {
            "games_with_planting": sum(row["field"]["created_crops"] > 0 for row in rows),
            "created_crops": created,
            "own_crops_reaped": reaped,
            "crop_reap_rate": ratio(reaped, created),
            "reaped_then_replanted_same_type": replanted,
            "own_crop_fruit_harvested": sum(
                row["field"]["own_crop_fruit_harvested"] for row in rows
            ),
            "own_crop_wood_collected": sum(
                row["field"]["own_crop_wood_collected"] for row in rows
            ),
            "opponent_takes": sum(
                row["field"]["own_crops_opponent_harvested"]
                + row["field"]["own_crops_opponent_chopped"]
                for row in rows
            ),
        },
        "denial": {
            "opponent_created_crops": sum(
                row["field"]["opponent_created_crops"] for row in rows
            ),
            "opponent_crops_contacted": sum(
                row["field"]["opponent_crops_contacted"] for row in rows
            ),
            "opponent_crops_chopped": sum(
                row["field"]["opponent_crops_chopped"] for row in rows
            ),
            "opponent_crops_harvested": sum(
                row["field"]["opponent_crops_harvested"] for row in rows
            ),
            "enemy_adjacent_natural_chop_turns": sum(
                row["field"]["enemy_adjacent_natural_chop_turns"] for row in rows
            ),
            "enemy_diagonal_natural_chop_turns": sum(
                row["field"]["enemy_diagonal_natural_chop_turns"] for row in rows
            ),
        },
        "endgame": {
            "conversion_crops": sum(
                row["field"]["endgame_conversion_crops"] for row in rows
            ),
            "conversion_wood": sum(
                row["field"]["endgame_conversion_wood"] for row in rows
            ),
            "games_with_conversion": sum(
                row["field"]["endgame_conversion_crops"] > 0 for row in rows
            ),
        },
        "liveness": {
            "move_commands": move_commands,
            "blocked_moves": blocked_moves,
            "blocked_move_rate": ratio(blocked_moves, move_commands),
            "games_with_period2_run_ge6": sum(
                row["movement"]["longest_period2_move_run"] >= 6 for row in rows
            ),
            "maximum_period2_move_run": max(
                (row["movement"]["longest_period2_move_run"] for row in rows),
                default=0,
            ),
        },
    }


def conditional_sector_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Describe policy shifts across predeclared map-richness quartiles; do not fit a selector."""

    if not rows:
        return {}
    fruit_values = [int(row["opening"]["fruit_total"]) for row in rows]
    tree_values = [int(row["opening"]["tree_total"]) for row in rows]
    fruit_cut = sorted(fruit_values)[(3 * len(fruit_values)) // 4]
    tree_cut = sorted(tree_values)[(3 * len(tree_values)) // 4]

    def group_summary(group: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "games": len(group),
            "worker3_rate": ratio(
                sum(row["final_worker_count"] >= 3 for row in group), len(group)
            ),
            "worker4_rate": ratio(
                sum(row["final_worker_count"] >= 4 for row in group), len(group)
            ),
            "planting_game_rate": ratio(
                sum(row["field"]["created_crops"] > 0 for row in group), len(group)
            ),
            "mean_margin": mean([row["margin"] for row in group]),
        }

    result = {
        "definition": (
            "rich iff initial fruit_total and tree_total are each at or above their pooled "
            "top-15 75th-percentile cut; descriptive, no fitted selector"
        ),
        "fruit_total_cut": fruit_cut,
        "tree_total_cut": tree_cut,
        "agents": [],
    }
    for agent_id, group in sorted(
        ((agent_id, [row for row in rows if row["agent_id"] == agent_id])
         for agent_id in {row["agent_id"] for row in rows}),
        key=lambda pair: min(row["leaderboard_rank"] for row in pair[1]),
    ):
        rich = [
            row
            for row in group
            if row["opening"]["fruit_total"] >= fruit_cut
            and row["opening"]["tree_total"] >= tree_cut
        ]
        other = [row for row in group if row not in rich]
        result["agents"].append(
            {
                "agent_id": agent_id,
                "pseudo": group[0]["pseudo"],
                "rank": group[0]["leaderboard_rank"],
                "rich": group_summary(rich),
                "other": group_summary(other),
            }
        )
    return result


def build_summary(
    rows: list[dict[str, Any]], inventory: dict[str, Any]
) -> dict[str, Any]:
    ranks = {int(row["agent_id"]): int(row["rank"]) for row in inventory["agents"]}
    by_agent: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_agent[int(row["agent_id"])].append(row)
    return {
        "per_agent": [
            summarize_agent(by_agent[agent_id], rank)
            for agent_id, rank in sorted(ranks.items(), key=lambda pair: pair[1])
        ],
        "conditional_map_sectors": conditional_sector_summary(rows),
    }


def run_full(inventory: dict[str, Any], jobs: int) -> dict[str, Any]:
    metadata_by_game = {
        int(row["game_id"]): row for row in inventory.get("games") or []
    }
    listed_by_agent = {
        int(agent["agent_id"]): {int(game_id) for game_id in agent["game_ids"]}
        for agent in inventory["agents"]
    }
    game_ids = sorted(metadata_by_game)

    def fetch_and_analyze(game_id: int) -> tuple[int, dict[str, Any] | None, str | None]:
        try:
            game = arena.call("gameResult/findByGameId", [game_id, None])
            return game_id, analyze_game(
                game, metadata_by_game[game_id], listed_by_agent
            ), None
        except Exception as error:  # noqa: BLE001 - preserve complete read audit
            return game_id, None, f"{type(error).__name__}: {error}"

    analyzed = []
    errors = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        for index, result in enumerate(executor.map(fetch_and_analyze, game_ids), 1):
            game_id, game_row, error = result
            if error is not None:
                errors.append({"game_id": game_id, "error": error})
            elif game_row is not None:
                analyzed.append(game_row)
            if index % 100 == 0 or index == len(game_ids):
                print(
                    f"decoded {index}/{len(game_ids)} games; failures={len(errors)}",
                    flush=True,
                )
    rows = [row for game in analyzed for row in game["occurrences"]]
    rank_by_agent = {
        int(agent["agent_id"]): int(agent["rank"])
        for agent in inventory["agents"]
    }
    for row in rows:
        row["leaderboard_rank"] = rank_by_agent[int(row["agent_id"])]
    rows.sort(key=lambda row: (row["leaderboard_rank"], row["game_id"], row["seat"]))
    quality = {
        "requested_unique_games": len(game_ids),
        "decoded_games": len(analyzed),
        "failed_games": len(errors),
        "requested_occurrences": int(inventory["counts"]["listed_finished_occurrences"]),
        "decoded_occurrences": len(rows),
        "unknown_diff_updates": sum(
            int(game["quality"]["unknown_diff_updates"]) for game in analyzed
        ),
        "fetch_or_decode_errors": errors,
    }
    result = {
        "schema": "troll-farm-top15-public-battle-audit-v1",
        "task_id": "20260802-top15-public-battle-audit",
        "generated_at_utc": utc_now(),
        "scope": (
            "descriptive audit of every finished occurrence in the captured public "
            "recent-battle lists for exact current top-15 agent/submission identities"
        ),
        "evidence_boundary": {
            "descriptive_only": True,
            "candidate_qualification": False,
            "causal_claims": False,
            "selection_bias": "recent public matchmaking, unequal games per exact agent",
            "version_boundary": "agentId and submissionId exact within the inventory",
        },
        "inventory_sha256": digest(inventory),
        "quality": quality,
        "summary": build_summary(rows, inventory),
        "rows": rows,
    }
    result["summary_sha256"] = digest(result["summary"])
    return result


def validate_output(payload: dict[str, Any], inventory: dict[str, Any]) -> None:
    if payload.get("schema") != "troll-farm-top15-public-battle-audit-v1":
        raise ValueError("unrecognized audit schema")
    if payload.get("inventory_sha256") != digest(inventory):
        raise ValueError("audit inventory hash mismatch")
    rows = payload.get("rows") or []
    rebuilt = build_summary(rows, inventory)
    if rebuilt != payload.get("summary"):
        raise ValueError("stored summary differs from rebuilt row summary")
    if digest(rebuilt) != payload.get("summary_sha256"):
        raise ValueError("summary hash mismatch")
    if int(payload["quality"]["decoded_occurrences"]) != len(rows):
        raise ValueError("decoded occurrence count mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=12)
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="capture leaderboard and battle-list metadata without fetching replays",
    )
    parser.add_argument(
        "--validate-inventory",
        action="store_true",
        help="validate an existing inventory without network access",
    )
    parser.add_argument(
        "--refresh-inventory",
        action="store_true",
        help="replace the captured inventory before full replay analysis",
    )
    parser.add_argument(
        "--validate-output",
        action="store_true",
        help="rebuild and validate summaries from compact checked-in rows",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 24:
        raise SystemExit("--jobs must be between 1 and 24")
    if args.validate_inventory:
        payload = json.loads(args.inventory.read_text())
        validate_inventory(payload)
        print(json.dumps({"inventory": str(args.inventory), "status": "ok"}))
        return 0
    if args.validate_output:
        inventory = json.loads(args.inventory.read_text())
        validate_inventory(inventory)
        output = json.loads(args.output.read_text())
        validate_output(output, inventory)
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "rows": len(output["rows"]),
                    "summary_sha256": output["summary_sha256"],
                    "status": "ok",
                },
                sort_keys=True,
            )
        )
        return 0
    if args.inventory_only or args.refresh_inventory or not args.inventory.exists():
        inventory = collect_inventory(args.jobs)
        validate_inventory(inventory)
        atomic_json(args.inventory, inventory)
        print(
            json.dumps(
                {
                    "inventory": str(args.inventory),
                    "leaderboard_sha256": inventory["leaderboard"]["response_sha256"],
                    **inventory["counts"],
                },
                sort_keys=True,
            )
        )
    else:
        inventory = json.loads(args.inventory.read_text())
        validate_inventory(inventory)
    if args.inventory_only:
        return 0
    output = run_full(inventory, args.jobs)
    validate_output(output, inventory)
    atomic_json(args.output, output)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "summary_sha256": output["summary_sha256"],
                **{key: value for key, value in output["quality"].items() if key != "fetch_or_decode_errors"},
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
