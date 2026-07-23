#!/usr/bin/env python3
"""Audit deployable observability of imminent attacks on resident-owned crops."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import (  # noqa: E402
    atomic_write_new,
    load_open_inputs,
    read_jsonl,
    sha256_file,
)
from cgauto.analyze_d63a_workforce_transition import (  # noqa: E402
    fit_logistic,
    materialize_features,
    metrics,
    predict,
)
from cgauto.recent_resident_field_census import (  # noqa: E402
    crop_provenance,
    decoded_states,
    score,
)
from cgauto.top_player_opening_analysis import adjacent, bfs, terrain  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
SNAPSHOT = REPO / "data/raw/snapshots/20260721T105508Z-d61p"
PROTOCOL = ANALYSIS / "d78a-opponent-commitment-observability-protocol-2026-07-21.md"
OUTPUT = ANALYSIS / "d78a-opponent-commitment-observability-result.json"
ROWS_OUTPUT = ANALYSIS / "d78a-opponent-commitment-rows.tsv"
EXPECTED_SNAPSHOT = "20260721T105508Z-d61p"
EXPECTED_RESIDENT = 6_561_795
HORIZON = 8
HISTORY = 6
ITEMS = ("plum", "lemon", "apple", "banana", "iron", "wood")
FRUITS = ITEMS[:4]
FRUIT_NAMES = tuple(item.upper() for item in FRUITS)


def hash_mod(label: str, modulus: int) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest(), 16) % modulus


def opponent_partition(user_id: int) -> str:
    return "discovery" if hash_mod(f"d78-opponent:{user_id}", 10) <= 5 else "validation"


def retain_row(game_id: int, cell: tuple[int, int], turn: int) -> bool:
    return hash_mod(f"d78-row:{game_id}:{cell[0]}:{cell[1]}:{turn}", 2) == 0


def unit_free(unit: dict) -> int:
    return max(0, int(unit["cc"]) - sum(int(value) for value in unit["carry"]))


def plant_at(state: dict, cell: tuple[int, int]) -> dict | None:
    return next(
        (
            plant
            for plant in state["plants"]
            if (int(plant["x"]), int(plant["y"])) == cell
        ),
        None,
    )


def side_units(state: dict, player: int) -> list[dict]:
    return [unit for unit in state["units"] if int(unit["player"]) == player]


def distance_for_unit(distances: dict[tuple[int, int], int], unit: dict) -> int:
    return int(distances.get((int(unit["x"]), int(unit["y"])), 50))


def target_side_metrics(
    state: dict,
    player: int,
    distances: dict[tuple[int, int], int],
    *,
    require_chop: bool,
) -> dict:
    units = side_units(state, player)
    eligible = [
        unit
        for unit in units
        if not require_chop or (int(unit["chop"]) > 0 and unit_free(unit) > 0)
    ]
    ranked = sorted(
        eligible,
        key=lambda unit: (
            math.ceil(distance_for_unit(distances, unit) / max(1, int(unit["ms"]))),
            distance_for_unit(distances, unit),
            int(unit["id"]),
        ),
    )
    nearest = ranked[0] if ranked else None
    nearest_distance = distance_for_unit(distances, nearest) if nearest else 50
    nearest_eta = (
        math.ceil(nearest_distance / max(1, int(nearest["ms"]))) if nearest else 50
    )
    return {
        "worker_count": len(units),
        "eligible_count": len(eligible),
        "nearest_id": int(nearest["id"]) if nearest else None,
        "nearest_distance": nearest_distance,
        "nearest_eta": nearest_eta,
        "nearest_chop": int(nearest["chop"]) if nearest else 0,
        "nearest_free": unit_free(nearest) if nearest else 0,
        "on_target": sum(distance_for_unit(distances, unit) == 0 for unit in eligible),
        "within_1": sum(distance_for_unit(distances, unit) <= 1 for unit in eligible),
        "within_2": sum(distance_for_unit(distances, unit) <= 2 for unit in eligible),
        "within_4": sum(distance_for_unit(distances, unit) <= 4 for unit in eligible),
        "wood_carry": sum(int(unit["carry"][5]) for unit in units),
    }


def aggregate_features(state: dict, resident: int, attacker: int) -> dict[str, float]:
    result: dict[str, float] = {
        "agg_turn": float(state["resolved_turn"]) / 300.0,
        "agg_plant_count": float(len(state["plants"])) / 40.0,
        "agg_fruit_total": float(
            sum(int(plant["fruits"]) for plant in state["plants"])
        )
        / 80.0,
    }
    for prefix, player in (("resident", resident), ("attacker", attacker)):
        inventory = [int(value) for value in state["inventories"][player]]
        units = side_units(state, player)
        result[f"agg_{prefix}_score"] = float(score(inventory)) / 400.0
        result[f"agg_{prefix}_workers"] = float(len(units)) / 5.0
        for index, item in enumerate(ITEMS):
            result[f"agg_{prefix}_bank_{item}"] = float(inventory[index]) / 20.0
            result[f"agg_{prefix}_carry_{item}"] = float(
                sum(int(unit["carry"][index]) for unit in units)
            ) / 20.0
        for talent in ("ms", "cc", "hp", "chop"):
            result[f"agg_{prefix}_{talent}_sum"] = float(
                sum(int(unit[talent]) for unit in units)
            ) / 20.0
        result[f"agg_{prefix}_free_sum"] = float(sum(unit_free(unit) for unit in units)) / 20.0
    result["agg_score_gap"] = (
        result["agg_resident_score"] - result["agg_attacker_score"]
    )
    for fruit in FRUIT_NAMES:
        selected = [plant for plant in state["plants"] if plant["type"] == fruit]
        key = fruit.lower()
        result[f"agg_board_{key}_plants"] = float(len(selected)) / 20.0
        result[f"agg_board_{key}_fruit"] = float(
            sum(int(plant["fruits"]) for plant in selected)
        ) / 40.0
    resident_cells = {
        (int(unit["x"]), int(unit["y"])) for unit in side_units(state, resident)
    }
    attacker_cells = {
        (int(unit["x"]), int(unit["y"])) for unit in side_units(state, attacker)
    }
    result["agg_contested_worker_cells"] = float(len(resident_cells & attacker_cells)) / 5.0
    return result


def spatial_features(
    aggregate: dict[str, float],
    state: dict,
    board: dict,
    record: dict,
    resident: int,
    attacker: int,
    distances: dict[tuple[int, int], int],
) -> dict[str, float]:
    cell = tuple(int(value) for value in record["cell"])
    plant = plant_at(state, cell)
    if plant is None:
        raise ValueError("D78 spatial row references an absent crop")
    result = dict(aggregate)
    for fruit in FRUIT_NAMES:
        result[f"target_type_{fruit.lower()}"] = float(record["type"] == fruit)
    result.update(
        {
            "target_age": float(int(state["resolved_turn"]) - int(record["birth_turn"])) / 100.0,
            "target_x": float(cell[0]) / 21.0,
            "target_y": float(cell[1]) / 10.0,
            "target_size": float(plant["size"]) / 10.0,
            "target_health": float(plant["health"]) / 20.0,
            "target_fruits": float(plant["fruits"]) / 20.0,
            "target_cooldown": float(plant["cooldown"]) / 20.0,
            "target_adjacent_water": float(any(neighbor in board["water"] for neighbor in adjacent(cell))),
        }
    )
    for prefix, player, require_chop in (
        ("attack", attacker, True),
        ("defend", resident, False),
    ):
        values = target_side_metrics(
            state, player, distances, require_chop=require_chop
        )
        for key in (
            "eligible_count",
            "nearest_distance",
            "nearest_eta",
            "nearest_chop",
            "nearest_free",
            "on_target",
            "within_1",
            "within_2",
            "within_4",
        ):
            denominator = 50.0 if key in {"nearest_distance", "nearest_eta"} else 5.0
            result[f"spatial_{prefix}_{key}"] = float(values[key]) / denominator
    for prefix, shack in (("resident", board["shacks"][resident]), ("attacker", board["shacks"][attacker])):
        doors = [door for door in adjacent(shack) if door in board["walkable"]]
        result[f"spatial_{prefix}_shack_distance"] = float(
            bfs(board["walkable"], doors).get(cell, 50)
        ) / 50.0
    return result


def historical_value(
    states: list[dict],
    turn: int,
    offset: int,
    birth_turn: int,
    getter,
) -> float | None:
    previous = turn - offset
    if previous < birth_turn or previous < 0:
        return None
    return getter(states[previous])


def history_features(
    spatial: dict[str, float],
    states: list[dict],
    turn: int,
    record: dict,
    resident: int,
    attacker: int,
    distances: dict[tuple[int, int], int],
) -> dict[str, float | None]:
    result: dict[str, float | None] = dict(spatial)
    cell = tuple(int(value) for value in record["cell"])
    birth = int(record["birth_turn"])
    current_plant = plant_at(states[turn], cell)
    if current_plant is None:
        raise ValueError("D78 history row references an absent crop")

    def plant_field(state: dict, field: str) -> float | None:
        plant = plant_at(state, cell)
        return None if plant is None else float(plant[field])

    current_attack = target_side_metrics(
        states[turn], attacker, distances, require_chop=True
    )
    current_defend = target_side_metrics(
        states[turn], resident, distances, require_chop=False
    )
    for offset in (1, 3, 6):
        old_health = historical_value(
            states, turn, offset, birth, lambda state: plant_field(state, "health")
        )
        old_fruits = historical_value(
            states, turn, offset, birth, lambda state: plant_field(state, "fruits")
        )
        old_attack = historical_value(
            states,
            turn,
            offset,
            birth,
            lambda state: float(
                target_side_metrics(state, attacker, distances, require_chop=True)[
                    "nearest_distance"
                ]
            ),
        )
        old_defend = historical_value(
            states,
            turn,
            offset,
            birth,
            lambda state: float(
                target_side_metrics(state, resident, distances, require_chop=False)[
                    "nearest_distance"
                ]
            ),
        )
        old_attack_metrics = (
            None
            if turn - offset < birth
            else target_side_metrics(
                states[turn - offset], attacker, distances, require_chop=True
            )
        )
        result[f"hist_health_loss_{offset}"] = (
            None
            if old_health is None
            else (old_health - float(current_plant["health"])) / 20.0
        )
        result[f"hist_fruit_change_{offset}"] = (
            None
            if old_fruits is None
            else (float(current_plant["fruits"]) - old_fruits) / 20.0
        )
        result[f"hist_attack_approach_{offset}"] = (
            None
            if old_attack is None
            else (old_attack - float(current_attack["nearest_distance"])) / 50.0
        )
        result[f"hist_defend_approach_{offset}"] = (
            None
            if old_defend is None
            else (old_defend - float(current_defend["nearest_distance"])) / 50.0
        )
        result[f"hist_nearest_same_{offset}"] = (
            None
            if old_attack_metrics is None
            else float(old_attack_metrics["nearest_id"] == current_attack["nearest_id"])
        )
        result[f"hist_attack_wood_gain_{offset}"] = (
            None
            if old_attack_metrics is None
            else (
                float(current_attack["wood_carry"])
                - float(old_attack_metrics["wood_carry"])
            )
            / 20.0
        )

    history_states = states[max(birth, turn - HISTORY) : turn + 1]
    attack_metrics = [
        target_side_metrics(state, attacker, distances, require_chop=True)
        for state in history_states
    ]
    distances_series = [int(values["nearest_distance"]) for values in attack_metrics]
    approach_steps = sum(
        right < left for left, right in zip(distances_series, distances_series[1:])
    )
    streak = 0
    for left, right in reversed(list(zip(distances_series, distances_series[1:]))):
        if right < left:
            streak += 1
        else:
            break
    result["hist_attack_approach_steps_6"] = float(approach_steps) / 6.0
    result["hist_attack_approach_streak"] = float(streak) / 6.0
    result["hist_attack_on_target_exposure_6"] = float(
        sum(int(values["on_target"]) > 0 for values in attack_metrics)
    ) / 7.0
    result["hist_attack_within2_exposure_6"] = float(
        sum(int(values["within_2"]) > 0 for values in attack_metrics)
    ) / 7.0
    result["hist_observed_steps"] = float(len(history_states) - 1) / 6.0
    return result


def extract_task(task: dict) -> dict:
    game = task["game"]
    resident_id = int(task["resident_agent_id"])
    resident_rows = [
        player for player in game["players"] if int(player.get("agentId", -1)) == resident_id
    ]
    if len(resident_rows) != 1:
        return {"rows": [], "integrity": None}
    resident_row = resident_rows[0]
    attacker_rows = [player for player in game["players"] if player is not resident_row]
    if len(attacker_rows) != 1 or attacker_rows[0].get("userId") is None:
        raise ValueError(f"D78 game {game['gameId']} lacks one identified attacker")
    attacker_row = attacker_rows[0]
    resident = int(resident_row["index"])
    attacker = int(attacker_row["index"])
    game_id = int(game["gameId"])
    user_id = int(attacker_row["userId"])
    agent_id = int(attacker_row["agentId"])

    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    decoded_map, states, unknown = decoded_states(raw, trajectory)
    expected_final = [
        list(game["per_player"][str(player)]["final_inv"]) for player in (0, 1)
    ]
    if len(states) != len(trajectory) + 1 or states[-1]["inventories"] != expected_final:
        raise ValueError(f"D78 decoded trajectory mismatch in game {game_id}")
    records, provenance_quality = crop_provenance(raw, trajectory, attacker)
    if (
        provenance_quality["unknown_diff_updates"] != 0
        or provenance_quality["decoded_turns"] != len(trajectory)
        or unknown != 0
    ):
        raise ValueError(f"D78 provenance/decode failure in game {game_id}")
    board = terrain(decoded_map)
    rows = []
    for crop_ordinal, record in enumerate(records):
        cell = tuple(int(value) for value in record["cell"])
        distances = bfs(board["walkable"], [cell])
        birth = int(record["birth_turn"])
        death = record["death_turn"]
        last_alive = len(trajectory) if death is None else int(death) - 1
        last_turn = min(last_alive, len(trajectory) - HORIZON)
        attacker_chops = {int(value) for value in record["our_chop_turns"]}
        resident_chops = {int(value) for value in record["opponent_chop_turns"]}
        for turn in range(birth, last_turn + 1):
            if not retain_row(game_id, cell, turn):
                continue
            plant = plant_at(states[turn], cell)
            if plant is None:
                raise ValueError(f"D78 selected absent crop in game {game_id}, turn {turn}")
            future_chops = sorted(
                value for value in attacker_chops if turn < value <= turn + HORIZON
            )
            aggregate = aggregate_features(states[turn], resident, attacker)
            spatial = spatial_features(
                aggregate,
                states[turn],
                board,
                record,
                resident,
                attacker,
                distances,
            )
            history = history_features(
                spatial,
                states,
                turn,
                record,
                resident,
                attacker,
                distances,
            )
            row_hash = hashlib.sha256(
                f"d78-row:{game_id}:{cell[0]}:{cell[1]}:{turn}".encode()
            ).hexdigest()
            terminal_chop = bool(
                death is not None
                and turn < int(death) <= turn + HORIZON
                and int(death) in attacker_chops
            )
            rows.append(
                {
                    "game_id": game_id,
                    "crop_ordinal": crop_ordinal,
                    "cell_x": cell[0],
                    "cell_y": cell[1],
                    "turn": turn,
                    "opponent_user_id": user_id,
                    "agent_id": user_id,
                    "source_agent_id": agent_id,
                    "partition": opponent_partition(user_id),
                    "label": int(bool(future_chops)),
                    "terminal_chop": int(terminal_chop),
                    "resident_future_chop": int(
                        any(turn < value <= turn + HORIZON for value in resident_chops)
                    ),
                    "row_hash": row_hash,
                    "aggregate_features": aggregate,
                    "spatial_features": spatial,
                    "history_features": history,
                }
            )
    return {
        "rows": rows,
        "integrity": {
            "game_id": game_id,
            "trajectory_turns": len(trajectory),
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": unknown,
            "final_inventory_exact": True,
            "resident_crops": len(records),
            "selected_rows": len(rows),
        },
    }


def account_support(rows: list[dict]) -> dict:
    positive = {row["opponent_user_id"] for row in rows if int(row["label"]) == 1}
    negative = {row["opponent_user_id"] for row in rows if int(row["label"]) == 0}
    return {
        "positive_accounts": len(positive),
        "negative_accounts": len(negative),
        "positive_account_ids": sorted(positive),
        "negative_account_ids": sorted(negative),
    }


def top_quintile(y: np.ndarray, probabilities: np.ndarray) -> dict:
    count = max(1, math.ceil(len(y) * 0.20))
    order = np.argsort(-probabilities, kind="mergesort")
    selected = order[:count]
    positives = int(y.sum())
    selected_positives = int(y[selected].sum())
    prevalence = positives / len(y)
    precision = selected_positives / count
    return {
        "rows": count,
        "positive_rows": selected_positives,
        "precision": precision,
        "recall": selected_positives / positives if positives else None,
        "lift": precision / prevalence if prevalence else None,
        "minimum_probability": float(probabilities[selected].min()),
    }


def fit_family(rows: list[dict], feature_field: str, label: str) -> dict:
    feature_names, x = materialize_features(rows, feature_field)
    y = np.asarray([int(row["label"]) for row in rows], dtype=int)
    discovery = np.asarray(
        [index for index, row in enumerate(rows) if row["partition"] == "discovery"],
        dtype=int,
    )
    validation = np.asarray(
        [index for index, row in enumerate(rows) if row["partition"] == "validation"],
        dtype=int,
    )
    model = fit_logistic(x[discovery], y[discovery])
    discovery_probabilities = predict(model, x[discovery])
    validation_probabilities = predict(model, x[validation])
    if not (
        np.isfinite(discovery_probabilities).all()
        and np.isfinite(validation_probabilities).all()
    ):
        raise ValueError(f"D78 {label} produces nonfinite probabilities")
    coefficients = [
        {"feature": name, "standardized_coefficient": float(value)}
        for name, value in zip(feature_names, model["beta"][1:])
    ]
    coefficients.sort(key=lambda row: abs(row["standardized_coefficient"]), reverse=True)

    def partition_report(indices: np.ndarray, probabilities: np.ndarray) -> dict:
        selected_rows = [rows[int(index)] for index in indices]
        return {
            **metrics(y[indices], probabilities),
            "top_quintile": top_quintile(y[indices], probabilities),
            "account_support": account_support(selected_rows),
        }

    return {
        "label": label,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "fit": {
            "l2_lambda": 1.0,
            "converged": bool(model["converged"]),
            "iterations": int(model["iterations"]),
            "maximum_step": float(model["maximum_step"]),
            "intercept": float(model["beta"][0]),
            "means": [float(value) for value in model["means"]],
            "scales": [float(value) for value in model["scales"]],
            "coefficients": [float(value) for value in model["beta"][1:]],
            "top_standardized_coefficients": coefficients[:20],
        },
        "discovery": partition_report(discovery, discovery_probabilities),
        "validation": partition_report(validation, validation_probabilities),
    }


def write_rows(path: Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    feature_names = sorted(
        {key for row in rows for key in row["history_features"]}
    )
    identity = (
        "game_id",
        "crop_ordinal",
        "cell_x",
        "cell_y",
        "turn",
        "opponent_user_id",
        "source_agent_id",
        "partition",
        "label",
        "terminal_chop",
        "resident_future_chop",
        "row_hash",
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as target:
            target.write("\t".join((*identity, *feature_names)) + "\n")
            for row in rows:
                values = [str(row[key]) for key in identity]
                for feature in feature_names:
                    value = row["history_features"].get(feature)
                    values.append("" if value is None else format(float(value), ".9g"))
                target.write("\t".join(values) + "\n")
            target.flush()
            os.fsync(target.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise FileExistsError(path) from None
    finally:
        temporary.unlink(missing_ok=True)


def build_report(loaded: dict, extracted: list[dict], rows_path: Path) -> dict:
    integrity_rows = [item["integrity"] for item in extracted if item["integrity"]]
    rows = [row for item in extracted for row in item["rows"]]
    rows.sort(
        key=lambda row: (
            row["opponent_user_id"],
            row["game_id"],
            row["crop_ordinal"],
            row["turn"],
        )
    )
    if len({row["row_hash"] for row in rows}) != len(rows):
        raise ValueError("D78 duplicate row identity")
    if any(
        not retain_row(row["game_id"], (row["cell_x"], row["cell_y"]), row["turn"])
        for row in rows
    ):
        raise ValueError("D78 row violates deterministic thinning")
    models = {
        "aggregate": fit_family(rows, "aggregate_features", "aggregate"),
        "spatial": fit_family(rows, "spatial_features", "spatial_snapshot"),
        "history": fit_family(rows, "history_features", "observable_history"),
    }
    write_rows(rows_path, rows)
    partition_rows = {
        partition: [row for row in rows if row["partition"] == partition]
        for partition in ("discovery", "validation")
    }
    support_checks = {
        "at_least_2000_rows_each": all(
            len(partition_rows[partition]) >= 2_000
            for partition in partition_rows
        ),
        "at_least_100_positive_rows_each": all(
            sum(int(row["label"]) for row in partition_rows[partition]) >= 100
            for partition in partition_rows
        ),
        "eight_positive_and_negative_accounts_each": all(
            account_support(partition_rows[partition])["positive_accounts"] >= 8
            and account_support(partition_rows[partition])["negative_accounts"] >= 8
            for partition in partition_rows
        ),
    }
    integrity_checks = {
        "all_selected_replays_exact": bool(integrity_rows)
        and all(
            row["trajectory_turns"] == row["decoded_turns"]
            and row["unknown_diff_updates"] == 0
            and row["final_inventory_exact"]
            for row in integrity_rows
        ),
        "unique_deterministic_live_crop_rows": len(rows) == len({row["row_hash"] for row in rows}),
        "all_feature_values_finite": all(
            value is None or math.isfinite(float(value))
            for row in rows
            for value in row["history_features"].values()
        ),
        "all_models_converged": all(model["fit"]["converged"] for model in models.values()),
        "confirmation_products_read_false": True,
    }
    aggregate = models["aggregate"]["validation"]
    spatial = models["spatial"]["validation"]
    history = models["history"]["validation"]
    spatial_checks = {
        "validation_auc_at_least_0_75": float(spatial["roc_auc"] or 0.0) >= 0.75,
        "validation_auc_uplift_at_least_0_05": float(spatial["roc_auc"] or 0.0)
        - float(aggregate["roc_auc"] or 0.0)
        >= 0.05,
        "validation_brier_improvement_at_least_0_005": float(aggregate["brier_score"])
        - float(spatial["brier_score"])
        >= 0.005,
        "validation_top_quintile_lift_at_least_2": float(
            spatial["top_quintile"]["lift"] or 0.0
        )
        >= 2.0,
    }
    top_history = models["history"]["fit"]["top_standardized_coefficients"][:10]
    history_checks = {
        "validation_auc_at_least_0_80": float(history["roc_auc"] or 0.0) >= 0.80,
        "validation_auc_uplift_at_least_0_03": float(history["roc_auc"] or 0.0)
        - float(spatial["roc_auc"] or 0.0)
        >= 0.03,
        "validation_brier_improvement_at_least_0_003": float(spatial["brier_score"])
        - float(history["brier_score"])
        >= 0.003,
        "validation_top_quintile_lift_at_least_2_5": float(
            history["top_quintile"]["lift"] or 0.0
        )
        >= 2.5,
        "three_top_ten_coefficients_are_history": sum(
            row["feature"].startswith("hist_") for row in top_history
        )
        >= 3,
    }
    full_support = all(support_checks.values()) and all(integrity_checks.values())
    spatial_pass = full_support and all(spatial_checks.values())
    history_pass = full_support and all(history_checks.values())
    if not full_support:
        next_interface = "quarantine_or_insufficient"
    elif history_pass:
        next_interface = "target_job_scorer_with_opponent_commitment_memory"
    elif spatial_pass:
        next_interface = "memoryless_context_complete_target_job_scorer"
    else:
        next_interface = "change_job_action_abstraction_not_state_history"
    report = {
        "schema": "troll-farm-d78a-opponent-commitment-observability-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_id": loaded["snapshot_id"],
        "scope": "open-only current-field behavior observability; no causal value or candidate claim",
        "inputs": {
            "open_loader": loaded["input_hashes"],
            "protocol": sha256_file(PROTOCOL),
            "analyzer": sha256_file(Path(__file__)),
        },
        "integrity": {
            "resident_games": len(integrity_rows),
            "selected_rows": len(rows),
            "selected_crops": sum(row["resident_crops"] for row in integrity_rows),
            "checks": integrity_checks,
            "confirmation_products_read": False,
        },
        "support": {
            "checks": support_checks,
            "partitions": {
                partition: {
                    "rows": len(selected),
                    "positive_rows": sum(int(row["label"]) for row in selected),
                    "terminal_chop_rows": sum(int(row["terminal_chop"]) for row in selected),
                    "accounts": len({row["opponent_user_id"] for row in selected}),
                    "account_support": account_support(selected),
                }
                for partition, selected in partition_rows.items()
            },
        },
        "models": models,
        "gates": {
            "full_integrity_and_support": full_support,
            "spatial": {"checks": spatial_checks, "pass": spatial_pass},
            "history": {"checks": history_checks, "pass": history_pass},
        },
        "comparison": {
            "spatial_minus_aggregate_auc": float(spatial["roc_auc"] or 0.0)
            - float(aggregate["roc_auc"] or 0.0),
            "aggregate_minus_spatial_brier": float(aggregate["brier_score"])
            - float(spatial["brier_score"]),
            "history_minus_spatial_auc": float(history["roc_auc"] or 0.0)
            - float(spatial["roc_auc"] or 0.0),
            "spatial_minus_history_brier": float(spatial["brier_score"])
            - float(history["brier_score"]),
            "top_ten_history_coefficients": sum(
                row["feature"].startswith("hist_") for row in top_history
            ),
        },
        "decision": {
            "status": next_interface,
            "next_controller_interface": next_interface,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
        "artifacts": {
            "rows": str(rows_path.relative_to(REPO)),
            "rows_sha256": sha256_file(rows_path),
        },
    }
    return report


def analyze(snapshot: Path, output: Path, rows_output: Path, jobs: int) -> dict:
    if not 1 <= jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    loaded = load_open_inputs(snapshot)
    if loaded["snapshot_id"] != EXPECTED_SNAPSHOT:
        raise ValueError(f"D78 is frozen to snapshot {EXPECTED_SNAPSHOT}")
    if int(loaded["resident_agent_id"]) != EXPECTED_RESIDENT:
        raise ValueError("D78 resident changed")
    tasks = [
        task
        for task in loaded["tasks"]
        if any(
            int(player.get("agentId", -1)) == EXPECTED_RESIDENT
            for player in task["game"]["players"]
        )
    ]
    if jobs == 1:
        extracted = [extract_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            extracted = list(executor.map(extract_task, tasks, chunksize=2))
    report = build_report(loaded, extracted, rows_output)
    atomic_write_new(output, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--rows-output", type=Path, default=ROWS_OUTPUT)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = analyze(args.snapshot, args.output, args.rows_output, args.jobs)
    print(
        json.dumps(
            {
                "rows": report["integrity"]["selected_rows"],
                "gates": report["gates"],
                "comparison": report["comparison"],
                "decision": report["decision"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
