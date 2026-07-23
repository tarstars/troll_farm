#!/usr/bin/env python3
"""Capture behavior-neutral last-tree, cash-out, and completion-race telemetry."""

from __future__ import annotations

import argparse
from collections import Counter, deque
from concurrent.futures import as_completed, ThreadPoolExecutor
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
from sim.terminal import focus_kind, selected_tree_races, terminal_snapshot  # noqa: E402

BASELINE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"


def run_seed(seed: int, binary: Path, history_size: int) -> dict:
    game = generate_bronze(seed)
    focus = [focus_kind(game, player) for player in (0, 1)]
    sessions = [BotSession(binary, game, player) for player in (0, 1)]
    turns_until_end = 0
    ended_by_stall = False
    history = deque(maxlen=history_size)
    transitions = []
    low_supply_races = []
    try:
        while game.turn <= 300:
            turn = game.turn
            plants_before = len(game.plants)
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            races = [
                selected_tree_races(game, player, commands[player], focus[player])
                for player in (0, 1)
            ]
            if plants_before <= 4:
                for player in (0, 1):
                    low_supply_races.extend(
                        {"turn": turn, "player": player, **race}
                        for race in races[player]
                    )

            game_was_empty = plants_before == 0
            step(game, commands[0], commands[1])
            ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
            frame = {
                **terminal_snapshot(game, turns_until_end),
                "commands": commands,
                "plants_before": plants_before,
                "selected_tree_races": races,
            }
            history.append(frame)
            if (plants_before > 0 and not game.plants) or (game_was_empty and game.plants):
                transitions.append(
                    {
                        **frame,
                        "transition": (
                            "last_tree_removed" if not game.plants else "empty_board_replanted"
                        ),
                    }
                )
            if ended_by_stall:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError("the exact baseline unexpectedly wrote to stderr")

    final = terminal_snapshot(game, turns_until_end)
    return {
        "seed": seed,
        "focus_kind": focus,
        "ended_by_stall": ended_by_stall,
        "terminal_turn": game.turn - 1,
        "end_reason": final["stall_reason"] if ended_by_stall else "turn_limit",
        "scores": list(game.scores),
        "margin_player_0": game.scores[0] - game.scores[1],
        "last_tree_transitions": transitions,
        "low_supply_races": low_supply_races,
        "final": final,
        "terminal_history": list(history),
    }


def _sign(value: int) -> int:
    return (value > 0) - (value < 0)


def aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {
            "games": 0,
            "end_reasons": {},
            "completion_races": {},
        }
    races = [race for row in rows for race in row["low_supply_races"]]
    commitments: dict[tuple, list[dict]] = {}
    for row in rows:
        for race in row["low_supply_races"]:
            fields = race["command"].split()
            unit = race["selected"]["unit"] if race["selected"] else int(fields[1])
            tree = race["tree"]
            key = (row["seed"], race["player"], unit, tree["x"], tree["y"])
            commitments.setdefault(key, []).append(race)
    commitment_rows = list(commitments.values())
    player_finals = [player for row in rows for player in row["final"]["players"]]
    return {
        "games": len(rows),
        "ended_by_stall": sum(row["ended_by_stall"] for row in rows),
        "median_terminal_turn": statistics.median(row["terminal_turn"] for row in rows),
        "end_reasons": dict(Counter(row["end_reason"] for row in rows)),
        "close_games_within_20": sum(abs(row["margin_player_0"]) <= 20 for row in rows),
        "mean_final_unbanked_value_per_side": statistics.mean(
            player["carried_value"] for player in player_finals
        ),
        "mean_value_cashable_inside_implied_grace_per_side": statistics.mean(
            player["value_within_implied_grace"] for player in player_finals
        ),
        "games_where_cargo_changes_projected_outcome": sum(
            _sign(row["final"]["margin_player_0"])
            != _sign(row["final"]["projected_margin_player_0"])
            for row in rows
        ),
        "last_tree_transitions": {
            "removed": sum(
                transition["transition"] == "last_tree_removed"
                for row in rows
                for transition in row["last_tree_transitions"]
            ),
            "replanted": sum(
                transition["transition"] == "empty_board_replanted"
                for row in rows
                for transition in row["last_tree_transitions"]
            ),
            "games_with_replant": sum(
                any(
                    transition["transition"] == "empty_board_replanted"
                    for transition in row["last_tree_transitions"]
                )
                for row in rows
            ),
        },
        "completion_races": {
            "selected_low_supply_tree_turns": len(races),
            "unique_unit_tree_commitments": len(commitment_rows),
            "with_both_estimates": sum(
                race["selected"] is not None and race["opponent_fastest"] is not None
                for race in races
            ),
            "opponent_beats_selected_fell": sum(
                race["opponent_beats_selected_fell"] for race in races
            ),
            "opponent_beats_selected_bank": sum(
                race["opponent_beats_selected_bank"] for race in races
            ),
            "focus_gate_active": sum(race["focus_gate_active"] for race in races),
            "focus_gate_active_and_opponent_beats_bank": sum(
                race["focus_gate_active"] and race["opponent_beats_selected_bank"]
                for race in races
            ),
            "unique_opponent_beats_selected_bank": sum(
                any(race["opponent_beats_selected_bank"] for race in commitment)
                for commitment in commitment_rows
            ),
            "unique_focus_gate_commitments": sum(
                any(race["focus_gate_active"] for race in commitment)
                for commitment in commitment_rows
            ),
            "unique_focus_gate_and_opponent_beats_bank": sum(
                any(
                    race["focus_gate_active"] and race["opponent_beats_selected_bank"]
                    for race in commitment
                )
                for commitment in commitment_rows
            ),
            "games_with_focus_gate_and_opponent_beats_bank": len(
                {
                    key[0]
                    for key, commitment in commitments.items()
                    if any(
                        race["focus_gate_active"] and race["opponent_beats_selected_bank"]
                        for race in commitment
                    )
                }
            ),
        },
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=BASELINE)
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--history", type=int, default=16)
    parser.add_argument(
        "--reuse-output",
        action="store_true",
        help="recompute only the aggregate from rows already stored at --output",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/terminal-race-telemetry-2026-07-16.json",
    )
    args = parser.parse_args()
    if args.seeds < 0:
        raise SystemExit("--seeds cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    if args.history < 1:
        raise SystemExit("--history must be positive")

    if args.reuse_output:
        payload = json.loads(args.output.read_text())
        payload["aggregate"] = aggregate(payload["rows"])
        save(args.output, payload)
        print(json.dumps(payload["aggregate"], indent=1))
        print(f"updated {args.output}")
        return 0

    with tempfile.TemporaryDirectory(prefix="terminal-race-study-") as directory:
        binary = Path(directory) / "bot"
        compile_source(args.source, binary, "terminal_race_bot")
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(run_seed, seed, binary, args.history): seed
                for seed in range(args.seed_start, args.seed_start + args.seeds)
            }
            for future in as_completed(futures):
                rows.append(future.result())
        rows.sort(key=lambda row: row["seed"])

    payload = {
        "schema": 1,
        "scope": "behavior-neutral exact-live local telemetry; not an arena predictor",
        "eta_model": "static single-worker, no growth and no shared chopping",
        "source": str(args.source.resolve().relative_to(REPO)),
        "seed_start": args.seed_start,
        "seeds": args.seeds,
        "jobs": args.jobs,
        "history": args.history,
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
