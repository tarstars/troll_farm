#!/usr/bin/env python3
"""Recreate D153 outer fits and export every held relative-value score."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import gc
import json
import multiprocessing
from pathlib import Path

import numpy as np

from cgauto import run_d153a_conditional_value_selection as d153a
from cgauto import train_d153a_conditional_value_policy as trainer


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d153b-oof-confidence-abstention-diagnostic-protocol-2026-07-23.md"
LOCK = BASE / "d153b-oof-confidence-abstention-diagnostic-lock.json"
SCORES_A = BASE / "d153b-oof-confidence-scores-a.tsv"
SCORES_B = BASE / "d153b-oof-confidence-scores-b.tsv"
METADATA_A = BASE / "d153b-oof-confidence-scores-a-metadata.json"
METADATA_B = BASE / "d153b-oof-confidence-scores-b-metadata.json"

SCORE_FIELDS = (
    "seed",
    "held_fold",
    "map_seed",
    "seat",
    "opponent",
    "target_active",
    "candidate_slot",
    "predicted_value",
    "exact_value",
)

_DATASET = None


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = d153a.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D153b lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d153a.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def score(value: float) -> str:
    return f"{float(value):.9f}"


def _fold_seed_worker(held_fold: int, seed: int) -> dict:
    if _DATASET is None:
        raise RuntimeError("D153b fork worker lacks its read-only dataset")
    folds = np.asarray(_DATASET["folds"])
    train_indices = np.flatnonzero(folds != held_fold)
    held_indices = np.flatnonzero(folds == held_fold)
    training = trainer.subset(_DATASET, train_indices)
    held = trainer.subset(_DATASET, held_indices)
    model, training_summary = trainer.train_model(
        training, seed, threads=d153a.THREADS_PER_WORKER
    )
    predicted = trainer.predict_margin_values(model, held)
    rows = []
    for group, task in enumerate(held["tasks"]):
        count = int(held["valid"][group].sum())
        for action in range(count):
            rows.append(
                {
                    "seed": seed,
                    "held_fold": held_fold,
                    "map_seed": int(task[0]),
                    "seat": int(task[1]),
                    "opponent": str(task[2]),
                    "target_active": int(held["target_active"][group]),
                    "candidate_slot": int(held["candidate_slots"][group, action]),
                    "predicted_value": score(predicted[group, action]),
                    "exact_value": int(held["target_values"][group, action]),
                }
            )
    result = {
        "held_fold": held_fold,
        "seed": seed,
        "training_groups": len(train_indices),
        "held_groups": len(held_indices),
        "rows": len(rows),
        "model_hash": training_summary["model_hash"],
        "training": training_summary,
        "scores": rows,
    }
    del training, held, model
    gc.collect()
    return result


def export(scores_path: Path, metadata_path: Path) -> dict:
    global _DATASET
    if scores_path.exists() or metadata_path.exists():
        raise FileExistsError(scores_path if scores_path.exists() else metadata_path)
    lock = verify_lock()
    parent = json.loads(d153a.OUTPUT.read_text())
    if parent["decision"] != "close_d153_compact_conditional_value_policy":
        raise RuntimeError("D153a is not at the frozen D153b boundary")
    _DATASET, structural = d153a.load_dataset()
    context = multiprocessing.get_context("fork")
    jobs = [
        (held_fold, seed)
        for held_fold in range(d153a.FOLDS)
        for seed in d153a.SEEDS
    ]
    try:
        with ProcessPoolExecutor(
            max_workers=d153a.WORKERS, mp_context=context
        ) as executor:
            futures = [executor.submit(_fold_seed_worker, *job) for job in jobs]
            fits = [future.result() for future in futures]
    finally:
        _DATASET = None
        gc.collect()
    ordered = sorted(fits, key=lambda row: (row["seed"], row["held_fold"]))
    rows = [score_row for fit in ordered for score_row in fit.pop("scores")]
    expected_rows = len(d153a.SEEDS) * int(structural["actions"])
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"D153b score row drift: {len(rows)} != {expected_rows}"
        )
    with scores_path.open("x", newline="") as target:
        writer = csv.DictWriter(
            target, fieldnames=SCORE_FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "schema": "troll-farm-d153b-oof-confidence-score-export-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d153a": {
            "path": str(d153a.OUTPUT.relative_to(ROOT)),
            "sha256": d153a.sha256(d153a.OUTPUT),
            "decision": parent["decision"],
        },
        "scores": {
            "path": str(scores_path.relative_to(ROOT)),
            "rows": len(rows),
            "bytes": scores_path.stat().st_size,
            "sha256": d153a.sha256(scores_path),
        },
        "dataset": structural,
        "fits": ordered,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("export-a", "export-b"))
    args = parser.parse_args()
    if args.mode == "export-a":
        export(SCORES_A, METADATA_A)
    else:
        export(SCORES_B, METADATA_B)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
