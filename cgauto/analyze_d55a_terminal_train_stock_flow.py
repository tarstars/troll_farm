#!/usr/bin/env python3
"""Validate and interpret the frozen D55a terminal TRAIN stock-flow diagnostic."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d52b_train_transaction import KINDS, TARGETS, partition_exact
from cgauto.analyze_d54a_shared_pick_ledger import MODELS


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d55a-terminal-train-stock-flow-diagnostic-protocol-2026-07-21.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
D54A = ANALYSIS / "d54a-shared-pick-ledger-a-phase21-local.tsv"
RUN = ANALYSIS / "d55a-terminal-train-stock-flow-phase21-local.tsv"
OUTPUT = ANALYSIS / "d55a-terminal-train-stock-flow-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "f3a9abf5d3932c38632ce1f10029d01fb54506b593a666321e0b721a4cd7bb91",
    RUNNER: "6cb143cff5e329ce70c8c6468a6e2663268cd2d83794f66155f8109ac80eed40",
    STRATEGY: "f5ec11f3ec8b480e82bbbc6c39e7caa77efdb2a678e0d5a190eaf0035c8e098d",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    D54A: "66f99af783e855fc64e48df3990bf04469fe1dea07798ede6b95a4fea17a1263",
}

CURRENCIES = ("plum", "lemon", "apple", "iron")
FRUITS = ("plum", "lemon", "apple", "banana")
READINESS = ("deposited_ready", "carry_closes", "ripe_closes", "source_unresolved")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def vector(row: dict[str, str], prefix: str, resources=CURRENCIES) -> dict[str, int]:
    return {resource: int(row[f"{prefix}_{resource}"]) for resource in resources}


def covers(stock: dict[str, int], cost: dict[str, int]) -> bool:
    return all(stock[resource] >= cost[resource] for resource in CURRENCIES)


def readiness_category(row: dict[str, str]) -> str:
    cost = vector(row, "next_cost")
    inventory = vector(row, "final_inventory")
    carry = vector(row, "final_carry")
    ripe = {
        resource: int(row[f"final_ripe_{resource}"])
        if resource != "iron"
        else 0
        for resource in CURRENCIES
    }
    if covers(inventory, cost):
        return "deposited_ready"
    inventory_carry = {
        resource: inventory[resource] + carry[resource]
        for resource in CURRENCIES
    }
    if covers(inventory_carry, cost):
        return "carry_closes"
    inventory_carry_ripe = {
        resource: inventory_carry[resource] + ripe[resource]
        for resource in CURRENCIES
    }
    if covers(inventory_carry_ripe, cost):
        return "ripe_closes"
    return "source_unresolved"


def dominant_resource(deficit_prevalence: dict[str, float]) -> str | None:
    ordered = sorted(deficit_prevalence.items(), key=lambda item: (-item[1], item[0]))
    if not ordered:
        return None
    top_resource, top_rate = ordered[0]
    second_rate = ordered[1][1] if len(ordered) > 1 else 0.0
    return (
        top_resource
        if top_rate + 1e-12 >= 0.70 and top_rate - second_rate + 1e-12 >= 0.15
        else None
    )


def select_mechanism(
    readiness: dict[str, int], deficit_prevalence: dict[str, float]
) -> str:
    total = sum(readiness.values())
    if not total:
        return "no blocked target-three cells; do not infer a mechanism"
    majority = next(
        (category for category in READINESS if readiness[category] / total >= 0.50),
        None,
    )
    if majority == "deposited_ready":
        return "end-of-turn retry"
    if majority == "carry_closes":
        return "explicit banking"
    if majority == "ripe_closes":
        return "ripe-harvest assignment"
    if majority == "source_unresolved":
        resource = dominant_resource(deficit_prevalence)
        return (
            f"resource-specific renewable/source acquisition: {resource}"
            if resource
            else "exact deficit-vector renewable/source acquisition"
        )
    return "factorized stock-flow allocator"


def summarize_target(rows: list[dict[str, str]]) -> dict:
    readiness = Counter(readiness_category(row) for row in rows)
    deficits = {resource: [] for resource in CURRENCIES}
    source = {
        fruit: {
            "successful_plants": [],
            "harvested": [],
            "standing": [],
            "ripe": [],
        }
        for fruit in FRUITS
    }
    for row in rows:
        cost = vector(row, "next_cost")
        inventory = vector(row, "final_inventory")
        for resource in CURRENCIES:
            deficits[resource].append(max(cost[resource] - inventory[resource], 0))
        for fruit in FRUITS:
            for field in source[fruit]:
                prefix = f"final_{field}" if field in {"standing", "ripe"} else field
                source[fruit][field].append(int(row[f"{prefix}_{fruit}"]))
    games = len(rows)
    prevalence = {
        resource: sum(value > 0 for value in values) / games if games else 0.0
        for resource, values in deficits.items()
    }
    return {
        "cells": games,
        "readiness": {
            category: {
                "cells": readiness[category],
                "rate": readiness[category] / games if games else None,
            }
            for category in READINESS
        },
        "deposited_deficit": {
            resource: {
                "positive_cells": sum(value > 0 for value in values),
                "positive_rate": prevalence[resource],
                "mean": statistics.mean(values) if values else None,
                "mean_when_positive": statistics.mean(
                    [value for value in values if value > 0]
                )
                if any(value > 0 for value in values)
                else None,
            }
            for resource, values in deficits.items()
        },
        "dominant_resource": dominant_resource(prevalence),
        "source_means": {
            fruit: {
                field: statistics.mean(values) if values else None
                for field, values in fields.items()
            }
            for fruit, fields in source.items()
        },
        "selected_mechanism": select_mechanism(
            {category: readiness[category] for category in READINESS}, prevalence
        ),
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D55a prerequisite missing or changed: {path}")
    if not RUN.exists():
        raise SystemExit("missing D55a diagnostic matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D55a result")

    baseline = read_rows(D54A)
    diagnostic = read_rows(RUN)
    if len(baseline) != 1_280 or len(diagnostic) != 1_280:
        raise ValueError("D55a matrices are not exact 160 x 8")
    identities = {(row["game_id"], row["model"]) for row in diagnostic}
    if len(identities) != 1_280 or {row["model"] for row in diagnostic} != set(MODELS):
        raise ValueError("D55a diagnostic identities are incomplete or duplicated")
    baseline_by_identity = {
        (row["game_id"], row["model"]): row for row in baseline
    }
    common_mismatches = sum(
        baseline_by_identity.get((row["game_id"], row["model"])) is None
        or any(
            row.get(field) != value
            for field, value in baseline_by_identity[
                (row["game_id"], row["model"])
            ].items()
        )
        for row in diagnostic
    )
    partition_failures = 0
    for row in diagnostic:
        for target in TARGETS:
            partition_failures += not partition_exact(
                {
                    kind: int(row[f"train{target}_{kind}"])
                    for kind in KINDS
                }
            )

    by_target_rows = {
        target: [row for row in diagnostic if int(row["next_train_target"]) == target]
        for target in TARGETS
    }
    by_target = {
        str(target): summarize_target(rows)
        for target, rows in by_target_rows.items()
    }
    target_three = by_target["3"]
    integrity = {
        "exact_160_by_8_grid": len(identities) == 1_280,
        "all_preexisting_fields_match_d54a": common_mismatches == 0,
        "all_attempt_partitions_exact": partition_failures == 0,
        "all_below_cap_rows_have_positive_target": sum(
            len(rows) for rows in by_target_rows.values()
        )
        == sum(int(row["next_train_target"]) > 0 for row in diagnostic),
    }
    report = {
        "schema": 1,
        "scope": (
            "terminal TRAIN stock-flow telemetry only on consumed maps; score, support, distance, "
            "cohort, opponent, candidate-value, and platform fields ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "d54a_sha256": sha256(D54A),
            "diagnostic_sha256": sha256(RUN),
            "observed_sha256": sha256(OBSERVED),
            "maps_sha256": sha256(MAPS),
            "runner_sha256": sha256(RUNNER),
            "strategy_sha256": sha256(STRATEGY),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "integrity": {
            **integrity,
            "common_field_mismatches": common_mismatches,
            "attempt_partition_failures": partition_failures,
        },
        "by_target": by_target,
        "binding_target_three": target_three,
        "pass": all(integrity.values()) and target_three["cells"] > 0,
        "decision": target_three["selected_mechanism"]
        if all(integrity.values()) and target_three["cells"] > 0
        else "diagnostic integrity failed; do not select a mechanism",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
