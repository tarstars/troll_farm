#!/usr/bin/env python3
"""Join live rollout activations to exact local continuation-model deltas."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics


EXPECTED_MODELS = ("gold_elite", "sched_bot", "mybot", "silver_boss")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def read_rollouts(path: Path) -> dict[tuple[int, int, str], dict[str, int]]:
    rows = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            key = (int(row["seed"]), int(row["seat"]), row["model"])
            if key in rows:
                raise ValueError(f"duplicate rollout row {key}")
            rows[key] = {
                "control_margin": int(row["control_margin"]),
                "option_margin": int(row["option_margin"]),
                "delta": int(row["delta"]),
            }
    return rows


def audit(
    forensics: dict,
    diverse: dict[tuple[int, int, str], dict[str, int]],
    compact: dict[tuple[int, int, str], dict[str, int]],
) -> dict:
    game_ids = {row["game_id"] for row in forensics["rows"]}
    expected_diverse = {
        (game_id, seat, model)
        for game_id in game_ids
        for seat in (0, 1)
        for model in EXPECTED_MODELS
    }
    if set(diverse) != expected_diverse:
        missing = sorted(expected_diverse - set(diverse))[:10]
        extra = sorted(set(diverse) - expected_diverse)[:10]
        raise ValueError(f"diverse rollout coverage mismatch; missing={missing}, extra={extra}")
    expected_compact = {
        (game_id, seat, "compact_gold")
        for game_id in game_ids
        for seat in (0, 1)
    }
    if set(compact) != expected_compact:
        missing = sorted(expected_compact - set(compact))[:10]
        extra = sorted(set(compact) - expected_compact)[:10]
        raise ValueError(f"CompactGold rollout coverage mismatch; missing={missing}, extra={extra}")

    parity_mismatches = []
    for game_id in sorted(game_ids):
        for seat in (0, 1):
            gold = diverse[(game_id, seat, "gold_elite")]
            compact_row = compact[(game_id, seat, "compact_gold")]
            if gold != compact_row:
                parity_mismatches.append(
                    {
                        "game_id": game_id,
                        "seat": seat,
                        "gold_elite": gold,
                        "compact_gold": compact_row,
                    }
                )

    reconstructed_selected = {
        game_id
        for game_id in game_ids
        if compact[(game_id, 0, "compact_gold")]["delta"] > 30
    }
    observed_selected = {
        row["game_id"]
        for row in forensics["rows"]
        if row["selection"] == "option"
    }
    selected_rows = []
    by_game = {row["game_id"]: row for row in forensics["rows"]}
    for game_id in sorted(observed_selected):
        deltas = {
            model: diverse[(game_id, 0, model)]["delta"]
            for model in EXPECTED_MODELS
        }
        arena = by_game[game_id]
        selected_rows.append(
            {
                "game_id": game_id,
                "arena_opponent": arena["opponent"],
                "arena_margin": arena["margin"],
                "arena_won": arena["won"],
                "model_deltas": deltas,
                "positive_model_count": sum(value > 0 for value in deltas.values()),
                "mean_model_delta": statistics.mean(deltas.values()),
                "worst_model_delta": min(deltas.values()),
                "all_models_positive": all(value > 0 for value in deltas.values()),
            }
        )

    return {
        "schema": 1,
        "scope": (
            "exact terminal control-vs-option rollouts on candidate-relative initial states "
            "from the known 60-game arena replay sample"
        ),
        "sample_games": len(game_ids),
        "model_names": EXPECTED_MODELS,
        "compact_gold_vs_gold_elite_exact_cells": len(expected_compact)
        - len(parity_mismatches),
        "compact_gold_vs_gold_elite_total_cells": len(expected_compact),
        "compact_gold_vs_gold_elite_mismatches": parity_mismatches,
        "selector_reconstruction": {
            "rule": "CompactGold option delta > 30",
            "observed_selected_game_ids": sorted(observed_selected),
            "reconstructed_selected_game_ids": sorted(reconstructed_selected),
            "exact": reconstructed_selected == observed_selected,
        },
        "selected_games": selected_rows,
        "selected_game_summary": {
            "games": len(selected_rows),
            "arena_wins": sum(row["arena_won"] for row in selected_rows),
            "all_models_positive": sum(
                row["all_models_positive"] for row in selected_rows
            ),
            "single_positive_model": sum(
                row["positive_model_count"] == 1 for row in selected_rows
            ),
            "negative_worst_model": sum(
                row["worst_model_delta"] < 0 for row in selected_rows
            ),
        },
        "interpretation_limit": (
            "The model deltas explain selector disagreement but are still simulator "
            "counterfactuals.  Arena margins are observational and do not reveal the exact "
            "resident-policy result on the same map and opponent."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forensics", type=Path, required=True)
    parser.add_argument("--diverse-rollouts", type=Path, required=True)
    parser.add_argument("--compact-rollouts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(
        json.loads(args.forensics.read_text()),
        read_rollouts(args.diverse_rollouts),
        read_rollouts(args.compact_rollouts),
    )
    if payload["compact_gold_vs_gold_elite_mismatches"]:
        raise RuntimeError("CompactGold and GoldElite rollout outcomes differ")
    if not payload["selector_reconstruction"]["exact"]:
        raise RuntimeError("rollout deltas do not reconstruct the observed selector")
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload["selected_game_summary"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
