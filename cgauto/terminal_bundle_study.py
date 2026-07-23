#!/usr/bin/env python3
"""Price zero-commitment terminal bundles on validated historical fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import bfs_distances  # noqa: E402
from cgauto.replay_state import to_game_state  # noqa: E402
from sim.terminal import cashout_eta, ceil_div, static_completion  # noqa: E402

MANIFEST = REPO / "data/analysis/live-agent-6553250/terminal-fixtures/manifest.json"


def home_doors(game, player: int) -> list[tuple[int, int]]:
    sx, sy = game.shacks[player]
    return [
        cell
        for cell in ((sx, sy + 1), (sx + 1, sy), (sx, sy - 1), (sx - 1, sy))
        if cell in game.walkable
    ]


def best_fell_cycle_from_home(game, unit) -> dict | None:
    """Static home-door -> tree -> home-door cycle after cargo has been dropped."""

    if unit.chop <= 0 or unit.cc <= 0:
        return None
    distance = bfs_distances(game.walkable, home_doors(game, unit.player))
    cycles = []
    for plant in game.plants:
        cells = distance.get(plant.pos)
        if cells is None or plant.health <= 0 or plant.size <= 0:
            continue
        travel = ceil_div(cells, unit.ms)
        chop = ceil_div(plant.health, unit.chop)
        wood = min(plant.size, unit.cc)
        cycles.append(
            {
                "tree": [plant.x, plant.y],
                "kind": plant.type,
                "eta": travel + chop + travel + 1,
                "wood": wood,
                "value": 4 * wood,
            }
        )
    return min(cycles, key=lambda cycle: (cycle["eta"], -cycle["value"], cycle["tree"])) if cycles else None


def best_direct_fell(game, unit) -> dict | None:
    completions = [
        completion
        for plant in game.plants
        if (completion := static_completion(game, unit, plant)) is not None
    ]
    return min(completions, key=lambda item: (item["bank_eta"], -item["value"])) if completions else None


def frame_opportunities(fixture: dict, frame: dict, next_commands: list[str]) -> list[dict]:
    state = {"resolved_turn": frame["resolved_turn"], **frame["state"]}
    game = to_game_state(fixture["map"], state)
    player = fixture["live_seat"]
    remaining = fixture["n_turns"] - frame["resolved_turn"]
    opportunities = []
    for unit in game.units:
        if unit.player != player:
            continue
        home_cycle = best_fell_cycle_from_home(game, unit)
        if home_cycle is None:
            continue
        cashout = cashout_eta(game, unit)
        carried = sum(unit.carry)
        if carried > 0 and cashout is not None:
            eta = cashout + home_cycle["eta"]
            opportunities.append(
                {
                    "kind": "cashout_then_fell",
                    "turn": game.turn,
                    "unit": unit.id,
                    "remaining_turns": remaining,
                    "eta": eta,
                    "feasible": eta <= remaining,
                    "home_cycle": home_cycle,
                    "direct": best_direct_fell(game, unit),
                    "next_commands": next_commands,
                }
            )
        plant = next((plant for plant in game.plants if plant.pos == unit.pos), None)
        if (
            plant is not None
            and plant.fruits > 0
            and unit.hp > 0
            and unit.free > 0
            and cashout is not None
        ):
            eta = 1 + cashout + home_cycle["eta"]
            fruit = min(unit.hp, unit.free, plant.fruits)
            opportunities.append(
                {
                    "kind": "harvest_bank_fell",
                    "turn": game.turn,
                    "unit": unit.id,
                    "remaining_turns": remaining,
                    "eta": eta,
                    "feasible": eta <= remaining,
                    "fruit": fruit,
                    "home_cycle": home_cycle,
                    "direct": best_direct_fell(game, unit),
                    "next_commands": next_commands,
                }
            )
    return opportunities


def analyze_fixture(path: Path) -> dict:
    fixture = json.loads(path.read_text())
    frames = fixture["terminal_history"]
    opportunities = []
    for index, frame in enumerate(frames[:-1]):
        next_commands = frames[index + 1]["commands"][fixture["live_seat"]]
        opportunities.extend(frame_opportunities(fixture, frame, next_commands))
    return {
        "game_id": fixture["game_id"],
        "won": fixture["won"],
        "margin": fixture["margin"],
        "opportunities": opportunities,
    }


def feasible_episode_count(rows: list[dict], kind: str) -> int:
    """Collapse consecutive frame observations of one unit/tree commitment."""

    episodes = 0
    for row in rows:
        last_turn_by_commitment: dict[tuple[int, tuple[int, int]], int] = {}
        events = sorted(
            (
                event
                for event in row["opportunities"]
                if event["kind"] == kind and event["feasible"]
            ),
            key=lambda event: event["turn"],
        )
        for event in events:
            key = (event["unit"], tuple(event["home_cycle"]["tree"]))
            previous_turn = last_turn_by_commitment.get(key)
            if previous_turn is None or event["turn"] > previous_turn + 1:
                episodes += 1
            last_turn_by_commitment[key] = event["turn"]
    return episodes


def aggregate(rows: list[dict]) -> dict:
    opportunities = [event for row in rows for event in row["opportunities"]]
    feasible = [event for event in opportunities if event["feasible"]]
    kinds = ("cashout_then_fell", "harvest_bank_fell")
    return {
        "fixtures": len(rows),
        "opportunities": len(opportunities),
        "feasible_opportunities": len(feasible),
        "games_with_feasible_opportunity": len(
            {
                row["game_id"]
                for row in rows
                if any(event["feasible"] for event in row["opportunities"])
            }
        ),
        "by_kind": {
            kind: {
                "observed": sum(event["kind"] == kind for event in opportunities),
                "feasible": sum(event["kind"] == kind for event in feasible),
                "feasible_episodes": feasible_episode_count(rows, kind),
                "selected_immediate_first_verb": sum(
                    event["kind"] == kind
                    and any(
                        command.split()[0].upper()
                        == ("DROP" if kind == "cashout_then_fell" else "HARVEST")
                        for command in event["next_commands"]
                        if command.split()
                    )
                    for event in feasible
                ),
            }
            for kind in kinds
        },
        "median_feasible_slack": statistics.median(
            event["remaining_turns"] - event["eta"] for event in feasible
        )
        if feasible
        else None,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/terminal-bundle-telemetry.json",
    )
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    rows = [analyze_fixture(MANIFEST.parent / row["file"]) for row in manifest["fixtures"]]
    payload = {
        "schema": 1,
        "scope": "static terminal bundle feasibility on validated historical fixtures",
        "assumptions": "single worker, no growth, no opponent interference, observed turns remaining",
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
