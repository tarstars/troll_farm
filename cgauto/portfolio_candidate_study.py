#!/usr/bin/env python3
"""Verify the deployable map portfolio against its selected complete-policy branches."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.offline_policy_league import (  # noqa: E402
    aggregate,
    attach_live_deltas,
    OPPONENT_SOURCES,
    paired_row,
    robust_summary,
)
from cgauto.policy_portfolio_analysis import stump_policy  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

CANDIDATE = (
    REPO / "cgauto/submissions/candidate-agent6553250-banana5-stack-portfolio.min.rs"
)
LEAGUE = REPO / "data/analysis/live-agent-6553250/offline-policy-league-2026-07-16.json"
ANALYSIS = REPO / "data/analysis/live-agent-6553250/policy-portfolio-analysis-2026-07-16.json"
COMPARABLE_FIELDS = (
    "seat_margins",
    "paired_margin",
    "seat_wood_edges",
    "paired_wood_edge",
    "policy_scores",
    "opponent_scores",
    "policy_wood",
    "opponent_wood",
    "policy_command_counts",
    "opponent_command_counts",
    "terminal_turns",
)
STOCHASTIC_OPPONENTS = {
    "motion": (
        "the frozen historical source uses process-randomized std HashMap/HashSet iteration; "
        "repeat processes are an outcome sample, not an exact branch-equivalence oracle"
    )
}


def compare_branch_row(candidate: dict, expected: dict) -> list[str]:
    return [field for field in COMPARABLE_FIELDS if candidate[field] != expected[field]]


def merge_with_live(control: dict, candidate_rows: list[dict]) -> list[dict]:
    rows = [row.copy() for row in control["rows"] if row["policy"] == "live"]
    rows.extend(candidate_rows)
    attach_live_deltas(rows)
    return sorted(rows, key=lambda row: (row["seed"], row["policy"], row["opponent"]))


def seed_balanced_split(rows: list[dict]) -> dict:
    grouped = {}
    for row in rows:
        grouped.setdefault(row["seed"], []).append(row["delta_vs_live_margin"])
    values = {
        seed: statistics.mean(seed_rows) for seed, seed_rows in grouped.items()
    }
    return {
        "train_even_seeds": robust_summary(
            value for seed, value in values.items() if seed % 2 == 0
        ),
        "test_odd_seeds": robust_summary(
            value for seed, value in values.items() if seed % 2 == 1
        ),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--league", type=Path, default=LEAGUE)
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--reuse-rows-from",
        type=Path,
        help="reanalyze portfolio rows from an existing result without rerunning games",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-candidate-study-2026-07-16.json",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    control = json.loads(args.league.read_text())
    analysis = json.loads(args.analysis.read_text())
    stump = analysis["stump"]
    expected_stump = {
        "feature": "banana_fruit_count",
        "threshold": 5.0,
        "left_policy": "stack",
        "right_policy": "live",
    }
    if any(stump[key] != value for key, value in expected_stump.items()):
        raise SystemExit("candidate source only implements the frozen banana-5 stack/live stump")
    features = {int(seed): row for seed, row in control["map_features"].items()}
    seeds = sorted(features)
    games = {seed: generate_bronze(seed) for seed in seeds}
    if args.reuse_rows_from:
        previous = json.loads(args.reuse_rows_from.read_text())
        rows = [row.copy() for row in previous["rows"] if row["policy"] == "portfolio"]
        print(f"reusing {len(rows)} portfolio cells from {args.reuse_rows_from}")
    else:
        rows = []
        with tempfile.TemporaryDirectory(prefix="portfolio-candidate-study-") as directory:
            temp = Path(directory)
            candidate_binary = temp / "portfolio"
            compile_source(args.candidate, candidate_binary, "portfolio_candidate")
            opponent_binaries = {}
            for index, (name, source) in enumerate(OPPONENT_SOURCES.items()):
                binary = temp / name
                compile_source(source, binary, f"portfolio_opponent_{index}_{name}")
                opponent_binaries[name] = binary
            print("compiled portfolio and six frozen opponents", flush=True)
            tasks = [(seed, opponent) for seed in seeds for opponent in OPPONENT_SOURCES]
            with ThreadPoolExecutor(max_workers=args.jobs) as executor:
                futures = {
                    executor.submit(
                        paired_row,
                        seed,
                        games[seed],
                        "portfolio",
                        opponent,
                        candidate_binary,
                        opponent_binaries[opponent],
                    ): (seed, opponent)
                    for seed, opponent in tasks
                }
                for completed, future in enumerate(as_completed(futures), 1):
                    rows.append(future.result())
                    if completed % 25 == 0 or completed == len(tasks):
                        print(f"completed {completed}/{len(tasks)} paired cells", flush=True)
    expected_cell_count = len(seeds) * len(OPPONENT_SOURCES)
    if len(rows) != expected_cell_count:
        raise SystemExit(f"expected {expected_cell_count} portfolio cells, found {len(rows)}")

    expected_rows = {
        (row["seed"], row["policy"], row["opponent"]): row
        for row in control["rows"]
    }
    deterministic_mismatches = []
    stochastic_mismatches = []
    branch_counts = Counter()
    for row in rows:
        branch = stump_policy(stump, features[row["seed"]])
        branch_counts[branch] += 1
        expected = expected_rows[(row["seed"], branch, row["opponent"])]
        fields = compare_branch_row(row, expected)
        if fields:
            mismatch = {
                "seed": row["seed"],
                "opponent": row["opponent"],
                "expected_policy": branch,
                "mismatch_fields": fields,
            }
            if row["opponent"] in STOCHASTIC_OPPONENTS:
                stochastic_mismatches.append(mismatch)
            else:
                deterministic_mismatches.append(mismatch)
    merged = merge_with_live(control, rows)
    portfolio_rows = [row for row in merged if row["policy"] == "portfolio"]
    split = seed_balanced_split(portfolio_rows)
    deterministic_cells = sum(
        row["opponent"] not in STOCHASTIC_OPPONENTS for row in rows
    )
    stochastic_cells = len(rows) - deterministic_cells
    result = {
        "schema": 1,
        "scope": (
            "deployable banana-5 stack/live portfolio versus frozen opponent zoo; "
            "complete branch equivalence and paired live deltas"
        ),
        "candidate": {
            "path": str(args.candidate.relative_to(REPO)),
            "sha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        },
        "stump": stump,
        "seeds": len(seeds),
        "paired_cells": len(rows),
        "branch_cell_counts": dict(sorted(branch_counts.items())),
        "branch_equivalence": {
            "deterministic_cells": deterministic_cells,
            "deterministic_exact_cells": deterministic_cells
            - len(deterministic_mismatches),
            "deterministic_mismatch_cells": len(deterministic_mismatches),
            "passed": not deterministic_mismatches,
            "deterministic_mismatches": deterministic_mismatches[:20],
            "stochastic_opponents": STOCHASTIC_OPPONENTS,
            "stochastic_cells": stochastic_cells,
            "stochastic_observed_exact_cells": stochastic_cells
            - len(stochastic_mismatches),
            "stochastic_observed_mismatch_cells": len(stochastic_mismatches),
            "stochastic_mismatches_sample": stochastic_mismatches[:20],
        },
        "cross_validated_selector_gate": analysis["selector_gate"],
        "aggregate": aggregate(merged),
        "seed_balanced_split": split,
        "rows": merged,
    }
    test = split["test_odd_seeds"]
    result["holdout_gate"] = {
        "mean_positive": test["mean"] > 0,
        "trimmed_mean_positive": test["trimmed_5pct_mean"] > 0,
        "passed": test["mean"] > 0 and test["trimmed_5pct_mean"] > 0,
        "promotion_ready": test["ci95_normal"][0] > 0
        and test["worst_decile_mean"] >= 0,
    }
    result["decision"] = (
        "retain_as_research_candidate"
        if result["branch_equivalence"]["passed"]
        and result["holdout_gate"]["passed"]
        else "reject"
    )
    save(args.output, result)
    print(
        json.dumps(
            {
                "branch_equivalence": result["branch_equivalence"],
                "portfolio": result["aggregate"]["by_policy"]["portfolio"],
                "seed_balanced_split": result["seed_balanced_split"],
                "holdout_gate": result["holdout_gate"],
                "decision": result["decision"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
