#!/usr/bin/env python3
"""Validate the frozen D59a materialization job-lease preflight."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
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
from cgauto.analyze_d57a_exact_post_stock_deficit_vector import (
    workforce_transition_summary,
)
from cgauto.analyze_d58a_pending_bill_labor_progress import (
    integrity_failures as pending_integrity_failures,
    summarize as pending_summary,
)
from cgauto.arena_opponent_opening_calibration import commands, train_spec
from cgauto.field_continuation_coverage import read_local_rows


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d59a-materialization-job-lease-preflight-protocol-2026-07-21.md"
AMENDMENT = ANALYSIS / "d59a-completion-turn-command-gate-amendment-2026-07-21.md"
D58_RESULT = ANALYSIS / "d58a-pending-bill-labor-progress-result.json"
V5_RUN = ANALYSIS / "d58a-pending-bill-v5-phase21-local.tsv"
ORIGINAL_RUN = ANALYSIS / "d59a-materialization-job-lease-a-phase21-local.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
PARENTS = ANALYSIS / "d50a-current-legend-v2-phase21-local.tsv"
RUN_A = ANALYSIS / "d59a-materialization-job-lease-corrected-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d59a-materialization-job-lease-corrected-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d59a-materialization-job-lease-corrected-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "79e35939cdffb71521e8d06e593fac2733d661389572d76e14a7d5020da4ce8b",
    AMENDMENT: "705fa35e75c5235c09e8252c9fdcd4ada09e1fa9911dfd330e2dbe8fd86fea1f",
    D58_RESULT: "c75325a23c37b042c109346b4145ef62eec29514de28e2004f3bbd6c008370c5",
    V5_RUN: "a2f44c821b94382e5ba67f086977153903f9efd98b973e21271df3468b98c0f8",
    ORIGINAL_RUN: "5ab3816fa573582cd69e940a83e8d1fd062ba4418fe39aca4c366d03ef943d43",
    RUNNER: "631ff64f65319762a12929f9f9708cd452e08d9d4117bf8aefb156af643fad9e",
    STRATEGY: "8334d99b0dcb5d508c02329e91e68af0cccfb8115244249d2f227be8fb322a73",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    PARENTS: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
}

CONFIGS = {
    label.replace("legend_v3_", "legend_v8_"): config
    for label, config in D52_CONFIGS.items()
}
MODELS = tuple(CONFIGS)
EXPECTED_WORKER_TWO = {"hp2": 130, "balanced": 134}


def validate_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(int(row["game_id"]), row["model"]) for row in rows}
    if len(rows) != 1_280 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D59a grid is not exact 160 x 8")


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D59a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D59a repeated preflight matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D59a result")

    observed = json.loads(OBSERVED.read_text())
    game_ids = {
        int(record["game_id"]) for record in (observed.get("records") or [])
    }
    if len(game_ids) != 160:
        raise ValueError("D59a observed cohort is not 160 unique games")
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
        raise ValueError("D59a V2 parent rows are not exact 160 x 2")

    opening_mismatches = []
    emitted_trains = defaultdict(int)
    cap_violations = []
    changed_from_parent = 0
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
        changed_from_parent += terminal_signature(row) != terminal_signature(parent)

    d52_rows = [
        {**row, "model": row["model"].replace("legend_v8_", "legend_v3_")}
        for row in rows_a
    ]
    d52_counts = summarize_counts(d52_rows)
    activation = activation_gates(
        repeat_exact=repeat_exact,
        complete_grid=complete_grid,
        opening_mismatches=len(opening_mismatches),
        cap_violations=len(cap_violations),
        counts=d52_counts,
        changed_cells=changed_from_parent,
    )
    counts = {
        label.replace("legend_v3_", "legend_v8_"): values
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
    pending_a = pending_integrity_failures(rows_a)
    pending_b = pending_integrity_failures(rows_b)
    pending_pick = sum(int(row["pending3_action_pick"]) for row in rows_a)
    pending_plant = sum(int(row["pending3_action_plant"]) for row in rows_a)
    completion_pick = sum(
        int(row["pending3_completion_action_pick"]) for row in rows_a
    )
    completion_plant = sum(
        int(row["pending3_completion_action_plant"]) for row in rows_a
    )
    completion_partition_failures = sum(
        sum(
            int(row[f"pending3_completion_action_{action}"])
            for action in ("move", "pick", "drop", "plant", "harvest", "mine", "chop", "idle")
        )
        != 2 * int(row["train3_successes"])
        for row in [*rows_a, *rows_b]
    )
    original_rows = read_local_rows(ORIGINAL_RUN)
    corrected_by_identity = {
        (int(row["game_id"]), row["model"]): row for row in rows_a
    }
    original_common_mismatches = sum(
        any(
            corrected_by_identity[(int(row["game_id"]), row["model"])].get(field)
            != value
            for field, value in row.items()
        )
        for row in original_rows
    )
    pending_gates = {
        "pending_action_progress_partitions_exact": all(
            value == 0 for value in [*pending_a.values(), *pending_b.values()]
        ),
        "completion_turn_action_partitions_exact": completion_partition_failures == 0,
        "corrected_run_reproduces_every_original_d59_field": original_common_mismatches == 0,
        "zero_lease_branch_pick_commands": pending_pick - completion_pick == 0,
        "zero_lease_branch_plant_commands": pending_plant - completion_plant == 0,
    }

    v5_rows = read_local_rows(V5_RUN)
    v5_by_identity = {
        (int(row["game_id"]), row["model"]): row for row in v5_rows
    }
    worker_pairs = []
    changed_from_v5 = 0
    for row in rows_a:
        v5_model = row["model"].replace("legend_v8_", "legend_v5_")
        baseline = v5_by_identity[(int(row["game_id"]), v5_model)]
        worker_pairs.append(
            (int(baseline["final_workers"]), int(row["final_workers"]))
        )
        changed_from_v5 += terminal_signature(baseline) != terminal_signature(row)

    total_cells = len(rows_a)
    max4_labels = [
        label for label, config in CONFIGS.items() if config["max_workers"] == 4
    ]
    workforce_pass = all(activation.values()) and all(invariance.values())
    transaction_pass = all(transaction.values())
    integrity_pass = all(pending_gates.values())
    gates = {**activation, **invariance, **transaction, **pending_gates}
    if not transaction_pass or not all(invariance.values()) or not integrity_pass:
        decision = "reject V8 before workforce interpretation and trace the exact regression"
    elif workforce_pass:
        decision = "freeze V8 and specify a separate consumed-map support audit"
    elif changed_from_v5:
        decision = (
            "close hand-designed source/materialization workforce jobs on this substrate and "
            "move to a different controller representation"
        )
    else:
        decision = "trace lease target availability only; support and value remain closed"

    report = {
        "schema": 1,
        "scope": (
            "materialization-lease activation, pending labor, workforce, and TRAIN integrity on "
            "consumed maps only; score direction, support, distance, opponent identity, candidate "
            "value, and platform outcomes ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "amendment": str(AMENDMENT),
        "amendment_sha256": sha256(AMENDMENT),
        "inputs": {
            "d58_result_sha256": sha256(D58_RESULT),
            "v5_matrix_sha256": sha256(V5_RUN),
            "original_d59_matrix_sha256": sha256(ORIGINAL_RUN),
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
            "train_partition_failures": partition_failures,
            "worker_two_invariance_by_config": worker_two_by_config,
            "pending_integrity_run_a": pending_a,
            "pending_integrity_run_b": pending_b,
            "original_common_field_mismatches": original_common_mismatches,
            "completion_partition_failures": completion_partition_failures,
            "pending_pick_commands_total": pending_pick,
            "pending_pick_commands_on_completion_turn": completion_pick,
            "pending_pick_commands_in_lease_branch": pending_pick - completion_pick,
            "pending_plant_commands_total": pending_plant,
            "pending_plant_commands_on_completion_turn": completion_plant,
            "pending_plant_commands_in_lease_branch": pending_plant - completion_plant,
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
            "changed_from_v2_parent": changed_from_parent,
            "changed_from_v2_parent_rate": changed_from_parent / total_cells,
            "changed_from_v5": changed_from_v5,
            "changed_from_v5_rate": changed_from_v5 / total_cells,
            "v5_transition": workforce_transition_summary(worker_pairs),
        },
        "pending_labor": {
            "v5": pending_summary(v5_rows),
            "v8": pending_summary(rows_a),
        },
        "train_transactions_by_target": by_target,
        "gates": gates,
        "transaction_pass": transaction_pass,
        "lease_active": changed_from_v5 > 0,
        "workforce_pass": workforce_pass,
        "pass": all(gates.values()),
        "decision": decision,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
