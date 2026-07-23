#!/usr/bin/env python3
"""Score the frozen local continuation zoo against exact Phase 21 trajectories."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.arena_opponent_opening_calibration import commands, train_spec, unit_command


MODELS = (
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
)
CHECKPOINTS = ("50", "100", "final")
FEATURES = (
    "score",
    "fruit",
    "wood",
    "workers",
    "plants",
    "harvested_fruit",
    "chops",
    "dropped_items",
)
ACTUAL_FIELDS = {
    "score": "score",
    "fruit": "fruit",
    "wood": "wood",
    "workers": "workers",
    "plants": "successful_plants",
    "harvested_fruit": "harvested_fruit",
    "chops": "chops_landed",
    "dropped_items": "dropped_items",
}
TOLERANCES = {
    "50": {
        "score": 20,
        "fruit": 6,
        "wood": 5,
        "workers": 1,
        "plants": 4,
        "harvested_fruit": 8,
        "chops": 15,
        "dropped_items": 12,
    },
    "100": {
        "score": 35,
        "fruit": 10,
        "wood": 8,
        "workers": 1,
        "plants": 8,
        "harvested_fruit": 15,
        "chops": 25,
        "dropped_items": 20,
    },
    "final": {
        "score": 60,
        "fruit": 15,
        "wood": 15,
        "workers": 1,
        "plants": 15,
        "harvested_fruit": 30,
        "chops": 50,
        "dropped_items": 40,
    },
}
TERMINAL_TOLERANCE = 40

INTEGER_FIELDS = (
    "game_id",
    "terminal_turn",
    *(f"t{checkpoint}_{feature}" for checkpoint in ("50", "100") for feature in FEATURES),
    *(f"final_{feature}" for feature in FEATURES),
)


def read_local_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def actual_checkpoint(record: dict, checkpoint: str) -> dict:
    if checkpoint == "final":
        return record["actual"]["final"]
    return record["actual"]["checkpoints"][checkpoint]


def opening_comparison(record: dict, local: dict) -> dict:
    actual = commands(record["actual_first_command"])
    predicted = commands(local["first_commands"])
    actual_train = train_spec(actual)
    predicted_train = train_spec(predicted)
    actual_unit = unit_command(actual, int(record["opponent_starter_id"]))
    predicted_unit = unit_command(predicted, int(record["opponent_starter_id"]))
    actual_verb = actual_unit[0] if actual_unit else None
    predicted_verb = predicted_unit[0] if predicted_unit else None
    train_presence = (actual_train is None) == (predicted_train is None)
    return {
        "train_presence_exact": train_presence,
        "train_exact": actual_train == predicted_train,
        "starter_verb_exact": actual_verb == predicted_verb,
        "starter_command_exact": actual_unit == predicted_unit,
        "commands_exact": actual == predicted,
        "coarse_opening": train_presence and actual_verb == predicted_verb,
        "exact_opening": actual_train == predicted_train and actual_unit == predicted_unit,
        "actual_train": actual_train,
        "predicted_train": predicted_train,
        "actual_starter_verb": actual_verb,
        "predicted_starter_verb": predicted_verb,
    }


def score_model_game(record: dict, local: dict) -> dict:
    opening = opening_comparison(record, local)
    checks = {}
    scaled_errors = []
    missing = False
    for checkpoint in CHECKPOINTS:
        actual = actual_checkpoint(record, checkpoint)
        prefix = f"t{checkpoint}" if checkpoint != "final" else "final"
        for feature in FEATURES:
            observed = int(actual[ACTUAL_FIELDS[feature]])
            predicted = int(local[f"{prefix}_{feature}"])
            if predicted < 0:
                missing = True
            error = abs(predicted - observed)
            tolerance = TOLERANCES[checkpoint][feature]
            checks[f"{checkpoint}_{feature}"] = error <= tolerance and predicted >= 0
            scaled_errors.append(error / tolerance)
    terminal_error = abs(int(local["terminal_turn"]) - int(record["actual"]["turns"]))
    terminal_pass = terminal_error <= TERMINAL_TOLERANCE
    required = all(
        checks[f"final_{feature}"] for feature in ("score", "wood", "workers")
    )
    macro_passes = sum(checks.values())
    macro_covers = (
        not missing and macro_passes >= 20 and required and terminal_pass
    )
    return {
        **opening,
        "macro_feature_passes": macro_passes,
        "macro_feature_checks": checks,
        "terminal_error": terminal_error,
        "terminal_pass": terminal_pass,
        "macro_covers": macro_covers,
        "fully_covers": macro_covers and opening["coarse_opening"],
        "normalized_macro_distance": statistics.mean(
            [*scaled_errors, terminal_error / TERMINAL_TOLERANCE]
        ),
        "missing_checkpoint": missing,
    }


def rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def cohort_summary(rows: list[dict]) -> dict:
    return {
        "games": len(rows),
        "coarse_opening": sum(row["coarse_opening"] for row in rows),
        "exact_opening": sum(row["exact_opening"] for row in rows),
        "macro_covers": sum(row["macro_covers"] for row in rows),
        "fully_covers": sum(row["fully_covers"] for row in rows),
        "coarse_opening_rate": rate(
            sum(row["coarse_opening"] for row in rows), len(rows)
        ),
        "exact_opening_rate": rate(sum(row["exact_opening"] for row in rows), len(rows)),
        "macro_coverage_rate": rate(sum(row["macro_covers"] for row in rows), len(rows)),
        "full_coverage_rate": rate(sum(row["fully_covers"] for row in rows), len(rows)),
        "mean_normalized_macro_distance": statistics.mean(
            row["normalized_macro_distance"] for row in rows
        )
        if rows
        else None,
    }


def archetype_key(record: dict) -> str:
    final = record["actual"]["final"]
    workers = int(final["workers"])
    plants = int(final["successful_plants"])
    chops = int(final["chops_landed"])
    scale = "rich3plus" if workers >= 3 else "compact2" if workers == 2 else "solo1"
    if plants >= 20 and chops >= 60:
        economy = "farm_wood"
    elif plants >= 20:
        economy = "farm_only"
    elif chops >= 60:
        economy = "wood_only"
    else:
        economy = "low_activity"
    opening = commands(record["actual_first_command"])
    trained = "train_now" if train_spec(opening) is not None else "deferred"
    return f"{scale}:{economy}:{trained}"


def archetype_summary(records: list[dict]) -> dict:
    finals = [record["actual"]["final"] for record in records]
    train_specs = []
    for record in records:
        spec = train_spec(commands(record["actual_first_command"]))
        train_specs.append("/".join(map(str, spec)) if spec else "none")
    return {
        "games": len(records),
        "opponents": dict(sorted(Counter(record["opponent"] for record in records).items())),
        "opening_train_specs": dict(sorted(Counter(train_specs).items())),
        "mean_final": {
            feature: statistics.mean(
                final[ACTUAL_FIELDS[feature]] for final in finals
            )
            for feature in FEATURES
        },
    }


def analyze(observed: dict, local_rows: list[dict]) -> dict:
    records = observed.get("records") or []
    if len(records) != 160:
        raise ValueError(f"expected 160 observed games, got {len(records)}")
    by_game = {int(record["game_id"]): record for record in records}
    if len(by_game) != 160:
        raise ValueError("observed cohort has duplicate game IDs")
    identities = {(row["game_id"], row["model"]) for row in local_rows}
    if len(identities) != len(local_rows):
        raise ValueError("local audit has duplicate game/model rows")
    expected = {(game_id, model) for game_id in by_game for model in MODELS}
    if identities != expected:
        raise ValueError("local audit does not contain the exact 160 x 8 grid")
    if any(row["model"] not in MODELS for row in local_rows):
        raise ValueError("unexpected local model")

    scored_rows = []
    rows_by_game: dict[int, list[dict]] = defaultdict(list)
    rows_by_model: dict[str, list[dict]] = defaultdict(list)
    for local in local_rows:
        record = by_game[local["game_id"]]
        result = score_model_game(record, local)
        row = {
            "game_id": local["game_id"],
            "model": local["model"],
            "opponent": record["opponent"],
            "catastrophic": record["catastrophic"],
            "worker_rich": record["worker_rich"],
            **result,
        }
        scored_rows.append(row)
        rows_by_game[row["game_id"]].append(row)
        rows_by_model[row["model"]].append(row)
    if any(row["missing_checkpoint"] for row in scored_rows):
        raise ValueError("at least one local trajectory misses a frozen checkpoint")

    game_rows = []
    nearest_counts = Counter()
    for game_id, model_rows in sorted(rows_by_game.items()):
        record = by_game[game_id]
        nearest = min(
            model_rows,
            key=lambda row: (row["normalized_macro_distance"], row["model"]),
        )
        nearest_counts[nearest["model"]] += 1
        game_rows.append(
            {
                "game_id": game_id,
                "opponent": record["opponent"],
                "catastrophic": record["catastrophic"],
                "worker_rich": record["worker_rich"],
                "coarse_opening_supported": any(
                    row["coarse_opening"] for row in model_rows
                ),
                "exact_opening_supported": any(row["exact_opening"] for row in model_rows),
                "macro_supported": any(row["macro_covers"] for row in model_rows),
                "fully_supported": any(row["fully_covers"] for row in model_rows),
                "covering_models": sorted(
                    row["model"] for row in model_rows if row["fully_covers"]
                ),
                "nearest_model": nearest["model"],
                "nearest_distance": nearest["normalized_macro_distance"],
            }
        )

    catastrophic_games = [row for row in game_rows if row["catastrophic"]]
    worker_rich_games = [row for row in game_rows if row["worker_rich"]]
    overall_full = rate(sum(row["fully_supported"] for row in game_rows), len(game_rows))
    catastrophic_full = rate(
        sum(row["fully_supported"] for row in catastrophic_games),
        len(catastrophic_games),
    )
    worker_rich_full = rate(
        sum(row["fully_supported"] for row in worker_rich_games),
        len(worker_rich_games),
    )
    exact_opening = rate(
        sum(row["exact_opening_supported"] for row in game_rows), len(game_rows)
    )
    per_opponent = {}
    for opponent in sorted({record["opponent"] for record in records}):
        group = [row for row in game_rows if row["opponent"] == opponent]
        per_opponent[opponent] = {
            "games": len(group),
            "full_coverage": sum(row["fully_supported"] for row in group),
            "full_coverage_rate": rate(
                sum(row["fully_supported"] for row in group), len(group)
            ),
        }
    sufficiently_sampled = [
        report for report in per_opponent.values() if report["games"] >= 5
    ]
    checks = {
        "overall_full_coverage": overall_full is not None and overall_full >= 0.70,
        "catastrophic_full_coverage": catastrophic_full is not None
        and catastrophic_full >= 0.70,
        "worker_rich_full_coverage": worker_rich_full is not None
        and worker_rich_full >= 0.60,
        "exact_opening_support": exact_opening is not None and exact_opening >= 0.50,
        "sampled_opponent_floor": bool(sufficiently_sampled)
        and all(report["full_coverage_rate"] >= 0.50 for report in sufficiently_sampled),
        "integrity": len(scored_rows) == 1280 and len(game_rows) == 160,
    }

    adaptive_rows = rows_by_model["gold_adaptive"]
    adaptive_cat = [row for row in adaptive_rows if row["catastrophic"]]
    adaptive_worker = [row for row in adaptive_rows if row["worker_rich"]]
    adaptive_cat_macro = rate(
        sum(row["macro_covers"] for row in adaptive_cat), len(adaptive_cat)
    )
    adaptive_worker_macro = rate(
        sum(row["macro_covers"] for row in adaptive_worker), len(adaptive_worker)
    )
    adaptive_cat_nearest = rate(
        sum(
            row["nearest_model"] == "gold_adaptive"
            for row in catastrophic_games
        ),
        len(catastrophic_games),
    )
    adaptive_worker_nearest = rate(
        sum(row["nearest_model"] == "gold_adaptive" for row in worker_rich_games),
        len(worker_rich_games),
    )
    adaptive_checks = {
        "catastrophic_macro_coverage": adaptive_cat_macro is not None
        and adaptive_cat_macro >= 0.20,
        "worker_rich_macro_coverage": adaptive_worker_macro is not None
        and adaptive_worker_macro >= 0.20,
        "catastrophic_nearest": adaptive_cat_nearest is not None
        and adaptive_cat_nearest >= 0.15,
        "worker_rich_nearest": adaptive_worker_nearest is not None
        and adaptive_worker_nearest >= 0.15,
    }

    uncovered = [by_game[row["game_id"]] for row in game_rows if not row["fully_supported"]]
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in uncovered:
        groups[archetype_key(record)].append(record)
    missing_archetypes = [
        {"archetype": key, **archetype_summary(group)}
        for key, group in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))[:3]
    ]

    model_summary = {
        model: {
            "all": cohort_summary(rows_by_model[model]),
            "catastrophic": cohort_summary(
                [row for row in rows_by_model[model] if row["catastrophic"]]
            ),
            "worker_rich": cohort_summary(
                [row for row in rows_by_model[model] if row["worker_rich"]]
            ),
            "nearest_games": nearest_counts[model],
        }
        for model in MODELS
    }
    return {
        "schema": 1,
        "scope": (
            "exact-map full-trajectory support audit on consumed Phase 21 games; "
            "not rollout weighting or candidate evidence"
        ),
        "games": len(game_rows),
        "model_cells": len(scored_rows),
        "models": MODELS,
        "tolerances": TOLERANCES,
        "terminal_tolerance": TERMINAL_TOLERANCE,
        "coverage": {
            "overall": {
                "games": len(game_rows),
                "coarse_opening_supported": sum(
                    row["coarse_opening_supported"] for row in game_rows
                ),
                "exact_opening_supported": sum(
                    row["exact_opening_supported"] for row in game_rows
                ),
                "macro_supported": sum(row["macro_supported"] for row in game_rows),
                "fully_supported": sum(row["fully_supported"] for row in game_rows),
                "full_coverage_rate": overall_full,
                "exact_opening_rate": exact_opening,
            },
            "catastrophic": {
                "games": len(catastrophic_games),
                "fully_supported": sum(
                    row["fully_supported"] for row in catastrophic_games
                ),
                "full_coverage_rate": catastrophic_full,
            },
            "worker_rich": {
                "games": len(worker_rich_games),
                "fully_supported": sum(
                    row["fully_supported"] for row in worker_rich_games
                ),
                "full_coverage_rate": worker_rich_full,
            },
        },
        "zoo_gate_checks": checks,
        "zoo_adequate": all(checks.values()),
        "adaptive_gold_relevance": {
            "catastrophic_macro_coverage_rate": adaptive_cat_macro,
            "worker_rich_macro_coverage_rate": adaptive_worker_macro,
            "catastrophic_nearest_rate": adaptive_cat_nearest,
            "worker_rich_nearest_rate": adaptive_worker_nearest,
            "checks": adaptive_checks,
            "material_field_proxy": all(adaptive_checks.values()),
        },
        "model_summary": model_summary,
        "nearest_model_counts": dict(sorted(nearest_counts.items())),
        "per_opponent": per_opponent,
        "missing_archetypes": missing_archetypes,
        "game_rows": game_rows,
        "model_game_rows": scored_rows,
        "decision": (
            "zoo passes frozen support gate"
            if all(checks.values())
            else "zoo is unsupported for calibrated robust policy selection; reconstruct missing archetypes"
        ),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(json.loads(args.observed.read_text()), read_local_rows(args.local))
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "model_cells": payload["model_cells"],
        "coverage": payload["coverage"],
        "zoo_gate_checks": payload["zoo_gate_checks"],
        "zoo_adequate": payload["zoo_adequate"],
        "adaptive_gold_relevance": payload["adaptive_gold_relevance"],
        "nearest_model_counts": payload["nearest_model_counts"],
        "missing_archetypes": payload["missing_archetypes"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
