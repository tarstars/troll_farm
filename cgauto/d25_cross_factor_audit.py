#!/usr/bin/env python3
"""Audit the frozen D25 selector under structural and crossed holdouts."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d25_turn75_regime_selector import (
    evaluate_policy,
    forest_predict_fold,
    prepare,
    read_features,
    read_label_paths,
    row_key,
    save,
)


STRUCTURAL_FAMILIES = (
    ("compact_gold", "gold_elite"),
    ("gold_adaptive",),
    ("mybot",),
    ("printer_bot",),
    ("sched_bot",),
    ("script_boss",),
    ("silver_boss",),
)
FROZEN_CONFIG = {
    "family": "random_forest",
    "trees": 256,
    "max_depth": 4,
    "min_leaf": 40,
    "label": "random_forest_d4_l40",
}
FROZEN_BUFFER = 30.0


def fit_fold(payload):
    matrix, targets, seeds, train, held, random_seed = payload
    return held, forest_predict_fold(
        matrix,
        targets,
        seeds,
        train,
        held,
        FROZEN_CONFIG,
        random_seed,
    )


def structural_tasks(matrix, targets, seeds, opponents):
    tasks = []
    for index, family in enumerate(STRUCTURAL_FAMILIES):
        held_mask = np.isin(opponents, family)
        tasks.append(
            (
                matrix,
                targets,
                seeds,
                np.flatnonzero(~held_mask),
                np.flatnonzero(held_mask),
                2501 + 100_000_000 + index * 100_003,
            )
        )
    return tasks


def crossed_tasks(matrix, targets, seeds, opponents):
    unique_seeds = np.unique(seeds)
    tasks = []
    index = 0
    for start in range(0, 120, 20):
        seed_mask = np.isin(seeds, unique_seeds[start : start + 20])
        for family in STRUCTURAL_FAMILIES:
            family_mask = np.isin(opponents, family)
            train = np.flatnonzero(~(seed_mask | family_mask))
            held = np.flatnonzero(seed_mask & family_mask)
            tasks.append(
                (
                    matrix,
                    targets,
                    seeds,
                    train,
                    held,
                    2501 + 200_000_000 + index * 100_003,
                )
            )
            index += 1
    return tasks


def run_tasks(tasks, size: int, jobs: int) -> np.ndarray:
    predictions = np.zeros(size, dtype=np.float64)
    covered = np.zeros(size, dtype=bool)
    if jobs == 1:
        results = [fit_fold(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(jobs, len(tasks))) as pool:
            results = list(pool.map(fit_fold, tasks))
    for held, values in results:
        if np.any(covered[held]):
            raise ValueError("audit folds overlap")
        predictions[held] = values
        covered[held] = True
    if not np.all(covered):
        raise ValueError("audit folds do not cover every row")
    return predictions


def execute(matrix, targets, seeds, opponents, jobs):
    structural = run_tasks(
        structural_tasks(matrix, targets, seeds, opponents), len(targets), jobs
    )
    crossed = run_tasks(
        crossed_tasks(matrix, targets, seeds, opponents), len(targets), jobs
    )
    return structural, crossed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--labels", type=Path, action="append", required=True)
    parser.add_argument("--d25", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    d25 = json.loads(args.d25.read_text())
    selected = d25["selected"]
    if selected["config"] != FROZEN_CONFIG or selected["buffer"] != FROZEN_BUFFER:
        raise SystemExit("D25 selected model does not match the frozen D25a audit")

    feature_rows, feature_names = read_features(args.features)
    labels = read_label_paths(args.labels)
    rows, matrix, varying_names, integrity = prepare(
        feature_rows, feature_names, labels
    )
    if not integrity["passed"]:
        raise SystemExit("D25 integrity no longer passes")
    targets = np.asarray([row["margin_delta"] for row in rows], dtype=np.float64)
    seeds = np.asarray([row["seed"] for row in rows], dtype=np.int64)
    opponents = np.asarray([row["opponent"] for row in rows], dtype=object)
    structural, crossed = execute(matrix, targets, seeds, opponents, args.jobs)
    structural_report = evaluate_policy(rows, structural, FROZEN_BUFFER)
    crossed_report = evaluate_policy(rows, crossed, FROZEN_BUFFER)

    reversed_rows, reversed_matrix, reversed_names, reversed_integrity = prepare(
        list(reversed(feature_rows)), feature_names, labels
    )
    if (
        not reversed_integrity["passed"]
        or reversed_names != varying_names
        or [row_key(row) for row in reversed_rows] != [row_key(row) for row in rows]
        or not np.array_equal(reversed_matrix, matrix)
    ):
        raise SystemExit("row-order canonicalization mismatch")
    repeated_structural, repeated_crossed = execute(
        reversed_matrix, targets, seeds, opponents, args.jobs
    )
    repeat = {
        "structural_predictions_exact": np.array_equal(
            structural, repeated_structural
        ),
        "crossed_predictions_exact": np.array_equal(crossed, repeated_crossed),
        "structural_hash": structural_report["prediction_hash"],
        "structural_repeat_hash": evaluate_policy(
            reversed_rows, repeated_structural, FROZEN_BUFFER
        )["prediction_hash"],
        "crossed_hash": crossed_report["prediction_hash"],
        "crossed_repeat_hash": evaluate_policy(
            reversed_rows, repeated_crossed, FROZEN_BUFFER
        )["prediction_hash"],
    }
    repeat["passed"] = (
        repeat["structural_predictions_exact"]
        and repeat["crossed_predictions_exact"]
        and repeat["structural_hash"] == repeat["structural_repeat_hash"]
        and repeat["crossed_hash"] == repeat["crossed_repeat_hash"]
    )
    passed = structural_report["passed"] and crossed_report["passed"] and repeat["passed"]
    payload = {
        "schema": 1,
        "scope": (
            "no-retuning audit of the frozen D25 random_forest_d4_l40_b30 selector; "
            "behavioral-alias structural-family and simultaneous unseen-map/unseen-family folds"
        ),
        "source": str(args.d25),
        "config": FROZEN_CONFIG,
        "buffer": FROZEN_BUFFER,
        "rows": len(rows),
        "features": len(varying_names),
        "structural_families": STRUCTURAL_FAMILIES,
        "structural_family_holdout": structural_report,
        "crossed_map_structural_family_holdout": crossed_report,
        "repeat": repeat,
        "passed": passed,
        "decision": {
            "open_prospective_seeds_50120_50179": passed,
            "retune": False,
            "build_candidate": False,
            "submit": False,
        },
    }
    save(args.output, payload)
    print(
        json.dumps(
            {
                "structural_family": structural_report,
                "crossed": crossed_report,
                "repeat": repeat,
                "passed": passed,
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
