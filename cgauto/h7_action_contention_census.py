#!/usr/bin/env python3
"""Exact H7' cross-player action-contention census on the frozen D159 panel."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import statistics
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import waste_sweep
from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import assigned_unit_commands, bfs

REPO = Path(__file__).resolve().parent.parent
EXPECTED_MANIFEST_SHA256 = (
    "97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443"
)
EXPECTED_ACCEPTED_RESULT_SHA256 = (
    "bd3fe4571aec423cdb57d514a2f610c0dcfe9845099b5500a6721e98d72965ac"
)
EXPECTED_RESIDENT_SOURCE_SHA256 = (
    "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
)
EXPECTED_RESIDENT_AGENT_ID = 6561795
EXPECTED_GAMES = 200
BOOTSTRAP_SEED = 20260731
BOOTSTRAP_REPLICATES = 10_000
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
ITEM_INDEX = {item: index for index, item in enumerate(ITEMS)}
TREE_HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}
PRIMARY_EVENTS = (
    "dual_harvest",
    "dual_chop",
    "resident_move_target_removed",
    "resident_move_target_depleted",
)
COUNT_KEYS = (
    "same_tree_colocation",
    "same_tree_move_target",
    "dual_harvest",
    "last_fruit_duplication",
    "dual_chop",
    "last_wood_duplication",
    "combined_only_kill",
    "resident_move_target_removed",
    "resident_move_target_depleted",
    "opponent_move_target_removed",
    "opponent_move_target_depleted",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def free_capacity(unit: dict[str, Any]) -> int:
    return int(unit["cc"]) - sum(int(value) for value in unit["carry"])


def command_verb(command: str | None) -> str:
    return command.split()[0].upper() if command else "WAIT"


def move_target(command: str | None) -> tuple[int, int] | None:
    fields = command.split() if command else []
    if len(fields) != 4 or fields[0].upper() != "MOVE":
        return None
    try:
        return int(fields[2]), int(fields[3])
    except ValueError:
        return None


def harvest_awards(
    fruits: int, ordered_units: list[tuple[int, dict[str, Any]]]
) -> tuple[dict[int, int], int]:
    """Exact referee round allocation, including the last-fruit duplication quirk."""

    remaining = int(fruits)
    gains = {int(unit["id"]): 0 for _, unit in ordered_units}
    for power_round in range(1, 4):
        if remaining == 0:
            break
        for _, unit in ordered_units:
            unit_id = int(unit["id"])
            if int(unit["hp"]) >= power_round and free_capacity(unit) > gains[unit_id]:
                gains[unit_id] += 1
                if remaining > 0:
                    remaining -= 1
    return gains, remaining


def wood_awards(
    size: int, ordered_units: list[tuple[int, dict[str, Any]]]
) -> tuple[dict[int, int], int]:
    """Exact lethal-CHOP wood allocation, including last-wood duplication."""

    remaining = int(size)
    gains = {int(unit["id"]): 0 for _, unit in ordered_units}
    round_index = 0
    while round_index < int(size) and remaining > 0:
        for _, unit in ordered_units:
            unit_id = int(unit["id"])
            if free_capacity(unit) > gains[unit_id]:
                gains[unit_id] += 1
                remaining -= 1
        round_index += 1
    return gains, remaining


def ticked_plant(
    plant: dict[str, Any], *, fruits: int | None = None, health: int | None = None
) -> dict[str, int]:
    """Relevant exact plant state after the end-of-turn tick."""

    size = int(plant["size"])
    result_health = int(plant["health"] if health is None else health)
    result_fruits = int(plant["fruits"] if fruits is None else fruits)
    cooldown = int(plant["cooldown"])
    if cooldown > 0:
        cooldown -= 1
    if cooldown == 0 and result_health > 0:
        if size < 4:
            size += 1
            result_health += TREE_HEALTH_SLOPE[str(plant["type"]).upper()]
        elif result_fruits < 3:
            result_fruits += 1
    return {"size": size, "health": result_health, "fruits": result_fruits}


def transition_carry_delta(
    before_units: dict[int, dict[str, Any]],
    after_units: dict[int, dict[str, Any]],
    unit_id: int,
    item_index: int,
) -> int | None:
    if unit_id not in before_units or unit_id not in after_units:
        return None
    return int(after_units[unit_id]["carry"][item_index]) - int(
        before_units[unit_id]["carry"][item_index]
    )


def assigned_by_player(
    game: waste_sweep.DecodedGame, turn_index: int, before: dict[str, Any]
) -> dict[int, dict[int, str]]:
    row = game.trajectory[turn_index]
    result: dict[int, dict[int, str]] = {}
    for player in (0, 1):
        units = [unit for unit in before["units"] if int(unit["player"]) == player]
        commands = action_commands(row.get(f"commands{player}"))
        result[player] = assigned_unit_commands(commands, units)
    return result


def legal_action_unit(
    *,
    player: int,
    verb: str,
    cell: tuple[int, int],
    units: dict[int, dict[str, Any]],
    assigned: dict[int, dict[int, str]],
    plant: dict[str, Any],
) -> dict[str, Any] | None:
    candidates = []
    for unit in units.values():
        if int(unit["player"]) != player or (int(unit["x"]), int(unit["y"])) != cell:
            continue
        if command_verb(assigned[player].get(int(unit["id"]))) != verb:
            continue
        if verb == "HARVEST":
            if (
                int(plant["fruits"]) <= 0
                or int(unit["hp"]) <= 0
                or free_capacity(unit) <= 0
            ):
                continue
        elif verb == "CHOP" and int(unit["chop"]) <= 0:
            continue
        candidates.append(unit)
    if len(candidates) > 1:
        raise ValueError(f"multiple player-{player} {verb} units at {cell}")
    return candidates[0] if candidates else None


def move_reduced_distance(
    *,
    unit: dict[str, Any],
    after_unit: dict[str, Any] | None,
    target: tuple[int, int],
    walkable: set[tuple[int, int]],
) -> bool:
    if after_unit is None:
        return False
    distances = bfs(walkable, [target])
    before_cell = (int(unit["x"]), int(unit["y"]))
    after_cell = (int(after_unit["x"]), int(after_unit["y"]))
    return (
        before_cell in distances
        and after_cell in distances
        and distances[after_cell] < distances[before_cell]
    )


def audit_game(
    manifest_row: dict[str, Any], game: waste_sweep.DecodedGame
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    counts = Counter({key: 0 for key in COUNT_KEYS})
    examples: list[dict[str, Any]] = []

    for turn_index in range(game.turns):
        turn = turn_index + 1
        before = game.states[turn_index]
        after = game.states[turn_index + 1]
        units = {int(unit["id"]): unit for unit in before["units"]}
        after_units = {int(unit["id"]): unit for unit in after["units"]}
        before_plants = {
            (int(plant["x"]), int(plant["y"])): plant for plant in before["plants"]
        }
        after_plants = {
            (int(plant["x"]), int(plant["y"])): plant for plant in after["plants"]
        }
        assigned = assigned_by_player(game, turn_index, before)

        for cell, plant in before_plants.items():
            players_here = {
                int(unit["player"])
                for unit in units.values()
                if (int(unit["x"]), int(unit["y"])) == cell
            }
            if players_here == {0, 1}:
                counts["same_tree_colocation"] += 1

            harvesters = [
                legal_action_unit(
                    player=player,
                    verb="HARVEST",
                    cell=cell,
                    units=units,
                    assigned=assigned,
                    plant=plant,
                )
                for player in (0, 1)
            ]
            if all(harvesters):
                ordered = [(player, harvesters[player]) for player in (0, 1)]
                gains, remaining = harvest_awards(int(plant["fruits"]), ordered)
                item_index = ITEM_INDEX[str(plant["type"]).upper()]
                for _, unit in ordered:
                    unit_id = int(unit["id"])
                    observed = transition_carry_delta(
                        units, after_units, unit_id, item_index
                    )
                    if observed != gains[unit_id]:
                        errors.append(
                            f"{game.game_id} turn {turn}: dual HARVEST unit {unit_id} "
                            f"carry delta {observed} != {gains[unit_id]}"
                        )
                expected_plant = ticked_plant(plant, fruits=remaining)
                observed_plant = after_plants.get(cell)
                if observed_plant is None or int(observed_plant["fruits"]) != expected_plant[
                    "fruits"
                ]:
                    errors.append(
                        f"{game.game_id} turn {turn}: dual HARVEST plant transition mismatch"
                    )
                else:
                    counts["dual_harvest"] += 1
                    duplicated = max(0, sum(gains.values()) - int(plant["fruits"]))
                    counts["last_fruit_duplication"] += duplicated
                    if len(examples) < 8:
                        examples.append(
                            {
                                "turn": turn,
                                "family": "dual_harvest",
                                "cell": list(cell),
                                "pre_fruits": int(plant["fruits"]),
                                "awarded": sum(gains.values()),
                                "duplicated": duplicated,
                            }
                        )

            choppers = [
                legal_action_unit(
                    player=player,
                    verb="CHOP",
                    cell=cell,
                    units=units,
                    assigned=assigned,
                    plant=plant,
                )
                for player in (0, 1)
            ]
            if all(choppers):
                ordered = [(player, choppers[player]) for player in (0, 1)]
                damage = [int(choppers[player]["chop"]) for player in (0, 1)]
                dead = sum(damage) >= int(plant["health"])
                gains = {int(unit["id"]): 0 for _, unit in ordered}
                if dead:
                    gains, _ = wood_awards(int(plant["size"]), ordered)
                for _, unit in ordered:
                    unit_id = int(unit["id"])
                    observed = transition_carry_delta(
                        units, after_units, unit_id, ITEM_INDEX["WOOD"]
                    )
                    if observed != gains[unit_id]:
                        errors.append(
                            f"{game.game_id} turn {turn}: dual CHOP unit {unit_id} "
                            f"wood delta {observed} != {gains[unit_id]}"
                        )
                if dead:
                    transition_ok = cell not in after_plants
                else:
                    expected = ticked_plant(
                        plant, health=max(0, int(plant["health"]) - sum(damage))
                    )
                    observed_plant = after_plants.get(cell)
                    transition_ok = (
                        observed_plant is not None
                        and int(observed_plant["health"]) == expected["health"]
                        and int(observed_plant["size"]) == expected["size"]
                    )
                if not transition_ok:
                    errors.append(
                        f"{game.game_id} turn {turn}: dual CHOP plant transition mismatch"
                    )
                else:
                    counts["dual_chop"] += 1
                    duplicated = max(0, sum(gains.values()) - int(plant["size"]))
                    counts["last_wood_duplication"] += duplicated
                    combined_only = dead and all(
                        value < int(plant["health"]) for value in damage
                    )
                    counts["combined_only_kill"] += int(combined_only)
                    if len(examples) < 8:
                        examples.append(
                            {
                                "turn": turn,
                                "family": "dual_chop",
                                "cell": list(cell),
                                "pre_health": int(plant["health"]),
                                "damage": damage,
                                "dead": dead,
                                "combined_only": combined_only,
                                "duplicated_wood": duplicated,
                            }
                        )

        move_targets: dict[int, dict[tuple[int, int], list[dict[str, Any]]]] = {
            0: defaultdict(list),
            1: defaultdict(list),
        }
        for player in (0, 1):
            for unit_id, command in assigned[player].items():
                target = move_target(command)
                unit = units.get(unit_id)
                if target is None or unit is None or target not in before_plants:
                    continue
                if move_reduced_distance(
                    unit=unit,
                    after_unit=after_units.get(unit_id),
                    target=target,
                    walkable=game.board["walkable"],
                ):
                    move_targets[player][target].append(unit)
        counts["same_tree_move_target"] += len(
            set(move_targets[0]).intersection(move_targets[1])
        )

        for mover_player in (0, 1):
            actor_player = 1 - mover_player
            mover_label = "resident" if mover_player == game.me else "opponent"
            for target, movers in move_targets[mover_player].items():
                plant = before_plants[target]
                for mover in movers:
                    capability_free = free_capacity(mover)
                    chopper = legal_action_unit(
                        player=actor_player,
                        verb="CHOP",
                        cell=target,
                        units=units,
                        assigned=assigned,
                        plant=plant,
                    )
                    if (
                        chopper is not None
                        and int(mover["chop"]) > 0
                        and capability_free > 0
                        and int(plant["size"]) > 0
                        and int(chopper["chop"]) >= int(plant["health"])
                        and target not in after_plants
                    ):
                        key = f"{mover_label}_move_target_removed"
                        counts[key] += 1
                        if len(examples) < 8:
                            examples.append(
                                {
                                    "turn": turn,
                                    "family": key,
                                    "cell": list(target),
                                    "tree_size": int(plant["size"]),
                                }
                            )
                    harvester = legal_action_unit(
                        player=actor_player,
                        verb="HARVEST",
                        cell=target,
                        units=units,
                        assigned=assigned,
                        plant=plant,
                    )
                    observed_plant = after_plants.get(target)
                    if (
                        harvester is not None
                        and int(mover["hp"]) > 0
                        and capability_free > 0
                        and int(plant["fruits"]) > 0
                        and observed_plant is not None
                        and int(observed_plant["fruits"]) == 0
                    ):
                        key = f"{mover_label}_move_target_depleted"
                        counts[key] += 1
                        if len(examples) < 8:
                            examples.append(
                                {
                                    "turn": turn,
                                    "family": key,
                                    "cell": list(target),
                                    "pre_fruits": int(plant["fruits"]),
                                }
                            )

    primary_count = sum(counts[key] for key in PRIMARY_EVENTS)
    rank = int(manifest_row["opponent_rank"])
    cohort = "strong" if rank <= 20 else "middle" if rank <= 40 else "comparator"
    return (
        {
            "game_id": int(game.game_id),
            "opponent_agent_id": int(manifest_row["opponent_agent_id"]),
            "opponent": manifest_row["opponent"],
            "opponent_rank": rank,
            "opponent_ladder_score": float(manifest_row["opponent_ladder_score"]),
            "cohort": cohort,
            "resident_seat": int(manifest_row["seat"]),
            "turns": int(game.turns),
            "margin": int(manifest_row["margin"]),
            "won": bool(manifest_row["won"]),
            "counts": dict(counts),
            "primary_event_count": primary_count,
            "primary_event_game": primary_count > 0,
            "direct_duplication_score_ceiling": int(
                counts["last_fruit_duplication"]
                + 4 * counts["last_wood_duplication"]
            ),
            "examples": examples,
        },
        errors,
    )


def cohort_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    games = len(rows)
    turns = sum(int(row["turns"]) for row in rows)
    event_games = sum(bool(row["primary_event_game"]) for row in rows)
    counts = {
        key: sum(int(row["counts"][key]) for row in rows) for key in COUNT_KEYS
    }
    return {
        "games": games,
        "turns": turns,
        "opponent_identities": len({row["opponent_agent_id"] for row in rows}),
        "resident_seats": sorted({row["resident_seat"] for row in rows}),
        "primary_event_games": event_games,
        "primary_event_game_prevalence": event_games / games if games else None,
        "primary_events_per_1000_turns": (
            1000
            * sum(int(row["primary_event_count"]) for row in rows)
            / turns
            if turns
            else None
        ),
        "direct_duplication_score_ceiling": sum(
            int(row["direct_duplication_score_ceiling"]) for row in rows
        ),
        "direct_duplication_score_ceiling_per_game": (
            sum(int(row["direct_duplication_score_ceiling"]) for row in rows) / games
            if games
            else None
        ),
        "counts": counts,
        "mean_margin": statistics.fmean(row["margin"] for row in rows)
        if rows
        else None,
        "event_game_mean_margin": statistics.fmean(
            row["margin"] for row in rows if row["primary_event_game"]
        )
        if event_games
        else None,
        "non_event_game_mean_margin": statistics.fmean(
            row["margin"] for row in rows if not row["primary_event_game"]
        )
        if games > event_games
        else None,
        "event_game_mean_turns": statistics.fmean(
            row["turns"] for row in rows if row["primary_event_game"]
        )
        if event_games
        else None,
        "non_event_game_mean_turns": statistics.fmean(
            row["turns"] for row in rows if not row["primary_event_game"]
        )
        if games > event_games
        else None,
    }


def clustered_prevalence_difference(
    strong: list[dict[str, Any]],
    comparator: list[dict[str, Any]],
    *,
    replicates: int = BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    grouped: dict[str, dict[int, list[dict[str, Any]]]] = {
        "strong": defaultdict(list),
        "comparator": defaultdict(list),
    }
    for row in strong:
        grouped["strong"][int(row["opponent_agent_id"])].append(row)
    for row in comparator:
        grouped["comparator"][int(row["opponent_agent_id"])].append(row)
    strong_ids = sorted(grouped["strong"])
    comparator_ids = sorted(grouped["comparator"])

    def prevalence(sampled_ids: list[int], cohort: str) -> float:
        sampled = [
            row for opponent_id in sampled_ids for row in grouped[cohort][opponent_id]
        ]
        return sum(bool(row["primary_event_game"]) for row in sampled) / len(sampled)

    observed = prevalence(strong_ids, "strong") - prevalence(
        comparator_ids, "comparator"
    )
    rng = random.Random(seed)
    differences = []
    for _ in range(replicates):
        sampled_strong = [
            strong_ids[rng.randrange(len(strong_ids))] for _ in strong_ids
        ]
        sampled_comparator = [
            comparator_ids[rng.randrange(len(comparator_ids))]
            for _ in comparator_ids
        ]
        differences.append(
            prevalence(sampled_strong, "strong")
            - prevalence(sampled_comparator, "comparator")
        )
    differences.sort()
    return {
        "seed": seed,
        "replicates": replicates,
        "unit": "opponent identity",
        "observed_percentage_points": 100 * observed,
        "ci95_percentage_points": [
            100 * differences[int(0.025 * (replicates - 1))],
            100 * differences[int(0.975 * (replicates - 1))],
        ],
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cohorts = {
        name: [row for row in rows if row["cohort"] == name]
        for name in ("strong", "middle", "comparator")
    }
    summaries = {
        "all": cohort_summary(rows),
        **{name: cohort_summary(group) for name, group in cohorts.items()},
    }
    contrast = clustered_prevalence_difference(
        cohorts["strong"], cohorts["comparator"]
    )
    event_rows = [row for row in rows if row["primary_event_game"]]
    consequences = (
        summaries["all"]["counts"]["last_fruit_duplication"]
        + summaries["all"]["counts"]["last_wood_duplication"]
        + summaries["all"]["counts"]["combined_only_kill"]
        + summaries["all"]["counts"]["resident_move_target_removed"]
        + summaries["all"]["counts"]["resident_move_target_depleted"]
    )
    gates = {
        "at_least_20_event_games": len(event_rows) >= 20,
        "at_least_8_event_opponent_identities": len(
            {row["opponent_agent_id"] for row in event_rows}
        )
        >= 8,
        "both_resident_seats": {row["resident_seat"] for row in event_rows} == {0, 1},
        "strong_minus_comparator_at_least_10pp": contrast[
            "observed_percentage_points"
        ]
        >= 10,
        "cluster_bootstrap_ci_lower_positive": contrast[
            "ci95_percentage_points"
        ][0]
        > 0,
        "direct_mechanical_consequence_exists": consequences > 0,
    }
    return {
        "cohorts": summaries,
        "strong_vs_comparator": contrast,
        "primary_event_games": len(event_rows),
        "primary_event_opponent_identities": len(
            {row["opponent_agent_id"] for row in event_rows}
        ),
        "primary_event_resident_seats": sorted(
            {row["resident_seat"] for row in event_rows}
        ),
        "materiality_gates": gates,
        "materiality_pass": all(gates.values()),
    }


def run(
    *, manifest_path: Path, accepted_result_path: Path, data_root: Path
) -> dict[str, Any]:
    manifest_hash = sha256(manifest_path)
    accepted_hash = sha256(accepted_result_path)
    manifest = json.loads(manifest_path.read_text())
    accepted = json.loads(accepted_result_path.read_text())
    source_path = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
    )
    source_hash = sha256(source_path)
    rows = manifest.get("rows") or []
    game_ids = [int(row["game_id"]) for row in rows]
    raw_games = data_root / "raw/games"
    trajectories = data_root / "processed/trajectories"
    waste_sweep.RAW_GAMES = raw_games
    waste_sweep.TRAJECTORIES = trajectories

    errors: list[str] = []
    if manifest_hash != EXPECTED_MANIFEST_SHA256:
        errors.append("D159 manifest hash mismatch")
    if accepted_hash != EXPECTED_ACCEPTED_RESULT_SHA256:
        errors.append("D159 accepted-result hash mismatch")
    if source_hash != EXPECTED_RESIDENT_SOURCE_SHA256:
        errors.append("resident source hash mismatch")
    if len(game_ids) != EXPECTED_GAMES or len(set(game_ids)) != EXPECTED_GAMES:
        errors.append("D159 game ID count/uniqueness mismatch")
    if (
        accepted.get("identity", {}).get("resident_agent_id")
        != EXPECTED_RESIDENT_AGENT_ID
    ):
        errors.append("accepted result resident identity mismatch")
    if accepted.get("identity", {}).get("resident_source_sha256") != source_hash:
        errors.append("accepted result source hash mismatch")

    missing_raw = [
        game_id for game_id in game_ids if not (raw_games / f"{game_id}.json").is_file()
    ]
    missing_trajectory = [
        game_id
        for game_id in game_ids
        if not (trajectories / f"{game_id}.jsonl").is_file()
    ]
    if missing_raw:
        errors.append(f"missing raw games: {missing_raw}")
    if missing_trajectory:
        errors.append(f"missing trajectories: {missing_trajectory}")

    audited_rows = []
    if not missing_raw and not missing_trajectory:
        for manifest_row in rows:
            game_id = int(manifest_row["game_id"])
            try:
                game = waste_sweep.decode_game(game_id)
                if game.me != int(manifest_row["seat"]):
                    raise ValueError(
                        f"resident seat {game.me} != manifest {manifest_row['seat']}"
                    )
                audited, audit_errors = audit_game(manifest_row, game)
                audited_rows.append(audited)
                errors.extend(audit_errors)
            except Exception as exc:
                errors.append(f"{game_id}: {type(exc).__name__}: {exc}")

    summary = summarize(audited_rows) if len(audited_rows) == EXPECTED_GAMES else None
    cohort_integrity = bool(
        summary
        and summary["cohorts"]["strong"]["games"] >= 30
        and summary["cohorts"]["comparator"]["games"] >= 40
        and summary["cohorts"]["strong"]["opponent_identities"] >= 10
        and summary["cohorts"]["comparator"]["opponent_identities"] >= 10
        and summary["cohorts"]["strong"]["resident_seats"] == [0, 1]
        and summary["cohorts"]["comparator"]["resident_seats"] == [0, 1]
    )
    integrity = {
        "manifest_hash_exact": manifest_hash == EXPECTED_MANIFEST_SHA256,
        "accepted_result_hash_exact": accepted_hash
        == EXPECTED_ACCEPTED_RESULT_SHA256,
        "resident_source_hash_exact": source_hash
        == EXPECTED_RESIDENT_SOURCE_SHA256,
        "exact_200_unique_ids": len(game_ids) == EXPECTED_GAMES
        and len(set(game_ids)) == EXPECTED_GAMES,
        "all_named_raw_games_present": not missing_raw,
        "all_named_trajectories_present": not missing_trajectory,
        "all_200_games_decoded_and_audited": len(audited_rows) == EXPECTED_GAMES,
        "zero_decode_or_transition_errors": not errors,
        "cohort_support": cohort_integrity,
        "outside_game_ids_read": 0,
    }
    integrity_pass = all(
        value if isinstance(value, bool) else value == 0
        for value in integrity.values()
    )
    if not integrity_pass:
        verdict = "UNIDENTIFIABLE"
    elif summary and summary["materiality_pass"]:
        verdict = "MATERIAL_STRONG_COHORT_SIGNATURE"
    else:
        verdict = "NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE"
    return {
        "schema": "troll-farm-h7-action-contention-census-v1",
        "task_id": "20260731-h7-action-contention-census",
        "verdict": verdict,
        "frozen_inputs": {
            "manifest": {
                "path": (
                    "data/analysis/live-agent-6553250/"
                    "d159a-current-resident-all-finished-effect-refresh-raw.json"
                ),
                "sha256": manifest_hash,
            },
            "accepted_result": {
                "path": (
                    "data/analysis/live-agent-6553250/"
                    "d159a-current-resident-all-finished-effect-refresh-result.json"
                ),
                "sha256": accepted_hash,
            },
            "resident_source": {
                "path": (
                    "cgauto/submissions/"
                    "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
                ),
                "sha256": source_hash,
            },
            "data_root": "data",
            "game_ids": len(game_ids),
        },
        "integrity": {
            "gates": integrity,
            "pass": integrity_pass,
            "errors": errors[:100],
            "error_count": len(errors),
        },
        "summary": summary,
        "rows": audited_rows,
        "interpretation_limits": [
            "observed action contention cannot identify private strategic intent",
            "move target coordinates show race exposure, not terminal waste",
            "direct duplication ceiling is not banked score or causal margin",
            "no result authorizes a policy, candidate, or Arena action",
        ],
    }


def self_test() -> None:
    unit0 = {"id": 0, "hp": 1, "cc": 2, "carry": [0] * 6}
    unit1 = {"id": 1, "hp": 1, "cc": 2, "carry": [0] * 6}
    gains, remaining = harvest_awards(1, [(0, unit0), (1, unit1)])
    assert gains == {0: 1, 1: 1}
    assert remaining == 0
    wood, remaining_wood = wood_awards(1, [(0, unit0), (1, unit1)])
    assert wood == {0: 1, 1: 1}
    assert remaining_wood == -1
    mature = {
        "type": "PLUM",
        "size": 4,
        "health": 12,
        "fruits": 0,
        "cooldown": 0,
    }
    assert ticked_plant(mature)["fruits"] == 1
    print("self-test: ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode", nargs="?", choices=("run", "self-test"), default="run"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "d159a-current-resident-all-finished-effect-refresh-raw.json",
    )
    parser.add_argument(
        "--accepted-result",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "d159a-current-resident-all-finished-effect-refresh-result.json",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=REPO / "data",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode == "self-test":
        self_test()
        return
    result = run(
        manifest_path=args.manifest.resolve(),
        accepted_result_path=args.accepted_result.resolve(),
        data_root=args.data_root.resolve(),
    )
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
