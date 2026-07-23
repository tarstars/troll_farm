#!/usr/bin/env python3
"""Audit replay-conditioned retrieval of rich-opponent 50-turn continuations."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


TARGET_FIELDS = (
    "score",
    "fruit",
    "wood",
    "workers",
    "successful_plants",
    "harvested_fruit",
    "chops_landed",
    "dropped_items",
)
TARGET_SCALES = {
    "score": 20.0,
    "fruit": 6.0,
    "wood": 5.0,
    "workers": 1.0,
    "successful_plants": 4.0,
    "harvested_fruit": 8.0,
    "chops_landed": 15.0,
    "dropped_items": 12.0,
}
MAP_FEATURES = (
    "initial_plum",
    "initial_lemon",
    "initial_apple",
    "initial_banana",
    "initial_iron",
    "initial_wood",
    "initial_score",
    "tree_total",
    "fruit_total",
    "ripe_tree_count",
    "tree_health_total",
    "tree_size_total",
    "plum_tree_count",
    "plum_fruit",
    "plum_health",
    "plum_size",
    "lemon_tree_count",
    "lemon_fruit",
    "lemon_health",
    "lemon_size",
    "apple_tree_count",
    "apple_fruit",
    "apple_health",
    "apple_size",
    "banana_tree_count",
    "banana_fruit",
    "banana_health",
    "banana_size",
    "water_adjacent_cells",
    "shack_door_distance",
)
ACTION_VERBS = ("CHOP", "DROP", "HARVEST", "MINE", "MOVE", "PICK", "PLANT")
REPRESENTATIONS = ("map", "state", "history")
K_VALUES = (1, 3)
CUTOFFS = (50, 100)
PHASE_BY_CUTOFF = {50: "001-050", 100: "051-100"}


def interval(row: dict, start: int, end: int) -> dict:
    matches = [
        value
        for value in row.get("intervals") or []
        if int(value["start_turn"]) == start and int(value["end_turn"]) == end
    ]
    if len(matches) != 1:
        raise ValueError(
            f"game {row.get('game_id')} has {len(matches)} intervals for {start}-{end}"
        )
    return matches[0]["increments"]


def numeric_fields(source: dict, names: tuple[str, ...], prefix: str) -> dict[str, float]:
    missing = [name for name in names if name not in source]
    if missing:
        raise ValueError(f"missing fields {missing}")
    return {f"{prefix}{name}": float(source[name]) for name in names}


def first_worker_spec(row: dict, cutoff: int) -> list[int]:
    events = [
        event
        for event in row.get("training_events") or []
        if int(event["ordinal"]) == 1 and int(event["turn"]) <= cutoff
    ]
    if len(events) != 1:
        raise ValueError(
            f"game {row.get('game_id')} has {len(events)} observable immediate workers at {cutoff}"
        )
    spec = [int(value) for value in events[0]["spec"]]
    if len(spec) != 4:
        raise ValueError(f"bad first-worker spec in game {row.get('game_id')}")
    return spec


def build_examples(scheduler: dict, census: dict) -> list[dict]:
    rows = scheduler.get("rows") or []
    if len(rows) != 21 or len({int(row["game_id"]) for row in rows}) != 21:
        raise ValueError("expected exactly 21 unique scheduler games")
    census_by_game = {
        int(row["game_id"]): row for row in census.get("rows") or []
    }
    if not {int(row["game_id"]) for row in rows}.issubset(census_by_game):
        raise ValueError("scheduler games are missing from the exact-map census")

    examples = []
    for row in rows:
        game_id = int(row["game_id"])
        opening = census_by_game[game_id].get("opening") or {}
        map_features = numeric_fields(opening, MAP_FEATURES, "map_")
        map_features["map_has_iron"] = float(bool(row["has_iron"]))
        for cutoff in CUTOFFS:
            snapshot = row.get("snapshots", {}).get(str(cutoff))
            if snapshot is None:
                raise ValueError(f"game {game_id} has no cutoff {cutoff} snapshot")
            state_features = numeric_fields(snapshot, TARGET_FIELDS, "state_")
            recent = interval(row, cutoff - 49, cutoff)
            future = interval(row, cutoff + 1, cutoff + 50)
            history_features = dict(state_features)
            history_features.update(numeric_fields(recent, TARGET_FIELDS, "recent_"))
            phase = (row.get("scheduler") or {}).get("phase_actions", {}).get(
                PHASE_BY_CUTOFF[cutoff], {}
            )
            history_features.update(
                {
                    f"action_{verb.lower()}_rate": float(phase.get(verb, 0)) / 50.0
                    for verb in ACTION_VERBS
                }
            )
            history_features.update(
                {
                    f"first_worker_stat_{index}": float(value)
                    for index, value in enumerate(first_worker_spec(row, cutoff))
                }
            )
            target = {field: float(future[field]) for field in TARGET_FIELDS}
            examples.append(
                {
                    "game_id": game_id,
                    "opponent": row["opponent"],
                    "partition": row["partition"],
                    "cutoff": cutoff,
                    "target": target,
                    "features": {
                        "map": map_features,
                        "state": state_features,
                        "history": history_features,
                    },
                }
            )
    identities = {(row["game_id"], row["cutoff"]) for row in examples}
    if len(examples) != 42 or len(identities) != 42:
        raise ValueError("expected exactly 42 unique replay-cutoff examples")
    counts = {
        name: sum(row["partition"] == name for row in examples)
        for name in ("discovery", "confirmation")
    }
    if counts != {"discovery": 24, "confirmation": 18}:
        raise ValueError(f"unexpected example partition counts: {counts}")
    return sorted(examples, key=lambda row: (row["game_id"], row["cutoff"]))


def target_mean(rows: list[dict]) -> dict[str, float]:
    if not rows:
        raise ValueError("cannot average an empty training fold")
    return {
        field: statistics.mean(row["target"][field] for row in rows)
        for field in TARGET_FIELDS
    }


def feature_scales(rows: list[dict], representation: str) -> dict[str, tuple[float, float]]:
    names = sorted(rows[0]["features"][representation])
    if any(sorted(row["features"][representation]) != names for row in rows):
        raise ValueError(f"inconsistent {representation} feature schema")
    scales = {}
    for name in names:
        values = [row["features"][representation][name] for row in rows]
        mean = statistics.mean(values)
        variance = statistics.mean((value - mean) ** 2 for value in values)
        scales[name] = (mean, math.sqrt(variance))
    return scales


def distance(query: dict, candidate: dict, representation: str, scales: dict) -> float:
    squared = 0.0
    used = 0
    for name, (_mean, deviation) in scales.items():
        if deviation == 0:
            continue
        delta = (
            query["features"][representation][name]
            - candidate["features"][representation][name]
        ) / deviation
        squared += delta * delta
        used += 1
    return math.sqrt(squared / used) if used else 0.0


def retrieve(query: dict, training: list[dict], representation: str, k: int) -> tuple[dict, list]:
    if not training:
        raise ValueError("empty retrieval fold")
    scales = feature_scales(training, representation)
    ranked = sorted(
        (
            (distance(query, candidate, representation, scales), candidate)
            for candidate in training
        ),
        key=lambda item: (
            item[0],
            item[1]["game_id"],
            item[1].get("opponent", item[1].get("agent_name", "")),
        ),
    )
    selected = ranked[: min(k, len(ranked))]
    prediction = {
        field: statistics.mean(candidate["target"][field] for _, candidate in selected)
        for field in TARGET_FIELDS
    }
    neighbors = [
        {
            "game_id": candidate["game_id"],
            "opponent": candidate.get("opponent", candidate.get("agent_name")),
            "distance": value,
        }
        for value, candidate in selected
    ]
    return prediction, neighbors


def prediction_error(actual: dict, predicted: dict) -> dict:
    absolute = {field: abs(predicted[field] - actual[field]) for field in TARGET_FIELDS}
    return {
        "normalized": statistics.mean(
            absolute[field] / TARGET_SCALES[field] for field in TARGET_FIELDS
        ),
        "absolute": absolute,
    }


def select_k(examples: list[dict]) -> tuple[dict, dict]:
    discovery = [row for row in examples if row["partition"] == "discovery"]
    selected = {}
    details = {}
    for representation in REPRESENTATIONS:
        ranking = []
        for k in K_VALUES:
            errors = []
            for query in discovery:
                training = [
                    row
                    for row in discovery
                    if row["cutoff"] == query["cutoff"]
                    and row["opponent"] != query["opponent"]
                ]
                predicted, _neighbors = retrieve(query, training, representation, k)
                errors.append(prediction_error(query["target"], predicted)["normalized"])
            ranking.append({"k": k, "normalized_mae": statistics.mean(errors)})
        ranking.sort(key=lambda row: (row["normalized_mae"], row["k"]))
        selected[representation] = ranking[0]["k"]
        details[representation] = {"selected_k": ranking[0]["k"], "ranking": ranking}
    return selected, details


def eligible_training(examples: list[dict], query: dict, mode: str) -> list[dict]:
    same_cutoff = [row for row in examples if row["cutoff"] == query["cutoff"]]
    if mode == "confirmation":
        return [
            row
            for row in same_cutoff
            if row["partition"] == "discovery"
            and row["opponent"] != query["opponent"]
        ]
    if mode == "leave_game_out":
        return [row for row in same_cutoff if row["game_id"] != query["game_id"]]
    if mode == "leave_opponent_out":
        return [row for row in same_cutoff if row["opponent"] != query["opponent"]]
    raise ValueError(f"unknown evaluation mode {mode}")


def evaluation_rows(examples: list[dict], selected_k: dict, mode: str) -> list[dict]:
    tests = (
        [row for row in examples if row["partition"] == "confirmation"]
        if mode == "confirmation"
        else examples
    )
    output = []
    for query in tests:
        training = eligible_training(examples, query, mode)
        if len(training) < max(K_VALUES):
            raise ValueError(f"too few eligible training games for {query['game_id']}")
        mean_prediction = target_mean(training)
        models = {
            "split_mean": {
                "prediction": mean_prediction,
                "neighbors": [],
                **prediction_error(query["target"], mean_prediction),
            }
        }
        for representation in REPRESENTATIONS:
            predicted, neighbors = retrieve(
                query, training, representation, selected_k[representation]
            )
            models[representation] = {
                "prediction": predicted,
                "neighbors": neighbors,
                **prediction_error(query["target"], predicted),
            }
        output.append(
            {
                "game_id": query["game_id"],
                "opponent": query["opponent"],
                "partition": query["partition"],
                "cutoff": query["cutoff"],
                "eligible_training_games": len(training),
                "target": query["target"],
                "models": models,
            }
        )
    return output


def relative_reduction(reference: float, challenger: float) -> float | None:
    return (reference - challenger) / reference if reference else None


def metrics(rows: list[dict]) -> dict:
    model_names = ("split_mean", *REPRESENTATIONS)
    model_metrics = {}
    for model in model_names:
        model_metrics[model] = {
            "normalized_mae": statistics.mean(row["models"][model]["normalized"] for row in rows),
            "median_normalized_absolute_error": statistics.median(
                row["models"][model]["normalized"] for row in rows
            ),
            "per_field_mae": {
                field: statistics.mean(
                    row["models"][model]["absolute"][field] for row in rows
                )
                for field in TARGET_FIELDS
            },
        }
    history_errors = [row["models"]["history"]["normalized"] for row in rows]
    state_errors = [row["models"]["state"]["normalized"] for row in rows]
    mean_errors = [row["models"]["split_mean"]["normalized"] for row in rows]
    return {
        "examples": len(rows),
        "models": model_metrics,
        "relative_reductions": {
            "history_vs_split_mean": relative_reduction(
                model_metrics["split_mean"]["normalized_mae"],
                model_metrics["history"]["normalized_mae"],
            ),
            "history_vs_state": relative_reduction(
                model_metrics["state"]["normalized_mae"],
                model_metrics["history"]["normalized_mae"],
            ),
        },
        "paired_wins": {
            "history_vs_state": sum(a < b for a, b in zip(history_errors, state_errors)),
            "history_vs_state_rate": sum(a < b for a, b in zip(history_errors, state_errors))
            / len(rows),
            "history_vs_split_mean": sum(a < b for a, b in zip(history_errors, mean_errors)),
            "history_vs_split_mean_rate": sum(a < b for a, b in zip(history_errors, mean_errors))
            / len(rows),
        },
    }


def summarize(rows: list[dict]) -> dict:
    return {
        "overall": metrics(rows),
        "by_cutoff": {
            str(cutoff): metrics([row for row in rows if row["cutoff"] == cutoff])
            for cutoff in CUTOFFS
        },
        "rows": rows,
    }


def analyze(scheduler: dict, census: dict) -> dict:
    examples = build_examples(scheduler, census)
    selected_k, discovery_selection = select_k(examples)
    confirmation = summarize(
        evaluation_rows(examples, selected_k, "confirmation")
    )
    leave_game = summarize(
        evaluation_rows(examples, selected_k, "leave_game_out")
    )
    leave_opponent = summarize(
        evaluation_rows(examples, selected_k, "leave_opponent_out")
    )
    conf = confirmation["overall"]
    conf100 = confirmation["by_cutoff"]["100"]
    lopo = leave_opponent["overall"]
    gates = {
        "integrity": len(examples) == 42,
        "confirmation_history_vs_mean": (
            conf["relative_reductions"]["history_vs_split_mean"] is not None
            and conf["relative_reductions"]["history_vs_split_mean"] >= 0.10
        ),
        "confirmation_history_vs_state": (
            conf["relative_reductions"]["history_vs_state"] is not None
            and conf["relative_reductions"]["history_vs_state"] >= 0.05
        ),
        "confirmation_t100_history_vs_mean": (
            conf100["relative_reductions"]["history_vs_split_mean"] is not None
            and conf100["relative_reductions"]["history_vs_split_mean"] >= 0.10
        ),
        "leave_opponent_out_history_vs_mean": (
            lopo["relative_reductions"]["history_vs_split_mean"] is not None
            and lopo["relative_reductions"]["history_vs_split_mean"] >= 0.05
        ),
        "confirmation_history_paired_wins": (
            conf["paired_wins"]["history_vs_state_rate"] >= 0.55
        ),
    }
    passed = all(gates.values())
    return {
        "schema": 1,
        "scope": "consumed rich-opponent replay-conditioned continuation feasibility",
        "games": 21,
        "examples": len(examples),
        "split_examples": {
            name: sum(row["partition"] == name for row in examples)
            for name in ("discovery", "confirmation")
        },
        "feature_counts": {
            representation: len(examples[0]["features"][representation])
            for representation in REPRESENTATIONS
        },
        "target_fields": TARGET_FIELDS,
        "target_scales": TARGET_SCALES,
        "selected_k": selected_k,
        "discovery_selection": discovery_selection,
        "confirmation": confirmation,
        "leave_one_game_out": leave_game,
        "leave_one_opponent_out": leave_opponent,
        "gates": gates,
        "passed": passed,
        "decision": (
            "history retrieval passes; test bounded replay resampling"
            if passed
            else "history retrieval fails held-opponent transfer; expand repeated-agent histories"
        ),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scheduler", type=Path, required=True)
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(
        json.loads(args.scheduler.read_text()),
        json.loads(args.census.read_text()),
    )
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "examples": payload["examples"],
        "split_examples": payload["split_examples"],
        "feature_counts": payload["feature_counts"],
        "selected_k": payload["selected_k"],
        "discovery_selection": payload["discovery_selection"],
        "confirmation": {
            "overall": payload["confirmation"]["overall"],
            "by_cutoff": payload["confirmation"]["by_cutoff"],
        },
        "leave_one_opponent_out": payload["leave_one_opponent_out"]["overall"],
        "gates": payload["gates"],
        "passed": payload["passed"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
