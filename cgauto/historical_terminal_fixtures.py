#!/usr/bin/env python3
"""Materialize exact terminal fixtures for close live losses and matched close wins."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import json
from pathlib import Path
import re
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_state import decode_replay, to_game_state  # noqa: E402
from sim.engine import has_stalled  # noqa: E402
from sim.terminal import focus_kind, selected_tree_races, terminal_snapshot  # noqa: E402

LIVE_AGENT = 6553250
GAMES = REPO / "data/processed/games.jsonl"
TRAJECTORIES = REPO / "data/processed/trajectories"
RAW_GAMES = REPO / "data/raw/games"


def action_commands(line: str | None) -> list[str]:
    return [
        command.strip()
        for command in re.split(r"[;\n]", line or "")
        if command.strip() and not command.strip().upper().startswith("MSG ")
    ]


def live_record(game: dict) -> dict | None:
    seat = next(
        (player["index"] for player in game["players"] if player["agentId"] == LIVE_AGENT),
        None,
    )
    if seat is None:
        return None
    opponent = next(player for player in game["players"] if player["index"] == 1 - seat)
    return {
        "game_id": game["gameId"],
        "seat": seat,
        "won": game["ranks"][seat] == 0,
        "margin": game["scores"][seat] - game["scores"][1 - seat],
        "scores": game["scores"],
        "n_turns": game["n_turns"],
        "initial_trees": len(game["map"]["trees0"]),
        "opponent": opponent["name"],
        "processed": game,
    }


def match_close_controls(losses: list[dict], wins: list[dict]) -> list[tuple[dict, dict]]:
    """Greedy unique nearest-neighbor match on duration, supply, margin, and seat."""

    candidates = []
    for loss_index, loss in enumerate(losses):
        for win_index, win in enumerate(wins):
            cost = (
                2 * abs(loss["n_turns"] - win["n_turns"])
                + 8 * abs(loss["initial_trees"] - win["initial_trees"])
                + 3 * abs(abs(loss["margin"]) - abs(win["margin"]))
                + 2 * (loss["seat"] != win["seat"])
                - 20 * (loss["opponent"] == win["opponent"])
            )
            candidates.append((cost, loss["game_id"], win["game_id"], loss_index, win_index))
    assigned_losses = set()
    assigned_wins = set()
    pairs = []
    for _cost, _loss_id, _win_id, loss_index, win_index in sorted(candidates):
        if loss_index in assigned_losses or win_index in assigned_wins:
            continue
        assigned_losses.add(loss_index)
        assigned_wins.add(win_index)
        pairs.append((losses[loss_index], wins[win_index]))
        if len(pairs) == len(losses):
            break
    if len(pairs) != len(losses):
        raise ValueError("not enough unique close wins to match all losses")
    return sorted(pairs, key=lambda pair: pair[0]["game_id"])


def read_trajectory(game_id: int) -> list[dict]:
    return [
        json.loads(line)
        for line in (TRAJECTORIES / f"{game_id}.jsonl").read_text().splitlines()
        if line.strip()
    ]


def frame_record(
    after_game,
    turns_until_end: int,
    commands: list[list[str]],
    races: list[list[dict]],
    plants_before: int,
) -> dict:
    return {
        **terminal_snapshot(after_game, turns_until_end),
        "commands": commands,
        "selected_tree_races": races,
        "plants_before": plants_before,
        "state": {
            "inventories": after_game.inventories,
            "units": [
                {
                    "id": unit.id,
                    "player": unit.player,
                    "x": unit.x,
                    "y": unit.y,
                    "ms": unit.ms,
                    "cc": unit.cc,
                    "hp": unit.hp,
                    "chop": unit.chop,
                    "carry": unit.carry,
                }
                for unit in after_game.units
            ],
            "plants": [
                {
                    "type": plant.type,
                    "x": plant.x,
                    "y": plant.y,
                    "size": plant.size,
                    "health": plant.health,
                    "fruits": plant.fruits,
                    "cooldown": plant.cooldown,
                }
                for plant in after_game.plants
            ],
        },
    }


def assigned_unit_commands(game, player: int, commands: list[str]) -> dict[int, str]:
    """Map the live bot's positional action slots back to its sorted unit ids."""

    unit_ids = sorted(unit.id for unit in game.units if unit.player == player)
    actions = [command for command in commands if not command.upper().startswith("TRAIN ")]
    return {
        unit_id: actions[index]
        for index, unit_id in enumerate(unit_ids)
        if index < len(actions)
    }


def preseed_opportunities(game, live_seat: int, commands: list[str]) -> list[dict]:
    if game.turn < 100 or len(game.plants) > 2:
        return []
    own_units = [unit for unit in game.units if unit.player == live_seat]
    if len(own_units) < 2 or not any(game.inventories[live_seat][:4]):
        return []
    assigned = assigned_unit_commands(game, live_seat, commands)
    plant_cells = {plant.pos for plant in game.plants}
    shack = game.shacks[live_seat]
    opportunities = []
    for unit in own_units:
        adjacent = abs(unit.x - shack[0]) + abs(unit.y - shack[1]) == 1
        if sum(unit.carry) or not adjacent or unit.pos in plant_cells:
            continue
        command = assigned.get(unit.id)
        opportunities.append(
            {
                "turn": game.turn,
                "unit": unit.id,
                "plants": len(game.plants),
                "scores": list(game.scores),
                "live_margin": game.scores[live_seat] - game.scores[1 - live_seat],
                "banked_fruit": list(game.inventories[live_seat][:4]),
                "selected_command": command,
                "would_change_selection": not bool(
                    command and command.upper().startswith("PICK ")
                ),
            }
        )
    return opportunities


def build_fixture(record: dict, history_size: int) -> tuple[dict, dict]:
    decoded = decode_replay(RAW_GAMES / f"{record['game_id']}.json")
    trajectory = read_trajectory(record["game_id"])
    states = decoded["states"]
    initial_game = to_game_state(decoded["map"], states[0])
    focus = [focus_kind(initial_game, player) for player in (0, 1)]
    turns_until_end = 0
    predicted_end_turns = []
    history = deque(maxlen=history_size)
    transitions = []
    preseed = []
    all_frames = []
    usable_turns = min(len(states) - 1, len(trajectory))
    for turn in range(1, usable_turns + 1):
        before_game = to_game_state(decoded["map"], states[turn - 1])
        after_game = to_game_state(decoded["map"], states[turn])
        row = trajectory[turn - 1]
        commands = [action_commands(row.get("commands0")), action_commands(row.get("commands1"))]
        preseed.extend(preseed_opportunities(before_game, record["seat"], commands[record["seat"]]))
        races = [
            selected_tree_races(before_game, player, commands[player], focus[player])
            for player in (0, 1)
        ]
        ended, turns_until_end = has_stalled(after_game, turns_until_end)
        if ended:
            predicted_end_turns.append(turn)
        frame = frame_record(
            after_game,
            turns_until_end,
            commands,
            races,
            len(before_game.plants),
        )
        all_frames.append(frame)
        history.append(frame)
        if before_game.plants and not after_game.plants:
            transitions.append({**frame, "transition": "last_tree_removed"})
        elif not before_game.plants and after_game.plants:
            transitions.append({**frame, "transition": "empty_board_replanted"})

    final_state = states[-1]
    processed = record["processed"]
    expected_final_inventory = [
        processed["per_player"][str(player)]["final_inv"] for player in (0, 1)
    ]
    validation = {
        "unknown_diff_updates": len(decoded["unknown_updates"]),
        "decoded_turns": len(states) - 1,
        "processed_turns": record["n_turns"],
        "trajectory_turns": len(trajectory),
        "final_inventory_matches": final_state["inventories"] == expected_final_inventory,
        "final_scores_match": decoded["scores"] == processed["scores"],
        "predicted_end_turns": predicted_end_turns,
        "early_end_matches": (
            record["n_turns"] == 300
            or predicted_end_turns == [record["n_turns"]]
        ),
        "no_premature_end": not predicted_end_turns
        or predicted_end_turns[0] == record["n_turns"],
    }
    fixture = {
        "schema": 1,
        "scope": "exact decoded historical replay; observational terminal fixture",
        "game_id": record["game_id"],
        "live_agent": LIVE_AGENT,
        "live_seat": record["seat"],
        "won": record["won"],
        "margin": record["margin"],
        "scores": record["scores"],
        "opponent": record["opponent"],
        "n_turns": record["n_turns"],
        "initial_trees": record["initial_trees"],
        "focus_kind": focus,
        "map": decoded["map"],
        "last_tree_transitions": transitions,
        "preseed_opportunities": preseed,
        "terminal_history": list(history),
        "final": all_frames[-1] if all_frames else None,
        "validation": validation,
    }
    return fixture, validation


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def validation_ok(validation: dict) -> bool:
    return (
        validation["unknown_diff_updates"] == 0
        and validation["decoded_turns"] == validation["processed_turns"]
        and validation["trajectory_turns"] == validation["processed_turns"]
        and validation["final_inventory_matches"]
        and validation["final_scores_match"]
        and validation["early_end_matches"]
        and validation["no_premature_end"]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", type=int, default=16)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/terminal-fixtures",
    )
    args = parser.parse_args()
    if args.history < 1:
        raise SystemExit("--history must be positive")

    games = [json.loads(line) for line in GAMES.read_text().splitlines() if line.strip()]
    records = [record for game in games if (record := live_record(game)) is not None]
    close_losses = [
        record for record in records if not record["won"] and abs(record["margin"]) <= 20
    ]
    close_wins = [
        record for record in records if record["won"] and abs(record["margin"]) <= 20
    ]
    pairs = match_close_controls(close_losses, close_wins)
    selected = []
    pair_rows = []
    for loss, win in pairs:
        pair_rows.append({"loss": loss["game_id"], "control_win": win["game_id"]})
        selected.extend((loss, win))

    fixtures = []
    validations = []
    for record in selected:
        fixture, validation = build_fixture(record, args.history)
        filename = f"game-{record['game_id']}.json"
        save(args.output_dir / filename, fixture)
        fixtures.append(
            {
                "game_id": record["game_id"],
                "won": record["won"],
                "margin": record["margin"],
                "opponent": record["opponent"],
                "n_turns": record["n_turns"],
                "file": filename,
                "valid": validation_ok(validation),
            }
        )
        validations.append(validation)

    terminal_reasons = Counter()
    transition_counts = Counter()
    carried_values = []
    fixture_payloads = []
    for fixture_row in fixtures:
        fixture = json.loads((args.output_dir / fixture_row["file"]).read_text())
        fixture_payloads.append(fixture)
        terminal_reasons[fixture["final"]["stall_reason"] or "turn_limit"] += 1
        transition_counts.update(
            transition["transition"] for transition in fixture["last_tree_transitions"]
        )
        carried_values.extend(
            player["carried_value"] for player in fixture["final"]["players"]
        )

    def opportunity_summary(won: bool) -> dict:
        group = [fixture for fixture in fixture_payloads if fixture["won"] == won]
        changes = [
            opportunity
            for fixture in group
            for opportunity in fixture["preseed_opportunities"]
            if opportunity["would_change_selection"]
        ]
        first_turns = [
            next(
                opportunity["turn"]
                for opportunity in fixture["preseed_opportunities"]
                if opportunity["would_change_selection"]
            )
            for fixture in group
            if any(
                opportunity["would_change_selection"]
                for opportunity in fixture["preseed_opportunities"]
            )
        ]
        return {
            "games": len(group),
            "games_with_state_opportunity": sum(
                bool(fixture["preseed_opportunities"]) for fixture in group
            ),
            "games_where_selection_would_change": sum(
                any(
                    opportunity["would_change_selection"]
                    for opportunity in fixture["preseed_opportunities"]
                )
                for fixture in group
            ),
            "selection_change_opportunities": len(changes),
            "median_first_change_turn": statistics.median(first_turns) if first_turns else None,
        }
    manifest = {
        "schema": 1,
        "scope": "13 historical close losses and 13 unique matched close wins",
        "live_agent": LIVE_AGENT,
        "history": args.history,
        "selection": {
            "loss_rule": "ranked loss/tie with absolute score margin <= 20",
            "control_rule": "unique greedy nearest close win by duration, tree count, margin, seat, opponent",
            "pairs": pair_rows,
        },
        "aggregate": {
            "fixtures": len(fixtures),
            "valid": sum(fixture["valid"] for fixture in fixtures),
            "terminal_reasons": dict(terminal_reasons),
            "transitions": dict(transition_counts),
            "mean_final_unbanked_value_per_side": statistics.mean(carried_values),
            "preseed_activation": {
                "close_losses": opportunity_summary(False),
                "matched_close_wins": opportunity_summary(True),
            },
        },
        "fixtures": fixtures,
    }
    save(args.output_dir / "manifest.json", manifest)
    print(json.dumps(manifest["aggregate"], indent=1))
    print(f"saved {args.output_dir / 'manifest.json'}")
    return 0 if all(fixture["valid"] for fixture in fixtures) else 1


if __name__ == "__main__":
    sys.exit(main())
