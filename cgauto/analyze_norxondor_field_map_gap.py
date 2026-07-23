#!/usr/bin/env python3
"""Analyze the frozen exact-field-map versus local-opponent model-gap grid."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics


REPO = Path(__file__).resolve().parent.parent
DEFAULT_ROWS = (
    REPO / "data/analysis/live-agent-6553250/norxondor-field-map-gap-5x2x8.tsv"
)
DEFAULT_OBSERVED = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "norxondor-three-worker-stage2a-field-5-observed.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/norxondor-field-map-model-gap-2026-07-19.json"
)
MODELS = {
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
}
POLICIES = {"resident", "norx_three_worker_silver"}


def summarize(rows: list[dict]) -> dict:
    return {
        "cells": len(rows),
        "mean_score": statistics.mean(int(row["score"]) for row in rows),
        "mean_opponent_score": statistics.mean(int(row["opponent_score"]) for row in rows),
        "mean_margin": statistics.mean(int(row["margin"]) for row in rows),
        "mean_wood": statistics.mean(int(row["wood"]) for row in rows),
        "mean_workers": statistics.mean(int(row["workers"]) for row in rows),
        "worker_distribution": dict(Counter(int(row["workers"]) for row in rows)),
        "mean_third_worker_turn_or_301": statistics.mean(
            int(row["third_worker_turn"]) or 301 for row in rows
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--observed", type=Path, default=DEFAULT_OBSERVED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    with args.rows.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    observed_payload = json.loads(args.observed.read_text())
    observed = {int(row["game_id"]): row for row in observed_payload["records"]}
    identities = {
        (int(row["game_id"]), row["policy"], row["model"]) for row in rows
    }
    expected = {
        (game_id, policy, model)
        for game_id in observed
        for policy in POLICIES
        for model in MODELS
    }
    integrity = {
        "five_unique_maps": len(observed) == 5,
        "eighty_unique_cells": len(rows) == 80 and identities == expected,
        "all_terminal": all(1 <= int(row["terminal_turn"]) <= 300 for row in rows),
    }

    by_policy = defaultdict(list)
    by_key = {}
    for row in rows:
        by_policy[row["policy"]].append(row)
        by_key[(int(row["game_id"]), row["policy"], row["model"])] = row
    local = by_policy["norx_three_worker_silver"]
    actual_miss_maps = {game_id for game_id, row in observed.items() if row["workers"] < 3}
    miss_map_cells = [row for row in local if int(row["game_id"]) in actual_miss_maps]
    reached_on_miss_maps = sum(int(row["workers"]) >= 3 for row in miss_map_cells)
    missed_on_miss_maps = len(miss_map_cells) - reached_on_miss_maps

    per_map = {}
    score_covered = 0
    margin_covered = 0
    third_residuals = []
    for game_id, actual in observed.items():
        map_rows = [row for row in local if int(row["game_id"]) == game_id]
        scores = [int(row["score"]) for row in map_rows]
        margins = [int(row["margin"]) for row in map_rows]
        third_turns = [
            int(row["third_worker_turn"])
            for row in map_rows
            if int(row["third_worker_turn"]) > 0
        ]
        score_inside = min(scores) <= actual["scores"][0] <= max(scores)
        margin_inside = min(margins) <= actual["margin"] <= max(margins)
        score_covered += score_inside
        margin_covered += margin_inside
        actual_third = (
            actual["successful_training_turns"][1]
            if len(actual["successful_training_turns"]) >= 2
            else None
        )
        local_third_median = statistics.median(third_turns) if third_turns else None
        residual = (
            actual_third - local_third_median
            if actual_third is not None and local_third_median is not None
            else None
        )
        if residual is not None:
            third_residuals.append(residual)
        per_map[str(game_id)] = {
            "opponent": actual["opponent"],
            "actual": {
                "score": actual["scores"][0],
                "opponent_score": actual["scores"][1],
                "margin": actual["margin"],
                "workers": actual["workers"],
                "third_worker_turn": actual_third,
            },
            "local_three_worker": {
                "score_min_median_max": [min(scores), statistics.median(scores), max(scores)],
                "margin_min_median_max": [
                    min(margins),
                    statistics.median(margins),
                    max(margins),
                ],
                "worker_distribution": dict(
                    Counter(int(row["workers"]) for row in map_rows)
                ),
                "third_turn_min_median_max": [
                    min(third_turns) if third_turns else None,
                    local_third_median,
                    max(third_turns) if third_turns else None,
                ],
            },
            "actual_score_within_local_range": score_inside,
            "actual_margin_within_local_range": margin_inside,
            "actual_minus_local_median_third_turn": residual,
        }

    deltas = []
    for game_id in observed:
        for model in MODELS:
            resident = by_key[(game_id, "resident", model)]
            alternative = by_key[(game_id, "norx_three_worker_silver", model)]
            deltas.append(
                {
                    "game_id": game_id,
                    "model": model,
                    "score": int(alternative["score"]) - int(resident["score"]),
                    "opponent_score": int(alternative["opponent_score"])
                    - int(resident["opponent_score"]),
                    "margin": int(alternative["margin"]) - int(resident["margin"]),
                    "wood": int(alternative["wood"]) - int(resident["wood"]),
                }
            )
    per_model_delta = {}
    for model in sorted(MODELS):
        group = [row for row in deltas if row["model"] == model]
        per_model_delta[model] = {
            key: statistics.mean(row[key] for row in group)
            for key in ("score", "opponent_score", "margin", "wood")
        }

    discriminators = {
        "map_driven_funding_failure": missed_on_miss_maps >= 8,
        "opponent_model_driven_funding_failure": reached_on_miss_maps >= 13,
        "own_score_calibrated_at_least_4_of_5": score_covered >= 4,
        "margin_calibrated_at_least_4_of_5": margin_covered >= 4,
    }
    payload = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rows": str(args.rows),
        "observed": str(args.observed),
        "integrity": integrity,
        "local_policy_summaries": {
            policy: summarize(by_policy[policy]) for policy in sorted(POLICIES)
        },
        "actual_two_worker_maps": sorted(actual_miss_maps),
        "local_three_worker_cells_on_actual_two_worker_maps": {
            "cells": len(miss_map_cells),
            "reached_three": reached_on_miss_maps,
            "missed_three": missed_on_miss_maps,
        },
        "field_range_coverage": {
            "score_maps": score_covered,
            "margin_maps": margin_covered,
            "total_maps": 5,
        },
        "third_worker_turn_residuals": third_residuals,
        "per_map": per_map,
        "local_three_worker_minus_resident": {
            key: statistics.mean(row[key] for row in deltas)
            for key in ("score", "opponent_score", "margin", "wood")
        },
        "per_model_three_worker_minus_resident": per_model_delta,
        "discriminators": discriminators,
        "field_transfer_gate_retired": (
            not discriminators["own_score_calibrated_at_least_4_of_5"]
            and not discriminators["margin_calibrated_at_least_4_of_5"]
        ),
        "pass": all(integrity.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

