#!/usr/bin/env python3
"""Run a paired local mechanism study for the live Yamo sparse-farming flag.

The candidate changes one existing policy bit.  On maps with at most 14 initial trees it
assigns the starter to maintain one mother/crop loop; on denser maps the code path stays off.
This study is a self-harm and activation check only.  The repository's paired local simulator
has failed historical arena calibration and must not be used as a promotion signal.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source, run_match  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

BASELINE_SOURCE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"
CANDIDATE_SOURCE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-sparse-farming-work-conserving.min.rs"
)
SPARSE_TREE_LIMIT = 14


def candidate_margins(baseline_seat0: dict, candidate_seat0: dict) -> list[float]:
    """Return both margins from the candidate's perspective."""

    return [
        baseline_seat0["scores"][1] - baseline_seat0["scores"][0],
        candidate_seat0["scores"][0] - candidate_seat0["scores"][1],
    ]


def command_delta(first: dict, second: dict) -> dict[str, float]:
    """Mean candidate-minus-baseline command counts across both seat assignments."""

    baseline = [first["command_counts"][0], second["command_counts"][1]]
    candidate = [first["command_counts"][1], second["command_counts"][0]]
    verbs = sorted(set().union(*(Counter(row) for row in baseline + candidate)))
    return {
        verb: statistics.mean(row.get(verb, 0) for row in candidate)
        - statistics.mean(row.get(verb, 0) for row in baseline)
        for verb in verbs
    }


def paired_row(seed: int, baseline: Path, candidate: Path) -> dict:
    initial = generate_bronze(seed)
    first = run_match(copy.deepcopy(initial), baseline, candidate)
    second = run_match(copy.deepcopy(initial), candidate, baseline)
    margins = candidate_margins(first, second)
    candidate_wood = [first["inventories"][1][5], second["inventories"][0][5]]
    baseline_wood = [first["inventories"][0][5], second["inventories"][1][5]]
    return {
        "seed": seed,
        "initial_trees": len(initial.plants),
        "activated": len(initial.plants) <= SPARSE_TREE_LIMIT,
        "candidate_margins": margins,
        "candidate_paired_margin": statistics.mean(margins),
        "candidate_mean_wood": statistics.mean(candidate_wood),
        "baseline_mean_wood": statistics.mean(baseline_wood),
        "candidate_wood_delta": statistics.mean(candidate_wood)
        - statistics.mean(baseline_wood),
        "command_delta": command_delta(first, second),
        "baseline_seat0": first,
        "candidate_seat0": second,
    }


def aggregate(rows: list[dict]) -> dict:
    def summarize(group: list[dict]) -> dict:
        return {
            "seeds": len(group),
            "candidate_mean_paired_margin": (
                statistics.mean(row["candidate_paired_margin"] for row in group)
                if group
                else None
            ),
            "candidate_mean_wood_delta": (
                statistics.mean(row["candidate_wood_delta"] for row in group)
                if group
                else None
            ),
            "candidate_wins_ties_losses": {
                "wins": sum(row["candidate_paired_margin"] > 0 for row in group),
                "ties": sum(row["candidate_paired_margin"] == 0 for row in group),
                "losses": sum(row["candidate_paired_margin"] < 0 for row in group),
            },
        }

    active = [row for row in rows if row["activated"]]
    inactive = [row for row in rows if not row["activated"]]
    return {
        "all": summarize(rows),
        "activated": summarize(active),
        "inactive": summarize(inactive),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=40)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE_SOURCE)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "sparse-farming-work-conserving-local-study.json",
    )
    args = parser.parse_args()
    if args.seeds < 0:
        raise SystemExit("--seeds cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")

    with tempfile.TemporaryDirectory(prefix="sparse-farming-study-") as directory:
        temp = Path(directory)
        baseline = temp / "baseline"
        candidate = temp / "candidate"
        compile_source(BASELINE_SOURCE, baseline, "sparse_farming_baseline")
        compile_source(args.candidate, candidate, "sparse_farming_candidate")

        rows = []
        seeds = range(args.seed_start, args.seed_start + args.seeds)
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(paired_row, seed, baseline, candidate): seed for seed in seeds
            }
            for future in as_completed(futures):
                row = future.result()
                rows.append(row)
                print(
                    f"seed {row['seed']}: trees={row['initial_trees']} "
                    f"active={row['activated']} margin={row['candidate_paired_margin']:+.1f} "
                    f"wood={row['candidate_wood_delta']:+.1f}",
                    flush=True,
                )
        rows.sort(key=lambda row: row["seed"])

    payload = {
        "schema": 1,
        "scope": "paired local self-harm/activation check; not an arena predictor",
        "sources": {
            "baseline": str(BASELINE_SOURCE.relative_to(REPO)),
            "candidate": str(args.candidate.relative_to(REPO)),
        },
        "sparse_tree_limit": SPARSE_TREE_LIMIT,
        "seed_start": args.seed_start,
        "seeds": args.seeds,
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
