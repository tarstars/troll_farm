#!/usr/bin/env python3
"""Analyze top-player opening conditions, training funding, and worker output.

This is observational replay archaeology.  It reconstructs exact official states and joins
them to the commands each player issued.  The resulting conditional summaries are intended to
nominate coherent macro options; they do not identify a causal training effect on their own.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from concurrent.futures import as_completed, ProcessPoolExecutor
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import (  # noqa: E402
    action_commands,
    effective_chop_unit_ids,
)
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_macro_census import role_of, spec_label  # noqa: E402

LIVE_AGENT_ID = 6553250
GAMES = REPO / "data/processed/games.jsonl"
TRAJECTORIES = REPO / "data/processed/trajectories"
RAW_GAMES = REPO / "data/raw/games"
LEADERBOARD = REPO / "data/raw/leaderboard.json"

ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
COST_ITEMS = (0, 1, 2, 4)
NEIGHBORS = ((0, 1), (1, 0), (0, -1), (-1, 0))
COMMON_SPECS = (
    (1, 1, 0, 1),
    (1, 1, 1, 1),
    (2, 2, 0, 2),
    (2, 2, 2, 1),
    (2, 2, 2, 2),
    (2, 3, 1, 2),
    (2, 4, 1, 2),
    (3, 4, 0, 3),
)
CONDITIONAL_FEATURES = (
    "initial_plum",
    "initial_lemon",
    "initial_apple",
    "initial_banana",
    "initial_iron",
    "affordable_common_spec_count",
    "tree_total",
    "fruit_total",
    "ripe_tree_count",
    "own_private_tree_count",
    "own_private_fruit",
    "own_near_tree_count",
    "own_near_fruit",
    "water_adjacent_base_cells",
    "own_nearest_tree_distance",
    "own_nearest_iron_distance",
    "shack_door_distance",
)


def mean_or_none(values):
    values = [value for value in values if value is not None]
    return statistics.mean(values) if values else None


def median_or_none(values):
    values = [value for value in values if value is not None]
    return statistics.median(values) if values else None


def score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[5]


def training_cost(n: int, spec) -> list[int]:
    ms, cc, hp, chop = spec
    cost = [0] * 6
    cost[0] = n + ms * ms
    cost[1] = n + cc * cc
    cost[2] = n + hp * hp
    cost[4] = n + chop * chop
    return cost


def affordable(inventory, cost) -> bool:
    return all(inventory[index] >= cost[index] for index in COST_ITEMS)


def read_trajectory(game_id: int) -> list[dict]:
    path = TRAJECTORIES / f"{game_id}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def player_commands(row: dict, player: int) -> list[str]:
    return action_commands(row.get(f"commands{player}"))


def assigned_unit_commands(commands: list[str], units: list[dict]) -> dict[int, str]:
    """Resolve explicit unit ids while retaining positional WAIT slots."""

    unit_ids = sorted(unit["id"] for unit in units)
    assigned = {}
    action_slot = 0
    for command in commands:
        fields = command.split()
        if not fields:
            continue
        verb = fields[0].upper()
        if verb in ("TRAIN", "MSG"):
            continue
        positional_id = unit_ids[action_slot] if action_slot < len(unit_ids) else None
        action_slot += 1
        if verb == "WAIT":
            unit_id = positional_id
        else:
            try:
                unit_id = int(fields[1])
            except (IndexError, ValueError):
                unit_id = positional_id
        if unit_id is not None and unit_id not in assigned:
            assigned[unit_id] = command
    return assigned


def train_specs(commands: list[str]) -> list[list[int]]:
    specs = []
    for command in commands:
        match = re.fullmatch(r"TRAIN\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", command)
        if match:
            specs.append([int(value) for value in match.groups()])
    return specs


def terrain(decoded_map: dict) -> dict:
    walkable = set()
    water = set()
    iron = set()
    shacks = [None, None]
    for y, row in enumerate(decoded_map["rows"]):
        for x, char in enumerate(row):
            cell = (x, y)
            if char == ".":
                walkable.add(cell)
            elif char == "~":
                water.add(cell)
            elif char == "+":
                iron.add(cell)
            elif char in ("0", "1"):
                shacks[int(char)] = cell
    return {"walkable": walkable, "water": water, "iron": iron, "shacks": shacks}


def adjacent(cell):
    return [(cell[0] + dx, cell[1] + dy) for dx, dy in NEIGHBORS]


def bfs(walkable: set[tuple[int, int]], sources) -> dict[tuple[int, int], int]:
    distances = {}
    queue = deque()
    for source in sources:
        if source in walkable and source not in distances:
            distances[source] = 0
            queue.append(source)
    while queue:
        cell = queue.popleft()
        for nxt in adjacent(cell):
            if nxt in walkable and nxt not in distances:
                distances[nxt] = distances[cell] + 1
                queue.append(nxt)
    return distances


def opening_features(decoded_map: dict, initial_state: dict, player: int) -> dict:
    board = terrain(decoded_map)
    own_shack = board["shacks"][player]
    opponent_shack = board["shacks"][1 - player]
    own_doors = [cell for cell in adjacent(own_shack) if cell in board["walkable"]]
    opponent_doors = [
        cell for cell in adjacent(opponent_shack) if cell in board["walkable"]
    ]
    own_distance = bfs(board["walkable"], own_doors)
    opponent_distance = bfs(board["walkable"], opponent_doors)
    inventory = initial_state["inventories"][player]
    n = sum(unit["player"] == player for unit in initial_state["units"])
    plants = initial_state["plants"]

    result = {
        f"initial_{name.lower()}": inventory[index]
        for index, name in enumerate(ITEMS)
    }
    result.update(
        {
            "initial_score": score(inventory),
            "tree_total": len(plants),
            "fruit_total": sum(plant["fruits"] for plant in plants),
            "ripe_tree_count": sum(plant["fruits"] > 0 for plant in plants),
            "tree_health_total": sum(plant["health"] for plant in plants),
            "tree_size_total": sum(plant["size"] for plant in plants),
            "own_door_count": len(own_doors),
            "opponent_door_count": len(opponent_doors),
        }
    )
    for kind in ("PLUM", "LEMON", "APPLE", "BANANA"):
        selected = [plant for plant in plants if plant["type"] == kind]
        prefix = kind.lower()
        result[f"{prefix}_tree_count"] = len(selected)
        result[f"{prefix}_fruit"] = sum(plant["fruits"] for plant in selected)
        result[f"{prefix}_health"] = sum(plant["health"] for plant in selected)
        result[f"{prefix}_size"] = sum(plant["size"] for plant in selected)

    own_private = []
    opponent_private = []
    contested = []
    own_near = []
    for plant in plants:
        cell = (plant["x"], plant["y"])
        own = own_distance.get(cell, 10_000)
        opponent = opponent_distance.get(cell, 10_000)
        if own < opponent:
            own_private.append(plant)
        elif opponent < own:
            opponent_private.append(plant)
        else:
            contested.append(plant)
        if own <= 6:
            own_near.append(plant)
    result.update(
        {
            "own_private_tree_count": len(own_private),
            "own_private_fruit": sum(plant["fruits"] for plant in own_private),
            "opponent_private_tree_count": len(opponent_private),
            "opponent_private_fruit": sum(
                plant["fruits"] for plant in opponent_private
            ),
            "contested_tree_count": len(contested),
            "contested_fruit": sum(plant["fruits"] for plant in contested),
            "own_near_tree_count": len(own_near),
            "own_near_fruit": sum(plant["fruits"] for plant in own_near),
            "own_nearest_tree_distance": min(
                (
                    own_distance.get((plant["x"], plant["y"]), 10_000)
                    for plant in plants
                ),
                default=10_000,
            ),
        }
    )

    water_adjacent = {
        cell
        for cell in board["walkable"]
        if any(neighbor in board["water"] for neighbor in adjacent(cell))
    }
    result["water_adjacent_cells"] = len(water_adjacent)
    result["water_adjacent_base_cells"] = sum(
        own_distance.get(cell, 10_000) <= 4 for cell in water_adjacent
    )
    result["own_nearest_iron_distance"] = min(
        (
            own_distance.get(cell, 10_000)
            for ore in board["iron"]
            for cell in adjacent(ore)
            if cell in board["walkable"]
        ),
        default=10_000,
    )
    result["shack_door_distance"] = min(
        (own_distance.get(cell, 10_000) for cell in opponent_doors),
        default=10_000,
    )

    affordable_specs = []
    for spec in COMMON_SPECS:
        label = spec_label(spec)
        can_afford = affordable(inventory, training_cost(n, spec))
        result[f"affords_{label.replace('/', '_')}"] = can_afford
        if can_afford:
            affordable_specs.append(label)
    result["affordable_common_specs"] = affordable_specs
    result["affordable_common_spec_count"] = len(affordable_specs)
    for index, stat in zip(COST_ITEMS, ("movement", "carry", "harvest", "chop")):
        result[f"max_affordable_{stat}"] = math.isqrt(max(0, inventory[index] - n))
    return result


def new_worker(unit: dict, spawn_turn: int, ordinal: int) -> dict:
    spec = [unit["ms"], unit["cc"], unit["hp"], unit["chop"]]
    return {
        "unit_id": unit["id"],
        "spawn_turn": spawn_turn,
        "ordinal": ordinal,
        "spec": spec,
        "role": "starter" if ordinal == 0 else role_of(spec),
        "commands": Counter(),
        "actual_move_turns": 0,
        "blocked_move_turns": 0,
        "chop_on_tree_turns": 0,
        "material_gained": [0] * 6,
        "material_spent": [0] * 6,
        "harvested": [0] * 6,
        "chopped": [0] * 6,
        "planted": [0] * 6,
        "picked": [0] * 6,
        "mined": [0] * 6,
        "dropped": [0] * 6,
        "direct_banked_value": 0,
        "productive_turns": 0,
        "last_productive_turn": None,
        "drop_value_events": [],
    }


def cargo_delta(before: dict, after: dict | None) -> tuple[list[int], list[int]]:
    if after is None:
        return [0] * 6, [0] * 6
    gained = [max(0, after["carry"][i] - before["carry"][i]) for i in range(6)]
    spent = [max(0, before["carry"][i] - after["carry"][i]) for i in range(6)]
    return gained, spent


def item_dict(values) -> dict:
    return {ITEMS[index]: value for index, value in enumerate(values) if value}


def finalize_worker(
    worker: dict,
    final_turn: int,
    training_event: dict | None,
    final_unit: dict | None,
) -> dict:
    active_turns = max(0, final_turn - worker["spawn_turn"])
    score_cost = training_event["score_cost"] if training_event else 0
    cumulative = 0
    direct_payback_turn = None
    for turn, value in worker["drop_value_events"]:
        cumulative += value
        if score_cost and cumulative >= score_cost and direct_payback_turn is None:
            direct_payback_turn = turn
    return {
        "unit_id": worker["unit_id"],
        "spawn_turn": worker["spawn_turn"],
        "ordinal": worker["ordinal"],
        "spec": worker["spec"],
        "role": worker["role"],
        "active_turns": active_turns,
        "commands": dict(sorted(worker["commands"].items())),
        "actual_move_turns": worker["actual_move_turns"],
        "blocked_move_turns": worker["blocked_move_turns"],
        "chop_on_tree_turns": worker["chop_on_tree_turns"],
        "material_gained": item_dict(worker["material_gained"]),
        "material_spent": item_dict(worker["material_spent"]),
        "harvested": item_dict(worker["harvested"]),
        "chopped": item_dict(worker["chopped"]),
        "planted": item_dict(worker["planted"]),
        "picked": item_dict(worker["picked"]),
        "mined": item_dict(worker["mined"]),
        "dropped": item_dict(worker["dropped"]),
        "final_carry": item_dict(final_unit["carry"] if final_unit else [0] * 6),
        "direct_banked_value": worker["direct_banked_value"],
        "productive_turns": worker["productive_turns"],
        "observed_inactive_turns": active_turns - worker["productive_turns"],
        "last_productive_turn": worker["last_productive_turn"],
        "inactive_tail_turns": (
            final_turn - worker["last_productive_turn"]
            if worker["last_productive_turn"] is not None
            else active_turns
        ),
        "score_cost": score_cost,
        "direct_payback_turn": direct_payback_turn,
        "direct_payback_delay": (
            direct_payback_turn - worker["spawn_turn"]
            if direct_payback_turn is not None
            else None
        ),
    }


def enrich_training_events(
    events: list[dict],
    workers: dict[int, dict],
    states: list[dict],
    action_events: list[dict],
    drop_events: list[dict],
    player: int,
) -> None:
    previous_turn = 0
    for event in events:
        turn = event["turn"]
        cost = event["cost_vector"]
        start_inventory = states[previous_turn]["inventories"][player]
        inventory_before = states[turn - 1]["inventories"][player]
        n_before = event["n_before"]
        max_affordable_spec = [
            math.isqrt(max(0, inventory_before[index] - n_before))
            for index in COST_ITEMS
        ]
        deficits = []
        first_affordable_turn = None
        for state_index in range(previous_turn, turn):
            inventory = states[state_index]["inventories"][player]
            row = [max(0, cost[i] - inventory[i]) for i in range(6)]
            deficits.append((state_index + 1, row))
            if first_affordable_turn is None and affordable(inventory, cost):
                first_affordable_turn = state_index + 1
        closest_turn, closest = min(
            deficits, key=lambda row: (sum(row[1][index] for index in COST_ITEMS), row[0])
        )

        by_worker = defaultdict(
            lambda: {
                "dropped": [0] * 6,
                "material_gained": [0] * 6,
                "commands": Counter(),
            }
        )
        for row in drop_events:
            if previous_turn < row["turn"] < turn:
                target = by_worker[row["unit_id"]]["dropped"]
                for index, value in enumerate(row["items"]):
                    target[index] += value
        for row in action_events:
            if previous_turn < row["turn"] < turn:
                target = by_worker[row["unit_id"]]
                target["commands"][row["verb"]] += 1
                for index, value in enumerate(row["gained"]):
                    target["material_gained"][index] += value

        contributors = []
        for unit_id, row in sorted(by_worker.items()):
            worker = workers.get(unit_id)
            contributors.append(
                {
                    "unit_id": unit_id,
                    "ordinal": worker["ordinal"] if worker else None,
                    "role": worker["role"] if worker else "unknown",
                    "spec": worker["spec"] if worker else None,
                    "dropped": item_dict(row["dropped"]),
                    "material_gained": item_dict(row["material_gained"]),
                    "commands": dict(sorted(row["commands"].items())),
                }
            )
        event.update(
            {
                "funding_window_start_turn": previous_turn + 1,
                "funding_window_start_inventory": list(start_inventory),
                "inventory_before": list(inventory_before),
                "max_affordable_spec": max_affordable_spec,
                "matches_max_affordable_spec": event["spec"] == max_affordable_spec,
                "max_affordable_stat_slack": [
                    available - selected
                    for available, selected in zip(max_affordable_spec, event["spec"])
                ],
                "deficit_at_window_start": item_dict(
                    [max(0, cost[i] - start_inventory[i]) for i in range(6)]
                ),
                "deficit_before_train": item_dict(
                    [max(0, cost[i] - inventory_before[i]) for i in range(6)]
                ),
                "deficit_trajectory": [
                    {"turn": deficit_turn, "deficit": item_dict(deficit)}
                    for deficit_turn, deficit in deficits
                ],
                "closest_deficit_turn": closest_turn,
                "closest_deficit": item_dict(closest),
                "first_affordable_turn": first_affordable_turn,
                "delay_after_affordable": (
                    turn - first_affordable_turn
                    if first_affordable_turn is not None
                    else None
                ),
                "starting_bank_funded": affordable(start_inventory, cost),
                "funding_contributors": contributors,
            }
        )
        pre_score = score(inventory_before)
        recovery_turn = None
        for state_index in range(turn, len(states)):
            if score(states[state_index]["inventories"][player]) >= pre_score:
                recovery_turn = state_index
                break
        event["whole_bank_recovery_turn"] = recovery_turn
        event["whole_bank_recovery_delay"] = (
            recovery_turn - turn if recovery_turn is not None else None
        )
        event["wood_delta_after"] = {
            str(offset): (
                states[turn + offset]["inventories"][player][5] - inventory_before[5]
                if turn + offset < len(states)
                else None
            )
            for offset in (10, 25, 50, 100)
        }
        event["bank_score_delta_after"] = {
            str(offset): (
                score(states[turn + offset]["inventories"][player]) - pre_score
                if turn + offset < len(states)
                else None
            )
            for offset in (0, 10, 25, 50, 100)
        }
        previous_turn = turn


def analyze_players(states: list[dict], trajectory: list[dict]) -> dict[int, dict]:
    usable_turns = min(len(states) - 1, len(trajectory))
    result = {}
    for player in (0, 1):
        initial_units = [
            unit for unit in states[0]["units"] if unit["player"] == player
        ]
        workers = {
            unit["id"]: new_worker(unit, 0, 0) for unit in initial_units
        }
        training_events = []
        action_events = []
        drop_events = []

        for turn in range(1, usable_turns + 1):
            before = states[turn - 1]
            after = states[turn]
            before_units = {
                unit["id"]: unit
                for unit in before["units"]
                if unit["player"] == player
            }
            after_units = {
                unit["id"]: unit
                for unit in after["units"]
                if unit["player"] == player
            }
            commands = player_commands(trajectory[turn - 1], player)
            assigned = assigned_unit_commands(commands, list(before_units.values()))
            before_plants = {
                (plant["x"], plant["y"]): plant for plant in before["plants"]
            }

            for unit_id, unit in before_units.items():
                worker = workers.setdefault(unit_id, new_worker(unit, 0, 0))
                command = assigned.get(unit_id)
                if command is None:
                    continue
                verb = command.split()[0].upper()
                worker["commands"][verb] += 1
                after_unit = after_units.get(unit_id)
                gained, spent = cargo_delta(unit, after_unit)
                for index in range(6):
                    worker["material_gained"][index] += gained[index]
                    worker["material_spent"][index] += spent[index]
                    if verb == "HARVEST":
                        worker["harvested"][index] += gained[index]
                    elif verb == "CHOP":
                        worker["chopped"][index] += gained[index]
                    elif verb == "PLANT":
                        worker["planted"][index] += spent[index]
                    elif verb == "PICK":
                        worker["picked"][index] += gained[index]
                    elif verb == "MINE":
                        worker["mined"][index] += gained[index]
                moved = bool(
                    after_unit
                    and (after_unit["x"], after_unit["y"])
                    != (unit["x"], unit["y"])
                )
                if verb == "MOVE":
                    if moved:
                        worker["actual_move_turns"] += 1
                    else:
                        worker["blocked_move_turns"] += 1
                chop_on_tree = verb == "CHOP" and (
                    unit["x"], unit["y"]
                ) in before_plants
                if chop_on_tree:
                    worker["chop_on_tree_turns"] += 1
                dropped = [0] * 6
                if verb == "DROP":
                    dropped = spent
                    value = sum(dropped[:4]) + 4 * dropped[5]
                    worker["direct_banked_value"] += value
                    worker["drop_value_events"].append((turn, value))
                    for index in range(6):
                        worker["dropped"][index] += dropped[index]
                    drop_events.append(
                        {"turn": turn, "unit_id": unit_id, "items": dropped}
                    )
                productive = moved or chop_on_tree or any(gained) or any(spent)
                if productive:
                    worker["productive_turns"] += 1
                    worker["last_productive_turn"] = turn
                action_events.append(
                    {
                        "turn": turn,
                        "unit_id": unit_id,
                        "verb": verb,
                        "gained": gained,
                        "spent": spent,
                    }
                )

            new_units = [
                unit for unit_id, unit in after_units.items() if unit_id not in before_units
            ]
            requested_specs = train_specs(commands)
            for unit in sorted(new_units, key=lambda row: row["id"]):
                spec = [unit["ms"], unit["cc"], unit["hp"], unit["chop"]]
                ordinal = len(training_events) + 1
                workers[unit["id"]] = new_worker(unit, turn, ordinal)
                n_before = len(before_units)
                cost = training_cost(n_before, spec)
                event = {
                    "ordinal": ordinal,
                    "turn": turn,
                    "new_unit_id": unit["id"],
                    "spec": spec,
                    "role": role_of(spec),
                    "n_before": n_before,
                    "cost": item_dict(cost),
                    "cost_vector": cost,
                    "score_cost": sum(cost[:4]),
                    "requested_specs": requested_specs,
                }
                training_events.append(event)

        enrich_training_events(
            training_events,
            workers,
            states[: usable_turns + 1],
            action_events,
            drop_events,
            player,
        )
        event_by_unit = {event["new_unit_id"]: event for event in training_events}
        final_units = {
            unit["id"]: unit
            for unit in states[usable_turns]["units"]
            if unit["player"] == player
        }
        final_workers = [
            finalize_worker(
                worker,
                usable_turns,
                event_by_unit.get(unit_id),
                final_units.get(unit_id),
            )
            for unit_id, worker in sorted(
                workers.items(), key=lambda item: (item[1]["ordinal"], item[0])
            )
        ]
        planting_by_window = defaultdict(Counter)
        for row in action_events:
            if row["verb"] != "PLANT":
                continue
            turn = row["turn"]
            if turn <= 25:
                window = "1-25"
            elif turn <= 50:
                window = "26-50"
            elif turn <= 100:
                window = "51-100"
            elif turn <= 150:
                window = "101-150"
            else:
                window = "151+"
            planting_by_window[window].update(item_dict(row["spent"]))
        result[player] = {
            "training_events": training_events,
            "workers": final_workers,
            "planting_by_window": {
                window: dict(sorted(counts.items()))
                for window, counts in sorted(planting_by_window.items())
            },
            "usable_turns": usable_turns,
        }
    return result


def command_counts_first(trajectory: list[dict], player: int, turns: int = 5) -> dict:
    counts = Counter()
    for row in trajectory[:turns]:
        counts.update(command.split()[0].upper() for command in player_commands(row, player))
    counts.pop("MSG", None)
    return dict(sorted(counts.items()))


def occurrence(
    game: dict,
    player_row: dict,
    analyses: dict[int, dict],
    decoded: dict,
    trajectory: list[dict],
    rank_by_agent: dict[int, int],
) -> dict:
    player = player_row["index"]
    opponent_row = next(row for row in game["players"] if row["index"] == 1 - player)
    analysis = analyses[player]
    opponent_analysis = analyses[1 - player]
    per_player = game["per_player"][str(player)]
    opening = opening_features(decoded["map"], decoded["states"][0], player)
    first_opponent_train = (
        opponent_analysis["training_events"][0]
        if opponent_analysis["training_events"]
        else None
    )
    specs = [event["spec"] for event in analysis["training_events"]]
    return {
        "game_id": game["gameId"],
        "agent_id": player_row.get("agentId"),
        "name": player_row.get("name"),
        "leaderboard_rank": rank_by_agent.get(player_row.get("agentId")),
        "seat": player,
        "opponent": {
            "agent_id": opponent_row.get("agentId"),
            "name": opponent_row.get("name"),
            "leaderboard_rank": rank_by_agent.get(opponent_row.get("agentId")),
            "first_five_command_counts": command_counts_first(
                trajectory, 1 - player
            ),
            "successful_train_count": len(opponent_analysis["training_events"]),
            "first_train_turn": (
                first_opponent_train["turn"] if first_opponent_train else None
            ),
            "first_train_spec": (
                first_opponent_train["spec"] if first_opponent_train else None
            ),
        },
        "turns": analysis["usable_turns"],
        "score": game["scores"][player],
        "opponent_score": game["scores"][1 - player],
        "margin": game["scores"][player] - game["scores"][1 - player],
        "won": game["scores"][player] > game["scores"][1 - player],
        "opening": opening,
        "first_five_command_counts": command_counts_first(trajectory, player),
        "successful_train_count": len(analysis["training_events"]),
        "final_worker_count": 1 + len(analysis["training_events"]),
        "training_sequence": " -> ".join(spec_label(spec) for spec in specs) or "none",
        "training_events": analysis["training_events"],
        "workers": analysis["workers"],
        "planting_by_window": analysis["planting_by_window"],
        "planted_ok": per_player.get("planted_ok", {}),
        "harvested": per_player.get("harvested", {}),
        "command_counts": per_player.get("commands_summary", {}),
        "final_inventory": per_player.get("final_inv", [0] * 6),
        "final_wood": per_player.get("final_inv", [0] * 6)[5],
        "collected_wood": per_player.get("effects", {}).get("collected_WOOD", 0),
    }


def analyze_game_task(task) -> dict:
    game, selected_ids, rank_by_agent = task
    game_id = game["gameId"]
    trajectory = read_trajectory(game_id)
    commands = [
        [player_commands(row, player) for player in (0, 1)] for row in trajectory
    ]
    chop_ids = [
        effective_chop_unit_ids(turn[0]) + effective_chop_unit_ids(turn[1])
        for turn in commands
    ]
    decoded = decode_replay(
        RAW_GAMES / f"{game_id}.json", chop_unit_ids_by_turn=chop_ids
    )
    analyses = analyze_players(decoded["states"], trajectory)
    selected_players = [
        row for row in game["players"] if row.get("agentId") in selected_ids
    ]
    rows = [
        occurrence(game, row, analyses, decoded, trajectory, rank_by_agent)
        for row in selected_players
    ]
    return {
        "game_id": game_id,
        "occurrences": rows,
        "quality": {
            "decoded_turns": len(decoded["states"]) - 1,
            "trajectory_turns": len(trajectory),
            "unknown_diff_updates": len(decoded["unknown_updates"]),
        },
    }


def numeric_summary(values) -> dict:
    values = [value for value in values if value is not None]
    return {
        "n": len(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
    }


def best_threshold(
    rows: list[dict], feature: str, required_train_count: int = 2
) -> dict | None:
    pairs = [
        (
            row["opening"].get(feature),
            row["successful_train_count"] >= required_train_count,
        )
        for row in rows
    ]
    pairs = [(value, label) for value, label in pairs if value is not None]
    positives = sum(label for _, label in pairs)
    negatives = len(pairs) - positives
    values = sorted({value for value, _ in pairs})
    if positives < 3 or negatives < 3 or len(values) < 2:
        return None
    thresholds = [(left + right) / 2 for left, right in zip(values, values[1:])]
    candidates = []
    for threshold in thresholds:
        for direction in ("above", "below"):
            predicted = [
                value > threshold if direction == "above" else value <= threshold
                for value, _ in pairs
            ]
            true_positive = sum(prediction and label for prediction, (_, label) in zip(predicted, pairs))
            true_negative = sum(not prediction and not label for prediction, (_, label) in zip(predicted, pairs))
            balanced = 0.5 * (true_positive / positives + true_negative / negatives)
            accuracy = (true_positive + true_negative) / len(pairs)
            candidates.append(
                {
                    "threshold": threshold,
                    "multiworker_direction": direction,
                    "balanced_accuracy_in_sample": balanced,
                    "accuracy_in_sample": accuracy,
                }
            )
    return max(
        candidates,
        key=lambda row: (
            row["balanced_accuracy_in_sample"],
            row["accuracy_in_sample"],
            -row["threshold"],
        ),
    )


def feature_contrasts(
    rows: list[dict], required_train_count: int = 2
) -> list[dict]:
    low = [
        row for row in rows if row["successful_train_count"] < required_train_count
    ]
    high = [
        row for row in rows if row["successful_train_count"] >= required_train_count
    ]
    contrasts = []
    for feature in CONDITIONAL_FEATURES:
        low_values = [row["opening"].get(feature) for row in low]
        high_values = [row["opening"].get(feature) for row in high]
        low_values = [value for value in low_values if value is not None]
        high_values = [value for value in high_values if value is not None]
        if not low_values or not high_values:
            continue
        combined = low_values + high_values
        deviation = statistics.pstdev(combined) if len(combined) > 1 else 0
        difference = statistics.mean(high_values) - statistics.mean(low_values)
        contrasts.append(
            {
                "feature": feature,
                "low_train_n": len(low_values),
                "multiworker_n": len(high_values),
                "low_train_mean": statistics.mean(low_values),
                "multiworker_mean": statistics.mean(high_values),
                "difference": difference,
                "standardized_difference": difference / deviation if deviation else 0,
                "best_threshold": best_threshold(
                    rows, feature, required_train_count=required_train_count
                ),
            }
        )
    return sorted(
        contrasts,
        key=lambda row: abs(row["standardized_difference"]),
        reverse=True,
    )


def summarize_workers(rows: list[dict]) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        for worker in row["workers"]:
            grouped[worker["ordinal"]].append(worker)
    result = {}
    for ordinal, workers in sorted(grouped.items()):
        command_totals = Counter()
        role_counts = Counter()
        spec_counts = Counter()
        gained = Counter()
        spent = Counter()
        harvested = Counter()
        chopped = Counter()
        planted = Counter()
        picked = Counter()
        mined = Counter()
        dropped = Counter()
        final_carry = Counter()
        for worker in workers:
            command_totals.update(worker["commands"])
            role_counts[worker["role"]] += 1
            spec_counts[spec_label(worker["spec"])] += 1
            gained.update(worker["material_gained"])
            spent.update(worker["material_spent"])
            harvested.update(worker["harvested"])
            chopped.update(worker["chopped"])
            planted.update(worker["planted"])
            picked.update(worker["picked"])
            mined.update(worker["mined"])
            dropped.update(worker["dropped"])
            final_carry.update(worker["final_carry"])
        total_active = sum(worker["active_turns"] for worker in workers)
        result[str(ordinal)] = {
            "workers": len(workers),
            "roles": dict(role_counts.most_common()),
            "specs": dict(spec_counts.most_common(12)),
            "mean_spawn_turn": mean_or_none(worker["spawn_turn"] for worker in workers),
            "mean_active_turns": mean_or_none(worker["active_turns"] for worker in workers),
            "actual_moves_per_100_active_turns": (
                sum(worker["actual_move_turns"] for worker in workers)
                * 100
                / total_active
                if total_active
                else None
            ),
            "blocked_moves_per_100_active_turns": (
                sum(worker["blocked_move_turns"] for worker in workers)
                * 100
                / total_active
                if total_active
                else None
            ),
            "chop_on_tree_per_100_active_turns": (
                sum(worker["chop_on_tree_turns"] for worker in workers)
                * 100
                / total_active
                if total_active
                else None
            ),
            "productive_per_100_active_turns": (
                sum(worker["productive_turns"] for worker in workers)
                * 100
                / total_active
                if total_active
                else None
            ),
            "observed_inactive_per_100_active_turns": (
                sum(worker["observed_inactive_turns"] for worker in workers)
                * 100
                / total_active
                if total_active
                else None
            ),
            "mean_inactive_tail_turns": mean_or_none(
                worker["inactive_tail_turns"] for worker in workers
            ),
            "commands_per_100_active_turns": {
                command: value * 100 / total_active if total_active else None
                for command, value in sorted(command_totals.items())
            },
            "mean_direct_banked_value": mean_or_none(
                worker["direct_banked_value"] for worker in workers
            ),
            "mean_dropped_wood": mean_or_none(
                worker["dropped"].get("WOOD", 0) for worker in workers
            ),
            "mean_dropped_fruit": mean_or_none(
                sum(worker["dropped"].get(item, 0) for item in ITEMS[:4])
                for worker in workers
            ),
            "mean_dropped_iron": mean_or_none(
                worker["dropped"].get("IRON", 0) for worker in workers
            ),
            "material_gained_total": dict(sorted(gained.items())),
            "material_spent_total": dict(sorted(spent.items())),
            "harvested_total": dict(sorted(harvested.items())),
            "chopped_total": dict(sorted(chopped.items())),
            "planted_total": dict(sorted(planted.items())),
            "picked_total": dict(sorted(picked.items())),
            "mined_total": dict(sorted(mined.items())),
            "material_dropped_total": dict(sorted(dropped.items())),
            "final_carry_total": dict(sorted(final_carry.items())),
            "direct_payback_rate": mean_or_none(
                float(worker["direct_payback_turn"] is not None)
                for worker in workers
                if worker["ordinal"] > 0
            ),
            "median_direct_payback_delay": median_or_none(
                worker["direct_payback_delay"] for worker in workers
            ),
        }
    return result


def summarize_training_events(rows: list[dict]) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        for event in row["training_events"]:
            grouped[event["ordinal"]].append(event)
    result = {}
    for ordinal, events in sorted(grouped.items()):
        costs = Counter()
        start_deficits = Counter()
        contributor_groups = defaultdict(list)
        for event in events:
            costs.update(event["cost"])
            start_deficits.update(event["deficit_at_window_start"])
            contributors_by_ordinal = {
                contributor["ordinal"]: contributor
                for contributor in event["funding_contributors"]
                if contributor["ordinal"] is not None
            }
            for worker_ordinal in range(event["n_before"]):
                contributor_groups[worker_ordinal].append(
                    contributors_by_ordinal.get(worker_ordinal)
                )

        funding_by_worker_ordinal = {}
        for worker_ordinal, contributors in sorted(contributor_groups.items()):
            present = [row for row in contributors if row is not None]
            commands = Counter()
            dropped = Counter()
            gained = Counter()
            for contributor in present:
                commands.update(contributor["commands"])
                dropped.update(contributor["dropped"])
                gained.update(contributor["material_gained"])
            funding_by_worker_ordinal[str(worker_ordinal)] = {
                "eligible_events": len(contributors),
                "active_in_window_rate": len(present) / len(contributors),
                "commands_per_event": {
                    command: value / len(contributors)
                    for command, value in sorted(commands.items())
                },
                "dropped_per_event": {
                    item: dropped[item] / len(contributors)
                    for item in ITEMS
                    if dropped[item]
                },
                "material_gained_per_event": {
                    item: gained[item] / len(contributors)
                    for item in ITEMS
                    if gained[item]
                },
            }

        result[str(ordinal)] = {
            "events": len(events),
            "median_turn": median_or_none(event["turn"] for event in events),
            "mean_funding_window_turns": mean_or_none(
                event["turn"] - event["funding_window_start_turn"]
                for event in events
            ),
            "specs": dict(Counter(spec_label(event["spec"]) for event in events).most_common(12)),
            "roles": dict(Counter(event["role"] for event in events).most_common()),
            "max_affordable_spec_match_rate": mean_or_none(
                float(event["matches_max_affordable_spec"]) for event in events
            ),
            "mean_max_affordable_stat_slack": {
                stat: mean_or_none(
                    event["max_affordable_stat_slack"][index] for event in events
                )
                for index, stat in enumerate(
                    ("movement", "carry", "harvest", "chop")
                )
            },
            "mean_cost": {
                item: costs[item] / len(events) for item in ITEMS if costs[item]
            },
            "mean_deficit_at_window_start": {
                item: start_deficits[item] / len(events)
                for item in ITEMS
                if start_deficits[item]
            },
            "starting_bank_funded_rate": mean_or_none(
                float(event["starting_bank_funded"]) for event in events
            ),
            "median_delay_after_affordable": median_or_none(
                event["delay_after_affordable"] for event in events
            ),
            "whole_bank_recovery_rate": mean_or_none(
                float(event["whole_bank_recovery_turn"] is not None)
                for event in events
            ),
            "median_whole_bank_recovery_delay": median_or_none(
                event["whole_bank_recovery_delay"] for event in events
            ),
            "bank_score_delta_after": {
                str(offset): numeric_summary(
                    event["bank_score_delta_after"][str(offset)] for event in events
                )
                for offset in (0, 10, 25, 50, 100)
            },
            "wood_delta_after": {
                str(offset): numeric_summary(
                    event["wood_delta_after"][str(offset)] for event in events
                )
                for offset in (10, 25, 50, 100)
            },
            "funding_by_worker_ordinal": funding_by_worker_ordinal,
        }
    return result


def summarize_agent(rows: list[dict]) -> dict:
    sequences = Counter(row["training_sequence"] for row in rows)
    train_counts = Counter(row["successful_train_count"] for row in rows)
    first_events = [row["training_events"][0] for row in rows if row["training_events"]]
    planted_totals = Counter()
    planted_by_window = defaultdict(Counter)
    for row in rows:
        planted_totals.update(row["planted_ok"])
        for window, counts in row["planting_by_window"].items():
            planted_by_window[window].update(counts)
    return {
        "appearances": len(rows),
        "successful_train_count_distribution": dict(sorted(train_counts.items())),
        "mean_successful_trains": mean_or_none(
            row["successful_train_count"] for row in rows
        ),
        "multiworker_rate": mean_or_none(
            float(row["successful_train_count"] >= 2) for row in rows
        ),
        "median_first_train_turn": median_or_none(
            event["turn"] for event in first_events
        ),
        "first_train_specs": dict(
            Counter(spec_label(event["spec"]) for event in first_events).most_common(15)
        ),
        "training_sequences": dict(sequences.most_common(15)),
        "mean_planted_per_game": {
            kind: planted_totals[kind] / len(rows) if rows else None
            for kind in sorted(planted_totals)
        },
        "mean_planted_by_window": {
            window: {
                item: counts[item] / len(rows)
                for item in ITEMS[:4]
                if counts[item]
            }
            for window, counts in sorted(planted_by_window.items())
        },
        "mean_final_wood": mean_or_none(row["final_wood"] for row in rows),
        "mean_score": mean_or_none(row["score"] for row in rows),
        "mean_margin": mean_or_none(row["margin"] for row in rows),
        "win_rate": mean_or_none(float(row["won"]) for row in rows),
        "opening_by_train_count": {
            str(count): {
                feature: numeric_summary(
                    row["opening"].get(feature)
                    for row in rows
                    if row["successful_train_count"] == count
                )
                for feature in CONDITIONAL_FEATURES
            }
            for count in sorted(train_counts)
        },
        "multiworker_feature_contrasts": feature_contrasts(rows),
        "stage_feature_contrasts": {
            str(required): feature_contrasts(rows, required)
            for required in range(1, max(train_counts, default=0) + 1)
            if sum(count < required for count in train_counts.elements()) >= 3
            and sum(count >= required for count in train_counts.elements()) >= 3
        },
        "workers_by_ordinal": summarize_workers(rows),
        "training_events_by_ordinal": summarize_training_events(rows),
    }


def summarize_cohort(rows: list[dict]) -> dict:
    return summarize_agent(rows)


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument("--games", type=int, default=0, help="0 means all selected games")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.json",
    )
    args = parser.parse_args()
    if args.jobs < 1:
        raise SystemExit("--jobs must be positive")
    if args.games < 0:
        raise SystemExit("--games cannot be negative")

    leaderboard = json.loads(LEADERBOARD.read_text())["users"]
    legend = [
        row for row in leaderboard if row.get("league", {}).get("divisionIndex") == 5
    ]
    top20 = legend[:20]
    top5_ids = {row["agentId"] for row in legend[:5]}
    top20_ids = {row["agentId"] for row in top20}
    selected_ids = top20_ids | {LIVE_AGENT_ID}
    rank_by_agent = {row["agentId"]: row["rank"] for row in leaderboard}
    profile_by_agent = {
        row["agentId"]: {"name": row["pseudo"], "rank": row["rank"]}
        for row in leaderboard
        if row["agentId"] in selected_ids
    }
    games = [json.loads(line) for line in GAMES.read_text().splitlines() if line.strip()]
    games = [
        game
        for game in games
        if any(row.get("agentId") in selected_ids for row in game["players"])
    ]
    games.sort(key=lambda row: row["gameId"])
    if args.games:
        games = games[: args.games]

    tasks = [(game, selected_ids, rank_by_agent) for game in games]
    analyzed = []
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(analyze_game_task, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), 1):
            analyzed.append(future.result())
            if completed % 25 == 0 or completed == len(futures):
                print(f"completed {completed}/{len(futures)} games", flush=True)

    analyzed.sort(key=lambda row: row["game_id"])
    occurrences = sorted(
        [row for game in analyzed for row in game["occurrences"]],
        key=lambda row: (row["leaderboard_rank"] or 10_000, row["game_id"], row["seat"]),
    )
    individual = {}
    for agent_id, profile in sorted(
        profile_by_agent.items(), key=lambda item: item[1]["rank"]
    ):
        rows = [row for row in occurrences if row["agent_id"] == agent_id]
        individual[str(agent_id)] = {**profile, "summary": summarize_agent(rows)}

    payload = {
        "schema": 1,
        "scope": (
            "observational official replay states joined to commands; per-agent conditional "
            "opening, funding, and worker-output archaeology; not causal policy evidence"
        ),
        "selected_game_count": len(analyzed),
        "occurrence_count": len(occurrences),
        "top5_agent_ids": sorted(top5_ids),
        "top20_agent_ids": sorted(top20_ids),
        "quality": {
            "turn_count_matches": sum(
                row["quality"]["decoded_turns"] == row["quality"]["trajectory_turns"]
                for row in analyzed
            ),
            "games": len(analyzed),
            "unknown_diff_updates": sum(
                row["quality"]["unknown_diff_updates"] for row in analyzed
            ),
        },
        "cohorts": {
            "top5": summarize_cohort(
                [row for row in occurrences if row["agent_id"] in top5_ids]
            ),
            "top20": summarize_cohort(
                [row for row in occurrences if row["agent_id"] in top20_ids]
            ),
            "live": summarize_cohort(
                [row for row in occurrences if row["agent_id"] == LIVE_AGENT_ID]
            ),
        },
        "individual": individual,
        "occurrences": occurrences,
    }
    save(args.output, payload)
    print(
        json.dumps(
            {
                "games": len(analyzed),
                "occurrences": len(occurrences),
                "quality": payload["quality"],
                "top5": {
                    key: payload["cohorts"]["top5"][key]
                    for key in (
                        "mean_successful_trains",
                        "multiworker_rate",
                        "median_first_train_turn",
                        "mean_final_wood",
                    )
                },
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
