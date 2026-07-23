#!/usr/bin/env python3
"""Ablate recipe identity from D63a's held-agent capitalization signal."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
from cgauto.analyze_d63a_workforce_transition import (  # noqa: E402
    gate_model_b,
    model_report,
)


REPO = Path(__file__).resolve().parent.parent
SOURCE = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d63a-agent-held-workforce-transition-2026-07-21.json"
)
PROTOCOL = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d63b-capitalization-signal-ablation-protocol-2026-07-21.md"
)
EXPECTED_SOURCE_SHA256 = (
    "58be23c7a7e6b5995bcaa5b7a209a412f7a06a0231b66a8c9eb83013b5a98ef2"
)
EXPECTED_SOURCE_SCHEMA = "troll-farm-d63a-agent-held-workforce-transition-v1"
EXPECTED_REFERENCE = {
    "discovery_auc": 1.0,
    "discovery_balanced_accuracy": 1.0,
    "validation_auc": 0.9695652173913043,
    "validation_balanced_accuracy": 0.7833333333333333,
}

RECIPE_PREFIXES = (
    "first_train_",
    "worker0_",
    "worker1_",
    "workers_sum_",
    "workers_max_",
)
SNAPSHOT_PREFIXES = (
    "board_",
    "own_bank_",
    "opponent_bank_",
    "own_carry_",
    "opponent_carry_",
)
SNAPSHOT_EXACT = {
    "bank_score_gap",
    "bank_wood_gap",
    "own_carrying_workers",
    "opponent_carrying_workers",
    "opponent_worker_count",
}
FLOW_PREFIXES = (
    "own_successful_",
    "opponent_successful_",
    "own_planted_",
    "opponent_planted_",
)
FLOW_EXACT = {
    "own_harvested_amount",
    "opponent_harvested_amount",
    "own_chops_landed",
    "opponent_chops_landed",
    "own_dropped_amount",
    "opponent_dropped_amount",
}


def in_recipe(key: str) -> bool:
    return key.startswith(RECIPE_PREFIXES)


def in_snapshot(key: str) -> bool:
    return key in SNAPSHOT_EXACT or key.startswith(SNAPSHOT_PREFIXES)


def in_flow(key: str) -> bool:
    return in_snapshot(key) or key in FLOW_EXACT or key.startswith(FLOW_PREFIXES)


def select_features(features: dict, family: str) -> dict:
    predicates = {
        "recipe": in_recipe,
        "snapshot": in_snapshot,
        "flow": in_flow,
    }
    if family not in predicates:
        raise ValueError(f"unknown D63b feature family: {family}")
    selected = {
        key: value for key, value in features.items() if predicates[family](key)
    }
    if not selected:
        raise ValueError(f"D63b feature family {family} is empty")
    return selected


def verify_reference(source: dict) -> dict:
    reference = source["models"]["turn100"]
    actual = {
        "discovery_auc": reference["discovery"]["roc_auc"],
        "discovery_balanced_accuracy": reference["discovery"][
            "balanced_accuracy_at_0_5"
        ],
        "validation_auc": reference["validation"]["roc_auc"],
        "validation_balanced_accuracy": reference["validation"][
            "balanced_accuracy_at_0_5"
        ],
    }
    checks = {
        key: math.isclose(float(actual[key]), expected, rel_tol=0.0, abs_tol=1e-15)
        for key, expected in EXPECTED_REFERENCE.items()
    }
    if not all(checks.values()):
        raise ValueError(f"D63a combined-reference metrics changed: {checks}")
    return {
        "feature_count": reference["feature_count"],
        **actual,
        "verified": checks,
        "gate_status": source["gates"]["turn100"]["status"],
    }


def load_source(path: Path) -> dict:
    if path.resolve() != SOURCE.resolve():
        raise ValueError(f"D63b is frozen to {SOURCE}")
    source_hash = sha256_file(path)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(
            f"D63a source hash mismatch: expected {EXPECTED_SOURCE_SHA256}, got {source_hash}"
        )
    source = json.loads(path.read_text())
    if source.get("schema") != EXPECTED_SOURCE_SCHEMA:
        raise ValueError("unexpected D63a schema")
    if source.get("integrity", {}).get("confirmation_products_read") is not False:
        raise ValueError("D63a confirmation sealing assertion is absent")
    return source


def eligible_rows(source: dict) -> list[dict]:
    rows = [row for row in source["rows"] if row["turn100_eligible"]]
    if len(rows) != 150:
        raise ValueError(f"D63b expected 150 rows, got {len(rows)}")
    if Counter(row["partition"] for row in rows) != {
        "discovery": 74,
        "validation": 76,
    }:
        raise ValueError("D63b partition counts changed")
    labels = Counter(
        (row["partition"], int(row["turn100_label"])) for row in rows
    )
    expected_labels = {
        ("discovery", 0): 58,
        ("discovery", 1): 16,
        ("validation", 0): 46,
        ("validation", 1): 30,
    }
    if labels != expected_labels:
        raise ValueError(f"D63b label support changed: {labels}")
    if any(row["turn100_features"] is None for row in rows):
        raise ValueError("D63b encountered a missing eligible feature vector")
    return rows


def family_rows(rows: list[dict], family: str) -> list[dict]:
    return [
        {
            "game_id": row["game_id"],
            "agent_id": row["agent_id"],
            "partition": row["partition"],
            "label": int(row["turn100_label"]),
            "features": select_features(row["turn100_features"], family),
        }
        for row in rows
    ]


def build_report(source: dict, rows: list[dict]) -> dict:
    combined_reference = verify_reference(source)
    reports = {
        family: model_report(
            family_rows(rows, family),
            "features",
            "label",
            f"d63b_{family}",
        )
        for family in ("recipe", "snapshot", "flow")
    }
    gates = {family: gate_model_b(report) for family, report in reports.items()}
    if gates["flow"]["status"] == "pass":
        next_experiment = "prospective_state_conditioned_capitalization_value"
        minimal_sufficient_state = (
            "instantaneous_economy"
            if gates["snapshot"]["status"] == "pass"
            else "cumulative_economy_flow"
        )
    elif gates["recipe"]["status"] == "pass":
        next_experiment = "whole_recipe_or_recurrent_policy"
        minimal_sufficient_state = "worker_recipe"
    elif combined_reference["gate_status"] == "pass":
        next_experiment = "recipe_state_interaction_capitalization"
        minimal_sufficient_state = "combined_recipe_and_economy"
    else:
        next_experiment = "invalid_or_unsupported"
        minimal_sufficient_state = None
    feature_sets = {
        family: reports[family]["feature_names"]
        for family in ("recipe", "snapshot", "flow")
    }
    return {
        "schema": "troll-farm-d63b-capitalization-signal-ablation-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "no-new-data held-agent feature ablation; behavior representation only, "
            "with no value or candidate claim"
        ),
        "inputs": {
            "d63a_report": EXPECTED_SOURCE_SHA256,
            "d63b_protocol": sha256_file(PROTOCOL),
            "d63b_analyzer": sha256_file(Path(__file__)),
        },
        "integrity": {
            "source_schema": source["schema"],
            "source_hash_exact": True,
            "rows": len(rows),
            "partition_counts": dict(
                sorted(Counter(row["partition"] for row in rows).items())
            ),
            "label_counts": {
                partition: dict(
                    sorted(
                        Counter(
                            int(row["turn100_label"])
                            for row in rows
                            if row["partition"] == partition
                        ).items()
                    )
                )
                for partition in ("discovery", "validation")
            },
            "confirmation_products_read": False,
            "new_replay_reads": 0,
        },
        "feature_sets": feature_sets,
        "combined_reference": combined_reference,
        "models": reports,
        "gates": gates,
        "decision": {
            "next_experiment": next_experiment,
            "minimal_sufficient_state": minimal_sufficient_state,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def analyze(source_path: Path, output: Path) -> dict:
    source = load_source(source_path)
    report = build_report(source, eligible_rows(source))
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = analyze(args.source, args.output)
    print(
        json.dumps(
            {
                "rows": report["integrity"]["rows"],
                "gates": {
                    name: gate["status"] for name, gate in report["gates"].items()
                },
                "next": report["decision"]["next_experiment"],
                "minimal_state": report["decision"]["minimal_sufficient_state"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

