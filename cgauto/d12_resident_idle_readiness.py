#!/usr/bin/env python3
"""Assess whether the D11 idle-only effect is broad enough to label a residual."""

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
CANDIDATE = "native_second_idle_only"
POLICIES = [CONTROL, CANDIDATE]
FROZEN_SEEDS = list(range(8, 24))
FROZEN_OPPONENTS = [
    "compact_gold",
    "gold_adaptive",
    "legend_balanced",
    "mybot",
    "norx_native_three",
    "resident",
]
NUMERIC_FIELDS = {
    "seed",
    "seat",
    "adopt_worker",
    "margin",
    "wood_edge",
    "workers",
    "shadow_decisions",
    "resident_wait_actor_action",
    "overrides",
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


def validate(rows: list[dict]) -> None:
    if not rows:
        raise ValueError("residual-readiness catalog is empty")
    seeds = sorted({row["seed"] for row in rows})
    opponents = sorted({row["opponent"] for row in rows})
    policies = {row["policy"] for row in rows}
    if seeds != FROZEN_SEEDS:
        raise ValueError(f"seed block is not frozen seeds 8--23: {seeds}")
    if opponents != FROZEN_OPPONENTS:
        raise ValueError("opponent panel does not match the frozen six-opponent panel")
    if policies != set(POLICIES):
        raise ValueError("policy set must contain resident and idle-only exactly")
    expected = {
        (seed, seat, opponent, policy)
        for seed in FROZEN_SEEDS
        for seat in range(2)
        for opponent in FROZEN_OPPONENTS
        for policy in POLICIES
    }
    observed = {
        (row["seed"], row["seat"], row["opponent"], row["policy"])
        for row in rows
    }
    if observed != expected or len(rows) != len(expected):
        raise ValueError(
            f"incomplete residual-readiness catalog: rows={len(rows)}, "
            f"expected={len(expected)}"
        )
    if any(row["adopt_worker"] != int(row["policy"] == CANDIDATE) for row in rows):
        raise ValueError("worker-adoption flag does not match policy")


def analyze(rows: list[dict], input_path: Path) -> dict:
    validate(rows)
    by_cell = {
        (row["seed"], row["seat"], row["opponent"], row["policy"]): row
        for row in rows
    }
    candidate_rows = [row for row in rows if row["policy"] == CANDIDATE]
    cell_records = []
    for row in candidate_rows:
        control = by_cell[(row["seed"], row["seat"], row["opponent"], CONTROL)]
        cell_records.append(
            {
                "seed": row["seed"],
                "seat": row["seat"],
                "opponent": row["opponent"],
                "margin_delta": row["margin"] - control["margin"],
                "wood_delta": row["wood_edge"] - control["wood_edge"],
                "worker_match": row["workers"] == control["workers"],
            }
        )

    map_groups = defaultdict(list)
    opponent_groups = defaultdict(list)
    for cell in cell_records:
        map_groups[cell["seed"]].append(cell["margin_delta"])
        opponent_groups[cell["opponent"]].append(cell["margin_delta"])
    map_deltas = {
        seed: statistics.mean(map_groups[seed]) for seed in FROZEN_SEEDS
    }
    opponent_deltas = {
        opponent: statistics.mean(opponent_groups[opponent])
        for opponent in FROZEN_OPPONENTS
    }
    changed = [cell for cell in cell_records if cell["margin_delta"] != 0]
    positive = [cell for cell in changed if cell["margin_delta"] > 0]
    negative = [cell for cell in changed if cell["margin_delta"] < 0]
    positive_map_sum = sum(max(delta, 0) for delta in map_deltas.values())
    largest_positive_map_share = (
        max(max(delta, 0) for delta in map_deltas.values()) / positive_map_sum
        if positive_map_sum > 0
        else None
    )

    gates = {
        "complete_384_games": len(rows) == 384,
        "resident_worker_count_retained_192_of_192": all(
            cell["worker_match"] for cell in cell_records
        ),
        "map_mean_delta_positive": statistics.mean(map_deltas.values()) > 0,
        "worst_opponent_mean_at_least_minus2": min(opponent_deltas.values()) >= -2,
        "at_least_20_changed_cells": len(changed) >= 20,
        "changed_on_at_least_4_maps": len({cell["seed"] for cell in changed}) >= 4,
        "changed_against_at_least_3_opponents": len(
            {cell["opponent"] for cell in changed}
        )
        >= 3,
        "both_positive_and_negative_changed_cells": bool(positive) and bool(negative),
        "largest_positive_map_share_at_most_60_percent": (
            largest_positive_map_share is not None
            and largest_positive_map_share <= 0.60
        ),
    }
    ready = all(gates.values())
    total_shadow = sum(row["shadow_decisions"] for row in candidate_rows)
    total_overrides = sum(row["overrides"] for row in candidate_rows)

    return {
        "schema": 1,
        "scope": (
            "D12 resident-idle residual dataset-readiness replication on reused "
            "development seeds; not a candidate or Arena gate"
        ),
        "source": {
            "rows": str(input_path),
            "rows_sha256": sha256(input_path),
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "seeds": FROZEN_SEEDS,
            "opponents": FROZEN_OPPONENTS,
            "seats": [0, 1],
            "policies": POLICIES,
            "games": len(rows),
            "candidate_cells": len(candidate_rows),
            "complete": True,
        },
        "effect": {
            "cell_margin_delta": summary(
                cell["margin_delta"] for cell in cell_records
            ),
            "cell_wood_delta": summary(cell["wood_delta"] for cell in cell_records),
            "map_balanced_margin_delta": summary(map_deltas.values()),
            "map_mean_deltas": {str(seed): map_deltas[seed] for seed in FROZEN_SEEDS},
            "opponent_mean_margin_deltas": opponent_deltas,
            "worst_opponent_mean_margin_delta": min(opponent_deltas.values()),
            "changed_cells": len(changed),
            "positive_changed_cells": len(positive),
            "negative_changed_cells": len(negative),
            "changed_maps": sorted({cell["seed"] for cell in changed}),
            "changed_opponents": sorted({cell["opponent"] for cell in changed}),
            "largest_positive_map_share": largest_positive_map_share,
            "worker_count_matches": sum(cell["worker_match"] for cell in cell_records),
            "overrides": total_overrides,
            "override_rate": total_overrides / total_shadow if total_shadow else 0,
        },
        "readiness": {
            "gates": gates,
            "ready_for_counterfactual_labeling": ready,
            "authorization": (
                "passing authorizes offline one-intervention labeling only; it does "
                "not authorize candidate construction, submission, or Arena activity"
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
                "ready": result["readiness"]["ready_for_counterfactual_labeling"],
                "effect": result["effect"],
                "gates": result["readiness"]["gates"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

