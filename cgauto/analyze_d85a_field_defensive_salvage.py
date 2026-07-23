#!/usr/bin/env python3
"""Extract and audit exact one-turn resident defensive salvage counterfactuals."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import tempfile

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import (  # noqa: E402
    load_open_inputs,
    read_jsonl,
    sha256_file,
)
from cgauto.analyze_d78a_opponent_commitment import (  # noqa: E402
    EXPECTED_RESIDENT,
    EXPECTED_SNAPSHOT,
    opponent_partition,
    plant_at,
    unit_free,
)
from cgauto.analyze_d78b_opponent_commitment import confirmed_chop_cells  # noqa: E402
from cgauto.recent_resident_field_census import (  # noqa: E402
    crop_provenance,
    decoded_states,
)
from cgauto.replay_conformance import (  # noqa: E402
    action_commands,
    plant_signature,
    transition_differences,
    unit_signature,
)
from cgauto.replay_state import to_game_state  # noqa: E402
from cgauto.top_player_opening_analysis import assigned_unit_commands  # noqa: E402
from sim.engine import step  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
SNAPSHOT = REPO / "data/raw/snapshots/20260721T105508Z-d61p"
PROTOCOL = ANALYSIS / "d85a-field-defensive-salvage-protocol-2026-07-21.md"
ARMS = ("control", "harvest", "joint_chop", "salvage")
ENDPOINT_FIELDS = (
    "own_score",
    "opponent_score",
    "own_liquid",
    "opponent_liquid",
    "liquid_margin",
    "own_workers",
    "opponent_workers",
    "own_carried_fruit",
    "opponent_carried_fruit",
    "own_carried_wood",
    "opponent_carried_wood",
    "target_exists",
    "target_health",
    "target_fruits",
    "target_size",
    "target_cooldown",
    "selected_unit_fruit",
    "selected_unit_wood",
    "endpoint_state_hash",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def command_verb(command: str | None) -> str:
    fields = (command or "").split()
    return fields[0].upper() if fields else "NONE"


def player_units(state: dict, player: int) -> list[dict]:
    return [unit for unit in state["units"] if int(unit["player"]) == player]


def replace_unit_command(
    commands: list[str], units: list[dict], unit_id: int, replacement: str
) -> list[str]:
    """Replace the first command assigned to one unit while preserving slots/order."""

    result = list(commands)
    unit_ids = sorted(int(unit["id"]) for unit in units)
    action_slot = 0
    assigned = set()
    for index, command in enumerate(result):
        fields = command.split()
        if not fields:
            continue
        verb = fields[0].upper()
        if verb in ("TRAIN", "MSG"):
            continue
        positional_id = unit_ids[action_slot] if action_slot < len(unit_ids) else None
        action_slot += 1
        if verb == "WAIT":
            assigned_id = positional_id
        else:
            try:
                assigned_id = int(fields[1])
            except (IndexError, ValueError):
                assigned_id = positional_id
        if assigned_id is None or assigned_id in assigned:
            continue
        assigned.add(assigned_id)
        if assigned_id == unit_id:
            result[index] = replacement
            return result
    result.append(replacement)
    return result


def liquid_value(game, player: int) -> int:
    carried = [unit for unit in game.units if unit.player == player]
    return game.scores[player] + sum(
        sum(unit.carry[:4]) + 4 * unit.carry[5] for unit in carried
    )


def target_signature(game, cell: tuple[int, int]) -> tuple | None:
    plant = next((plant for plant in game.plants if plant.pos == cell), None)
    if plant is None:
        return None
    return (
        plant.type,
        plant.x,
        plant.y,
        plant.size,
        plant.health,
        plant.fruits,
        plant.cooldown,
    )


def involved_unit_economy(game, unit_ids: set[int]) -> list[tuple]:
    return sorted(
        (
            unit.id,
            unit.player,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
            tuple(unit.carry),
        )
        for unit in game.units
        if unit.id in unit_ids
    )


def endpoint_metrics(
    game, resident: int, attacker: int, cell: tuple[int, int], selected_id: int
) -> dict[str, int | str]:
    plant = next((plant for plant in game.plants if plant.pos == cell), None)
    selected = next((unit for unit in game.units if unit.id == selected_id), None)
    own_units = [unit for unit in game.units if unit.player == resident]
    opponent_units = [unit for unit in game.units if unit.player == attacker]
    state = {
        "inventories": game.inventories,
        "scores": game.scores,
        "units": unit_signature(game, include_position=True),
        "plants": plant_signature(game),
    }
    own_liquid = liquid_value(game, resident)
    opponent_liquid = liquid_value(game, attacker)
    return {
        "own_score": game.scores[resident],
        "opponent_score": game.scores[attacker],
        "own_liquid": own_liquid,
        "opponent_liquid": opponent_liquid,
        "liquid_margin": own_liquid - opponent_liquid,
        "own_workers": len(own_units),
        "opponent_workers": len(opponent_units),
        "own_carried_fruit": sum(sum(unit.carry[:4]) for unit in own_units),
        "opponent_carried_fruit": sum(sum(unit.carry[:4]) for unit in opponent_units),
        "own_carried_wood": sum(unit.carry[5] for unit in own_units),
        "opponent_carried_wood": sum(unit.carry[5] for unit in opponent_units),
        "target_exists": int(plant is not None),
        "target_health": plant.health if plant is not None else -1,
        "target_fruits": plant.fruits if plant is not None else -1,
        "target_size": plant.size if plant is not None else -1,
        "target_cooldown": plant.cooldown if plant is not None else -1,
        "selected_unit_fruit": sum(selected.carry[:4]) if selected is not None else -1,
        "selected_unit_wood": selected.carry[5] if selected is not None else -1,
        "endpoint_state_hash": sha256_text(
            json.dumps(state, sort_keys=True, separators=(",", ":"))
        ),
    }


def choose_harvester(units: list[dict], plant: dict) -> dict | None:
    if int(plant["fruits"]) <= 0:
        return None
    eligible = [
        unit
        for unit in units
        if int(unit["hp"]) > 0 and unit_free(unit) > 0
    ]
    return max(
        eligible,
        key=lambda unit: (
            min(int(unit["hp"]), unit_free(unit)),
            int(unit["hp"]),
            unit_free(unit),
            -int(unit["id"]),
        ),
        default=None,
    )


def choose_joint_chopper(
    units: list[dict], plant: dict, maximum_attacker_chop: int, harvest_available: bool
) -> dict | None:
    if harvest_available or int(plant["health"]) > maximum_attacker_chop:
        return None
    eligible = [
        unit
        for unit in units
        if int(unit["chop"]) > 0 and unit_free(unit) > 0
    ]
    return max(
        eligible,
        key=lambda unit: (int(unit["chop"]), unit_free(unit), -int(unit["id"])),
        default=None,
    )


def arm_candidate(
    arm: str, harvester: dict | None, chopper: dict | None
) -> tuple[dict | None, str]:
    if arm == "harvest":
        return harvester, "HARVEST"
    if arm == "joint_chop":
        return chopper, "CHOP"
    if arm == "salvage":
        if harvester is not None:
            return harvester, "HARVEST"
        return chopper, "CHOP"
    return None, ""


def extract_task(task: dict) -> dict:
    game = task["game"]
    resident_rows = [
        player
        for player in game["players"]
        if int(player.get("agentId", -1)) == int(task["resident_agent_id"])
    ]
    if len(resident_rows) != 1:
        return {"rows": [], "integrity": None}
    resident_row = resident_rows[0]
    attacker_row = next(player for player in game["players"] if player is not resident_row)
    if attacker_row.get("userId") is None:
        raise ValueError(f"D85 game {game['gameId']} has no opponent account")
    resident = int(resident_row["index"])
    attacker = 1 - resident
    game_id = int(game["gameId"])
    user_id = int(attacker_row["userId"])
    source_agent_id = int(attacker_row["agentId"])

    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    decoded_map, states, unknown = decoded_states(raw, trajectory)
    expected_final = [
        list(game["per_player"][str(player)]["final_inv"]) for player in (0, 1)
    ]
    final_exact = states[-1]["inventories"] == expected_final
    if len(states) != len(trajectory) + 1 or unknown or not final_exact:
        raise ValueError(f"D85 decoded trajectory mismatch in game {game_id}")
    records, provenance = crop_provenance(raw, trajectory, attacker)
    if provenance["unknown_diff_updates"] or provenance["decoded_turns"] != len(trajectory):
        raise ValueError(f"D85 provenance mismatch in game {game_id}")
    confirmed = confirmed_chop_cells(raw, trajectory, states, attacker)

    rows = []
    trigger_count = 0
    for crop_ordinal, record in enumerate(records):
        cell = tuple(int(value) for value in record["cell"])
        birth = int(record["birth_turn"])
        death = record["death_turn"]
        last_alive = len(trajectory) if death is None else int(death) - 1
        for turn in range(birth, min(last_alive, len(trajectory) - 1) + 1):
            before_state = states[turn]
            plant = plant_at(before_state, cell)
            if plant is None:
                raise ValueError(f"D85 live generation absent in game {game_id}, turn {turn}")
            attacker_on = [
                unit
                for unit in player_units(before_state, attacker)
                if (int(unit["x"]), int(unit["y"])) == cell
                and int(unit["chop"]) > 0
                and unit_free(unit) > 0
            ]
            resident_on = [
                unit
                for unit in player_units(before_state, resident)
                if (int(unit["x"]), int(unit["y"])) == cell
            ]
            if not attacker_on or not resident_on:
                continue
            maximum_attacker_chop = max(int(unit["chop"]) for unit in attacker_on)
            harvester = choose_harvester(resident_on, plant)
            chopper = choose_joint_chopper(
                resident_on,
                plant,
                maximum_attacker_chop,
                harvester is not None,
            )
            if harvester is None and chopper is None:
                continue

            trigger_count += 1
            next_turn = turn + 1
            command_row = trajectory[turn]
            commands = [
                action_commands(command_row.get(f"commands{player}"))
                for player in (0, 1)
            ]
            resident_units = player_units(before_state, resident)
            assigned = assigned_unit_commands(commands[resident], resident_units)
            label = int(next_turn in confirmed.get(cell, set()))
            involved_ids = {
                int(unit["id"]) for unit in (*attacker_on, *resident_on)
            }

            control_game = to_game_state(decoded_map, before_state)
            step(control_game, commands[0], commands[1])
            official_game = to_game_state(decoded_map, states[next_turn])
            differences = transition_differences(control_game, official_game)
            full_material_exact = int(not differences or differences == ["unit_position"])
            target_local_exact = int(
                target_signature(control_game, cell) == target_signature(official_game, cell)
                and involved_unit_economy(control_game, involved_ids)
                == involved_unit_economy(official_game, involved_ids)
            )
            control_endpoint = endpoint_metrics(
                control_game, resident, attacker, cell, -1
            )

            identity_hash = sha256_text(
                f"d85-trigger:{game_id}:{crop_ordinal}:{cell[0]}:{cell[1]}:{turn}"
            )
            for arm in ARMS:
                candidate, response_verb = arm_candidate(arm, harvester, chopper)
                selected_id = -1 if candidate is None else int(candidate["id"])
                original_command = assigned.get(selected_id, "") if selected_id >= 0 else ""
                replaced_verb = command_verb(original_command)
                available = int(arm == "control" or candidate is not None)
                intervention = int(
                    arm != "control"
                    and candidate is not None
                    and replaced_verb != response_verb
                )
                treated_commands = [list(commands[0]), list(commands[1])]
                if intervention:
                    treated_commands[resident] = replace_unit_command(
                        treated_commands[resident],
                        resident_units,
                        selected_id,
                        f"{response_verb} {selected_id}",
                    )
                if arm == "control" or not intervention:
                    endpoint = control_endpoint
                else:
                    treatment_game = to_game_state(decoded_map, before_state)
                    step(treatment_game, treated_commands[0], treated_commands[1])
                    endpoint = endpoint_metrics(
                        treatment_game, resident, attacker, cell, selected_id
                    )
                rows.append(
                    {
                        "game_id": game_id,
                        "crop_ordinal": crop_ordinal,
                        "cell_x": cell[0],
                        "cell_y": cell[1],
                        "turn": turn,
                        "next_turn": next_turn,
                        "resident_seat": resident,
                        "opponent_user_id": user_id,
                        "source_agent_id": source_agent_id,
                        "partition": opponent_partition(user_id),
                        "label": label,
                        "trigger_hash": identity_hash,
                        "plant_type": plant["type"],
                        "plant_health": int(plant["health"]),
                        "plant_fruits": int(plant["fruits"]),
                        "plant_size": int(plant["size"]),
                        "maximum_attacker_chop": maximum_attacker_chop,
                        "attackers_on_target": len(attacker_on),
                        "residents_on_target": len(resident_on),
                        "arm": arm,
                        "available": available,
                        "intervention": intervention,
                        "selected_unit_id": selected_id,
                        "replaced_verb": replaced_verb,
                        "response_verb": response_verb,
                        "control_command_hash": sha256_text(
                            json.dumps(commands, separators=(",", ":"))
                        ),
                        "treatment_command_hash": sha256_text(
                            json.dumps(treated_commands, separators=(",", ":"))
                        ),
                        "baseline_classification": (
                            "exact"
                            if not differences
                            else (
                                "movement_rng_only"
                                if differences == ["unit_position"]
                                else "material_mismatch"
                            )
                        ),
                        "baseline_difference_fields": ",".join(differences),
                        "full_material_exact": full_material_exact,
                        "target_local_exact": target_local_exact,
                        **endpoint,
                    }
                )

    return {
        "rows": rows,
        "integrity": {
            "game_id": game_id,
            "trajectory_turns": len(trajectory),
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": unknown,
            "final_inventory_exact": final_exact,
            "resident_crops": len(records),
            "triggers": trigger_count,
        },
    }


def write_tsv_new(path: Path, rows: list[dict]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            target.flush()
            os.fsync(target.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json_new(path: Path, value: dict) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as target:
            target.write(content)
            target.flush()
            os.fsync(target.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def extract(snapshot: Path, rows_output: Path, manifest_output: Path, jobs: int) -> dict:
    if not 1 <= jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    loaded = load_open_inputs(snapshot)
    if loaded["snapshot_id"] != EXPECTED_SNAPSHOT:
        raise ValueError(f"D85 is frozen to snapshot {EXPECTED_SNAPSHOT}")
    if int(loaded["resident_agent_id"]) != EXPECTED_RESIDENT:
        raise ValueError("D85 resident changed")
    tasks = [
        task
        for task in loaded["tasks"]
        if any(
            int(player.get("agentId", -1)) == EXPECTED_RESIDENT
            for player in task["game"]["players"]
        )
    ]
    if jobs == 1:
        extracted = [extract_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            extracted = list(executor.map(extract_task, tasks, chunksize=2))
    integrity = sorted(
        (item["integrity"] for item in extracted if item["integrity"]),
        key=lambda row: row["game_id"],
    )
    rows = [row for item in extracted for row in item["rows"]]
    arm_order = {arm: index for index, arm in enumerate(ARMS)}
    rows.sort(
        key=lambda row: (
            row["game_id"],
            row["crop_ordinal"],
            row["turn"],
            arm_order[row["arm"]],
        )
    )
    identities = {
        (row["game_id"], row["crop_ordinal"], row["turn"])
        for row in rows
    }
    manifest = {
        "schema": "troll-farm-d85a-field-defensive-salvage-extract-v1",
        "snapshot_id": loaded["snapshot_id"],
        "resident_agent_id": loaded["resident_agent_id"],
        "scope": "open snapshot only; no sealed confirmation or platform action",
        "input_hashes": loaded["input_hashes"],
        "resident_games": len(integrity),
        "resident_crops": sum(row["resident_crops"] for row in integrity),
        "trigger_games": sum(row["triggers"] > 0 for row in integrity),
        "triggers": len(identities),
        "rows": len(rows),
        "confirmation_products_read": False,
        "game_integrity": integrity,
    }
    write_tsv_new(rows_output, rows)
    write_json_new(manifest_output, manifest)
    return manifest


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def mean(values) -> float:
    return statistics.fmean(values)


def trigger_key(row: dict[str, str]) -> tuple[int, int, int]:
    return (int(row["game_id"]), int(row["crop_ordinal"]), int(row["turn"]))


def paired_delta(row: dict[str, str], control: dict[str, str], field: str) -> int:
    return int(row[field]) - int(control[field])


def analyze(
    rows_a_path: Path,
    rows_b_path: Path,
    manifest_a_path: Path,
    manifest_b_path: Path,
) -> dict:
    rows_a_path = rows_a_path.resolve()
    rows_b_path = rows_b_path.resolve()
    manifest_a_path = manifest_a_path.resolve()
    manifest_b_path = manifest_b_path.resolve()
    rows_a_bytes = rows_a_path.read_bytes()
    rows_b_bytes = rows_b_path.read_bytes()
    rows = read_tsv(rows_a_path)
    manifest_a = json.loads(manifest_a_path.read_text())
    manifest_b = json.loads(manifest_b_path.read_text())
    grouped: dict[tuple[int, int, int], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        grouped[trigger_key(row)][row["arm"]] = row

    arm_set_failures = sum(set(arms) != set(ARMS) for arms in grouped.values())
    parity_failures = 0
    arm_accounting_failures = 0
    for arms in grouped.values():
        control = arms.get("control")
        if control is None:
            continue
        for arm, row in arms.items():
            arm_accounting_failures += int(
                (arm == "control" and (int(row["available"]) != 1 or int(row["intervention"]) != 0))
                or (int(row["intervention"]) > int(row["available"]))
                or (arm != "control" and int(row["available"]) == 0 and int(row["selected_unit_id"]) != -1)
            )
            if arm == "control" or int(row["intervention"]) == 1:
                continue
            parity_failures += int(
                any(row[field] != control[field] for field in ENDPOINT_FIELDS)
                or row["treatment_command_hash"] != control["control_command_hash"]
            )

    controls = [arms["control"] for arms in grouped.values() if "control" in arms]
    material_exact_rate = mean(int(row["full_material_exact"]) for row in controls) if controls else 0.0
    target_local_exact_rate = mean(int(row["target_local_exact"]) for row in controls) if controls else 0.0
    game_integrity = manifest_a.get("game_integrity", [])
    extraction_integrity = bool(game_integrity) and all(
        int(row["trajectory_turns"]) == int(row["decoded_turns"])
        and int(row["unknown_diff_updates"]) == 0
        and bool(row["final_inventory_exact"])
        for row in game_integrity
    )
    integrity_gates = {
        "byte_identical_rows": rows_a_bytes == rows_b_bytes,
        "byte_identical_manifests": manifest_a_path.read_bytes() == manifest_b_path.read_bytes(),
        "complete_four_arm_sets": arm_set_failures == 0 and len(rows) == 4 * len(grouped),
        "zero_arm_accounting_failures": arm_accounting_failures == 0,
        "unavailable_or_unchanged_arms_match_control": parity_failures == 0,
        "all_selected_replays_exact": extraction_integrity,
        "target_local_exact_100_percent": target_local_exact_rate == 1.0,
        "full_material_exact_at_least_95_percent": material_exact_rate >= 0.95,
        "confirmation_products_read_false": not manifest_a.get("confirmation_products_read", True),
    }
    integrity_pass = all(integrity_gates.values())

    triggers = list(controls)
    partition_rows = {
        partition: [row for row in triggers if row["partition"] == partition]
        for partition in ("discovery", "validation")
    }
    partition_support = {}
    for partition, selected in partition_rows.items():
        partition_support[partition] = {
            "triggers": len(selected),
            "confirmed_attacks": sum(int(row["label"]) for row in selected),
            "opponent_accounts": len({row["opponent_user_id"] for row in selected}),
            "seats": sorted({int(row["resident_seat"]) for row in selected}),
            "attack_precision": (
                sum(int(row["label"]) for row in selected) / len(selected)
                if selected
                else 0.0
            ),
        }
    salvage_interventions = sum(
        int(arms["salvage"]["intervention"]) for arms in grouped.values()
    )
    semantic_interventions = {
        arm: sum(int(arms[arm]["intervention"]) for arms in grouped.values())
        for arm in ("harvest", "joint_chop")
    }
    support_gates = {
        "at_least_16_triggers_each_partition": all(
            values["triggers"] >= 16 for values in partition_support.values()
        ),
        "at_least_8_attacks_each_partition": all(
            values["confirmed_attacks"] >= 8 for values in partition_support.values()
        ),
        "both_seats_complete_corpus": {int(row["resident_seat"]) for row in triggers} == {0, 1},
        "at_least_4_accounts_each_partition": all(
            values["opponent_accounts"] >= 4 for values in partition_support.values()
        ),
        "at_least_16_salvage_interventions": salvage_interventions >= 16,
        "one_semantic_has_at_least_8_interventions": max(semantic_interventions.values(), default=0) >= 8,
    }
    support_pass = all(support_gates.values())
    trigger_precision = partition_support["validation"]["attack_precision"]
    observability_gates = {"validation_attack_precision_at_least_85_percent": trigger_precision >= 0.85}
    observability_pass = all(observability_gates.values())

    validation = [
        arms
        for arms in grouped.values()
        if arms["control"]["partition"] == "validation"
        and int(arms["control"]["target_local_exact"]) == 1
    ]
    deltas = []
    changed_deltas = []
    own_deltas = []
    opponent_deltas = []
    premature_deaths = 0
    account_deltas: dict[str, list[int]] = defaultdict(list)
    changed_validation = 0
    for arms in validation:
        control = arms["control"]
        salvage = arms["salvage"]
        delta = paired_delta(salvage, control, "liquid_margin")
        own_delta = paired_delta(salvage, control, "own_liquid")
        opponent_delta = paired_delta(salvage, control, "opponent_liquid")
        deltas.append(delta)
        own_deltas.append(own_delta)
        opponent_deltas.append(opponent_delta)
        account_deltas[control["opponent_user_id"]].append(delta)
        if int(salvage["intervention"]) == 1:
            changed_validation += 1
            changed_deltas.append(delta)
        premature_deaths += int(
            int(control["target_exists"]) == 1 and int(salvage["target_exists"]) == 0
        )
    account_means = {
        account: mean(values) for account, values in sorted(account_deltas.items())
    }
    fixed_metrics = {
        "validation_triggers": len(validation),
        "changed_interventions": changed_validation,
        "intervention_rate": changed_validation / len(validation) if validation else 0.0,
        "mean_liquid_margin_gain": mean(deltas) if deltas else 0.0,
        "changed_strict_improvement_rate": (
            sum(value > 0 for value in changed_deltas) / len(changed_deltas)
            if changed_deltas
            else 0.0
        ),
        "changed_regression_rate": (
            sum(value < 0 for value in changed_deltas) / len(changed_deltas)
            if changed_deltas
            else 0.0
        ),
        "mean_own_liquid_delta": mean(own_deltas) if own_deltas else 0.0,
        "mean_opponent_liquid_delta": mean(opponent_deltas) if opponent_deltas else 0.0,
        "treatment_only_crop_deaths": premature_deaths,
        "opponent_account_mean_gains": account_means,
        "nonnegative_opponent_accounts": sum(value >= 0 for value in account_means.values()),
        "worst_opponent_account_mean": min(account_means.values(), default=0.0),
    }
    fixed_value_gates = {
        "mean_margin_gain_at_least_0_25": fixed_metrics["mean_liquid_margin_gain"] >= 0.25,
        "changed_strict_improvement_at_least_50_percent": fixed_metrics[
            "changed_strict_improvement_rate"
        ]
        >= 0.50,
        "changed_regression_at_most_5_percent": fixed_metrics["changed_regression_rate"] <= 0.05,
        "own_nonnegative_and_opponent_nonpositive": fixed_metrics["mean_own_liquid_delta"] >= 0
        and fixed_metrics["mean_opponent_liquid_delta"] <= 0,
        "zero_treatment_only_crop_deaths": premature_deaths == 0,
        "four_nonnegative_accounts_and_worst_nonnegative": fixed_metrics[
            "nonnegative_opponent_accounts"
        ]
        >= 4
        and fixed_metrics["worst_opponent_account_mean"] >= 0,
        "at_least_8_changed_validation_interventions": changed_validation >= 8,
    }
    fixed_value_pass = all(fixed_value_gates.values())

    semantic_metrics = {}
    for arm in ("harvest", "joint_chop"):
        available = []
        changed = []
        for arms in grouped.values():
            control = arms["control"]
            row = arms[arm]
            if int(row["available"]) == 0 or int(control["target_local_exact"]) == 0:
                continue
            delta = paired_delta(row, control, "liquid_margin")
            available.append(delta)
            if int(row["intervention"]) == 1:
                changed.append(delta)
        semantic_metrics[arm] = {
            "available_triggers": len(available),
            "changed_interventions": len(changed),
            "available_mean_liquid_margin_gain": mean(available) if available else 0.0,
            "changed_strict_improvement_rate": (
                sum(value > 0 for value in changed) / len(changed) if changed else 0.0
            ),
            "changed_regression_rate": (
                sum(value < 0 for value in changed) / len(changed) if changed else 0.0
            ),
        }

    oracle_deltas = []
    oracle_counts: Counter[str] = Counter()
    for arms in validation:
        control = arms["control"]
        eligible = [control] + [
            row
            for arm, row in arms.items()
            if arm in ("harvest", "joint_chop") and int(row["available"]) == 1
        ]
        best = max(
            eligible,
            key=lambda row: (int(row["liquid_margin"]), -ARMS.index(row["arm"])),
        )
        oracle_deltas.append(paired_delta(best, control, "liquid_margin"))
        oracle_counts[best["arm"]] += 1

    if not integrity_pass:
        decision = "quarantine_integrity_failure"
    elif not support_pass:
        decision = "reject_insufficient_field_support"
    elif not observability_pass:
        decision = "reject_on_target_trigger_not_precise"
    elif not fixed_value_pass:
        decision = "reject_one_turn_salvage_value_or_safety"
    else:
        decision = "pass_open_d85b_resident_integration"
    passed = (
        integrity_pass and support_pass and observability_pass and fixed_value_pass
    )
    return {
        "schema": "troll-farm-d85a-field-defensive-salvage-result-v1",
        "scope": "open current-field one-turn command counterfactual only; no terminal or candidate claim",
        "protocol": str(PROTOCOL.relative_to(REPO)),
        "protocol_sha256": sha256_file(PROTOCOL),
        "inputs": {
            "rows_a": str(rows_a_path.relative_to(REPO)),
            "rows_a_sha256": sha256_file(rows_a_path),
            "rows_b": str(rows_b_path.relative_to(REPO)),
            "rows_b_sha256": sha256_file(rows_b_path),
            "manifest_a": str(manifest_a_path.relative_to(REPO)),
            "manifest_a_sha256": sha256_file(manifest_a_path),
            "manifest_b": str(manifest_b_path.relative_to(REPO)),
            "manifest_b_sha256": sha256_file(manifest_b_path),
            "analyzer_sha256": sha256_file(Path(__file__)),
        },
        "audit": {
            "rows_per_repeat": len(rows),
            "triggers": len(grouped),
            "arm_set_failures": arm_set_failures,
            "arm_accounting_failures": arm_accounting_failures,
            "parity_failures": parity_failures,
            "target_local_exact_rate": target_local_exact_rate,
            "full_material_exact_rate": material_exact_rate,
            "baseline_classifications": dict(
                sorted(Counter(row["baseline_classification"] for row in controls).items())
            ),
        },
        "integrity_gates": integrity_gates,
        "integrity_pass": integrity_pass,
        "support": {
            "partitions": partition_support,
            "salvage_interventions": salvage_interventions,
            "semantic_interventions": semantic_interventions,
        },
        "support_gates": support_gates,
        "support_pass": support_pass,
        "observability_gates": observability_gates,
        "observability_pass": observability_pass,
        "fixed_salvage": fixed_metrics,
        "fixed_value_gates": fixed_value_gates,
        "fixed_value_pass": fixed_value_pass,
        "semantic_arms": semantic_metrics,
        "immediate_oracle": {
            "mean_liquid_margin_gain": mean(oracle_deltas) if oracle_deltas else 0.0,
            "selected_arm_counts": dict(sorted(oracle_counts.items())),
        },
        "decision": decision,
        "pass": passed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    extract_parser.add_argument("--rows-output", type=Path, required=True)
    extract_parser.add_argument("--manifest-output", type=Path, required=True)
    extract_parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("--rows-a", type=Path, required=True)
    analyze_parser.add_argument("--rows-b", type=Path, required=True)
    analyze_parser.add_argument("--manifest-a", type=Path, required=True)
    analyze_parser.add_argument("--manifest-b", type=Path, required=True)
    analyze_parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "extract":
        manifest = extract(
            args.snapshot, args.rows_output, args.manifest_output, args.jobs
        )
        print(
            json.dumps(
                {
                    "resident_games": manifest["resident_games"],
                    "triggers": manifest["triggers"],
                    "rows": manifest["rows"],
                },
                sort_keys=True,
            )
        )
        return
    result = analyze(args.rows_a, args.rows_b, args.manifest_a, args.manifest_b)
    write_json_new(args.output, result)
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "integrity_pass": result["integrity_pass"],
                "support_pass": result["support_pass"],
                "observability_pass": result["observability_pass"],
                "fixed_value_pass": result["fixed_value_pass"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
