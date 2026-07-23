#!/usr/bin/env python3
"""Validate the frozen D57a exact post-stock deficit-vector preflight."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
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
PROTOCOL = ANALYSIS / "d57a-exact-post-stock-deficit-vector-preflight-protocol-2026-07-21.md"
D56_RESULT = ANALYSIS / "d56a-deficit-scaled-lemon-source-result.json"
D56_RUN = ANALYSIS / "d56a-deficit-scaled-lemon-source-a-phase21-local.tsv"
D55_RUN = ANALYSIS / "d55a-terminal-train-stock-flow-phase21-local.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
PARENTS = ANALYSIS / "d50a-current-legend-v2-phase21-local.tsv"
RUN_A = ANALYSIS / "d57a-exact-post-stock-deficit-vector-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d57a-exact-post-stock-deficit-vector-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d57a-exact-post-stock-deficit-vector-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "8c45e8bf82b17130d1d2303d2bfad5a68dec2c0327fe8e2f7c09f662e02168f0",
    D56_RESULT: "2ad610b248ae0af6933465079c0de510ee6bfd3b9fa08cea8f588c08060b7d50",
    D56_RUN: "90ac87e0f5140192bafb346d161a116d84821fa317f3b6d30880acc9b443a912",
    D55_RUN: "59240f763c285c5961be0eea417b5a66ad5e049ccb076f7835caeb67fdb766fa",
    RUNNER: "b634af9d3cb3d2240c562a21ab3c6ab3f942f1ae9f8367642a2598a6cfccf552",
    STRATEGY: "394548bc6000826d1d2cdcc12cda1c696ad1c92ca15c525626d872e9c5448309",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    PARENTS: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
}

CONFIGS = {
    label.replace("legend_v3_", "legend_v7_"): config
    for label, config in D52_CONFIGS.items()
}
MODELS = tuple(CONFIGS)
EXPECTED_WORKER_TWO = {"hp2": 130, "balanced": 134}
FRUITS = ("plum", "lemon", "apple", "banana")


def validate_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(int(row["game_id"]), row["model"]) for row in rows}
    if len(rows) != 1_280 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D57a grid is not exact 160 x 8")


def workforce_transition_summary(pairs: list[tuple[int, int]]) -> dict:
    transitions = Counter(pairs)
    deltas = [treatment - baseline for baseline, treatment in pairs]
    return {
        "cells": len(pairs),
        "transitions": {
            f"{baseline}_to_{treatment}": cells
            for (baseline, treatment), cells in sorted(transitions.items())
        },
        "promoted_cells": sum(delta > 0 for delta in deltas),
        "unchanged_cells": sum(delta == 0 for delta in deltas),
        "demoted_cells": sum(delta < 0 for delta in deltas),
        "net_worker_delta": sum(deltas),
    }


def species_delta_summary(pairs: list[tuple[dict, dict]]) -> dict:
    out = {}
    for fruit in FRUITS:
        plants = [
            int(treatment[f"successful_plants_{fruit}"])
            - int(baseline[f"successful_plants_{fruit}"])
            for baseline, treatment in pairs
        ]
        harvested = [
            int(treatment[f"harvested_{fruit}"])
            - int(baseline[f"harvested_{fruit}"])
            for baseline, treatment in pairs
        ]
        out[fruit] = {
            "successful_plants_total_delta": sum(plants),
            "successful_plants_mean_delta": statistics.mean(plants)
            if plants
            else None,
            "harvested_total_delta": sum(harvested),
            "harvested_mean_delta": statistics.mean(harvested)
            if harvested
            else None,
        }
    return out


def comparison_rows(path: Path, expected_prefix: str) -> list[dict]:
    rows = read_local_rows(path)
    identities = {(int(row["game_id"]), row["model"]) for row in rows}
    if (
        len(rows) != 1_280
        or len(identities) != 1_280
        or any(not row["model"].startswith(expected_prefix) for row in rows)
    ):
        raise ValueError(f"comparison grid {path} is not exact 160 x 8")
    return rows


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D57a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D57a repeated preflight matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D57a result")

    observed = json.loads(OBSERVED.read_text())
    game_ids = {
        int(record["game_id"]) for record in (observed.get("records") or [])
    }
    if len(game_ids) != 160:
        raise ValueError("D57a observed cohort is not 160 unique games")
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
        raise ValueError("D57a V2 parent rows are not exact 160 x 2")

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
        {**row, "model": row["model"].replace("legend_v7_", "legend_v3_")}
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
        label.replace("legend_v3_", "legend_v7_"): values
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

    treatment_by_identity = {
        (int(row["game_id"]), row["model"]): row for row in rows_a
    }
    comparisons = {}
    changed_from_v5 = 0
    d55_blocked_pairs = []
    for name, path, prefix in (
        ("v5", D55_RUN, "legend_v5_"),
        ("v6", D56_RUN, "legend_v6_"),
    ):
        baseline_rows = comparison_rows(path, prefix)
        worker_pairs = []
        missing = []
        for baseline in baseline_rows:
            treatment_model = baseline["model"].replace(prefix, "legend_v7_")
            treatment = treatment_by_identity.get(
                (int(baseline["game_id"]), treatment_model)
            )
            if treatment is None:
                missing.append((int(baseline["game_id"]), treatment_model))
                continue
            worker_pairs.append(
                (int(baseline["final_workers"]), int(treatment["final_workers"]))
            )
            if name == "v5":
                changed_from_v5 += terminal_signature(baseline) != terminal_signature(
                    treatment
                )
                if int(baseline["next_train_target"]) == 3:
                    d55_blocked_pairs.append((baseline, treatment))
        if missing:
            raise ValueError(f"missing {name} comparison pairs")
        comparisons[name] = workforce_transition_summary(worker_pairs)

    total_cells = len(rows_a)
    max4_labels = [
        label for label, config in CONFIGS.items() if config["max_workers"] == 4
    ]
    workforce_pass = all(activation.values()) and all(invariance.values())
    transaction_pass = all(transaction.values())
    gates = {**activation, **invariance, **transaction}
    if not transaction_pass:
        decision = "reject V7 before workforce interpretation and trace the TRAIN regression"
    elif not all(invariance.values()):
        decision = "reject V7: treatment leaked into the frozen worker-two layer"
    elif workforce_pass:
        decision = "freeze V7 and specify a separate consumed-map support audit"
    elif changed_from_v5:
        decision = (
            "close this exact vector allocator and diagnose allocation time versus exact "
            "bill-coordinate progress before choosing another controller representation"
        )
    else:
        decision = (
            "trace exact seed/source access and V5 fallbacks; do not add weights or thresholds"
        )

    report = {
        "schema": 1,
        "scope": (
            "exact deficit-vector activation, workforce, and TRAIN integrity on consumed maps only; "
            "score direction, support, distance, cohorts, opponent identity, candidate value, and "
            "platform outcomes ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "d56_result_sha256": sha256(D56_RESULT),
            "d56_matrix_sha256": sha256(D56_RUN),
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
            "changed_from_v2_parent": changed_from_parent,
            "changed_from_v2_parent_rate": changed_from_parent / total_cells,
            "changed_from_v5": changed_from_v5,
            "changed_from_v5_rate": changed_from_v5 / total_cells,
            "transitions": comparisons,
        },
        "d55_target_three_blocked_species_delta": {
            "cells": len(d55_blocked_pairs),
            "by_species": species_delta_summary(d55_blocked_pairs),
        },
        "train_transactions_by_target": by_target,
        "gates": gates,
        "transaction_pass": transaction_pass,
        "vector_active": changed_from_v5 > 0,
        "workforce_pass": workforce_pass,
        "pass": all(gates.values()),
        "decision": decision,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
