#!/usr/bin/env python3
"""Is TRAIN reachable at all on the fuzz panel? Full-width measurement.

Settles blocker 3 of `chatgpt_1`'s revision-2 review: "the one-worker half is
not proven unable to TRAIN — initial unaffordability is not a reachability
proof; full 240-row evidence or an exact proof is still required."

That objection is correct. Two mechanisms were claimed to prevent TRAIN:

1. the panel injects a second worker (`fuzz_panel.py:486-495`) at
   `second_worker_bias` = 0.5, after which the resident's `can_train` returns
   false at `if n >= 2` (`yamo_orchard_live.rs:836`). This half is an exact
   proof: the cap is unconditional and checked before affordability.
2. in the remaining one-worker games the starting inventory grants PLUM <= 1
   against a cost of >= 2. This half is NOT a proof — the bot could harvest a
   plum and then afford it. Only measurement settles it.

This probe runs the parent alone (not the candidate — half the work) over every
job the floor config generates, and records, per game: whether a second worker
is present at turn 1, and whether any TRAIN command is ever emitted.

Read-only with respect to the repository: it compiles the parent into the
configured binary cache and writes only the JSON report it is asked for.

Usage:
    python3 cgauto/probe_panel_train_reachability.py \
        --config local_claude_1/verification/local_claude_1-floor-selftest-config-2026-08-07.json \
        --json <out.json>
"""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "claude_1" / "pipeline"))
sys.path.insert(0, str(ROOT / "claude_1" / "banana-restoration-r2"))

import fuzz_panel as fp  # noqa: E402
import regression_tests as rt  # noqa: E402
import trace_detectors as td  # noqa: E402


def probe_one(job) -> dict:
    """Run the parent on one job; report roster and TRAIN reachability."""
    spec = job["spec"]
    own_at_start = sum(1 for u in spec["units"] if u[1] == 0)
    ref = fp.make_referee(spec)
    _, commands = rt.run_binary_custom(
        pathlib.Path(job["parent"]), ref, job["turns"])
    parsed = td.CommandParser().parse(commands)
    train_turns = [t for t, tc in enumerate(parsed, start=1)
                   if tc.train is not None]
    return {
        "map_id": spec["map_id"],
        "seat": spec["seat"],
        "class": spec["class"],
        "profile": spec["profile"],
        "own_units_at_start": own_at_start,
        "turns_parsed": len(parsed),
        "train_turns": train_turns,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("--json", type=pathlib.Path)
    ap.add_argument("--limit", type=int, default=0,
                    help="probe only the first N jobs (0 = all)")
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    workdir = pathlib.Path(cfg["bin_cache_dir"])
    workdir.mkdir(parents=True, exist_ok=True)
    parent_bin = fp.compile_bot(cfg, "parent", workdir)

    jobs = fp.build_jobs(cfg, parent_bin, parent_bin)
    if args.limit:
        jobs = jobs[:args.limit]

    procs = max(1, int(cfg.get("processes", 4)))
    with multiprocessing.Pool(procs) as pool:
        rows = pool.map(probe_one, jobs)

    one_worker = [r for r in rows if r["own_units_at_start"] == 1]
    two_worker = [r for r in rows if r["own_units_at_start"] >= 2]
    trained = [r for r in rows if r["train_turns"]]

    report = {
        "task": "panel TRAIN reachability (revision-2 review blocker 3)",
        "config": str(args.config),
        "games": len(rows),
        "games_with_one_own_unit_at_start": len(one_worker),
        "games_with_two_own_units_at_start": len(two_worker),
        "games_emitting_any_TRAIN": len(trained),
        "trained_among_one_worker_games": sum(
            1 for r in trained if r["own_units_at_start"] == 1),
        "turns_parsed_min": min((r["turns_parsed"] for r in rows), default=0),
        "turns_parsed_max": max((r["turns_parsed"] for r in rows), default=0),
        "by_class": dict(collections.Counter(
            r["class"] for r in one_worker)),
        "by_profile": dict(collections.Counter(
            r["profile"] for r in one_worker)),
        "verdict": ("TRAIN_UNREACHABLE_ON_PANEL" if not trained
                    else "TRAIN_REACHABLE"),
        "rows": rows,
    }

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n",
                             encoding="utf-8")

    print(f"games                      : {report['games']}")
    print(f"  one own unit at start    : {report['games_with_one_own_unit_at_start']}")
    print(f"  two own units at start   : {report['games_with_two_own_units_at_start']}")
    print(f"turns parsed per game      : "
          f"{report['turns_parsed_min']}-{report['turns_parsed_max']}")
    print(f"games emitting any TRAIN   : {report['games_emitting_any_TRAIN']}")
    print(f"  of which one-worker      : {report['trained_among_one_worker_games']}")
    print(f"verdict                    : {report['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
