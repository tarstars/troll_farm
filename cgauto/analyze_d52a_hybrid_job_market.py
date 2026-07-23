#!/usr/bin/env python3
"""Validate the frozen D52a hybrid job-market activation preflight."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d50a_phase_population import terminal_signature
from cgauto.arena_opponent_opening_calibration import commands, train_spec
from cgauto.field_continuation_coverage import FEATURES, read_local_rows


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d52a-hybrid-job-market-workforce-preflight-protocol-2026-07-21.md"
AMENDMENT = ANALYSIS / "d52a-opening-affordability-amendment-2026-07-21.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
PARENTS = ANALYSIS / "d50a-current-legend-v2-phase21-local.tsv"
RUN_A = ANALYSIS / "d52a-hybrid-job-market-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d52a-hybrid-job-market-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d52a-hybrid-job-market-activation-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "608ce2c166438da52171e788b6c2c7ca18908151ac3025eafda6a44a0859676d",
    AMENDMENT: "4438d60f76d4adf800ab94bd684dbffbb642cf1d54ad873501aee25382fb9979",
    RUNNER: "fb6c66f8cdcfa7d76b9309a4d05ae7d02c91733ea1e40516cbf6985294be92d1",
    STRATEGY: "d13dea27b559e531d7fc53dc316768d2cb30e91e1064dd46f46c2e05fb645b78",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    PARENTS: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
}

FIRST_SPECS = {
    "hp2": (2, 2, 2, 1),
    "balanced": (2, 2, 1, 1),
}
PARENT_LABELS = {
    "hp2": "legend_v2_hp2_cheap_farm",
    "balanced": "legend_v2_balanced_cheap_farm",
}


def expected_configs() -> dict[str, dict]:
    return {
        f"legend_v3_{first_name}_m{max_workers}_p{post_producers}": {
            "first_name": first_name,
            "first_spec": first_spec,
            "max_workers": max_workers,
            "post_producers": post_producers,
            "parent": PARENT_LABELS[first_name],
        }
        for first_name, first_spec in FIRST_SPECS.items()
        for max_workers in (3, 4)
        for post_producers in (1, 2)
    }


CONFIGS = expected_configs()
MODELS = tuple(CONFIGS)
MECHANISM_FIELDS = (
    "terminal_turn",
    *(
        f"{prefix}_{feature}"
        for prefix in ("t50", "t100", "final")
        for feature in FEATURES
        if feature != "score"
    ),
)


def validate_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(row["game_id"], row["model"]) for row in rows}
    if len(rows) != 1_280 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D52a grid is not exact 160 x 8")


def complete_row(row: dict) -> bool:
    return int(row["terminal_turn"]) >= 1 and all(
        int(row[f"{prefix}_{feature}"]) >= 0
        for prefix in ("t50", "t100", "final")
        for feature in FEATURES
    )


def mechanism_signature(row: dict) -> tuple[int, ...]:
    return tuple(int(row[field]) for field in MECHANISM_FIELDS)


def activation_gates(
    *,
    repeat_exact: bool,
    complete_grid: bool,
    opening_mismatches: int,
    cap_violations: int,
    counts: dict[str, dict[str, int]],
    changed_cells: int,
) -> dict[str, bool]:
    four_worker_models = [
        label for label, config in CONFIGS.items() if config["max_workers"] == 4
    ]
    return {
        "complete_byte_exact_repeat": repeat_exact and complete_grid,
        "parent_conditioned_first_train_exact": opening_mismatches == 0,
        "configured_worker_caps_exact": cap_violations == 0,
        "each_config_worker_two_at_least_90_percent": all(
            counts[label]["worker_two"] >= math.ceil(0.90 * counts[label]["cells"])
            for label in MODELS
        ),
        "each_config_worker_three_at_least_55_percent": all(
            counts[label]["worker_three"] >= math.ceil(0.55 * counts[label]["cells"])
            for label in MODELS
        ),
        "aggregate_worker_three_at_least_70_percent": sum(
            counts[label]["worker_three"] for label in MODELS
        )
        >= math.ceil(0.70 * sum(counts[label]["cells"] for label in MODELS)),
        "each_max4_config_worker_four_at_least_5_percent": all(
            counts[label]["worker_four"] >= math.ceil(0.05 * counts[label]["cells"])
            for label in four_worker_models
        ),
        "aggregate_max4_worker_four_at_least_15_percent": sum(
            counts[label]["worker_four"] for label in four_worker_models
        )
        >= math.ceil(
            0.15 * sum(counts[label]["cells"] for label in four_worker_models)
        ),
        "each_config_successful_crop_at_least_90_percent": all(
            counts[label]["successful_crop"]
            >= math.ceil(0.90 * counts[label]["cells"])
            for label in MODELS
        ),
        "aggregate_successful_crop_at_least_95_percent": sum(
            counts[label]["successful_crop"] for label in MODELS
        )
        >= math.ceil(0.95 * sum(counts[label]["cells"] for label in MODELS)),
        "at_least_50_percent_cells_change_from_v2_parent": changed_cells
        >= math.ceil(0.50 * sum(counts[label]["cells"] for label in MODELS)),
    }


def summarize_counts(rows: list[dict]) -> dict[str, dict[str, int]]:
    counts = {
        label: {
            "cells": 0,
            "worker_two": 0,
            "worker_three": 0,
            "worker_four": 0,
            "successful_crop": 0,
        }
        for label in MODELS
    }
    for row in rows:
        values = counts[row["model"]]
        workers = int(row["final_workers"])
        values["cells"] += 1
        values["worker_two"] += workers >= 2
        values["worker_three"] += workers >= 3
        values["worker_four"] += workers >= 4
        values["successful_crop"] += int(row["final_plants"]) >= 1
    return counts


def with_rates(counts: dict[str, dict[str, int]]) -> dict[str, dict]:
    return {
        label: {
            **values,
            **{
                f"{field}_rate": values[field] / values["cells"]
                for field in (
                    "worker_two",
                    "worker_three",
                    "worker_four",
                    "successful_crop",
                )
            },
        }
        for label, values in counts.items()
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D52a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D52a repeated activation matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D52a result")

    observed = json.loads(OBSERVED.read_text())
    game_ids = {
        int(record["game_id"]) for record in (observed.get("records") or [])
    }
    if len(game_ids) != 160:
        raise ValueError("D52a observed cohort is not 160 unique games")

    rows_a = read_local_rows(RUN_A)
    rows_b = read_local_rows(RUN_B)
    validate_grid(rows_a, game_ids)
    validate_grid(rows_b, game_ids)
    repeat_exact = RUN_A.read_bytes() == RUN_B.read_bytes()
    complete_grid = all(complete_row(row) for row in [*rows_a, *rows_b])

    parent_rows = read_local_rows(PARENTS)
    parent_by_game_model = {
        (row["game_id"], row["model"]): row
        for row in parent_rows
        if row["model"] in PARENT_LABELS.values()
    }
    expected_parent_keys = {
        (game_id, parent) for game_id in game_ids for parent in PARENT_LABELS.values()
    }
    if set(parent_by_game_model) != expected_parent_keys:
        raise ValueError("D52a V2 parent rows are not exact 160 x 2")

    opening_mismatches = []
    emitted_trains = {label: 0 for label in MODELS}
    cap_violations = []
    changed_cells = 0
    mechanism_changed_cells = 0
    for row in rows_a:
        config = CONFIGS[row["model"]]
        parent = parent_by_game_model[(row["game_id"], config["parent"])]
        actual_train = train_spec(commands(row["first_commands"]))
        parent_train = train_spec(commands(parent["first_commands"]))
        if actual_train is not None:
            emitted_trains[row["model"]] += 1
        if actual_train != parent_train or (
            actual_train is not None and actual_train != config["first_spec"]
        ):
            opening_mismatches.append((row["game_id"], row["model"]))
        if max(
            int(row["t50_workers"]),
            int(row["t100_workers"]),
            int(row["final_workers"]),
        ) > config["max_workers"]:
            cap_violations.append((row["game_id"], row["model"]))
        if terminal_signature(row) != terminal_signature(parent):
            changed_cells += 1
        if mechanism_signature(row) != mechanism_signature(parent):
            mechanism_changed_cells += 1

    counts = summarize_counts(rows_a)
    gates = activation_gates(
        repeat_exact=repeat_exact,
        complete_grid=complete_grid,
        opening_mismatches=len(opening_mismatches),
        cap_violations=len(cap_violations),
        counts=counts,
        changed_cells=changed_cells,
    )
    total_cells = len(rows_a)
    four_worker_models = [
        label for label, config in CONFIGS.items() if config["max_workers"] == 4
    ]
    report = {
        "schema": 1,
        "scope": (
            "activation and mechanism only on consumed maps; score direction, field support, "
            "coverage, cohorts, opponent identity, candidate value, and platform outcomes ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "amendment": str(AMENDMENT),
        "amendment_sha256": sha256(AMENDMENT),
        "inputs": {
            "observed_sha256": sha256(OBSERVED),
            "maps_sha256": sha256(MAPS),
            "v2_parents_sha256": sha256(PARENTS),
            "run_a_sha256": sha256(RUN_A),
            "run_b_sha256": sha256(RUN_B),
            "runner_sha256": sha256(RUNNER),
            "strategy_sha256": sha256(STRATEGY),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "grid": {
            "games": len(game_ids),
            "models": len(MODELS),
            "cells_per_run": total_cells,
            "repeat_byte_identical": repeat_exact,
            "all_checkpoints_complete": complete_grid,
        },
        "audit": {
            "outcome_fields_ignored": True,
            "support_not_evaluated": True,
            "opening_mismatches": len(opening_mismatches),
            "cap_violations": len(cap_violations),
            "expected_total_immediate_trains": 468,
            "actual_total_immediate_trains": sum(emitted_trains.values()),
            "immediate_trains_by_config": emitted_trains,
        },
        "mechanism": {
            "by_config": with_rates(counts),
            "aggregate": {
                "worker_two": sum(values["worker_two"] for values in counts.values()),
                "worker_two_rate": sum(
                    values["worker_two"] for values in counts.values()
                )
                / total_cells,
                "worker_three": sum(
                    values["worker_three"] for values in counts.values()
                ),
                "worker_three_rate": sum(
                    values["worker_three"] for values in counts.values()
                )
                / total_cells,
                "worker_four_max4": sum(
                    counts[label]["worker_four"] for label in four_worker_models
                ),
                "worker_four_max4_rate": sum(
                    counts[label]["worker_four"] for label in four_worker_models
                )
                / sum(counts[label]["cells"] for label in four_worker_models),
                "successful_crop": sum(
                    values["successful_crop"] for values in counts.values()
                ),
                "successful_crop_rate": sum(
                    values["successful_crop"] for values in counts.values()
                )
                / total_cells,
            },
            "changed_from_v2_parent": changed_cells,
            "changed_from_v2_parent_rate": changed_cells / total_cells,
            "mechanism_changed_from_v2_parent": mechanism_changed_cells,
            "mechanism_changed_from_v2_parent_rate": mechanism_changed_cells
            / total_cells,
        },
        "gates": gates,
        "pass": all(gates.values()),
        "decision": (
            "freeze all eight V3 configs and open the separately frozen support audit"
            if all(gates.values())
            else "close this exact V3 job market before support and localize its failed mechanism"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
