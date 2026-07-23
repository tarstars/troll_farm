#!/usr/bin/env python3
"""Validate the frozen D54a shared PICK-ledger workforce preflight."""

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
from cgauto.arena_opponent_opening_calibration import commands, train_spec
from cgauto.field_continuation_coverage import read_local_rows


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d54a-shared-pick-ledger-workforce-preflight-protocol-2026-07-21.md"
AMENDMENT = ANALYSIS / "d52a-opening-affordability-amendment-2026-07-21.md"
D53B_RESULT = ANALYSIS / "d53b-shared-surplus-diagnostic-result.json"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
PARENTS = ANALYSIS / "d50a-current-legend-v2-phase21-local.tsv"
RUN_A = ANALYSIS / "d54a-shared-pick-ledger-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d54a-shared-pick-ledger-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d54a-shared-pick-ledger-activation-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "2231f5972c0a5243a1ade1771d79a9e3b827e2ce8fab6988137c0917836a5175",
    AMENDMENT: "4438d60f76d4adf800ab94bd684dbffbb642cf1d54ad873501aee25382fb9979",
    D53B_RESULT: "bc980354842b0defc20206281318baea46950e9925c0f0612eb69c71fd68e8ae",
    RUNNER: "99aec36964f8d6b865f9ad34801f97565877d7ddb9e3e50aa004c0152fea8e3e",
    STRATEGY: "f5ec11f3ec8b480e82bbbc6c39e7caa77efdb2a678e0d5a190eaf0035c8e098d",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    PARENTS: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
}

CONFIGS = {
    label.replace("legend_v3_", "legend_v5_"): config
    for label, config in D52_CONFIGS.items()
}
MODELS = tuple(CONFIGS)


def validate_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(row["game_id"], row["model"]) for row in rows}
    if len(rows) != 1_280 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D54a grid is not exact 160 x 8")


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D54a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D54a repeated activation matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D54a result")

    observed = json.loads(OBSERVED.read_text())
    game_ids = {
        int(record["game_id"]) for record in (observed.get("records") or [])
    }
    if len(game_ids) != 160:
        raise ValueError("D54a observed cohort is not 160 unique games")
    rows_a = read_local_rows(RUN_A)
    rows_b = read_local_rows(RUN_B)
    validate_grid(rows_a, game_ids)
    validate_grid(rows_b, game_ids)
    repeat_exact = RUN_A.read_bytes() == RUN_B.read_bytes()
    complete_grid = all(complete_row(row) for row in [*rows_a, *rows_b])

    parent_labels = {config["parent"] for config in CONFIGS.values()}
    parent_by_game_model = {
        (row["game_id"], row["model"]): row
        for row in read_local_rows(PARENTS)
        if row["model"] in parent_labels
    }
    expected_parent_keys = {
        (game_id, parent) for game_id in game_ids for parent in parent_labels
    }
    if set(parent_by_game_model) != expected_parent_keys:
        raise ValueError("D54a V2 parent rows are not exact 160 x 2")

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

    d52_rows = [
        {**row, "model": row["model"].replace("legend_v5_", "legend_v3_")}
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
        label.replace("legend_v3_", "legend_v5_"): values
        for label, values in d52_counts.items()
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
            "d53b_result_sha256": sha256(D53B_RESULT),
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
            "by_config": with_rates(counts),
            "aggregate": {
                "worker_two": sum(v["worker_two"] for v in counts.values()),
                "worker_two_rate": sum(v["worker_two"] for v in counts.values())
                / total_cells,
                "worker_three": sum(v["worker_three"] for v in counts.values()),
                "worker_three_rate": sum(v["worker_three"] for v in counts.values())
                / total_cells,
                "worker_four_max4": sum(
                    counts[label]["worker_four"] for label in max4_labels
                ),
                "worker_four_max4_rate": sum(
                    counts[label]["worker_four"] for label in max4_labels
                )
                / sum(counts[label]["cells"] for label in max4_labels),
                "successful_crop": sum(v["successful_crop"] for v in counts.values()),
                "successful_crop_rate": sum(
                    v["successful_crop"] for v in counts.values()
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
            "freeze all eight V5 trajectories and specify a separate consumed-map support audit"
            if all(gates.values())
            else (
                "shared spending is repaired; close transaction tuning and diagnose acquisition deficits"
                if all(transaction.values())
                else "transaction repair failed; trace the new exact cause before workforce interpretation"
            )
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
