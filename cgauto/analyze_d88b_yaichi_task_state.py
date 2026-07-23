#!/usr/bin/env python3
"""Reconstruct yaichi's task grammar and renewable crop lineage from open replays.

D88b is observational.  The repaired message aliases are frozen from D88a discovery, while the
splits, accounting rules, and
mechanism gates are frozen in the accompanying protocol before validation message streams are
opened.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    assigned_unit_commands,
    cargo_delta,
    player_commands,
)

AGENT_ID = 6480541
RAW_GAMES = REPO / "data/raw/games"
HISTORICAL_TRAJECTORIES = REPO / "data/processed/trajectories"
CURRENT_TRAJECTORIES = (
    REPO
    / "data/raw/snapshots/20260721T105508Z-d61p/processed/open/trajectories"
)
D86_RESULT = (
    REPO
    / "data/analysis/live-agent-6553250/d86a-two-worker-renewable-role-result.json"
)

DISCOVERY_HISTORICAL_IDS = (
    893174122,
    893407296,
    893412043,
    893876322,
    894397581,
    895446276,
    895925001,
    895926495,
    895927312,
)
CURRENT_IDS = (
    896491202,
    896492419,
    896493461,
    896493721,
    896494122,
    896494214,
    896494703,
    896495136,
    896495350,
    896495475,
)
VALIDATION_IDS = (
    895446639,
    895447009,
    895447026,
    895447237,
    895883032,
    895883103,
    895883400,
    895883571,
    895924585,
    895926546,
    895926772,
    895927134,
    895927164,
    895927169,
    895927226,
    895927242,
)

FRUIT_NAMES = ("PLUM", "LEMON", "APPLE", "BANANA")
FRUIT_INDICES = range(4)
KNOWN_STATES = (
    "MINE",
    "HARVEST",
    "DROP",
    "DO_CHOP",
    "PLANT",
    "PICK_SHACK",
    "GO_PLANT",
    "RETURN",
    "CHOP_TRAVEL",
    "HARVEST_TRAVEL",
    "MINE_TRAVEL",
    "GET_SEED_TREE",
    "ATTACK",
)
ALLOWED_COMMANDS = {
    "MINE": {"MINE"},
    "HARVEST": {"HARVEST"},
    "DROP": {"DROP"},
    "DO_CHOP": {"CHOP"},
    "PLANT": {"PICK", "HARVEST", "PLANT"},
    "PICK_SHACK": {"MOVE", "PICK", "WAIT"},
    "GO_PLANT": {"MOVE", "PLANT", "WAIT"},
    "RETURN": {"MOVE", "DROP", "WAIT"},
    "CHOP_TRAVEL": {"MOVE", "CHOP", "WAIT"},
    "HARVEST_TRAVEL": {"MOVE", "HARVEST", "WAIT"},
    "MINE_TRAVEL": {"MOVE", "MINE", "WAIT"},
    "GET_SEED_TREE": {"MOVE", "WAIT"},
    "ATTACK": {"MOVE", "WAIT"},
}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def canonical_rows(rows: list[dict]) -> bytes:
    return (
        "\n".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows
        )
        + "\n"
    ).encode()


def read_trajectory(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[5]


def agent_seat(raw: dict) -> tuple[int, dict, dict]:
    own = next(
        (row for row in raw.get("agents", []) if row.get("agentId") == AGENT_ID),
        None,
    )
    if own is None:
        raise ValueError(f"agent {AGENT_ID} absent from game {raw.get('gameId')}")
    opponent = next(row for row in raw["agents"] if row.get("index") != own["index"])
    return int(own["index"]), own, opponent


def extract_msg_payload(line: str | None) -> tuple[str | None, int]:
    payloads = []
    for command in re.split(r"[;\n]", line or ""):
        stripped = command.strip()
        if stripped.upper().startswith("MSG "):
            payloads.append(stripped[4:])
        elif stripped.upper() == "MSG":
            payloads.append("")
    if not payloads:
        return None, 0
    return " | ".join(payloads), len(payloads)


def parse_msg_payload(payload: str | None) -> dict:
    if payload is None:
        return {"segments": {}, "malformed": [], "duplicates": []}
    segments: dict[int, str] = {}
    malformed = []
    duplicates = []
    for piece in payload.split(" | "):
        match = re.fullmatch(r"\s*(\d+)\s*:(.*)", piece)
        if not match:
            malformed.append(piece)
            continue
        unit_id = int(match.group(1))
        state = match.group(2).strip()
        if unit_id in segments:
            duplicates.append(unit_id)
        else:
            segments[unit_id] = state
    return {"segments": segments, "malformed": malformed, "duplicates": duplicates}


def normalize_state(text: str) -> str:
    value = text.strip()
    for exact in ("MINE", "HARVEST", "DROP", "DO_CHOP", "PLANT"):
        if re.match(rf"^{exact}(?:\b|$)", value):
            return exact
    if value.startswith("PICK_SHACK"):
        return "PICK_SHACK"
    if value.startswith("GO_PLANT"):
        return "GO_PLANT"
    if value.startswith("RETURN"):
        return "RETURN"
    if value.startswith("CHOP"):
        return "CHOP_TRAVEL"
    if value.startswith("H("):
        return "HARVEST_TRAVEL"
    if value.startswith("M("):
        return "MINE_TRAVEL"
    if value.startswith("GET_SEED_TREE"):
        return "GET_SEED_TREE"
    if value.startswith("ATTACK"):
        return "ATTACK"
    return "UNKNOWN"


def successful_chop(
    unit: dict, before_plants: dict[tuple[int, int], dict], after_plants: dict
) -> bool:
    cell = (unit["x"], unit["y"])
    before = before_plants.get(cell)
    if before is None:
        return False
    after = after_plants.get(cell)
    return after is None or after["health"] < before["health"]


def new_token(
    serial: int,
    source: str,
    turn: int,
    unit_id: int,
    species: int,
) -> dict:
    return {
        "id": serial,
        "source": source,
        "acquisition_turn": turn,
        "unit_id": unit_id,
        "species": species,
        "disposition": "carried",
        "disposition_turn": None,
    }


def consume_tokens(
    pool: deque[dict], amount: int, disposition: str, turn: int
) -> tuple[list[dict], int]:
    consumed = []
    underflow = 0
    for _ in range(amount):
        if not pool:
            underflow += 1
            continue
        token = pool.popleft()
        token["disposition"] = disposition
        token["disposition_turn"] = turn
        consumed.append(token)
    return consumed, underflow


def plant_output(record: dict) -> dict:
    return {
        key: record.get(key)
        for key in (
            "lineage_id",
            "cell",
            "species",
            "owner",
            "origin",
            "planted_turn",
            "planter_id",
            "source",
            "harvests_by_yaichi",
            "harvested_fruit_by_yaichi",
            "chops_by_yaichi",
            "chops_by_opponent",
            "first_harvest_turn",
            "first_chop_turn",
            "removed_turn",
            "terminal_live",
        )
    }


def load_d86_labels() -> dict[int, bool]:
    payload = json.loads(D86_RESULT.read_text())
    return {int(row["game_id"]): bool(row["renewable_mode"]) for row in payload["rows"]}


def trajectory_path(game_id: int, corpus: str) -> Path:
    root = CURRENT_TRAJECTORIES if corpus == "current" else HISTORICAL_TRAJECTORIES
    return root / f"{game_id}.jsonl"


def task_rows(phase: str) -> list[tuple[int, str, str]]:
    rows = []
    if phase in {"discovery", "all"}:
        rows.extend((game_id, "discovery_historical", "historical") for game_id in DISCOVERY_HISTORICAL_IDS)
        rows.extend((game_id, "current_consumed", "current") for game_id in CURRENT_IDS)
    if phase in {"validation", "all"}:
        rows.extend((game_id, "validation", "historical") for game_id in VALIDATION_IDS)
    return rows


def analyze_game(task: tuple[int, str, str]) -> dict:
    game_id, split, corpus = task
    raw_path = RAW_GAMES / f"{game_id}.json"
    raw = json.loads(raw_path.read_text())
    trajectory = read_trajectory(trajectory_path(game_id, corpus))
    commands_by_turn = [
        [player_commands(row, player) for player in (0, 1)] for row in trajectory
    ]
    chop_ids = [
        effective_chop_unit_ids(commands[0]) + effective_chop_unit_ids(commands[1])
        for commands in commands_by_turn
    ]
    decoded = decode_replay(raw_path, chop_unit_ids_by_turn=chop_ids)
    states = decoded["states"]
    player, own_agent, opponent_agent = agent_seat(raw)
    labels = load_d86_labels()

    initial_units = sorted(states[0]["units"], key=lambda row: row["id"])
    cargo: dict[int, list[deque[dict]]] = {}
    all_tokens: list[dict] = []
    token_serial = 0
    for unit in initial_units:
        cargo[unit["id"]] = [deque() for _ in FRUIT_INDICES]
        for species in FRUIT_INDICES:
            for _ in range(unit["carry"][species]):
                token_serial += 1
                token = new_token(token_serial, "initial", 0, unit["id"], species)
                cargo[unit["id"]][species].append(token)
                all_tokens.append(token)

    yaichi_initial = [unit for unit in initial_units if unit["player"] == player]
    if not yaichi_initial:
        raise ValueError(f"game {game_id} has no initial yaichi unit")
    ordinal_by_id: dict[int, int] = {
        unit["id"]: ordinal for ordinal, unit in enumerate(yaichi_initial)
    }
    next_ordinal = len(ordinal_by_id)

    plant_serial = 0
    lineages: dict[tuple[int, int], dict] = {}
    plant_records: list[dict] = []
    for plant in states[0]["plants"]:
        plant_serial += 1
        cell = (plant["x"], plant["y"])
        record = {
            "lineage_id": plant_serial,
            "cell": list(cell),
            "species": plant["type"],
            "owner": None,
            "origin": "natural",
            "planted_turn": 0,
            "planter_id": None,
            "source": "natural",
            "harvests_by_yaichi": 0,
            "harvested_fruit_by_yaichi": 0,
            "chops_by_yaichi": 0,
            "chops_by_opponent": 0,
            "first_harvest_turn": None,
            "first_chop_turn": None,
            "removed_turn": None,
            "terminal_live": False,
        }
        lineages[cell] = record
        plant_records.append(record)

    state_counts: dict[int, Counter] = defaultdict(Counter)
    raw_unknown_states = Counter()
    transitions: dict[int, Counter] = defaultdict(Counter)
    previous_state: dict[int, str] = {}
    successful_actions: dict[int, Counter] = defaultdict(Counter)
    planted_sources: dict[int, Counter] = defaultdict(Counter)
    task_coordinates: dict[str, Counter] = defaultdict(Counter)
    msg_turns = 0
    msg_command_count = 0
    alive_unit_turns = 0
    parsed_unit_turns = 0
    known_unit_turns = 0
    conforming_unit_turns = 0
    state_command_pairs = Counter()
    state_command_mismatches = Counter()
    unknown_state_command_pairs = Counter()
    malformed_segments = 0
    duplicate_segments = 0
    foreign_segments = 0
    exact_plant_lineage_failures = 0
    exact_harvest_lineage_failures = 0
    provenance_underflows = 0
    phase_turns = {
        "bank_acquisition": None,
        "bank_sourced_plant": None,
        "own_crop_harvest": None,
        "own_crop_sourced_plant": None,
    }

    usable_turns = min(len(states) - 1, len(trajectory))
    for turn in range(1, usable_turns + 1):
        before = states[turn - 1]
        after = states[turn]
        before_units_all = {unit["id"]: unit for unit in before["units"]}
        after_units_all = {unit["id"]: unit for unit in after["units"]}
        before_plants = {(plant["x"], plant["y"]): plant for plant in before["plants"]}
        after_plants = {(plant["x"], plant["y"]): plant for plant in after["plants"]}
        assigned_by_player = {}
        for seat in (0, 1):
            units = [unit for unit in before["units"] if unit["player"] == seat]
            assigned_by_player[seat] = assigned_unit_commands(
                commands_by_turn[turn - 1][seat], units
            )

        own_before = {
            unit_id: unit
            for unit_id, unit in before_units_all.items()
            if unit["player"] == player
        }
        payload, payload_count = extract_msg_payload(
            trajectory[turn - 1].get(f"commands{player}")
        )
        parsed = parse_msg_payload(payload)
        msg_command_count += payload_count
        if payload is not None:
            msg_turns += 1
        malformed_segments += len(parsed["malformed"])
        duplicate_segments += len(parsed["duplicates"])
        alive_unit_turns += len(own_before)
        for unit_id, raw_state in parsed["segments"].items():
            if unit_id not in own_before:
                foreign_segments += 1
                continue
            parsed_unit_turns += 1
            normalized = normalize_state(raw_state)
            ordinal = ordinal_by_id.get(unit_id, -1)
            state_counts[ordinal][normalized] += 1
            command = assigned_by_player[player].get(unit_id, "WAIT")
            verb = command.split()[0].upper() if command.split() else "WAIT"
            if normalized == "UNKNOWN":
                raw_unknown_states[raw_state] += 1
                raw_prefix = raw_state.split("->", 1)[0].split("(", 1)[0]
                unknown_state_command_pairs[f"{raw_prefix}:{verb}"] += 1
            else:
                known_unit_turns += 1
                state_command_pairs[f"{normalized}:{verb}"] += 1
                if verb in ALLOWED_COMMANDS[normalized]:
                    conforming_unit_turns += 1
                else:
                    state_command_mismatches[f"{normalized}:{verb}"] += 1
            if unit_id in previous_state:
                transitions[ordinal][f"{previous_state[unit_id]}->{normalized}"] += 1
            previous_state[unit_id] = normalized
            for x, y in re.findall(r"\((-?\d+),\s*(-?\d+)\)", raw_state):
                task_coordinates[normalized][f"{x},{y}"] += 1

        successful_plants_this_turn: list[tuple[int, int, tuple[int, int], int, dict]] = []
        successful_chops_this_turn: set[tuple[int, int]] = set()
        for seat in (0, 1):
            for unit_id, unit in sorted(before_units_all.items()):
                if unit["player"] != seat:
                    continue
                command = assigned_by_player[seat].get(unit_id)
                if command is None:
                    continue
                fields = command.split()
                if not fields:
                    continue
                verb = fields[0].upper()
                after_unit = after_units_all.get(unit_id)
                gained, spent = cargo_delta(unit, after_unit)
                cell = (unit["x"], unit["y"])
                chop_ok = verb == "CHOP" and successful_chop(
                    unit, before_plants, after_plants
                )
                harvest_ok = verb == "HARVEST" and any(gained[i] for i in FRUIT_INDICES)
                plant_ok = verb == "PLANT" and any(spent[i] for i in FRUIT_INDICES)
                drop_ok = verb == "DROP" and any(spent)
                pick_ok = verb == "PICK" and any(gained[i] for i in FRUIT_INDICES)
                mine_ok = verb == "MINE" and gained[4] > 0
                success = {
                    "CHOP": chop_ok,
                    "HARVEST": harvest_ok,
                    "PLANT": plant_ok,
                    "DROP": drop_ok,
                    "PICK": pick_ok,
                    "MINE": mine_ok,
                }.get(verb, False)
                if seat == player and success:
                    successful_actions[ordinal_by_id[unit_id]][verb] += 1

                consumed_by_species: dict[int, list[dict]] = defaultdict(list)
                for species in FRUIT_INDICES:
                    disposition = "planted" if verb == "PLANT" else "dropped" if verb == "DROP" else "spent_other"
                    consumed, underflow = consume_tokens(
                        cargo[unit_id][species], spent[species], disposition, turn
                    )
                    consumed_by_species[species].extend(consumed)
                    provenance_underflows += underflow

                if harvest_ok:
                    lineage = lineages.get(cell)
                    before_plant = before_plants.get(cell)
                    if lineage is None or before_plant is None:
                        if seat == player:
                            exact_harvest_lineage_failures += 1
                        source = "unknown"
                    elif lineage["owner"] is None:
                        source = "natural"
                    elif lineage["owner"] == seat:
                        source = "own_crop"
                    else:
                        source = "opponent_crop"
                    if seat == player and source == "own_crop":
                        lineage["harvests_by_yaichi"] += 1
                        lineage["harvested_fruit_by_yaichi"] += sum(
                            gained[i] for i in FRUIT_INDICES
                        )
                        if lineage["first_harvest_turn"] is None:
                            lineage["first_harvest_turn"] = turn
                        if phase_turns["own_crop_harvest"] is None and ordinal_by_id[unit_id] == 0:
                            phase_turns["own_crop_harvest"] = turn
                    if seat == player and before_plant is not None:
                        species_name = before_plant["type"]
                        gained_species = [
                            FRUIT_NAMES[i] for i in FRUIT_INDICES for _ in range(gained[i])
                        ]
                        if any(name != species_name for name in gained_species):
                            exact_harvest_lineage_failures += 1
                else:
                    source = "bank" if pick_ok else "other"

                for species in FRUIT_INDICES:
                    if not gained[species]:
                        continue
                    token_source = source if harvest_ok else "bank" if pick_ok else "other"
                    for _ in range(gained[species]):
                        token_serial += 1
                        token = new_token(token_serial, token_source, turn, unit_id, species)
                        cargo[unit_id][species].append(token)
                        all_tokens.append(token)

                if seat == player and pick_ok and ordinal_by_id[unit_id] == 0:
                    if phase_turns["bank_acquisition"] is None:
                        phase_turns["bank_acquisition"] = turn

                if plant_ok:
                    planted_species = [i for i in FRUIT_INDICES if spent[i] > 0]
                    after_plant = after_plants.get(cell)
                    if (
                        len(planted_species) != 1
                        or spent[planted_species[0]] != 1
                        or after_plant is None
                        or after_plant["type"] != FRUIT_NAMES[planted_species[0]]
                    ):
                        if seat == player:
                            exact_plant_lineage_failures += 1
                    else:
                        species = planted_species[0]
                        tokens = consumed_by_species[species]
                        source_token = tokens[0] if len(tokens) == 1 else None
                        if source_token is None and seat == player:
                            exact_plant_lineage_failures += 1
                        source_name = source_token["source"] if source_token else "unknown"
                        successful_plants_this_turn.append(
                            (seat, unit_id, cell, species, source_token or {"source": "unknown"})
                        )
                        if seat == player:
                            ordinal = ordinal_by_id[unit_id]
                            planted_sources[ordinal][source_name] += 1
                            if ordinal == 0 and source_name == "bank" and phase_turns["bank_sourced_plant"] is None:
                                phase_turns["bank_sourced_plant"] = turn
                            if ordinal == 0 and source_name == "own_crop" and phase_turns["own_crop_sourced_plant"] is None:
                                phase_turns["own_crop_sourced_plant"] = turn

                if chop_ok:
                    lineage = lineages.get(cell)
                    if lineage is not None:
                        if seat == player:
                            lineage["chops_by_yaichi"] += 1
                        else:
                            lineage["chops_by_opponent"] += 1
                        if lineage["first_chop_turn"] is None:
                            lineage["first_chop_turn"] = turn
                    successful_chops_this_turn.add(cell)

        for unit_id, unit in sorted(after_units_all.items()):
            if unit_id in before_units_all:
                continue
            cargo[unit_id] = [deque() for _ in FRUIT_INDICES]
            for species in FRUIT_INDICES:
                for _ in range(unit["carry"][species]):
                    token_serial += 1
                    token = new_token(token_serial, "initial", turn, unit_id, species)
                    cargo[unit_id][species].append(token)
                    all_tokens.append(token)
            if unit["player"] == player:
                ordinal_by_id[unit_id] = next_ordinal
                next_ordinal += 1

        for unit_id in set(before_units_all) - set(after_units_all):
            for pool in cargo.get(unit_id, []):
                while pool:
                    token = pool.popleft()
                    token["disposition"] = "lost"
                    token["disposition_turn"] = turn

        planted_cells = set()
        for seat, unit_id, cell, species, source_token in successful_plants_this_turn:
            plant_serial += 1
            record = {
                "lineage_id": plant_serial,
                "cell": list(cell),
                "species": FRUIT_NAMES[species],
                "owner": seat,
                "origin": "yaichi_crop" if seat == player else "opponent_crop",
                "planted_turn": turn,
                "planter_id": unit_id,
                "source": source_token["source"],
                "harvests_by_yaichi": 0,
                "harvested_fruit_by_yaichi": 0,
                "chops_by_yaichi": 0,
                "chops_by_opponent": 0,
                "first_harvest_turn": None,
                "first_chop_turn": None,
                "removed_turn": None,
                "terminal_live": False,
            }
            previous = lineages.get(cell)
            if previous is not None and previous["removed_turn"] is None:
                previous["removed_turn"] = turn
            lineages[cell] = record
            plant_records.append(record)
            planted_cells.add(cell)

        for cell, record in list(lineages.items()):
            if cell not in after_plants:
                if record["removed_turn"] is None:
                    record["removed_turn"] = turn
                del lineages[cell]
            elif cell not in before_plants and cell not in planted_cells:
                # A replay-created plant without a successful decoded PLANT is retained but makes
                # exact lineage fail for yaichi only if it later enters yaichi accounting.
                record["origin"] = record.get("origin", "unknown")

    terminal = states[usable_turns]
    terminal_unit_ids = {unit["id"] for unit in terminal["units"]}
    for unit_id, pools in cargo.items():
        if unit_id not in terminal_unit_ids:
            continue
        for pool in pools:
            for token in pool:
                token["disposition"] = "terminal"
                token["disposition_turn"] = usable_turns
    for record in lineages.values():
        record["terminal_live"] = True

    own_crop_tokens = [
        token
        for token in all_tokens
        if token["unit_id"] in ordinal_by_id and token["source"] == "own_crop"
    ]
    own_crop_dispositions = Counter(token["disposition"] for token in own_crop_tokens)
    official_scores = [int(round(value)) for value in raw.get("scores", [])]
    terminal_scores = [score(list(inventory)) for inventory in terminal["inventories"]]
    ordered_phase_values = [
        phase_turns[name]
        for name in (
            "bank_acquisition",
            "bank_sourced_plant",
            "own_crop_harvest",
            "own_crop_sourced_plant",
        )
    ]
    complete_ordered_phases = all(value is not None for value in ordered_phase_values) and all(
        left < right for left, right in zip(ordered_phase_values, ordered_phase_values[1:])
    )
    starter_sources = planted_sources.get(0, Counter())
    first_bank = phase_turns["bank_sourced_plant"]
    first_own = phase_turns["own_crop_sourced_plant"]
    bank_before_maintenance = first_bank is not None and first_own is not None and first_bank < first_own

    crop_outcomes = Counter()
    crop_ages_at_first_harvest = []
    crop_ages_at_first_chop = []
    for record in plant_records:
        if record["owner"] != player:
            continue
        if record["harvests_by_yaichi"]:
            crop_outcomes["harvested_by_yaichi"] += 1
            crop_ages_at_first_harvest.append(record["first_harvest_turn"] - record["planted_turn"])
        if record["chops_by_yaichi"]:
            crop_outcomes["chopped_by_yaichi"] += 1
            crop_ages_at_first_chop.append(record["first_chop_turn"] - record["planted_turn"])
        if record["chops_by_opponent"]:
            crop_outcomes["chopped_by_opponent"] += 1
        if record["terminal_live"]:
            crop_outcomes["terminal_live"] += 1
        if record["harvests_by_yaichi"] and record["chops_by_yaichi"]:
            crop_outcomes["harvested_before_own_chop"] += int(
                record["first_harvest_turn"] <= record["first_chop_turn"]
            )

    return {
        "game_id": game_id,
        "split": split,
        "seat": player,
        "opponent_agent_id": opponent_agent.get("agentId"),
        "opponent": opponent_agent.get("codingamer", {}).get("pseudo"),
        "turns": usable_turns,
        "renewable_mode": labels[game_id],
        "score": official_scores[player],
        "opponent_score": official_scores[1 - player],
        "margin": official_scores[player] - official_scores[1 - player],
        "worker_count": len(ordinal_by_id),
        "phase_turns": phase_turns,
        "bank_bootstrap_before_maintenance": bank_before_maintenance,
        "complete_ordered_phases": complete_ordered_phases,
        "starter_plant_sources": dict(sorted(starter_sources.items())),
        "own_crop_token_dispositions": dict(sorted(own_crop_dispositions.items())),
        "successful_actions_by_ordinal": {
            str(key): dict(sorted(value.items())) for key, value in sorted(successful_actions.items())
        },
        "state_counts_by_ordinal": {
            str(key): dict(sorted(value.items())) for key, value in sorted(state_counts.items())
        },
        "state_transitions_by_ordinal": {
            str(key): dict(sorted(value.items())) for key, value in sorted(transitions.items())
        },
        "raw_unknown_states": dict(sorted(raw_unknown_states.items())),
        "state_command_pairs": dict(sorted(state_command_pairs.items())),
        "state_command_mismatches": dict(sorted(state_command_mismatches.items())),
        "unknown_state_command_pairs": dict(sorted(unknown_state_command_pairs.items())),
        "task_coordinate_top10": {
            state: [[cell, count] for cell, count in counter.most_common(10)]
            for state, counter in sorted(task_coordinates.items())
        },
        "crop_outcomes": dict(sorted(crop_outcomes.items())),
        "crop_ages_at_first_harvest": crop_ages_at_first_harvest,
        "crop_ages_at_first_chop": crop_ages_at_first_chop,
        "plants": [plant_output(record) for record in plant_records],
        "telemetry": {
            "msg_turns": msg_turns,
            "msg_command_count": msg_command_count,
            "alive_unit_turns": alive_unit_turns,
            "parsed_unit_turns": parsed_unit_turns,
            "known_unit_turns": known_unit_turns,
            "conforming_unit_turns": conforming_unit_turns,
            "malformed_segments": malformed_segments,
            "duplicate_segments": duplicate_segments,
            "foreign_segments": foreign_segments,
        },
        "integrity": {
            "trajectory_matches_decoded_turns": len(trajectory) == len(states) - 1,
            "unknown_diff_updates": len(decoded["unknown_updates"]),
            "terminal_scores_exact": terminal_scores == official_scores,
            "provenance_underflows": provenance_underflows,
            "exact_plant_lineage_failures": exact_plant_lineage_failures,
            "exact_harvest_lineage_failures": exact_harvest_lineage_failures,
            "raw_agent_valid": own_agent.get("valid"),
        },
    }


def sum_counter_dict(rows: list[dict], key: str) -> Counter:
    total = Counter()
    for row in rows:
        total.update(row.get(key, {}))
    return total


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def aggregate_integrity(rows: list[dict]) -> dict:
    telemetry = Counter()
    for row in rows:
        telemetry.update(row["telemetry"])
    msg_rate = ratio(telemetry["msg_turns"], sum(row["turns"] for row in rows))
    parsed_rate = ratio(telemetry["parsed_unit_turns"], telemetry["alive_unit_turns"])
    known_rate = ratio(telemetry["known_unit_turns"], telemetry["parsed_unit_turns"])
    conformance_rate = ratio(
        telemetry["conforming_unit_turns"], telemetry["known_unit_turns"]
    )
    gates = {
        "decoded_and_terminal_exact": all(
            row["integrity"]["trajectory_matches_decoded_turns"]
            and row["integrity"]["unknown_diff_updates"] == 0
            and row["integrity"]["terminal_scores_exact"]
            for row in rows
        ),
        "zero_provenance_underflow": all(
            row["integrity"]["provenance_underflows"] == 0 for row in rows
        ),
        "msg_turn_rate_at_least_0.98": msg_rate is not None and msg_rate >= 0.98,
        "parsed_unit_turn_rate_at_least_0.98": parsed_rate is not None and parsed_rate >= 0.98,
        "known_state_rate_at_least_0.98": known_rate is not None and known_rate >= 0.98,
        "state_command_conformance_at_least_0.95": conformance_rate is not None and conformance_rate >= 0.95,
        "zero_malformed_duplicate_foreign_segments": (
            telemetry["malformed_segments"] == 0
            and telemetry["duplicate_segments"] == 0
            and telemetry["foreign_segments"] == 0
        ),
        "exact_plant_and_harvest_lineage": all(
            row["integrity"]["exact_plant_lineage_failures"] == 0
            and row["integrity"]["exact_harvest_lineage_failures"] == 0
            for row in rows
        ),
    }
    return {
        "games": len(rows),
        "telemetry": dict(sorted(telemetry.items())),
        "msg_turn_rate": msg_rate,
        "parsed_unit_turn_rate": parsed_rate,
        "known_state_rate": known_rate,
        "state_command_conformance_rate": conformance_rate,
        "gates": gates,
        "pass": all(gates.values()),
    }


def mechanism_summary(rows: list[dict]) -> dict:
    renewable = [row for row in rows if row["renewable_mode"]]
    starter_sources = Counter()
    dispositions = Counter()
    trained_actions = Counter()
    for row in renewable:
        starter_sources.update(row["starter_plant_sources"])
        dispositions.update(row["own_crop_token_dispositions"])
        trained_actions.update(row["successful_actions_by_ordinal"].get("1", {}))
    planted_total = sum(starter_sources.values())
    supported_plants = starter_sources["bank"] + starter_sources["own_crop"]
    own_crop_tokens = sum(dispositions.values())
    replanted_tokens = dispositions["planted"]
    productive_total = sum(trained_actions.values())
    trained_role_actions = trained_actions["CHOP"] + trained_actions["DROP"]
    trained_farm_games = sum(
        row["successful_actions_by_ordinal"].get("1", {}).get("HARVEST", 0) > 0
        or row["successful_actions_by_ordinal"].get("1", {}).get("PLANT", 0) > 0
        for row in renewable
    )
    bank_before = sum(row["bank_bootstrap_before_maintenance"] for row in renewable)
    ordered = sum(row["complete_ordered_phases"] for row in renewable)
    return {
        "renewable_games": len(renewable),
        "bank_bootstrap_before_maintenance_games": bank_before,
        "bank_bootstrap_before_maintenance_rate": ratio(bank_before, len(renewable)),
        "starter_plant_sources": dict(sorted(starter_sources.items())),
        "supported_starter_plant_rate": ratio(supported_plants, planted_total),
        "own_crop_token_dispositions": dict(sorted(dispositions.items())),
        "own_crop_same_worker_replant_rate": ratio(replanted_tokens, own_crop_tokens),
        "trained_successful_actions": dict(sorted(trained_actions.items())),
        "trained_chop_drop_rate": ratio(trained_role_actions, productive_total),
        "trained_farm_games": trained_farm_games,
        "complete_ordered_phase_games": ordered,
        "complete_ordered_phase_rate": ratio(ordered, len(renewable)),
    }


def descriptive_summary(rows: list[dict]) -> dict:
    state_counts = Counter()
    transitions = Counter()
    crop_outcomes = Counter()
    harvest_ages = []
    chop_ages = []
    for row in rows:
        for ordinal, counts in row["state_counts_by_ordinal"].items():
            state_counts.update({f"{ordinal}:{state}": count for state, count in counts.items()})
        for ordinal, counts in row["state_transitions_by_ordinal"].items():
            transitions.update({f"{ordinal}:{transition}": count for transition, count in counts.items()})
        crop_outcomes.update(row["crop_outcomes"])
        harvest_ages.extend(row["crop_ages_at_first_harvest"])
        chop_ages.extend(row["crop_ages_at_first_chop"])
    return {
        "state_counts": dict(sorted(state_counts.items())),
        "top_state_transitions": [[key, count] for key, count in transitions.most_common(40)],
        "crop_outcomes": dict(sorted(crop_outcomes.items())),
        "crop_age_at_first_harvest": sorted(harvest_ages),
        "crop_age_at_first_chop": sorted(chop_ages),
    }


def current_qualitative(summary: dict) -> bool:
    values = (
        summary["bank_bootstrap_before_maintenance_rate"],
        summary["supported_starter_plant_rate"],
        summary["own_crop_same_worker_replant_rate"],
        summary["trained_chop_drop_rate"],
        summary["complete_ordered_phase_rate"],
    )
    return all(value is not None and value > 0.5 for value in values)


def analyze(rows: list[dict], phase: str) -> dict:
    groups = {
        split: [row for row in rows if row["split"] == split]
        for split in ("discovery_historical", "current_consumed", "validation")
        if any(row["split"] == split for row in rows)
    }
    integrity = {split: aggregate_integrity(selected) for split, selected in groups.items()}
    mechanism = {split: mechanism_summary(selected) for split, selected in groups.items()}
    descriptive = {split: descriptive_summary(selected) for split, selected in groups.items()}
    result: dict[str, Any] = {
        "schema": "d88b-yaichi-task-state-v1",
        "phase": phase,
        "agent_id": AGENT_ID,
        "counts": {split: len(selected) for split, selected in groups.items()},
        "integrity": integrity,
        "mechanism": mechanism,
        "descriptive": descriptive,
        "rows_hash": sha256_bytes(canonical_rows(rows)),
        "rows": rows,
    }
    if "validation" not in groups:
        result["decision"] = (
            "discovery_integrity_pass_validation_unopened"
            if all(value["pass"] for value in integrity.values())
            else "repair_discovery_integrity_validation_unopened"
        )
        return result

    validation = mechanism["validation"]
    current = mechanism.get("current_consumed")
    mechanism_gates = {
        "bank_before_maintenance_at_least_10_of_12": (
            validation["renewable_games"] == 12
            and validation["bank_bootstrap_before_maintenance_games"] >= 10
        ),
        "supported_starter_plants_at_least_0.80": (
            validation["supported_starter_plant_rate"] is not None
            and validation["supported_starter_plant_rate"] >= 0.80
        ),
        "own_crop_same_worker_replant_at_least_0.80": (
            validation["own_crop_same_worker_replant_rate"] is not None
            and validation["own_crop_same_worker_replant_rate"] >= 0.80
        ),
        "trained_chop_drop_at_least_0.95": (
            validation["trained_chop_drop_rate"] is not None
            and validation["trained_chop_drop_rate"] >= 0.95
        ),
        "trained_farm_in_at_most_one_game": validation["trained_farm_games"] <= 1,
        "complete_ordered_phases_at_least_10_of_12": (
            validation["renewable_games"] == 12
            and validation["complete_ordered_phase_games"] >= 10
        ),
        "current_same_qualitative_direction": current is not None and current_qualitative(current),
    }
    result["mechanism_gates"] = mechanism_gates
    all_integrity = all(value["pass"] for value in integrity.values())
    if not all_integrity:
        decision = "repair_integrity_no_behavioral_interpretation"
    elif all(mechanism_gates.values()):
        decision = "pass_write_blueprint_open_d89"
    else:
        decision = "reject_literal_task_imitation"
    result["decision"] = decision
    return result


def analyze_all(phase: str, jobs: int) -> list[dict]:
    tasks = task_rows(phase)
    if jobs == 1:
        rows = [analyze_game(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            rows = list(executor.map(analyze_game, tasks))
    return sorted(rows, key=lambda row: (row["split"], row["game_id"]))


def write_atomic(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("discovery", "validation", "all"), required=True)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--rows-output", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = analyze_all(args.phase, args.jobs)
    if args.rows_output:
        args.rows_output.write_bytes(canonical_rows(rows))
    result = analyze(rows, args.phase)
    write_atomic(args.output, result)
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "counts": result["counts"],
                "integrity": result["integrity"],
                "mechanism": result["mechanism"],
                "mechanism_gates": result.get("mechanism_gates"),
                "rows_hash": result["rows_hash"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
