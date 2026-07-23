#!/usr/bin/env python3
"""Fit D114a root-balanced ridge scorers and select one on fresh validation maps."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113
from cgauto.make_d110a_antithetic_q6_linear_population import render


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d114a-supervised-one-use-q6-linear-scorer-protocol-2026-07-22.md"
FROZEN_INPUTS = BASE / "d114a-supervised-one-use-q6-linear-scorer-repair1-frozen-inputs.json"
TRAIN_ARMS = BASE / "d114a-q6-train-arms-9843300-9843315.tsv"
TRAIN_BASELINES = BASE / "d114a-q6-train-baselines-9843300-9843315.tsv"
VALIDATION_ARMS = BASE / "d114a-q6-validation-arms-9843400-9843407.tsv"
VALIDATION_BASELINES = BASE / "d114a-q6-validation-baselines-9843400-9843407.tsv"
POPULATION = BASE / "d114a-supervised-one-use-q6-linear-population.tsv"
OUTPUT = BASE / "d114a-supervised-one-use-q6-linear-fit-result.json"

TRAIN_START = 9_843_300
TRAIN_MAPS = 16
VALIDATION_START = 9_843_400
VALIDATION_MAPS = 8
FEATURES = 379
CLIPS = (50.0, 100.0)
ALPHAS = (1.0, 10.0, 100.0, 1000.0)
OFFSETS = (0.0, 2.0, 5.0, 10.0, 15.0, 20.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_inputs() -> dict:
    payload = json.loads(FROZEN_INPUTS.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {
        "manifest_sha256": sha256(FROZEN_INPUTS),
        "declared": payload,
        "mismatches": mismatches,
        "pass": not mismatches,
    }


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def panel(
    arms_path: Path,
    baselines_path: Path,
    start: int,
    maps: int,
    elapsed: float,
) -> dict:
    arms, fields = read_table(arms_path)
    baselines, _ = read_table(baselines_path)
    d113.START_SEED = start
    d113.MAPS = maps
    mechanics, baseline_by_task, arms_by_root = d113.zero_aware_mechanics(
        arms,
        baselines,
        fields,
        elapsed,
        {"pass": True},
    )
    teacher, labels = d113.teacher_analysis(arms, baseline_by_task, arms_by_root)
    label_by_key = {
        (
            (
                int(row["map_seed"]),
                int(row["seat"]),
                row["opponent"],
            ),
            int(row["boundary_index"]),
            int(row["slot"]),
        ): row
        for row in labels
    }
    action_fields = [f"action_{index:03}" for index in range(FEATURES)]
    x = np.asarray(
        [[float(row[field]) for field in action_fields] for row in arms],
        dtype=np.float64,
    )
    y = np.asarray(
        [label_by_key[d112.arm_key(row)]["act_advantage"] for row in arms],
        dtype=np.float64,
    )
    root_keys = [d112.root_key(row) for row in arms]
    assert x.shape == (len(arms), FEATURES)
    assert y.shape == (len(arms),)
    assert np.isfinite(x).all() and np.isfinite(y).all()
    assert np.array_equal(x[:, 0], np.ones(len(arms)))
    return {
        "arms": arms,
        "baselines": baselines,
        "baseline_by_task": baseline_by_task,
        "arms_by_root": arms_by_root,
        "mechanics": mechanics,
        "teacher": teacher,
        "x": x,
        "y": y,
        "root_keys": root_keys,
        "start": start,
    }


def ridge(
    x: np.ndarray,
    y: np.ndarray,
    root_keys: list,
    clip: float,
    alpha: float,
) -> np.ndarray:
    counts = Counter(root_keys)
    sample_weight = np.asarray([1.0 / counts[key] for key in root_keys])
    target = np.clip(y, -clip, clip)
    gram = x.T @ (sample_weight[:, None] * x)
    rhs = x.T @ (sample_weight * target)
    penalty = np.eye(x.shape[1]) * alpha
    penalty[0, 0] = 0.0
    weights = np.linalg.solve(gram + penalty, rhs)
    assert weights.shape == (FEATURES,) and np.isfinite(weights).all()
    return weights


def rounded(weights: np.ndarray, offset: float) -> np.ndarray:
    result = weights.copy()
    result[0] -= offset
    result = np.round(result, 8).astype(np.float32)
    assert np.isfinite(result).all()
    return result


def policy_metrics(data: dict, weights: np.ndarray) -> dict:
    arms = data["arms"]
    predictions = data["x"].astype(np.float32) @ weights
    score_by_key = {
        d112.arm_key(row): float(score) for row, score in zip(arms, predictions)
    }
    selected = []
    positive_ties = 0
    for task, control in data["baseline_by_task"].items():
        choice = None
        boundary_count = int(control["boundary_count"])
        for boundary in range(boundary_count):
            rows = data["arms_by_root"][(task, boundary)]
            scores = [score_by_key[d112.arm_key(row)] for row in rows]
            best_score = max(scores)
            if best_score <= 0.0:
                continue
            winners = [index for index, score in enumerate(scores) if score == best_score]
            positive_ties += int(len(winners) > 1)
            choice = rows[winners[0]]
            break
        outcome = choice or control
        selected.append(
            {
                "task": task,
                "opponent": task[2],
                "map_seed": task[0],
                "margin": d112.margin(outcome) - d112.margin(control),
                "own": int(outcome["own_score"]) - int(control["own_score"]),
                "rival": int(outcome["opponent_score"])
                - int(control["opponent_score"]),
                "intervened": choice is not None,
                "crop": int(outcome["own_created_crops"]) > 0,
                "worker_three": int(outcome["own_workers"]) >= 3,
                "control_worker_three": int(control["own_workers"]) >= 3,
            }
        )
    family = {
        opponent: d112.mean(
            row["margin"] for row in selected if row["opponent"] == opponent
        )
        for opponent in d112.OPPONENTS
    }
    folds = {
        str(fold): d112.mean(
            row["margin"]
            for row in selected
            if (row["map_seed"] - data["start"]) % 2 == fold
        )
        for fold in range(2)
    }
    return {
        "tasks": len(selected),
        "mean_margin_delta": d112.mean(row["margin"] for row in selected),
        "strict_improvement_rate": d112.mean(row["margin"] > 0 for row in selected),
        "mean_own_score_delta": d112.mean(row["own"] for row in selected),
        "mean_opponent_score_delta": d112.mean(row["rival"] for row in selected),
        "family_mean_margin_delta": family,
        "positive_families": sum(value > 0 for value in family.values()),
        "worst_family": min(family.values()),
        "fold_mean_margin_delta": folds,
        "intervention_rate": d112.mean(row["intervened"] for row in selected),
        "crop_rate": d112.mean(row["crop"] for row in selected),
        "worker_three_rate": d112.mean(row["worker_three"] for row in selected),
        "control_worker_three_rate": d112.mean(
            row["control_worker_three"] for row in selected
        ),
        "positive_score_ties": positive_ties,
    }


def admission(metrics: dict) -> dict[str, bool]:
    return {
        "mean_at_least_2": metrics["mean_margin_delta"] >= 2.0,
        "strict_at_least_30pct": metrics["strict_improvement_rate"] >= 0.30,
        "both_folds_nonnegative": min(metrics["fold_mean_margin_delta"].values()) >= 0.0,
        "worst_family_at_least_minus5": metrics["worst_family"] >= -5.0,
        "five_positive_families": metrics["positive_families"] >= 5,
        "own_nonnegative_or_opponent_nonpositive": (
            metrics["mean_own_score_delta"] >= 0.0
            or metrics["mean_opponent_score_delta"] <= 0.0
        ),
        "activity_10_to_85pct": 0.10 <= metrics["intervention_rate"] <= 0.85,
        "crop_100pct": metrics["crop_rate"] == 1.0,
        "worker_three_within_5pp": (
            metrics["worker_three_rate"]
            >= metrics["control_worker_three_rate"] - 0.05
        ),
    }


def population(weights: np.ndarray) -> list[dict]:
    zeros = [0.0] * FEATURES
    values = [float(value) for value in weights]
    rows = [{"policy": "zero_control", "kind": "zero", "budget": 4, "parameters": zeros}]
    for index in range(64):
        parameters = values if index == 0 else zeros
        rows.extend(
            [
                {
                    "policy": f"one_{index:02d}",
                    "kind": "one",
                    "budget": 1,
                    "parameters": parameters,
                },
                {
                    "policy": f"four_{index:02d}",
                    "kind": "four",
                    "budget": 4,
                    "parameters": parameters,
                },
            ]
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-elapsed", type=float, required=True)
    parser.add_argument("--validation-elapsed", type=float, required=True)
    args = parser.parse_args()
    frozen = verify_frozen_inputs()
    train = panel(
        TRAIN_ARMS,
        TRAIN_BASELINES,
        TRAIN_START,
        TRAIN_MAPS,
        args.train_elapsed,
    )
    validation = panel(
        VALIDATION_ARMS,
        VALIDATION_BASELINES,
        VALIDATION_START,
        VALIDATION_MAPS,
        args.validation_elapsed,
    )
    mechanics_pass = frozen["pass"] and train["mechanics"]["pass"] and validation["mechanics"]["pass"]
    candidates = []
    fitted = {}
    if mechanics_pass:
        grid_index = 0
        for clip in CLIPS:
            for alpha in ALPHAS:
                base = ridge(train["x"], train["y"], train["root_keys"], clip, alpha)
                fitted[(clip, alpha)] = base
                for offset in OFFSETS:
                    weights = rounded(base, offset)
                    metrics = policy_metrics(validation, weights)
                    gates = admission(metrics)
                    candidates.append(
                        {
                            "grid_index": grid_index,
                            "clip": clip,
                            "alpha": alpha,
                            "offset": offset,
                            "weight_hash": hashlib.sha256(weights.tobytes()).hexdigest(),
                            "metrics": metrics,
                            "admission": gates,
                            "admitted": all(gates.values()),
                        }
                    )
                    grid_index += 1
    admitted = [candidate for candidate in candidates if candidate["admitted"]]
    selected = None
    final_weights = None
    if admitted:
        selected = max(
            admitted,
            key=lambda candidate: (
                min(candidate["metrics"]["fold_mean_margin_delta"].values()),
                candidate["metrics"]["worst_family"],
                candidate["metrics"]["mean_margin_delta"],
                candidate["metrics"]["strict_improvement_rate"],
                -candidate["metrics"]["intervention_rate"],
                -candidate["grid_index"],
            ),
        )
        combined_x = np.concatenate((train["x"], validation["x"]), axis=0)
        combined_y = np.concatenate((train["y"], validation["y"]), axis=0)
        combined_roots = [
            ("train", key) for key in train["root_keys"]
        ] + [("validation", key) for key in validation["root_keys"]]
        base = ridge(
            combined_x,
            combined_y,
            combined_roots,
            selected["clip"],
            selected["alpha"],
        )
        final_weights = rounded(base, selected["offset"])
        POPULATION.write_text(render(population(final_weights)))

    result = {
        "schema": "troll-farm-d114a-supervised-one-use-q6-linear-fit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "collection_mechanics": {
            "train": train["mechanics"],
            "validation": validation["mechanics"],
            "pass": mechanics_pass,
        },
        "teacher": {"train": train["teacher"], "validation": validation["teacher"]},
        "grid": {
            "clips": CLIPS,
            "alphas": ALPHAS,
            "offsets": OFFSETS,
            "candidates": len(candidates),
            "admitted": len(admitted),
            "results": candidates,
        },
        "selected": selected,
        "population": {
            "path": str(POPULATION.relative_to(ROOT)) if final_weights is not None else None,
            "sha256": sha256(POPULATION) if final_weights is not None else None,
            "final_weight_hash": (
                hashlib.sha256(final_weights.tobytes()).hexdigest()
                if final_weights is not None
                else None
            ),
            "nonzero_weights": int(np.count_nonzero(final_weights)) if final_weights is not None else 0,
            "maximum_absolute_weight": (
                float(np.max(np.abs(final_weights))) if final_weights is not None else None
            ),
        },
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (TRAIN_ARMS, TRAIN_BASELINES, VALIDATION_ARMS, VALIDATION_BASELINES)
        },
        "decision": (
            "open_repeated_held_qualification"
            if selected is not None
            else "repair_only"
            if not mechanics_pass
            else "close_supervised_linear_without_held"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
