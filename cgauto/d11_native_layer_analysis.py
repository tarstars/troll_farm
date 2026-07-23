#!/usr/bin/env python3
"""Analyze paired resident-native D11 tactical-layer outcomes."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
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
EXPECTED_POLICIES = {
    CONTROL,
    "native_actor_all",
    "native_resident_starter_actor_second",
    "native_actor_starter_resident_second",
}
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
        raise ValueError("native layer catalog is empty")
    seeds = sorted({row["seed"] for row in rows})
    opponents = sorted({row["opponent"] for row in rows})
    policies = {row["policy"] for row in rows}
    if policies != EXPECTED_POLICIES:
        raise ValueError(
            f"policy mismatch: observed={sorted(policies)}, expected={sorted(EXPECTED_POLICIES)}"
        )
    expected = {
        (seed, seat, opponent, policy)
        for seed in seeds
        for seat in range(2)
        for opponent in opponents
        for policy in EXPECTED_POLICIES
    }
    observed = {
        (row["seed"], row["seat"], row["opponent"], row["policy"])
        for row in rows
    }
    if expected != observed or len(rows) != len(expected):
        raise ValueError(
            f"incomplete native layer catalog: rows={len(rows)}, expected={len(expected)}"
        )
    if any(
        row["adopt_worker"] != int(row["policy"] != CONTROL) for row in rows
    ):
        raise ValueError("worker-adoption flag does not match policy")
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
    for policy in sorted(EXPECTED_POLICIES):
        policy_rows = [row for row in rows if row["policy"] == policy]
        deltas = []
        wood_deltas = []
        worker_matches = []
        action_deltas = defaultdict(list)
        for row in policy_rows:
            control = by_cell[
                (row["seed"], row["seat"], row["opponent"], CONTROL)
            ]
            deltas.append(row["margin"] - control["margin"])
            wood_deltas.append(row["wood_edge"] - control["wood_edge"])
            worker_matches.append(row["workers"] == control["workers"])
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
        specs = Counter(
            (
                row["trained_ms"],
                row["trained_cc"],
                row["trained_hp"],
                row["trained_chop"],
            )
            if row["workers"] >= 2
            else None
            for row in policy_rows
        )
        map_delta_summary = summary(map_deltas)
        cell_delta_summary = summary(deltas)
        gates = {
            "resident_worker_count_retained": all(worker_matches),
            "map_mean_delta_at_least_5": map_delta_summary["mean"] >= 5,
            "map_ci95_lower_nonnegative": map_delta_summary["ci95_normal"][0] >= 0,
            "worst_opponent_mean_at_least_minus5": min(opponent_deltas.values()) >= -5,
            "worst_decile_cell_delta_at_least_minus20": cell_delta_summary[
                "worst_decile_mean"
            ]
            >= -20,
            "resident_opponent_mean_nonnegative": opponent_deltas.get(
                "resident", float("-inf")
            )
            >= 0,
        }
        is_eligible = policy != CONTROL and all(gates.values())
        if is_eligible:
            eligible.append(policy)
        per_policy[policy] = {
            "game_margin": summary(row["margin"] for row in policy_rows),
            "game_wood_edge": summary(row["wood_edge"] for row in policy_rows),
            "cell_margin_delta_vs_resident": cell_delta_summary,
            "cell_wood_delta_vs_resident": summary(wood_deltas),
            "map_balanced_margin": summary(
                map_margin[(seed, policy)] for seed in seeds
            ),
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
            "final_worker_specs": {
                ("none" if spec is None else "/".join(map(str, spec))): count
                for spec, count in sorted(specs.items(), key=lambda item: str(item[0]))
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
        one_worker = [policy for policy in near if policy != "native_actor_all"]
        if one_worker:
            near = one_worker
        priority = [
            "native_actor_starter_resident_second",
            "native_resident_starter_actor_second",
            "native_actor_all",
        ]
        selected = min(near, key=priority.index)

    return {
        "schema": 1,
        "scope": (
            "resident-native PPO tactical layer development catalog on reused seeds; "
            "exact paired engine outcomes; not Arena-calibrated"
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
            "policies": sorted(EXPECTED_POLICIES),
            "games": len(rows),
            "complete": True,
        },
        "per_policy": per_policy,
        "selection": {
            "eligible_policies": eligible,
            "selected_policy": selected,
            "rule": (
                "all six frozen gates; maximize map-balanced delta; within one point "
                "prefer one-worker PPO, then actor-starter/resident-second"
            ),
            "authorization": (
                "development evidence only; a selected policy requires a frozen disjoint "
                "prospective protocol before candidate construction"
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
