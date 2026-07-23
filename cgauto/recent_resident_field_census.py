#!/usr/bin/env python3
"""Read-only, effect-level census of the resident's recent arena battles.

The older :mod:`cgauto.battle_taxonomy` report counts emitted commands.  This
study additionally parses referee-confirmed effects, score composition, fixed
turn state, and opening geometry.  It is diagnostic only: it never starts a
game, submits code, or changes arena state.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import importlib.util
import json
import math
from pathlib import Path
import re
import statistics
import sys
from typing import Callable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.replay_conformance import action_commands, effective_chop_unit_ids
from cgauto.replay_state import DiffDecoder, view_payload
from cgauto.top_player_opening_analysis import (
    adjacent,
    assigned_unit_commands,
    bfs,
    opening_features,
    terrain,
)

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "recent-resident-field-census-2026-07-18.json"
)
USER_ID = 1302251
CUTS = (50, 75, 100, 150, 200, 225, 300)
PHASE_CUTS = (50, 75, 100)
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
ITEM_INDEX = {item: index for index, item in enumerate(ITEMS)}


@lru_cache(maxsize=1)
def corpus_parser():
    """Load the checked-in replay parser without making ``data`` a package."""

    path = REPO / "data/scripts/parse.py"
    spec = importlib.util.spec_from_file_location("troll_farm_corpus_parser", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load replay parser from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def score(inventory: list[int] | tuple[int, ...] | None) -> int | None:
    if inventory is None:
        return None
    return sum(inventory[:4]) + 4 * inventory[5]


def inventory_after(
    turns: list[dict], final_inventory: tuple[list[int], list[int]], player: int, turn: int
) -> list[int] | None:
    """Return the inventory after a resolved turn, or ``None`` after game end."""

    if turn < len(turns):
        return list(turns[turn][f"inv{player}"])
    if turn == len(turns):
        return list(final_inventory[player])
    return None


def successful_events(frames: list[dict]) -> dict[int, list[dict]]:
    """Extract referee-confirmed productive events with their resolved turn."""

    events = {0: [], 1: []}
    turn = 1
    for frame in frames[1:]:
        for line in (frame.get("summary") or "").splitlines():
            match = re.match(r"\$([01]): (.*)", line)
            if not match:
                continue
            player = int(match.group(1))
            message = match.group(2)
            if message.startswith("[failed]"):
                continue
            event = None
            if "trained a troll" in message:
                event = {"turn": turn, "kind": "TRAIN", "amount": 1}
            elif found := re.search(r"planted a (\w+)", message):
                event = {
                    "turn": turn,
                    "kind": "PLANT",
                    "amount": 1,
                    "item": found.group(1).upper(),
                }
            elif found := re.search(r"harvested (\d+) (\w+)", message):
                event = {
                    "turn": turn,
                    "kind": "HARVEST",
                    "amount": int(found.group(1)),
                    "item": found.group(2).upper(),
                }
            elif re.search(r"(?:damaged a tree|collected \d+ WOOD)$", message):
                event = {"turn": turn, "kind": "CHOP", "amount": 1}
            elif found := re.search(r"dropped (\d+) items? to the shack", message):
                event = {
                    "turn": turn,
                    "kind": "DROP",
                    "amount": int(found.group(1)),
                }
            if event is not None:
                events[player].append(event)
        view = frame.get("view") or ""
        if frame.get("keyframe") and "{" in view:
            turn += 1
    return events


def event_amount(events: list[dict], kind: str, through: int | None = None) -> int:
    return sum(
        event["amount"]
        for event in events
        if event["kind"] == kind and (through is None or event["turn"] <= through)
    )


def side_snapshot(
    inventory: list[int] | None, events: list[dict], through: int
) -> dict | None:
    if inventory is None:
        return None
    return {
        "inventory": inventory,
        "score": score(inventory),
        "fruit": sum(inventory[:4]),
        "wood": inventory[5],
        "workers": 1 + event_amount(events, "TRAIN", through),
        "successful_trains": event_amount(events, "TRAIN", through),
        "successful_plants": event_amount(events, "PLANT", through),
        "harvested_fruit": event_amount(events, "HARVEST", through),
        "chops_landed": event_amount(events, "CHOP", through),
        "dropped_items": event_amount(events, "DROP", through),
    }


def decoded_states(game: dict, trajectory: list[dict]) -> tuple[dict, list[dict], int]:
    """Decode exact official states directly from an in-memory game result."""

    initial = view_payload(game["frames"][0]["view"])
    if initial is None:
        raise ValueError(f"game {game.get('gameId')} has no initial payload")
    header, *rows = initial["global"]["inputmodule"].splitlines()
    width, height = (int(value) for value in header.split())
    decoder = DiffDecoder()
    decoder.apply(initial["frame"].get("diff", ""), 0)
    inventories = [
        [int(value) for value in line.split()]
        for line in initial["frame"]["inputmodule"].splitlines()
    ]
    states = [decoder.snapshot(0, inventories)]
    chop_ids = []
    for row in trajectory:
        commands = [
            action_commands(row.get(f"commands{player}")) for player in (0, 1)
        ]
        chop_ids.append(
            effective_chop_unit_ids(commands[0])
            + effective_chop_unit_ids(commands[1])
        )
    resolved_turn = 0
    for frame_index, frame in enumerate(game["frames"][1:], 1):
        if not frame.get("keyframe"):
            continue
        payload = view_payload(frame.get("view") or "")
        if payload is None:
            continue
        decoder.apply_known_chops(
            chop_ids[resolved_turn] if resolved_turn < len(chop_ids) else []
        )
        decoder.tick_existing_plants()
        decoder.apply(payload.get("diff", ""), frame_index)
        if payload.get("inputmodule"):
            inventories = [
                [int(value) for value in line.split()]
                for line in payload["inputmodule"].splitlines()
            ]
        resolved_turn += 1
        states.append(decoder.snapshot(resolved_turn, inventories))
    return {"width": width, "height": height, "rows": rows}, states, len(
        decoder.unknown_updates
    )


def unit_eta(
    distances: dict[tuple[int, int], int], unit: dict, walkable: set[tuple[int, int]]
) -> int | None:
    cell = (unit["x"], unit["y"])
    distance = distances.get(cell)
    if distance is None:
        alternatives = [
            distances[next_cell] + 1
            for next_cell in adjacent(cell)
            if next_cell in walkable and next_cell in distances
        ]
        distance = min(alternatives) if alternatives else None
    if distance is None:
        return None
    return math.ceil(distance / max(unit["ms"], 1))


def crop_provenance(game: dict, trajectory: list[dict], me: int) -> tuple[list[dict], dict]:
    """Attribute planted-tree fruit/wood and interception from official states."""

    map_data, states, unknown_updates = decoded_states(game, trajectory)
    board = terrain(map_data)
    usable = min(len(states) - 1, len(trajectory))
    active: dict[tuple[int, int], dict] = {}
    records = []
    for turn in range(1, usable + 1):
        before = states[turn - 1]
        after = states[turn]
        before_plants = {
            (plant["x"], plant["y"]): plant for plant in before["plants"]
        }
        after_plants = {
            (plant["x"], plant["y"]): plant for plant in after["plants"]
        }
        before_units = {
            unit["id"]: unit for unit in before["units"]
        }
        after_units = {unit["id"]: unit for unit in after["units"]}
        assigned = {}
        for player in (0, 1):
            units = [unit for unit in before["units"] if unit["player"] == player]
            assigned[player] = assigned_unit_commands(
                action_commands(trajectory[turn - 1].get(f"commands{player}")),
                units,
            )

        # Attribute work performed on already-existing planted generations.
        for cell, record in list(active.items()):
            if cell not in before_plants:
                record["death_turn"] = turn - 1
                active.pop(cell, None)
                continue
            for player in (0, 1):
                for unit_id, command in assigned[player].items():
                    unit = before_units.get(unit_id)
                    if unit is None or (unit["x"], unit["y"]) != cell:
                        continue
                    verb = command.split()[0].upper()
                    if verb not in ("CHOP", "HARVEST"):
                        continue
                    after_unit = after_units.get(unit_id)
                    gained = [0] * 6
                    if after_unit is not None:
                        gained = [
                            max(0, after_unit["carry"][index] - unit["carry"][index])
                            for index in range(6)
                        ]
                    if verb == "CHOP":
                        record["chop_turns"][player].append(turn)
                        record["wood_collected"][player] += gained[ITEM_INDEX["WOOD"]]
                    else:
                        record["harvest_turns"][player].append(turn)
                        record["fruit_harvested"][player] += sum(gained[:4])
            if cell not in after_plants:
                record["death_turn"] = turn
                active.pop(cell, None)

        # A successful plant is an empty-before / occupied-after cell with at
        # least one matching PLANT command from a unit standing on that cell.
        for cell, plant in after_plants.items():
            if cell in before_plants:
                continue
            creators = []
            for player in (0, 1):
                for unit_id, command in assigned[player].items():
                    fields = command.split()
                    unit = before_units.get(unit_id)
                    if (
                        len(fields) >= 3
                        and fields[0].upper() == "PLANT"
                        and unit is not None
                        and (unit["x"], unit["y"]) == cell
                        and fields[2].upper() == plant["type"]
                    ):
                        creators.append(player)
            creator_players = sorted(set(creators))
            if not creator_players:
                continue
            distances = bfs(board["walkable"], [cell])
            etas = {
                player: min(
                    (
                        eta
                        for unit in before["units"]
                        if unit["player"] == player
                        and (eta := unit_eta(distances, unit, board["walkable"]))
                        is not None
                    ),
                    default=None,
                )
                for player in (0, 1)
            }
            shack_distances = {}
            for player, shack in enumerate(board["shacks"]):
                doors = [door for door in adjacent(shack) if door in board["walkable"]]
                from_doors = bfs(board["walkable"], doors)
                shack_distances[player] = from_doors.get(cell)
            record = {
                "cell": list(cell),
                "type": plant["type"],
                "birth_turn": turn,
                "death_turn": None,
                "creators": creator_players,
                "birth_eta": etas,
                "shack_distance": shack_distances,
                "chop_turns": {0: [], 1: []},
                "harvest_turns": {0: [], 1: []},
                "wood_collected": {0: 0, 1: 0},
                "fruit_harvested": {0: 0, 1: 0},
            }
            active[cell] = record
            records.append(record)

    for record in active.values():
        record["survived_to_end"] = True
    relative = []
    opponent = 1 - me
    for record in records:
        if record["creators"] != [opponent]:
            continue
        our_contacts = sorted(record["chop_turns"][me] + record["harvest_turns"][me])
        their_harvests = record["harvest_turns"][opponent]
        relative.append(
            {
                "cell": record["cell"],
                "type": record["type"],
                "birth_turn": record["birth_turn"],
                "death_turn": record["death_turn"],
                "survived_to_end": record.get("survived_to_end", False),
                "our_eta_at_birth": record["birth_eta"][me],
                "opponent_eta_at_birth": record["birth_eta"][opponent],
                "our_shack_distance": record["shack_distance"][me],
                "opponent_shack_distance": record["shack_distance"][opponent],
                "our_chop_turns": record["chop_turns"][me],
                "our_harvest_turns": record["harvest_turns"][me],
                "opponent_chop_turns": record["chop_turns"][opponent],
                "opponent_harvest_turns": their_harvests,
                "our_wood_collected": record["wood_collected"][me],
                "opponent_wood_collected": record["wood_collected"][opponent],
                "our_fruit_harvested": record["fruit_harvested"][me],
                "opponent_fruit_harvested": record["fruit_harvested"][opponent],
                "first_our_contact_turn": our_contacts[0] if our_contacts else None,
                "first_opponent_harvest_turn": (
                    their_harvests[0] if their_harvests else None
                ),
            }
        )
    return relative, {
        "decoded_turns": len(states) - 1,
        "trajectory_turns": len(trajectory),
        "unknown_diff_updates": unknown_updates,
        "all_attributed_plants": len(records),
        "opponent_exclusive_plants": len(relative),
    }


def summarize_crop_records(records: list[dict]) -> dict:
    contacted = [record for record in records if record["first_our_contact_turn"] is not None]
    reachable_20 = [
        record
        for record in records
        if record["our_eta_at_birth"] is not None and record["our_eta_at_birth"] <= 20
    ]
    harvested_first = [
        record
        for record in records
        if record["first_opponent_harvest_turn"] is not None
        and (
            record["first_our_contact_turn"] is None
            or record["first_opponent_harvest_turn"] < record["first_our_contact_turn"]
        )
    ]
    etas = [record["our_eta_at_birth"] for record in records if record["our_eta_at_birth"] is not None]
    return {
        "crops": len(records),
        "types": dict(sorted(Counter(record["type"] for record in records).items())),
        "our_contacted_crops": len(contacted),
        "our_interception_rate": len(contacted) / len(records) if records else 0.0,
        "our_chopped_crops": sum(bool(record["our_chop_turns"]) for record in records),
        "our_harvested_crops": sum(bool(record["our_harvest_turns"]) for record in records),
        "our_wood_collected": sum(record["our_wood_collected"] for record in records),
        "our_fruit_harvested": sum(record["our_fruit_harvested"] for record in records),
        "opponent_wood_collected": sum(
            record["opponent_wood_collected"] for record in records
        ),
        "opponent_fruit_harvested": sum(
            record["opponent_fruit_harvested"] for record in records
        ),
        "reachable_within_20_at_birth": len(reachable_20),
        "reachable_20_contacted": sum(
            record["first_our_contact_turn"] is not None for record in reachable_20
        ),
        "opponent_harvested_before_our_contact": len(harvested_first),
        "median_our_eta_at_birth": statistics.median(etas) if etas else None,
        "mean_our_eta_at_birth": statistics.mean(etas) if etas else None,
    }


def current_player(game: dict) -> int | None:
    for index, agent in enumerate(game.get("agents") or []):
        if (agent.get("codingamer") or {}).get("userId") == USER_ID:
            return index
    return None


def player_name(agent: dict) -> str:
    codingamer = agent.get("codingamer") or {}
    boss = agent.get("arenaboss") or {}
    return codingamer.get("pseudo") or boss.get("nickname") or "?"


def game_row(game: dict, rank_of: dict[str, tuple[int | None, float | None]]) -> dict | None:
    frames = game.get("frames") or []
    me = current_player(game)
    if me is None or len(frames) < 2 or len(game.get("scores") or []) != 2:
        return None
    opponent = 1 - me
    parser = corpus_parser()
    decoded_map, units, inv0, inv1 = parser.parse_frame0(frames[0]["view"])
    turns, final_inventory = parser.extract_turns(frames, inv0, inv1)
    effects = successful_events(frames)
    crop_records, crop_quality = crop_provenance(game, turns, me)
    agents = game.get("agents") or []
    opponent_name = player_name(agents[opponent])
    opponent_rank, opponent_ladder_score = rank_of.get(opponent_name, (None, None))
    scores = [int(value) for value in game["scores"]]
    ranks = game.get("ranks") or []
    margin = scores[me] - scores[opponent]
    initial_state = {
        "inventories": [inv0, inv1],
        "units": units,
        "plants": decoded_map["trees0"],
    }
    timeline = {}
    for cut in CUTS:
        mine = inventory_after(turns, final_inventory, me, cut)
        theirs = inventory_after(turns, final_inventory, opponent, cut)
        timeline[str(cut)] = {
            "my": side_snapshot(mine, effects[me], cut),
            "opponent": side_snapshot(theirs, effects[opponent], cut),
        }
    final_my = side_snapshot(list(final_inventory[me]), effects[me], len(turns))
    final_opponent = side_snapshot(
        list(final_inventory[opponent]), effects[opponent], len(turns)
    )
    assert final_my is not None and final_opponent is not None
    return {
        "game_id": int(game.get("gameId")),
        "agent_id": (agents[me] or {}).get("agentId"),
        "seat": me,
        "opponent": opponent_name,
        "opponent_agent_id": (agents[opponent] or {}).get("agentId"),
        "opponent_rank": opponent_rank,
        "opponent_ladder_score": opponent_ladder_score,
        "turns": len(turns),
        "won": bool(ranks and ranks[me] == 0 and margin > 0),
        "tied": margin == 0,
        "margin": margin,
        "scores": {"my": scores[me], "opponent": scores[opponent]},
        "final": {"my": final_my, "opponent": final_opponent},
        "timeline": timeline,
        "opening": opening_features(decoded_map, initial_state, me),
        "opponent_crop_summary": summarize_crop_records(crop_records),
        "opponent_crop_records": crop_records,
        "crop_attribution_quality": crop_quality,
    }


def mean(rows: list[dict], getter: Callable[[dict], int | float | None]) -> float | None:
    values = [value for row in rows if (value := getter(row)) is not None]
    return statistics.mean(values) if values else None


def side_means(rows: list[dict], side: str) -> dict:
    return {
        field: mean(rows, lambda row, f=field: row["final"][side][f])
        for field in (
            "score",
            "fruit",
            "wood",
            "workers",
            "successful_trains",
            "successful_plants",
            "harvested_fruit",
            "chops_landed",
            "dropped_items",
        )
    }


def crop_means(rows: list[dict]) -> dict:
    return {
        field: mean(rows, lambda row, f=field: row["opponent_crop_summary"][f])
        for field in (
            "crops",
            "our_contacted_crops",
            "our_interception_rate",
            "our_chopped_crops",
            "our_harvested_crops",
            "our_wood_collected",
            "our_fruit_harvested",
            "opponent_wood_collected",
            "opponent_fruit_harvested",
            "reachable_within_20_at_birth",
            "reachable_20_contacted",
            "opponent_harvested_before_our_contact",
            "median_our_eta_at_birth",
        )
    }


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {"games": 0}
    timeline = {}
    for cut in CUTS:
        key = str(cut)
        valid = [row for row in rows if row["timeline"][key]["my"] is not None]
        timeline[key] = {
            "games": len(valid),
            "my_score": mean(valid, lambda row, k=key: row["timeline"][k]["my"]["score"]),
            "opponent_score": mean(
                valid, lambda row, k=key: row["timeline"][k]["opponent"]["score"]
            ),
            "my_wood": mean(valid, lambda row, k=key: row["timeline"][k]["my"]["wood"]),
            "opponent_wood": mean(
                valid, lambda row, k=key: row["timeline"][k]["opponent"]["wood"]
            ),
            "opponent_workers": mean(
                valid, lambda row, k=key: row["timeline"][k]["opponent"]["workers"]
            ),
            "opponent_plants": mean(
                valid,
                lambda row, k=key: row["timeline"][k]["opponent"]["successful_plants"],
            ),
        }
    return {
        "games": len(rows),
        "wins": sum(row["won"] for row in rows),
        "ties": sum(row["tied"] for row in rows),
        "mean_margin": mean(rows, lambda row: row["margin"]),
        "minimum_margin": min(row["margin"] for row in rows),
        "maximum_margin": max(row["margin"] for row in rows),
        "my": side_means(rows, "my"),
        "opponent": side_means(rows, "opponent"),
        "opponent_crops": crop_means(rows),
        "timeline": timeline,
    }


def condition_value(row: dict, feature: str) -> float | None:
    cut_text, field = feature.split(":", 1)
    cut = cut_text.removeprefix("t")
    snapshot = row["timeline"][cut]
    mine = snapshot["my"]
    opponent = snapshot["opponent"]
    if mine is None or opponent is None:
        return None
    if field == "opponent_workers":
        return opponent["workers"]
    if field == "opponent_plants":
        return opponent["successful_plants"]
    if field == "opponent_harvest":
        return opponent["harvested_fruit"]
    if field == "opponent_wood":
        return opponent["wood"]
    if field == "wood_gap":
        return opponent["wood"] - mine["wood"]
    if field == "score_gap":
        return opponent["score"] - mine["score"]
    raise KeyError(feature)


def atomic_conditions() -> list[dict]:
    thresholds = {
        "opponent_workers": (2, 3, 4),
        "opponent_plants": (4, 8, 12, 16, 20),
        "opponent_harvest": (5, 10, 20, 30),
        "opponent_wood": (10, 20, 30, 40),
        "wood_gap": (-5, 0, 5, 10),
        "score_gap": (-25, 0, 25, 50),
    }
    return [
        {
            "feature": f"t{cut}:{field}",
            "operator": ">=",
            "threshold": threshold,
            "label": f"t{cut} {field} >= {threshold}",
        }
        for cut in PHASE_CUTS
        for field, values in thresholds.items()
        for threshold in values
    ]


def matches(row: dict, conditions: list[dict]) -> bool:
    for condition in conditions:
        value = condition_value(row, condition["feature"])
        if value is None or value < condition["threshold"]:
            return False
    return True


def rule_report(rows: list[dict], conditions: list[dict]) -> dict:
    selected = [row for row in rows if matches(row, conditions)]
    catastrophic = [row for row in selected if row["margin"] <= -100]
    all_catastrophic = sum(row["margin"] <= -100 for row in rows)
    precision = len(catastrophic) / len(selected) if selected else 0.0
    recall = len(catastrophic) / all_catastrophic if all_catastrophic else 0.0
    beta_sq = 0.25
    f_half = (
        (1 + beta_sq) * precision * recall / (beta_sq * precision + recall)
        if precision and recall
        else 0.0
    )
    by_opponent = Counter(row["opponent"] for row in selected)
    return {
        "conditions": conditions,
        "selected": len(selected),
        "catastrophic": len(catastrophic),
        "precision": precision,
        "recall": recall,
        "f0_5": f_half,
        "mean_final_margin": mean(selected, lambda row: row["margin"]),
        "mean_opponent_final_wood": mean(
            selected, lambda row: row["final"]["opponent"]["wood"]
        ),
        "opponents": len(by_opponent),
        "opponent_counts": dict(sorted(by_opponent.items())),
    }


def early_risk_rules(rows: list[dict]) -> dict:
    atoms = atomic_conditions()
    reports = [rule_report(rows, [atom]) for atom in atoms]
    # Pair only conditions observed by the same cutoff.  This keeps the audit
    # interpretable and avoids an unconstrained classifier search on 80 games.
    for left_index, left in enumerate(atoms):
        for right in atoms[left_index + 1 :]:
            if left["feature"].split(":", 1)[0] != right["feature"].split(":", 1)[0]:
                continue
            if left["feature"] == right["feature"]:
                continue
            reports.append(rule_report(rows, [left, right]))
    eligible = [
        report
        for report in reports
        if report["selected"] >= 5 and report["opponents"] >= 3
    ]
    eligible.sort(
        key=lambda report: (
            report["f0_5"],
            report["precision"],
            report["recall"],
            -report["selected"],
        ),
        reverse=True,
    )
    catastrophic = sum(row["margin"] <= -100 for row in rows)
    return {
        "label": "final margin <= -100",
        "baseline_frequency": catastrophic / len(rows) if rows else 0.0,
        "search_scope": (
            "fixed thresholds over opponent workers/plants/harvest, score, and wood at "
            "turns 50/75/100; univariate and same-cut two-condition conjunctions"
        ),
        "minimum_selected": 5,
        "minimum_distinct_opponents": 3,
        "eligible_rules": len(eligible),
        "top_rules": eligible[:20],
    }


def opening_contrasts(rows: list[dict]) -> list[dict]:
    catastrophic = [row for row in rows if row["margin"] <= -100]
    comparison = [row for row in rows if row["margin"] > -100]
    if not catastrophic or not comparison:
        return []
    names = sorted(set.intersection(*(set(row["opening"]) for row in rows)))
    reports = []
    for name in names:
        cat = [row["opening"][name] for row in catastrophic]
        other = [row["opening"][name] for row in comparison]
        if not all(isinstance(value, (int, float, bool)) for value in cat + other):
            continue
        cat = [float(value) for value in cat]
        other = [float(value) for value in other]
        combined = cat + other
        deviation = statistics.pstdev(combined)
        if deviation == 0:
            continue
        reports.append(
            {
                "feature": name,
                "catastrophic_mean": statistics.mean(cat),
                "other_mean": statistics.mean(other),
                "standardized_difference": (
                    statistics.mean(cat) - statistics.mean(other)
                )
                / deviation,
            }
        )
    reports.sort(key=lambda report: abs(report["standardized_difference"]), reverse=True)
    return reports[:20]


def opponent_volatility(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[row["opponent"]].append(row)
    result = []
    for opponent, group in groups.items():
        if len(group) < 3:
            continue
        result.append(
            {
                "opponent": opponent,
                "games": len(group),
                "wins": sum(row["won"] for row in group),
                "catastrophic_losses": sum(row["margin"] <= -100 for row in group),
                "mean_margin": statistics.mean(row["margin"] for row in group),
                "minimum_margin": min(row["margin"] for row in group),
                "maximum_margin": max(row["margin"] for row in group),
                "margin_range": max(row["margin"] for row in group)
                - min(row["margin"] for row in group),
            }
        )
    result.sort(key=lambda report: report["margin_range"], reverse=True)
    return result


def analyze(rows: list[dict], arena_snapshot: dict) -> dict:
    wins = [row for row in rows if row["margin"] > 0]
    ties = [row for row in rows if row["margin"] == 0]
    losses = [row for row in rows if row["margin"] < 0]
    catastrophic = [row for row in rows if row["margin"] <= -100]
    ordinary_losses = [row for row in rows if -100 < row["margin"] < 0]
    negative_mass = sum(-row["margin"] for row in losses)
    catastrophic_mass = sum(-row["margin"] for row in catastrophic)
    catastrophic_opponents = {row["opponent"] for row in catastrophic}
    tail_share = catastrophic_mass / negative_mass if negative_mass else 0.0
    mechanism_gate = {
        "definition": "final margin <= -100",
        "frequency": len(catastrophic) / len(rows) if rows else 0.0,
        "negative_margin_mass_share": tail_share,
        "distinct_opponents": len(catastrophic_opponents),
        "opponent_wood_gap_vs_noncatastrophic": (
            (mean(catastrophic, lambda row: row["final"]["opponent"]["wood"]) or 0)
            - (mean([row for row in rows if row["margin"] > -100], lambda row: row["final"]["opponent"]["wood"]) or 0)
        ),
        "opponent_crop_wood_gap_vs_noncatastrophic": (
            (
                mean(
                    catastrophic,
                    lambda row: row["opponent_crop_summary"]["opponent_wood_collected"],
                )
                or 0
            )
            - (
                mean(
                    [row for row in rows if row["margin"] > -100],
                    lambda row: row["opponent_crop_summary"]["opponent_wood_collected"],
                )
                or 0
            )
        ),
        "our_crop_interception_rate_gap_vs_noncatastrophic": (
            (
                mean(
                    catastrophic,
                    lambda row: row["opponent_crop_summary"]["our_interception_rate"],
                )
                or 0
            )
            - (
                mean(
                    [row for row in rows if row["margin"] > -100],
                    lambda row: row["opponent_crop_summary"]["our_interception_rate"],
                )
                or 0
            )
        ),
    }
    mechanism_gate["repeated_material_signature"] = bool(
        mechanism_gate["frequency"] >= 0.10
        and tail_share >= 0.50
        and mechanism_gate["distinct_opponents"] >= 3
        and mechanism_gate["opponent_wood_gap_vs_noncatastrophic"] >= 20
    )
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only effect-level census of the current resident's most recent finished "
            "arena battles; no game creation or submission"
        ),
        "arena_snapshot": arena_snapshot,
        "games": len(rows),
        "cohorts": {
            "all": summarize(rows),
            "wins": summarize(wins),
            "ties": summarize(ties),
            "ordinary_losses": summarize(ordinary_losses),
            "catastrophic_losses": summarize(catastrophic),
        },
        "catastrophic_tail": mechanism_gate,
        "early_observable_risk": early_risk_rules(rows),
        "opening_feature_contrasts": opening_contrasts(rows),
        "same_opponent_volatility": opponent_volatility(rows),
        "rows": rows,
        "decision": {
            "construct_candidate": False,
            "submit": False,
            "next_diagnostic": (
                "attribute opponent-planted tree creation, harvest, and interception before "
                "designing a baseline-preserving anti-compounding objective"
            ),
        },
    }


def fetch(max_games: int) -> tuple[list[dict], dict]:
    # Reuse the authenticated read-only service helper.  Importing here keeps
    # pure analysis/tests independent of local credentials.
    from cgauto import battle_taxonomy as arena

    battles = arena.call(
        "gamesPlayersRanking/findLastBattlesByTestSessionHandle", [arena.TSH, None]
    )
    done = [battle for battle in battles if battle.get("done")][:max_games]
    leaderboard = arena.call(
        "Leaderboards/getFilteredPuzzleLeaderboard",
        [arena.PID, arena.TSH, "global", {"active": False, "column": "", "filter": ""}],
    )
    rank_of = {
        user.get("pseudo"): (user.get("localRank"), user.get("score"))
        for user in leaderboard.get("users", [])
    }
    resident = next(
        (
            user
            for user in leaderboard.get("users", [])
            if (user.get("codingamer") or {}).get("userId") == USER_ID
        ),
        {},
    )
    rows = []
    failures = []
    for index, battle in enumerate(done, 1):
        game_id = battle["gameId"]
        try:
            game = arena.call("gameResult/findByGameId", [game_id, None])
            row = game_row(game, rank_of)
            if row is not None:
                rows.append(row)
        except Exception as error:  # noqa: BLE001 - retain a complete read audit
            failures.append({"game_id": game_id, "error": f"{type(error).__name__}: {error}"})
        if index % 10 == 0 or index == len(done):
            print(f"fetched {index}/{len(done)} finished battles", flush=True)
    snapshot = {
        "battle_rows_listed": len(battles),
        "finished_requested": len(done),
        "parsed": len(rows),
        "fetch_failures": failures,
        "resident_agent_id": resident.get("agentId"),
        "resident_rank": resident.get("localRank"),
        "resident_score": resident.get("score"),
        "resident_league": (resident.get("league") or {}).get("divisionIndex"),
    }
    return rows, snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-games", type=int, default=80)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.max_games < 1:
        parser.error("--max-games must be positive")
    rows, snapshot = fetch(args.max_games)
    if not rows:
        raise SystemExit("no recent battles could be parsed")
    payload = analyze(rows, snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    tail = payload["catastrophic_tail"]
    print(
        f"rank={snapshot.get('resident_rank')} score={snapshot.get('resident_score')} "
        f"games={len(rows)} catastrophes={tail['frequency']:.1%} "
        f"negative-mass={tail['negative_margin_mass_share']:.1%}"
    )
    rules = payload["early_observable_risk"]["top_rules"]
    if rules:
        top = rules[0]
        labels = " AND ".join(condition["label"] for condition in top["conditions"])
        print(
            f"top early rule: {labels} -> {top['catastrophic']}/{top['selected']} "
            f"catastrophic ({top['precision']:.1%}), recall {top['recall']:.1%}"
        )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
