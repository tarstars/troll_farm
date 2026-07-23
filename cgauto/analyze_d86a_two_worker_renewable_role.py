#!/usr/bin/env python3
"""Audit yaichi's two-worker renewable role split on frozen open replays.

D86a is observational.  It reconstructs harvested-fruit provenance, fits the frozen shallow
opening selector on historical discovery games, and evaluates it once on the historical
validation block.  Current D61p games are consumed discovery evidence and are descriptive only.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    assigned_unit_commands,
    cargo_delta,
    opening_features,
    player_commands,
)

AGENT_ID = 6480541
HISTORICAL_ANALYSIS = (
    REPO
    / "data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.json"
)
RAW_GAMES = REPO / "data/raw/games"
HISTORICAL_TRAJECTORIES = REPO / "data/processed/trajectories"
CURRENT_TRAJECTORIES = (
    REPO
    / "data/raw/snapshots/20260721T105508Z-d61p/processed/open/trajectories"
)

DISCOVERY_GAME_IDS = (
    893174122,
    893407296,
    893412043,
    893876322,
    894397581,
    895446276,
    895446639,
    895447009,
    895447026,
    895447237,
    895883032,
    895883103,
    895883400,
    895883571,
    895924585,
)
VALIDATION_GAME_IDS = (
    895925001,
    895926495,
    895926546,
    895926772,
    895927134,
    895927164,
    895927169,
    895927226,
    895927242,
    895927312,
)
CURRENT_GAME_IDS = (
    896491202,
    896492419,
    896493461,
    896493721,
    896494122,
    896494214,
    896494703,
    896495136,
    896495350,
    896495475,
)

FEATURES = (
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
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
FRUIT_INDICES = range(4)


def score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[5]


def mean_or_none(values) -> float | None:
    selected = [value for value in values if value is not None]
    return statistics.mean(selected) if selected else None


def read_trajectory(path: str | Path) -> list[dict]:
    return [
        json.loads(line)
        for line in Path(path).read_text().splitlines()
        if line.strip()
    ]


def agent_seat(raw: dict) -> tuple[int, dict, dict]:
    agents = raw.get("agents", [])
    own = next((row for row in agents if row.get("agentId") == AGENT_ID), None)
    if own is None:
        raise ValueError(f"agent {AGENT_ID} absent from game {raw.get('gameId')}")
    opponent = next(row for row in agents if row.get("index") != own.get("index"))
    return int(own["index"]), own, opponent


def successful_chop(
    unit: dict, before_plants: dict[tuple[int, int], dict], after_plants: dict
) -> bool:
    cell = (unit["x"], unit["y"])
    before = before_plants.get(cell)
    if before is None:
        return False
    after = after_plants.get(cell)
    return after is None or after["health"] < before["health"]


def consume_provenance(pool: deque[str], amount: int) -> tuple[int, int]:
    """Consume acquisition-ordered cargo and return harvested/other token counts."""

    harvested = 0
    other = 0
    for _ in range(amount):
        if not pool:
            # A missing provenance token is retained as OTHER so reconstruction remains total;
            # the caller records the mismatch as an integrity failure.
            other += 1
            continue
        if pool.popleft() == "H":
            harvested += 1
        else:
            other += 1
    return harvested, other


def new_worker(unit: dict, ordinal: int, spawn_turn: int) -> dict:
    return {
        "unit_id": unit["id"],
        "ordinal": ordinal,
        "spawn_turn": spawn_turn,
        "spec": [unit["ms"], unit["cc"], unit["hp"], unit["chop"]],
        "issued": Counter(),
        "successful": Counter(),
        "gained": [0] * 6,
        "spent": [0] * 6,
        "reinvested_by_100": [0] * 4,
        "reinvested_total": [0] * 4,
        "successful_plants_by_100": 0,
        "successful_plants_total": 0,
        "first_successful_harvest": None,
        "first_successful_plant": None,
        "first_reinvestment": None,
    }


def item_dict(values: list[int]) -> dict[str, int]:
    return {ITEMS[index]: value for index, value in enumerate(values) if value}


def worker_output(worker: dict) -> dict:
    productive = sum(worker["successful"].values())
    return {
        "unit_id": worker["unit_id"],
        "ordinal": worker["ordinal"],
        "spawn_turn": worker["spawn_turn"],
        "spec": worker["spec"],
        "issued": dict(sorted(worker["issued"].items())),
        "successful": dict(sorted(worker["successful"].items())),
        "successful_productive_nonmove": productive,
        "successful_chop_share": (
            worker["successful"].get("CHOP", 0) / productive if productive else None
        ),
        "gained": item_dict(worker["gained"]),
        "spent": item_dict(worker["spent"]),
        "reinvested_by_100": item_dict(worker["reinvested_by_100"] + [0, 0]),
        "reinvested_total": item_dict(worker["reinvested_total"] + [0, 0]),
        "successful_plants_by_100": worker["successful_plants_by_100"],
        "successful_plants_total": worker["successful_plants_total"],
        "first_successful_harvest": worker["first_successful_harvest"],
        "first_successful_plant": worker["first_successful_plant"],
        "first_reinvestment": worker["first_reinvestment"],
    }


def analyze_game(task: tuple[int, str, str]) -> dict:
    game_id, split, trajectory_name = task
    raw_path = RAW_GAMES / f"{game_id}.json"
    raw = json.loads(raw_path.read_text())
    trajectory = read_trajectory(trajectory_name)
    commands_by_turn = [
        [player_commands(row, player) for player in (0, 1)] for row in trajectory
    ]
    chop_ids = [
        effective_chop_unit_ids(commands[0]) + effective_chop_unit_ids(commands[1])
        for commands in commands_by_turn
    ]
    decoded = decode_replay(raw_path, chop_unit_ids_by_turn=chop_ids)
    states = decoded["states"]
    player, own_agent, opponent_agent = agent_seat(raw)
    initial_units = sorted(
        (unit for unit in states[0]["units"] if unit["player"] == player),
        key=lambda row: row["id"],
    )
    if not initial_units:
        raise ValueError(f"game {game_id} has no initial yaichi unit")

    workers: dict[int, dict] = {}
    provenance: dict[int, list[deque[str]]] = {}
    ordinal_by_id: dict[int, int] = {}
    next_ordinal = 0
    provenance_underflows = 0
    train_turns = []

    for unit in initial_units:
        ordinal_by_id[unit["id"]] = next_ordinal
        workers[unit["id"]] = new_worker(unit, next_ordinal, 0)
        provenance[unit["id"]] = [
            deque("O" for _ in range(unit["carry"][index])) for index in FRUIT_INDICES
        ]
        next_ordinal += 1

    usable_turns = min(len(states) - 1, len(trajectory))
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
        assigned = assigned_unit_commands(
            commands_by_turn[turn - 1][player], list(before_units.values())
        )
        before_plants = {
            (plant["x"], plant["y"]): plant for plant in before["plants"]
        }
        after_plants = {
            (plant["x"], plant["y"]): plant for plant in after["plants"]
        }

        for unit_id, unit in sorted(before_units.items()):
            command = assigned.get(unit_id)
            if command is None:
                continue
            verb = command.split()[0].upper()
            worker = workers[unit_id]
            worker["issued"][verb] += 1
            after_unit = after_units.get(unit_id)
            gained, spent = cargo_delta(unit, after_unit)
            for index in range(6):
                worker["gained"][index] += gained[index]
                worker["spent"][index] += spent[index]

            chop_ok = verb == "CHOP" and successful_chop(
                unit, before_plants, after_plants
            )
            harvest_ok = verb == "HARVEST" and any(gained[index] for index in FRUIT_INDICES)
            plant_ok = verb == "PLANT" and any(spent[index] for index in FRUIT_INDICES)
            drop_ok = verb == "DROP" and any(spent)
            pick_ok = verb == "PICK" and any(gained[index] for index in FRUIT_INDICES)
            mine_ok = verb == "MINE" and gained[4] > 0
            successful = {
                "CHOP": chop_ok,
                "HARVEST": harvest_ok,
                "PLANT": plant_ok,
                "DROP": drop_ok,
                "PICK": pick_ok,
                "MINE": mine_ok,
            }.get(verb, False)
            if successful:
                worker["successful"][verb] += 1

            for index in FRUIT_INDICES:
                if spent[index]:
                    available = len(provenance[unit_id][index])
                    harvested, _ = consume_provenance(
                        provenance[unit_id][index], spent[index]
                    )
                    provenance_underflows += max(0, spent[index] - available)
                    if verb == "PLANT" and harvested:
                        worker["reinvested_total"][index] += harvested
                        if turn <= 100:
                            worker["reinvested_by_100"][index] += harvested
                        if worker["first_reinvestment"] is None:
                            worker["first_reinvestment"] = turn
                if gained[index]:
                    provenance[unit_id][index].extend(
                        ("H" if verb == "HARVEST" else "O")
                        for _ in range(gained[index])
                    )

            if harvest_ok and worker["first_successful_harvest"] is None:
                worker["first_successful_harvest"] = turn
            if plant_ok:
                planted = sum(spent[index] for index in FRUIT_INDICES)
                worker["successful_plants_total"] += planted
                if turn <= 100:
                    worker["successful_plants_by_100"] += planted
                if worker["first_successful_plant"] is None:
                    worker["first_successful_plant"] = turn

            if after_unit is None:
                for pool in provenance[unit_id]:
                    pool.clear()

        new_units = sorted(
            (
                unit
                for unit_id, unit in after_units.items()
                if unit_id not in before_units
            ),
            key=lambda row: row["id"],
        )
        for unit in new_units:
            ordinal_by_id[unit["id"]] = next_ordinal
            workers[unit["id"]] = new_worker(unit, next_ordinal, turn)
            provenance[unit["id"]] = [
                deque("O" for _ in range(unit["carry"][index]))
                for index in FRUIT_INDICES
            ]
            train_turns.append(
                {
                    "turn": turn,
                    "unit_id": unit["id"],
                    "ordinal": next_ordinal,
                    "spec": [unit["ms"], unit["cc"], unit["hp"], unit["chop"]],
                }
            )
            next_ordinal += 1

    outputs = [worker_output(row) for _, row in sorted(workers.items(), key=lambda item: item[1]["ordinal"])]
    starter = next(row for row in outputs if row["ordinal"] == 0)
    reinvested_by_worker = {
        row["unit_id"]: sum(row["reinvested_by_100"].values()) for row in outputs
    }
    total_reinvested = sum(reinvested_by_worker.values())
    starter_reinvested = reinvested_by_worker[starter["unit_id"]]
    renewable_mode = (
        starter_reinvested >= 3
        and starter["successful_plants_by_100"] >= 3
        and starter["successful"].get("HARVEST", 0) > 0
        and starter["successful"].get("PLANT", 0) > 0
    )
    trained = next((row for row in outputs if row["ordinal"] == 1), None)
    starter_share = starter_reinvested / total_reinvested if total_reinvested else None
    trained_chop_share = trained["successful_chop_share"] if trained else None
    role_split = bool(
        len(train_turns) == 1
        and trained_chop_share is not None
        and trained_chop_share >= 0.80
        and starter_share is not None
        and starter_share >= 0.80
    )

    terminal = states[usable_turns]
    official_scores = [int(round(value)) for value in raw.get("scores", [])]
    terminal_scores = [score(list(inventory)) for inventory in terminal["inventories"]]
    opening = opening_features(decoded["map"], states[0], player)
    return {
        "game_id": game_id,
        "corpus": "current_consumed" if split == "current" else "historical",
        "split": split,
        "seat": player,
        "opponent_agent_id": opponent_agent.get("agentId"),
        "opponent": opponent_agent.get("codingamer", {}).get("pseudo"),
        "turns": usable_turns,
        "score": official_scores[player],
        "opponent_score": official_scores[1 - player],
        "margin": official_scores[player] - official_scores[1 - player],
        "final_inventory": list(terminal["inventories"][player]),
        "final_wood": terminal["inventories"][player][5],
        "opening": {feature: opening.get(feature) for feature in FEATURES},
        "successful_train_count": len(train_turns),
        "final_worker_count": len(
            [unit for unit in terminal["units"] if unit["player"] == player]
        ),
        "training_events": train_turns,
        "workers": outputs,
        "starter_reinvested_by_100": starter_reinvested,
        "total_reinvested_by_100": total_reinvested,
        "starter_reinvestment_share": starter_share,
        "trained_chop_share": trained_chop_share,
        "renewable_mode": renewable_mode,
        "role_split": role_split,
        "threshold_labels": {
            str(threshold): starter_reinvested >= threshold
            for threshold in (1, 2, 4, 8)
        },
        "integrity": {
            "trajectory_matches_decoded_turns": len(trajectory) == len(states) - 1,
            "unknown_diff_updates": len(decoded["unknown_updates"]),
            "terminal_scores_exact": terminal_scores == official_scores,
            "provenance_underflows": provenance_underflows,
            "raw_agent_valid": own_agent.get("valid"),
        },
    }


def tasks() -> list[tuple[int, str, str]]:
    rows = []
    for game_id in DISCOVERY_GAME_IDS:
        rows.append(
            (game_id, "discovery", str(HISTORICAL_TRAJECTORIES / f"{game_id}.jsonl"))
        )
    for game_id in VALIDATION_GAME_IDS:
        rows.append(
            (game_id, "validation", str(HISTORICAL_TRAJECTORIES / f"{game_id}.jsonl"))
        )
    for game_id in CURRENT_GAME_IDS:
        rows.append(
            (game_id, "current", str(CURRENT_TRAJECTORIES / f"{game_id}.jsonl"))
        )
    return rows


def analyze_all(jobs: int) -> list[dict]:
    work = tasks()
    if jobs == 1:
        rows = [analyze_game(task) for task in work]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            rows = list(executor.map(analyze_game, work))
    return sorted(rows, key=lambda row: (row["split"], row["game_id"]))


def canonical_rows(rows: list[dict]) -> bytes:
    return (
        "\n".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows
        )
        + "\n"
    ).encode()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def objective_weights(labels: list[bool]) -> list[float]:
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives and negatives:
        return [0.5 / positives if label else 0.5 / negatives for label in labels]
    return [1.0 / len(labels)] * len(labels)


def node_count(model: dict) -> int:
    if "leaf" in model:
        return 0
    return 1 + node_count(model["left"]) + node_count(model["right"])


def serialize_model(model: dict) -> str:
    return json.dumps(model, sort_keys=True, separators=(",", ":"))


def better_candidate(candidate: dict, incumbent: dict | None) -> bool:
    if incumbent is None:
        return True
    candidate_key = (
        candidate["weighted_correct"],
        candidate["ordinary_correct"],
        -node_count(candidate["model"]),
    )
    incumbent_key = (
        incumbent["weighted_correct"],
        incumbent["ordinary_correct"],
        -node_count(incumbent["model"]),
    )
    if candidate_key != incumbent_key:
        return candidate_key > incumbent_key
    return serialize_model(candidate["model"]) < serialize_model(incumbent["model"])


def fit_tree(rows: list[dict], max_depth: int) -> dict:
    labels = [bool(row["renewable_mode"]) for row in rows]
    weights = objective_weights(labels)
    memo: dict[tuple[tuple[int, ...], int], dict] = {}

    def leaf(indices: tuple[int, ...]) -> dict:
        options = []
        for prediction in (False, True):
            options.append(
                {
                    "model": {"leaf": prediction},
                    "weighted_correct": sum(
                        weights[index]
                        for index in indices
                        if labels[index] == prediction
                    ),
                    "ordinary_correct": sum(
                        labels[index] == prediction for index in indices
                    ),
                }
            )
        return options[0] if better_candidate(options[0], options[1]) else options[1]

    def recurse(indices: tuple[int, ...], depth: int) -> dict:
        key = (indices, depth)
        if key in memo:
            return memo[key]
        best = leaf(indices)
        if depth:
            for feature in FEATURES:
                values = sorted(
                    {
                        rows[index]["opening"].get(feature)
                        for index in indices
                        if rows[index]["opening"].get(feature) is not None
                    }
                )
                thresholds = [
                    (left + right) / 2 for left, right in zip(values, values[1:])
                ]
                for threshold in thresholds:
                    left_indices = tuple(
                        index
                        for index in indices
                        if rows[index]["opening"].get(feature) is not None
                        and rows[index]["opening"][feature] <= threshold
                    )
                    right_indices = tuple(
                        index
                        for index in indices
                        if rows[index]["opening"].get(feature) is not None
                        and rows[index]["opening"][feature] > threshold
                    )
                    if len(left_indices) < 3 or len(right_indices) < 3:
                        continue
                    left = recurse(left_indices, depth - 1)
                    right = recurse(right_indices, depth - 1)
                    candidate = {
                        "model": {
                            "feature": feature,
                            "threshold": threshold,
                            "left": left["model"],
                            "right": right["model"],
                        },
                        "weighted_correct": left["weighted_correct"]
                        + right["weighted_correct"],
                        "ordinary_correct": left["ordinary_correct"]
                        + right["ordinary_correct"],
                    }
                    if better_candidate(candidate, best):
                        best = candidate
        memo[key] = best
        return best

    selected = recurse(tuple(range(len(rows))), max_depth)
    selected["balanced_accuracy_in_sample"] = selected["weighted_correct"]
    selected["accuracy_in_sample"] = selected["ordinary_correct"] / len(rows)
    return selected


def predict(model: dict, row: dict) -> bool:
    while "leaf" not in model:
        value = row["opening"].get(model["feature"])
        if value is None:
            return False
        model = model["left"] if value <= model["threshold"] else model["right"]
    return bool(model["leaf"])


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if not total:
        return None
    rate = successes / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    radius = (
        z
        * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total))
        / denominator
    )
    return [center - radius, center + radius]


def classification_metrics(rows: list[dict], model: dict) -> dict:
    labels = [bool(row["renewable_mode"]) for row in rows]
    predictions = [predict(model, row) for row in rows]
    tp = sum(label and prediction for label, prediction in zip(labels, predictions))
    tn = sum(not label and not prediction for label, prediction in zip(labels, predictions))
    fp = sum(not label and prediction for label, prediction in zip(labels, predictions))
    fn = sum(label and not prediction for label, prediction in zip(labels, predictions))
    positive = tp + fn
    negative = tn + fp
    predicted_positive = tp + fp
    recall = tp / positive if positive else None
    specificity = tn / negative if negative else None
    precision = tp / predicted_positive if predicted_positive else None
    balanced = (
        0.5 * (recall + specificity)
        if recall is not None and specificity is not None
        else None
    )
    return {
        "n": len(rows),
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "accuracy": (tp + tn) / len(rows) if rows else None,
        "balanced_accuracy": balanced,
        "renewable_precision": precision,
        "renewable_recall": recall,
        "nonrenewable_recall": specificity,
        "intervals_95": {
            "renewable_precision": wilson(tp, predicted_positive),
            "renewable_recall": wilson(tp, positive),
            "nonrenewable_recall": wilson(tn, negative),
        },
        "predictions": [
            {
                "game_id": row["game_id"],
                "actual": label,
                "predicted": prediction,
            }
            for row, label, prediction in zip(rows, labels, predictions)
        ],
    }


def feature_distributions(rows: list[dict]) -> dict:
    result = {}
    for feature in FEATURES:
        result[feature] = {}
        for label, name in ((False, "nonrenewable"), (True, "renewable")):
            values = [
                row["opening"].get(feature)
                for row in rows
                if bool(row["renewable_mode"]) == label
                and row["opening"].get(feature) is not None
            ]
            result[feature][name] = {
                "n": len(values),
                "mean": mean_or_none(values),
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
            }
    return result


def outcome_summary(rows: list[dict]) -> dict:
    result = {}
    for label, name in ((False, "nonrenewable"), (True, "renewable")):
        selected = [row for row in rows if bool(row["renewable_mode"]) == label]
        result[name] = {
            "n": len(selected),
            "score_mean": mean_or_none(row["score"] for row in selected),
            "margin_mean": mean_or_none(row["margin"] for row in selected),
            "wood_mean": mean_or_none(row["final_wood"] for row in selected),
            "starter_reinvested_by_100_mean": mean_or_none(
                row["starter_reinvested_by_100"] for row in selected
            ),
        }
    return result


def leaf_summaries(rows: list[dict], model: dict) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        node = model
        path = []
        missing = False
        while "leaf" not in node:
            value = row["opening"].get(node["feature"])
            if value is None:
                missing = True
                break
            direction = "left" if value <= node["threshold"] else "right"
            path.append(direction)
            node = node[direction]
        key = "missing=>false" if missing else "/".join(path) or "root"
        grouped[key].append(row)
    return [
        {
            "path": path,
            "n": len(selected),
            "renewable": sum(row["renewable_mode"] for row in selected),
            "game_ids": [row["game_id"] for row in selected],
        }
        for path, selected in sorted(grouped.items())
    ]


def historical_reference_checks(rows: list[dict]) -> dict:
    payload = json.loads(HISTORICAL_ANALYSIS.read_text())
    references = {
        row["game_id"]: row
        for row in payload["occurrences"]
        if row.get("agent_id") == AGENT_ID
    }
    checks = []
    for row in rows:
        reference = references.get(row["game_id"])
        checks.append(
            {
                "game_id": row["game_id"],
                "present": reference is not None,
                "seat_exact": reference is not None and reference["seat"] == row["seat"],
                "score_exact": reference is not None and reference["score"] == row["score"],
                "final_inventory_exact": reference is not None
                and reference["final_inventory"] == row["final_inventory"],
                "opening_exact": reference is not None
                and all(
                    reference["opening"].get(feature) == row["opening"].get(feature)
                    for feature in FEATURES
                ),
            }
        )
    return {
        "checks": checks,
        "all_exact": all(
            all(value for key, value in check.items() if key != "game_id")
            for check in checks
        ),
    }


def build_result(rows: list[dict], repeat_exact: bool, hashes: dict) -> dict:
    historical = [row for row in rows if row["corpus"] == "historical"]
    discovery = [row for row in rows if row["split"] == "discovery"]
    validation = [row for row in rows if row["split"] == "validation"]
    current = [row for row in rows if row["split"] == "current"]

    depth_two = fit_tree(discovery, 2)
    stump = fit_tree(discovery, 1)
    constant = fit_tree(discovery, 0)
    if (
        depth_two["balanced_accuracy_in_sample"]
        - constant["balanced_accuracy_in_sample"]
        < 0.10
    ):
        selected_model = constant["model"]
        selected_reason = "depth_two_advantage_below_0.10_use_constant"
    else:
        selected_model = depth_two["model"]
        selected_reason = "depth_two_advantage_at_least_0.10"

    discovery_metrics = classification_metrics(discovery, selected_model)
    validation_metrics = classification_metrics(validation, selected_model)
    current_metrics = classification_metrics(current, selected_model)
    validation_constant = classification_metrics(validation, constant["model"])
    validation_advantage = (
        validation_metrics["balanced_accuracy"]
        - validation_constant["balanced_accuracy"]
        if validation_metrics["balanced_accuracy"] is not None
        and validation_constant["balanced_accuracy"] is not None
        else None
    )

    reference = historical_reference_checks(historical)
    per_row_integrity = all(
        row["integrity"]["trajectory_matches_decoded_turns"]
        and row["integrity"]["unknown_diff_updates"] == 0
        and row["integrity"]["terminal_scores_exact"]
        and row["integrity"]["provenance_underflows"] == 0
        for row in rows
    )
    integrity_gates = {
        "all_35_games_present": len(rows) == 35,
        "repeat_rows_byte_identical": repeat_exact,
        "per_row_reconstruction_exact": per_row_integrity,
        "historical_reference_exact": reference["all_exact"],
    }

    discovery_positive = sum(row["renewable_mode"] for row in discovery)
    validation_positive = sum(row["renewable_mode"] for row in validation)
    historical_renewable = [row for row in historical if row["renewable_mode"]]
    current_renewable = [row for row in current if row["renewable_mode"]]
    historical_role_rate = mean_or_none(
        int(row["role_split"]) for row in historical_renewable
    )
    current_role_rate = mean_or_none(int(row["role_split"]) for row in current_renewable)
    support_gates = {
        "discovery_at_least_4_each": discovery_positive >= 4
        and len(discovery) - discovery_positive >= 4,
        "validation_at_least_3_each": validation_positive >= 3
        and len(validation) - validation_positive >= 3,
        "both_seats": len({row["seat"] for row in historical}) == 2,
        "at_least_6_opponents": len(
            {row["opponent_agent_id"] for row in historical}
        )
        >= 6,
        "historical_role_rate_at_least_0.80": historical_role_rate is not None
        and historical_role_rate >= 0.80,
        "current_role_rate_at_least_0.80": current_role_rate is not None
        and current_role_rate >= 0.80,
    }
    transfer_gates = {
        "validation_balanced_accuracy_at_least_0.75": (
            validation_metrics["balanced_accuracy"] or 0.0
        )
        >= 0.75,
        "validation_precision_at_least_0.75": (
            validation_metrics["renewable_precision"] or 0.0
        )
        >= 0.75,
        "validation_recall_at_least_0.75": (
            validation_metrics["renewable_recall"] or 0.0
        )
        >= 0.75,
        "validation_nonrenewable_recall_at_least_0.60": (
            validation_metrics["nonrenewable_recall"] or 0.0
        )
        >= 0.60,
        "validation_constant_advantage_at_least_0.10": (
            validation_advantage is not None and validation_advantage >= 0.10
        ),
    }

    class_support_gates = (
        "discovery_at_least_4_each",
        "validation_at_least_3_each",
        "both_seats",
        "at_least_6_opponents",
    )
    role_gates = (
        "historical_role_rate_at_least_0.80",
        "current_role_rate_at_least_0.80",
    )
    if not all(integrity_gates.values()):
        decision = "quarantine_integrity_failure"
    elif not all(support_gates[key] for key in class_support_gates):
        decision = "support_failure_no_selector_or_integration"
    elif not all(support_gates[key] for key in role_gates):
        decision = "reject_role_consistency"
    elif not all(transfer_gates.values()):
        decision = "reject_static_opening_selector"
    else:
        decision = "pass_open_d86b_local_challenger"

    return {
        "schema": 1,
        "scope": "D86a passive open-replay behavior audit; no platform or sealed access",
        "agent_id": AGENT_ID,
        "input_hashes": {
            "historical_analysis": hashlib.sha256(
                HISTORICAL_ANALYSIS.read_bytes()
            ).hexdigest(),
            **hashes,
        },
        "counts": {
            "historical": len(historical),
            "discovery": len(discovery),
            "validation": len(validation),
            "current_consumed": len(current),
            "discovery_renewable": discovery_positive,
            "validation_renewable": validation_positive,
            "current_renewable": len(current_renewable),
        },
        "integrity": {"gates": integrity_gates, "reference": reference},
        "role_consistency": {
            "historical_renewable_n": len(historical_renewable),
            "historical_role_rate": historical_role_rate,
            "current_renewable_n": len(current_renewable),
            "current_role_rate": current_role_rate,
        },
        "selector": {
            "depth_two_fit": depth_two,
            "best_stump_fit": stump,
            "constant_fit": constant,
            "selected_reason": selected_reason,
            "selected_model": selected_model,
            "discovery": discovery_metrics,
            "validation": validation_metrics,
            "validation_constant": validation_constant,
            "validation_balanced_accuracy_advantage": validation_advantage,
            "current_consumed_descriptive": current_metrics,
            "leaves_discovery": leaf_summaries(discovery, selected_model),
            "leaves_validation": leaf_summaries(validation, selected_model),
        },
        "feature_distributions": {
            "discovery": feature_distributions(discovery),
            "validation": feature_distributions(validation),
        },
        "outcomes_observational": {
            "discovery": outcome_summary(discovery),
            "validation": outcome_summary(validation),
            "current_consumed": outcome_summary(current),
        },
        "support_gates": support_gates,
        "transfer_gates": transfer_gates,
        "decision": decision,
        "rows": rows,
    }


def write_atomic(path: Path, content: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rows-a", type=Path, required=True)
    parser.add_argument("--rows-b", type=Path, required=True)
    args = parser.parse_args()

    rows_a = analyze_all(args.jobs)
    rows_b = analyze_all(1)
    content_a = canonical_rows(rows_a)
    content_b = canonical_rows(rows_b)
    repeat_exact = content_a == content_b
    write_atomic(args.rows_a, content_a)
    write_atomic(args.rows_b, content_b)
    result = build_result(
        rows_a,
        repeat_exact,
        {
            "rows_a": sha256_bytes(content_a),
            "rows_b": sha256_bytes(content_b),
        },
    )
    write_atomic(args.output, (json.dumps(result, indent=1) + "\n").encode())
    print(json.dumps({
        "decision": result["decision"],
        "counts": result["counts"],
        "support_gates": result["support_gates"],
        "transfer_gates": result["transfer_gates"],
        "selected_model": result["selector"]["selected_model"],
        "validation": result["selector"]["validation"],
        "current": result["selector"]["current_consumed_descriptive"],
    }, indent=2))


if __name__ == "__main__":
    main()
