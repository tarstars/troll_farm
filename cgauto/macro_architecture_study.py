#!/usr/bin/env python3
"""Kill-test the census-derived hybrid/wood-worker architecture on the fixed zoo."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
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
)
from sim.mapgen import generate_bronze  # noqa: E402

CANDIDATE = (
    REPO / "cgauto/submissions/candidate-agent6553250-hybrid-funded-third-worker.min.rs"
)
DEFAULT_CONTROL = (
    REPO
    / "data/analysis/live-agent-6553250/offline-policy-league-2026-07-16.json"
)


def merge_with_live(control: dict, candidate_rows: list[dict]) -> list[dict]:
    live_rows = [row.copy() for row in control["rows"] if row["policy"] == "live"]
    rows = live_rows + candidate_rows
    attach_live_deltas(rows)
    return sorted(rows, key=lambda row: (row["seed"], row["policy"], row["opponent"]))


def training_activation(rows: list[dict]) -> dict:
    live = {
        (row["seed"], row["opponent"]): row["policy_command_counts"].get("TRAIN", 0)
        for row in rows
        if row["policy"] == "live"
    }
    candidate = [row for row in rows if row["policy"] == "hybrid_macro"]
    counts = [row["policy_command_counts"].get("TRAIN", 0) for row in candidate]
    extra = [
        count - live[(row["seed"], row["opponent"])]
        for row, count in zip(candidate, counts)
    ]
    return {
        "paired_cell_train_count_distribution": {
            str(count): frequency
            for count, frequency in sorted(Counter(counts).items())
        },
        "paired_cells": len(candidate),
        "paired_cells_above_live_train_count": sum(value > 0 for value in extra),
        "paired_cells_above_live_rate": (
            sum(value > 0 for value in extra) / len(extra) if extra else 0.0
        ),
        "extra_train_commands": sum(extra),
        "activated": bool(extra) and sum(value > 0 for value in extra) > 0,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, default=DEFAULT_CONTROL)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/macro-architecture-funded-study-2026-07-16.json",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    control = json.loads(args.control.read_text())
    seeds = sorted(int(seed) for seed in control["map_features"])
    if sorted(control["opponents"]) != sorted(OPPONENT_SOURCES):
        raise SystemExit("control opponent zoo differs from the frozen study zoo")
    games = {seed: generate_bronze(seed) for seed in seeds}
    candidate_rows = []
    with tempfile.TemporaryDirectory(prefix="macro-architecture-study-") as directory:
        temp = Path(directory)
        candidate_binary = temp / "hybrid"
        compile_source(args.candidate, candidate_binary, "macro_hybrid_candidate")
        opponent_binaries = {}
        for index, (name, source) in enumerate(OPPONENT_SOURCES.items()):
            binary = temp / name
            compile_source(source, binary, f"macro_opponent_{index}_{name}")
            opponent_binaries[name] = binary
        print("compiled candidate and six frozen opponents", flush=True)
        tasks = [(seed, opponent) for seed in seeds for opponent in OPPONENT_SOURCES]
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    paired_row,
                    seed,
                    games[seed],
                    "hybrid_macro",
                    opponent,
                    candidate_binary,
                    opponent_binaries[opponent],
                ): (seed, opponent)
                for seed, opponent in tasks
            }
            for completed, future in enumerate(as_completed(futures), 1):
                candidate_rows.append(future.result())
                if completed % 25 == 0 or completed == len(tasks):
                    print(f"completed {completed}/{len(tasks)} paired cells", flush=True)
    rows = merge_with_live(control, candidate_rows)
    result = {
        "schema": 1,
        "scope": (
            "census-derived funded three-worker hybrid/wood sequence versus fixed opponent zoo; "
            "same corrected deterministic simulator and live controls as policy league"
        ),
        "hypothesis": (
            "a 2/2/1/2 hybrid second worker and the starter can collect the resources needed "
            "for a 2/2/0/2 dedicated third worker, after which all three convert wood"
        ),
        "kill_rules": [
            "reject as untested if no paired cell issues more TRAIN commands than live",
            "reject if seed-balanced mean delta versus live is not positive",
            "reject if 5%-trimmed mean delta is not positive",
            "reject if worst-opponent mean delta is below live",
        ],
        "control": str(args.control),
        "candidate": {
            "path": str(args.candidate.relative_to(REPO)),
            "sha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        },
        "seeds": len(seeds),
        "aggregate": aggregate(rows),
        "training_activation": training_activation(rows),
        "rows": rows,
    }
    candidate_summary = result["aggregate"]["by_policy"]["hybrid_macro"]
    delta = candidate_summary["seed_balanced_delta_vs_live_margin"]
    result["decision"] = (
        "retain_for_followup"
        if result["training_activation"]["activated"]
        and delta["mean"] > 0
        and delta["trimmed_5pct_mean"] > 0
        and candidate_summary["worst_opponent_mean_delta"] >= 0
        else "reject"
    )
    save(args.output, result)
    print(json.dumps({"summary": candidate_summary, "decision": result["decision"]}, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
