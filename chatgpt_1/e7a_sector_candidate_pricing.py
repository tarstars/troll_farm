#!/usr/bin/env python3
"""Price the already-frozen E7a sector rule from exact recovered E7 deltas.

No fitting, threshold selection, simulation, or source mutation occurs here. The rule and
its 60-root labels were frozen before the 360-row magnitude table was recovered.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SIGN_ROWS = ROOT / "chatgpt_1/e7a-initial-sector-sign-preflight-2026-08-02.csv"
DELTA_ROWS = ROOT / "data/analysis/live-agent-6553250/e7a-root-delta-pricing-input-2026-08-02.csv"
DELTA_SHA256 = "cb2a98e63c245534b743501000b3ef8529cca674c7bb3ea226717e767abd4d6a"
DEFAULT_OUTPUT = ROOT / "chatgpt_1/e7a-sector-candidate-pricing-2026-08-02.json"
OPPONENTS = ("motion", "taskplan", "race", "yield", "ringfix3", "chopharvest")
BOOTSTRAP_SEED = 20260802
BOOTSTRAP_REPS = 100_000


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.mean(values) if values else math.nan


def quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return math.nan
    position = q * (len(sorted_values) - 1)
    lo = math.floor(position)
    hi = math.ceil(position)
    if lo == hi:
        return sorted_values[lo]
    weight = position - lo
    return sorted_values[lo] * (1 - weight) + sorted_values[hi] * weight


def load_sign_rows() -> dict[int, dict[str, Any]]:
    with SIGN_ROWS.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 60:
        raise ValueError(f"expected 60 sign rows, found {len(rows)}")
    result = {int(row["seed"]): row for row in rows}
    if sorted(result) != list(range(60)):
        raise ValueError("sign rows must contain seeds 0..59 exactly once")
    return result


def frozen_sector(row: dict[str, Any]) -> bool:
    return (
        row["default_species"].upper() == "LEMON"
        and int(float(row["delta_dist_sum"])) <= 8
    )


def load_delta_rows(sign_rows: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    observed_sha = sha256_path(DELTA_ROWS)
    if observed_sha != DELTA_SHA256:
        raise ValueError(f"delta CSV SHA mismatch: {observed_sha} != {DELTA_SHA256}")
    with DELTA_ROWS.open(newline="", encoding="utf-8") as stream:
        raw = list(csv.DictReader(stream))
    if len(raw) != 360:
        raise ValueError(f"expected 360 delta rows, found {len(raw)}")
    rows = []
    keys = set()
    for item in raw:
        seed = int(item["seed"])
        opponent = item["opponent"]
        key = (seed, opponent)
        if key in keys:
            raise ValueError(f"duplicate delta key: {key}")
        keys.add(key)
        if seed not in sign_rows:
            raise ValueError(f"delta seed absent from sign rows: {seed}")
        if opponent not in OPPONENTS:
            raise ValueError(f"unexpected opponent: {opponent}")
        sign = sign_rows[seed]
        if item["control_species"] != sign["default_species"]:
            raise ValueError(
                f"species mismatch seed {seed}: {item['control_species']} != "
                f"{sign['default_species']}"
            )
        seat = ast.literal_eval(item["delta_seat_margins"])
        if not isinstance(seat, list) or len(seat) != 2:
            raise ValueError(f"invalid seat delta row: {key}: {seat}")
        delta = float(item["delta_paired_margin"])
        if abs(delta - mean(float(value) for value in seat)) > 1e-9:
            raise ValueError(f"paired/seat delta mismatch: {key}")
        policy_delta = float(item["delta_policy_score"])
        opponent_delta = float(item["delta_opponent_score"])
        if abs(delta - (policy_delta - opponent_delta)) > 1e-9:
            raise ValueError(f"score decomposition mismatch: {key}")
        selected = frozen_sector(sign)
        rows.append(
            {
                "seed": seed,
                "opponent": opponent,
                "control_species": item["control_species"],
                "selected": selected,
                "flip_delta_margin": delta,
                "candidate_delta_margin": delta if selected else 0.0,
                "candidate_minus_always_flip": 0.0 if selected else -delta,
                "flip_delta_seats": [float(value) for value in seat],
                "candidate_delta_seats": [
                    float(value) if selected else 0.0 for value in seat
                ],
                "candidate_delta_policy_score": policy_delta if selected else 0.0,
                "candidate_delta_opponent_score": opponent_delta if selected else 0.0,
                "candidate_delta_wood_edge": (
                    float(item["delta_paired_wood_edge"]) if selected else 0.0
                ),
            }
        )
    expected_keys = {(seed, opponent) for seed in range(60) for opponent in OPPONENTS}
    if keys != expected_keys:
        raise ValueError("delta table does not contain the exact 60 x 6 key grid")
    return rows


def grouped_means(rows: list[dict[str, Any]], key_field: str, value_field: str) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for row in rows:
        groups.setdefault(str(row[key_field]), []).append(float(row[value_field]))
    return {key: mean(values) for key, values in sorted(groups.items())}


def root_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for seed in range(60):
        subset = [row for row in rows if row["seed"] == seed]
        if len(subset) != 6:
            raise ValueError(f"seed {seed} has {len(subset)} rows")
        result.append(
            {
                "seed": seed,
                "selected": subset[0]["selected"],
                "flip_delta_margin": mean(row["flip_delta_margin"] for row in subset),
                "candidate_delta_margin": mean(
                    row["candidate_delta_margin"] for row in subset
                ),
                "candidate_minus_always_flip": mean(
                    row["candidate_minus_always_flip"] for row in subset
                ),
                "candidate_delta_policy_score": mean(
                    row["candidate_delta_policy_score"] for row in subset
                ),
                "candidate_delta_opponent_score": mean(
                    row["candidate_delta_opponent_score"] for row in subset
                ),
                "candidate_delta_wood_edge": mean(
                    row["candidate_delta_wood_edge"] for row in subset
                ),
            }
        )
    return result


def clustered_bootstrap(root_level: list[dict[str, Any]], field: str) -> dict[str, float]:
    rng = random.Random(BOOTSTRAP_SEED)
    values = [float(row[field]) for row in root_level]
    draws = []
    n = len(values)
    for _ in range(BOOTSTRAP_REPS):
        draws.append(mean(values[rng.randrange(n)] for _ in range(n)))
    draws.sort()
    return {
        "repetitions": BOOTSTRAP_REPS,
        "seed": BOOTSTRAP_SEED,
        "lower_95": quantile(draws, 0.025),
        "median": quantile(draws, 0.5),
        "upper_95": quantile(draws, 0.975),
        "probability_le_zero": sum(value <= 0 for value in draws) / len(draws),
    }


def leave_one_family_out(rows: list[dict[str, Any]], field: str) -> dict[str, float]:
    return {
        opponent: mean(row[field] for row in rows if row["opponent"] != opponent)
        for opponent in OPPONENTS
    }


def price() -> dict[str, Any]:
    sign_rows = load_sign_rows()
    rows = load_delta_rows(sign_rows)
    roots = root_rows(rows)

    # Reproduce the original E7 summaries before pricing C1.
    global_flip = mean(row["flip_delta_margin"] for row in rows)
    positive_flip_roots = sum(root["flip_delta_margin"] > 0 for root in roots)
    oracle = mean(max(0.0, root["flip_delta_margin"]) for root in roots)
    if abs(global_flip - (-12.17361111111111)) > 1e-9:
        raise ValueError(f"global E7 FLIP mismatch: {global_flip}")
    if positive_flip_roots != 24:
        raise ValueError(f"E7 positive-root count mismatch: {positive_flip_roots}")
    if abs(oracle - 10.509722222222223) > 1e-9:
        raise ValueError(f"E7 oracle mismatch: {oracle}")

    selected_roots = [root for root in roots if root["selected"]]
    if len(selected_roots) != 13:
        raise ValueError(f"frozen sector support mismatch: {len(selected_roots)}")
    selected_positive = sum(root["flip_delta_margin"] > 0 for root in selected_roots)
    if selected_positive != 10:
        raise ValueError(f"frozen sector positive count mismatch: {selected_positive}")

    candidate_mean = mean(root["candidate_delta_margin"] for root in roots)
    candidate_vs_flip = mean(root["candidate_minus_always_flip"] for root in roots)
    selected_effect = mean(root["flip_delta_margin"] for root in selected_roots)
    candidate_policy = mean(root["candidate_delta_policy_score"] for root in roots)
    candidate_opponent = mean(root["candidate_delta_opponent_score"] for root in roots)
    candidate_wood = mean(root["candidate_delta_wood_edge"] for root in roots)
    seat_means = [
        mean(row["candidate_delta_seats"][seat] for row in rows)
        for seat in (0, 1)
    ]
    family_means = grouped_means(rows, "opponent", "candidate_delta_margin")
    selected_family_means = {
        opponent: mean(
            row["flip_delta_margin"]
            for row in rows
            if row["selected"] and row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }

    result = {
        "schema": "troll-farm-e7a-frozen-sector-pricing/1",
        "task": "20260802-e7a-sector-candidate",
        "verdict": "FROZEN_RULE_PRICED_ON_CONSUMED_E7_ONLY",
        "inputs": {
            "sign_rows": str(SIGN_ROWS.relative_to(ROOT)),
            "delta_rows": str(DELTA_ROWS.relative_to(ROOT)),
            "delta_rows_sha256": DELTA_SHA256,
            "row_count": len(rows),
            "root_count": len(roots),
            "opponents": list(OPPONENTS),
        },
        "rule": {
            "definition": "default LEMON and alternate-minus-default distance <= 8",
            "selected_roots": len(selected_roots),
            "selected_root_ids": [root["seed"] for root in selected_roots],
            "selected_positive_roots": selected_positive,
            "selected_nonpositive_roots": len(selected_roots) - selected_positive,
        },
        "integrity_reproduction": {
            "global_always_flip_margin": global_flip,
            "positive_flip_roots": positive_flip_roots,
            "hindsight_oracle_margin": oracle,
        },
        "candidate_c1": {
            "c1_minus_c0_mean_margin": candidate_mean,
            "c1_minus_c0_root_cluster_bootstrap": clustered_bootstrap(
                roots, "candidate_delta_margin"
            ),
            "c1_minus_a1_mean_margin": candidate_vs_flip,
            "c1_minus_a1_root_cluster_bootstrap": clustered_bootstrap(
                roots, "candidate_minus_always_flip"
            ),
            "best_static_arm": "C0",
            "c1_minus_best_static_mean_margin": candidate_mean,
            "selected_root_conditional_margin": selected_effect,
            "oracle_capture_fraction": candidate_mean / oracle if oracle else math.nan,
            "seat_means": seat_means,
            "opponent_family_means": family_means,
            "selected_root_opponent_family_means": selected_family_means,
            "leave_one_family_out_means": leave_one_family_out(
                rows, "candidate_delta_margin"
            ),
            "root_signs": {
                "positive": sum(root["candidate_delta_margin"] > 0 for root in roots),
                "zero": sum(root["candidate_delta_margin"] == 0 for root in roots),
                "negative": sum(root["candidate_delta_margin"] < 0 for root in roots),
                "selected_positive": selected_positive,
                "selected_negative_or_zero": len(selected_roots) - selected_positive,
            },
            "score_decomposition": {
                "own_policy_score_delta": candidate_policy,
                "opponent_score_delta": candidate_opponent,
                "reconstructed_margin_delta": candidate_policy - candidate_opponent,
                "wood_edge_delta": candidate_wood,
            },
        },
        "unavailable_from_compact_delta_table": [
            "absolute control/candidate terminal margins",
            "candidate catastrophe count/rate",
            "candidate negative-margin mass",
            "candidate win/tie/loss changes",
            "fresh-root or official-map generalization",
            "Arena rating effect",
        ],
        "interpretation": {
            "rule_frozen_before_magnitude_recovery": True,
            "labels_and_pricing_panel_consumed": True,
            "no_refit_or_threshold_change": True,
            "development_measurement_only": True,
            "source_or_arena_authorization": False,
        },
        "root_rows": roots,
    }
    if abs(
        result["candidate_c1"]["score_decomposition"]["reconstructed_margin_delta"]
        - candidate_mean
    ) > 1e-9:
        raise ValueError("candidate score decomposition does not reconstruct margin")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = price()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    c1 = result["candidate_c1"]
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "selected_roots": result["rule"]["selected_roots"],
                "c1_minus_c0": c1["c1_minus_c0_mean_margin"],
                "c1_minus_a1": c1["c1_minus_a1_mean_margin"],
                "ci95": [
                    c1["c1_minus_c0_root_cluster_bootstrap"]["lower_95"],
                    c1["c1_minus_c0_root_cluster_bootstrap"]["upper_95"],
                ],
                "own_delta": c1["score_decomposition"]["own_policy_score_delta"],
                "opponent_delta": c1["score_decomposition"]["opponent_score_delta"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
