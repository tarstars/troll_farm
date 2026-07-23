#!/usr/bin/env python3
"""Evaluate complete policies against a frozen, diverse opponent league.

Every policy/opponent/seed cell contains two deterministic games with seats
swapped.  Results are paired against the exact live policy on the same map and
opponent; this is an offline research discriminator, not an arena predictor.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source, run_match  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

SUBMISSIONS = REPO / "cgauto/submissions"
POLICY_SOURCES = {
    "live": SUBMISSIONS / "agent-6553250-yamo-orchard-live.min.rs",
    "preseed": SUBMISSIONS / "candidate-agent6553250-preseed-low-supply.min.rs",
    "geometry": SUBMISSIONS
    / "candidate-agent6553250-secure-orchard-coverage.min.rs",
    "stack": SUBMISSIONS / "candidate-agent6553250-preseed-orchard-coverage.min.rs",
}
OPPONENT_SOURCES = {
    "motion": SUBMISSIONS / "v1.20.0-motion.min.rs",
    "taskplan": SUBMISSIONS / "v1.27.0-taskplan.min.rs",
    "race": SUBMISSIONS / "v1.36.0-race.min.rs",
    "yield": SUBMISSIONS / "v1.43.0-yield.min.rs",
    "ringfix3": SUBMISSIONS / "v1.59.0-ringfix3.min.rs",
    "chopharvest": SUBMISSIONS / "v1.61.0-chopharvest.min.rs",
}


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_seeds(seed_start: int, seed_count: int, seed_list: str | None) -> list[int]:
    """Resolve either one contiguous range or an explicit sparse discovery block."""

    if seed_list is None:
        if seed_count <= 0:
            raise ValueError("seed count must be positive")
        return list(range(seed_start, seed_start + seed_count))
    try:
        seeds = [int(value.strip()) for value in seed_list.split(",") if value.strip()]
    except ValueError as error:
        raise ValueError("seed list must contain comma-separated integers") from error
    if not seeds:
        raise ValueError("seed list must not be empty")
    if any(seed < 0 for seed in seeds):
        raise ValueError("seeds must be non-negative")
    if len(seeds) != len(set(seeds)):
        raise ValueError("seed list must not contain duplicates")
    return seeds


def map_features(game) -> dict[str, float]:
    """Seat-invariant features observable before the first command."""

    type_counts = Counter(plant.type for plant in game.plants)
    fruit_counts = Counter()
    for plant in game.plants:
        fruit_counts[plant.type] += plant.fruits
    all_distances = [
        min(
            abs(plant.x - shack[0]) + abs(plant.y - shack[1])
            for shack in game.shacks
        )
        for plant in game.plants
    ]
    water_adjacent = sum(
        any(abs(plant.x - x) + abs(plant.y - y) == 1 for x, y in game.water)
        for plant in game.plants
    )
    features: dict[str, float] = {
        "tree_count": len(game.plants),
        "ripe_tree_count": sum(plant.fruits > 0 for plant in game.plants),
        "initial_fruit_total": sum(plant.fruits for plant in game.plants),
        "water_adjacent_tree_count": water_adjacent,
        "mean_nearest_shack_tree_distance": (
            statistics.mean(all_distances) if all_distances else 0.0
        ),
        "max_nearest_shack_tree_distance": max(all_distances, default=0),
        "shack_manhattan_distance": abs(game.shacks[0][0] - game.shacks[1][0])
        + abs(game.shacks[0][1] - game.shacks[1][1]),
        "walkable_count": len(game.walkable),
        "initial_plum": game.inventories[0][0],
        "initial_lemon": game.inventories[0][1],
        "initial_apple": game.inventories[0][2],
        "initial_banana": game.inventories[0][3],
        "initial_iron": game.inventories[0][4],
    }
    for kind in ("PLUM", "LEMON", "APPLE", "BANANA"):
        features[f"{kind.lower()}_tree_count"] = type_counts[kind]
        features[f"{kind.lower()}_fruit_count"] = fruit_counts[kind]
    return features


def combine_counts(first: dict, second: dict) -> dict:
    combined = Counter(first)
    combined.update(second)
    return dict(sorted(combined.items()))


def paired_row(seed: int, initial, policy_name: str, opponent_name: str, policy, opponent) -> dict:
    first = run_match(copy.deepcopy(initial), policy, opponent)
    second = run_match(copy.deepcopy(initial), opponent, policy)
    margins = [
        first["scores"][0] - first["scores"][1],
        second["scores"][1] - second["scores"][0],
    ]
    wood_edges = [
        first["inventories"][0][5] - first["inventories"][1][5],
        second["inventories"][1][5] - second["inventories"][0][5],
    ]
    return {
        "seed": seed,
        "policy": policy_name,
        "opponent": opponent_name,
        "seat_margins": margins,
        "paired_margin": statistics.mean(margins),
        "seat_wood_edges": wood_edges,
        "paired_wood_edge": statistics.mean(wood_edges),
        "policy_scores": [first["scores"][0], second["scores"][1]],
        "opponent_scores": [first["scores"][1], second["scores"][0]],
        "policy_wood": [first["inventories"][0][5], second["inventories"][1][5]],
        "opponent_wood": [first["inventories"][1][5], second["inventories"][0][5]],
        "policy_command_counts": combine_counts(
            first["command_counts"][0], second["command_counts"][1]
        ),
        "opponent_command_counts": combine_counts(
            first["command_counts"][1], second["command_counts"][0]
        ),
        "terminal_turns": [first["terminal_turn"], second["terminal_turn"]],
    }


def robust_summary(values) -> dict:
    values = list(values)
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "trimmed_5pct_mean": None,
            "standard_deviation": None,
            "standard_error": None,
            "ci95_normal": [None, None],
            "worst_decile_mean": None,
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "minimum": None,
            "maximum": None,
        }
    ordered = sorted(values)
    trim = math.floor(0.05 * len(ordered))
    trimmed = ordered[trim : len(ordered) - trim] if trim else ordered
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    se = sd / math.sqrt(len(values))
    worst_n = max(1, math.ceil(0.10 * len(ordered)))
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "trimmed_5pct_mean": statistics.mean(trimmed),
        "standard_deviation": sd,
        "standard_error": se,
        "ci95_normal": [mean - 1.96 * se, mean + 1.96 * se],
        "worst_decile_mean": statistics.mean(ordered[:worst_n]),
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
        "minimum": ordered[0],
        "maximum": ordered[-1],
    }


def attach_live_deltas(rows: list[dict]) -> None:
    live = {
        (row["opponent"], row["seed"]): row
        for row in rows
        if row["policy"] == "live"
    }
    for row in rows:
        control = live[(row["opponent"], row["seed"])]
        row["delta_vs_live_margin"] = row["paired_margin"] - control["paired_margin"]
        row["delta_vs_live_wood"] = (
            row["paired_wood_edge"] - control["paired_wood_edge"]
        )


def aggregate(rows: list[dict]) -> dict:
    policies = sorted({row["policy"] for row in rows})
    opponents = sorted({row["opponent"] for row in rows})
    by_policy_opponent = {}
    by_policy = {}
    for policy in policies:
        policy_rows = [row for row in rows if row["policy"] == policy]
        seed_values = {}
        for row in policy_rows:
            seed_values.setdefault(row["seed"], []).append(row["delta_vs_live_margin"])
        by_policy[policy] = {
            "absolute_margin": robust_summary(row["paired_margin"] for row in policy_rows),
            "delta_vs_live_margin": robust_summary(
                row["delta_vs_live_margin"] for row in policy_rows
            ),
            "seed_balanced_delta_vs_live_margin": robust_summary(
                statistics.mean(values) for values in seed_values.values()
            ),
            "delta_vs_live_wood": robust_summary(
                row["delta_vs_live_wood"] for row in policy_rows
            ),
        }
        opponent_means = {}
        for opponent in opponents:
            cell = [
                row
                for row in policy_rows
                if row["opponent"] == opponent
            ]
            key = f"{policy}__vs__{opponent}"
            by_policy_opponent[key] = {
                "absolute_margin": robust_summary(row["paired_margin"] for row in cell),
                "delta_vs_live_margin": robust_summary(
                    row["delta_vs_live_margin"] for row in cell
                ),
                "delta_vs_live_wood": robust_summary(
                    row["delta_vs_live_wood"] for row in cell
                ),
            }
            opponent_means[opponent] = by_policy_opponent[key]["delta_vs_live_margin"][
                "mean"
            ]
        by_policy[policy]["opponent_mean_deltas"] = opponent_means
        by_policy[policy]["worst_opponent"] = min(
            opponent_means, key=opponent_means.get
        )
        by_policy[policy]["worst_opponent_mean_delta"] = min(opponent_means.values())
    return {
        "by_policy": by_policy,
        "by_policy_opponent": by_policy_opponent,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=60)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument(
        "--seed-list",
        help="comma-separated sparse seed registry; overrides --seeds and --seed-start",
    )
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--extra-policy",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="register an additional complete-policy source",
    )
    parser.add_argument(
        "--policy-names",
        default=",".join(POLICY_SOURCES),
        help="comma-separated registered policies to evaluate (must include live)",
    )
    parser.add_argument(
        "--opponent-names",
        default=",".join(OPPONENT_SOURCES),
        help="comma-separated frozen opponents to evaluate",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/offline-policy-league-2026-07-16.json",
    )
    args = parser.parse_args()
    try:
        seeds = resolve_seeds(args.seed_start, args.seeds, args.seed_list)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    policy_sources = dict(POLICY_SOURCES)
    for value in args.extra_policy:
        if "=" not in value:
            raise SystemExit("--extra-policy must be NAME=PATH")
        name, raw_path = value.split("=", 1)
        path = Path(raw_path)
        if not path.is_absolute():
            path = REPO / path
        policy_sources[name] = path
    selected_names = [name for name in args.policy_names.split(",") if name]
    if "live" not in selected_names:
        raise SystemExit("--policy-names must include live for paired deltas")
    unknown = [name for name in selected_names if name not in policy_sources]
    if unknown:
        raise SystemExit("unknown policy names: " + ", ".join(unknown))
    policy_sources = {name: policy_sources[name] for name in selected_names}
    selected_opponents = [name for name in args.opponent_names.split(",") if name]
    unknown_opponents = [
        name for name in selected_opponents if name not in OPPONENT_SOURCES
    ]
    if unknown_opponents:
        raise SystemExit("unknown opponent names: " + ", ".join(unknown_opponents))
    if not selected_opponents:
        raise SystemExit("--opponent-names must select at least one opponent")
    opponent_sources = {
        name: OPPONENT_SOURCES[name] for name in selected_opponents
    }
    sources = {**policy_sources, **opponent_sources}
    missing = [str(path) for path in sources.values() if not path.exists()]
    if missing:
        raise SystemExit("missing sources: " + ", ".join(missing))

    games = {seed: generate_bronze(seed) for seed in seeds}
    features = {str(seed): map_features(game) for seed, game in games.items()}
    rows = []
    with tempfile.TemporaryDirectory(prefix="offline-policy-league-") as directory:
        temp = Path(directory)
        binaries = {}
        for index, (name, source) in enumerate(sources.items()):
            binary = temp / name
            compile_source(source, binary, f"league_{index}_{name}")
            binaries[name] = binary
        print(f"compiled {len(binaries)} frozen policies", flush=True)

        tasks = [
            (seed, policy, opponent)
            for seed in seeds
            for policy in policy_sources
            for opponent in opponent_sources
        ]
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    paired_row,
                    seed,
                    games[seed],
                    policy,
                    opponent,
                    binaries[policy],
                    binaries[opponent],
                ): (seed, policy, opponent)
                for seed, policy, opponent in tasks
            }
            for completed, future in enumerate(as_completed(futures), 1):
                rows.append(future.result())
                if completed % 25 == 0 or completed == len(tasks):
                    print(f"completed {completed}/{len(tasks)} paired cells", flush=True)

    rows.sort(key=lambda row: (row["seed"], row["policy"], row["opponent"]))
    attach_live_deltas(rows)
    payload = {
        "schema": 1,
        "scope": (
            "deterministic corrected local simulator; common seeds and both seats; "
            "offline discriminator, not an arena predictor"
        ),
        "seed_start": args.seed_start if args.seed_list is None else None,
        "seeds": len(seeds),
        "seed_values": seeds,
        "jobs": args.jobs,
        "policies": {
            name: {
                "source": str(path.relative_to(REPO)),
                "sha256": source_sha256(path),
            }
            for name, path in policy_sources.items()
        },
        "opponents": {
            name: {
                "source": str(path.relative_to(REPO)),
                "sha256": source_sha256(path),
            }
            for name, path in opponent_sources.items()
        },
        "map_features": features,
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"]["by_policy"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
