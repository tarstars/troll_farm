#!/usr/bin/env python3
"""Measure whether normal promoted-policy play ever funds a third worker.

This is behavior-neutral telemetry.  It runs the frozen source against itself, records every
two-worker state, and prices several third-worker specifications without changing commands.
The expensive work runs in compiled Rust bot subprocesses; Python threads only orchestrate I/O.
"""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ThreadPoolExecutor
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import ITEM_INDEX, training_cost  # noqa: E402
from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from sim.engine import has_stalled, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

BASELINE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
SPECS = {
    "minimal_wood_1101": (1, 1, 0, 1),
    "fast_wood_2101": (2, 1, 0, 1),
    "carry_wood_1201": (1, 2, 0, 1),
    "live_wood_2202": (2, 2, 0, 2),
    "minimal_hybrid_1111": (1, 1, 1, 1),
}
PAY_ITEMS = (ITEM_INDEX["PLUM"], ITEM_INDEX["LEMON"], ITEM_INDEX["APPLE"], ITEM_INDEX["IRON"])


def affordability(inventory: list[int], spec: tuple[int, int, int, int]) -> dict:
    cost = training_cost(2, spec)
    deficits = [max(cost[index] - inventory[index], 0) for index in PAY_ITEMS]
    return {
        "cost": [cost[index] for index in PAY_ITEMS],
        "inventory": [inventory[index] for index in PAY_ITEMS],
        "deficits": deficits,
        "total_deficit": sum(deficits),
        "affordable": not any(deficits),
    }


def run_seed(seed: int, binary: Path) -> list[dict]:
    game = generate_bronze(seed)
    sessions = [BotSession(binary, game, seat) for seat in (0, 1)]
    observations = [[], []]
    first_two_worker_turn = [None, None]
    turns_until_end = 0
    try:
        while game.turn <= 300:
            for seat in (0, 1):
                units = [unit for unit in game.units if unit.player == seat]
                if len(units) == 2 and game.turn <= 280:
                    if first_two_worker_turn[seat] is None:
                        first_two_worker_turn[seat] = game.turn
                    observations[seat].append(
                        {
                            "turn": game.turn,
                            "inventory": list(game.inventories[seat]),
                            "specs": {
                                name: affordability(game.inventories[seat], spec)
                                for name, spec in SPECS.items()
                            },
                        }
                    )
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            step(game, commands[0], commands[1])
            ended, turns_until_end = has_stalled(game, turns_until_end)
            if ended:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError("promoted baseline unexpectedly wrote to stderr")
    return [
        {
            "seed": seed,
            "seat": seat,
            "first_two_worker_turn": first_two_worker_turn[seat],
            "observations": observations[seat],
        }
        for seat in (0, 1)
    ]


def summarize(rows: list[dict]) -> dict:
    two_worker = [row for row in rows if row["observations"]]
    by_spec = {}
    for name in SPECS:
        best = []
        affordable_turns = 0
        sides_with_window = 0
        for row in two_worker:
            observations = row["observations"]
            affordable = [item for item in observations if item["specs"][name]["affordable"]]
            affordable_turns += len(affordable)
            sides_with_window += bool(affordable)
            chosen = min(
                observations,
                key=lambda item: (item["specs"][name]["total_deficit"], item["turn"]),
            )
            best.append({"turn": chosen["turn"], **chosen["specs"][name]})
        by_spec[name] = {
            "spec": list(SPECS[name]),
            "sides_with_affordable_window": sides_with_window,
            "affordable_turns": affordable_turns,
            "minimum_total_deficit": min(
                (item["total_deficit"] for item in best), default=None
            ),
            "median_best_total_deficit": (
                statistics.median(item["total_deficit"] for item in best) if best else None
            ),
            "median_best_turn": statistics.median(item["turn"] for item in best) if best else None,
            "median_resource_deficits_at_best": (
                [
                    statistics.median(item["deficits"][index] for item in best)
                    for index in range(4)
                ]
                if best
                else None
            ),
        }
    return {
        "side_games": len(rows),
        "sides_reaching_two_workers": len(two_worker),
        "median_first_two_worker_turn": (
            statistics.median(row["first_two_worker_turn"] for row in two_worker)
            if two_worker
            else None
        ),
        "pay_item_order": ["PLUM", "LEMON", "APPLE", "IRON"],
        "by_spec": by_spec,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=BASELINE)
    parser.add_argument("--seeds", type=int, default=200)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/surplus-workforce-telemetry.json",
    )
    args = parser.parse_args()
    if args.seeds <= 0:
        raise SystemExit("--seeds must be positive")
    if not 1 <= args.jobs <= 16:
        raise SystemExit("--jobs must be between 1 and 16")

    with tempfile.TemporaryDirectory(prefix="surplus-workforce-") as directory:
        binary = Path(directory) / "baseline"
        compile_source(args.source, binary, "surplus_workforce_baseline")
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(run_seed, seed, binary): seed
                for seed in range(args.seed_start, args.seed_start + args.seeds)
            }
            for completed, future in enumerate(as_completed(futures), 1):
                rows.extend(future.result())
                if completed % 25 == 0 or completed == len(futures):
                    print(f"completed {completed}/{len(futures)} seeds", flush=True)
    rows.sort(key=lambda row: (row["seed"], row["seat"]))
    payload = {
        "schema": 1,
        "scope": "behavior-neutral promoted-policy affordability telemetry",
        "source": str(args.source.resolve().relative_to(REPO)),
        "seed_start": args.seed_start,
        "seeds": args.seeds,
        "jobs": args.jobs,
        "aggregate": summarize(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
