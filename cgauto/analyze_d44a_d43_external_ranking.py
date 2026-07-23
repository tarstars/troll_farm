#!/usr/bin/env python3
"""Audit frozen D43 actor ranking on the consumed exact D42 continuation bank."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
import torch

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.train_d43_binary_preflight import BinaryActorCritic


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d44a-d43-external-ranking-audit-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d42-context-manifest-9773000-9773063.tsv"
OUTCOMES = ANALYSIS / "d42-context-results-9773000-9773063.tsv"
FEATURE_ROWS = ANALYSIS / "d44a-d43-external-features.tsv"
CHECKPOINT = ANALYSIS / "d43-binary-closed-loop-preflight-final.pt"
D43_RESULT = ANALYSIS / "d43-binary-closed-loop-preflight-result.json"
OUTPUT = ANALYSIS / "d44a-d43-external-ranking-audit-result.json"

EXPECTED_PROTOCOL_SHA256 = "f95f6f4fc01c3d74deb0b4fe74e085d233501b935af843dbc8e545f90b2b325c"
EXPECTED_MANIFEST_SHA256 = "6d7a09bcba26b3cc9a65e583d3b48699704a0dcab545a1d631404b0a13ffba3f"
EXPECTED_OUTCOMES_SHA256 = "fd7525314a272b6ce3b9b22788f46af08e7841ff8452b6eea4b17352f951a7a4"
EXPECTED_CHECKPOINT_SHA256 = "ae25f7a889ffe74a203bccefdc1140bd5d436091d63f0342612a5ec02550b469"
EXPECTED_D43_RESULT_SHA256 = "12bac7491b67e118d9d90baf3895b8a1165b1f7b8335572956039608e352661e"
ROWS = 1_087
FEATURES = 154
TOP_HALF = 544
TOP_QUARTILE = 272
BOOTSTRAPS = 4_096
BOOTSTRAP_SEED = 4_401
SEED_BASE = 9_773_000


def average_tie_ranks(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
    order = np.argsort(values, kind="stable")
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
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if len(left) < 2 or left.std() == 0 or right.std() == 0:
        return 0.0
    return float(np.corrcoef(left, right)[0, 1])


def spearman(left: np.ndarray, right: np.ndarray) -> float:
    return correlation(average_tie_ranks(left), average_tie_ranks(right))


def top_mask(scores: np.ndarray, sample_ids: np.ndarray, count: int) -> np.ndarray:
    if not 0 < count < len(scores):
        raise ValueError("invalid top-mask count")
    order = np.lexsort((sample_ids, scores))
    selected = np.zeros(len(scores), dtype=bool)
    selected[order[-count:]] = True
    return selected


def outcome_stats(values: np.ndarray) -> dict:
    values = np.asarray(values, dtype=np.float64)
    if not len(values):
        raise ValueError("empty outcome group")
    standard_error = float(values.std(ddof=1) / math.sqrt(len(values))) if len(values) > 1 else 0.0
    return {
        "rows": int(len(values)),
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "normal_95_low": float(values.mean() - 1.96 * standard_error),
        "positive_rate": float(np.mean(values > 0)),
        "tie_rate": float(np.mean(values == 0)),
        "negative_rate": float(np.mean(values < 0)),
    }


def grouped_means(values: np.ndarray, groups: np.ndarray, selected: np.ndarray) -> dict[str, float]:
    return {
        str(group): float(values[selected & (groups == group)].mean())
        for group in sorted(set(groups.tolist()))
        if np.any(selected & (groups == group))
    }


def clustered_normal(values: np.ndarray, maps: np.ndarray, selected: np.ndarray) -> dict:
    means = np.asarray(
        [values[selected & (maps == seed)].mean() for seed in sorted(set(maps[selected].tolist()))],
        dtype=np.float64,
    )
    standard_error = float(means.std(ddof=1) / math.sqrt(len(means))) if len(means) > 1 else 0.0
    return {
        "maps": int(len(means)),
        "mean_of_map_means": float(means.mean()),
        "normal_95_low": float(means.mean() - 1.96 * standard_error),
        "normal_95_high": float(means.mean() + 1.96 * standard_error),
    }


def clustered_contrast(
    values: np.ndarray, maps: np.ndarray, high: np.ndarray, low: np.ndarray
) -> dict:
    contrasts = []
    for seed in sorted(set(maps.tolist())):
        high_rows = high & (maps == seed)
        low_rows = low & (maps == seed)
        if np.any(high_rows) and np.any(low_rows):
            contrasts.append(values[high_rows].mean() - values[low_rows].mean())
    contrasts = np.asarray(contrasts, dtype=np.float64)
    standard_error = (
        float(contrasts.std(ddof=1) / math.sqrt(len(contrasts))) if len(contrasts) > 1 else 0.0
    )
    return {
        "maps": int(len(contrasts)),
        "mean": float(contrasts.mean()),
        "normal_95_low": float(contrasts.mean() - 1.96 * standard_error),
        "normal_95_high": float(contrasts.mean() + 1.96 * standard_error),
    }


def bootstrap_spearman(
    scores: np.ndarray, values: np.ndarray, maps: np.ndarray
) -> dict:
    unique_maps = np.asarray(sorted(set(maps.tolist())), dtype=np.int64)
    indexes = {seed: np.flatnonzero(maps == seed) for seed in unique_maps}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    samples = np.empty(BOOTSTRAPS, dtype=np.float64)
    for iteration in range(BOOTSTRAPS):
        chosen = rng.choice(unique_maps, size=len(unique_maps), replace=True)
        rows = np.concatenate([indexes[int(seed)] for seed in chosen])
        samples[iteration] = spearman(scores[rows], values[rows])
    return {
        "replicates": BOOTSTRAPS,
        "seed": BOOTSTRAP_SEED,
        "mean": float(samples.mean()),
        "low_2_5pct": float(np.quantile(samples, 0.025)),
        "high_97_5pct": float(np.quantile(samples, 0.975)),
    }


def residualize(values: np.ndarray, groups: np.ndarray) -> np.ndarray:
    output = np.asarray(values, dtype=np.float64).copy()
    for group in sorted(set(groups.tolist())):
        selected = groups == group
        output[selected] -= output[selected].mean()
    return output


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    return rows, fields


def load_data() -> dict[str, np.ndarray]:
    manifest, manifest_fields = read_table(MANIFEST)
    outcomes, _ = read_table(OUTCOMES)
    exported, exported_fields = read_table(FEATURE_ROWS)
    feature_names = [f"feature_{index:03}" for index in range(FEATURES)]
    if exported_fields != [
        "sample_id",
        "map_seed",
        "seat",
        "opponent_index",
        "decision_ordinal",
        *feature_names,
    ]:
        raise RuntimeError("D44a exported feature schema mismatch")
    if not (len(manifest) == len(outcomes) == len(exported) == ROWS):
        raise RuntimeError("D44a row-count mismatch")
    features = np.empty((ROWS, FEATURES), dtype=np.float32)
    identity = ("sample_id", "map_seed", "seat", "opponent_index", "decision_ordinal")
    for index, (expected, outcome, row) in enumerate(zip(manifest, outcomes, exported)):
        if int(expected["sample_id"]) != index:
            raise RuntimeError("D44a manifest sample order mismatch")
        for name in manifest_fields:
            if name == "residual_gap":
                if abs(float(expected[name]) - float(outcome[name])) > 1e-6:
                    raise RuntimeError("D44a outcome residual-gap drift")
            elif expected[name] != outcome[name]:
                raise RuntimeError(f"D44a outcome identity drift: {name}")
        if any(expected[name] != row[name] for name in identity):
            raise RuntimeError("D44a replay identity drift")
        features[index] = [float(row[name]) for name in feature_names]
    if not np.isfinite(features).all():
        raise RuntimeError("D44a nonfinite features")
    return {
        "features": features,
        "sample_id": np.arange(ROWS, dtype=np.int32),
        "map_seed": np.asarray([int(row["map_seed"]) for row in manifest], dtype=np.int64),
        "fold": np.asarray(
            [(int(row["map_seed"]) - SEED_BASE) % 8 for row in manifest], dtype=np.int8
        ),
        "opponent": np.asarray(
            [int(row["opponent_index"]) for row in manifest], dtype=np.int8
        ),
        "phase": np.asarray([row["phase"] for row in manifest]),
        "cohort": np.asarray([f'{row["phase"]}|{row["cohort"]}' for row in manifest]),
        "margin_delta": np.asarray(
            [int(row["margin_delta"]) for row in outcomes], dtype=np.float64
        ),
        "residual_gap": np.asarray(
            [float(row["residual_gap"]) for row in manifest], dtype=np.float64
        ),
    }


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (MANIFEST, EXPECTED_MANIFEST_SHA256),
        (OUTCOMES, EXPECTED_OUTCOMES_SHA256),
        (CHECKPOINT, EXPECTED_CHECKPOINT_SHA256),
        (D43_RESULT, EXPECTED_D43_RESULT_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D44a prerequisite missing or changed: {path}")
    if not FEATURE_ROWS.exists():
        raise SystemExit(f"missing D44a replay export: {FEATURE_ROWS}")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D44a result")

    data = load_data()
    saved = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = BinaryActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    model.eval()
    with torch.inference_mode():
        logits = model.actor_logits(torch.from_numpy(data["features"])).numpy()
        probabilities = torch.sigmoid(torch.from_numpy(logits)).numpy().astype(np.float64)
    values = data["margin_delta"]
    top_half = top_mask(probabilities, data["sample_id"], TOP_HALF)
    bottom_half = ~top_half
    top_quartile = top_mask(probabilities, data["sample_id"], TOP_QUARTILE)

    global_spearman = spearman(probabilities, values)
    bootstrap = bootstrap_spearman(probabilities, values, data["map_seed"])
    row_contrast = float(values[top_half].mean() - values[bottom_half].mean())
    cluster_contrast = clustered_contrast(
        values, data["map_seed"], top_half, bottom_half
    )
    fold_contrasts = {
        str(fold): float(
            values[top_half & (data["fold"] == fold)].mean()
            - values[bottom_half & (data["fold"] == fold)].mean()
        )
        for fold in range(8)
    }

    residual_scores = residualize(probabilities, data["cohort"])
    residual_values = residualize(values, data["cohort"])
    cohort_contrasts = {}
    for cohort in sorted(set(data["cohort"].tolist())):
        selected = data["cohort"] == cohort
        local_top = top_mask(
            probabilities[selected], data["sample_id"][selected], (int(selected.sum()) + 1) // 2
        )
        local_values = values[selected]
        cohort_contrasts[cohort] = float(
            local_values[local_top].mean() - local_values[~local_top].mean()
        )

    top_quartile_stats = outcome_stats(values[top_quartile])
    top_quartile_cluster = clustered_normal(
        values, data["map_seed"], top_quartile
    )
    top_quartile_folds = grouped_means(values, data["fold"], top_quartile)
    top_quartile_opponents = grouped_means(values, data["opponent"], top_quartile)
    top_quartile_phases = grouped_means(values, data["phase"], top_quartile)
    top_quartile_cohorts = grouped_means(values, data["cohort"], top_quartile)
    residual_spearman = spearman(residual_scores, residual_values)

    gates = {
        "exact_1087_row_replay_and_schema": True,
        "external_probability_std_at_least_00005": float(probabilities.std()) >= 0.0005,
        "global_spearman_at_least_008": global_spearman >= 0.08,
        "bootstrap_spearman_low_above_zero": bootstrap["low_2_5pct"] > 0,
        "top_half_contrast_at_least_4": row_contrast >= 4,
        "top_half_cluster_low_above_zero": cluster_contrast["normal_95_low"] > 0,
        "at_least_six_positive_fold_contrasts": sum(
            value > 0 for value in fold_contrasts.values()
        )
        >= 6,
        "residualized_spearman_at_least_005": residual_spearman >= 0.05,
        "at_least_seven_positive_cohort_contrasts": sum(
            value > 0 for value in cohort_contrasts.values()
        )
        >= 7,
        "top_quartile_at_least_250_rows": top_quartile_stats["rows"] >= 250,
        "top_quartile_mean_at_least_10": top_quartile_stats["mean"] >= 10,
        "top_quartile_cluster_low_above_5": top_quartile_cluster["normal_95_low"] > 5,
        "top_quartile_positive_rate_at_least_60pct": top_quartile_stats["positive_rate"] >= 0.60,
        "top_quartile_negative_rate_at_most_30pct": top_quartile_stats["negative_rate"] <= 0.30,
        "all_eight_top_quartile_fold_means_positive": len(top_quartile_folds) == 8
        and min(top_quartile_folds.values()) > 0,
        "top_quartile_opponent_breadth": len(top_quartile_opponents) == 8
        and sum(value > 0 for value in top_quartile_opponents.values()) >= 6
        and min(top_quartile_opponents.values()) >= -10,
        "both_top_quartile_phase_means_positive": len(top_quartile_phases) == 2
        and min(top_quartile_phases.values()) > 0,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "manifest": str(MANIFEST),
            "manifest_sha256": sha256(MANIFEST),
            "outcomes": str(OUTCOMES),
            "outcomes_sha256": sha256(OUTCOMES),
            "feature_rows": str(FEATURE_ROWS),
            "feature_rows_sha256": sha256(FEATURE_ROWS),
            "checkpoint": str(CHECKPOINT),
            "checkpoint_sha256": sha256(CHECKPOINT),
            "d43_result": str(D43_RESULT),
            "d43_result_sha256": sha256(D43_RESULT),
        },
        "audit": {
            "rows": ROWS,
            "features": FEATURES,
            "unique_maps": int(len(set(data["map_seed"].tolist()))),
            "unique_cohorts": int(len(set(data["cohort"].tolist()))),
            "finite": True,
        },
        "score": {
            "mean_probability": float(probabilities.mean()),
            "probability_std": float(probabilities.std()),
            "minimum_probability": float(probabilities.min()),
            "maximum_probability": float(probabilities.max()),
            "deterministic_alternatives": int(np.count_nonzero(probabilities >= 0.5)),
            "pearson_margin": correlation(probabilities, values),
            "spearman_margin": global_spearman,
            "spearman_residual_gap": spearman(probabilities, data["residual_gap"]),
            "cluster_bootstrap_spearman": bootstrap,
        },
        "halves": {
            "top": outcome_stats(values[top_half]),
            "bottom": outcome_stats(values[bottom_half]),
            "row_mean_contrast": row_contrast,
            "map_cluster_contrast": cluster_contrast,
            "fold_contrasts": fold_contrasts,
        },
        "within_phase_gap": {
            "residualized_spearman": residual_spearman,
            "cohort_contrasts": cohort_contrasts,
        },
        "top_quartile": {
            "outcomes": top_quartile_stats,
            "map_cluster": top_quartile_cluster,
            "fold_means": top_quartile_folds,
            "opponent_means": top_quartile_opponents,
            "phase_means": top_quartile_phases,
            "cohort_means": top_quartile_cohorts,
        },
        "gates": gates,
        "pass": all(gates.values()),
        "scope": "consumed-bank architecture diagnostic only; no fresh maps, fit, candidate, or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
