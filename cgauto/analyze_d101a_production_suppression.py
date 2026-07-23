#!/usr/bin/env python3
"""Reconstruct production/suppression role separation in the frozen D61p field snapshot."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import (  # noqa: E402
    load_open_inputs,
    read_jsonl,
    sha256_file,
)
from cgauto.analyze_d95a_rank_one_scaler import (  # noqa: E402
    MATERIAL_VERBS,
    cargo_delta,
    command_births,
    item_dict,
    reconstruct_actions,
    successful_action,
)
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    analyze_players,
    assigned_unit_commands,
    player_commands,
)


REPO = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = REPO / "data/raw/snapshots/20260721T105508Z-d61p"
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d101a-production-suppression-result.json"
)
PROTOCOL = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d101a-production-suppression-archaeology-protocol-2026-07-22.md"
)
HELPERS = (
    REPO / "cgauto/analyze_d95a_rank_one_scaler.py",
    REPO / "cgauto/recent_resident_field_census.py",
    REPO / "cgauto/top_player_opening_analysis.py",
)


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def mean(values) -> float | None:
    selected = list(values)
    return statistics.mean(selected) if selected else None


def median(values) -> float | None:
    selected = list(values)
    return statistics.median(selected) if selected else None


def origin_for_creator(creator: str, actor: int) -> str:
    if creator in {"ambiguous", "unknown"}:
        return creator
    return "actor" if int(creator) == actor else "opponent"


def generation_id(turn: int, cell: tuple[int, int]) -> str:
    return f"{turn}:{cell[0]}:{cell[1]}"


def explicit_plant_creator(
    before: dict,
    after: dict,
    trajectory_row: dict,
    cell: tuple[int, int],
) -> str:
    """Resolve births shadowed by an earlier positional WAIT in the legacy assigner."""

    before_units = {int(unit["id"]): unit for unit in before["units"]}
    after_plant = next(
        (
            plant
            for plant in after["plants"]
            if (int(plant["x"]), int(plant["y"])) == cell
        ),
        None,
    )
    creators = set()
    for player in (0, 1):
        for command in player_commands(trajectory_row, player):
            fields = command.split()
            if len(fields) < 3 or fields[0].upper() != "PLANT":
                continue
            try:
                unit = before_units.get(int(fields[1]))
            except ValueError:
                continue
            if (
                unit is not None
                and int(unit["player"]) == player
                and (int(unit["x"]), int(unit["y"])) == cell
                and after_plant is not None
                and fields[2].upper() == after_plant["type"]
            ):
                creators.add(player)
    if len(creators) == 1:
        return str(next(iter(creators)))
    return "ambiguous" if creators else "unknown"


def reconstruct_generation_actions(
    states: list[dict],
    trajectory: list[dict],
    actor: int,
    worker_ordinals: dict[int, int],
) -> tuple[list[dict], dict[str, dict], list[dict], dict]:
    """Return actor events plus generation-level crop lineage for every decoded state."""

    generations = {}
    active = {}
    for plant in states[0]["plants"]:
        cell = (int(plant["x"]), int(plant["y"]))
        identifier = generation_id(0, cell)
        active[cell] = identifier
        generations[identifier] = {
            "birth_turn": 0,
            "cell": list(cell),
            "kind": plant["type"],
            "origin": "natural",
        }
    lineage_by_state = [dict(active)]
    events = []
    quality = Counter()

    for turn in range(1, min(len(states) - 1, len(trajectory)) + 1):
        before = states[turn - 1]
        after = states[turn]
        before_units = {int(unit["id"]): unit for unit in before["units"]}
        after_units = {int(unit["id"]): unit for unit in after["units"]}
        assigned = {}
        for player in (0, 1):
            units = [unit for unit in before["units"] if int(unit["player"]) == player]
            assigned[player] = assigned_unit_commands(
                player_commands(trajectory[turn - 1], player), units
            )

        raw_births = command_births(before, after, assigned)
        before_plants = {
            (int(plant["x"]), int(plant["y"])): plant
            for plant in before["plants"]
        }
        after_plants = {
            (int(plant["x"]), int(plant["y"])): plant for plant in after["plants"]
        }
        new_cells = sorted(set(after_plants) - set(before_plants))
        new_generations = {}
        for cell in new_cells:
            creator = raw_births.get(cell, "unknown")
            if creator == "unknown":
                repaired = explicit_plant_creator(
                    before, after, trajectory[turn - 1], cell
                )
                if repaired != "unknown":
                    creator = repaired
                    quality["explicit_birth_repairs"] += 1
            origin = origin_for_creator(creator, actor)
            quality[f"{origin}_births"] += 1
            identifier = generation_id(turn, cell)
            new_generations[cell] = identifier
            generations[identifier] = {
                "birth_turn": turn,
                "cell": list(cell),
                "kind": after_plants[cell]["type"],
                "origin": origin,
            }

        actor_before_units = {
            unit_id: unit
            for unit_id, unit in before_units.items()
            if int(unit["player"]) == actor
        }
        for unit_id, unit in actor_before_units.items():
            after_unit = after_units.get(unit_id)
            gained, spent = cargo_delta(unit, after_unit)
            command = assigned[actor].get(unit_id)
            if command is None:
                if any(gained) or any(spent):
                    quality["unassigned_cargo_deltas"] += 1
                continue
            fields = command.split()
            verb = fields[0].upper() if fields else "WAIT"
            cell = (int(unit["x"]), int(unit["y"]))
            before_plant = before_plants.get(cell)
            after_plant = after_plants.get(cell)
            target_generation = active.get(cell) if before_plant else None
            target_origin = (
                generations[target_generation]["origin"]
                if target_generation is not None
                else None
            )
            created_generation = new_generations.get(cell)
            created_origin = (
                generations[created_generation]["origin"]
                if created_generation is not None
                else None
            )
            ordinal = worker_ordinals.get(unit_id)
            if ordinal is None:
                quality["missing_worker_ordinals"] += 1
                ordinal = -1
            success = successful_action(
                verb,
                unit,
                after_unit,
                before_plant,
                after_plant,
                gained,
                spent,
                created_origin,
            )
            events.append(
                {
                    "turn": turn,
                    "unit_id": unit_id,
                    "ordinal": int(ordinal),
                    "workforce": sum(
                        int(candidate["player"]) == actor
                        for candidate in before["units"]
                    ),
                    "verb": verb,
                    "success": success,
                    "target_kind": before_plant["type"] if before_plant else None,
                    "target_origin": target_origin,
                    "target_generation": target_generation,
                    "created_origin": created_origin,
                    "created_generation": created_generation,
                    "gained": item_dict(gained),
                    "spent": item_dict(spent),
                }
            )

        next_active = {}
        for cell in after_plants:
            if cell in before_plants:
                identifier = active.get(cell)
                if identifier is None:
                    quality["missing_live_generations"] += 1
                    identifier = generation_id(turn, cell)
                    generations[identifier] = {
                        "birth_turn": turn,
                        "cell": list(cell),
                        "kind": after_plants[cell]["type"],
                        "origin": "unknown",
                    }
                next_active[cell] = identifier
            else:
                next_active[cell] = new_generations[cell]
        active = next_active
        lineage_by_state.append(dict(active))

    return events, generations, lineage_by_state, dict(quality)


def event_projection(event: dict) -> dict:
    return {
        key: event[key]
        for key in (
            "turn",
            "unit_id",
            "ordinal",
            "workforce",
            "verb",
            "success",
            "target_kind",
            "target_origin",
            "created_origin",
            "gained",
            "spent",
        )
    }


def compatible_event(event: dict, reference: dict) -> bool:
    projected = event_projection(event)
    for key, value in projected.items():
        reference_value = reference[key]
        if key in {"target_origin", "created_origin"}:
            if reference_value == value:
                continue
            if reference_value == "unknown" and value in {"actor", "opponent"}:
                continue
            return False
        if reference_value != value:
            return False
    return True


def analyze_occurrence(task: dict, actor_id: int, metadata: dict) -> dict:
    game = task["game"]
    player_row = next(
        row for row in game["players"] if int(row.get("agentId", -1)) == actor_id
    )
    actor = int(player_row["index"])
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    _decoded_map, states, unknown = decoded_states(raw, trajectory)
    if len(states) - 1 != len(trajectory):
        raise ValueError(f"turn mismatch in {game['gameId']}")
    analyses = analyze_players(states, trajectory)
    analysis = analyses[actor]
    worker_ordinals = {
        int(worker["unit_id"]): int(worker["ordinal"])
        for worker in analysis["workers"]
    }
    events, generations, lineage_states, quality = reconstruct_generation_actions(
        states, trajectory, actor, worker_ordinals
    )
    reference_events, reference_lineage, reference_quality = reconstruct_actions(
        states, trajectory, actor, worker_ordinals
    )
    event_reference_parity = [event_projection(row) for row in events] == reference_events
    event_reference_compatible = len(events) == len(reference_events) and all(
        compatible_event(event, reference)
        for event, reference in zip(events, reference_events)
    )
    lineage_origins = [
        {
            cell: generations[identifier]["origin"]
            for cell, identifier in generation.items()
        }
        for generation in lineage_states
    ]
    lineage_reference_parity = lineage_origins == reference_lineage
    lineage_reference_compatible = len(lineage_origins) == len(reference_lineage) and all(
        set(generation) == set(reference)
        and all(
            reference[cell] == origin
            or (reference[cell] == "unknown" and origin in {"actor", "opponent"})
            for cell, origin in generation.items()
        )
        for generation, reference in zip(lineage_origins, reference_lineage)
    )

    successful = [
        event
        for event in events
        if event["success"] and event["verb"] in MATERIAL_VERBS
    ]
    plants = [
        event
        for event in successful
        if event["verb"] == "PLANT" and event["created_origin"] == "actor"
    ]
    own_harvests = [
        event
        for event in successful
        if event["verb"] == "HARVEST" and event["target_origin"] == "actor"
    ]
    opponent_chops = [
        event
        for event in successful
        if event["verb"] == "CHOP" and event["target_origin"] == "opponent"
    ]
    own_created = {event["created_generation"] for event in plants}
    own_reaped = {event["target_generation"] for event in own_harvests}
    opponent_created = {
        identifier
        for identifier, row in generations.items()
        if row["origin"] == "opponent"
    }
    opponent_contacted = {event["target_generation"] for event in opponent_chops}
    first_contact = {}
    for event in opponent_chops:
        identifier = event["target_generation"]
        first_contact[identifier] = min(event["turn"], first_contact.get(identifier, 10**9))
    contact_latencies = [
        first_contact[identifier] - int(generations[identifier]["birth_turn"])
        for identifier in sorted(first_contact)
    ]

    planted_workers = {event["ordinal"] for event in plants}
    reaping_workers = {event["ordinal"] for event in own_harvests}
    own_loop_workers = planted_workers | reaping_workers
    strict_producer_workers = planted_workers & reaping_workers
    suppression_workers = {event["ordinal"] for event in opponent_chops}
    final_workers = len(analysis["workers"])
    role_pairs = sorted(
        f"{producer}->{suppressor}"
        for producer in own_loop_workers
        for suppressor in suppression_workers
        if producer != suppressor
    )
    strict_role_pairs = sorted(
        f"{producer}->{suppressor}"
        for producer in strict_producer_workers
        for suppressor in suppression_workers
        if producer != suppressor
    )
    first_plant_turn = min((event["turn"] for event in plants), default=None)
    last_own_harvest_turn = max(
        (event["turn"] for event in own_harvests), default=None
    )
    temporally_overlapped = bool(
        first_plant_turn is not None
        and last_own_harvest_turn is not None
        and any(
            first_plant_turn <= event["turn"] <= last_own_harvest_turn
            for event in opponent_chops
        )
    )
    indicators = {
        "own_creation": bool(plants),
        "own_reaping": bool(own_harvests),
        "opponent_suppression": bool(opponent_chops),
        "creation_and_suppression": bool(plants and opponent_chops),
        "renewal_and_suppression": bool(own_harvests and opponent_chops),
        "role_separated": bool(final_workers >= 2 and role_pairs),
        "strict_role_separated": bool(final_workers >= 2 and strict_role_pairs),
        "temporally_overlapped": temporally_overlapped,
    }
    successful_by_verb_origin = Counter(
        f"{event['verb']}:{event['target_origin'] or event['created_origin'] or 'none'}"
        for event in successful
    )
    own_loop_by_ordinal = Counter(
        event["ordinal"] for event in plants + own_harvests
    )
    suppression_by_ordinal = Counter(event["ordinal"] for event in opponent_chops)
    suppression_by_workforce = Counter(event["workforce"] for event in opponent_chops)
    training_count = len(analysis["training_events"])
    return {
        "game_id": int(game["gameId"]),
        "split": game["split"],
        "agent_id": actor_id,
        "agent": metadata["pseudo"],
        "source_rank": metadata.get("source_rank"),
        "cohort": metadata["cohort"],
        "seat": actor,
        "turns": len(trajectory),
        "score": int(game["scores"][actor]),
        "opponent_score": int(game["scores"][1 - actor]),
        "margin": int(game["scores"][actor]) - int(game["scores"][1 - actor]),
        "won": int(game["scores"][actor]) > int(game["scores"][1 - actor]),
        "final_workers": final_workers,
        "successful_trains": training_count,
        "indicators": indicators,
        "crop_generations": {
            "actor_created": len(own_created),
            "actor_created_reaped": len(own_created & own_reaped),
            "opponent_created": len(opponent_created),
            "opponent_contacted": len(opponent_contacted),
            "opponent_contact_coverage": ratio(
                len(opponent_contacted), len(opponent_created)
            ),
            "first_contact_latencies": contact_latencies,
        },
        "actions": {
            "successful_material": len(successful),
            "successful_by_verb_origin": dict(sorted(successful_by_verb_origin.items())),
            "own_loop_by_ordinal": {
                str(key): value for key, value in sorted(own_loop_by_ordinal.items())
            },
            "suppression_by_ordinal": {
                str(key): value for key, value in sorted(suppression_by_ordinal.items())
            },
            "suppression_by_workforce": {
                str(key): value for key, value in sorted(suppression_by_workforce.items())
            },
            "role_pairs": role_pairs,
            "strict_role_pairs": strict_role_pairs,
            "first_plant_turn": first_plant_turn,
            "last_own_harvest_turn": last_own_harvest_turn,
        },
        "integrity": {
            "trajectory_turns": len(trajectory),
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": unknown,
            "workers": final_workers,
            "successful_trains": training_count,
            "unknown_births": quality.get("unknown_births", 0),
            "ambiguous_births": quality.get("ambiguous_births", 0),
            "explicit_birth_repairs": quality.get("explicit_birth_repairs", 0),
            "missing_live_generations": quality.get("missing_live_generations", 0),
            "missing_worker_ordinals": quality.get("missing_worker_ordinals", 0),
            "unassigned_cargo_deltas": quality.get("unassigned_cargo_deltas", 0),
            "reference_unknown_births": reference_quality["unknown_births"],
            "reference_unassigned_cargo_deltas": reference_quality[
                "unassigned_cargo_deltas"
            ],
            "event_reference_parity": event_reference_parity,
            "event_reference_compatible": event_reference_compatible,
            "lineage_reference_parity": lineage_reference_parity,
            "lineage_reference_compatible": lineage_reference_compatible,
        },
    }


INDICATORS = (
    "own_creation",
    "own_reaping",
    "opponent_suppression",
    "creation_and_suppression",
    "renewal_and_suppression",
    "role_separated",
    "strict_role_separated",
    "temporally_overlapped",
)


def summarize_rows(rows: list[dict]) -> dict:
    multiworker = [row for row in rows if row["final_workers"] >= 2]
    counts = {
        indicator: sum(row["indicators"][indicator] for row in rows)
        for indicator in INDICATORS
    }
    rates = {
        indicator: ratio(
            counts[indicator],
            len(multiworker) if indicator in {"role_separated", "strict_role_separated"} else len(rows),
        )
        for indicator in INDICATORS
    }
    own_loop_ordinals = Counter()
    suppression_ordinals = Counter()
    suppression_workforces = Counter()
    role_pairs = Counter()
    strict_role_pairs = Counter()
    successful_material = Counter()
    latencies = []
    for row in rows:
        own_loop_ordinals.update(row["actions"]["own_loop_by_ordinal"])
        suppression_ordinals.update(row["actions"]["suppression_by_ordinal"])
        suppression_workforces.update(row["actions"]["suppression_by_workforce"])
        role_pairs.update(row["actions"]["role_pairs"])
        strict_role_pairs.update(row["actions"]["strict_role_pairs"])
        successful_material.update(row["actions"]["successful_by_verb_origin"])
        latencies.extend(row["crop_generations"]["first_contact_latencies"])
    actor_created = sum(
        row["crop_generations"]["actor_created"] for row in rows
    )
    actor_created_reaped = sum(
        row["crop_generations"]["actor_created_reaped"] for row in rows
    )
    indicator_outcomes = {}
    for indicator in INDICATORS:
        selected = [row for row in rows if row["indicators"][indicator]]
        unselected = [row for row in rows if not row["indicators"][indicator]]
        selected_mean = mean(row["margin"] for row in selected)
        unselected_mean = mean(row["margin"] for row in unselected)
        indicator_outcomes[indicator] = {
            "true_games": len(selected),
            "false_games": len(unselected),
            "true_mean_margin": selected_mean,
            "false_mean_margin": unselected_mean,
            "descriptive_margin_difference": (
                selected_mean - unselected_mean
                if selected_mean is not None and unselected_mean is not None
                else None
            ),
        }
    opponent_created = sum(
        row["crop_generations"]["opponent_created"] for row in rows
    )
    opponent_contacted = sum(
        row["crop_generations"]["opponent_contacted"] for row in rows
    )
    return {
        "games": len(rows),
        "multiworker_games": len(multiworker),
        "wins": sum(row["won"] for row in rows),
        "win_rate": ratio(sum(row["won"] for row in rows), len(rows)),
        "mean_margin": mean(row["margin"] for row in rows),
        "mean_final_workers": mean(row["final_workers"] for row in rows),
        "indicator_counts": counts,
        "indicator_rates": rates,
        "actor_generations": {
            "created": actor_created,
            "created_reaped": actor_created_reaped,
            "pooled_reaped_coverage": ratio(actor_created_reaped, actor_created),
        },
        "opponent_generations": {
            "created": opponent_created,
            "contacted": opponent_contacted,
            "pooled_contact_coverage": ratio(opponent_contacted, opponent_created),
            "first_contact_count": len(latencies),
            "first_contact_mean_latency": mean(latencies),
            "first_contact_median_latency": median(latencies),
        },
        "successful_material_actions": dict(sorted(successful_material.items())),
        "own_loop_action_count_by_ordinal": dict(sorted(own_loop_ordinals.items())),
        "suppression_action_count_by_ordinal": dict(sorted(suppression_ordinals.items())),
        "suppression_action_count_by_workforce": dict(
            sorted(suppression_workforces.items())
        ),
        "role_pair_game_counts": dict(sorted(role_pairs.items())),
        "strict_role_pair_game_counts": dict(sorted(strict_role_pairs.items())),
        "indicator_outcomes_descriptive_only": indicator_outcomes,
    }


def analyze(rows: list[dict], top_targets: dict[int, dict], input_hashes: dict) -> dict:
    rows = sorted(rows, key=lambda row: (row["agent_id"], row["game_id"], row["seat"]))
    top_rows = [row for row in rows if row["cohort"] in {"rank_1_5", "rank_6_20"}]
    top_five = [row for row in rows if row["cohort"] == "rank_1_5"]
    top_three = [
        row
        for row in top_five
        if top_targets[row["agent_id"]]["source_rank"] <= 3
    ]
    rank_four_five = [
        row
        for row in top_five
        if top_targets[row["agent_id"]]["source_rank"] >= 4
    ]
    reference = [row for row in rows if row["cohort"] == "rank_6_20"]
    resident = [row for row in rows if row["cohort"] == "resident"]
    per_agent = {}
    support = {}
    for agent_id, metadata in sorted(
        top_targets.items(), key=lambda item: item[1]["source_rank"]
    ):
        selected = [row for row in top_rows if row["agent_id"] == agent_id]
        summary = summarize_rows(selected)
        per_agent[str(agent_id)] = {
            "agent": metadata["pseudo"],
            "source_rank": metadata["source_rank"],
            **summary,
        }
        if metadata["source_rank"] <= 5:
            rates = summary["indicator_rates"]
            conditions = {
                "own_creation_at_least_0.80": rates["own_creation"] >= 0.80,
                "opponent_suppression_at_least_0.50": rates[
                    "opponent_suppression"
                ]
                >= 0.50,
                "creation_and_suppression_at_least_0.40": rates[
                    "creation_and_suppression"
                ]
                >= 0.40,
                "role_separated_multiworker_at_least_0.30": (
                    rates["role_separated"] is not None
                    and rates["role_separated"] >= 0.30
                ),
            }
            support[str(agent_id)] = {
                "agent": metadata["pseudo"],
                "source_rank": metadata["source_rank"],
                "conditions": conditions,
                "supports_architecture": all(conditions.values()),
            }

    top_counts = Counter(row["agent_id"] for row in top_rows)
    unique_occurrences = {(row["game_id"], row["agent_id"]) for row in rows}
    integrity = {
        "exact_365_occurrences": len(rows) == 365,
        "exact_200_top20_occurrences": len(top_rows) == 200,
        "exact_ten_per_top20_agent": top_counts
        == Counter({agent_id: 10 for agent_id in top_targets}),
        "exact_50_top5_occurrences": len(top_five) == 50,
        "exact_150_rank6_20_occurrences": len(reference) == 150,
        "exact_165_resident_occurrences": len(resident) == 165,
        "all_occurrences_unique": len(unique_occurrences) == len(rows),
        "no_confirmation_rows": all(row["split"] != "confirmation" for row in rows),
        "all_turn_streams_exact": all(
            row["integrity"]["trajectory_turns"]
            == row["integrity"]["decoded_turns"]
            for row in rows
        ),
        "zero_unknown_diff_updates": all(
            row["integrity"]["unknown_diff_updates"] == 0 for row in rows
        ),
        "zero_unknown_or_ambiguous_births": all(
            row["integrity"]["unknown_births"] == 0
            and row["integrity"]["ambiguous_births"] == 0
            for row in rows
        ),
        "legacy_unknown_births_exactly_repaired_from_explicit_commands": all(
            row["integrity"]["reference_unknown_births"]
            == row["integrity"]["explicit_birth_repairs"]
            for row in rows
        ),
        "zero_missing_lineage_or_worker_ordinals": all(
            row["integrity"]["missing_live_generations"] == 0
            and row["integrity"]["missing_worker_ordinals"] == 0
            for row in rows
        ),
        "zero_unassigned_cargo_deltas": all(
            row["integrity"]["unassigned_cargo_deltas"] == 0
            and row["integrity"]["reference_unassigned_cargo_deltas"] == 0
            for row in rows
        ),
        "spawn_train_exact": all(
            row["integrity"]["workers"]
            == 1 + row["integrity"]["successful_trains"]
            for row in rows
        ),
        "independent_event_reconstruction_compatible": all(
            row["integrity"]["event_reference_compatible"] for row in rows
        ),
        "independent_lineage_reconstruction_compatible": all(
            row["integrity"]["lineage_reference_compatible"] for row in rows
        ),
    }
    supporting_agents = sum(row["supports_architecture"] for row in support.values())
    mechanism = {
        "per_top5_agent": support,
        "supporting_agent_count": supporting_agents,
        "required_supporting_agent_count": 3,
        "architecture_warrant": supporting_agents >= 3,
    }
    return {
        "schema": 1,
        "scope": "frozen open D61p production/suppression role archaeology",
        "input_hashes": input_hashes,
        "integrity": integrity,
        "intrinsic_integrity_pass": all(integrity.values()),
        "parallel_reproduction": "assessed externally by byte comparison of 1- and 20-process outputs",
        "mechanism": mechanism,
        "cohort_summaries": {
            "rank_1_3": summarize_rows(top_three),
            "rank_4_5": summarize_rows(rank_four_five),
            "rank_1_5": summarize_rows(top_five),
            "rank_6_20": summarize_rows(reference),
            "resident": summarize_rows(resident),
        },
        "top20_agent_summaries": per_agent,
        "rows": rows,
    }


def atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(payload, stream, indent=1, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    args = parser.parse_args()

    inputs = load_open_inputs(args.snapshot)
    players = json.loads((Path(args.snapshot).resolve() / "players.json").read_text())
    top_targets = {
        int(row["agent_id"]): {
            "pseudo": row["pseudo"],
            "source_rank": int(row["source_rank"]),
        }
        for row in players
        if "legend_top20" in (row.get("groups") or [])
    }
    resident_id = int(inputs["resident_agent_id"])
    resident_row = next(row for row in players if int(row["agent_id"]) == resident_id)
    metadata = {
        agent_id: {
            **row,
            "cohort": "rank_1_5" if row["source_rank"] <= 5 else "rank_6_20",
        }
        for agent_id, row in top_targets.items()
    }
    metadata[resident_id] = {
        "pseudo": resident_row["pseudo"],
        "source_rank": int(resident_row["source_rank"]),
        "cohort": "resident",
    }

    occurrences = []
    for task in inputs["tasks"]:
        present = {int(row.get("agentId", -1)) for row in task["game"]["players"]}
        for agent_id in sorted(set(task["top_source_ids"]) & present):
            occurrences.append((task, agent_id, metadata[agent_id]))
        if resident_id in present:
            occurrences.append((task, resident_id, metadata[resident_id]))
    occurrences.sort(key=lambda item: (item[1], int(item[0]["game"]["gameId"])))

    if args.jobs <= 1:
        rows = [analyze_occurrence(*occurrence) for occurrence in occurrences]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            rows = list(
                executor.map(
                    analyze_occurrence,
                    (task for task, _, _ in occurrences),
                    (agent_id for _, agent_id, _ in occurrences),
                    (row for _, _, row in occurrences),
                )
            )

    input_hashes = {
        **{f"d61_{key}": value for key, value in inputs["input_hashes"].items()},
        "d101_protocol": sha256_file(PROTOCOL),
        "d101_analyzer": sha256_file(Path(__file__)),
        **{
            f"helper_{path.name}": sha256_file(path)
            for path in HELPERS
        },
    }
    result = analyze(rows, top_targets, input_hashes)
    atomic_write(args.output, result)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "occurrences": len(rows),
                "intrinsic_integrity_pass": result["intrinsic_integrity_pass"],
                "mechanism": result["mechanism"],
                "cohort_indicator_rates": {
                    cohort: summary["indicator_rates"]
                    for cohort, summary in result["cohort_summaries"].items()
                },
            },
            indent=1,
            sort_keys=True,
        )
    )
    return 0 if result["intrinsic_integrity_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
