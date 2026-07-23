#!/usr/bin/env python3
"""Analyze conservative resident-gated D11 action overrides."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d11_recipe_catalog_analysis import summary  # noqa: E402

CONTROL = "resident"
POLICIES = [
    CONTROL,
    "native_second_idle_only",
    "native_second_crop_local",
    "native_second_productive_local",
    "native_starter_crop_local",
    "native_all_productive_local",
]
SAFETY_ORDER = POLICIES[1:]
NUMERIC_FIELDS = {
    "seed",
    "seat",
    "adopt_worker",
    "recipe",
    "fallback_turn",
    "ms",
    "cc",
    "hp",
    "chop",
    "score",
    "opponent_score",
    "margin",
    "wood",
    "opponent_wood",
    "wood_edge",
    "terminal_turn",
    "workers",
    "opponent_workers",
    "trained_ms",
    "trained_cc",
    "trained_hp",
    "trained_chop",
    "train_commands",
    "plant_commands",
    "harvest_commands",
    "chop_commands",
    "drop_commands",
    "move_commands",
    "shadow_decisions",
    "exact_agreements",
    "verb_agreements",
    "resident_wait_actor_action",
    "actor_local_resident_transit",
    "overrides",
    "elapsed_us",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field in NUMERIC_FIELDS & row.keys():
            row[field] = int(row[field])
    return rows


def grouped_mean(rows: list[dict], key_fields: tuple[str, ...], value) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in key_fields)].append(value(row))
    return {key: statistics.mean(values) for key, values in groups.items()}


def validate(rows: list[dict]) -> tuple[list[int], list[str]]:
    if not rows:
        raise ValueError("advisory layer catalog is empty")
    seeds = sorted({row["seed"] for row in rows})
    opponents = sorted({row["opponent"] for row in rows})
    observed_policies = {row["policy"] for row in rows}
    if observed_policies != set(POLICIES):
        raise ValueError("advisory policy set does not match the frozen catalog")
    expected = {
        (seed, seat, opponent, policy)
        for seed in seeds
        for seat in range(2)
        for opponent in opponents
        for policy in POLICIES
    }
    observed = {
        (row["seed"], row["seat"], row["opponent"], row["policy"])
        for row in rows
    }
    if expected != observed or len(rows) != len(expected):
        raise ValueError(
            f"incomplete advisory catalog: rows={len(rows)}, expected={len(expected)}"
        )
    if any(
        row["adopt_worker"] != int(row["policy"] != CONTROL) for row in rows
    ):
        raise ValueError("worker-adoption flag does not match advisory policy")
    return seeds, opponents


def analyze(rows: list[dict], input_path: Path) -> dict:
    seeds, opponents = validate(rows)
    by_cell = {
        (row["seed"], row["seat"], row["opponent"], row["policy"]): row
        for row in rows
    }
    map_margin = grouped_mean(rows, ("seed", "policy"), lambda row: row["margin"])
    per_policy = {}
    eligible = []
    for policy in POLICIES:
        policy_rows = [row for row in rows if row["policy"] == policy]
        deltas = []
        wood_deltas = []
        worker_matches = []
        activated_deltas = []
        action_deltas = defaultdict(list)
        for row in policy_rows:
            control = by_cell[
                (row["seed"], row["seat"], row["opponent"], CONTROL)
            ]
            delta = row["margin"] - control["margin"]
            deltas.append(delta)
            wood_deltas.append(row["wood_edge"] - control["wood_edge"])
            worker_matches.append(row["workers"] == control["workers"])
            if row["overrides"] > 0:
                activated_deltas.append(delta)
            for field in (
                "plant_commands",
                "harvest_commands",
                "chop_commands",
                "drop_commands",
                "move_commands",
            ):
                action_deltas[field].append(row[field] - control[field])
        map_deltas = [
            map_margin[(seed, policy)] - map_margin[(seed, CONTROL)]
            for seed in seeds
        ]
        opponent_deltas = {}
        for opponent in opponents:
            opponent_rows = [
                row for row in policy_rows if row["opponent"] == opponent
            ]
            opponent_deltas[opponent] = statistics.mean(
                row["margin"]
                - by_cell[
                    (row["seed"], row["seat"], opponent, CONTROL)
                ]["margin"]
                for row in opponent_rows
            )
        total_shadow = sum(row["shadow_decisions"] for row in policy_rows)
        total_overrides = sum(row["overrides"] for row in policy_rows)
        activated_cells = sum(row["overrides"] > 0 for row in policy_rows)
        map_delta_summary = summary(map_deltas)
        cell_delta_summary = summary(deltas)
        activated_summary = summary(activated_deltas)
        override_rate = total_overrides / total_shadow if total_shadow else 0
        gates = {
            "resident_worker_count_retained": all(worker_matches),
            "at_least_10_activated_cells": activated_cells >= 10,
            "override_rate_between_1_and_20_percent": 0.01 <= override_rate <= 0.20,
            "map_mean_delta_at_least_2": map_delta_summary["mean"] >= 2,
            "map_ci95_lower_nonnegative": map_delta_summary["ci95_normal"][0] >= 0,
            "worst_opponent_mean_at_least_minus2": min(opponent_deltas.values()) >= -2,
            "worst_decile_cell_delta_at_least_minus10": cell_delta_summary[
                "worst_decile_mean"
            ]
            >= -10,
            "resident_opponent_mean_nonnegative": opponent_deltas.get(
                "resident", float("-inf")
            )
            >= 0,
            "activated_cell_mean_positive": activated_summary["mean"] is not None
            and activated_summary["mean"] > 0,
        }
        is_eligible = policy != CONTROL and all(gates.values())
        if is_eligible:
            eligible.append(policy)
        per_policy[policy] = {
            "game_margin": summary(row["margin"] for row in policy_rows),
            "cell_margin_delta_vs_resident": cell_delta_summary,
            "cell_wood_delta_vs_resident": summary(wood_deltas),
            "map_balanced_margin_delta_vs_resident": map_delta_summary,
            "opponent_mean_margin_delta_vs_resident": opponent_deltas,
            "worst_opponent_mean_margin_delta_vs_resident": min(
                opponent_deltas.values()
            ),
            "resident_opponent_mean_margin_delta": opponent_deltas.get("resident"),
            "worker_count_matches": {
                "matches": sum(worker_matches),
                "games": len(worker_matches),
                "rate": statistics.mean(worker_matches),
            },
            "shadow": {
                "decisions": total_shadow,
                "exact_agreements": sum(
                    row["exact_agreements"] for row in policy_rows
                ),
                "verb_agreements": sum(row["verb_agreements"] for row in policy_rows),
                "resident_wait_actor_action": sum(
                    row["resident_wait_actor_action"] for row in policy_rows
                ),
                "actor_local_resident_transit": sum(
                    row["actor_local_resident_transit"] for row in policy_rows
                ),
            },
            "activation": {
                "overrides": total_overrides,
                "override_rate": override_rate,
                "activated_cells": activated_cells,
                "activated_cell_delta": activated_summary,
            },
            "mean_action_delta_vs_resident": {
                field: statistics.mean(values)
                for field, values in sorted(action_deltas.items())
            },
            "gates": gates,
            "eligible": is_eligible,
        }

    selected = None
    if eligible:
        maximum = max(
            per_policy[policy]["map_balanced_margin_delta_vs_resident"]["mean"]
            for policy in eligible
        )
        near = [
            policy
            for policy in eligible
            if per_policy[policy]["map_balanced_margin_delta_vs_resident"]["mean"]
            >= maximum - 1
        ]
        selected = min(
            near,
            key=lambda policy: (
                per_policy[policy]["activation"]["overrides"],
                SAFETY_ORDER.index(policy),
            ),
        )

    return {
        "schema": 1,
        "scope": (
            "resident-gated D11 local-action advisory development catalog on reused "
            "seeds; exact paired engine outcomes; not Arena-calibrated"
        ),
        "source": {
            "rows": str(input_path),
            "rows_sha256": sha256(input_path),
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "seeds": seeds,
            "opponents": opponents,
            "seats": [0, 1],
            "policies": POLICIES,
            "games": len(rows),
            "complete": True,
        },
        "per_policy": per_policy,
        "selection": {
            "eligible_policies": eligible,
            "selected_policy": selected,
            "rule": (
                "all nine frozen gates; maximize map mean; within one point minimize "
                "overrides then apply frozen nested safety order"
            ),
            "authorization": (
                "development only; a selected policy requires disjoint prospective "
                "validation before candidate construction"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rows", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = analyze(read_rows(args.rows), args.rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "games": result["design"]["games"],
                "eligible_policies": result["selection"]["eligible_policies"],
                "selected_policy": result["selection"]["selected_policy"],
                "ranking": [
                    {
                        "policy": policy,
                        "mean_delta": values[
                            "map_balanced_margin_delta_vs_resident"
                        ]["mean"],
                        "ci95_lower": values[
                            "map_balanced_margin_delta_vs_resident"
                        ]["ci95_normal"][0],
                        "worst_opponent": values[
                            "worst_opponent_mean_margin_delta_vs_resident"
                        ],
                        "overrides": values["activation"]["overrides"],
                        "activated_cells": values["activation"]["activated_cells"],
                        "eligible": values["eligible"],
                    }
                    for policy, values in result["per_policy"].items()
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
