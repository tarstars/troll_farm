#!/usr/bin/env python3
"""Held-map pooled ridge value test for D82 threatened-own-crop responses."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d83a-threatened-response-value-predictability-protocol-2026-07-21.md"
FEATURE_A = ANALYSIS / "d83a-threatened-response-features-a-9914000-9914031.tsv"
FEATURE_B = ANALYSIS / "d83a-threatened-response-features-b-9914000-9914031.tsv"
D82_ROWS = ANALYSIS / "d82a-threatened-own-crop-rollout-a-9914000-9914031.tsv"
D82_RESULT = ANALYSIS / "d82a-threatened-own-crop-rollout-result.json"
EXPORTER = ROOT / "rust" / "src" / "bin" / "d83_threatened_response_features.rs"
OUTPUT = ANALYSIS / "d83a-threatened-response-value-result.json"
MODEL = ANALYSIS / "d83a-threatened-response-value-model.tsv"

EXPECTED_PROTOCOL_SHA256 = "7f44611f0f38dd272ab7ee4daf30dd3c3d2e0e740f99e9e13381265fc5ef5e41"
EXPECTED_FEATURE_SHA256 = "17d2ca501204baa026e2c388a8d550b5251479e4b75206317a04bca93f15bbeb"
EXPECTED_D82_ROWS_SHA256 = "a2d9e12d12b550398f1b84946daccdf01da379dd9155083969ed22ca5bf1438b"
EXPECTED_D82_RESULT_SHA256 = "efa13cd95f30d4b5796441916e4b35fba84935b248122030964feeff7f9d5342"
EXPECTED_EXPORTER_SHA256 = "5fc03ded5aac52d27ea3f20612a3acffe5ad5008a024dcf38b74c4824a855a73"

FEATURES = 169
LAMBDA = 10.0
TASKS = 512
ROOTED_TASKS = 449
SEMANTIC_ROWS = 656
ARMS = ("fell", "harvest", "renew")
PRIORITY = {"control": 0, "harvest": 1, "renew": 2, "fell": 3}


@dataclass(frozen=True)
class Ridge:
    mean: np.ndarray
    scale: np.ndarray
    weight: np.ndarray
    intercept: float


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    return rows, fields


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def arm_key(row: dict[str, str]) -> tuple[int, int, str, str]:
    return (*task_key(row), row["arm"])


def fit_ridge(x: np.ndarray, y: np.ndarray, penalty: float = LAMBDA) -> Ridge:
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale = np.where(scale > 1.0e-12, scale, 1.0)
    z = (x - mean) / scale
    intercept = float(y.mean())
    gram = z.T @ z + penalty * np.eye(z.shape[1], dtype=np.float64)
    weight = np.linalg.solve(gram, z.T @ (y - intercept))
    return Ridge(mean=mean, scale=scale, weight=weight, intercept=intercept)


def predict(model: Ridge, x: np.ndarray) -> np.ndarray:
    return model.intercept + ((x - model.mean) / model.scale) @ model.weight


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and values[order[stop]] == values[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1)
        start = stop
    return ranks


def correlation(left: np.ndarray, right: np.ndarray) -> float:
    if left.std() == 0 or right.std() == 0:
        return 0.0
    return float(np.corrcoef(left, right)[0, 1])


def oof_predictions(x: np.ndarray, y: np.ndarray, maps: np.ndarray) -> np.ndarray:
    predictions = np.full(len(y), np.nan, dtype=np.float64)
    for fold in range(8):
        validation = maps % 8 == fold
        training = ~validation
        model = fit_ridge(x[training], y[training])
        predictions[validation] = predict(model, x[validation])
    assert np.isfinite(predictions).all()
    return predictions


def policy_metrics(
    semantic_rows: list[dict],
    control: dict[tuple[int, int, str], dict[str, str]],
    predictions: np.ndarray,
) -> dict:
    by_task: dict[tuple[int, int, str], list[tuple[str, float, dict]]] = defaultdict(list)
    for row, prediction in zip(semantic_rows, predictions):
        by_task[row["task"]].append((row["arm"], float(prediction), row))
    selected = []
    for task in sorted(control):
        choices = [("control", 0.0, None), *by_task.get(task, [])]
        arm, score, row = min(
            choices,
            key=lambda item: (-item[1], PRIORITY[item[0]]),
        )
        if score <= 0:
            arm, score, row = "control", 0.0, None
        selected.append(
            {
                "task": task,
                "arm": arm,
                "prediction": score,
                "margin_delta": 0 if row is None else row["margin_delta"],
                "own_score_delta": 0 if row is None else row["own_score_delta"],
                "opponent_score_delta": 0 if row is None else row["opponent_score_delta"],
                "rooted": int(control[task]["root_seen"]) == 1,
            }
        )
    rooted = [row for row in selected if row["rooted"]]
    family: dict[str, list[int]] = defaultdict(list)
    folds: dict[int, list[int]] = defaultdict(list)
    for row in selected:
        family[row["task"][2]].append(row["margin_delta"])
        folds[row["task"][0] % 8].append(row["margin_delta"])
    arm_counts = Counter(row["arm"] for row in selected)
    return {
        "tasks": len(selected),
        "rooted_tasks": len(rooted),
        "mean_margin_gain": float(np.mean([row["margin_delta"] for row in selected])),
        "rooted_strict_improvement_rate": float(
            np.mean([row["margin_delta"] > 0 for row in rooted])
        ),
        "rooted_regression_rate": float(
            np.mean([row["margin_delta"] < 0 for row in rooted])
        ),
        "mean_own_score_delta": float(
            np.mean([row["own_score_delta"] for row in selected])
        ),
        "mean_opponent_score_delta": float(
            np.mean([row["opponent_score_delta"] for row in selected])
        ),
        "opponent_family_mean_margin_gains": {
            name: float(np.mean(values)) for name, values in sorted(family.items())
        },
        "fold_mean_margin_gains": {
            str(fold): float(np.mean(values)) for fold, values in sorted(folds.items())
        },
        "intervention_rate_on_rooted_tasks": float(
            np.mean([row["arm"] != "control" for row in rooted])
        ),
        "selected_arm_counts": dict(sorted(arm_counts.items())),
        "strict_selected_arm_counts": dict(
            sorted(
                Counter(
                    row["arm"]
                    for row in selected
                    if row["arm"] != "control" and row["margin_delta"] > 0
                ).items()
            )
        ),
    }


def frozen_gates(metrics: dict) -> dict[str, bool]:
    family = metrics["opponent_family_mean_margin_gains"]
    folds = metrics["fold_mean_margin_gains"]
    selected = metrics["selected_arm_counts"]
    gates = {
        "mean_margin_gain_at_least_2": metrics["mean_margin_gain"] >= 2,
        "strict_improvement_at_least_30_percent": metrics[
            "rooted_strict_improvement_rate"
        ]
        >= 0.30,
        "regression_at_most_30_percent": metrics["rooted_regression_rate"] <= 0.30,
        "own_nonnegative_or_opponent_nonpositive": metrics["mean_own_score_delta"] >= 0
        or metrics["mean_opponent_score_delta"] <= 0,
        "six_nonnegative_families_and_worst_at_least_minus_3": len(family) == 8
        and sum(value >= 0 for value in family.values()) >= 6
        and min(family.values()) >= -3,
        "intervention_rate_between_10_and_70_percent": 0.10
        <= metrics["intervention_rate_on_rooted_tasks"]
        <= 0.70,
        "two_semantic_arms_selected_at_least_8": sum(
            selected.get(arm, 0) >= 8 for arm in ARMS
        )
        >= 2,
        "six_nonnegative_folds_and_worst_at_least_minus_5": len(folds) == 8
        and sum(value >= 0 for value in folds.values()) >= 6
        and min(folds.values()) >= -5,
    }
    return {name: bool(value) for name, value in gates.items()}


def write_model(path: Path, model: Ridge) -> None:
    with path.open("x", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(("intercept", "feature", "mean", "scale", "weight"))
        for index in range(FEATURES):
            writer.writerow(
                (
                    f"{model.intercept:.17g}",
                    f"feature_{index:03d}",
                    f"{model.mean[index]:.17g}",
                    f"{model.scale[index]:.17g}",
                    f"{model.weight[index]:.17g}",
                )
            )


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (FEATURE_A, EXPECTED_FEATURE_SHA256),
        (FEATURE_B, EXPECTED_FEATURE_SHA256),
        (D82_ROWS, EXPECTED_D82_ROWS_SHA256),
        (D82_RESULT, EXPECTED_D82_RESULT_SHA256),
        (EXPORTER, EXPECTED_EXPORTER_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D83a prerequisite missing or changed: {path}")
    if FEATURE_A.read_bytes() != FEATURE_B.read_bytes():
        raise RuntimeError("D83a feature exports are not byte-identical")
    if OUTPUT.exists() or MODEL.exists():
        raise SystemExit("refusing to overwrite D83a output")

    feature_rows, fields = read_table(FEATURE_A)
    d82_rows, _ = read_table(D82_ROWS)
    feature_names = [f"feature_{index:03d}" for index in range(FEATURES)]
    if fields[-FEATURES:] != feature_names or len(feature_rows) != TASKS + SEMANTIC_ROWS:
        raise RuntimeError("D83a feature schema or row count mismatch")
    d82 = {arm_key(row): row for row in d82_rows}
    controls = {
        task_key(row): row for row in d82_rows if row["arm"] == "control"
    }
    if len(controls) != TASKS:
        raise RuntimeError("D83a D82 control coverage mismatch")

    integrity_failures = 0
    semantic = []
    control_feature_rows = 0
    for row in feature_rows:
        task = task_key(row)
        values = np.asarray([float(row[name]) for name in feature_names], dtype=np.float64)
        integrity_failures += int(not np.isfinite(values).all())
        control_row = controls[task]
        for field in ("root_seen", "root_turn", "root_state_hash", "root_candidate_count"):
            integrity_failures += int(row[field] != control_row[field])
        if row["arm"] == "control":
            control_feature_rows += 1
            if row["root_seen"] == "0":
                integrity_failures += int(np.any(values != 0))
            continue
        source = d82.get(arm_key(row))
        if source is None:
            integrity_failures += 1
            continue
        integrity_failures += int(source["arm_available"] != "1")
        integrity_failures += int(row["prior_rank"] != source["arm_prior_rank"])
        integrity_failures += int(
            int(row["action"]) // 242 != int(source["arm_action_plane"])
        )
        integrity_failures += int(values[106 + 31] != 1.0)
        integrity_failures += int(values[150 + 13] != 1.0)
        expected_onehot = {
            "fell": np.asarray([1.0, 0.0, 0.0]),
            "harvest": np.asarray([0.0, 1.0, 0.0]),
            "renew": np.asarray([0.0, 0.0, 1.0]),
        }[row["arm"]]
        integrity_failures += int(not np.array_equal(values[166:169], expected_onehot))
        semantic.append(
            {
                "task": task,
                "arm": row["arm"],
                "features": values,
                "margin_delta": int(source["margin"]) - int(control_row["margin"]),
                "own_score_delta": int(source["own_score"])
                - int(control_row["own_score"]),
                "opponent_score_delta": int(source["opponent_score"])
                - int(control_row["opponent_score"]),
            }
        )
    expected_semantic = {
        key for key, row in d82.items() if key[3] != "control" and row["arm_available"] == "1"
    }
    actual_semantic = {(*row["task"], row["arm"]) for row in semantic}
    integrity_failures += len(expected_semantic.symmetric_difference(actual_semantic))
    integrity_failures += int(control_feature_rows != TASKS)

    x = np.stack([row["features"] for row in semantic])
    y = np.asarray([row["margin_delta"] for row in semantic], dtype=np.float64)
    maps = np.asarray([row["task"][0] for row in semantic], dtype=np.int64)
    first_predictions = oof_predictions(x, y, maps)
    second_predictions = oof_predictions(x, y, maps)
    repeat_equal = np.array_equal(first_predictions, second_predictions)
    integrity_failures += int(not repeat_equal)
    metrics = policy_metrics(semantic, controls, first_predictions)
    gates = frozen_gates(metrics)
    passed = integrity_failures == 0 and all(gates.values())

    positive = first_predictions > 0
    diagnostics = {
        "rows": len(semantic),
        "target_mean": float(y.mean()),
        "prediction_mean": float(first_predictions.mean()),
        "prediction_standard_deviation": float(first_predictions.std()),
        "pearson": correlation(first_predictions, y),
        "spearman": correlation(rankdata(first_predictions), rankdata(y)),
        "predicted_positive_rows": int(positive.sum()),
        "predicted_positive_precision": float(np.mean(y[positive] > 0)) if positive.any() else 0.0,
        "oracle_capture": metrics["mean_margin_gain"] / 11.240234375,
    }
    model_info = None
    if passed:
        full_model = fit_ridge(x, y)
        repeat_model = fit_ridge(x, y)
        if not (
            np.array_equal(full_model.mean, repeat_model.mean)
            and np.array_equal(full_model.scale, repeat_model.scale)
            and np.array_equal(full_model.weight, repeat_model.weight)
            and full_model.intercept == repeat_model.intercept
        ):
            raise RuntimeError("D83a full-fit repeat mismatch")
        write_model(MODEL, full_model)
        model_info = {
            "path": str(MODEL),
            "sha256": sha256(MODEL),
            "intercept": full_model.intercept,
            "weight_l2": float(np.linalg.norm(full_model.weight)),
            "nonzero_weights": int(np.count_nonzero(full_model.weight)),
        }

    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "feature_export": str(FEATURE_A),
            "feature_export_sha256": sha256(FEATURE_A),
            "d82_rows": str(D82_ROWS),
            "d82_rows_sha256": sha256(D82_ROWS),
            "exporter_sha256": sha256(EXPORTER),
        },
        "audit": {
            "feature_rows": len(feature_rows),
            "control_rows": control_feature_rows,
            "semantic_rows": len(semantic),
            "feature_count": FEATURES,
            "byte_repeat_export": True,
            "deterministic_repeat_fit": repeat_equal,
            "integrity_failures": integrity_failures,
        },
        "recipe": {"folds": 8, "fold_rule": "map_seed mod 8", "ridge_lambda": LAMBDA},
        "diagnostics": diagnostics,
        "oof_policy": metrics,
        "gates": gates,
        "pass": passed,
        "decision": (
            "pass_serialize_model_open_d83b_prospective_closed_loop"
            if passed
            else "reject_close_pooled_snapshot_value_model"
        ),
        "model": model_info,
        "scope": "consumed D82 held-map predictability only; no candidate or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
