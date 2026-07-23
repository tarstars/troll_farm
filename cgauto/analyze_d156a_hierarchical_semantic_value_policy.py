#!/usr/bin/env python3
"""Cross-fit deterministic hierarchical macro-semantic value policies."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from cgauto import analyze_d153b_oof_confidence_abstention as d153b
from cgauto import run_d153a_conditional_value_selection as d153a
from cgauto import run_d155a_first_action_memory_value_ablation as d155a
from cgauto import train_d153a_conditional_value_policy as d153_trainer


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d156a-hierarchical-semantic-value-policy-protocol-2026-07-23.md"
LOCK = BASE / "d156a-hierarchical-semantic-value-policy-lock.json"
OUTPUT = BASE / "d156a-hierarchical-semantic-value-policy-result.json"

SHRINKAGE = 16.0
LCB_STANDARD_DEVIATIONS = 0.5
VARIANTS = (
    "jobs",
    "job_owner",
    "job_owner_phase",
    "job_owner_phase_rank",
    "job_owner_regime",
    "job_owner_phase_lcb",
    "job_owner_regime_lcb",
)


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = d153a.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D156 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d153a.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def positive_one_hot(features: np.ndarray, start: int, count: int) -> int:
    selected = np.flatnonzero(features[start : start + count] > 0.5)
    if len(selected) > 1:
        raise RuntimeError("D156 semantic delta has multiple positive one-hot entries")
    return int(selected[0]) if len(selected) else 0


def decode_action(features: np.ndarray) -> dict[str, int | tuple]:
    features = np.asarray(features, dtype=np.float32)
    if features.shape != (379,) or not np.isfinite(features).all():
        raise ValueError("D156 action feature shape/value drift")
    if features[0] <= 0.5:
        raise ValueError("D156 decoder requires a noncontrol action")
    kind = positive_one_hot(features, 1, 4)
    if kind == 0:
        raise RuntimeError("D156 noncontrol action lacks a positive proposal kind")
    job_one = positive_one_hot(features, 5, 5)
    job_two = positive_one_hot(features, 10, 5)
    owner_one = positive_one_hot(features, 15, 5)
    owner_two = positive_one_hot(features, 20, 5)

    def rank_bucket(index: int) -> int:
        value = max(0.0, float(features[index]))
        return min(3, int(math.floor(value * 4.0)))

    jobs = (kind, job_one, job_two)
    owner = (*jobs, owner_one, owner_two)
    return {
        "jobs": jobs,
        "job_owner": owner,
        "rank_one": rank_bucket(25),
        "rank_two": rank_bucket(26),
    }


def state_regime(state: np.ndarray) -> dict[str, int]:
    state = np.asarray(state, dtype=np.float32)
    if state.shape != (64,) or not np.isfinite(state).all():
        raise ValueError("D156 state feature shape/value drift")
    phase = min(2, max(0, int(math.floor(float(state[56]) * 3.0))))
    workers = max(0, int(round(float(state[2]) * 3.0)))
    crops = max(0, int(round(float(state[58]) * 20.0)))
    crop_bucket = 0 if crops <= 1 else 1 if crops <= 3 else 2
    previous = int(np.argmax(state[60:64]))
    if state[60 + previous] <= 0.5:
        raise RuntimeError("D156 state lacks previous-kind one-hot")
    return {
        "phase": phase,
        "workers": workers,
        "crop_bucket": crop_bucket,
        "previous_kind": previous,
    }


def keys(state: np.ndarray, action: np.ndarray) -> dict[str, tuple]:
    decoded = decode_action(action)
    regime = state_regime(state)
    owner = decoded["job_owner"]
    phase = (*owner, regime["phase"])
    return {
        "jobs": decoded["jobs"],
        "job_owner": owner,
        "job_owner_phase": phase,
        "job_owner_phase_rank": (
            *phase,
            decoded["rank_one"],
            decoded["rank_two"],
        ),
        "job_owner_regime": (
            *phase,
            regime["workers"],
            regime["crop_bucket"],
            regime["previous_kind"],
        ),
    }


def add_stat(stats: dict, key: tuple, value: float) -> None:
    row = stats[key]
    row[0] += 1.0
    row[1] += value
    row[2] += value * value


def fit_stats(dataset: dict) -> dict[str, dict[tuple, list[float]]]:
    stats = {
        name: defaultdict(lambda: [0.0, 0.0, 0.0])
        for name in (
            "jobs",
            "job_owner",
            "job_owner_phase",
            "job_owner_phase_rank",
            "job_owner_regime",
        )
    }
    for group, state in enumerate(dataset["state_features"]):
        count = int(dataset["valid"][group].sum())
        for action_index in range(1, count):
            action = dataset["action_features"][group, action_index]
            value = float(dataset["target_values"][group, action_index])
            action_keys = keys(state, action)
            for name, key in action_keys.items():
                add_stat(stats[name], key, value)
    return {name: dict(rows) for name, rows in stats.items()}


def posterior(stat: list[float] | None, prior: float) -> tuple[float, float, int]:
    count, total, square = stat if stat is not None else (0.0, 0.0, 0.0)
    mass = count + SHRINKAGE
    mean = (total + SHRINKAGE * prior) / mass
    second = (square + SHRINKAGE * prior * prior) / mass
    standard_deviation = math.sqrt(max(0.0, second - mean * mean))
    return mean, standard_deviation, int(count)


def score_action(variant: str, stats: dict, action_keys: dict) -> tuple[float, int]:
    jobs, _, jobs_count = posterior(stats["jobs"].get(action_keys["jobs"]), 0.0)
    owner, _, owner_count = posterior(
        stats["job_owner"].get(action_keys["job_owner"]), 0.0
    )
    phase, phase_std, phase_count = posterior(
        stats["job_owner_phase"].get(action_keys["job_owner_phase"]), owner
    )
    rank, _, rank_count = posterior(
        stats["job_owner_phase_rank"].get(
            action_keys["job_owner_phase_rank"]
        ),
        phase,
    )
    regime, regime_std, regime_count = posterior(
        stats["job_owner_regime"].get(action_keys["job_owner_regime"]), phase
    )
    if variant == "jobs":
        return jobs, jobs_count
    if variant == "job_owner":
        return owner, owner_count
    if variant == "job_owner_phase":
        return phase, phase_count
    if variant == "job_owner_phase_rank":
        return rank, rank_count
    if variant == "job_owner_regime":
        return regime, regime_count
    if variant == "job_owner_phase_lcb":
        return phase - LCB_STANDARD_DEVIATIONS * phase_std, phase_count
    if variant == "job_owner_regime_lcb":
        return regime - LCB_STANDARD_DEVIATIONS * regime_std, regime_count
    raise ValueError(f"unknown D156 variant: {variant}")


def evaluate_fold(training: dict, held: dict, held_fold: int) -> dict[str, dict]:
    stats = fit_stats(training)
    valid = np.asarray(held["valid"], dtype=np.bool_)
    width = valid.shape[1]
    scores = {
        variant: np.full(valid.shape, -np.inf, dtype=np.float64)
        for variant in VARIANTS
    }
    support = {
        variant: {
            "held_noncontrol_actions": 0,
            "held_supported_actions": 0,
            "selected_noncontrol": 0,
            "selected_supported": 0,
            "selected_support_sum": 0,
        }
        for variant in VARIANTS
    }
    for variant in VARIANTS:
        scores[variant][:, 0] = 0.0
    support_counts = {
        variant: np.zeros(valid.shape, dtype=np.int64) for variant in VARIANTS
    }
    for group, state in enumerate(held["state_features"]):
        count = int(valid[group].sum())
        for action_index in range(1, count):
            action_keys = keys(state, held["action_features"][group, action_index])
            for variant in VARIANTS:
                value, count_support = score_action(variant, stats, action_keys)
                scores[variant][group, action_index] = value
                support_counts[variant][group, action_index] = count_support
                support[variant]["held_noncontrol_actions"] += 1
                support[variant]["held_supported_actions"] += int(count_support > 0)
    result = {}
    for variant in VARIANTS:
        selected = scores[variant].argmax(axis=1)
        roots = np.arange(len(selected))
        selected_support = support_counts[variant][roots, selected]
        selected_noncontrol = selected != 0
        support[variant]["selected_noncontrol"] = int(selected_noncontrol.sum())
        support[variant]["selected_supported"] = int(
            ((selected_support > 0) & selected_noncontrol).sum()
        )
        support[variant]["selected_support_sum"] = int(
            selected_support[selected_noncontrol].sum()
        )
        digest = hashlib.sha256()
        digest.update(np.asarray(scores[variant], dtype="<f8").tobytes(order="C"))
        digest.update(np.asarray(selected, dtype="<i8").tobytes(order="C"))
        counts = d153b.counts_from_selected(held, scores[variant], selected)
        result[variant] = {
            "variant": variant,
            "held_fold": held_fold,
            "class_cardinality": {name: len(rows) for name, rows in stats.items()},
            "support": support[variant],
            "score_and_selection_sha256": digest.hexdigest(),
            "counts": counts,
            "metrics": d153a.metric_view(counts),
        }
    return result


def run_crossfit(dataset: dict) -> dict:
    folds = np.asarray(dataset["folds"])
    fold_results = []
    for held_fold in range(d153a.FOLDS):
        training = d153_trainer.subset(dataset, np.flatnonzero(folds != held_fold))
        held = d153_trainer.subset(dataset, np.flatnonzero(folds == held_fold))
        fold_results.append(evaluate_fold(training, held, held_fold))
    candidates = []
    for variant in VARIANTS:
        rows = [fold[variant] for fold in fold_results]
        counts = d153a.merge_counts([row["counts"] for row in rows])
        metrics = d153a.metric_view(counts)
        gates = d153a.held_gates(metrics, rows)
        support = {
            key: sum(row["support"][key] for row in rows)
            for key in rows[0]["support"]
        }
        candidates.append(
            {
                "variant": variant,
                "folds": rows,
                "counts": counts,
                "metrics": metrics,
                "support": support,
                "gates": gates,
                "eligible": all(gates.values()),
            }
        )
    return {"candidates": candidates}


def candidate_key(candidate: dict) -> tuple:
    metrics = candidate["metrics"]
    return (
        min(fold["metrics"]["mean_selected_value"] for fold in candidate["folds"]),
        metrics["worst_family_mean_value"],
        metrics["mean_selected_value"],
        metrics["oracle_value_capture"],
        metrics["within_ten_rate"],
        -metrics["harmful_negative_rate"],
        -VARIANTS.index(candidate["variant"]),
    )


def main() -> int:
    lock = verify_lock()
    parent = json.loads(d155a.OUTPUT.read_text())
    if parent["decision"] != "close_static_first_action_memory_value_models":
        raise RuntimeError("D155a did not authorize D156")
    dataset, structural = d153a.load_dataset()
    first = run_crossfit(dataset)
    second = run_crossfit(dataset)
    exact_repeat = first == second
    if not exact_repeat:
        raise RuntimeError("D156 deterministic in-memory repeat drift")
    eligible = [row for row in first["candidates"] if row["eligible"]]
    selected = max(eligible, key=candidate_key) if eligible else None
    result = {
        "schema": "troll-farm-d156a-hierarchical-semantic-value-policy-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d155a": {
            "path": str(d155a.OUTPUT.relative_to(ROOT)),
            "sha256": d153a.sha256(d155a.OUTPUT),
            "decision": parent["decision"],
        },
        "dataset": structural,
        "shrinkage_pseudo_observations": SHRINKAGE,
        "lcb_standard_deviations": LCB_STANDARD_DEVIATIONS,
        "exact_in_memory_repeat": exact_repeat,
        "candidates": first["candidates"],
        "eligible_variants": len(eligible),
        "selected": selected,
        "pass": selected is not None,
        "decision": (
            "open_fresh_nonreserved_semantic_policy_confirmation"
            if selected is not None
            else "close_static_empirical_semantic_class_value"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
