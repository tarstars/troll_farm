#!/usr/bin/env python3
"""Agent-held opening/state prediction of current top-policy third-worker creation."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import (  # noqa: E402
    atomic_write_new,
    load_open_inputs,
    read_jsonl,
    sha256_file,
)
from cgauto.recent_resident_field_census import (  # noqa: E402
    decoded_states,
    event_amount,
    successful_events,
)
from cgauto.top_player_opening_analysis import (  # noqa: E402
    analyze_players,
    opening_features,
)


REPO = Path(__file__).resolve().parent.parent
EXPECTED_SNAPSHOT = "20260721T105508Z-d61p"
PROTOCOL = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d63a-agent-held-workforce-transition-protocol-2026-07-21.md"
)
FIELD_REPORT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d61p-field-transfer-20260721T105508Z.json"
)
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
FRUITS = ITEMS[:4]
TALENTS = ("movement", "carry", "harvest", "chop")
L2_LAMBDA = 1.0
MAX_ITERATIONS = 100
STEP_TOLERANCE = 1e-9


def agent_bucket(agent_id: int) -> int:
    digest = hashlib.sha256(f"d63-agent:{agent_id}".encode()).hexdigest()
    return int(digest, 16) % 10


def agent_partition(agent_id: int) -> str:
    return "discovery" if agent_bucket(agent_id) <= 5 else "validation"


def score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[5]


def selected_player_rows(game: dict, selected_ids: set[int]) -> list[dict]:
    return [
        row
        for row in game["players"]
        if row.get("agentId") is not None and int(row["agentId"]) in selected_ids
    ]


def carrying_features(state: dict, player: int, prefix: str) -> dict[str, float]:
    units = [unit for unit in state["units"] if int(unit["player"]) == player]
    totals = [sum(int(unit["carry"][index]) for unit in units) for index in range(6)]
    result = {
        f"{prefix}_carry_{item.lower()}": float(totals[index])
        for index, item in enumerate(ITEMS)
    }
    result[f"{prefix}_carrying_workers"] = float(
        sum(any(int(value) > 0 for value in unit["carry"]) for unit in units)
    )
    return result


def event_features(events: list[dict], prefix: str, through: int = 100) -> dict[str, float]:
    result = {
        f"{prefix}_successful_trains": float(event_amount(events, "TRAIN", through)),
        f"{prefix}_successful_plants": float(event_amount(events, "PLANT", through)),
        f"{prefix}_harvested_amount": float(event_amount(events, "HARVEST", through)),
        f"{prefix}_chops_landed": float(event_amount(events, "CHOP", through)),
        f"{prefix}_dropped_amount": float(event_amount(events, "DROP", through)),
    }
    for item in FRUITS:
        result[f"{prefix}_planted_{item.lower()}"] = float(
            sum(
                event["amount"]
                for event in events
                if event["kind"] == "PLANT"
                and event.get("item") == item
                and event["turn"] <= through
            )
        )
    return result


def board_features(state: dict) -> dict[str, float]:
    plants = state["plants"]
    result = {
        "board_plant_count": float(len(plants)),
        "board_fruit_total": float(sum(int(plant["fruits"]) for plant in plants)),
        "board_health_total": float(sum(int(plant["health"]) for plant in plants)),
        "board_size_total": float(sum(int(plant["size"]) for plant in plants)),
        "board_ripe_count": float(sum(int(plant["fruits"]) > 0 for plant in plants)),
    }
    for item in FRUITS:
        selected = [plant for plant in plants if plant["type"] == item]
        result[f"board_{item.lower()}_count"] = float(len(selected))
        result[f"board_{item.lower()}_fruit"] = float(
            sum(int(plant["fruits"]) for plant in selected)
        )
    return result


def worker_features(state: dict, player: int, analysis: dict) -> dict[str, float]:
    metadata = {int(worker["unit_id"]): worker for worker in analysis["workers"]}
    units = sorted(
        (unit for unit in state["units"] if int(unit["player"]) == player),
        key=lambda unit: (metadata[int(unit["id"])]["ordinal"], int(unit["id"])),
    )
    if len(units) != 2:
        raise ValueError(f"turn-100 eligible row has {len(units)} own workers, expected 2")
    specs = [[unit["ms"], unit["cc"], unit["hp"], unit["chop"]] for unit in units]
    result = {}
    for ordinal, spec in enumerate(specs):
        for index, talent in enumerate(TALENTS):
            result[f"worker{ordinal}_{talent}"] = float(spec[index])
    for index, talent in enumerate(TALENTS):
        result[f"workers_sum_{talent}"] = float(sum(spec[index] for spec in specs))
        result[f"workers_max_{talent}"] = float(max(spec[index] for spec in specs))
    return result


def numeric_opening(raw: dict) -> dict[str, float | None]:
    result = {}
    for key, value in raw.items():
        if value is None or isinstance(value, (bool, int, float)):
            result[f"open_{key}"] = None if value is None else float(value)
    return result


def turn100_features(
    opening: dict,
    states: list[dict],
    player: int,
    analyses: dict[int, dict],
    events: dict[int, list[dict]],
) -> dict[str, float | None]:
    state = states[100]
    opponent = 1 - player
    own_inventory = [int(value) for value in state["inventories"][player]]
    opponent_inventory = [int(value) for value in state["inventories"][opponent]]
    features: dict[str, float | None] = numeric_opening(opening)
    for prefix, inventory in (("own", own_inventory), ("opponent", opponent_inventory)):
        for index, item in enumerate(ITEMS):
            features[f"{prefix}_bank_{item.lower()}"] = float(inventory[index])
        features[f"{prefix}_bank_score"] = float(score(inventory))
    features["bank_score_gap"] = float(score(own_inventory) - score(opponent_inventory))
    features["bank_wood_gap"] = float(own_inventory[5] - opponent_inventory[5])
    features.update(carrying_features(state, player, "own"))
    features.update(carrying_features(state, opponent, "opponent"))
    features.update(worker_features(state, player, analyses[player]))
    features["opponent_worker_count"] = float(
        sum(int(unit["player"]) == opponent for unit in state["units"])
    )
    features.update(board_features(state))
    features.update(event_features(events[player], "own"))
    features.update(event_features(events[opponent], "opponent"))
    first_train = analyses[player]["training_events"][0]
    features["first_train_turn"] = float(first_train["turn"])
    for index, talent in enumerate(TALENTS):
        features[f"first_train_{talent}"] = float(first_train["spec"][index])
    return features


def extract_task(task: dict) -> list[dict]:
    game = task["game"]
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    decoded_map, states, unknown = decoded_states(raw, trajectory)
    if unknown or len(states) != len(trajectory) + 1:
        raise ValueError(f"state decode mismatch in game {game['gameId']}")
    expected_final = [
        list(game["per_player"][str(player)]["final_inv"]) for player in (0, 1)
    ]
    if states[-1]["inventories"] != expected_final:
        raise ValueError(f"final inventory mismatch in game {game['gameId']}")
    analyses = analyze_players(states, trajectory)
    events = successful_events(raw["frames"])
    selected = selected_player_rows(game, set(task["top_source_ids"]))
    rows = []
    for player_row in selected:
        player = int(player_row["index"])
        agent_id = int(player_row["agentId"])
        analysis = analyses[player]
        third_turn = next(
            (
                int(event["turn"])
                for event in analysis["training_events"]
                if int(event["ordinal"]) == 2
            ),
            None,
        )
        opening = opening_features(decoded_map, states[0], player)
        row = {
            "game_id": int(game["gameId"]),
            "agent_id": agent_id,
            "agent_name": player_row.get("name"),
            "leaderboard_rank": player_row.get("localRank"),
            "seat": player,
            "partition": agent_partition(agent_id),
            "agent_bucket": agent_bucket(agent_id),
            "turns": len(trajectory),
            "third_worker_turn": third_turn,
            "opening_label": int(third_turn is not None),
            "opening_features": numeric_opening(opening),
            "turn100_eligible": False,
            "turn100_label": None,
            "turn100_features": None,
            "integrity": {
                "trajectory_turns": len(trajectory),
                "decoded_turns": len(states) - 1,
                "unknown_diff_updates": unknown,
                "final_inventory_exact": True,
            },
        }
        if len(trajectory) >= 150 and len(states) > 100:
            workers_at_100 = sum(
                int(unit["player"]) == player for unit in states[100]["units"]
            )
            if workers_at_100 == 2 and (third_turn is None or third_turn > 100):
                row["turn100_eligible"] = True
                row["turn100_label"] = int(third_turn is not None)
                row["turn100_features"] = turn100_features(
                    opening, states, player, analyses, events
                )
        rows.append(row)
    return rows


def materialize_features(rows: list[dict], field: str) -> tuple[list[str], np.ndarray]:
    mappings = [row[field] for row in rows]
    if any(mapping is None for mapping in mappings):
        raise ValueError(f"missing feature mapping in {field}")
    keys = sorted({key for mapping in mappings for key in mapping})
    feature_names = []
    columns = []
    for key in keys:
        values = [mapping.get(key) for mapping in mappings]
        numeric = [value for value in values if isinstance(value, (bool, int, float))]
        if not numeric:
            continue
        missing = [value is None or not isinstance(value, (bool, int, float)) for value in values]
        feature_names.append(key)
        columns.append(np.asarray([-1.0 if miss else float(value) for value, miss in zip(values, missing)]))
        if any(missing):
            feature_names.append(f"{key}__missing")
            columns.append(np.asarray(missing, dtype=float))
    if not columns:
        raise ValueError(f"no numeric features in {field}")
    return feature_names, np.column_stack(columns)


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40.0, 40.0)))


def fit_logistic(x: np.ndarray, y: np.ndarray) -> dict:
    means = x.mean(axis=0)
    scales = x.std(axis=0)
    scales[scales == 0] = 1.0
    normalized = (x - means) / scales
    design = np.column_stack((np.ones(len(normalized)), normalized))
    beta = np.zeros(design.shape[1], dtype=float)
    converged = False
    iterations = 0
    maximum_step = None
    penalty = np.ones(design.shape[1], dtype=float)
    penalty[0] = 0.0
    for iteration in range(1, MAX_ITERATIONS + 1):
        probabilities = sigmoid(design @ beta)
        gradient = design.T @ (probabilities - y) / len(y) + L2_LAMBDA * penalty * beta
        weights = probabilities * (1.0 - probabilities)
        hessian = (design.T * weights) @ design / len(y)
        hessian += np.diag(L2_LAMBDA * penalty)
        step = np.linalg.solve(hessian, gradient)
        beta -= step
        iterations = iteration
        maximum_step = float(np.max(np.abs(step)))
        if maximum_step <= STEP_TOLERANCE:
            converged = True
            break
    return {
        "means": means,
        "scales": scales,
        "beta": beta,
        "converged": converged,
        "iterations": iterations,
        "maximum_step": maximum_step,
    }


def predict(model: dict, x: np.ndarray) -> np.ndarray:
    normalized = (x - model["means"]) / model["scales"]
    design = np.column_stack((np.ones(len(normalized)), normalized))
    return sigmoid(design @ model["beta"])


def roc_auc(y: np.ndarray, probabilities: np.ndarray) -> float | None:
    positives = int(y.sum())
    negatives = len(y) - positives
    if not positives or not negatives:
        return None
    order = np.argsort(probabilities, kind="mergesort")
    ranks = np.empty(len(y), dtype=float)
    start = 0
    while start < len(y):
        end = start + 1
        while end < len(y) and probabilities[order[end]] == probabilities[order[start]]:
            end += 1
        average_rank = (start + 1 + end) / 2.0
        ranks[order[start:end]] = average_rank
        start = end
    rank_sum = float(ranks[y == 1].sum())
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def metrics(y: np.ndarray, probabilities: np.ndarray) -> dict:
    predicted = probabilities >= 0.5
    positive = y == 1
    negative = ~positive
    tp = int(np.sum(predicted & positive))
    tn = int(np.sum(~predicted & negative))
    fp = int(np.sum(predicted & negative))
    fn = int(np.sum(~predicted & positive))
    sensitivity = tp / (tp + fn) if tp + fn else None
    specificity = tn / (tn + fp) if tn + fp else None
    balanced = (
        (sensitivity + specificity) / 2.0
        if sensitivity is not None and specificity is not None
        else None
    )
    return {
        "rows": len(y),
        "positives": int(y.sum()),
        "negatives": int(len(y) - y.sum()),
        "prevalence": float(y.mean()) if len(y) else None,
        "roc_auc": roc_auc(y, probabilities),
        "balanced_accuracy_at_0_5": balanced,
        "sensitivity_at_0_5": sensitivity,
        "specificity_at_0_5": specificity,
        "brier_score": float(np.mean((probabilities - y) ** 2)),
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
    }


def agent_label_support(rows: list[dict], label_field: str) -> dict:
    positive = {row["agent_id"] for row in rows if int(row[label_field]) == 1}
    negative = {row["agent_id"] for row in rows if int(row[label_field]) == 0}
    return {
        "positive_agents": len(positive),
        "negative_agents": len(negative),
        "positive_agent_ids": sorted(positive),
        "negative_agent_ids": sorted(negative),
    }


def model_report(
    rows: list[dict], feature_field: str, label_field: str, model_name: str
) -> dict:
    feature_names, x = materialize_features(rows, feature_field)
    y = np.asarray([int(row[label_field]) for row in rows], dtype=int)
    discovery_indices = [index for index, row in enumerate(rows) if row["partition"] == "discovery"]
    validation_indices = [index for index, row in enumerate(rows) if row["partition"] == "validation"]
    discovery_x = x[discovery_indices]
    discovery_y = y[discovery_indices]
    validation_x = x[validation_indices]
    validation_y = y[validation_indices]
    if not len(discovery_y) or len(set(discovery_y.tolist())) != 2:
        raise ValueError(f"{model_name} discovery partition lacks both labels")
    model = fit_logistic(discovery_x, discovery_y)
    discovery_probabilities = predict(model, discovery_x)
    validation_probabilities = predict(model, validation_x)
    coefficient_rows = [
        {"feature": feature, "standardized_coefficient": float(coefficient)}
        for feature, coefficient in zip(feature_names, model["beta"][1:])
    ]
    coefficient_rows.sort(
        key=lambda row: abs(row["standardized_coefficient"]), reverse=True
    )
    discovery_rows = [rows[index] for index in discovery_indices]
    validation_rows = [rows[index] for index in validation_indices]
    return {
        "model": model_name,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "fit": {
            "l2_lambda": L2_LAMBDA,
            "iterations": model["iterations"],
            "converged": model["converged"],
            "maximum_step": model["maximum_step"],
            "intercept": float(model["beta"][0]),
            "top_standardized_coefficients": coefficient_rows[:20],
        },
        "discovery": {
            **metrics(discovery_y, discovery_probabilities),
            "agent_support": agent_label_support(discovery_rows, label_field),
        },
        "validation": {
            **metrics(validation_y, validation_probabilities),
            "agent_support": agent_label_support(validation_rows, label_field),
        },
        "predictions": [
            {
                "game_id": rows[index]["game_id"],
                "agent_id": rows[index]["agent_id"],
                "partition": rows[index]["partition"],
                "label": int(y[index]),
                "probability": float(
                    discovery_probabilities[discovery_indices.index(index)]
                    if index in discovery_indices
                    else validation_probabilities[validation_indices.index(index)]
                ),
            }
            for index in range(len(rows))
        ],
    }


def gate_model_a(report: dict) -> dict:
    discovery = report["discovery"]
    validation = report["validation"]
    support = {
        "at_least_30_rows_each": discovery["rows"] >= 30 and validation["rows"] >= 30,
        "at_least_10_labels_each": min(
            discovery["positives"],
            discovery["negatives"],
            validation["positives"],
            validation["negatives"],
        )
        >= 10,
        "validation_labels_span_3_agents_each": validation["agent_support"][
            "positive_agents"
        ]
        >= 3
        and validation["agent_support"]["negative_agents"] >= 3,
    }
    performance = {
        "validation_auc_at_least_0_65": (validation["roc_auc"] or 0.0) >= 0.65,
        "validation_balanced_accuracy_at_least_0_60": (
            validation["balanced_accuracy_at_0_5"] or 0.0
        )
        >= 0.60,
    }
    enough = all(support.values())
    passed = enough and all(performance.values())
    return {
        "support": support,
        "performance": performance,
        "status": "pass" if passed else ("fail" if enough else "insufficient"),
    }


def gate_model_b(report: dict) -> dict:
    discovery = report["discovery"]
    validation = report["validation"]
    support = {
        "at_least_30_rows_each": discovery["rows"] >= 30 and validation["rows"] >= 30,
        "discovery_at_least_8_positive_15_negative": discovery["positives"] >= 8
        and discovery["negatives"] >= 15,
        "validation_at_least_8_positive_15_negative": validation["positives"] >= 8
        and validation["negatives"] >= 15,
        "validation_labels_span_3_agents_each": validation["agent_support"][
            "positive_agents"
        ]
        >= 3
        and validation["agent_support"]["negative_agents"] >= 3,
    }
    performance = {
        "validation_auc_at_least_0_70": (validation["roc_auc"] or 0.0) >= 0.70,
        "validation_balanced_accuracy_at_least_0_60": (
            validation["balanced_accuracy_at_0_5"] or 0.0
        )
        >= 0.60,
    }
    enough = all(support.values())
    passed = enough and all(performance.values())
    return {
        "support": support,
        "performance": performance,
        "status": "pass" if passed else ("fail" if enough else "insufficient"),
    }


def build_report(loaded: dict, rows: list[dict]) -> dict:
    rows.sort(key=lambda row: (row["agent_id"], row["game_id"], row["seat"]))
    if len(rows) != 200 or len({row["agent_id"] for row in rows}) != 20:
        raise ValueError("D63a expected 200 appearances from exactly 20 agents")
    per_agent = Counter(row["agent_id"] for row in rows)
    if set(per_agent.values()) != {10}:
        raise ValueError("D63a expected exactly ten appearances per selected agent")
    opening_report = model_report(
        rows, "opening_features", "opening_label", "opening_selector"
    )
    turn100_rows = [row for row in rows if row["turn100_eligible"]]
    turn100_report = model_report(
        turn100_rows,
        "turn100_features",
        "turn100_label",
        "turn100_capitalization_selector",
    )
    opening_gate = gate_model_a(opening_report)
    turn100_gate = gate_model_b(turn100_report)
    if turn100_gate["status"] == "pass":
        next_representation = "state_conditioned_capitalization_action"
    elif opening_gate["status"] == "pass":
        next_representation = "opening_recipe_portfolio_selector"
    else:
        next_representation = "recurrent_sequence_or_policy_portfolio"
    return {
        "schema": "troll-farm-d63a-agent-held-workforce-transition-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_id": loaded["snapshot_id"],
        "scope": (
            "outcome-blind agent-held behavior transfer audit on open current top-20 "
            "appearances; no value or candidate claim"
        ),
        "inputs": {
            "source_open_loader": loaded["input_hashes"],
            "d63_protocol": sha256_file(PROTOCOL),
            "d61p_field_report": sha256_file(FIELD_REPORT),
            "d63_analyzer": sha256_file(Path(__file__)),
        },
        "integrity": {
            "qa_pass": loaded["qa"]["pass"],
            "appearances": len(rows),
            "agents": len(per_agent),
            "appearances_per_agent": dict(sorted(per_agent.items())),
            "agent_partition_counts": dict(
                sorted(Counter(row["partition"] for row in rows).items())
            ),
            "all_turn_streams_exact": all(
                row["integrity"]["trajectory_turns"]
                == row["integrity"]["decoded_turns"]
                for row in rows
            ),
            "unknown_diff_updates": sum(
                row["integrity"]["unknown_diff_updates"] for row in rows
            ),
            "confirmation_products_read": False,
        },
        "behavior": {
            "third_worker_appearances": sum(row["opening_label"] for row in rows),
            "third_worker_rate": sum(row["opening_label"] for row in rows) / len(rows),
            "third_worker_turns": dict(
                sorted(
                    Counter(
                        row["third_worker_turn"]
                        for row in rows
                        if row["third_worker_turn"] is not None
                    ).items()
                )
            ),
            "turn100_eligible_rows": len(turn100_rows),
            "turn100_later_third_workers": sum(
                int(row["turn100_label"]) for row in turn100_rows
            ),
        },
        "models": {
            "opening": opening_report,
            "turn100": turn100_report,
        },
        "gates": {
            "opening": opening_gate,
            "turn100": turn100_gate,
        },
        "decision": {
            "next_representation": next_representation,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
        "rows": rows,
    }


def analyze(snapshot: Path, output: Path, jobs: int) -> dict:
    if not 1 <= jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    loaded = load_open_inputs(snapshot)
    if loaded["snapshot_id"] != EXPECTED_SNAPSHOT:
        raise ValueError(f"D63a is frozen to snapshot {EXPECTED_SNAPSHOT}")
    tasks = [task for task in loaded["tasks"] if task["top_source_ids"]]
    if jobs == 1:
        nested = [extract_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            nested = list(executor.map(extract_task, tasks, chunksize=2))
    rows = [row for group in nested for row in group]
    report = build_report(loaded, rows)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = analyze(args.snapshot, args.output, args.jobs)
    print(
        json.dumps(
            {
                "snapshot": report["snapshot_id"],
                "behavior": report["behavior"],
                "gates": {
                    name: value["status"] for name, value in report["gates"].items()
                },
                "next": report["decision"]["next_representation"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
