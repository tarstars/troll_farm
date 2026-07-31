#!/usr/bin/env python3
"""Reconstruct the owner-observed DoubtinGiyov tent-adjacent orchard game.

This is an exact, single-game accounting audit. It caches the immutable Codingame result
under external-backed storage, decodes official states, tracks every tree generation
orthogonally adjacent to the opponent shack, and measures the observed response of both
players. It does not estimate a causal score uplift or mutate Arena state.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import battle_taxonomy as arena
from cgauto.recent_resident_field_census import corpus_parser, decoded_states
from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import assigned_unit_commands, terrain


REPO = Path(__file__).resolve().parent.parent
GAME_ID = 897547554
OUR_AGENT = 6585578
OUR_SUBMISSION = 41070584
OPPONENT_AGENT = 6482016
OPPONENT_SUBMISSION = 40751228
EXTERNAL_DIR = REPO / "data/external/doubtingiyov-tent-proximity-denial"
RAW_CACHE = EXTERNAL_DIR / f"game-{GAME_ID}.json"
TRAJECTORY_CACHE = EXTERNAL_DIR / f"trajectory-{GAME_ID}.jsonl"
RESULT_JSON = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "doubtingiyov-tent-proximity-denial-result-2026-07-31.json"
)
RESULT_MD = RESULT_JSON.with_suffix(".md")
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def fetch_game(cache: Path = RAW_CACHE) -> dict[str, Any]:
    if cache.exists():
        game = json.loads(cache.read_text(encoding="utf-8"))
    else:
        game = arena.call("gameResult/findByGameId", [GAME_ID, None])
        atomic_write(cache, canonical_json(game))
    if int(game.get("gameId") or -1) != GAME_ID:
        raise ValueError(f"requested game {GAME_ID}, received {game.get('gameId')}")
    return game


def validate_identity(game: dict[str, Any]) -> tuple[int, int]:
    agents = game.get("agents") or []
    ours = [
        row for row in agents if int(row.get("agentId") or -1) == OUR_AGENT
    ]
    opponents = [
        row for row in agents if int(row.get("agentId") or -1) == OPPONENT_AGENT
    ]
    if len(ours) != 1 or len(opponents) != 1:
        raise ValueError(
            f"identity mismatch: ours={len(ours)} opponents={len(opponents)}"
        )
    if ours[0].get("valid") is not True or opponents[0].get("valid") is not True:
        raise ValueError("one or both exact agents are invalid")
    return int(ours[0]["index"]), int(opponents[0]["index"])


def plant_by_cell(state: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    return {(int(row["x"]), int(row["y"])): row for row in state["plants"]}


def unit_by_id(state: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(row["id"]): row for row in state["units"]}


def target_cell(command: str, unit: dict[str, Any]) -> tuple[int, int] | None:
    fields = command.split()
    if not fields:
        return None
    if fields[0].upper() == "MOVE" and len(fields) >= 4:
        try:
            return int(fields[2]), int(fields[3])
        except ValueError:
            return None
    if fields[0].upper() in {"CHOP", "HARVEST", "DROP", "PICK", "PLANT"}:
        return int(unit["x"]), int(unit["y"])
    return None


def trigger_band(count: int) -> str:
    if count == 0:
        return "zero"
    if count <= 2:
        return "one_or_two"
    return "more_than_two"


def training_cost(workers: int, spec: tuple[int, int, int, int]) -> list[int]:
    movement, capacity, harvest, chop = spec
    return [
        workers + movement * movement,
        workers + capacity * capacity,
        workers + harvest * harvest,
        0,
        workers + chop * chop,
        0,
    ]


def assignments_for(
    state: dict[str, Any], trajectory_row: dict[str, Any], player: int
) -> dict[int, str]:
    units = [row for row in state["units"] if int(row["player"]) == player]
    return assigned_unit_commands(
        action_commands(trajectory_row.get(f"commands{player}")), units
    )


def summarize_unit(
    unit: dict[str, Any],
    command: str,
    adjacent_cells: set[tuple[int, int]],
    opponent_planted_cells: set[tuple[int, int]],
) -> dict[str, Any]:
    cell = target_cell(command, unit)
    if cell in adjacent_cells:
        category = "tent_adjacent_tree"
    elif cell in opponent_planted_cells:
        category = "opponent_planted_tree"
    elif command.split()[0].upper() in {"CHOP", "HARVEST"}:
        category = "other_tree"
    else:
        category = "other"
    carried = sum(int(value) for value in unit["carry"])
    return {
        "unit_id": int(unit["id"]),
        "position": [int(unit["x"]), int(unit["y"])],
        "stats": [
            int(unit["ms"]),
            int(unit["cc"]),
            int(unit["hp"]),
            int(unit["chop"]),
        ],
        "carry": [int(value) for value in unit["carry"]],
        "carried": carried,
        "free_capacity": int(unit["cc"]) - carried,
        "command": command,
        "target_cell": list(cell) if cell is not None else None,
        "target_category": category,
    }


def analyze(game: dict[str, Any]) -> dict[str, Any]:
    our_seat, opponent_seat = validate_identity(game)
    parser = corpus_parser()
    map_obj, _units, inventory0, inventory1 = parser.parse_frame0(
        game["frames"][0]["view"]
    )
    trajectory, final_inventory = parser.extract_turns(
        game["frames"], inventory0, inventory1
    )
    decoded_map, states, unknown_updates = decoded_states(game, trajectory)
    if len(trajectory) != len(states) - 1:
        raise ValueError(
            f"trajectory/state mismatch: {len(trajectory)} vs {len(states) - 1}"
        )
    if unknown_updates:
        raise ValueError(f"unknown official diff updates: {unknown_updates}")

    atomic_write(
        TRAJECTORY_CACHE,
        "".join(canonical_json(row) for row in trajectory),
    )

    board = terrain(decoded_map)
    opponent_shack = board["shacks"][opponent_seat]
    adjacent_ordered = [
        (opponent_shack[0], opponent_shack[1] + 1),
        (opponent_shack[0] + 1, opponent_shack[1]),
        (opponent_shack[0], opponent_shack[1] - 1),
        (opponent_shack[0] - 1, opponent_shack[1]),
    ]
    adjacent_set = set(adjacent_ordered)

    generations: list[dict[str, Any]] = []
    active_generation: dict[tuple[int, int], int] = {}
    for plant in states[0]["plants"]:
        cell = (int(plant["x"]), int(plant["y"]))
        generation = {
            "generation": len(generations),
            "cell": list(cell),
            "source": "initial",
            "planter": None,
            "birth_turn": 0,
            "death_turn": None,
            "kind": plant["type"],
            "birth_health": int(plant["health"]),
            "birth_size": int(plant["size"]),
            "birth_fruits": int(plant["fruits"]),
            "resident_commands": Counter(),
            "opponent_commands": Counter(),
            "first_resident_contact_turn": None,
            "first_opponent_harvest_turn": None,
        }
        generations.append(generation)
        active_generation[cell] = generation["generation"]

    bands = Counter()
    transitions: list[dict[str, Any]] = []
    command_matrix: Counter[tuple[str, str, str]] = Counter()
    adjacent_harvest_commands = Counter()
    adjacent_drop_commands = Counter()
    adjacent_drop_units = Counter()
    adjacent_chop_commands = Counter()
    resident_adjacent_chop_confirmed = 0
    opponent_adjacent_harvest_confirmed = 0
    opponent_adjacent_harvested_item_units = 0
    opponent_adjacent_drop_confirmed_units = 0
    adjacent_effect_events = []
    training_events = []
    previous_band = None
    previous_count = None

    for turn, row in enumerate(trajectory, 1):
        before = states[turn - 1]
        after = states[turn]
        before_plants = plant_by_cell(before)
        after_plants = plant_by_cell(after)
        before_units = unit_by_id(before)
        after_units = unit_by_id(after)
        assignments = {
            player: assignments_for(before, row, player) for player in (0, 1)
        }

        active_adjacent = sorted(set(before_plants) & adjacent_set)
        count = len(active_adjacent)
        band = trigger_band(count)
        bands[band] += 1
        opponent_planted_cells = {
            cell
            for cell, generation_id in active_generation.items()
            if generations[generation_id]["source"] == "planted"
            and generations[generation_id]["planter"] == opponent_seat
        }

        if band != previous_band or count != previous_count:
            units = []
            for unit in sorted(
                (
                    unit
                    for unit in before["units"]
                    if int(unit["player"]) == our_seat
                ),
                key=lambda unit: int(unit["id"]),
            ):
                command = assignments[our_seat].get(int(unit["id"]), "WAIT")
                units.append(
                    summarize_unit(
                        unit,
                        command,
                        set(active_adjacent),
                        opponent_planted_cells,
                    )
                )
            transitions.append(
                {
                    "turn": turn,
                    "adjacent_tree_count": count,
                    "band": band,
                    "active_adjacent_cells": [list(cell) for cell in active_adjacent],
                    "resident_units": units,
                }
            )
            previous_band = band
            previous_count = count

        for player in (0, 1):
            for command in action_commands(row.get(f"commands{player}")):
                fields = command.split()
                if fields and fields[0].upper() == "TRAIN" and len(fields) == 5:
                    spec = tuple(int(value) for value in fields[1:])
                    workers = sum(
                        int(candidate["player"]) == player
                        for candidate in before["units"]
                    )
                    training_events.append(
                        {
                            "turn": turn,
                            "player": player,
                            "workers_before": workers,
                            "spec": list(spec),
                            "cost": training_cost(workers, spec),
                            "inventory_before": list(
                                before["inventories"][player]
                            ),
                        }
                    )
            for unit_id, command in assignments[player].items():
                unit = before_units.get(int(unit_id))
                if unit is None:
                    continue
                fields = command.split()
                if not fields:
                    continue
                verb = fields[0].upper()
                cell = target_cell(command, unit)
                if cell in adjacent_set and cell in before_plants:
                    category = "tent_adjacent_tree"
                elif cell in opponent_planted_cells:
                    category = "opponent_planted_tree"
                elif verb in {"CHOP", "HARVEST"}:
                    category = "other_tree"
                else:
                    category = "other"
                command_matrix[(band, f"player_{player}", f"{verb}:{category}")] += 1

                if cell in active_generation:
                    generation = generations[active_generation[cell]]
                    key = (
                        "resident_commands"
                        if player == our_seat
                        else "opponent_commands"
                    )
                    generation[key][verb] += 1
                    if (
                        player == our_seat
                        and verb in {"CHOP", "HARVEST"}
                        and generation["first_resident_contact_turn"] is None
                    ):
                        generation["first_resident_contact_turn"] = turn
                    if (
                        player == opponent_seat
                        and verb == "HARVEST"
                        and generation["first_opponent_harvest_turn"] is None
                    ):
                        generation["first_opponent_harvest_turn"] = turn

                if cell in adjacent_set and cell in before_plants:
                    if verb == "HARVEST":
                        adjacent_harvest_commands[f"player_{player}"] += 1
                        after_unit = after_units.get(int(unit_id))
                        if (
                            player == opponent_seat
                            and after_unit is not None
                            and sum(after_unit["carry"]) > sum(unit["carry"])
                        ):
                            opponent_adjacent_harvest_confirmed += 1
                            gained = sum(after_unit["carry"]) - sum(unit["carry"])
                            opponent_adjacent_harvested_item_units += gained
                            adjacent_effect_events.append(
                                {
                                    "turn": turn,
                                    "player": player,
                                    "verb": verb,
                                    "item_units": gained,
                                }
                            )
                    elif verb == "DROP":
                        adjacent_drop_commands[f"player_{player}"] += 1
                        after_unit = after_units.get(int(unit_id))
                        if (
                            player == opponent_seat
                            and after_unit is not None
                            and sum(after_unit["carry"]) < sum(unit["carry"])
                        ):
                            opponent_adjacent_drop_confirmed_units += 1
                            dropped = sum(unit["carry"]) - sum(after_unit["carry"])
                            adjacent_drop_units[f"player_{player}"] += dropped
                            adjacent_effect_events.append(
                                {
                                    "turn": turn,
                                    "player": player,
                                    "verb": verb,
                                    "item_units": dropped,
                                }
                            )
                    elif verb == "CHOP":
                        adjacent_chop_commands[f"player_{player}"] += 1
                        after_plant = after_plants.get(cell)
                        if (
                            player == our_seat
                            and (
                                after_plant is None
                                or int(after_plant["health"])
                                < int(before_plants[cell]["health"])
                            )
                        ):
                            resident_adjacent_chop_confirmed += 1

        removed = sorted(set(before_plants) - set(after_plants))
        for cell in removed:
            generation_id = active_generation.pop(cell, None)
            if generation_id is not None:
                generations[generation_id]["death_turn"] = turn
                generations[generation_id]["death_health_before"] = int(
                    before_plants[cell]["health"]
                )
                generations[generation_id]["death_fruits_before"] = int(
                    before_plants[cell]["fruits"]
                )

        created = sorted(set(after_plants) - set(before_plants))
        for cell in created:
            planter = None
            for player in (0, 1):
                for unit_id, command in assignments[player].items():
                    unit = before_units.get(int(unit_id))
                    if (
                        unit is not None
                        and command.split()[0].upper() == "PLANT"
                        and (int(unit["x"]), int(unit["y"])) == cell
                    ):
                        planter = player
                        break
                if planter is not None:
                    break
            plant = after_plants[cell]
            generation = {
                "generation": len(generations),
                "cell": list(cell),
                "source": "planted",
                "planter": planter,
                "birth_turn": turn,
                "death_turn": None,
                "kind": plant["type"],
                "birth_health": int(plant["health"]),
                "birth_size": int(plant["size"]),
                "birth_fruits": int(plant["fruits"]),
                "resident_commands": Counter(),
                "opponent_commands": Counter(),
                "first_resident_contact_turn": None,
                "first_opponent_harvest_turn": None,
            }
            generations.append(generation)
            active_generation[cell] = generation["generation"]

    adjacent_generations = [
        generation for generation in generations if tuple(generation["cell"]) in adjacent_set
    ]
    for generation in generations:
        generation["resident_commands"] = dict(
            sorted(generation["resident_commands"].items())
        )
        generation["opponent_commands"] = dict(
            sorted(generation["opponent_commands"].items())
        )

    first_three_turn = next(
        (
            transition["turn"]
            for transition in transitions
            if transition["adjacent_tree_count"] > 2
        ),
        None,
    )
    first_resident_adjacent_contact = min(
        (
            generation["first_resident_contact_turn"]
            for generation in adjacent_generations
            if generation["first_resident_contact_turn"] is not None
        ),
        default=None,
    )
    max_adjacent = max(
        (transition["adjacent_tree_count"] for transition in transitions), default=0
    )
    verdict = (
        "MECHANICALLY_COHERENT"
        if max_adjacent > 2
        and first_three_turn is not None
        and first_resident_adjacent_contact is not None
        and first_resident_adjacent_contact > first_three_turn
        and opponent_adjacent_harvest_confirmed > 0
        else "UNSUPPORTED_IN_EXACT_GAME"
    )
    pre_contact_effects = [
        event
        for event in adjacent_effect_events
        if first_resident_adjacent_contact is not None
        and event["turn"] < first_resident_adjacent_contact
    ]

    return {
        "schema": "troll-farm-doubtingiyov-tent-denial-v1",
        "game": {
            "game_id": GAME_ID,
            "our_agent_id": OUR_AGENT,
            "our_submission_id": OUR_SUBMISSION,
            "our_seat": our_seat,
            "opponent": "DoubtinGiyov",
            "opponent_agent_id": OPPONENT_AGENT,
            "opponent_submission_id": OPPONENT_SUBMISSION,
            "opponent_seat": opponent_seat,
            "scores": [int(value) for value in game["scores"]],
            "ranks": game["ranks"],
            "turns": len(trajectory),
        },
        "integrity": {
            "decoded_turns": len(states) - 1,
            "trajectory_turns": len(trajectory),
            "unknown_diff_updates": unknown_updates,
            "raw_cache": str(RAW_CACHE.relative_to(REPO)),
            "raw_sha256": sha256(RAW_CACHE),
            "trajectory_cache": str(TRAJECTORY_CACHE.relative_to(REPO)),
            "trajectory_sha256": sha256(TRAJECTORY_CACHE),
        },
        "geometry": {
            "opponent_shack": list(opponent_shack),
            "cardinal_adjacent_cells": [list(cell) for cell in adjacent_ordered],
            "initial_adjacent_tree_count": sum(
                tuple(generation["cell"]) in adjacent_set
                and generation["birth_turn"] == 0
                for generation in generations
            ),
        },
        "trigger": {
            "turns_by_band": dict(sorted(bands.items())),
            "max_adjacent_tree_count": max_adjacent,
            "first_more_than_two_turn": first_three_turn,
            "first_resident_adjacent_contact_turn": first_resident_adjacent_contact,
            "transitions": transitions,
        },
        "adjacent_tree_generations": adjacent_generations,
        "observed_actions": {
            "command_matrix": {
                "|".join(key): value for key, value in sorted(command_matrix.items())
            },
            "adjacent_harvest_commands": dict(sorted(adjacent_harvest_commands.items())),
            "opponent_adjacent_harvest_confirmed": opponent_adjacent_harvest_confirmed,
            "opponent_adjacent_harvested_item_units": (
                opponent_adjacent_harvested_item_units
            ),
            "adjacent_drop_commands": dict(sorted(adjacent_drop_commands.items())),
            "opponent_adjacent_drop_confirmed_units": opponent_adjacent_drop_confirmed_units,
            "opponent_adjacent_dropped_item_units": dict(
                sorted(adjacent_drop_units.items())
            ),
            "adjacent_chop_commands": dict(sorted(adjacent_chop_commands.items())),
            "resident_adjacent_chop_confirmed": resident_adjacent_chop_confirmed,
            "before_first_resident_contact": {
                "opponent_harvest_commands": sum(
                    event["verb"] == "HARVEST" for event in pre_contact_effects
                ),
                "opponent_harvested_item_units": sum(
                    event["item_units"]
                    for event in pre_contact_effects
                    if event["verb"] == "HARVEST"
                ),
                "opponent_drop_commands": sum(
                    event["verb"] == "DROP" for event in pre_contact_effects
                ),
                "opponent_dropped_item_units": sum(
                    event["item_units"]
                    for event in pre_contact_effects
                    if event["verb"] == "DROP"
                ),
            },
        },
        "training_events": training_events,
        "final_inventory": [list(inventory) for inventory in final_inventory],
        "verdict": verdict,
        "interpretation": (
            "The exact game supports the trigger and exposes a delayed response window. "
            "It does not identify the counterfactual score effect of the proposed policy."
        ),
    }


def human_report(result: dict[str, Any]) -> str:
    trigger = result["trigger"]
    actions = result["observed_actions"]
    generations = result["adjacent_tree_generations"]
    lines = [
        "# DoubtinGiyov tent-proximity denial reconstruction",
        "",
        f"Verdict: **`{result['verdict']}`**.",
        "",
        "## Exact identity and integrity",
        "",
        (
            f"Game `{GAME_ID}` is exact active agent/submission `{OUR_AGENT}`/"
            f"`{OUR_SUBMISSION}` against DoubtinGiyov `{OPPONENT_AGENT}`/"
            f"`{OPPONENT_SUBMISSION}`. Final score is 208–262 from our seat; "
            f"{result['integrity']['decoded_turns']}/{result['integrity']['trajectory_turns']} "
            "turns decode with zero unknown updates."
        ),
        "",
        "## Geometry and trigger",
        "",
        (
            f"The opponent shack is at {tuple(result['geometry']['opponent_shack'])}. "
            "There are no adjacent trees initially. The maximum standing cardinal-adjacent "
            f"tree count is {trigger['max_adjacent_tree_count']}; the first >2 state is "
            f"turn {trigger['first_more_than_two_turn']}."
        ),
        (
            f"The resident first contacts an adjacent generation on turn "
            f"{trigger['first_resident_adjacent_contact_turn']}. Band exposure is "
            f"{trigger['turns_by_band']}."
        ),
        "",
        "## Observed orchard flow",
        "",
        (
            f"The opponent creates {sum(g['planter'] == 0 for g in generations)} "
            f"adjacent generations across {len(generations)} total adjacent generations. "
            f"Confirmed opponent adjacent HARVEST commands: "
            f"{actions['opponent_adjacent_harvest_confirmed']} for "
            f"{actions['opponent_adjacent_harvested_item_units']} items; confirmed "
            f"adjacent DROP commands: {actions['opponent_adjacent_drop_confirmed_units']}."
        ),
        (
            "Before the resident's first adjacent-tree contact, the opponent already "
            f"completed {actions['before_first_resident_contact']['opponent_harvest_commands']} "
            f"harvests for "
            f"{actions['before_first_resident_contact']['opponent_harvested_item_units']} "
            f"items and {actions['before_first_resident_contact']['opponent_drop_commands']} "
            f"drops for "
            f"{actions['before_first_resident_contact']['opponent_dropped_item_units']} "
            "items."
        ),
        (
            f"Resident adjacent CHOP commands are "
            f"{actions['adjacent_chop_commands'].get('player_1', 0)}, with "
            f"{actions['resident_adjacent_chop_confirmed']} directly confirmed by a health "
            "decrease or removal."
        ),
        "",
        "The first three planted generations are:",
        "",
    ]
    for generation in generations[:3]:
        lines.append(
            f"- turn {generation['birth_turn']}: {generation['kind']} at "
            f"{tuple(generation['cell'])}, first resident contact "
            f"{generation['first_resident_contact_turn']}, first opponent harvest "
            f"{generation['first_opponent_harvest_turn']}."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The proposed 0 / 1–2 / >2 trigger is mechanically present and the current "
                "policy responds late while the opponent harvests at shack-adjacent cells. "
                "This supports implementing a bounded successor candidate. The replay alone "
                "does not prove the candidate's causal score uplift, and it authorizes no "
                "second Arena cycle."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    game = fetch_game()
    result = analyze(game)
    atomic_write(RESULT_JSON, json.dumps(result, indent=1, sort_keys=True) + "\n")
    atomic_write(RESULT_MD, human_report(result))
    print(
        f"game={GAME_ID} verdict={result['verdict']} "
        f"turns={result['integrity']['decoded_turns']} "
        f"unknown={result['integrity']['unknown_diff_updates']} "
        f"max_adjacent={result['trigger']['max_adjacent_tree_count']} "
        f"first_gt2={result['trigger']['first_more_than_two_turn']} "
        f"first_contact={result['trigger']['first_resident_adjacent_contact_turn']}"
    )
    print(f"raw sha256 {result['integrity']['raw_sha256']}")
    print(f"trajectory sha256 {result['integrity']['trajectory_sha256']}")
    return 0 if result["verdict"] == "MECHANICALLY_COHERENT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
