#!/usr/bin/env python3
"""Integrate held-game objectives, commitments, and the frozen tree ranker.

Both learned layers exclude the evaluated game's fold.  The resulting command renderer remains
an offline policy skeleton: it omits TRAIN prediction and does not resolve arbitrary open-cell
waypoints, but unlike the separate component studies it propagates its own predicted targets.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.escdemon_target_assignment_study import (  # noqa: E402
    MOVE_LABELS,
    extract_game as extract_command_game,
    held_objective_predictions,
    replay_prediction,
)
from cgauto.escdemon_tree_target_study import (  # noqa: E402
    candidate_features,
    fit_ranker,
    ranker_predict,
)
from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    RAW_GAMES,
    adjacent,
    assigned_unit_commands,
    bfs,
    player_commands,
    read_trajectory,
    terrain,
)


TREE_LABELS = ("MOVE_TREE", "MOVE_TREE_RIPE")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def enrich_game(
    occurrence: dict,
    row_lookup: dict[tuple[int, int, int], dict],
    prediction_lookup: dict[tuple[int, int, int], str],
) -> list[dict]:
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
    own_doors = [
        cell
        for cell in adjacent(board["shacks"][player])
        if cell in board["walkable"]
    ]
    opponent_doors = [
        cell
        for cell in adjacent(board["shacks"][1 - player])
        if cell in board["walkable"]
    ]
    from_bank = bfs(board["walkable"], own_doors)
    from_opponent_bank = bfs(board["walkable"], opponent_doors)
    ordinals = {}
    next_ordinal = 0
    training_events = []
    usable = min(len(decoded["states"]) - 1, len(trajectory))
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
        # Resolve the official actions as a coverage assertion. The rows being enriched came
        # from the same command/state join and must name every current unit exactly once.
        assigned = assigned_unit_commands(parsed[turn - 1][player], units)
        plants = {(plant["x"], plant["y"]): plant for plant in state["plants"]}
        opponents = [unit for unit in state["units"] if unit["player"] != player]
        for unit in units:
            key = (game_id, turn, unit["id"])
            row = row_lookup[key]
            assert row["ordinal"] == ordinals[unit["id"]]
            assert bool(assigned.get(unit["id"], "WAIT"))
            predicted_label = prediction_lookup[key]
            labels_needed = set()
            if predicted_label in TREE_LABELS:
                labels_needed.add(predicted_label)
            actual_is_hard_tree = (
                row["label"] in TREE_LABELS
                and row["actual_target"] is not None
                and not row["repeated_actual_target"]
                and row["singleton_targets"].get(row["label"])
                != row["actual_target"]
            )
            if actual_is_hard_tree:
                labels_needed.add(row["label"])
            row["tree_options"] = {}
            from_unit = None
            for label in labels_needed:
                ripe = label == "MOVE_TREE_RIPE"
                candidates = [
                    cell
                    for cell, plant in plants.items()
                    if (plant["fruits"] > 0) == ripe
                ]
                if not candidates:
                    continue
                if from_unit is None:
                    from_unit = bfs(board["walkable"], [(unit["x"], unit["y"])])
                event = {
                    "game_id": game_id,
                    "turn": turn,
                    "ordinal": row["ordinal"],
                    "target": row["actual_target"] if label == row["label"] else None,
                    "candidates": candidates,
                    "features": candidate_features(
                        candidates=candidates,
                        plants=plants,
                        unit=unit,
                        ordinal=row["ordinal"],
                        turn=turn,
                        from_unit=from_unit,
                        from_bank=from_bank,
                        from_opponent_bank=from_opponent_bank,
                        other_units=[other for other in units if other["id"] != unit["id"]],
                        opponents=opponents,
                        water=board["water"],
                    ),
                }
                row["tree_options"][label] = event
                if actual_is_hard_tree and label == row["label"]:
                    training_events.append(event)
    return training_events


def ranker_replay_prediction(
    rows: list[dict], predictions: list[str], weights_by_fold: dict[int, dict]
) -> dict:
    committed = {}
    exact_rows = []
    move_target_exact = []
    per_game_turns = defaultdict(lambda: defaultdict(list))
    for row, predicted_label in zip(rows, predictions):
        key = (row["game_id"], row["unit_id"])
        actual_target = row["actual_target"]
        if actual_target is not None:
            predicted_target = committed.get(key)
            if predicted_target is None and predicted_label in TREE_LABELS:
                option = row.get("tree_options", {}).get(predicted_label)
                if option is not None:
                    predicted_target = ranker_predict(
                        weights_by_fold[row["game_id"] % 5], option
                    )
            if predicted_target is None:
                predicted_target = row["singleton_targets"].get(predicted_label)
            exact = (
                predicted_label in MOVE_LABELS and predicted_target == actual_target
            )
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


def study(occurrences: list[dict], agent_id: int) -> dict:
    analyzed = sorted(
        [extract_command_game(occurrence) for occurrence in occurrences],
        key=lambda game: game["game_id"],
    )
    rows = [row for game in analyzed for row in game["rows"]]
    predictions, _ = held_objective_predictions(rows)
    row_lookup = {
        (row["game_id"], row["turn"], row["unit_id"]): row for row in rows
    }
    prediction_lookup = {
        (row["game_id"], row["turn"], row["unit_id"]): prediction
        for row, prediction in zip(rows, predictions)
    }
    tree_events = []
    for occurrence in occurrences:
        tree_events.extend(enrich_game(occurrence, row_lookup, prediction_lookup))
    if len(tree_events) != 633:
        raise ValueError(f"expected 633 frozen hard-tree events, found {len(tree_events)}")

    weights_by_fold = {
        fold: fit_ranker(
            [event for event in tree_events if event["game_id"] % 5 != fold], 20
        )
        for fold in range(5)
    }
    baseline = replay_prediction(rows, predictions)
    integrated = ranker_replay_prediction(rows, predictions, weights_by_fold)
    fold_rows = []
    for fold in range(5):
        indices = [
            index for index, row in enumerate(rows) if row["game_id"] % 5 == fold
        ]
        selected_rows = [rows[index] for index in indices]
        selected_predictions = [predictions[index] for index in indices]
        base = replay_prediction(selected_rows, selected_predictions)
        rich = ranker_replay_prediction(
            selected_rows, selected_predictions, weights_by_fold
        )
        fold_rows.append(
            {
                "fold": fold,
                "games": len({row["game_id"] for row in selected_rows}),
                "rows": len(selected_rows),
                "baseline_move_target_exact_rate": base["move_target_exact_rate"],
                "ranker_move_target_exact_rate": rich["move_target_exact_rate"],
                "ranker_unit_command_exact_rate": rich["unit_command_exact_rate"],
                "ranker_all_worker_commands_exact_rate": rich[
                    "all_worker_commands_exact_rate"
                ],
            }
        )
    target_gain = (
        integrated["move_target_exact_rate"] - baseline["move_target_exact_rate"]
    )
    passed = (
        integrated["move_target_exact_rate"] >= 0.55
        and integrated["unit_command_exact_rate"] >= 0.68
        and integrated["all_worker_commands_exact_rate"] >= 0.48
        and target_gain >= 0.10
        and min(row["ranker_move_target_exact_rate"] for row in fold_rows) >= 0.50
    )
    clean = lambda report: {
        key: value for key, value in report.items() if key != "row_exact_flags"
    }
    return {
        "schema": 1,
        "scope": (
            "five-fold held-game objective lookup plus five-fold held-game 20-epoch tree ranker; "
            "autoregressive own target commitments; unit-command rendering only, excluding TRAIN, "
            "arbitrary MOVE_OTHER waypoints, counterfactual play, and causal value"
        ),
        "agent_id": agent_id,
        "games": len(occurrences),
        "rows": len(rows),
        "hard_tree_training_events": len(tree_events),
        "commitment_singleton_baseline": clean(baseline),
        "integrated_tree_ranker": {
            **clean(integrated),
            "move_target_exact_rate_gain": target_gain,
        },
        "folds": fold_rows,
        "policy_skeleton_gate": {
            "requirements": [
                "autoregressive MOVE-target exact rate at least 0.55",
                "unit-command exact rate at least 0.68",
                "all-worker command exact rate at least 0.48",
                "MOVE-target gain over commitment/singleton baseline at least 0.10",
                "every held fold MOVE-target exact rate at least 0.50",
            ],
            "passed": passed,
        },
        "decision": {
            "tree_ranker_integrates": passed,
            "build_complete_candidate": False,
            "next": (
                "Even a passing skeleton remains offline until opening-spec prediction and "
                "MOVE_OTHER routing are recovered. A failing skeleton retires learned exact-tree "
                "rendering as insufficient despite its conditional gate."
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
    occurrences.sort(key=lambda row: row["game_id"])
    payload = study(occurrences, args.agent_id)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
