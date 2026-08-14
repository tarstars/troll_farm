#!/usr/bin/env python3
"""Leakage-controlled F1 proxy-family readiness audit.

This is a readiness measurement only.  It never trains an adaptive controller and never
authorizes a source change, experiment, TestSession, submission, or Arena action.
"""

from __future__ import annotations

import argparse
import copy
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import pickle
import statistics
import time
from typing import Iterable

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


EXPECTED_SHA256 = "9b7281fb374d229524afc8341cf119ff30b073c73121f0fd4d87b8597c2af6f4"
START_SEED = 9_854_000
END_SEED = 9_854_127
HORIZONS = (10, 20, 40, 80)
LABELS = tuple(range(8))
FAMILIES = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
    "script_boss",
    "silver_boss",
)
SPECIES = ("PLUM", "LEMON", "APPLE", "BANANA")
LINEAR_C_GRID = (0.01, 0.1, 1.0)
FORBIDDEN_INPUT_FIELDS = (
    "seed",
    "opp",
    "opp_name",
    "arm",
    "turns",
    "scores",
    "c0",
    "c1",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _append(names: list[str], values: list[float], name: str, value: float) -> None:
    names.append(name)
    values.append(float(value))


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.mean(values) if values else 0.0


def _shacks(map_rows: list[str]) -> dict[int, tuple[int, int]]:
    found: dict[int, tuple[int, int]] = {}
    for y, row in enumerate(map_rows):
        for x, char in enumerate(row):
            if char in "01":
                found[int(char)] = (x, y)
    if set(found) != {0, 1}:
        raise ValueError(f"expected exactly two player shacks, got {found}")
    return found


def _distance_summary(
    origin: tuple[int, int], cells: list[tuple[int, int]], scale: float
) -> tuple[float, float]:
    distances = [abs(origin[0] - x) + abs(origin[1] - y) for x, y in cells]
    if not distances:
        return 0.0, 0.0
    return min(distances) / scale, statistics.mean(distances) / scale


def _static_features(record: dict, names: list[str], values: list[float]) -> None:
    rows = record["map_rows"]
    height, width = len(rows), len(rows[0])
    if not rows or any(len(row) != width for row in rows):
        raise ValueError("ragged or empty map")
    scale = max(1.0, width + height - 2)
    cells: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            cells[char].append((x, y))
    shacks = _shacks(rows)
    seat = int(record["seat"])
    own, opponent = shacks[seat], shacks[1 - seat]
    _append(names, values, "map_width", width / 32.0)
    _append(names, values, "map_height", height / 32.0)
    for char, slug in ((".", "walkable"), ("#", "iron"), ("~", "water"), ("+", "stock")):
        _append(names, values, f"map_{slug}_fraction", len(cells[char]) / (width * height))
        for role, origin in (("own", own), ("opp", opponent)):
            minimum, average = _distance_summary(origin, cells[char], scale)
            _append(names, values, f"map_{role}_{slug}_min_distance", minimum)
            _append(names, values, f"map_{role}_{slug}_mean_distance", average)
    _append(
        names,
        values,
        "map_shack_distance",
        (abs(own[0] - opponent[0]) + abs(own[1] - opponent[1])) / scale,
    )


def _units_for(state: dict, player: int) -> list[list]:
    return [unit for unit in state["u"] if int(unit[1]) == player]


def _current_features(
    record: dict, horizon: int, names: list[str], values: list[float]
) -> None:
    if len(record["states"]) <= horizon:
        raise ValueError(f"record ends before horizon {horizon}")
    state = record["states"][horizon]
    rows = record["map_rows"]
    height, width = len(rows), len(rows[0])
    scale = max(1.0, width + height - 2)
    shacks = _shacks(rows)
    seat = int(record["seat"])
    for role, player in (("own", seat), ("opp", 1 - seat)):
        units = _units_for(state, player)
        _append(names, values, f"current_{role}_unit_count", len(units) / 8.0)
        for offset, slug in ((4, "move_stat"), (5, "carry_capacity"), (6, "health"), (7, "chop_stat")):
            _append(names, values, f"current_{role}_{slug}_mean", _mean(unit[offset] for unit in units) / 8.0)
        for resource in range(6):
            _append(
                names,
                values,
                f"current_{role}_carry_{resource}",
                sum(unit[8 + resource] for unit in units) / 32.0,
            )
            _append(
                names,
                values,
                f"current_{role}_inventory_{resource}",
                state["b"][player][resource] / 64.0,
            )
        for target_role, target in (("own_shack", shacks[seat]), ("opp_shack", shacks[1 - seat])):
            distances = [abs(unit[2] - target[0]) + abs(unit[3] - target[1]) for unit in units]
            _append(names, values, f"current_{role}_{target_role}_mean_distance", _mean(distances) / scale)
            _append(names, values, f"current_{role}_{target_role}_min_distance", (min(distances) / scale) if distances else 0.0)

    plants = state["p"]
    for species in SPECIES:
        selected = [plant for plant in plants if plant[2] == species]
        _append(names, values, f"current_plant_{species.lower()}_count", len(selected) / 32.0)
        for offset, slug, divisor in (
            (3, "size", 8.0),
            (4, "health", 32.0),
            (5, "fruit", 16.0),
            (6, "cooldown", 16.0),
        ):
            _append(
                names,
                values,
                f"current_plant_{species.lower()}_{slug}_sum",
                sum(plant[offset] for plant in selected) / divisor,
            )


def _transition_features(
    record: dict, horizon: int, names: list[str], values: list[float]
) -> None:
    states = record["states"]
    if len(states) <= horizon:
        raise ValueError(f"record ends before horizon {horizon}")
    seat = int(record["seat"])
    side_totals = {
        role: {
            "births": 0.0,
            "deaths": 0.0,
            "movement": 0.0,
            "carry_gain": 0.0,
            "carry_loss": 0.0,
            "inventory_gain": [0.0] * 6,
            "inventory_loss": [0.0] * 6,
        }
        for role in ("own", "opp")
    }
    plant_totals = {
        species: {"appear": 0.0, "remove": 0.0, "fruit_gain": 0.0, "fruit_loss": 0.0}
        for species in SPECIES
    }

    for turn in range(1, horizon + 1):
        before, after = states[turn - 1], states[turn]
        for role, player in (("own", seat), ("opp", 1 - seat)):
            prior = {unit[0]: unit for unit in _units_for(before, player)}
            current = {unit[0]: unit for unit in _units_for(after, player)}
            side_totals[role]["births"] += len(current.keys() - prior.keys())
            side_totals[role]["deaths"] += len(prior.keys() - current.keys())
            for unit_id in current.keys() & prior.keys():
                old, new = prior[unit_id], current[unit_id]
                side_totals[role]["movement"] += abs(new[2] - old[2]) + abs(new[3] - old[3])
                for resource in range(6):
                    delta = new[8 + resource] - old[8 + resource]
                    side_totals[role]["carry_gain"] += max(0, delta)
                    side_totals[role]["carry_loss"] += max(0, -delta)
            for resource in range(6):
                delta = after["b"][player][resource] - before["b"][player][resource]
                side_totals[role]["inventory_gain"][resource] += max(0, delta)
                side_totals[role]["inventory_loss"][resource] += max(0, -delta)

        prior_plants = {(plant[0], plant[1], plant[2]): plant for plant in before["p"]}
        current_plants = {(plant[0], plant[1], plant[2]): plant for plant in after["p"]}
        for key in current_plants.keys() - prior_plants.keys():
            plant_totals[key[2]]["appear"] += 1
        for key in prior_plants.keys() - current_plants.keys():
            plant_totals[key[2]]["remove"] += 1
        for key in current_plants.keys() & prior_plants.keys():
            delta = current_plants[key][5] - prior_plants[key][5]
            plant_totals[key[2]]["fruit_gain"] += max(0, delta)
            plant_totals[key[2]]["fruit_loss"] += max(0, -delta)

    for role in ("own", "opp"):
        total = side_totals[role]
        for field, divisor in (
            ("births", 8.0),
            ("deaths", 8.0),
            ("movement", 512.0),
            ("carry_gain", 128.0),
            ("carry_loss", 128.0),
        ):
            _append(names, values, f"transition_{role}_{field if field != 'movement' else 'manhattan_movement'}", total[field] / divisor)
        for resource in range(6):
            _append(names, values, f"transition_{role}_inventory_{resource}_gain", total["inventory_gain"][resource] / 128.0)
            _append(names, values, f"transition_{role}_inventory_{resource}_loss", total["inventory_loss"][resource] / 128.0)
    for species in SPECIES:
        for field, divisor in (("appear", 32.0), ("remove", 32.0), ("fruit_gain", 128.0), ("fruit_loss", 128.0)):
            _append(names, values, f"transition_plant_{species.lower()}_{field}", plant_totals[species][field] / divisor)


def named_features(record: dict, horizon: int, variant: str) -> tuple[list[str], np.ndarray]:
    if variant not in ("static", "current", "cumulative"):
        raise ValueError(f"unknown feature variant {variant!r}")
    names: list[str] = []
    values: list[float] = []
    _static_features(record, names, values)
    if variant in ("current", "cumulative"):
        _current_features(record, horizon, names, values)
    if variant == "cumulative":
        _transition_features(record, horizon, names, values)
    return names, np.asarray(values, dtype=np.float64)


def feature_vector(record: dict, horizon: int, variant: str) -> np.ndarray:
    return named_features(record, horizon, variant)[1]


def outer_fold_ids(seeds: np.ndarray) -> np.ndarray:
    unique = sorted(int(seed) for seed in np.unique(seeds))
    mapping = {seed: index % 5 for index, seed in enumerate(unique)}
    return np.asarray([mapping[int(seed)] for seed in seeds], dtype=np.int8)


def permute_labels_within_seed(
    seeds: np.ndarray, seats: np.ndarray, labels: np.ndarray, repetition: int
) -> np.ndarray:
    del seats  # both seats share the label mapping because mapping is keyed by original family
    result = labels.copy()
    rng = np.random.default_rng(0xF1_2026 + repetition)
    for seed in sorted(np.unique(seeds)):
        permutation = rng.permutation(np.asarray(LABELS))
        mask = seeds == seed
        result[mask] = permutation[labels[mask]]
    return result


def _linear_model(c_value: float) -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    C=c_value,
                    solver="lbfgs",
                    max_iter=400,
                    random_state=20260814,
                ),
            ),
        ]
    )


def _centroid_model() -> Pipeline:
    return Pipeline([("scale", StandardScaler()), ("model", NearestCentroid())])


def portable_linear_artifact(model: Pipeline, feature_names: list[str]) -> dict:
    """Extract the exact standardized linear scorer without sklearn call overhead."""
    scaler = model.named_steps["scale"]
    classifier = model.named_steps["model"]
    artifact = {
        "mean": np.asarray(scaler.mean_, dtype=np.float64),
        "scale": np.asarray(scaler.scale_, dtype=np.float64),
        "coefficients": np.asarray(classifier.coef_, dtype=np.float64),
        "intercept": np.asarray(classifier.intercept_, dtype=np.float64),
        "classes": np.asarray(classifier.classes_, dtype=np.int64),
        "feature_names": list(feature_names),
    }
    artifact["serialized_bytes"] = (
        artifact["mean"].nbytes
        + artifact["scale"].nbytes
        + artifact["coefficients"].nbytes
        + artifact["intercept"].nbytes
        + artifact["classes"].nbytes
        + len(json.dumps(feature_names, separators=(",", ":")).encode())
        + 128
    )
    return artifact


def portable_linear_scores(artifact: dict, features: np.ndarray) -> np.ndarray:
    standardized = (np.asarray(features, dtype=np.float64) - artifact["mean"]) / artifact["scale"]
    return standardized @ artifact["coefficients"].T + artifact["intercept"]


def _scores(model: Pipeline, features: np.ndarray) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return np.asarray(model.predict_proba(features), dtype=np.float64)
    return np.asarray(model.decision_function(features), dtype=np.float64)


def _metric_summary(labels: np.ndarray, scores: np.ndarray, seats: np.ndarray) -> dict:
    predictions = np.argmax(scores, axis=1)
    precision, recall, f1, support = precision_recall_fscore_support(
        labels, predictions, labels=LABELS, zero_division=0
    )
    top2 = np.argsort(scores, axis=1)[:, -2:]
    by_seat = {}
    for seat in (0, 1):
        mask = seats == seat
        by_seat[str(seat)] = {
            "accuracy": float(accuracy_score(labels[mask], predictions[mask])),
            "macro_f1": float(f1_score(labels[mask], predictions[mask], labels=LABELS, average="macro", zero_division=0)),
        }
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "macro_f1": float(f1_score(labels, predictions, labels=LABELS, average="macro", zero_division=0)),
        "top2_accuracy": float(np.mean(np.any(top2 == labels[:, None], axis=1))),
        "per_family": {
            FAMILIES[index]: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index in LABELS
        },
        "confusion_matrix": confusion_matrix(labels, predictions, labels=LABELS).tolist(),
        "by_seat": by_seat,
    }


def _choose_c_inner(
    features: np.ndarray,
    labels: np.ndarray,
    seeds: np.ndarray,
    outer_fold: int,
) -> tuple[float, dict[str, float]]:
    groups = sorted(int(seed) for seed in np.unique(seeds))
    group_slot = {seed: index % 4 for index, seed in enumerate(groups)}
    validation = np.asarray([group_slot[int(seed)] == (outer_fold % 4) for seed in seeds])
    training = ~validation
    scores = {}
    for c_value in LINEAR_C_GRID:
        model = _linear_model(c_value).fit(features[training], labels[training])
        prediction = model.predict(features[validation])
        scores[str(c_value)] = float(
            f1_score(labels[validation], prediction, labels=LABELS, average="macro", zero_division=0)
        )
    best = max(LINEAR_C_GRID, key=lambda value: (scores[str(value)], -value))
    return best, scores


def cross_validated_scores(
    features: np.ndarray,
    labels: np.ndarray,
    seeds: np.ndarray,
    model_kind: str,
    feature_names: list[str],
) -> tuple[np.ndarray, dict]:
    folds = outer_fold_ids(seeds)
    held_scores = np.zeros((len(labels), len(LABELS)), dtype=np.float64)
    details = {
        "folds": [],
        "max_serialized_bytes": 0,
        "inference_p95_ms": 0.0,
        "portable_prediction_parity": True,
    }
    for fold in range(5):
        train, test = folds != fold, folds == fold
        if model_kind == "linear":
            c_value, inner = _choose_c_inner(features[train], labels[train], seeds[train], fold)
            model = _linear_model(c_value)
        elif model_kind == "centroid":
            c_value, inner = None, None
            model = _centroid_model()
        else:
            raise ValueError(model_kind)
        model.fit(features[train], labels[train])
        held_scores[test] = _scores(model, features[test])
        portable = portable_linear_artifact(model, feature_names) if model_kind == "linear" else None
        if portable is not None:
            portable_test_scores = portable_linear_scores(portable, features[test])
            portable_parity = np.array_equal(
                np.argmax(portable_test_scores, axis=1), model.predict(features[test])
            )
            serialized = portable["serialized_bytes"]
        else:
            portable_parity = True
            serialized = len(pickle.dumps(model, protocol=5)) + len(json.dumps(feature_names).encode())
        sample_indices = np.flatnonzero(test)[:256]
        timings = []
        for index in sample_indices:
            start = time.perf_counter_ns()
            if portable is not None:
                portable_linear_scores(portable, features[index : index + 1])
            else:
                _scores(model, features[index : index + 1])
            timings.append((time.perf_counter_ns() - start) / 1_000_000)
        p95 = float(np.percentile(timings, 95))
        details["max_serialized_bytes"] = max(details["max_serialized_bytes"], serialized)
        details["inference_p95_ms"] = max(details["inference_p95_ms"], p95)
        details["portable_prediction_parity"] = details["portable_prediction_parity"] and portable_parity
        details["folds"].append(
            {
                "fold": fold,
                "test_seeds": int(len(np.unique(seeds[test]))),
                "test_rows": int(np.sum(test)),
                "selected_c": c_value,
                "inner_macro_f1": inner,
                "serialized_bytes": serialized,
                "inference_p95_ms": p95,
                "portable_prediction_parity": portable_parity,
            }
        )
    return held_scores, details


def bootstrap_macro_f1(
    labels: np.ndarray,
    predictions: np.ndarray,
    seeds: np.ndarray,
    repetitions: int = 2000,
) -> dict:
    groups = {int(seed): np.flatnonzero(seeds == seed) for seed in np.unique(seeds)}
    unique = np.asarray(sorted(groups))
    rng = np.random.default_rng(20260814)
    samples = np.empty(repetitions, dtype=np.float64)
    for repetition in range(repetitions):
        drawn = rng.choice(unique, size=len(unique), replace=True)
        indices = np.concatenate([groups[int(seed)] for seed in drawn])
        samples[repetition] = f1_score(
            labels[indices], predictions[indices], labels=LABELS, average="macro", zero_division=0
        )
    return {
        "repetitions": repetitions,
        "lower_95": float(np.percentile(samples, 2.5)),
        "upper_95": float(np.percentile(samples, 97.5)),
    }


def permutation_control(
    labels: np.ndarray,
    predictions: np.ndarray,
    seeds: np.ndarray,
    seats: np.ndarray,
    repetitions: int = 1000,
) -> dict:
    samples = np.empty(repetitions, dtype=np.float64)
    for repetition in range(repetitions):
        permuted = permute_labels_within_seed(seeds, seats, labels, repetition)
        samples[repetition] = f1_score(
            permuted, predictions, labels=LABELS, average="macro", zero_division=0
        )
    return {
        "repetitions": repetitions,
        "p99_macro_f1": float(np.percentile(samples, 99)),
        "mean_macro_f1": float(np.mean(samples)),
    }


def synthetic_passing_gate_metrics() -> dict:
    return {
        "macro_f1": 0.50,
        "bootstrap_lower_95": 0.351,
        "top2_accuracy": 0.75,
        "recalls": [0.5] * 8,
        "seat_macro_f1": [0.4, 0.4],
        "permutation_p99": 0.2,
        "static_macro_f1": 0.125,
        "deletion_parity": True,
        "portable_prediction_parity": True,
        "inference_p95_ms": 1.0,
        "serialized_bytes": 10_000,
    }


def _passes_gate(metrics: dict) -> bool:
    recalls = metrics["recalls"]
    return all(
        (
            metrics["macro_f1"] >= 0.50,
            metrics["bootstrap_lower_95"] > 0.35,
            metrics["top2_accuracy"] >= 0.75,
            min(recalls) >= 0.25,
            sum(value >= 0.50 for value in recalls) >= 6,
            min(metrics["seat_macro_f1"]) >= 0.40,
            metrics["macro_f1"] > metrics["permutation_p99"],
            metrics["static_macro_f1"] <= 0.20,
            metrics["deletion_parity"],
            metrics["portable_prediction_parity"],
            metrics["inference_p95_ms"] <= 2.0,
            metrics["serialized_bytes"] <= 20_000,
        )
    )


def readiness_verdict(by_horizon: dict[int, dict], integrity: bool) -> str:
    if not integrity:
        return "BLOCKED_LEAKAGE_OR_INTEGRITY"
    if _passes_gate(by_horizon[40]):
        return "EARLY_PROXY_SIGNAL"
    if _passes_gate(by_horizon[80]):
        return "LATE_ONLY_PROXY_SIGNAL"
    return "NO_RELIABLE_PROXY_SIGNAL"


def load_dataset(path: Path) -> dict:
    observed_hash = sha256_file(path)
    features = {horizon: {variant: [] for variant in ("static", "current", "cumulative")} for horizon in HORIZONS}
    feature_names: dict[int, dict[str, list[str]]] = {horizon: {} for horizon in HORIZONS}
    labels, seeds, seats = [], [], []
    keys, duplicates, errors = set(), [], []
    deletion_fixtures = []
    deterministic = True
    reference_turn40_extraction_ms = []
    with path.open() as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                key = (int(record["seed"]), int(record["seat"]), int(record["opp"]))
                if key in keys:
                    duplicates.append(key)
                keys.add(key)
                if record["arm"] != "referee":
                    raise ValueError("non-referee arm")
                if len(record["states"]) <= max(HORIZONS):
                    raise ValueError("record ends before turn 80")
                if len(deletion_fixtures) < 8:
                    deletion_fixtures.append(copy.deepcopy(record))
                for horizon in HORIZONS:
                    for variant in ("static", "current", "cumulative"):
                        started = time.perf_counter_ns() if horizon == 40 and variant == "cumulative" else None
                        names, vector = named_features(record, horizon, variant)
                        if started is not None:
                            reference_turn40_extraction_ms.append((time.perf_counter_ns() - started) / 1_000_000)
                        if variant not in feature_names[horizon]:
                            feature_names[horizon][variant] = names
                        elif names != feature_names[horizon][variant]:
                            raise ValueError("feature schema drift")
                        if line_number == 1:
                            deterministic = deterministic and vector.tobytes() == feature_vector(record, horizon, variant).tobytes()
                        features[horizon][variant].append(vector)
                seeds.append(key[0])
                seats.append(key[1])
                labels.append(key[2])
            except Exception as error:
                if len(errors) < 20:
                    errors.append({"line": line_number, "error": f"{type(error).__name__}: {error}"})
    expected = {
        (seed, seat, label)
        for seed in range(START_SEED, END_SEED + 1)
        for seat in (0, 1)
        for label in LABELS
    }
    matrices = {
        horizon: {variant: np.vstack(rows) for variant, rows in variants.items()}
        for horizon, variants in features.items()
    }
    integrity = {
        "expected_sha256": EXPECTED_SHA256,
        "observed_sha256": observed_hash,
        "sha256_exact": observed_hash == EXPECTED_SHA256,
        "records": len(labels),
        "records_exact": len(labels) == 2048,
        "task_coverage_exact": keys == expected,
        "missing_tasks": len(expected - keys),
        "unexpected_tasks": len(keys - expected),
        "duplicate_tasks": len(duplicates),
        "decode_errors": errors,
        "deterministic_features": deterministic,
    }
    integrity["pass"] = all(
        (
            integrity["sha256_exact"],
            integrity["records_exact"],
            integrity["task_coverage_exact"],
            not duplicates,
            not errors,
            deterministic,
        )
    )
    return {
        "features": matrices,
        "feature_names": feature_names,
        "labels": np.asarray(labels, dtype=np.int8),
        "seeds": np.asarray(seeds, dtype=np.int64),
        "seats": np.asarray(seats, dtype=np.int8),
        "integrity": integrity,
        "deletion_fixtures": deletion_fixtures,
        "runtime_reference": {
            "turn40_offline_replay_extractor_p95_ms": float(np.percentile(reference_turn40_extraction_ms, 95)),
            "boundary": "rebuilds 40 observed transitions from a stored trajectory; reported for transparency but not used as the maintained-feature scorer inference gate",
        },
    }


def deletion_feature_parity(fixtures: list[dict], horizon: int, variant: str) -> bool:
    for source in fixtures:
        clean = copy.deepcopy(source)
        for field in FORBIDDEN_INPUT_FIELDS:
            clean.pop(field, None)
        if feature_vector(source, horizon, variant).tobytes() != feature_vector(clean, horizon, variant).tobytes():
            return False
    return True


def deletion_prediction_parity(
    features: np.ndarray,
    labels: np.ndarray,
    feature_names: list[str],
    fixtures: list[dict],
    horizon: int,
    variant: str,
) -> bool:
    model = _linear_model(0.1).fit(features, labels)
    artifact = portable_linear_artifact(model, feature_names)
    for source in fixtures:
        clean = copy.deepcopy(source)
        for field in FORBIDDEN_INPUT_FIELDS:
            clean.pop(field, None)
        left = portable_linear_scores(artifact, feature_vector(source, horizon, variant)[None, :])
        right = portable_linear_scores(artifact, feature_vector(clean, horizon, variant)[None, :])
        if left.tobytes() != right.tobytes():
            return False
    return True


def analyze(path: Path) -> dict:
    dataset = load_dataset(path)
    labels, seeds, seats = dataset["labels"], dataset["seeds"], dataset["seats"]
    results = {}
    gate_inputs = {}
    for horizon in HORIZONS:
        print(f"horizon {horizon}: cumulative linear", flush=True)
        cumulative = dataset["features"][horizon]["cumulative"]
        cumulative_names = dataset["feature_names"][horizon]["cumulative"]
        linear_scores, linear_details = cross_validated_scores(cumulative, labels, seeds, "linear", cumulative_names)
        linear_metrics = _metric_summary(labels, linear_scores, seats)
        linear_predictions = np.argmax(linear_scores, axis=1)
        linear_metrics["bootstrap"] = bootstrap_macro_f1(labels, linear_predictions, seeds)
        linear_metrics["permutation"] = permutation_control(labels, linear_predictions, seeds, seats)
        linear_metrics["model"] = linear_details

        print(f"horizon {horizon}: cumulative centroid", flush=True)
        centroid_scores, centroid_details = cross_validated_scores(cumulative, labels, seeds, "centroid", cumulative_names)
        centroid_metrics = _metric_summary(labels, centroid_scores, seats)
        centroid_metrics["model"] = centroid_details

        print(f"horizon {horizon}: current-only linear and centroid", flush=True)
        current = dataset["features"][horizon]["current"]
        current_names = dataset["feature_names"][horizon]["current"]
        current_linear_scores, current_linear_details = cross_validated_scores(current, labels, seeds, "linear", current_names)
        current_centroid_scores, current_centroid_details = cross_validated_scores(current, labels, seeds, "centroid", current_names)
        current_linear_metrics = _metric_summary(labels, current_linear_scores, seats)
        current_linear_metrics["model"] = current_linear_details
        current_centroid_metrics = _metric_summary(labels, current_centroid_scores, seats)
        current_centroid_metrics["model"] = current_centroid_details

        print(f"horizon {horizon}: static-map control", flush=True)
        static = dataset["features"][horizon]["static"]
        static_names = dataset["feature_names"][horizon]["static"]
        static_scores, static_details = cross_validated_scores(static, labels, seeds, "linear", static_names)
        static_metrics = _metric_summary(labels, static_scores, seats)
        static_metrics["model"] = static_details

        deletion_feature_exact = deletion_feature_parity(dataset["deletion_fixtures"], horizon, "cumulative")
        deletion_prediction_exact = deletion_prediction_parity(
            cumulative,
            labels,
            cumulative_names,
            dataset["deletion_fixtures"],
            horizon,
            "cumulative",
        )
        deletion_parity = deletion_feature_exact and deletion_prediction_exact
        recalls = [linear_metrics["per_family"][family]["recall"] for family in FAMILIES]
        gate_inputs[horizon] = {
            "macro_f1": linear_metrics["macro_f1"],
            "bootstrap_lower_95": linear_metrics["bootstrap"]["lower_95"],
            "top2_accuracy": linear_metrics["top2_accuracy"],
            "recalls": recalls,
            "seat_macro_f1": [linear_metrics["by_seat"][str(seat)]["macro_f1"] for seat in (0, 1)],
            "permutation_p99": linear_metrics["permutation"]["p99_macro_f1"],
            "static_macro_f1": static_metrics["macro_f1"],
            "deletion_parity": deletion_parity,
            "inference_p95_ms": linear_details["inference_p95_ms"],
            "serialized_bytes": linear_details["max_serialized_bytes"],
            "portable_prediction_parity": linear_details["portable_prediction_parity"],
        }
        results[str(horizon)] = {
            "feature_counts": {variant: len(dataset["feature_names"][horizon][variant]) for variant in ("static", "current", "cumulative")},
            "cumulative": {"linear": linear_metrics, "centroid": centroid_metrics},
            "current_only": {"linear": current_linear_metrics, "centroid": current_centroid_metrics},
            "static_map_control": static_metrics,
            "command_label_deletion_feature_parity": deletion_feature_exact,
            "command_label_deletion_prediction_parity": deletion_prediction_exact,
            "gate_inputs": gate_inputs[horizon],
        }
    integrity = dataset["integrity"]["pass"] and all(
        value["deletion_parity"] and value["portable_prediction_parity"]
        for value in gate_inputs.values()
    )
    verdict = readiness_verdict(gate_inputs, integrity)
    return {
        "schema": "troll-farm-f1-opponent-archetype-readiness-v1",
        "scope": "readiness only; no adaptive-controller or Arena authority",
        "source": {"path": str(path), "records": 2048, "seeds": [START_SEED, END_SEED], "seats": [0, 1], "families": list(FAMILIES)},
        "split": {"outer": "five deterministic folds grouped by whole map seed", "inner": "one deterministic whole-seed validation slot inside each outer training fold", "linear_c_grid": list(LINEAR_C_GRID)},
        "integrity": dataset["integrity"],
        "integrity_and_leakage_pass": integrity,
        "runtime_reference": dataset["runtime_reference"],
        "horizons": results,
        "verdict": verdict,
    }


def render_markdown(result: dict) -> str:
    lines = [
        "# F1 opponent-archetype readiness result",
        "",
        f"**Verdict: `{result['verdict']}`**",
        "",
        "This is a proxy-family signal audit only. It does not authorize adaptation, a bot change,",
        "an experiment, TestSession, submission, or Arena action.",
        "",
        "## Integrity",
        "",
        f"The restored 2,048-game source hashes to `{result['integrity']['observed_sha256']}` and exact task coverage is `{result['integrity']['task_coverage_exact']}`.",
        f"Overall integrity and leakage controls pass: `{result['integrity_and_leakage_pass']}`.",
        "",
        "## Held-map results",
        "",
        "| Turn | Linear cumulative macro-F1 | 95% map bootstrap | Top-2 | Min recall | Seat F1s | Centroid F1 | Current-only linear F1 | Static-map F1 | Permutation p99 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for horizon in HORIZONS:
        row = result["horizons"][str(horizon)]
        linear = row["cumulative"]["linear"]
        gate = row["gate_inputs"]
        lines.append(
            f"| {horizon} | {linear['macro_f1']:.3f} | [{linear['bootstrap']['lower_95']:.3f}, {linear['bootstrap']['upper_95']:.3f}] | {linear['top2_accuracy']:.3f} | {min(gate['recalls']):.3f} | {gate['seat_macro_f1'][0]:.3f} / {gate['seat_macro_f1'][1]:.3f} | {row['cumulative']['centroid']['macro_f1']:.3f} | {row['current_only']['linear']['macro_f1']:.3f} | {gate['static_macro_f1']:.3f} | {gate['permutation_p99']:.3f} |"
        )
    turn40 = result["horizons"]["40"]
    lines.extend(
        [
            "",
            "## Turn-40 gate interpretation",
            "",
            f"The primary frozen model is standardized multinomial linear over cumulative legal history. Its serialized model plus feature schema is {turn40['gate_inputs']['serialized_bytes']} bytes and worst outer-fold single-example p95 inference is {turn40['gate_inputs']['inference_p95_ms']:.3f} ms.",
            f"For clarity, the offline Python audit path takes {result['runtime_reference']['turn40_offline_replay_extractor_p95_ms']:.3f} ms p95 to rebuild all 40 observed transitions from scratch. That replay-rebuild cost is not the inference gate above; a live extractor maintains those transition totals as states arrive. This report is not an end-to-end Rust deployment benchmark.",
            f"Command/label deletion feature and prediction parity are `{turn40['command_label_deletion_feature_parity']}` / `{turn40['command_label_deletion_prediction_parity']}`; portable-scorer prediction parity is `{turn40['gate_inputs']['portable_prediction_parity']}`.",
            "",
            "The exact per-family precision/recall tables, confusion matrices, nested choices, seat controls, 1,000 within-seed permutations, and all four horizon results are in the adjacent JSON.",
            "",
            "A positive readiness verdict would authorize only a separately reviewed three-arm action-target audit. This report itself authorizes nothing downstream.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text(render_markdown(result))
    print(json.dumps({"verdict": result["verdict"], "output_json": str(args.output_json), "output_md": str(args.output_md)}, sort_keys=True))
    return 0 if result["verdict"] != "BLOCKED_LEAKAGE_OR_INTEGRITY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
