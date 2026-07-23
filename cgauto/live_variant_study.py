#!/usr/bin/env python3
"""Run a generic paired-local self-harm check for an exact live-source variant.

The historical calibration failure still applies: this is not an arena promotion signal.  It
only checks whether a candidate has an obvious deterministic mechanism loss against its exact
parent under the repository simulator.
"""

from __future__ import annotations

import argparse
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
from cgauto.sparse_farming_study import candidate_margins, command_delta  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

BASELINE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"


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
        "candidate_margins": margins,
        "candidate_paired_margin": statistics.mean(margins),
        "candidate_wood_delta": statistics.mean(candidate_wood)
        - statistics.mean(baseline_wood),
        "command_delta": command_delta(first, second),
        "baseline_seat0": first,
        "candidate_seat0": second,
    }


def aggregate(rows: list[dict]) -> dict:
    verbs = sorted({verb for row in rows for verb in row["command_delta"]})
    return {
        "seeds": len(rows),
        "candidate_mean_paired_margin": (
            statistics.mean(row["candidate_paired_margin"] for row in rows) if rows else None
        ),
        "candidate_mean_wood_delta": (
            statistics.mean(row["candidate_wood_delta"] for row in rows) if rows else None
        ),
        "candidate_wins_ties_losses": {
            "wins": sum(row["candidate_paired_margin"] > 0 for row in rows),
            "ties": sum(row["candidate_paired_margin"] == 0 for row in rows),
            "losses": sum(row["candidate_paired_margin"] < 0 for row in rows),
        },
        "mean_command_delta": {
            verb: statistics.mean(row["command_delta"].get(verb, 0) for row in rows)
            for verb in verbs
        },
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=BASELINE,
        help="exact parent source to use as the paired control",
    )
    parser.add_argument("--seeds", type=int, default=40)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--quiet", action="store_true", help="suppress per-seed progress")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.seeds < 0:
        raise SystemExit("--seeds cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")

    with tempfile.TemporaryDirectory(prefix="live-variant-study-") as directory:
        temp = Path(directory)
        baseline = temp / "baseline"
        candidate = temp / "candidate"
        compile_source(args.baseline, baseline, "live_variant_baseline")
        compile_source(args.candidate, candidate, "live_variant_candidate")
        rows = []
        seeds = range(args.seed_start, args.seed_start + args.seeds)
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(paired_row, seed, baseline, candidate): seed for seed in seeds
            }
            for future in as_completed(futures):
                row = future.result()
                rows.append(row)
                if not args.quiet:
                    print(
                        f"seed {row['seed']}: margin={row['candidate_paired_margin']:+.1f} "
                        f"wood={row['candidate_wood_delta']:+.1f}",
                        flush=True,
                    )
        rows.sort(key=lambda row: row["seed"])

    payload = {
        "schema": 1,
        "scope": "paired local self-harm check; not an arena predictor",
        "sources": {
            "baseline": str(args.baseline.resolve().relative_to(REPO)),
            "candidate": str(args.candidate.resolve().relative_to(REPO)),
        },
        "seed_start": args.seed_start,
        "seeds": args.seeds,
        "jobs": args.jobs,
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
