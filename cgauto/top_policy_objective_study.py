#!/usr/bin/env python3
"""Test state-only imitation of top-player per-worker objectives."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import as_completed, ProcessPoolExecutor
import json
import os
from pathlib import Path
import statistics
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_macro_census import role_of  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    GAMES,
    LEADERBOARD,
    RAW_GAMES,
    assigned_unit_commands,
    player_commands,
    read_trajectory,
    terrain,
)


FEATURES = (
    "phase",
    "ordinal",
    "role",
    "carry_class",
    "full",
    "bank_distance",
    "on_cell",
    "unit_count",
    "score_bucket",
    "nearest_ripe",
    "nearest_tree",
    "nearest_iron",
    "cheap_train_affordable",
)
BACKOFFS = (
    FEATURES,
    (
        "phase",
        "ordinal",
        "role",
        "carry_class",
        "full",
        "bank_distance",
        "on_cell",
        "unit_count",
    ),
    ("phase", "role", "carry_class", "full", "bank_distance", "on_cell"),
    ("role", "carry_class", "full", "on_cell"),
    ("carry_class", "full", "on_cell"),
)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def phase_bucket(turn: int) -> str:
    for upper, label in (
        (5, "01-05"),
        (25, "06-25"),
        (75, "26-75"),
        (150, "76-150"),
        (250, "151-250"),
    ):
        if turn <= upper:
            return label
    return "251+"


def distance_bucket(value: int | None) -> str:
    if value is None:
        return "none"
    if value <= 2:
        return str(value)
    if value <= 5:
        return "3-5"
    if value <= 9:
        return "6-9"
    return "10+"


def score_bucket(value: int) -> str:
    if value <= -50:
        return "<-50"
    if value <= -10:
        return "-49..-10"
    if value < 10:
        return "-9..9"
    if value < 50:
        return "10..49"
    return "50+"


def bank_score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[5]


def manhattan(left: tuple[int, int], right: tuple[int, int]) -> int:
    return abs(left[0] - right[0]) + abs(left[1] - right[1])


def nearest(cell: tuple[int, int], targets) -> int | None:
    values = [manhattan(cell, target) for target in targets]
    return min(values) if values else None


def carry_class(carry: list[int]) -> str:
    kinds = set()
    if any(carry[:4]):
        kinds.add("fruit")
    if carry[4]:
        kinds.add("iron")
    if carry[5]:
        kinds.add("wood")
    if not kinds:
        return "empty"
    if len(kinds) > 1:
        return "mixed"
    return next(iter(kinds))


def objective_label(command: str | None, context: dict) -> str:
    if not command:
        return "WAIT"
    fields = command.split()
    if not fields:
        return "WAIT"
    verb = fields[0].upper()
    if verb == "WAIT":
        return "WAIT"
    if verb in {"PICK", "PLANT"}:
        kind = fields[2].upper() if len(fields) >= 3 else "UNKNOWN"
        return f"{verb}_{kind}"
    if verb != "MOVE":
        return verb
    if len(fields) < 4:
        return "MOVE_OTHER"
    try:
        target = (int(fields[2]), int(fields[3]))
    except ValueError:
        return "MOVE_OTHER"
    if target == context["own_shack"]:
        return "MOVE_BANK"
    if target == context["opponent_shack"]:
        return "MOVE_ENEMY_BANK"
    if target in context["iron"]:
        return "MOVE_IRON"
    plant = context["plants"].get(target)
    if plant is not None:
        return "MOVE_TREE_RIPE" if plant["fruits"] > 0 else "MOVE_TREE"
    return "MOVE_OTHER"


def row_features(
    state: dict,
    map_terrain: dict,
    player: int,
    unit: dict,
    ordinal: int,
    turn: int,
) -> dict:
    mine = [row for row in state["units"] if row["player"] == player]
    cell = (unit["x"], unit["y"])
    plants = {(row["x"], row["y"]): row for row in state["plants"]}
    ripe = [target for target, plant in plants.items() if plant["fruits"] > 0]
    inventory = state["inventories"][player]
    opponent_inventory = state["inventories"][1 - player]
    carried = unit["carry"]
    if cell in plants:
        on_cell = "ripe_tree" if plants[cell]["fruits"] > 0 else "tree"
    elif cell in map_terrain["iron"]:
        on_cell = "iron"
    elif manhattan(cell, map_terrain["shacks"][player]) <= 1:
        on_cell = "bank_edge"
    else:
        on_cell = "open"
    n = len(mine)
    cheap_cost = n + 1
    cheap_train = all(inventory[index] >= cheap_cost for index in (0, 1, 4))
    return {
        "phase": phase_bucket(turn),
        "ordinal": str(min(ordinal, 3)),
        "role": role_of([unit["ms"], unit["cc"], unit["hp"], unit["chop"]]),
        "carry_class": carry_class(carried),
        "full": str(sum(carried) >= unit["cc"]),
        "bank_distance": distance_bucket(manhattan(cell, map_terrain["shacks"][player])),
        "on_cell": on_cell,
        "unit_count": str(min(n, 4)),
        "score_bucket": score_bucket(bank_score(inventory) - bank_score(opponent_inventory)),
        "nearest_ripe": distance_bucket(nearest(cell, ripe)),
        "nearest_tree": distance_bucket(nearest(cell, plants)),
        "nearest_iron": distance_bucket(nearest(cell, map_terrain["iron"])),
        "cheap_train_affordable": str(cheap_train),
    }


def extract_game(task: tuple[dict, set[int]]) -> dict:
    game, selected_ids = task
    game_id = int(game["gameId"])
    trajectory = read_trajectory(game_id)
    parsed_commands = [
        [player_commands(row, player) for player in (0, 1)] for row in trajectory
    ]
    chop_ids = [
        effective_chop_unit_ids(turn[0]) + effective_chop_unit_ids(turn[1])
        for turn in parsed_commands
    ]
    decoded = decode_replay(
        RAW_GAMES / f"{game_id}.json", chop_unit_ids_by_turn=chop_ids
    )
    usable = min(len(decoded["states"]) - 1, len(trajectory))
    map_terrain = terrain(decoded["map"])
    rows = []
    selected = [row for row in game["players"] if row.get("agentId") in selected_ids]
    for player_row in selected:
        player = player_row["index"]
        ordinals = {}
        next_ordinal = 0
        for turn in range(1, usable + 1):
            state = decoded["states"][turn - 1]
            units = sorted(
                [row for row in state["units"] if row["player"] == player],
                key=lambda row: row["id"],
            )
            for unit in units:
                if unit["id"] not in ordinals:
                    ordinals[unit["id"]] = next_ordinal
                    next_ordinal += 1
            assigned = assigned_unit_commands(
                parsed_commands[turn - 1][player], units
            )
            plants = {(row["x"], row["y"]): row for row in state["plants"]}
            context = {
                "own_shack": map_terrain["shacks"][player],
                "opponent_shack": map_terrain["shacks"][1 - player],
                "iron": map_terrain["iron"],
                "plants": plants,
            }
            for unit in units:
                command = assigned.get(unit["id"])
                rows.append(
                    {
                        "game_id": game_id,
                        "agent_id": player_row["agentId"],
                        "turn": turn,
                        "unit_id": unit["id"],
                        "label": objective_label(command, context),
                        "features": row_features(
                            state,
                            map_terrain,
                            player,
                            unit,
                            ordinals[unit["id"]],
                            turn,
                        ),
                    }
                )
    return {
        "game_id": game_id,
        "rows": rows,
        "quality": {
            "decoded_turns": len(decoded["states"]) - 1,
            "trajectory_turns": len(trajectory),
            "unknown_diff_updates": len(decoded["unknown_updates"]),
        },
    }


def key(row: dict, fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(row["features"][field] for field in fields)


def majority(counts: Counter) -> str:
    return min(counts, key=lambda label: (-counts[label], label))


def fit(rows: list[dict]) -> dict:
    tables = [defaultdict(Counter) for _ in BACKOFFS]
    global_counts = Counter()
    for row in rows:
        global_counts[row["label"]] += 1
        for table, fields in zip(tables, BACKOFFS):
            table[key(row, fields)][row["label"]] += 1
    return {
        "tables": tables,
        "global": majority(global_counts),
        "global_counts": global_counts,
    }


def predict(model: dict, row: dict) -> tuple[str, str]:
    for index, (table, fields) in enumerate(zip(model["tables"], BACKOFFS)):
        counts = table.get(key(row, fields))
        if counts:
            return majority(counts), f"backoff_{index}"
    return model["global"], "global"


def classification_summary(labels: list[str], predictions: list[str]) -> dict:
    all_labels = sorted(set(labels) | set(predictions))
    per_label = {}
    f1_values = []
    for label in all_labels:
        true_positive = sum(a == label and p == label for a, p in zip(labels, predictions))
        false_positive = sum(a != label and p == label for a, p in zip(labels, predictions))
        false_negative = sum(a == label and p != label for a, p in zip(labels, predictions))
        support = sum(a == label for a in labels)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0
        recall = true_positive / support if support else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        if support:
            f1_values.append(f1)
        per_label[label] = {
            "support": support,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return {
        "rows": len(labels),
        "accuracy": sum(a == p for a, p in zip(labels, predictions)) / len(labels),
        "macro_f1": statistics.mean(f1_values),
        "per_label": per_label,
    }


def cross_validate(rows: list[dict], group_field: str, groups: list) -> dict:
    folds = []
    labels_all = []
    predictions_all = []
    baselines_all = []
    coverage = Counter()
    for held in groups:
        train = [row for row in rows if row[group_field] != held]
        test = [row for row in rows if row[group_field] == held]
        if not train or not test:
            continue
        model = fit(train)
        predictions = []
        for row in test:
            prediction, level = predict(model, row)
            predictions.append(prediction)
            coverage[level] += 1
        labels = [row["label"] for row in test]
        baselines = [model["global"]] * len(test)
        report = classification_summary(labels, predictions)
        baseline = classification_summary(labels, baselines)
        folds.append(
            {
                "held": held,
                "train_rows": len(train),
                "test_rows": len(test),
                "accuracy": report["accuracy"],
                "macro_f1": report["macro_f1"],
                "majority_accuracy": baseline["accuracy"],
            }
        )
        labels_all.extend(labels)
        predictions_all.extend(predictions)
        baselines_all.extend(baselines)
    result = classification_summary(labels_all, predictions_all)
    baseline = classification_summary(labels_all, baselines_all)
    result.update(
        {
            "group_field": group_field,
            "folds": folds,
            "majority_baseline": baseline,
            "accuracy_gain": result["accuracy"] - baseline["accuracy"],
            "coverage": dict(sorted(coverage.items())),
            "worst_fold_accuracy": min(row["accuracy"] for row in folds),
            "worst_fold_macro_f1": min(row["macro_f1"] for row in folds),
        }
    )
    return result


def study(rows: list[dict], quality: dict) -> dict:
    labels = Counter(row["label"] for row in rows)
    game_folds = sorted({row["game_id"] % 5 for row in rows})
    for row in rows:
        row["game_fold"] = row["game_id"] % 5
    agents = sorted({row["agent_id"] for row in rows})
    held_game = cross_validate(rows, "game_fold", game_folds)
    held_agent = cross_validate(rows, "agent_id", agents)
    per_agent_held_game = {}
    coherent_agents = []
    for agent in agents:
        agent_rows = [row for row in rows if row["agent_id"] == agent]
        folds = sorted({row["game_fold"] for row in agent_rows})
        report = cross_validate(agent_rows, "game_fold", folds)
        report["games"] = len({row["game_id"] for row in agent_rows})
        report["label_counts"] = dict(
            sorted(Counter(row["label"] for row in agent_rows).items())
        )
        passed_agent = (
            report["accuracy"] >= 0.60
            and report["macro_f1"] >= 0.35
            and report["worst_fold_accuracy"] >= 0.50
        )
        report["coherent_architecture_gate"] = {
            "requirements": [
                "within-agent held-game accuracy at least 0.60",
                "within-agent held-game macro F1 at least 0.35",
                "every within-agent fold accuracy at least 0.50",
            ],
            "passed": passed_agent,
        }
        per_agent_held_game[str(agent)] = report
        if passed_agent:
            coherent_agents.append(agent)
    passed = (
        held_game["accuracy"] >= 0.60
        and held_game["macro_f1"] >= 0.35
        and held_game["accuracy_gain"] >= 0.10
        and held_agent["worst_fold_accuracy"] >= 0.45
        and held_agent["worst_fold_macro_f1"] >= 0.25
    )
    return {
        "schema": 1,
        "scope": (
            "observational per-worker objective labels from current top-five official replays; "
            "state-only coarse lookup with nested backoff; diagnosis data, not causal policy or "
            "arena evidence"
        ),
        "rows": len(rows),
        "games": len({row["game_id"] for row in rows}),
        "agents": agents,
        "quality": quality,
        "features": FEATURES,
        "backoffs": BACKOFFS,
        "label_counts": dict(sorted(labels.items())),
        "held_game": held_game,
        "held_agent": held_agent,
        "per_agent_held_game": per_agent_held_game,
        "coherent_architecture_agents": coherent_agents,
        "discovery_gate": {
            "requirements": [
                "held-game accuracy at least 0.60",
                "held-game macro F1 at least 0.35",
                "held-game accuracy beats fold-majority by at least 0.10",
                "every held-agent accuracy at least 0.45",
                "every held-agent macro F1 at least 0.25",
            ],
            "passed": passed,
        },
        "interpretation_limit": (
            "The first gate tests whether high-level unit objectives are learnable without agent "
            "identity or outcomes. It does not yet model TRAIN timing/spec, target coordinates, "
            "multi-worker assignment, or counterfactual value. Passing only authorizes a richer "
            "imitation study; failure authorizes feature/label diagnosis, not bot construction. "
            "The separate within-agent gate identifies coherent architecture targets on consumed "
            "replays and does not establish counterfactual value."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument("--games", type=int, default=0, help="0 means all selected games")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.jobs < 1:
        raise SystemExit("--jobs must be positive")
    leaderboard = json.loads(LEADERBOARD.read_text())["users"]
    legend = [
        row for row in leaderboard if row.get("league", {}).get("divisionIndex") == 5
    ]
    top5_ids = {row["agentId"] for row in legend[:5]}
    games = [json.loads(line) for line in GAMES.read_text().splitlines() if line.strip()]
    games = [
        game
        for game in games
        if any(row.get("agentId") in top5_ids for row in game["players"])
    ]
    games.sort(key=lambda row: row["gameId"])
    if args.games:
        games = games[: args.games]

    analyzed = []
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(extract_game, (game, top5_ids)) for game in games]
        for completed, future in enumerate(as_completed(futures), 1):
            analyzed.append(future.result())
            if completed % 25 == 0 or completed == len(futures):
                print(f"completed {completed}/{len(futures)} games", flush=True)
    analyzed.sort(key=lambda row: row["game_id"])
    rows = [row for game in analyzed for row in game["rows"]]
    quality = {
        "games": len(analyzed),
        "turn_count_matches": sum(
            row["quality"]["decoded_turns"] == row["quality"]["trajectory_turns"]
            for row in analyzed
        ),
        "unknown_diff_updates": sum(
            row["quality"]["unknown_diff_updates"] for row in analyzed
        ),
    }
    payload = study(rows, quality)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "rows": payload["rows"],
        "games": payload["games"],
        "labels": payload["label_counts"],
        "held_game": {
            key: payload["held_game"][key]
            for key in ("accuracy", "macro_f1", "accuracy_gain", "worst_fold_accuracy")
        },
        "held_agent": {
            key: payload["held_agent"][key]
            for key in (
                "accuracy",
                "macro_f1",
                "accuracy_gain",
                "worst_fold_accuracy",
                "worst_fold_macro_f1",
            )
        },
        "per_agent": {
            agent: {
                "games": row["games"],
                "accuracy": row["accuracy"],
                "macro_f1": row["macro_f1"],
                "worst_fold_accuracy": row["worst_fold_accuracy"],
                "passed": row["coherent_architecture_gate"]["passed"],
            }
            for agent, row in payload["per_agent_held_game"].items()
        },
        "gate": payload["discovery_gate"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
