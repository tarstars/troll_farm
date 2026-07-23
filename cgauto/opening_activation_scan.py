#!/usr/bin/env python3
"""Scan turn-one command divergence for a frozen sparse opening selector."""

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

from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from cgauto.offline_policy_league import resolve_seeds  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_seed(seed: int, baseline: Path, candidate: Path) -> dict:
    game = generate_bronze(seed)
    sides = []
    for seat in (0, 1):
        sessions = [BotSession(baseline, game, seat), BotSession(candidate, game, seat)]
        try:
            baseline_commands = action_commands(sessions[0].command(game))
            candidate_commands = action_commands(sessions[1].command(game))
        finally:
            stderrs = [session.close() for session in sessions]
        sides.append(
            {
                "seat": seat,
                "diverged": baseline_commands != candidate_commands,
                "baseline_commands": baseline_commands,
                "candidate_commands": candidate_commands,
                "baseline_stderr": stderrs[0],
                "candidate_stderr": stderrs[1],
            }
        )
    return {"seed": seed, "sides": sides}


def summarize(rows: list[dict]) -> dict:
    active_sides = [
        (row["seed"], side["seat"])
        for row in rows
        for side in row["sides"]
        if side["diverged"]
    ]
    active_seeds = sorted({seed for seed, _ in active_sides})
    train_specs = Counter()
    for row in rows:
        for side in row["sides"]:
            if not side["diverged"]:
                continue
            for command in side["candidate_commands"]:
                fields = command.split()
                if fields and fields[0].upper() == "TRAIN":
                    train_specs["/".join(fields[1:])] += 1
    return {
        "seed_count": len(rows),
        "side_count": 2 * len(rows),
        "active_seed_count": len(active_seeds),
        "active_side_count": len(active_sides),
        "active_seed_rate": len(active_seeds) / len(rows) if rows else 0.0,
        "active_side_rate": len(active_sides) / (2 * len(rows)) if rows else 0.0,
        "active_seeds": active_seeds,
        "active_sides": [list(value) for value in active_sides],
        "candidate_train_specs": dict(sorted(train_specs.items())),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--seeds", type=int, default=1000)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--seed-list")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        seeds = resolve_seeds(args.seed_start, args.seeds, args.seed_list)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    for path in (args.baseline, args.candidate):
        if not path.exists():
            raise SystemExit(f"missing source: {path}")

    with tempfile.TemporaryDirectory(prefix="opening-activation-scan-") as directory:
        temporary = Path(directory)
        baseline_binary = temporary / "baseline"
        candidate_binary = temporary / "candidate"
        compile_source(args.baseline, baseline_binary, "opening_scan_baseline")
        compile_source(args.candidate, candidate_binary, "opening_scan_candidate")
        print("compiled frozen baseline and candidate", flush=True)
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    scan_seed, seed, baseline_binary, candidate_binary
                ): seed
                for seed in seeds
            }
            for completed, future in enumerate(as_completed(futures), 1):
                rows.append(future.result())
                if completed % 100 == 0 or completed == len(futures):
                    print(f"completed {completed}/{len(futures)} seeds", flush=True)
    rows.sort(key=lambda row: row["seed"])
    payload = {
        "schema": 1,
        "scope": (
            "frozen turn-one command comparison on reused local discovery maps; "
            "no opponent continuation and no arena action"
        ),
        "seed_start": args.seed_start if args.seed_list is None else None,
        "seeds": len(seeds),
        "seed_values": seeds,
        "jobs": args.jobs,
        "baseline": {
            "source": str(args.baseline),
            "sha256": source_sha256(args.baseline),
        },
        "candidate": {
            "source": str(args.candidate),
            "sha256": source_sha256(args.candidate),
        },
        "aggregate": summarize(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
