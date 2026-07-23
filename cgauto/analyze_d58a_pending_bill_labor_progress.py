#!/usr/bin/env python3
"""Validate and interpret the frozen D58a pending-bill labor diagnostic."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d52b_train_transaction import KINDS, TARGETS, partition_exact


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d58a-pending-bill-labor-progress-diagnostic-protocol-2026-07-21.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
D57_RESULT = ANALYSIS / "d57a-exact-post-stock-deficit-vector-result.json"

FAMILIES = {
    "v5": {
        "old": ANALYSIS / "d54a-shared-pick-ledger-a-phase21-local.tsv",
        "new": ANALYSIS / "d58a-pending-bill-v5-phase21-local.tsv",
        "prefix": "legend_v5_",
    },
    "v6": {
        "old": ANALYSIS / "d56a-deficit-scaled-lemon-source-a-phase21-local.tsv",
        "new": ANALYSIS / "d58a-pending-bill-v6-phase21-local.tsv",
        "prefix": "legend_v6_",
    },
    "v7": {
        "old": ANALYSIS / "d57a-exact-post-stock-deficit-vector-a-phase21-local.tsv",
        "new": ANALYSIS / "d58a-pending-bill-v7-phase21-local.tsv",
        "prefix": "legend_v7_",
    },
}
OUTPUT = ANALYSIS / "d58a-pending-bill-labor-progress-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "4e66064ecbb2d97c93ecb179fd3b9283b0c252417443cb4f1ec62b592e7ee99b",
    RUNNER: "bbfd6a0732cf2d531d359247f33b41b508c9d37b71e46a7531a4f301aa45519d",
    STRATEGY: "394548bc6000826d1d2cdcc12cda1c696ad1c92ca15c525626d872e9c5448309",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    D57_RESULT: "5f3ad4745d2012d40289733e007c0a909a29c75920122a38ddc0ede152959eda",
    FAMILIES["v5"]["old"]: "66f99af783e855fc64e48df3990bf04469fe1dea07798ede6b95a4fea17a1263",
    FAMILIES["v6"]["old"]: "90ac87e0f5140192bafb346d161a116d84821fa317f3b6d30880acc9b443a912",
    FAMILIES["v7"]["old"]: "58382e713123931f207d37c539bd96a7a7a9e53f1243f577ea88968ad14f7704",
}

ACTIONS = ("move", "pick", "drop", "plant", "harvest", "mine", "chop", "idle")
RESOURCES = ("plum", "lemon", "apple", "iron")
FRUITS = ("plum", "lemon", "apple", "banana")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def mean(values: list[int]) -> float | None:
    return statistics.mean(values) if values else None


def median(values: list[int]) -> float | None:
    return statistics.median(values) if values else None


def summarize(rows: list[dict[str, str]]) -> dict:
    turns = [int(row["pending3_turns"]) for row in rows]
    worker_turns = sum(int(row["pending3_worker_turns"]) for row in rows)
    noncompletion_turns = sum(
        int(row["pending3_progress_turns"])
        + int(row["pending3_equal_turns"])
        + int(row["pending3_regress_turns"])
        for row in rows
    )
    action_totals = {
        action: sum(int(row[f"pending3_action_{action}"]) for row in rows)
        for action in ACTIONS
    }
    reduced = sum(int(row["pending3_reduced_units"]) for row in rows)
    increased = sum(int(row["pending3_increased_units"]) for row in rows)
    per_action = {}
    for action in ACTIONS:
        observed = sum(int(row[f"pending3_{action}_observed_turns"]) for row in rows)
        progress = sum(int(row[f"pending3_{action}_progress_turns"]) for row in rows)
        regress = sum(int(row[f"pending3_{action}_regress_turns"]) for row in rows)
        per_action[action] = {
            "observed_turns": observed,
            "progress_turns": progress,
            "progress_rate": progress / observed if observed else None,
            "regress_turns": regress,
            "regress_rate": regress / observed if observed else None,
        }
    deficits = {}
    for resource in RESOURCES:
        initial = [int(row[f"pending3_initial_deficit_{resource}"]) for row in rows]
        minimum = [int(row[f"pending3_minimum_deficit_{resource}"]) for row in rows]
        last = [int(row[f"pending3_last_deficit_{resource}"]) for row in rows]
        deficits[resource] = {
            "initial_mean": mean(initial),
            "minimum_mean": mean(minimum),
            "last_mean": mean(last),
            "initial_to_minimum_mean": mean(
                [before - after for before, after in zip(initial, minimum)]
            ),
            "initial_to_last_mean": mean(
                [before - after for before, after in zip(initial, last)]
            ),
        }
    return {
        "cells": len(rows),
        "reached_worker_three": sum(int(row["final_workers"]) >= 3 for row in rows),
        "pending_turns": {
            "total": sum(turns),
            "mean": mean(turns),
            "median": median(turns),
        },
        "pending_worker_turns": worker_turns,
        "actions": {
            action: {
                "count": count,
                "share": count / worker_turns if worker_turns else None,
            }
            for action, count in action_totals.items()
        },
        "source_and_travel_share": sum(
            action_totals[action] for action in ("move", "pick", "plant")
        )
        / worker_turns
        if worker_turns
        else None,
        "capitalization_share": sum(
            action_totals[action] for action in ("drop", "harvest", "mine")
        )
        / worker_turns
        if worker_turns
        else None,
        "progress": {
            "noncompletion_turns": noncompletion_turns,
            "decrease_turns": sum(
                int(row["pending3_progress_turns"]) for row in rows
            ),
            "equal_turns": sum(int(row["pending3_equal_turns"]) for row in rows),
            "increase_turns": sum(
                int(row["pending3_regress_turns"]) for row in rows
            ),
            "reduced_units": reduced,
            "increased_units": increased,
            "net_units": reduced - increased,
            "net_units_per_worker_turn": (reduced - increased) / worker_turns
            if worker_turns
            else None,
        },
        "per_action_next_state": per_action,
        "deficit": deficits,
        "species": {
            fruit: {
                "successful_plants": sum(
                    int(row[f"successful_plants_{fruit}"]) for row in rows
                ),
                "harvested": sum(int(row[f"harvested_{fruit}"]) for row in rows),
            }
            for fruit in FRUITS
        },
    }


def integrity_failures(rows: list[dict[str, str]]) -> dict[str, int]:
    action_sum = sum(
        sum(int(row[f"pending3_action_{action}"]) for action in ACTIONS)
        != int(row["pending3_worker_turns"])
        for row in rows
    )
    progress_partition = sum(
        int(row["pending3_progress_turns"])
        + int(row["pending3_equal_turns"])
        + int(row["pending3_regress_turns"])
        != int(row["pending3_turns"]) - int(row["train3_successes"])
        for row in rows
    )
    vector_order = sum(
        any(
            int(row[f"pending3_minimum_deficit_{resource}"])
            > int(row[f"pending3_initial_deficit_{resource}"])
            for resource in RESOURCES
        )
        for row in rows
    )
    transaction_partition = 0
    for row in rows:
        for target in TARGETS:
            transaction_partition += not partition_exact(
                {kind: int(row[f"train{target}_{kind}"]) for kind in KINDS}
            )
    return {
        "action_sum_mismatches": action_sum,
        "progress_partition_mismatches": progress_partition,
        "minimum_vector_order_mismatches": vector_order,
        "train_partition_mismatches": transaction_partition,
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D58a prerequisite missing or changed: {path}")
    if any(not family["new"].exists() for family in FAMILIES.values()):
        raise SystemExit("missing D58a diagnostic matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D58a result")

    observed = json.loads(OBSERVED.read_text())
    game_ids = {
        str(record["game_id"]) for record in (observed.get("records") or [])
    }
    if len(game_ids) != 160:
        raise ValueError("D58a observed cohort is not 160 unique games")

    rows_by_family = {}
    integrity = {}
    summaries = {}
    for name, family in FAMILIES.items():
        old_rows = read_rows(family["old"])
        new_rows = read_rows(family["new"])
        expected_models = {
            f"{family['prefix']}{first}_m{cap}_p{post}"
            for first in ("hp2", "balanced")
            for cap in (3, 4)
            for post in (1, 2)
        }
        identities = {(row["game_id"], row["model"]) for row in new_rows}
        expected_identities = {
            (game_id, model) for game_id in game_ids for model in expected_models
        }
        if (
            len(new_rows) != 1_280
            or len(identities) != 1_280
            or identities != expected_identities
        ):
            raise ValueError(f"D58a {name} grid is not exact 160 x 8")
        new_by_identity = {
            (row["game_id"], row["model"]): row for row in new_rows
        }
        common_mismatches = sum(
            any(new_by_identity[(row["game_id"], row["model"])].get(field) != value
                for field, value in row.items())
            for row in old_rows
        )
        failures = integrity_failures(new_rows)
        expected_worker_two = {
            model: 130 if "_hp2_" in model else 134 for model in expected_models
        }
        actual_worker_two = {
            model: sum(
                row["model"] == model and int(row["final_workers"]) >= 2
                for row in new_rows
            )
            for model in expected_models
        }
        worker_two_mismatches = sum(
            actual_worker_two[model] != expected_worker_two[model]
            for model in expected_models
        )
        integrity[name] = {
            "cells": len(new_rows),
            "identities": len(identities),
            "common_field_mismatches": common_mismatches,
            "worker_two_mismatches": worker_two_mismatches,
            **failures,
            "pass": common_mismatches == 0
            and worker_two_mismatches == 0
            and all(value == 0 for value in failures.values()),
        }
        rows_by_family[name] = new_rows
        summaries[name] = {
            "all": summarize(new_rows),
            "reached_worker_three": summarize(
                [row for row in new_rows if int(row["final_workers"]) >= 3]
            ),
            "blocked_worker_three": summarize(
                [row for row in new_rows if int(row["final_workers"]) == 2]
            ),
        }

    paired = {}
    for treatment in ("v6", "v7"):
        treatment_by_identity = {
            (
                row["game_id"],
                row["model"].replace(f"legend_{treatment}_", "legend_v5_"),
            ): row
            for row in rows_by_family[treatment]
        }
        pairs = [
            (baseline, treatment_by_identity[(baseline["game_id"], baseline["model"])])
            for baseline in rows_by_family["v5"]
        ]
        fields = (
            "pending3_turns",
            "pending3_worker_turns",
            "pending3_reduced_units",
            "pending3_increased_units",
            *(f"pending3_action_{action}" for action in ACTIONS),
        )
        paired[treatment] = {
            field: {
                "total_delta": sum(int(right[field]) - int(left[field]) for left, right in pairs),
                "mean_delta": statistics.mean(
                    int(right[field]) - int(left[field]) for left, right in pairs
                ),
            }
            for field in fields
        }

    base = summaries["v5"]["all"]
    source_shift = all(
        summaries[name]["all"]["source_and_travel_share"]
        > base["source_and_travel_share"]
        for name in ("v6", "v7")
    )
    progress_lower = all(
        summaries[name]["all"]["progress"]["net_units_per_worker_turn"]
        < base["progress"]["net_units_per_worker_turn"]
        for name in ("v6", "v7")
    )
    capitalization_lower = all(
        summaries[name]["all"]["capitalization_share"]
        < base["capitalization_share"]
        for name in ("v6", "v7")
    )
    integrity_pass = all(values["pass"] for values in integrity.values())
    if not integrity_pass:
        decision = "diagnostic integrity failed; repair telemetry before interpretation"
    elif source_shift and (progress_lower or capitalization_lower):
        decision = (
            "close source investment while only two workers exist; freeze a labor-preserving "
            "representation from the pending-bill action/progress evidence"
        )
    elif all(
        summaries[name]["all"]["progress"]["net_units_per_worker_turn"]
        > base["progress"]["net_units_per_worker_turn"]
        for name in ("v6", "v7")
    ) and capitalization_lower:
        decision = "freeze a materialization-first representation; source progress is not banked"
    else:
        dominant = max(
            RESOURCES,
            key=lambda resource: base["deficit"][resource]["last_mean"],
        )
        decision = (
            f"freeze a coordinate access/travel diagnostic for {dominant}; do not add a source floor"
        )

    report = {
        "schema": 1,
        "scope": (
            "pending worker-three bill labor and exact stock progress only on consumed maps; all "
            "score, support, distance, opponent, candidate-value, and platform outcomes ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "runner_sha256": sha256(RUNNER),
            "strategy_sha256": sha256(STRATEGY),
            "observed_sha256": sha256(OBSERVED),
            "maps_sha256": sha256(MAPS),
            "d57_result_sha256": sha256(D57_RESULT),
            "analyzer_sha256": sha256(Path(__file__)),
            **{
                f"{name}_old_sha256": sha256(family["old"])
                for name, family in FAMILIES.items()
            },
            **{
                f"{name}_diagnostic_sha256": sha256(family["new"])
                for name, family in FAMILIES.items()
            },
        },
        "integrity": integrity,
        "summaries": summaries,
        "paired_deltas_from_v5": paired,
        "decision_evidence": {
            "source_and_travel_share_increases_in_v6_and_v7": source_shift,
            "net_progress_per_worker_turn_decreases_in_v6_and_v7": progress_lower,
            "capitalization_share_decreases_in_v6_and_v7": capitalization_lower,
        },
        "pass": integrity_pass,
        "decision": decision,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
