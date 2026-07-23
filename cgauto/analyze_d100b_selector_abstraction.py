#!/usr/bin/env python3
"""Post-result D100 diagnostic: how much parent-oracle value survives coarse selection?"""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
MATRIX = (
    ANALYSIS
    / "d100a-d98-anchored-pair-residual-population-a-9823000-9823007.tsv"
)
BASELINES = (
    ANALYSIS
    / "d100a-d98-anchored-pair-residual-baselines-a-9823000-9823007.tsv"
)
D100_RESULT = ANALYSIS / "d100a-d98-anchored-pair-residual-result.json"
OUTPUT = ANALYSIS / "d100b-selector-abstraction-diagnostic.json"

EXPECTED_HASHES = {
    MATRIX: "c27bacd7122ef536c084b43e3168062e1a0afcdc9308245962dc0ef307c56182",
    BASELINES: "b9cf5ffda4f853efe0441f5d72f75876dac8497bbb610bd730ce2994d828b01d",
    D100_RESULT: "3ca4e6289823e2725a985bb4854e384f534a33fcf4ed0089f09fb56fb3db98f7",
}

CONTROL = "d40_control"
PARENTS = tuple(f"parent_{index:02d}" for index in range(64))
POLICIES = (CONTROL, *PARENTS)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def task(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def mean(values) -> float:
    return float(statistics.mean(values))


def ranks(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        stop = start + 1
        while stop < len(ordered) and values[ordered[stop]] == values[ordered[start]]:
            stop += 1
        rank = (start + stop - 1) / 2.0
        for index in ordered[start:stop]:
            result[index] = rank
        start = stop
    return result


def spearman(left: list[float], right: list[float]) -> float:
    return float(statistics.correlation(ranks(left), ranks(right)))


def summarize_realized(
    tasks: list[tuple[int, int, str]],
    realized: dict[tuple[int, int, str], str],
    margins: dict[tuple[int, int, str, str], int],
    baselines: dict[tuple[int, int, str], int],
    oracle_gain: float,
) -> dict:
    deltas = [margins[(*key, realized[key])] - baselines[key] for key in tasks]
    families = defaultdict(list)
    for key, delta in zip(tasks, deltas):
        families[key[2]].append(delta)
    return {
        "mean_margin": mean(margins[(*key, realized[key])] for key in tasks),
        "paired_mean_margin_gain_vs_d40": mean(deltas),
        "task_oracle_gain_captured": mean(deltas) / oracle_gain,
        "strict_improvement_rate_vs_d40": mean(delta > 0 for delta in deltas),
        "selected_policy_count": len(set(realized.values())),
        "opponent_family_mean_margin_gains_vs_d40": {
            opponent: mean(values) for opponent, values in sorted(families.items())
        },
        "worst_opponent_family_mean_margin_gain_vs_d40": min(
            mean(values) for values in families.values()
        ),
    }


def in_sample_grouping(
    tasks: list[tuple[int, int, str]],
    fields: tuple[int, ...],
    margins: dict[tuple[int, int, str, str], int],
    baselines: dict[tuple[int, int, str], int],
    oracle_gain: float,
) -> dict:
    groups = defaultdict(list)
    for key in tasks:
        groups[tuple(key[index] for index in fields)].append(key)
    choices = {
        group: max(
            POLICIES,
            key=lambda policy: (
                mean(margins[(*key, policy)] for key in members),
                policy,
            ),
        )
        for group, members in groups.items()
    }
    realized = {
        key: choices[tuple(key[index] for index in fields)] for key in tasks
    }
    return {
        "group_count": len(groups),
        "optimism": "same outcomes choose and evaluate each grouping",
        **summarize_realized(tasks, realized, margins, baselines, oracle_gain),
    }


def leave_one_map_out(
    tasks: list[tuple[int, int, str]],
    margins: dict[tuple[int, int, str, str], int],
    baselines: dict[tuple[int, int, str], int],
    oracle_gain: float,
    by_opponent: bool,
) -> dict:
    realized = {}
    for held_seed in sorted({key[0] for key in tasks}):
        training = [key for key in tasks if key[0] != held_seed]
        held = [key for key in tasks if key[0] == held_seed]
        if by_opponent:
            choices = {}
            for opponent in sorted({key[2] for key in tasks}):
                members = [key for key in training if key[2] == opponent]
                choices[opponent] = max(
                    POLICIES,
                    key=lambda policy: (
                        mean(margins[(*key, policy)] for key in members),
                        policy,
                    ),
                )
            for key in held:
                realized[key] = choices[key[2]]
        else:
            choice = max(
                POLICIES,
                key=lambda policy: (
                    mean(margins[(*key, policy)] for key in training),
                    policy,
                ),
            )
            for key in held:
                realized[key] = choice
    return {
        "folds": len({key[0] for key in tasks}),
        "uses_opponent_identity": by_opponent,
        **summarize_realized(tasks, realized, margins, baselines, oracle_gain),
    }


def cross_seat_map_opponent(
    tasks: list[tuple[int, int, str]],
    margins: dict[tuple[int, int, str, str], int],
    baselines: dict[tuple[int, int, str], int],
    oracle_gain: float,
) -> dict:
    realized = {}
    for key in tasks:
        seed, seat, opponent = key
        opposite = (seed, 1 - seat, opponent)
        realized[key] = max(
            POLICIES,
            key=lambda policy: (margins[(*opposite, policy)], policy),
        )
    return {
        "optimism": "same map and opponent, but choice uses only the opposite seat outcome",
        **summarize_realized(tasks, realized, margins, baselines, oracle_gain),
    }


def main() -> None:
    for path, expected in EXPECTED_HASHES.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D100b prerequisite missing or changed: {path}")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D100b diagnostic")

    rows = read(MATRIX)
    baseline_rows = read(BASELINES)
    baselines = {task(row): int(row["margin"]) for row in baseline_rows}
    margins = {
        (*task(row), row["policy"]): int(row["margin"])
        for row in rows
        if row["policy"] in POLICIES
    }
    tasks = sorted(baselines)
    if len(tasks) != 128 or len(margins) != len(tasks) * len(POLICIES):
        raise RuntimeError("D100b grid mismatch")

    d40_mean = mean(baselines.values())
    oracle_mean = mean(
        max(margins[(*key, policy)] for policy in POLICIES) for key in tasks
    )
    oracle_gain = oracle_mean - d40_mean
    groupings = {
        name: in_sample_grouping(tasks, fields, margins, baselines, oracle_gain)
        for name, fields in {
            "global": (),
            "seat": (1,),
            "opponent_identity": (2,),
            "opponent_identity_and_seat": (2, 1),
            "map_seed": (0,),
            "map_seed_and_seat": (0, 1),
            "map_seed_and_opponent_identity": (0, 2),
            "full_task": (0, 1, 2),
        }.items()
    }

    seeds = sorted({key[0] for key in tasks})
    map_vectors = {
        seed: [
            mean(
                margins[(*key, policy)] - baselines[key]
                for key in tasks
                if key[0] == seed
            )
            for policy in PARENTS
        ]
        for seed in seeds
    }
    map_correlations = [
        spearman(map_vectors[left], map_vectors[right])
        for left_index, left in enumerate(seeds)
        for right in seeds[left_index + 1 :]
    ]
    seat_correlations = []
    for seed in seeds:
        for opponent in sorted({key[2] for key in tasks}):
            vectors = [
                [
                    margins[(seed, seat, opponent, policy)]
                    - baselines[(seed, seat, opponent)]
                    for policy in PARENTS
                ]
                for seat in (0, 1)
            ]
            seat_correlations.append(spearman(*vectors))

    result = {
        "scope": (
            "post-result consumed-map diagnosis only; every grouping except held folds is an "
            "optimistic hindsight ceiling and no policy is selectable"
        ),
        "inputs": {str(path): sha256(path) for path in EXPECTED_HASHES},
        "tasks": len(tasks),
        "policies": len(POLICIES),
        "d40_mean_margin": d40_mean,
        "parent_task_oracle_mean_margin": oracle_mean,
        "parent_task_oracle_gain_vs_d40": oracle_gain,
        "in_sample_groupings": groupings,
        "held_selection": {
            "leave_one_map_out_global": leave_one_map_out(
                tasks, margins, baselines, oracle_gain, False
            ),
            "leave_one_map_out_opponent_identity": leave_one_map_out(
                tasks, margins, baselines, oracle_gain, True
            ),
            "cross_seat_map_and_opponent_identity": cross_seat_map_opponent(
                tasks, margins, baselines, oracle_gain
            ),
        },
        "policy_order_stability": {
            "map_pair_spearman_mean": mean(map_correlations),
            "map_pair_spearman_minimum": min(map_correlations),
            "map_pair_spearman_maximum": max(map_correlations),
            "same_map_opponent_cross_seat_spearman_mean": mean(seat_correlations),
            "same_map_opponent_cross_seat_spearman_minimum": min(seat_correlations),
            "same_map_opponent_cross_seat_spearman_maximum": max(seat_correlations),
        },
        "conclusion": (
            "most parent-oracle value is task-specific and unstable; static map, seat, or "
            "opponent-family selection is not the next representation"
        ),
        "analyzer_sha256": sha256(Path(__file__)),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
