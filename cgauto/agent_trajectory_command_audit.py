#!/usr/bin/env python3
"""Compare local policy commands with one agent's official trajectories."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import (  # noqa: E402
    action_commands,
    effective_chop_unit_ids,
)
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    RAW_GAMES,
    assigned_unit_commands,
    player_commands,
    read_trajectory,
    terrain,
    train_specs,
)
from cgauto.top_policy_objective_study import objective_label  # noqa: E402


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def command_signature(command: str) -> tuple[str, ...]:
    fields = command.split()
    verb = fields[0].upper() if fields else "WAIT"
    if verb == "WAIT":
        return (verb,)
    if verb == "MOVE":
        return (verb, *fields[2:4])
    if verb in ("PICK", "PLANT"):
        return (verb, fields[2].upper() if len(fields) >= 3 else "UNKNOWN")
    return (verb,)


def read_grid(path: Path) -> dict[str, dict[tuple[int, int], list[str]]]:
    grid = defaultdict(dict)
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            key = int(row["game_id"]), int(row["turn"])
            if key in grid[row["model"]]:
                raise ValueError(f"duplicate command row for {row['model']} {key}")
            grid[row["model"]][key] = action_commands(row["commands"])
    return dict(grid)


def audit(analysis: dict, agent_id: int, grid: dict) -> dict:
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == agent_id
    ]
    occurrences.sort(key=lambda row: row["game_id"])
    expected_keys = set()
    counters = {model: defaultdict(int) for model in grid}
    for occurrence in occurrences:
        game_id = occurrence["game_id"]
        player = occurrence["seat"]
        trajectory = read_trajectory(game_id)
        parsed = [
            [player_commands(turn, seat) for seat in (0, 1)] for turn in trajectory
        ]
        chop_ids = [
            effective_chop_unit_ids(turn[0]) + effective_chop_unit_ids(turn[1])
            for turn in parsed
        ]
        decoded = decode_replay(
            RAW_GAMES / f"{game_id}.json", chop_unit_ids_by_turn=chop_ids
        )
        board = terrain(decoded["map"])
        usable = min(len(decoded["states"]) - 1, len(trajectory))
        for turn in range(1, usable + 1):
            key = game_id, turn
            expected_keys.add(key)
            state = decoded["states"][turn - 1]
            units = sorted(
                [unit for unit in state["units"] if unit["player"] == player],
                key=lambda unit: unit["id"],
            )
            plants = {(plant["x"], plant["y"]): plant for plant in state["plants"]}
            context = {
                "own_shack": board["shacks"][player],
                "opponent_shack": board["shacks"][1 - player],
                "iron": board["iron"],
                "plants": plants,
            }
            actual_commands = parsed[turn - 1][player]
            actual_assigned = assigned_unit_commands(actual_commands, units)
            actual_train = train_specs(actual_commands)
            for model, commands_by_turn in grid.items():
                if key not in commands_by_turn:
                    raise ValueError(f"missing {model} commands for {key}")
                predicted_commands = commands_by_turn[key]
                predicted_assigned = assigned_unit_commands(predicted_commands, units)
                predicted_train = train_specs(predicted_commands)
                count = counters[model]
                count["turns"] += 1
                count["predicted_train_turns"] += bool(predicted_train)
                count["actual_train_turns"] += bool(actual_train)
                if actual_train:
                    count["predicted_train_on_actual_turn"] += bool(predicted_train)
                    count["exact_train_on_actual_turn"] += predicted_train == actual_train
                elif predicted_train:
                    count["false_positive_train_turns"] += 1
                action_turn_exact = True
                for unit in units:
                    actual = actual_assigned.get(unit["id"], "WAIT")
                    predicted = predicted_assigned.get(unit["id"], "WAIT")
                    exact = command_signature(actual) == command_signature(predicted)
                    count["unit_rows"] += 1
                    count["unit_command_exact"] += exact
                    action_turn_exact &= exact
                    actual_objective = objective_label(actual, context)
                    predicted_objective = objective_label(predicted, context)
                    count["objective_exact"] += actual_objective == predicted_objective
                    if actual_objective.startswith("MOVE_"):
                        count["actual_move_rows"] += 1
                        count["move_target_exact"] += exact
                count["all_action_commands_exact_turns"] += action_turn_exact
                count["full_protocol_exact_turns"] += (
                    action_turn_exact and predicted_train == actual_train
                )
    for model, commands in grid.items():
        if set(commands) != expected_keys:
            raise ValueError(
                f"grid coverage mismatch for {model}; missing={len(expected_keys - set(commands))}, "
                f"extra={len(set(commands) - expected_keys)}"
            )

    models = {}
    for model, count in counters.items():
        # Preserve zero-valued event counters in serialized output and in the compact CLI
        # summary.  defaultdict does not add a key until it is read.
        for key in (
            "predicted_train_turns",
            "actual_train_turns",
            "predicted_train_on_actual_turn",
            "exact_train_on_actual_turn",
            "false_positive_train_turns",
        ):
            count[key] += 0
        rows = count["unit_rows"]
        turns = count["turns"]
        moves = count["actual_move_rows"]
        models[model] = {
            **dict(count),
            "objective_accuracy": count["objective_exact"] / rows,
            "unit_command_exact_rate": count["unit_command_exact"] / rows,
            "move_target_exact_rate": count["move_target_exact"] / moves,
            "all_action_commands_exact_turn_rate": count[
                "all_action_commands_exact_turns"
            ]
            / turns,
            "full_protocol_exact_turn_rate": count["full_protocol_exact_turns"]
            / turns,
        }
    actual_train_turns = next(iter(models.values()))["actual_train_turns"]
    required_exact_trains = math.ceil(0.75 * actual_train_turns)
    shortcut_passes = [
        model
        for model, row in models.items()
        if row["objective_accuracy"] >= 0.70
        and row["unit_command_exact_rate"] >= 0.60
        and row["move_target_exact_rate"] >= 0.60
        and row["exact_train_on_actual_turn"] >= required_exact_trains
        and row["false_positive_train_turns"] <= 5
    ]
    return {
        "schema": 1,
        "scope": (
            "teacher-forced local policy commands on official agent states; persistent local "
            "controllers see the actual next state, so agreement is behavioral support only, "
            "not a counterfactual rollout or causal-value estimate"
        ),
        "agent_id": agent_id,
        "games": len(occurrences),
        "turns": len(expected_keys),
        "models": dict(sorted(models.items())),
        "best": {
            metric: max(models, key=lambda model: models[model][metric])
            for metric in (
                "objective_accuracy",
                "unit_command_exact_rate",
                "move_target_exact_rate",
                "all_action_commands_exact_turn_rate",
            )
        },
        "shortcut_gate": {
            "requirements": [
                "objective accuracy at least 0.70",
                "unit-command exact rate at least 0.60",
                "MOVE-target exact rate at least 0.60",
                f"exact TRAIN on at least 75% of actual train turns "
                f"({required_exact_trains}/{actual_train_turns})",
                "at most five false-positive TRAIN turns",
            ],
            "passing_models": shortcut_passes,
            "passed": bool(shortcut_passes),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--commands", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(
        json.loads(args.analysis.read_text()), args.agent_id, read_grid(args.commands)
    )
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "turns": payload["turns"],
        "best": payload["best"],
        "models": {
            model: {
                key: row[key]
                for key in (
                    "objective_accuracy",
                    "unit_command_exact_rate",
                    "move_target_exact_rate",
                    "all_action_commands_exact_turn_rate",
                    "predicted_train_turns",
                    "exact_train_on_actual_turn",
                    "false_positive_train_turns",
                )
            }
            for model, row in payload["models"].items()
        },
        "gate": payload["shortcut_gate"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
