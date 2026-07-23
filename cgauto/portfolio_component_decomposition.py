#!/usr/bin/env python3
"""Diagnose which stack component creates prospective gains and tail losses."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ProcessPoolExecutor
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

from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.offline_policy_league import (  # noqa: E402
    map_features,
    OPPONENT_SOURCES,
    paired_row,
    robust_summary,
    source_sha256,
)
from cgauto.portfolio_candidate_study import compare_branch_row  # noqa: E402
from cgauto.portfolio_prospective_gate import (  # noqa: E402
    CANDIDATE_SHA256,
    DETERMINISTIC_OPPONENTS,
    save,
    same_outcome_protocol,
    SEED_START,
    SEEDS,
    THRESHOLD,
)
from sim.mapgen import generate_bronze  # noqa: E402

SUBMISSIONS = REPO / "cgauto/submissions"
POLICIES = {
    "preseed": SUBMISSIONS / "candidate-agent6553250-preseed-low-supply.min.rs",
    "geometry": SUBMISSIONS / "candidate-agent6553250-secure-orchard-coverage.min.rs",
    "stack_parent": SUBMISSIONS
    / "candidate-agent6553250-preseed-orchard-coverage.min.rs",
}
EXPECTED_POLICY_SHA256 = {
    "preseed": "6bc52f199f79cf891fcd3a0a3745b43dbf67485581c7baa6194505f9a36e7397",
    "geometry": "3e045b7b09f49b2f707382e769f81e779b4d2a6762fa193915ebd938d8e0bea7",
    "stack_parent": "da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9",
}


def protocol(input_path: Path, jobs: int) -> dict:
    return {
        "input_sha256": source_sha256(input_path),
        "seed_start": SEED_START,
        "seeds": SEEDS,
        "portfolio_threshold": THRESHOLD,
        "jobs": jobs,
        "policies": {name: source_sha256(path) for name, path in POLICIES.items()},
        "opponents": {
            name: source_sha256(OPPONENT_SOURCES[name])
            for name in DETERMINISTIC_OPPONENTS
        },
    }


def summarize(values) -> dict:
    values = list(values)
    result = robust_summary(values)
    result["mean_without_largest"] = (
        statistics.mean(sorted(values)[:-1]) if len(values) > 1 else None
    )
    return result


def decomposition_record(
    seed: int,
    opponent: str,
    stack_delta: float,
    preseed_delta: float,
    geometry_delta: float,
) -> dict:
    return {
        "seed": seed,
        "opponent": opponent,
        "stack_delta": stack_delta,
        "preseed_delta": preseed_delta,
        "geometry_delta": geometry_delta,
        "additive_prediction": preseed_delta + geometry_delta,
        "interaction": stack_delta - preseed_delta - geometry_delta,
    }


def seed_balanced(records: list[dict], field: str, seeds: set[int] | None = None) -> list[float]:
    grouped = {}
    for row in records:
        if seeds is not None and row["seed"] not in seeds:
            continue
        grouped.setdefault(row["seed"], []).append(row[field])
    return [statistics.mean(grouped[seed]) for seed in sorted(grouped)]


def component_summary(records: list[dict], seeds: set[int] | None = None) -> dict:
    return {
        field: summarize(seed_balanced(records, field, seeds))
        for field in (
            "stack_delta",
            "preseed_delta",
            "geometry_delta",
            "interaction",
        )
    }


def interaction_equivalence(records: list[dict]) -> dict:
    exact = sum(math.isclose(row["interaction"], 0.0, abs_tol=1e-12) for row in records)
    return {
        "cells": len(records),
        "exact_additive_cells": exact,
        "nonadditive_cells": len(records) - exact,
        "mean_interaction": statistics.mean(row["interaction"] for row in records),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-prospective-gate-2026-07-16.json",
    )
    parser.add_argument("--jobs", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-component-decomposition-2026-07-16.json",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-component-decomposition-2026-07-16.checkpoint.json",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 20:
        raise SystemExit("--jobs must be between 1 and 20")
    for name, expected in EXPECTED_POLICY_SHA256.items():
        actual = source_sha256(POLICIES[name])
        if actual != expected:
            raise SystemExit(f"{name} checksum changed: {actual}")

    prospective = json.loads(args.input.read_text())
    if prospective["candidate"]["sha256"] != CANDIDATE_SHA256:
        raise SystemExit("prospective input is not the frozen banana-5 candidate")
    features = {int(seed): row for seed, row in prospective["map_features"].items()}
    low_seeds = {
        seed for seed, row in features.items() if row["banana_fruit_count"] <= THRESHOLD
    }
    games = {seed: generate_bronze(seed) for seed in low_seeds}
    frozen_protocol = protocol(args.input, args.jobs)
    expected_keys = {
        (seed, policy, opponent)
        for seed in low_seeds
        for policy in POLICIES
        for opponent in DETERMINISTIC_OPPONENTS
    }
    rows = []
    worker_history = [args.jobs]
    if args.checkpoint.exists():
        checkpoint = json.loads(args.checkpoint.read_text())
        if not same_outcome_protocol(checkpoint["protocol"], frozen_protocol):
            raise SystemExit("checkpoint protocol differs from this diagnostic")
        rows = checkpoint["rows"]
        worker_history = checkpoint.get(
            "worker_history", [checkpoint["protocol"]["jobs"]]
        )
        if worker_history[-1] != args.jobs:
            worker_history.append(args.jobs)
        print(f"resuming from {len(rows)}/{len(expected_keys)} paired cells", flush=True)
    completed_keys = {(row["seed"], row["policy"], row["opponent"]) for row in rows}
    if not completed_keys <= expected_keys:
        raise SystemExit("checkpoint contains cells outside this diagnostic")

    with tempfile.TemporaryDirectory(prefix="portfolio-components-") as directory:
        temp = Path(directory)
        sources = {**POLICIES}
        sources.update(
            {name: OPPONENT_SOURCES[name] for name in DETERMINISTIC_OPPONENTS}
        )
        binaries = {}
        for index, (name, source) in enumerate(sources.items()):
            binary = temp / name
            compile_source(source, binary, f"portfolio_component_{index}_{name}")
            binaries[name] = binary
        print(f"compiled {len(binaries)} frozen sources", flush=True)
        tasks = sorted(expected_keys - completed_keys)
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
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
            for future in as_completed(futures):
                rows.append(future.result())
                completed = len(rows)
                if completed % 25 == 0 or completed == len(expected_keys):
                    print(f"completed {completed}/{len(expected_keys)} paired cells", flush=True)
                if completed % 50 == 0:
                    save(
                        args.checkpoint,
                        {
                            "protocol": frozen_protocol,
                            "worker_history": worker_history,
                            "rows": rows,
                        },
                    )

    rows.sort(key=lambda row: (row["seed"], row["policy"], row["opponent"]))
    controls = {
        (row["seed"], row["opponent"]): row
        for row in prospective["rows"]
        if row["policy"] == "live" and row["seed"] in low_seeds
    }
    portfolio = {
        (row["seed"], row["opponent"]): row
        for row in prospective["rows"]
        if row["policy"] == "portfolio" and row["seed"] in low_seeds
    }
    indexed = {(row["seed"], row["policy"], row["opponent"]): row for row in rows}
    parent_mismatches = []
    records = []
    for seed in sorted(low_seeds):
        for opponent in DETERMINISTIC_OPPONENTS:
            key = (seed, opponent)
            control = controls[key]
            stack = portfolio[key]
            parent = indexed[(seed, "stack_parent", opponent)]
            fields = compare_branch_row(parent, stack)
            if fields:
                parent_mismatches.append(
                    {"seed": seed, "opponent": opponent, "mismatch_fields": fields}
                )
            deltas = {}
            for policy in ("preseed", "geometry"):
                row = indexed[(seed, policy, opponent)]
                deltas[policy] = row["paired_margin"] - control["paired_margin"]
            records.append(
                decomposition_record(
                    seed,
                    opponent,
                    stack["delta_vs_live_margin"],
                    deltas["preseed"],
                    deltas["geometry"],
                )
            )

    stack_seed_values = dict(
        zip(sorted(low_seeds), seed_balanced(records, "stack_delta"))
    )
    tail_count = math.ceil(0.10 * len(low_seeds))
    tail_seeds = set(sorted(low_seeds, key=stack_seed_values.get)[:tail_count])
    by_banana = {}
    for fruit in sorted({features[seed]["banana_fruit_count"] for seed in low_seeds}):
        bin_seeds = {
            seed for seed in low_seeds if features[seed]["banana_fruit_count"] == fruit
        }
        by_banana[str(fruit)] = {
            "seed_count": len(bin_seeds),
            "components": component_summary(records, bin_seeds),
        }
    by_opponent = {
        opponent: {
            field: summarize(
                row[field] for row in records if row["opponent"] == opponent
            )
            for field in (
                "stack_delta",
                "preseed_delta",
                "geometry_delta",
                "interaction",
            )
        }
        for opponent in DETERMINISTIC_OPPONENTS
    }
    result = {
        "schema": 1,
        "scope": "post-outcome component and tail diagnosis; not a promotion estimate",
        "protocol": frozen_protocol,
        "worker_history": worker_history,
        "branch_seed_count": len(low_seeds),
        "stack_parent_equivalence": {
            "cells": len(portfolio),
            "exact_cells": len(portfolio) - len(parent_mismatches),
            "mismatch_cells": len(parent_mismatches),
            "passed": not parent_mismatches,
            "mismatches": parent_mismatches[:20],
        },
        "all_low_banana": component_summary(records),
        "by_banana_fruit_count": by_banana,
        "by_opponent": by_opponent,
        "interaction_equivalence": interaction_equivalence(records),
        "stack_bottom_decile": {
            "seed_count": len(tail_seeds),
            "seeds": sorted(tail_seeds),
            "components": component_summary(records, tail_seeds),
        },
        "records": records,
        "rows": rows,
    }
    save(args.output, result)
    if args.checkpoint.exists():
        args.checkpoint.unlink()
    print(
        json.dumps(
            {
                "stack_parent_equivalence": result["stack_parent_equivalence"],
                "all_low_banana": result["all_low_banana"],
                "by_banana_fruit_count": by_banana,
                "interaction_equivalence": result["interaction_equivalence"],
                "stack_bottom_decile": result["stack_bottom_decile"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
