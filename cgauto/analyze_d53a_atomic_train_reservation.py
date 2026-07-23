#!/usr/bin/env python3
"""Validate the frozen D53a atomic TRAIN-bill reservation preflight."""

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
from cgauto.analyze_d52b_train_transaction import KINDS, TARGETS, partition_exact
from cgauto.arena_opponent_opening_calibration import commands, train_spec
from cgauto.field_continuation_coverage import read_local_rows


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d53a-atomic-train-bill-reservation-protocol-2026-07-21.md"
AMENDMENT = ANALYSIS / "d52a-opening-affordability-amendment-2026-07-21.md"
D52B_RESULT = ANALYSIS / "d52b-train-transaction-diagnostic-result.json"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
PARENTS = ANALYSIS / "d50a-current-legend-v2-phase21-local.tsv"
RUN_A = ANALYSIS / "d53a-atomic-train-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d53a-atomic-train-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d53a-atomic-train-activation-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "5ff6dd6ac01db8b84a7fbb22610af8e5ea5fe7f5df0e10635b0f085d428050e2",
    AMENDMENT: "4438d60f76d4adf800ab94bd684dbffbb642cf1d54ad873501aee25382fb9979",
    D52B_RESULT: "9b4913fd19b243f4b37bbdf558901dd822e9d329e0b2457ca9ed62cde4cc69e6",
    RUNNER: "dd18c52790db4519e6d381afa38a2d42d010eb2361fd03eff7d53a1bb2e672e2",
    STRATEGY: "cf5cdb1df23033f88f465a8213d47b4291137c916d539f8861ba040f4363062a",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    PARENTS: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
}

CONFIGS = {
    label.replace("legend_v3_", "legend_v4_"): config
    for label, config in D52_CONFIGS.items()
}
MODELS = tuple(CONFIGS)


def validate_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(row["game_id"], row["model"]) for row in rows}
    if len(rows) != 1_280 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D53a grid is not exact 160 x 8")


def d52_count_labels(counts: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    return {
        label.replace("legend_v4_", "legend_v3_"): values
        for label, values in counts.items()
    }


def transaction_summary(rows: list[dict]) -> tuple[dict[str, dict[str, int]], int]:
    by_target = {
        str(target): {kind: 0 for kind in KINDS}
        for target in TARGETS
    }
    partition_failures = 0
    for row in rows:
        for target in TARGETS:
            values = {
                kind: int(row[f"train{target}_{kind}"])
                for kind in KINDS
            }
            partition_failures += not partition_exact(values)
            for kind, value in values.items():
                by_target[str(target)][kind] += value
    for values in by_target.values():
        values["failures"] = values["attempts"] - values["successes"]
        values["budget_inclusive"] = (
            values["fail_budget_only"] + values["fail_both"]
        )
    return by_target, partition_failures


def transaction_gates(
    by_target: dict[str, dict[str, int]], partition_failures: int
) -> dict[str, bool]:
    return {
        "every_train_attempt_partition_exact": partition_failures == 0
        and all(partition_exact(values) for values in by_target.values()),
        "zero_budget_inclusive_train_failures": all(
            values["budget_inclusive"] == 0 for values in by_target.values()
        ),
        "zero_unexplained_train_failures": all(
            values["fail_other"] == 0 for values in by_target.values()
        ),
        "target_three_four_failures_are_shack_only": all(
            by_target[str(target)][kind] == 0
            for target in (3, 4)
            for kind in ("fail_budget_only", "fail_both", "fail_other")
        ),
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D53a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D53a repeated activation matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D53a result")

    observed = json.loads(OBSERVED.read_text())
    game_ids = {
        int(record["game_id"]) for record in (observed.get("records") or [])
    }
    if len(game_ids) != 160:
        raise ValueError("D53a observed cohort is not 160 unique games")
    rows_a = read_local_rows(RUN_A)
    rows_b = read_local_rows(RUN_B)
    validate_grid(rows_a, game_ids)
    validate_grid(rows_b, game_ids)
    repeat_exact = RUN_A.read_bytes() == RUN_B.read_bytes()
    complete_grid = all(complete_row(row) for row in [*rows_a, *rows_b])

    parent_rows = read_local_rows(PARENTS)
    parent_labels = {config["parent"] for config in CONFIGS.values()}
    parent_by_game_model = {
        (row["game_id"], row["model"]): row
        for row in parent_rows
        if row["model"] in parent_labels
    }
    expected_parent_keys = {
        (game_id, parent) for game_id in game_ids for parent in parent_labels
    }
    if set(parent_by_game_model) != expected_parent_keys:
        raise ValueError("D53a V2 parent rows are not exact 160 x 2")

    opening_mismatches = []
    emitted_trains = defaultdict(int)
    cap_violations = []
    changed_cells = 0
    for row in rows_a:
        config = CONFIGS[row["model"]]
        parent = parent_by_game_model[(row["game_id"], config["parent"])]
        actual_train = train_spec(commands(row["first_commands"]))
        parent_train = train_spec(commands(parent["first_commands"]))
        emitted_trains[row["model"]] += actual_train is not None
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

    counts = summarize_counts(
        [
            {**row, "model": row["model"].replace("legend_v4_", "legend_v3_")}
            for row in rows_a
        ]
    )
    activation = activation_gates(
        repeat_exact=repeat_exact,
        complete_grid=complete_grid,
        opening_mismatches=len(opening_mismatches),
        cap_violations=len(cap_violations),
        counts=counts,
        changed_cells=changed_cells,
    )
    counts_v4 = {
        label.replace("legend_v3_", "legend_v4_"): values
        for label, values in counts.items()
    }
    by_target, partition_failures = transaction_summary(rows_a)
    transaction = transaction_gates(by_target, partition_failures)
    gates = {**activation, **transaction}
    total_cells = len(rows_a)
    max4_labels = [
        label for label, config in CONFIGS.items() if config["max_workers"] == 4
    ]
    report = {
        "schema": 1,
        "scope": (
            "activation and TRAIN transaction integrity only on consumed maps; score direction, "
            "support, distance, cohorts, opponent identity, candidate value, and platform outcomes ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "amendment_sha256": sha256(AMENDMENT),
            "d52b_result_sha256": sha256(D52B_RESULT),
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
        },
        "mechanism": {
            "by_config": with_rates(counts_v4),
            "aggregate": {
                "worker_two": sum(v["worker_two"] for v in counts_v4.values()),
                "worker_two_rate": sum(v["worker_two"] for v in counts_v4.values())
                / total_cells,
                "worker_three": sum(v["worker_three"] for v in counts_v4.values()),
                "worker_three_rate": sum(
                    v["worker_three"] for v in counts_v4.values()
                )
                / total_cells,
                "worker_four_max4": sum(
                    counts_v4[label]["worker_four"] for label in max4_labels
                ),
                "worker_four_max4_rate": sum(
                    counts_v4[label]["worker_four"] for label in max4_labels
                )
                / sum(counts_v4[label]["cells"] for label in max4_labels),
                "successful_crop": sum(
                    v["successful_crop"] for v in counts_v4.values()
                ),
                "successful_crop_rate": sum(
                    v["successful_crop"] for v in counts_v4.values()
                )
                / total_cells,
            },
            "changed_from_v2_parent": changed_cells,
            "changed_from_v2_parent_rate": changed_cells / total_cells,
        },
        "train_transactions_by_target": by_target,
        "gates": gates,
        "transaction_pass": all(transaction.values()),
        "workforce_pass": all(activation.values()),
        "pass": all(gates.values()),
        "decision": (
            "freeze all eight V4 trajectories and specify a separate consumed-map support audit"
            if all(gates.values())
            else (
                "TRAIN currency transaction is repaired, but funding acquisition remains insufficient"
                if all(transaction.values())
                else "transaction repair failed; diagnose the new exact cause before workforce interpretation"
            )
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
