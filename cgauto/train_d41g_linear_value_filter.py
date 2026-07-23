#!/usr/bin/env python3
"""Extract exact D41 rate features and run frozen grouped linear value discovery."""

from __future__ import annotations

import collections
import csv
import json
import math
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.rl_macro_env import BRANCHES, MacroVecEnv, OPPONENTS, TASKS_PER_MAP
from cgauto.train_d41c_residual_ppo import ExactPriorResidualActorCritic


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41g-linear-continuation-value-filter-protocol-2026-07-21.md"
CHECKPOINT = ANALYSIS / "d41c-residual-ppo-seed411-final.pt"
D41F_ROWS = ANALYSIS / "d41f-rate-boundary-results-9772000-9772031.tsv"
D41D_ROWS = ANALYSIS / "d41d-one-deviation-results-9760000-9760031.tsv"
TRAIN_FEATURES = ANALYSIS / "d41g-d41f-linear-features.npz"
EXTERNAL_FEATURES = ANALYSIS / "d41g-d41d-external-features.npz"
WEIGHTS = ANALYSIS / "d41g-linear-value-filter-weights.npz"
OUTPUT = ANALYSIS / "d41g-linear-value-filter-result.json"
EXPECTED_D41F_SHA256 = "3bbc1c62a5383c3d8667c40ba7173026ded60721ec41d0db72fb6d021fe09d26"
EXPECTED_D41D_SHA256 = "be1181bbcdb4e5188f19f80377e111803d4a261ad90a4c469928869516559f53"
EXPECTED_CHECKPOINT_SHA256 = "1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a"
FEATURES = 100
FOLDS = 8
ALPHAS = (0.1, 1.0, 10.0, 100.0)
TARGETS = ("clip100", "clip50", "positive")
SHARES = (0.40, 0.50, 0.60, 0.70, 0.80)


def read_rows(path: Path, *, external: bool) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    output = []
    for row in rows:
        converted = {
            **row,
            "sample_id": int(row["sample_id"]),
            "map_seed": int(row["map_seed"]),
            "task_index": int(row["task_index"]),
            "seat": int(row["seat"]),
            "opponent_index": int(row["opponent_index"]),
            "decision_ordinal": int(row["decision_ordinal"]),
            "turn": int(row["turn"]),
            "branch_index": int(row["branch_index"]),
            "candidate_count": int(row["candidate_count"]),
            "teacher_action": int(row["teacher_action"]),
            "alternative_action": int(row["alternative_action"]),
            "residual_gap": float(row["residual_gap"]),
            "margin_delta": int(row["margin_delta"]),
        }
        if external and not (
            converted["branch"] == "rate"
            and converted["phase"] in {"early", "late"}
            and 0.200 <= converted["residual_gap"] <= 0.340
        ):
            continue
        output.append(converted)
    output.sort(key=lambda row: row["sample_id"])
    return output


def feature_vector(
    rank_zero: np.ndarray,
    rank_one: np.ndarray,
    residual_gap: float,
    candidate_count: int,
) -> np.ndarray:
    vector = np.concatenate(
        (
            rank_zero[:17],
            rank_zero[17:44],
            rank_one[17:44],
            rank_one[17:44] - rank_zero[17:44],
            np.asarray([residual_gap, candidate_count / 768.0], dtype=np.float32),
        )
    ).astype(np.float32, copy=False)
    if vector.shape != (FEATURES,) or not np.isfinite(vector).all():
        raise RuntimeError("invalid D41g feature vector")
    return vector


@torch.inference_mode()
def extract_exact_features(
    rows: list[dict], seed_base: int, model: ExactPriorResidualActorCritic
) -> tuple[np.ndarray, dict]:
    targets = {(row["task_index"], row["decision_ordinal"]): row for row in rows}
    if len(targets) != len(rows):
        raise ValueError("duplicate D41g state identity")
    target_tasks = 32 * TASKS_PER_MAP
    completed = set()
    ordinals: collections.Counter[int] = collections.Counter()
    extracted: dict[tuple[int, int], np.ndarray] = {}
    validation_failures = 0
    model.eval()
    with MacroVecEnv(64, seed_base) as env:
        while len(completed) < target_tasks:
            active = np.flatnonzero(env.task_indices < target_tasks)
            maximum = int(env.counts.max())
            features = torch.from_numpy(env.features[:, :maximum])
            residual = model.actor_output(F.relu(model.actor_hidden(features))).squeeze(-1).numpy()
            for slot in active:
                task_index = int(env.task_indices[slot])
                ordinal = ordinals[task_index]
                ordinals[task_index] += 1
                expected = targets.get((task_index, ordinal))
                if expected is None:
                    continue
                count = int(env.counts[slot])
                ranks = env.prior_ranks[slot, :count]
                rank_zero_index = int(np.flatnonzero(ranks == 0)[0])
                rank_one_index = int(np.flatnonzero(ranks == 1)[0])
                turn = int(round(float(env.features[slot, 0, 1]) * 300))
                gap = float(residual[slot, rank_one_index] - residual[slot, rank_zero_index])
                actual = (
                    seed_base + task_index // TASKS_PER_MAP,
                    (task_index % TASKS_PER_MAP) // len(OPPONENTS),
                    task_index % len(OPPONENTS),
                    turn,
                    int(env.branches[slot]),
                    count,
                    int(env.actions[slot, rank_zero_index]),
                    int(env.actions[slot, rank_one_index]),
                )
                wanted = (
                    expected["map_seed"],
                    expected["seat"],
                    expected["opponent_index"],
                    expected["turn"],
                    expected["branch_index"],
                    expected["candidate_count"],
                    expected["teacher_action"],
                    expected["alternative_action"],
                )
                if actual != wanted or abs(gap - expected["residual_gap"]) > 1e-6:
                    validation_failures += 1
                    continue
                extracted[(task_index, ordinal)] = feature_vector(
                    env.features[slot, rank_zero_index],
                    env.features[slot, rank_one_index],
                    gap,
                    count,
                )
            _, _, _, _, info = env.step(env.teacher_actions())
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed.add(terminal["task_index"])
    missing = [key for key in targets if key not in extracted]
    if validation_failures or missing:
        raise RuntimeError(
            f"D41g exact extraction failed: validation={validation_failures}, missing={len(missing)}"
        )
    matrix = np.stack(
        [extracted[(row["task_index"], row["decision_ordinal"])] for row in rows]
    )
    return matrix, {
        "rows": len(rows),
        "features": matrix.shape[1],
        "validation_failures": validation_failures,
        "missing": len(missing),
        "finite": bool(np.isfinite(matrix).all()),
    }


def save_dataset(path: Path, features: np.ndarray, rows: list[dict], seed_base: int) -> None:
    np.savez(
        path,
        features=features,
        margin_delta=np.asarray([row["margin_delta"] for row in rows], dtype=np.float32),
        map_seed=np.asarray([row["map_seed"] for row in rows], dtype=np.int64),
        fold=np.asarray([(row["map_seed"] - seed_base) % FOLDS for row in rows], dtype=np.int8),
        opponent=np.asarray([row["opponent_index"] for row in rows], dtype=np.int8),
        phase=np.asarray([0 if row["phase"] == "early" else 1 for row in rows], dtype=np.int8),
        residual_gap=np.asarray([row["residual_gap"] for row in rows], dtype=np.float32),
        sample_id=np.asarray([row["sample_id"] for row in rows], dtype=np.int32),
    )


def target_values(name: str, margin: np.ndarray) -> np.ndarray:
    if name == "clip100":
        return np.clip(margin, -100, 100)
    if name == "clip50":
        return np.clip(margin, -50, 50)
    if name == "positive":
        return (margin > 0).astype(np.float64)
    raise ValueError(name)


def fit_ridge(features: np.ndarray, target: np.ndarray, alpha: float) -> dict:
    mean = features.mean(axis=0, dtype=np.float64)
    scale = features.std(axis=0, dtype=np.float64)
    scale[scale < 1e-8] = 1.0
    standardized = (features - mean) / scale
    design = np.column_stack((np.ones(len(features)), standardized))
    penalty = np.eye(design.shape[1], dtype=np.float64) * alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ target)
    raw_weights = beta[1:] / scale
    raw_bias = beta[0] - float(np.dot(mean, raw_weights))
    standardized_prediction = design @ beta
    raw_prediction = features @ raw_weights + raw_bias
    return {
        "mean": mean,
        "scale": scale,
        "beta": beta,
        "raw_weights": raw_weights,
        "raw_bias": raw_bias,
        "prediction": raw_prediction,
        "maximum_raw_parity_error": float(
            np.max(np.abs(standardized_prediction - raw_prediction))
        ),
    }


def threshold_for_share(scores: np.ndarray, share: float) -> float:
    count = max(1, int(math.ceil(len(scores) * share)))
    return float(np.sort(scores)[-count])


def delta_stats(values: np.ndarray) -> dict:
    values = np.asarray(values, dtype=np.float64)
    if not len(values):
        return {"samples": 0}
    standard_error = float(values.std(ddof=1) / math.sqrt(len(values))) if len(values) > 1 else 0.0
    mean = float(values.mean())
    return {
        "samples": len(values),
        "mean": mean,
        "standard_error": standard_error,
        "normal_95_low": mean - 1.96 * standard_error,
        "normal_95_high": mean + 1.96 * standard_error,
        "minimum": float(values.min()),
        "median": float(np.median(values)),
        "maximum": float(values.max()),
        "positive_rate": float(np.mean(values > 0)),
        "tie_rate": float(np.mean(values == 0)),
        "negative_rate": float(np.mean(values < 0)),
    }


def grouped_means(values: np.ndarray, groups: np.ndarray, selected: np.ndarray) -> dict:
    return {
        str(group): float(values[selected & (groups == group)].mean())
        for group in sorted(set(groups.tolist()))
        if np.any(selected & (groups == group))
    }


def discovery_metrics(data: dict, scores: np.ndarray, threshold: float) -> dict:
    eligible = (data["residual_gap"] >= 0.200) & (data["residual_gap"] <= 0.340)
    selected = eligible & (scores >= threshold)
    margin = data["margin_delta"].astype(np.float64)
    overall = delta_stats(margin[selected])
    below = int(np.count_nonzero(selected & (data["residual_gap"] < 0.280)))
    phase_means = grouped_means(margin, data["phase"], selected)
    fold_means = grouped_means(margin, data["fold"], selected)
    opponent_means = grouped_means(margin, data["opponent"], selected)
    gates = {
        "at_least_240_rows": overall["samples"] >= 240,
        "at_least_64_below_0280": below >= 64,
        "mean_at_least_12": overall["mean"] >= 12,
        "normal_95_low_above_8": overall["normal_95_low"] > 8,
        "positive_rate_at_least_65pct": overall["positive_rate"] >= 0.65,
        "negative_rate_at_most_27pct": overall["negative_rate"] <= 0.27,
        "phase_means": set(phase_means) == {"0", "1"}
        and phase_means["0"] >= 14
        and phase_means["1"] >= 5,
        "all_eight_fold_means_positive": len(fold_means) == 8
        and min(fold_means.values()) > 0,
        "opponent_breadth": len(opponent_means) == 8
        and sum(value > 0 for value in opponent_means.values()) >= 6
        and min(opponent_means.values()) >= -10,
    }
    return {
        "threshold": threshold,
        "eligible_rows": int(eligible.sum()),
        "selected_share": float(selected.sum() / eligible.sum()),
        "below_0280": below,
        "margin": overall,
        "phase_means": phase_means,
        "fold_means": fold_means,
        "opponent_means": opponent_means,
        "gates": gates,
        "pass": all(gates.values()),
    }


def external_metrics(data: dict, scores: np.ndarray, threshold: float) -> dict:
    selected = scores >= threshold
    margin = data["margin_delta"].astype(np.float64)
    overall = delta_stats(margin[selected])
    below = int(np.count_nonzero(selected & (data["residual_gap"] < 0.280)))
    phase_means = grouped_means(margin, data["phase"], selected)
    opponent_means = grouped_means(margin, data["opponent"], selected)
    gates = {
        "at_least_64_rows": overall["samples"] >= 64,
        "at_least_24_below_0280": below >= 24,
        "mean_at_least_8": overall["mean"] >= 8,
        "normal_95_low_above_zero": overall["normal_95_low"] > 0,
        "positive_rate_at_least_60pct": overall["positive_rate"] >= 0.60,
        "both_phase_means_positive": set(phase_means) == {"0", "1"}
        and min(phase_means.values()) > 0,
        "opponent_breadth": len(opponent_means) >= 5
        and sum(value > 0 for value in opponent_means.values()) >= 5
        and min(opponent_means.values()) >= -15,
    }
    return {
        "selected_rows": int(selected.sum()),
        "below_0280": below,
        "margin": overall,
        "phase_means": phase_means,
        "opponent_means": opponent_means,
        "gates": gates,
        "pass": all(gates.values()),
    }


def load_npz(path: Path) -> dict[str, np.ndarray]:
    with np.load(path) as source:
        return {name: source[name] for name in source.files}


def main() -> None:
    for required in (PROTOCOL, CHECKPOINT, D41F_ROWS, D41D_ROWS):
        if not required.exists():
            raise SystemExit(f"missing D41g prerequisite: {required}")
    if sha256(CHECKPOINT) != EXPECTED_CHECKPOINT_SHA256:
        raise SystemExit("D41g checkpoint hash mismatch")
    if sha256(D41F_ROWS) != EXPECTED_D41F_SHA256 or sha256(D41D_ROWS) != EXPECTED_D41D_SHA256:
        raise SystemExit("D41g label-bank hash mismatch")
    if any(path.exists() for path in (TRAIN_FEATURES, EXTERNAL_FEATURES, WEIGHTS, OUTPUT)):
        raise SystemExit("refusing to overwrite D41g artifacts")

    saved = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = ExactPriorResidualActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    training_rows = read_rows(D41F_ROWS, external=False)
    external_rows = read_rows(D41D_ROWS, external=True)
    training_features, training_audit = extract_exact_features(training_rows, 9_772_000, model)
    external_features, external_audit = extract_exact_features(external_rows, 9_760_000, model)
    save_dataset(TRAIN_FEATURES, training_features, training_rows, 9_772_000)
    save_dataset(EXTERNAL_FEATURES, external_features, external_rows, 9_760_000)
    training = load_npz(TRAIN_FEATURES)
    external = load_npz(EXTERNAL_FEATURES)

    candidates = []
    for target_index, target_name in enumerate(TARGETS):
        target = target_values(target_name, training["margin_delta"].astype(np.float64))
        for alpha in ALPHAS:
            oof = np.empty(len(target), dtype=np.float64)
            fold_parity = []
            for fold in range(FOLDS):
                train = training["fold"] != fold
                held = ~train
                fitted = fit_ridge(training["features"][train].astype(np.float64), target[train], alpha)
                oof[held] = (
                    training["features"][held].astype(np.float64) @ fitted["raw_weights"]
                    + fitted["raw_bias"]
                )
                fold_parity.append(fitted["maximum_raw_parity_error"])
            eligible_scores = oof[
                (training["residual_gap"] >= 0.200)
                & (training["residual_gap"] <= 0.340)
            ]
            for share in SHARES:
                threshold = threshold_for_share(eligible_scores, share)
                metrics = discovery_metrics(training, oof, threshold)
                candidates.append(
                    {
                        "target": target_name,
                        "target_index": target_index,
                        "alpha": alpha,
                        "share_target": share,
                        "maximum_fold_raw_parity_error": max(fold_parity),
                        **metrics,
                    }
                )

    passing = [candidate for candidate in candidates if candidate["pass"]]
    selected = None
    external_report = None
    final_parity = None
    if passing:
        selected = max(
            passing,
            key=lambda item: (
                item["margin"]["normal_95_low"],
                item["margin"]["samples"],
                -item["alpha"],
                -item["target_index"],
                -item["share_target"],
            ),
        )
        target = target_values(selected["target"], training["margin_delta"].astype(np.float64))
        fitted = fit_ridge(
            training["features"].astype(np.float64), target, selected["alpha"]
        )
        full_scores = fitted["prediction"]
        eligible = (training["residual_gap"] >= 0.200) & (training["residual_gap"] <= 0.340)
        production_threshold = threshold_for_share(
            full_scores[eligible], selected["selected_share"]
        )
        external_scores = (
            external["features"].astype(np.float64) @ fitted["raw_weights"]
            + fitted["raw_bias"]
        )
        external_report = external_metrics(external, external_scores, production_threshold)
        final_parity = fitted["maximum_raw_parity_error"]
        np.savez(
            WEIGHTS,
            weights=fitted["raw_weights"].astype(np.float32),
            bias=np.asarray(fitted["raw_bias"], dtype=np.float32),
            threshold=np.asarray(production_threshold, dtype=np.float32),
            residual_gap_min=np.asarray(0.200, dtype=np.float32),
            residual_gap_max=np.asarray(0.340, dtype=np.float32),
        )
        selected = {
            **selected,
            "production_threshold": production_threshold,
            "full_training_metrics": discovery_metrics(
                training, full_scores, production_threshold
            ),
        }

    qualifies = bool(
        selected is not None
        and external_report is not None
        and external_report["pass"]
        and final_parity is not None
        and final_parity <= 1e-5
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "d41f_rows_sha256": sha256(D41F_ROWS),
            "d41d_rows_sha256": sha256(D41D_ROWS),
            "checkpoint_sha256": sha256(CHECKPOINT),
        },
        "feature_definition": {
            "dimensions": FEATURES,
            "opponent_identity_included": False,
            "training_audit": training_audit,
            "external_audit": external_audit,
            "training_features": str(TRAIN_FEATURES),
            "training_features_sha256": sha256(TRAIN_FEATURES),
            "external_features": str(EXTERNAL_FEATURES),
            "external_features_sha256": sha256(EXTERNAL_FEATURES),
        },
        "matrix": {
            "targets": TARGETS,
            "alphas": ALPHAS,
            "shares": SHARES,
            "candidates": candidates,
            "passing_candidates": len(passing),
        },
        "selected": selected,
        "external_replication": external_report,
        "final_raw_prediction_parity_error": final_parity,
        "weights": str(WEIGHTS) if WEIGHTS.exists() else None,
        "weights_sha256": sha256(WEIGHTS) if WEIGHTS.exists() else None,
        "scalar_parameters": 101 if WEIGHTS.exists() else 0,
        "pass": qualifies,
        "scope": "consumed-label D41g discovery only; no fresh outcome or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "pass": qualifies,
                "passing_candidates": len(passing),
                "selected": selected,
                "external_replication": external_report,
                "feature_definition": report["feature_definition"],
                "weights_sha256": report["weights_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
