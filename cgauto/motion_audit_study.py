#!/usr/bin/env python3
"""Behavior-neutral audit of emitted movement, blocking, and one-turn reversals."""

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

from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from sim.engine import has_stalled, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

BASELINE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"


def move_commands(commands: list[str]) -> dict[int, tuple[int, int]]:
    moves = {}
    for command in commands:
        fields = command.split()
        if len(fields) != 4 or fields[0].upper() != "MOVE":
            continue
        try:
            moves[int(fields[1])] = (int(fields[2]), int(fields[3]))
        except ValueError:
            continue
    return moves


def audit_transition(
    game_before,
    game_after,
    player: int,
    moves: dict[int, tuple[int, int]],
    previous_origins: dict[int, tuple[int, int]],
) -> tuple[Counter, list[dict]]:
    before = {unit.id: unit.pos for unit in game_before.units if unit.player == player}
    after = {unit.id: unit.pos for unit in game_after.units if unit.player == player}
    counters = Counter(moves=len(moves))
    examples = []
    target_counts = Counter(moves.values())
    moving_ids = set(moves)
    stationary_cells = {
        cell for unit_id, cell in before.items() if unit_id not in moving_ids
    }
    for unit_id, target in moves.items():
        origin = before.get(unit_id)
        landing = after.get(unit_id)
        if origin is None or landing is None:
            continue
        kind = []
        if landing == target:
            counters["reached_emitted_target"] += 1
        elif landing == origin:
            counters["no_progress"] += 1
            kind.append("no_progress")
        else:
            counters["partial_progress"] += 1
            kind.append("partial_progress")
        if target_counts[target] > 1:
            counters["duplicate_emitted_landing"] += 1
            kind.append("duplicate_emitted_landing")
        if target in stationary_cells:
            counters["targets_stationary_teammate"] += 1
            kind.append("targets_stationary_teammate")
        if previous_origins.get(unit_id) == landing and landing != origin:
            counters["one_turn_reversal"] += 1
            kind.append("one_turn_reversal")
        shack = game_before.shacks[player]
        if abs(target[0] - shack[0]) + abs(target[1] - shack[1]) == 1:
            counters["door_moves"] += 1
            if landing == origin:
                counters["door_no_progress"] += 1
                kind.append("door_no_progress")
        if kind:
            examples.append(
                {
                    "unit": unit_id,
                    "origin": list(origin),
                    "target": list(target),
                    "landing": list(landing),
                    "kinds": kind,
                }
            )

    for unit_a, target_a in moves.items():
        for unit_b, target_b in moves.items():
            if unit_a < unit_b and target_a == before.get(unit_b) and target_b == before.get(unit_a):
                counters["emitted_swaps"] += 1
    return counters, examples


def run_seed(seed: int, binary: Path, example_limit: int = 20) -> dict:
    game = generate_bronze(seed)
    sessions = [BotSession(binary, game, player) for player in (0, 1)]
    totals = [Counter(), Counter()]
    examples = []
    previous_origins = [{}, {}]
    turns_until_end = 0
    ended_by_stall = False
    try:
        while game.turn <= 300:
            turn = game.turn
            before = copy.deepcopy(game)
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            moves = [move_commands(commands[player]) for player in (0, 1)]
            step(game, commands[0], commands[1])
            for player in (0, 1):
                counters, transition_examples = audit_transition(
                    before, game, player, moves[player], previous_origins[player]
                )
                totals[player].update(counters)
                for example in transition_examples:
                    if len(examples) < example_limit:
                        examples.append(
                            {"turn": turn, "player": player, **example}
                        )
                previous_origins[player] = {
                    unit.id: unit.pos
                    for unit in before.units
                    if unit.player == player
                }
            ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
            if ended_by_stall:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError("the exact baseline unexpectedly wrote to stderr")
    return {
        "seed": seed,
        "terminal_turn": game.turn - 1,
        "ended_by_stall": ended_by_stall,
        "players": [dict(counter) for counter in totals],
        "examples": examples,
    }


def aggregate(rows: list[dict]) -> dict:
    totals = Counter()
    for row in rows:
        for player in row["players"]:
            totals.update(player)
    moves = totals["moves"]
    door_moves = totals["door_moves"]
    return {
        "games": len(rows),
        "side_games": 2 * len(rows),
        "ended_by_stall": sum(row["ended_by_stall"] for row in rows),
        "median_terminal_turn": statistics.median(row["terminal_turn"] for row in rows)
        if rows
        else None,
        "counts": dict(totals),
        "rates_per_move": {
            key: (totals[key] / moves if moves else None)
            for key in (
                "reached_emitted_target",
                "no_progress",
                "partial_progress",
                "duplicate_emitted_landing",
                "targets_stationary_teammate",
                "one_turn_reversal",
            )
        },
        "door_no_progress_rate": (
            totals["door_no_progress"] / door_moves if door_moves else None
        ),
        "games_with_no_progress": sum(
            any(player.get("no_progress", 0) for player in row["players"])
            for row in rows
        ),
        "games_with_reversal": sum(
            any(player.get("one_turn_reversal", 0) for player in row["players"])
            for row in rows
        ),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=200)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--source", type=Path, default=BASELINE)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/motion-audit-telemetry.json",
    )
    args = parser.parse_args()
    if args.seeds < 0:
        raise SystemExit("--seeds cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")

    with tempfile.TemporaryDirectory(prefix="motion-audit-") as directory:
        binary = Path(directory) / "baseline"
        compile_source(args.source, binary, "motion_audit_source")
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(run_seed, seed, binary): seed for seed in range(args.seeds)
            }
            for future in as_completed(futures):
                rows.append(future.result())
        rows.sort(key=lambda row: row["seed"])

    payload = {
        "schema": 1,
        "scope": "behavior-neutral exact-live local motion audit; not an arena predictor",
        "source": str(args.source.resolve().relative_to(REPO)),
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
