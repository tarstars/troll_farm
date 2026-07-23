#!/usr/bin/env python3
"""Validate the frozen D56a deficit-scaled LEMON-source preflight."""

from __future__ import annotations

from collections import defaultdict
import json
import math
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d50a_phase_population import terminal_signature
from cgauto.analyze_d52a_hybrid_job_market import (
    CONFIGS as D52_CONFIGS,
    activation_gates,
    complete_row,
    summarize_counts,
    with_rates,
)
from cgauto.analyze_d53a_atomic_train_reservation import (
    transaction_gates,
    transaction_summary,
)
from cgauto.arena_opponent_opening_calibration import commands, train_spec
from cgauto.field_continuation_coverage import read_local_rows


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d56a-deficit-scaled-lemon-source-preflight-protocol-2026-07-21.md"
D55_RESULT = ANALYSIS / "d55a-terminal-train-stock-flow-result.json"
D55_RUN = ANALYSIS / "d55a-terminal-train-stock-flow-phase21-local.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
PARENTS = ANALYSIS / "d50a-current-legend-v2-phase21-local.tsv"
RUN_A = ANALYSIS / "d56a-deficit-scaled-lemon-source-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d56a-deficit-scaled-lemon-source-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d56a-deficit-scaled-lemon-source-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "79c7cb43ed873890b2f2a7bc6b7dc8d14764b957ad2a2c1b95a8026340f984a4",
    D55_RESULT: "eca4391b6f39400ad4683972268971ccfd2b00227a6c7f15255b5fec4782067c",
    D55_RUN: "59240f763c285c5961be0eea417b5a66ad5e049ccb076f7835caeb67fdb766fa",
    RUNNER: "9496e298219af3f6395eeeee0d5b72bd67d06f166984f9c3d0eaa2385ec42e4e",
    STRATEGY: "7abdf4d3bf6dba227286767922bfaa8b9334e593e502e0bc59dd54d63afdd873",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    PARENTS: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
}

CONFIGS = {
    label.replace("legend_v3_", "legend_v6_"): config
    for label, config in D52_CONFIGS.items()
}
MODELS = tuple(CONFIGS)
EXPECTED_WORKER_TWO = {"hp2": 130, "balanced": 134}
EXPECTED_BLOCKED_TARGET_THREE = 732
MIN_INCREASED_CELLS = 183
MIN_MEAN_LEMON_PLANT_DELTA = 1.0


def validate_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(int(row["game_id"]), row["model"]) for row in rows}
    if len(rows) != 1_280 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D56a grid is not exact 160 x 8")


def lemon_mechanism_summary(pairs: list[tuple[int, int]]) -> dict:
    deltas = [treatment - baseline for baseline, treatment in pairs]
    return {
        "cells": len(pairs),
        "increased_cells": sum(delta > 0 for delta in deltas),
        "equal_cells": sum(delta == 0 for delta in deltas),
        "decreased_cells": sum(delta < 0 for delta in deltas),
        "baseline_mean": statistics.mean(baseline for baseline, _ in pairs)
        if pairs
        else None,
        "treatment_mean": statistics.mean(treatment for _, treatment in pairs)
        if pairs
        else None,
        "mean_delta": statistics.mean(deltas) if deltas else None,
        "total_delta": sum(deltas),
    }


def lemon_mechanism_gates(summary: dict) -> dict[str, bool]:
    return {
        "exact_732_d55_target_three_blocked_pairs": summary["cells"]
        == EXPECTED_BLOCKED_TARGET_THREE,
        "at_least_183_blocked_cells_create_more_lemon_plants": summary[
            "increased_cells"
        ]
        >= MIN_INCREASED_CELLS,
        "mean_successful_lemon_plants_increases_by_at_least_one": summary[
            "mean_delta"
        ]
        is not None
        and summary["mean_delta"] + 1e-12 >= MIN_MEAN_LEMON_PLANT_DELTA,
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D56a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D56a repeated preflight matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D56a result")

    observed = json.loads(OBSERVED.read_text())
    game_ids = {
        int(record["game_id"]) for record in (observed.get("records") or [])
    }
    if len(game_ids) != 160:
        raise ValueError("D56a observed cohort is not 160 unique games")
    rows_a = read_local_rows(RUN_A)
    rows_b = read_local_rows(RUN_B)
    validate_grid(rows_a, game_ids)
    validate_grid(rows_b, game_ids)
    repeat_exact = RUN_A.read_bytes() == RUN_B.read_bytes()
    complete_grid = all(complete_row(row) for row in [*rows_a, *rows_b])

    parent_labels = {config["parent"] for config in CONFIGS.values()}
    parent_by_identity = {
        (int(row["game_id"]), row["model"]): row
        for row in read_local_rows(PARENTS)
        if row["model"] in parent_labels
    }
    expected_parent_identities = {
        (game_id, parent) for game_id in game_ids for parent in parent_labels
    }
    if set(parent_by_identity) != expected_parent_identities:
        raise ValueError("D56a V2 parent rows are not exact 160 x 2")

    opening_mismatches = []
    emitted_trains = defaultdict(int)
    cap_violations = []
    changed_cells = 0
    for row in rows_a:
        config = CONFIGS[row["model"]]
        parent = parent_by_identity[(int(row["game_id"]), config["parent"])]
        actual_train = train_spec(commands(row["first_commands"]))
        parent_train = train_spec(commands(parent["first_commands"]))
        emitted_trains[row["model"]] += actual_train is not None
        if actual_train != parent_train or (
            actual_train is not None and actual_train != config["first_spec"]
        ):
            opening_mismatches.append((int(row["game_id"]), row["model"]))
        if max(
            int(row["t50_workers"]),
            int(row["t100_workers"]),
            int(row["final_workers"]),
        ) > config["max_workers"]:
            cap_violations.append((int(row["game_id"]), row["model"]))
        if terminal_signature(row) != terminal_signature(parent):
            changed_cells += 1

    d52_rows = [
        {**row, "model": row["model"].replace("legend_v6_", "legend_v3_")}
        for row in rows_a
    ]
    d52_counts = summarize_counts(d52_rows)
    activation = activation_gates(
        repeat_exact=repeat_exact,
        complete_grid=complete_grid,
        opening_mismatches=len(opening_mismatches),
        cap_violations=len(cap_violations),
        counts=d52_counts,
        changed_cells=changed_cells,
    )
    counts = {
        label.replace("legend_v3_", "legend_v6_"): values
        for label, values in d52_counts.items()
    }
    worker_two_by_config = {
        label: {
            "expected": EXPECTED_WORKER_TWO[config["first_name"]],
            "actual": counts[label]["worker_two"],
            "exact": counts[label]["worker_two"]
            == EXPECTED_WORKER_TWO[config["first_name"]],
        }
        for label, config in CONFIGS.items()
    }
    invariance = {
        "every_config_worker_two_reach_exactly_matches_d54": all(
            values["exact"] for values in worker_two_by_config.values()
        )
    }

    by_target, partition_failures = transaction_summary(rows_a)
    transaction = transaction_gates(by_target, partition_failures)

    d55_rows = read_local_rows(D55_RUN)
    expected_d55_models = {label.replace("legend_v6_", "legend_v5_") for label in MODELS}
    d55_identities = {(int(row["game_id"]), row["model"]) for row in d55_rows}
    if (
        len(d55_rows) != 1_280
        or len(d55_identities) != 1_280
        or {row["model"] for row in d55_rows} != expected_d55_models
    ):
        raise ValueError("D55a comparison grid is not exact 160 x 8")
    treatment_by_identity = {
        (int(row["game_id"]), row["model"]): row for row in rows_a
    }
    pairs = []
    pairs_by_config = defaultdict(list)
    missing_pairs = []
    for baseline in d55_rows:
        if int(baseline["next_train_target"]) != 3:
            continue
        treatment_model = baseline["model"].replace("legend_v5_", "legend_v6_")
        identity = (int(baseline["game_id"]), treatment_model)
        treatment = treatment_by_identity.get(identity)
        if treatment is None:
            missing_pairs.append(identity)
            continue
        pair = (
            int(baseline["successful_plants_lemon"]),
            int(treatment["successful_plants_lemon"]),
        )
        pairs.append(pair)
        pairs_by_config[treatment_model].append(pair)
    mechanism = lemon_mechanism_summary(pairs)
    mechanism["missing_pairs"] = len(missing_pairs)
    mechanism["by_config"] = {
        label: lemon_mechanism_summary(pairs_by_config[label]) for label in MODELS
    }
    mechanism_gates = lemon_mechanism_gates(mechanism)
    mechanism_gates["all_d55_blocked_cells_have_exact_treatment_pair"] = not missing_pairs

    total_cells = len(rows_a)
    max4_labels = [
        label for label, config in CONFIGS.items() if config["max_workers"] == 4
    ]
    workforce_pass = all(activation.values()) and all(invariance.values())
    mechanism_pass = all(mechanism_gates.values())
    transaction_pass = all(transaction.values())
    gates = {**activation, **invariance, **transaction, **mechanism_gates}
    if not transaction_pass:
        decision = "reject V6 before workforce interpretation and trace the TRAIN regression"
    elif not all(invariance.values()):
        decision = "reject V6: treatment leaked into the frozen worker-two layer"
    elif mechanism_pass and workforce_pass:
        decision = "freeze V6 and specify a separate consumed-map support audit"
    elif mechanism_pass:
        decision = (
            "close one-resource LEMON source building and freeze an exact deficit-vector "
            "source allocator using D55 secondary shortages"
        )
    else:
        decision = (
            "diagnose V6 seed access and farm-cap saturation; do not tune the LEMON floor"
        )

    report = {
        "schema": 1,
        "scope": (
            "prospective source acquisition, workforce activation, and TRAIN integrity on consumed "
            "maps only; score direction, support, distance, cohorts, opponent identity, candidate "
            "value, and platform outcomes ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "d55_result_sha256": sha256(D55_RESULT),
            "d55_matrix_sha256": sha256(D55_RUN),
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
            "immediate_trains_by_config": dict(emitted_trains),
            "train_partition_failures": partition_failures,
            "worker_two_invariance_by_config": worker_two_by_config,
        },
        "workforce": {
            "by_config": with_rates(counts),
            "aggregate": {
                "worker_two": sum(values["worker_two"] for values in counts.values()),
                "worker_two_rate": sum(
                    values["worker_two"] for values in counts.values()
                )
                / total_cells,
                "worker_three": sum(values["worker_three"] for values in counts.values()),
                "worker_three_rate": sum(
                    values["worker_three"] for values in counts.values()
                )
                / total_cells,
                "worker_four_max4": sum(
                    counts[label]["worker_four"] for label in max4_labels
                ),
                "worker_four_max4_rate": sum(
                    counts[label]["worker_four"] for label in max4_labels
                )
                / sum(counts[label]["cells"] for label in max4_labels),
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
        },
        "lemon_source_mechanism": mechanism,
        "train_transactions_by_target": by_target,
        "gates": gates,
        "transaction_pass": transaction_pass,
        "lemon_mechanism_pass": mechanism_pass,
        "workforce_pass": workforce_pass,
        "pass": all(gates.values()),
        "decision": decision,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
