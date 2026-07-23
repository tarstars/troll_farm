#!/usr/bin/env python3
"""Diagnose the farm-first macro option on reused local discovery seeds.

This study is intentionally a mechanism gate, not an arena predictor.  It runs
the complete option against the frozen opponent zoo in both seats, attaches the
already-computed exact-live outcomes for the same cells, and records why each
opening did or did not scale:

* target costs, per-resource deficits, affordability, and train success;
* deposits and productive effects by worker and option stage;
* candidate-planted supply, creation geometry, and later capture by either side;
* whole-bank recovery, command displacement, handoff, and final outcome.

Only reused discovery seeds should be supplied while the option is changing.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
import json
import math
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import ITEM_INDEX, ITEM_NAMES, bfs_distances, training_cost  # noqa: E402
from cgauto.idle_harvest_study import (  # noqa: E402
    BotSession,
    action_commands,
    compile_source,
)
from cgauto.offline_policy_league import (  # noqa: E402
    OPPONENT_SOURCES,
    aggregate,
    combine_counts,
    map_features,
    paired_row as outcome_paired_row,
    robust_summary,
    source_sha256,
)
from sim.engine import has_stalled, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402


CANDIDATE_SOURCE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-farm-first-orchard-option.min.rs"
)
CONTROL_LEAGUE = (
    REPO / "data/analysis/live-agent-6553250/offline-policy-league-2026-07-16.json"
)
DEFAULT_OUTPUT = (
    REPO / "data/analysis/live-agent-6553250/farm-first-option-study-2026-07-17.json"
)

FUNDING_SLOTS = (
    ITEM_INDEX["PLUM"],
    ITEM_INDEX["LEMON"],
    ITEM_INDEX["APPLE"],
    ITEM_INDEX["IRON"],
)
STAGE_NAMES = {
    1: "entry_farmer",
    2: "fund_first_chopper",
    3: "fund_second_chopper",
    4: "scaled_four_workers",
}
ROLE_NAMES = ("starter", "farmer", "first_chopper", "second_chopper")


def integer_farmer_level(inventory: int, cap: int) -> int:
    """Replay-derived ``min(cap, isqrt(inventory - 1))``, bounded at one."""

    return min(cap, max(1, math.isqrt(max(inventory - 1, 0))))


def farmer_spec(inventory: list[int]) -> tuple[int, int, int, int]:
    return (
        integer_farmer_level(inventory[ITEM_INDEX["PLUM"]], 2),
        integer_farmer_level(inventory[ITEM_INDEX["LEMON"]], 3),
        integer_farmer_level(inventory[ITEM_INDEX["APPLE"]], 2),
        1,
    )


def stage_target(unit_count: int, inventory: list[int]) -> dict | None:
    """Return the exact target used by the current diagnostic option."""

    if unit_count == 1:
        stats = farmer_spec(inventory)
        deadline = 1
        role = "farmer"
    elif unit_count == 2:
        stats = (2, 2, 0, 2)
        deadline = 100
        role = "first_chopper"
    elif unit_count == 3:
        stats = (2, 2, 0, 2)
        deadline = 180
        role = "second_chopper"
    else:
        return None
    return {
        "unit_count": unit_count,
        "stage": STAGE_NAMES[unit_count],
        "role": role,
        "stats": list(stats),
        "cost": training_cost(unit_count, stats),
        "deadline": deadline,
    }


def funding_deficit(inventory: list[int], cost: list[int]) -> list[int]:
    return [max(cost[index] - inventory[index], 0) for index in range(len(ITEM_NAMES))]


def bank_score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[ITEM_INDEX["WOOD"]]


def parse_command(command: str) -> dict:
    """Parse one already-split action line into a telemetry-friendly record."""

    parts = command.split()
    if not parts:
        return {"verb": "WAIT", "raw": command}
    verb = parts[0].upper()
    record: dict = {"verb": verb, "raw": command}
    if verb == "TRAIN" and len(parts) >= 5:
        record["stats"] = [int(value) for value in parts[1:5]]
    elif verb not in {"WAIT", "MSG"} and len(parts) >= 2:
        record["unit_id"] = int(parts[1])
        if verb == "MOVE" and len(parts) >= 4:
            record["target"] = [int(parts[2]), int(parts[3])]
        elif verb in {"PICK", "PLANT"} and len(parts) >= 3:
            record["kind"] = parts[2].upper()
    return record


def unit_record(unit) -> dict:
    return {
        "id": unit.id,
        "player": unit.player,
        "pos": unit.pos,
        "stats": [unit.ms, unit.cc, unit.hp, unit.chop],
        "carry": list(unit.carry),
    }


def plant_record(plant) -> dict:
    return {
        "kind": plant.type,
        "pos": plant.pos,
        "size": plant.size,
        "health": plant.health,
        "fruits": plant.fruits,
        "cooldown": plant.cooldown,
    }


def stage_name(unit_count: int) -> str:
    return STAGE_NAMES.get(min(unit_count, 4), "scaled_four_workers")


def empty_worker_metrics(unit, spawn_turn: int) -> dict:
    return {
        "id": unit.id,
        "spawn_turn": spawn_turn,
        "stats": [unit.ms, unit.cc, unit.hp, unit.chop],
        "commands": Counter(),
        "successful_actions": Counter(),
        "blocked_actions": Counter(),
        "material_gains": Counter(),
        "deposits": Counter(),
        "plants": Counter(),
        "stage_commands": defaultdict(Counter),
        "stage_successes": defaultdict(Counter),
        "moved_cells_manhattan": 0,
    }


def geometry_label(own_distance: int, opponent_distance: int) -> str:
    if own_distance + 2 <= opponent_distance:
        return "candidate_favored"
    if opponent_distance + 2 <= own_distance:
        return "opponent_favored"
    return "contested"


def _nearest_unit_eta(game, player: int, cell: tuple[int, int]) -> int | None:
    distances = bfs_distances(game.walkable, [cell])
    etas = [
        math.ceil(distances[unit.pos] / max(unit.ms, 1))
        for unit in game.units
        if unit.player == player and unit.pos in distances
    ]
    return min(etas, default=None)


def new_supply_episode(
    game,
    candidate_seat: int,
    turn: int,
    cell: tuple[int, int],
    kind: str,
    planter_ids: list[int],
    joint_plant: bool,
) -> dict:
    own_distances = bfs_distances(game.walkable, [game.shacks[candidate_seat]])
    opponent_distances = bfs_distances(game.walkable, [game.shacks[1 - candidate_seat]])
    own_distance = own_distances.get(cell, 9_999)
    opponent_distance = opponent_distances.get(cell, 9_999)
    return {
        "turn": turn,
        "cell": list(cell),
        "kind": kind,
        "planter_ids": sorted(planter_ids),
        "joint_plant": joint_plant,
        "candidate_shack_distance": own_distance,
        "opponent_shack_distance": opponent_distance,
        "candidate_unit_eta": _nearest_unit_eta(game, candidate_seat, cell),
        "opponent_unit_eta": _nearest_unit_eta(game, 1 - candidate_seat, cell),
        "geometry": geometry_label(own_distance, opponent_distance),
        "harvested_fruit": [0, 0],
        "chop_hits": [0, 0],
        "wood_captured": [0, 0],
        "fell_players": [],
        "removed_turn": None,
    }


def _serialise_worker(metrics: dict, role: str, terminal_turn: int) -> dict:
    active = sum(metrics["successful_actions"].values())
    issued = sum(metrics["commands"].values())
    return {
        "id": metrics["id"],
        "role": role,
        "spawn_turn": metrics["spawn_turn"],
        "lifetime_turns": max(terminal_turn - metrics["spawn_turn"] + 1, 0),
        "stats": metrics["stats"],
        "commands": dict(sorted(metrics["commands"].items())),
        "successful_actions": dict(sorted(metrics["successful_actions"].items())),
        "blocked_actions": dict(sorted(metrics["blocked_actions"].items())),
        "material_gains": dict(sorted(metrics["material_gains"].items())),
        "deposits": dict(sorted(metrics["deposits"].items())),
        "plants": dict(sorted(metrics["plants"].items())),
        "stage_commands": {
            stage: dict(sorted(counts.items()))
            for stage, counts in sorted(metrics["stage_commands"].items())
        },
        "stage_successes": {
            stage: dict(sorted(counts.items()))
            for stage, counts in sorted(metrics["stage_successes"].items())
        },
        "issued_actions": issued,
        "successful_action_turns": active,
        "success_fraction": active / issued if issued else None,
        "moved_cells_manhattan": metrics["moved_cells_manhattan"],
    }


def summarise_supply(episodes: list[dict], candidate_seat: int) -> dict:
    by_kind = Counter(episode["kind"] for episode in episodes)
    geometry = Counter(episode["geometry"] for episode in episodes)
    own = candidate_seat
    opponent = 1 - candidate_seat
    return {
        "created_trees": len(episodes),
        "by_kind": dict(sorted(by_kind.items())),
        "geometry": dict(sorted(geometry.items())),
        "joint_plants": sum(episode["joint_plant"] for episode in episodes),
        "removed_trees": sum(episode["removed_turn"] is not None for episode in episodes),
        "surviving_trees": sum(episode["removed_turn"] is None for episode in episodes),
        "candidate_harvested_fruit": sum(
            episode["harvested_fruit"][own] for episode in episodes
        ),
        "opponent_harvested_fruit": sum(
            episode["harvested_fruit"][opponent] for episode in episodes
        ),
        "candidate_wood_captured": sum(
            episode["wood_captured"][own] for episode in episodes
        ),
        "opponent_wood_captured": sum(
            episode["wood_captured"][opponent] for episode in episodes
        ),
        "opponent_touched_trees": sum(
            episode["harvested_fruit"][opponent] > 0
            or episode["chop_hits"][opponent] > 0
            for episode in episodes
        ),
    }


def handoff_reason(successful_trains: int, terminal_turn: int) -> str:
    if successful_trains >= 3:
        return "scaled"
    if successful_trains == 0:
        return "farmer_not_trained"
    if successful_trains == 1:
        return "first_chopper_timeout" if terminal_turn >= 100 else "terminal_before_first_deadline"
    return "second_chopper_timeout" if terminal_turn >= 180 else "terminal_before_second_deadline"


def trace_match(game, binary0: Path, binary1: Path, candidate_seat: int) -> dict:
    """Run one game and externally observe the complete candidate option."""

    sessions = [BotSession(binary0, game, 0), BotSession(binary1, game, 1)]
    command_counts = [Counter(), Counter()]
    candidate_workers: dict[int, dict] = {}
    for unit in game.units:
        if unit.player == candidate_seat:
            candidate_workers[unit.id] = empty_worker_metrics(unit, 1)

    funding: dict[int, dict] = {}
    training_events: list[dict] = []
    bank_samples: list[dict] = []
    supply_episodes: list[dict] = []
    active_supply: dict[tuple[int, int], dict] = {}
    initial_inventory = list(game.inventories[candidate_seat])
    initial_bank_score = bank_score(initial_inventory)
    last_sampled_unit_count = None
    turns_until_end = 0
    ended_by_stall = False

    try:
        while game.turn <= 300:
            turn = game.turn
            pre_units = {unit.id: unit_record(unit) for unit in game.units}
            pre_plants = {plant.pos: plant_record(plant) for plant in game.plants}
            pre_inventories = copy.deepcopy(game.inventories)
            own_units = [unit for unit in game.units if unit.player == candidate_seat]
            own_count = len(own_units)
            current_stage = stage_name(own_count)

            target = stage_target(own_count, pre_inventories[candidate_seat])
            current_deficit = None
            if target is not None:
                tracker = funding.get(own_count)
                if tracker is None:
                    tracker = copy.deepcopy(target)
                    tracker.update(
                        {
                            "first_observed_turn": turn,
                            "initial_bank": list(pre_inventories[candidate_seat]),
                            "initial_deficit": funding_deficit(
                                pre_inventories[candidate_seat], target["cost"]
                            ),
                            "minimum_total_deficit": None,
                            "first_bank_affordable_turn": None,
                            "first_ready_turn": None,
                            "deadline_deficit": None,
                            "last_observed_turn": turn,
                            "last_bank": list(pre_inventories[candidate_seat]),
                            "last_deficit": None,
                            "trained_turn": None,
                        }
                    )
                    funding[own_count] = tracker
                current_deficit = funding_deficit(
                    pre_inventories[candidate_seat], tracker["cost"]
                )
                total_deficit = sum(current_deficit[index] for index in FUNDING_SLOTS)
                tracker["minimum_total_deficit"] = (
                    total_deficit
                    if tracker["minimum_total_deficit"] is None
                    else min(tracker["minimum_total_deficit"], total_deficit)
                )
                tracker["last_observed_turn"] = turn
                tracker["last_bank"] = list(pre_inventories[candidate_seat])
                tracker["last_deficit"] = current_deficit
                if total_deficit == 0 and tracker["first_bank_affordable_turn"] is None:
                    tracker["first_bank_affordable_turn"] = turn
                shack_free = all(unit.pos != game.shacks[candidate_seat] for unit in own_units)
                if total_deficit == 0 and shack_free and tracker["first_ready_turn"] is None:
                    tracker["first_ready_turn"] = turn
                if turn == tracker["deadline"]:
                    tracker["deadline_deficit"] = current_deficit

            for event in training_events:
                inventory = pre_inventories[candidate_seat]
                if event["bank_score_recovery_turn"] is None and bank_score(inventory) >= event[
                    "bank_score_before"
                ]:
                    event["bank_score_recovery_turn"] = turn
                if event["vector_recovery_turn"] is None and all(
                    inventory[index] >= event["bank_before"][index]
                    for index in FUNDING_SLOTS
                ):
                    event["vector_recovery_turn"] = turn

            if turn == 1 or turn % 10 == 0 or own_count != last_sampled_unit_count:
                bank_samples.append(
                    {
                        "turn": turn,
                        "unit_count": own_count,
                        "stage": current_stage,
                        "bank": list(pre_inventories[candidate_seat]),
                        "bank_score": bank_score(pre_inventories[candidate_seat]),
                        "score": game.scores[candidate_seat],
                        "tree_count": len(game.plants),
                        "target_deficit": current_deficit,
                    }
                )
                last_sampled_unit_count = own_count

            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            parsed = [[parse_command(command) for command in actions] for actions in commands]
            for player in (0, 1):
                command_counts[player].update(
                    record["verb"] for record in parsed[player] if record["verb"] != "MSG"
                )

            for record in parsed[candidate_seat]:
                unit_id = record.get("unit_id")
                if unit_id is None or unit_id not in candidate_workers:
                    continue
                metrics = candidate_workers[unit_id]
                metrics["commands"][record["verb"]] += 1
                metrics["stage_commands"][current_stage][record["verb"]] += 1

            step(game, commands[0], commands[1])

            post_units = {unit.id: unit_record(unit) for unit in game.units}
            post_plants = {plant.pos: plant_record(plant) for plant in game.plants}
            new_candidate_units = [
                unit
                for unit in game.units
                if unit.player == candidate_seat and unit.id not in pre_units
            ]
            new_candidate_units.sort(key=lambda unit: unit.id)

            train_requests = [
                record for record in parsed[candidate_seat] if record["verb"] == "TRAIN"
            ]
            for request_index, request in enumerate(train_requests):
                spec = request.get("stats", [])
                cost = training_cost(own_count, tuple(spec)) if len(spec) == 4 else [0] * 6
                new_unit = (
                    new_candidate_units[request_index]
                    if request_index < len(new_candidate_units)
                    else None
                )
                event = {
                    "turn": turn,
                    "unit_count_before": own_count,
                    "role": ROLE_NAMES[min(own_count, len(ROLE_NAMES) - 1)],
                    "stats": spec,
                    "cost": cost,
                    "bank_before": list(pre_inventories[candidate_seat]),
                    "deficit_before": funding_deficit(
                        pre_inventories[candidate_seat], cost
                    ),
                    "success": new_unit is not None,
                    "new_unit_id": new_unit.id if new_unit is not None else None,
                    "bank_score_before": bank_score(pre_inventories[candidate_seat]),
                    "bank_score_recovery_turn": None,
                    "vector_recovery_turn": None,
                }
                training_events.append(event)
                if new_unit is not None:
                    candidate_workers[new_unit.id] = empty_worker_metrics(new_unit, turn)
                    if own_count in funding:
                        funding[own_count]["trained_turn"] = turn

            # Attribute command effects from exact before/after unit state.
            for player in (0, 1):
                for record in parsed[player]:
                    unit_id = record.get("unit_id")
                    if unit_id is None:
                        continue
                    before = pre_units.get(unit_id)
                    after = post_units.get(unit_id)
                    if before is None or after is None:
                        continue
                    verb = record["verb"]
                    gains = [
                        max(after["carry"][index] - before["carry"][index], 0)
                        for index in range(len(ITEM_NAMES))
                    ]
                    cell = tuple(before["pos"])
                    episode = active_supply.get(cell)
                    success = False
                    if verb == "MOVE":
                        success = before["pos"] != after["pos"]
                    elif verb == "HARVEST":
                        harvested = sum(gains[:4])
                        success = harvested > 0
                        if episode is not None:
                            episode["harvested_fruit"][player] += harvested
                    elif verb == "CHOP":
                        plant_before = pre_plants.get(cell)
                        plant_after = post_plants.get(cell)
                        success = plant_before is not None and (
                            plant_after is None
                            or plant_after["health"] < plant_before["health"]
                        )
                        if episode is not None and success:
                            episode["chop_hits"][player] += 1
                            episode["wood_captured"][player] += gains[ITEM_INDEX["WOOD"]]
                            if plant_after is None:
                                episode["fell_players"].append(player)
                    elif verb == "MINE":
                        success = gains[ITEM_INDEX["IRON"]] > 0
                    elif verb == "PICK":
                        kind = record.get("kind")
                        success = bool(kind) and gains[ITEM_INDEX[kind]] > 0
                    elif verb == "DROP":
                        success = sum(before["carry"]) > sum(after["carry"])
                    elif verb == "PLANT":
                        kind = record.get("kind")
                        success = (
                            kind is not None
                            and cell not in pre_plants
                            and cell in post_plants
                            and post_plants[cell]["kind"] == kind
                            and after["carry"][ITEM_INDEX[kind]]
                            < before["carry"][ITEM_INDEX[kind]]
                        )

                    if player != candidate_seat or unit_id not in candidate_workers:
                        continue
                    metrics = candidate_workers[unit_id]
                    if success:
                        metrics["successful_actions"][verb] += 1
                        metrics["stage_successes"][current_stage][verb] += 1
                    elif verb not in {"WAIT", "MSG"}:
                        metrics["blocked_actions"][verb] += 1
                    for index, amount in enumerate(gains):
                        if amount:
                            metrics["material_gains"][ITEM_NAMES[index]] += amount
                    if verb == "DROP" and success:
                        for index, amount in enumerate(before["carry"]):
                            if amount:
                                metrics["deposits"][ITEM_NAMES[index]] += amount
                    if verb == "PLANT" and success:
                        metrics["plants"][record["kind"]] += 1
                    if verb == "MOVE" and success:
                        metrics["moved_cells_manhattan"] += abs(
                            before["pos"][0] - after["pos"][0]
                        ) + abs(before["pos"][1] - after["pos"][1])

            # Close old candidate-created supply before registering new trees.
            for cell, episode in list(active_supply.items()):
                if cell not in post_plants:
                    episode["removed_turn"] = turn
                    del active_supply[cell]

            candidate_plant_intents: dict[tuple[int, int], list[dict]] = defaultdict(list)
            opponent_plant_intents: dict[tuple[int, int], list[dict]] = defaultdict(list)
            for player, target in (
                (candidate_seat, candidate_plant_intents),
                (1 - candidate_seat, opponent_plant_intents),
            ):
                for record in parsed[player]:
                    if record["verb"] != "PLANT" or "unit_id" not in record:
                        continue
                    before = pre_units.get(record["unit_id"])
                    if before is not None:
                        target[tuple(before["pos"])].append(record)

            for cell, intents in candidate_plant_intents.items():
                if cell in pre_plants or cell not in post_plants or cell in active_supply:
                    continue
                kind = post_plants[cell]["kind"]
                successful = [intent for intent in intents if intent.get("kind") == kind]
                if not successful:
                    continue
                episode = new_supply_episode(
                    game,
                    candidate_seat,
                    turn,
                    cell,
                    kind,
                    [intent["unit_id"] for intent in successful],
                    any(
                        intent.get("kind") == kind
                        for intent in opponent_plant_intents.get(cell, [])
                    ),
                )
                supply_episodes.append(episode)
                active_supply[cell] = episode

            ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
            if ended_by_stall:
                break
    finally:
        stderrs = [session.close() for session in sessions]

    if any(stderr.strip() for stderr in stderrs):
        # Keep bounded diagnostics without making benign debug output fatal.
        stderr_tail = [stderr[-2_000:] for stderr in stderrs]
    else:
        stderr_tail = ["", ""]

    terminal_turn = game.turn - 1
    successful_trains = [event for event in training_events if event["success"]]
    ordered_workers = sorted(
        candidate_workers.values(), key=lambda metrics: (metrics["spawn_turn"], metrics["id"])
    )
    workers = [
        _serialise_worker(
            metrics,
            ROLE_NAMES[index] if index < len(ROLE_NAMES) else f"worker_{index + 1}",
            terminal_turn,
        )
        for index, metrics in enumerate(ordered_workers)
    ]
    for tracker in funding.values():
        if tracker["deadline_deficit"] is None and tracker["last_observed_turn"] >= tracker[
            "deadline"
        ]:
            tracker["deadline_deficit"] = tracker["last_deficit"]
        tracker["limiting_resources_at_end"] = [
            ITEM_NAMES[index]
            for index in FUNDING_SLOTS
            if tracker["last_deficit"][index] > 0
        ]

    return {
        "scores": list(game.scores),
        "inventories": copy.deepcopy(game.inventories),
        "command_counts": [dict(sorted(counts.items())) for counts in command_counts],
        "terminal_turn": terminal_turn,
        "ended_by_stall": ended_by_stall,
        "option": {
            "candidate_seat": candidate_seat,
            "initial_inventory": initial_inventory,
            "initial_bank_score": initial_bank_score,
            "final_unit_count": len(
                [unit for unit in game.units if unit.player == candidate_seat]
            ),
            "handoff_reason": handoff_reason(len(successful_trains), terminal_turn),
            "training_events": training_events,
            "funding_stages": [funding[key] for key in sorted(funding)],
            "bank_samples": bank_samples,
            "workers": workers,
            "supply": summarise_supply(supply_episodes, candidate_seat),
            "supply_episodes": supply_episodes,
            "stderr_tail": stderr_tail[candidate_seat],
        },
    }


def paired_row(
    seed: int,
    initial,
    opponent_name: str,
    candidate: Path,
    opponent: Path,
) -> dict:
    first = trace_match(copy.deepcopy(initial), candidate, opponent, 0)
    second = trace_match(copy.deepcopy(initial), opponent, candidate, 1)
    margins = [
        first["scores"][0] - first["scores"][1],
        second["scores"][1] - second["scores"][0],
    ]
    wood_edges = [
        first["inventories"][0][ITEM_INDEX["WOOD"]]
        - first["inventories"][1][ITEM_INDEX["WOOD"]],
        second["inventories"][1][ITEM_INDEX["WOOD"]]
        - second["inventories"][0][ITEM_INDEX["WOOD"]],
    ]
    return {
        "seed": seed,
        "policy": "farmfirst",
        "opponent": opponent_name,
        "seat_margins": margins,
        "paired_margin": statistics.mean(margins),
        "seat_wood_edges": wood_edges,
        "paired_wood_edge": statistics.mean(wood_edges),
        "policy_scores": [first["scores"][0], second["scores"][1]],
        "opponent_scores": [first["scores"][1], second["scores"][0]],
        "policy_wood": [
            first["inventories"][0][ITEM_INDEX["WOOD"]],
            second["inventories"][1][ITEM_INDEX["WOOD"]],
        ],
        "opponent_wood": [
            first["inventories"][1][ITEM_INDEX["WOOD"]],
            second["inventories"][0][ITEM_INDEX["WOOD"]],
        ],
        "policy_command_counts": combine_counts(
            first["command_counts"][0], second["command_counts"][1]
        ),
        "opponent_command_counts": combine_counts(
            first["command_counts"][1], second["command_counts"][0]
        ),
        "terminal_turns": [first["terminal_turn"], second["terminal_turn"]],
        "map_features": map_features(initial),
        "option_games": [first["option"], second["option"]],
    }


def command_delta(candidate: dict, control: dict) -> dict:
    verbs = sorted(
        set(candidate["policy_command_counts"]) | set(control["policy_command_counts"])
    )
    return {
        verb: candidate["policy_command_counts"].get(verb, 0)
        - control["policy_command_counts"].get(verb, 0)
        for verb in verbs
    }


def _mean_or_none(values) -> float | None:
    values = list(values)
    return statistics.mean(values) if values else None


def mechanism_summary(rows: list[dict]) -> dict:
    games = [game for row in rows for game in row["option_games"]]
    training_turns: dict[str, list[int]] = defaultdict(list)
    requested = Counter()
    succeeded = Counter()
    for game in games:
        for event in game["training_events"]:
            requested[event["role"]] += 1
            if event["success"]:
                succeeded[event["role"]] += 1
                training_turns[event["role"]].append(event["turn"])

    funding_by_stage = {}
    for unit_count in (1, 2, 3):
        stages = [
            stage
            for game in games
            for stage in game["funding_stages"]
            if stage["unit_count"] == unit_count
        ]
        limiting = Counter(
            resource for stage in stages for resource in stage["limiting_resources_at_end"]
        )
        trained_turns = [stage["trained_turn"] for stage in stages if stage["trained_turn"]]
        ready_turns = [
            stage["first_ready_turn"] for stage in stages if stage["first_ready_turn"]
        ]
        funding_by_stage[STAGE_NAMES[unit_count]] = {
            "games_entered": len(stages),
            "games_trained": len(trained_turns),
            "train_rate": len(trained_turns) / len(stages) if stages else None,
            "trained_turn": robust_summary(trained_turns),
            "first_ready_turn": robust_summary(ready_turns),
            "limiting_resources_at_end": dict(sorted(limiting.items())),
            "mean_minimum_total_deficit": _mean_or_none(
                stage["minimum_total_deficit"] for stage in stages
            ),
        }

    role_totals: dict[str, dict[str, Counter]] = defaultdict(
        lambda: {
            "commands": Counter(),
            "successes": Counter(),
            "gains": Counter(),
            "deposits": Counter(),
            "plants": Counter(),
        }
    )
    for game in games:
        for worker in game["workers"]:
            totals = role_totals[worker["role"]]
            totals["commands"].update(worker["commands"])
            totals["successes"].update(worker["successful_actions"])
            totals["gains"].update(worker["material_gains"])
            totals["deposits"].update(worker["deposits"])
            totals["plants"].update(worker["plants"])

    supply_fields = (
        "created_trees",
        "joint_plants",
        "removed_trees",
        "surviving_trees",
        "candidate_harvested_fruit",
        "opponent_harvested_fruit",
        "candidate_wood_captured",
        "opponent_wood_captured",
        "opponent_touched_trees",
    )
    supply = {
        field: sum(game["supply"][field] for game in games) for field in supply_fields
    }
    supply["by_kind"] = dict(
        sorted(
            sum(
                (Counter(game["supply"]["by_kind"]) for game in games),
                Counter(),
            ).items()
        )
    )
    supply["geometry"] = dict(
        sorted(
            sum(
                (Counter(game["supply"]["geometry"]) for game in games),
                Counter(),
            ).items()
        )
    )

    command_displacement = Counter()
    for row in rows:
        command_displacement.update(row["delta_vs_live_commands"])

    handoffs = Counter(game["handoff_reason"] for game in games)
    return {
        "games": len(games),
        "handoff_reasons": dict(sorted(handoffs.items())),
        "final_unit_count": robust_summary(game["final_unit_count"] for game in games),
        "training": {
            role: {
                "requests": requested[role],
                "successes": succeeded[role],
                "success_rate": succeeded[role] / requested[role] if requested[role] else None,
                "turn": robust_summary(training_turns[role]),
            }
            for role in ROLE_NAMES[1:]
        },
        "funding": funding_by_stage,
        "worker_roles": {
            role: {
                key: dict(sorted(value.items()))
                for key, value in totals.items()
            }
            for role, totals in sorted(role_totals.items())
        },
        "created_supply": supply,
        "command_displacement_vs_live": dict(sorted(command_displacement.items())),
    }


def attach_replicate_live_deltas(rows: list[dict]) -> None:
    live = {
        (row["opponent"], row["seed"], row["replicate"]): row
        for row in rows
        if row["policy"] == "live"
    }
    for row in rows:
        control = live[(row["opponent"], row["seed"], row["replicate"])]
        row["delta_vs_live_margin"] = row["paired_margin"] - control["paired_margin"]
        row["delta_vs_live_wood"] = (
            row["paired_wood_edge"] - control["paired_wood_edge"]
        )


def load_control_registry(
    path: Path, seeds: list[int], opponents: list[str]
) -> tuple[dict, Path]:
    payload = json.loads(path.read_text())
    live_meta = payload["policies"]["live"]
    live_source = REPO / live_meta["source"]
    if source_sha256(live_source) != live_meta["sha256"]:
        raise RuntimeError("the frozen live source no longer matches the control league")
    for opponent in opponents:
        meta = payload["opponents"][opponent]
        if source_sha256(REPO / meta["source"]) != meta["sha256"]:
            raise RuntimeError(f"opponent {opponent!r} no longer matches the control league")
    seed_set = set(seeds)
    opponent_set = set(opponents)
    registered_cells = {
        (row["seed"], row["opponent"])
        for row in payload["rows"]
        if row["policy"] == "live"
        and row["seed"] in seed_set
        and row["opponent"] in opponent_set
    }
    expected = len(seeds) * len(opponents)
    if len(registered_cells) != expected:
        raise RuntimeError(
            f"control registry has {len(registered_cells)} requested cells, expected {expected}"
        )
    return payload, live_source


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument(
        "--replicates",
        type=int,
        default=2,
        help=(
            "independent process replications per map/opponent; frozen legacy opponents use "
            "randomized hash iteration"
        ),
    )
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--opponents",
        default=",".join(OPPONENT_SOURCES),
        help="comma-separated frozen opponent names",
    )
    parser.add_argument("--candidate", type=Path, default=CANDIDATE_SOURCE)
    parser.add_argument("--control-league", type=Path, default=CONTROL_LEAGUE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.seeds <= 0:
        raise SystemExit("--seeds must be positive")
    if args.replicates <= 0:
        raise SystemExit("--replicates must be positive")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    opponents = [name for name in args.opponents.split(",") if name]
    unknown = [name for name in opponents if name not in OPPONENT_SOURCES]
    if unknown:
        raise SystemExit("unknown opponents: " + ", ".join(unknown))
    if not opponents:
        raise SystemExit("--opponents cannot be empty")
    candidate_source = args.candidate if args.candidate.is_absolute() else REPO / args.candidate
    control_path = (
        args.control_league
        if args.control_league.is_absolute()
        else REPO / args.control_league
    )
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    _, live_source = load_control_registry(control_path, seeds, opponents)
    games = {seed: generate_bronze(seed) for seed in seeds}

    candidate_rows = []
    control_rows = []
    with tempfile.TemporaryDirectory(prefix="farm-first-option-study-") as directory:
        temp = Path(directory)
        candidate_binary = temp / "farmfirst"
        live_binary = temp / "live"
        compile_source(candidate_source, candidate_binary, "farm_first_option")
        compile_source(live_source, live_binary, "farm_first_live_control")
        opponent_binaries = {}
        for index, name in enumerate(opponents):
            binary = temp / name
            compile_source(OPPONENT_SOURCES[name], binary, f"farm_first_opp_{index}_{name}")
            opponent_binaries[name] = binary
        print(
            f"compiled candidate, exact live, and {len(opponents)} frozen opponents",
            flush=True,
        )

        tasks = [
            (seed, opponent, replicate)
            for seed in seeds
            for opponent in opponents
            for replicate in range(args.replicates)
        ]

        def run_cell(seed: int, opponent: str, replicate: int) -> tuple[dict, dict]:
            candidate_row = paired_row(
                seed,
                games[seed],
                opponent,
                candidate_binary,
                opponent_binaries[opponent],
            )
            candidate_row["replicate"] = replicate
            control_row = outcome_paired_row(
                seed,
                games[seed],
                "live",
                opponent,
                live_binary,
                opponent_binaries[opponent],
            )
            control_row["replicate"] = replicate
            return candidate_row, control_row

        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    run_cell,
                    seed,
                    opponent,
                    replicate,
                ): (seed, opponent, replicate)
                for seed, opponent, replicate in tasks
            }
            for completed, future in enumerate(as_completed(futures), 1):
                candidate_row, control_row = future.result()
                candidate_rows.append(candidate_row)
                control_rows.append(control_row)
                if completed % 10 == 0 or completed == len(tasks):
                    print(f"completed {completed}/{len(tasks)} paired cells", flush=True)

    candidate_rows.sort(
        key=lambda row: (row["seed"], row["opponent"], row["replicate"])
    )
    control_rows.sort(key=lambda row: (row["seed"], row["opponent"], row["replicate"]))
    control_by_cell = {
        (row["seed"], row["opponent"], row["replicate"]): row
        for row in control_rows
    }
    combined_rows = control_rows + candidate_rows
    attach_replicate_live_deltas(combined_rows)
    for row in candidate_rows:
        control = control_by_cell[(row["seed"], row["opponent"], row["replicate"])]
        row["delta_vs_live_commands"] = command_delta(row, control)

    payload = {
        "schema": 1,
        "scope": (
            "farm-first mechanism study on reused discovery seeds; corrected deterministic "
            "local simulator and frozen exact-live controls; not an arena predictor"
        ),
        "seed_start": args.seed_start,
        "seeds": args.seeds,
        "replicates": args.replicates,
        "jobs": args.jobs,
        "candidate": {
            "source": str(candidate_source.relative_to(REPO)),
            "sha256": source_sha256(candidate_source),
        },
        "control_league": str(control_path.relative_to(REPO)),
        "opponents": opponents,
        "aggregate": aggregate(combined_rows),
        "mechanisms": mechanism_summary(candidate_rows),
        "control_rows": control_rows,
        "rows": candidate_rows,
    }
    save(output_path, payload)
    print(json.dumps(payload["aggregate"]["by_policy"]["farmfirst"], indent=1))
    print(json.dumps(payload["mechanisms"], indent=1))
    print(f"saved {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
