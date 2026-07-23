#!/usr/bin/env python3
"""Audit held-game exact-target recovery and role assignment for Escdemon.

The state-only objective model is reused unchanged.  This layer asks how much of the remaining
command can be rendered exactly from persistent targets or singleton semantic targets, and how
cleanly work is divided between the starter and the trained worker.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    RAW_GAMES,
    assigned_unit_commands,
    player_commands,
    read_trajectory,
    terrain,
)
from cgauto.top_policy_objective_study import (  # noqa: E402
    classification_summary,
    fit,
    objective_label,
    predict,
    row_features,
)


Cell = tuple[int, int]
MOVE_LABELS = {
    "MOVE_BANK",
    "MOVE_ENEMY_BANK",
    "MOVE_IRON",
    "MOVE_TREE_RIPE",
    "MOVE_TREE",
    "MOVE_OTHER",
}


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def move_target(command: str) -> Cell | None:
    fields = command.split()
    if len(fields) < 4 or fields[0].upper() != "MOVE":
        return None
    try:
        return int(fields[2]), int(fields[3])
    except ValueError:
        return None


def singleton_targets(context: dict) -> dict[str, Cell]:
    candidates = {
        "MOVE_BANK": [context["own_shack"]],
        "MOVE_ENEMY_BANK": [context["opponent_shack"]],
        "MOVE_IRON": sorted(context["iron"]),
        "MOVE_TREE_RIPE": sorted(
            cell for cell, plant in context["plants"].items() if plant["fruits"] > 0
        ),
        "MOVE_TREE": sorted(
            cell for cell, plant in context["plants"].items() if plant["fruits"] == 0
        ),
    }
    return {
        label: values[0] for label, values in candidates.items() if len(values) == 1
    }


def extract_game(occurrence: dict) -> dict:
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
    usable = min(len(decoded["states"]) - 1, len(trajectory))
    board = terrain(decoded["map"])
    ordinals = {}
    next_ordinal = 0
    prior_actual_target: dict[int, Cell] = {}
    rows = []
    for turn in range(1, usable + 1):
        state = decoded["states"][turn - 1]
        units = sorted(
            [unit for unit in state["units"] if unit["player"] == player],
            key=lambda unit: unit["id"],
        )
        for unit in units:
            if unit["id"] not in ordinals:
                ordinals[unit["id"]] = next_ordinal
                next_ordinal += 1
        assigned = assigned_unit_commands(parsed[turn - 1][player], units)
        plants = {(plant["x"], plant["y"]): plant for plant in state["plants"]}
        context = {
            "own_shack": board["shacks"][player],
            "opponent_shack": board["shacks"][1 - player],
            "iron": board["iron"],
            "plants": plants,
        }
        singletons = singleton_targets(context)
        target_labels = {
            cell: objective_label(f"MOVE 0 {cell[0]} {cell[1]}", context)
            for cell in board["walkable"]
            | board["iron"]
            | set(plants)
            | set(board["shacks"])
        }
        for unit in units:
            command = assigned.get(unit["id"], "WAIT")
            label = objective_label(command, context)
            target = move_target(command)
            previous = prior_actual_target.get(unit["id"])
            repeated = target is not None and target == previous
            verb = command.split()[0].upper() if command.split() else "WAIT"
            rows.append(
                {
                    "game_id": game_id,
                    "turn": turn,
                    "unit_id": unit["id"],
                    "ordinal": ordinals[unit["id"]],
                    "verb": verb,
                    "label": label,
                    "actual_target": target,
                    "repeated_actual_target": repeated,
                    "singleton_targets": singletons,
                    "target_labels": target_labels,
                    "features": row_features(
                        state,
                        board,
                        player,
                        unit,
                        ordinals[unit["id"]],
                        turn,
                    ),
                    "carry": tuple(unit["carry"]),
                }
            )
            if target is not None:
                prior_actual_target[unit["id"]] = target
            elif verb != "WAIT":
                prior_actual_target.pop(unit["id"], None)
    return {
        "game_id": game_id,
        "rows": rows,
        "quality": {
            "decoded_turns": len(decoded["states"]) - 1,
            "trajectory_turns": len(trajectory),
            "unknown_diff_updates": len(decoded["unknown_updates"]),
        },
    }


def held_objective_predictions(rows: list[dict]) -> tuple[list[str], list[dict]]:
    predictions = [""] * len(rows)
    folds = []
    fold_by_game = {game: game % 5 for game in {row["game_id"] for row in rows}}
    for fold in sorted(set(fold_by_game.values())):
        train_indices = [
            index
            for index, row in enumerate(rows)
            if fold_by_game[row["game_id"]] != fold
        ]
        test_indices = [
            index
            for index, row in enumerate(rows)
            if fold_by_game[row["game_id"]] == fold
        ]
        model = fit([rows[index] for index in train_indices])
        for index in test_indices:
            predictions[index] = predict(model, rows[index])[0]
        folds.append(
            {
                "fold": fold,
                "train_games": len(
                    {rows[index]["game_id"] for index in train_indices}
                ),
                "held_games": len({rows[index]["game_id"] for index in test_indices}),
                "held_rows": len(test_indices),
            }
        )
    if any(not prediction for prediction in predictions):
        raise ValueError("held-game objective prediction coverage is incomplete")
    return predictions, folds


def renderable_target(
    row: dict, predicted_label: str, committed: Cell | None
) -> Cell | None:
    if predicted_label not in MOVE_LABELS:
        return None
    if committed is not None:
        return committed
    return row["singleton_targets"].get(predicted_label)


def replay_prediction(rows: list[dict], predictions: list[str]) -> dict:
    committed: dict[tuple[int, int], Cell] = {}
    exact_rows = []
    move_target_exact = []
    per_game_turns: dict[int, dict[int, list[bool]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row, predicted_label in zip(rows, predictions):
        key = (row["game_id"], row["unit_id"])
        actual_target = row["actual_target"]
        if actual_target is not None:
            predicted_target = renderable_target(row, predicted_label, committed.get(key))
            exact = predicted_label in MOVE_LABELS and predicted_target == actual_target
            move_target_exact.append(exact)
            if predicted_target is None:
                committed.pop(key, None)
            else:
                committed[key] = predicted_target
        else:
            exact = predicted_label == row["label"]
            if predicted_label != "WAIT":
                committed.pop(key, None)
        exact_rows.append(exact)
        per_game_turns[row["game_id"]][row["turn"]].append(exact)
    turn_exact = [
        all(unit_rows)
        for turns in per_game_turns.values()
        for unit_rows in turns.values()
    ]
    return {
        "unit_rows": len(exact_rows),
        "unit_command_exact": sum(exact_rows),
        "unit_command_exact_rate": statistics.mean(exact_rows),
        "move_rows": len(move_target_exact),
        "move_target_exact": sum(move_target_exact),
        "move_target_exact_rate": statistics.mean(move_target_exact),
        "unit_turns": len(turn_exact),
        "all_worker_commands_exact": sum(turn_exact),
        "all_worker_commands_exact_rate": statistics.mean(turn_exact),
        "row_exact_flags": exact_rows,
    }


def semantic_new_target(row: dict) -> str:
    if row["label"] != "MOVE_OTHER":
        return row["label"]
    target = row["actual_target"]
    if target is None:
        return "NOT_MOVE"
    return "MOVE_OTHER"


def study(analyzed: list[dict], agent_id: int) -> dict:
    analyzed.sort(key=lambda game: game["game_id"])
    rows = [row for game in analyzed for row in game["rows"]]
    predictions, fold_skeleton = held_objective_predictions(rows)
    labels = [row["label"] for row in rows]
    objective = classification_summary(labels, predictions)
    rendered = replay_prediction(rows, predictions)

    move_rows = [row for row in rows if row["actual_target"] is not None]
    teacher_recovered = [
        row["repeated_actual_target"]
        or row["singleton_targets"].get(row["label"]) == row["actual_target"]
        for row in move_rows
    ]
    hard_new = [
        row
        for row, recovered in zip(move_rows, teacher_recovered)
        if not recovered
    ]

    fold_reports = []
    for fold_row in fold_skeleton:
        fold = fold_row["fold"]
        indices = [
            index for index, row in enumerate(rows) if row["game_id"] % 5 == fold
        ]
        selected_rows = [rows[index] for index in indices]
        selected_predictions = [predictions[index] for index in indices]
        replayed = replay_prediction(selected_rows, selected_predictions)
        report = classification_summary(
            [row["label"] for row in selected_rows], selected_predictions
        )
        fold_reports.append(
            {
                **fold_row,
                "objective_accuracy": report["accuracy"],
                "objective_macro_f1": report["macro_f1"],
                "unit_command_exact_rate": replayed["unit_command_exact_rate"],
                "move_target_exact_rate": replayed["move_target_exact_rate"],
                "all_worker_commands_exact_rate": replayed[
                    "all_worker_commands_exact_rate"
                ],
            }
        )

    by_ordinal = {}
    for ordinal in sorted({row["ordinal"] for row in rows}):
        selected = [row for row in rows if row["ordinal"] == ordinal]
        verbs = Counter(row["verb"] for row in selected)
        carried = [sum(row["carry"][index] for index in range(5)) for row in selected]
        by_ordinal[str(ordinal)] = {
            "rows": len(selected),
            "verbs": dict(sorted(verbs.items())),
            "non_wood_carry_turns": sum(value > 0 for value in carried),
            "wood_carry_turns": sum(row["carry"][5] > 0 for row in selected),
        }
    second = by_ordinal.get("1", {"verbs": {}, "non_wood_carry_turns": 1})
    pure_wood_assignment = (
        set(second["verbs"]).issubset({"MOVE", "CHOP", "DROP", "WAIT"})
        and second["non_wood_carry_turns"] == 0
    )

    exact_layer_gate = (
        objective["accuracy"] >= 0.70
        and rendered["unit_command_exact_rate"] >= 0.65
        and rendered["move_target_exact_rate"] >= 0.60
        and rendered["all_worker_commands_exact_rate"] >= 0.45
        and min(row["unit_command_exact_rate"] for row in fold_reports) >= 0.60
        and pure_wood_assignment
    )
    return {
        "schema": 1,
        "scope": (
            "observational Escdemon trajectories with five-fold held-game objective prediction; "
            "exact target rendering uses only the model's own prior target commitment or a "
            "singleton semantic target; excludes TRAIN and does not establish causal value"
        ),
        "agent_id": agent_id,
        "games": len(analyzed),
        "quality": {
            "turn_count_matches": sum(
                game["quality"]["decoded_turns"]
                == game["quality"]["trajectory_turns"]
                for game in analyzed
            ),
            "unknown_diff_updates": sum(
                game["quality"]["unknown_diff_updates"] for game in analyzed
            ),
        },
        "rows": len(rows),
        "objective_held_game": objective,
        "target_persistence": {
            "move_rows": len(move_rows),
            "consecutive_exact_target_repeats": sum(
                row["repeated_actual_target"] for row in move_rows
            ),
            "repeat_rate": statistics.mean(
                row["repeated_actual_target"] for row in move_rows
            ),
            "teacher_forced_recoverable": sum(teacher_recovered),
            "teacher_forced_recoverable_rate": statistics.mean(teacher_recovered),
            "hard_new_targets": len(hard_new),
            "hard_new_target_labels": dict(
                sorted(Counter(semantic_new_target(row) for row in hard_new).items())
            ),
            "interpretation_limit": (
                "Teacher-forced recovery assumes the previous observed target is known. The "
                "autoregressive result below keeps only targets the renderer itself recovered."
            ),
        },
        "autoregressive_command_rendering": {
            key: value for key, value in rendered.items() if key != "row_exact_flags"
        },
        "assignment": {
            "by_ordinal": by_ordinal,
            "trained_worker_is_pure_wood_converter": pure_wood_assignment,
        },
        "folds": fold_reports,
        "exact_layer_gate": {
            "requirements": [
                "held-game objective accuracy at least 0.70",
                "autoregressive unit-command exact rate at least 0.65",
                "autoregressive MOVE-target exact rate at least 0.60",
                "all-worker command exact rate at least 0.45",
                "every fold unit-command exact rate at least 0.60",
                "trained-worker assignment is purely wood conversion",
            ],
            "passed": exact_layer_gate,
        },
        "decision": {
            "build_complete_research_policy": exact_layer_gate,
            "next": (
                "If the exact layer passes, compare teacher-forced commands from local policy "
                "skeletons and then implement the smallest matching two-role controller. If it "
                "fails, learn only hard new-tree selection; do not alter the resident."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analysis = json.loads(args.analysis.read_text())
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == args.agent_id
    ]
    analyzed = []
    for index, occurrence in enumerate(occurrences, 1):
        analyzed.append(extract_game(occurrence))
        if index % 10 == 0 or index == len(occurrences):
            print(f"decoded {index}/{len(occurrences)} games", flush=True)
    payload = study(analyzed, args.agent_id)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "rows": payload["rows"],
        "objective_accuracy": payload["objective_held_game"]["accuracy"],
        "objective_macro_f1": payload["objective_held_game"]["macro_f1"],
        "target_persistence": payload["target_persistence"],
        "autoregressive": payload["autoregressive_command_rendering"],
        "assignment": payload["assignment"],
        "folds": payload["folds"],
        "gate": payload["exact_layer_gate"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
