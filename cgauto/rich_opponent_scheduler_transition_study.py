#!/usr/bin/env python3
"""Decode scheduler mechanisms in the 21 consumed rich-immediate arena opponents."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import battle_taxonomy as arena
from cgauto.field_continuation_coverage import archetype_key
from cgauto.field_economy_catalog_calibration import partition
from cgauto.recent_resident_field_census import (
    corpus_parser,
    decoded_states,
    inventory_after,
    side_snapshot,
    successful_events,
)
from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import analyze_players, assigned_unit_commands


REPO = Path(__file__).resolve().parent.parent
RICH_ARCHETYPE = "rich3plus:farm_wood:train_now"
PHASES = (
    ("001-050", 1, 50),
    ("051-100", 51, 100),
    ("101-150", 101, 150),
    ("151-200", 151, 200),
    ("201-250", 201, 250),
    ("251-300", 251, 300),
)
PRODUCTIVE_VERBS = {"HARVEST", "PLANT", "CHOP", "DROP", "PICK", "MINE"}
SNAPSHOT_FIELDS = (
    "score",
    "fruit",
    "wood",
    "workers",
    "successful_plants",
    "harvested_fruit",
    "chops_landed",
    "dropped_items",
)


def phase_name(turn: int) -> str:
    return next(name for name, start, end in PHASES if start <= turn <= end)


def affordable(inventory: list[int], cost: list[int], has_iron: bool) -> bool:
    indices = (0, 1, 2, 4) if has_iron else (0, 1, 2)
    return all(inventory[index] >= cost[index] for index in indices)


def useful_contributors(event: dict, has_iron: bool) -> list[int]:
    cost_items = {"PLUM", "LEMON", "APPLE"}
    if has_iron:
        cost_items.add("IRON")
    contributors = []
    for contributor in event["funding_contributors"]:
        dropped = contributor.get("dropped") or {}
        gained = contributor.get("material_gained") or {}
        if any(dropped.get(item, 0) > 0 or gained.get(item, 0) > 0 for item in cost_items):
            contributors.append(int(contributor["unit_id"]))
    return sorted(set(contributors))


def verified_training_events(
    analysis: dict, states: list[dict], player: int, has_iron: bool
) -> list[dict]:
    out = []
    previous_turn = 0
    for event in analysis["training_events"]:
        turn = int(event["turn"])
        cost = list(event["cost_vector"])
        first_affordable = None
        for state_index in range(previous_turn, turn):
            if affordable(states[state_index]["inventories"][player], cost, has_iron):
                first_affordable = state_index + 1
                break
        contributors = useful_contributors(event, has_iron)
        out.append(
            {
                "ordinal": int(event["ordinal"]),
                "turn": turn,
                "n_before": int(event["n_before"]),
                "new_unit_id": int(event["new_unit_id"]),
                "spec": list(event["spec"]),
                "cost": event["cost"],
                "starting_bank_funded": affordable(
                    list(event["funding_window_start_inventory"]), cost, has_iron
                ),
                "first_affordable_turn": first_affordable,
                "delay_after_affordable": (
                    turn - first_affordable if first_affordable is not None else None
                ),
                "useful_funding_contributors": contributors,
                "useful_funding_contributor_count": len(contributors),
            }
        )
        previous_turn = turn
    return out


def worker_scheduler(
    states: list[dict], trajectory: list[dict], player: int, workers: list[dict]
) -> dict:
    metadata = {int(worker["unit_id"]): worker for worker in workers}
    phase_actions: dict[int, dict[str, Counter]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    total_actions: dict[int, Counter] = defaultdict(Counter)
    transitions: dict[int, Counter] = defaultdict(Counter)
    last_productive = {}
    usable = min(len(states) - 1, len(trajectory))
    for turn in range(1, usable + 1):
        before_units = [
            unit for unit in states[turn - 1]["units"] if unit["player"] == player
        ]
        assigned = assigned_unit_commands(
            action_commands(trajectory[turn - 1].get(f"commands{player}")),
            before_units,
        )
        for unit_id, command in assigned.items():
            verb = command.split()[0].upper()
            phase_actions[unit_id][phase_name(turn)][verb] += 1
            total_actions[unit_id][verb] += 1
            if verb in PRODUCTIVE_VERBS:
                previous = last_productive.get(unit_id)
                if previous is not None:
                    transitions[unit_id][f"{previous}->{verb}"] += 1
                last_productive[unit_id] = verb

    rows = []
    aggregate_transitions = Counter()
    aggregate_phase = defaultdict(Counter)
    for unit_id, worker in sorted(
        metadata.items(), key=lambda item: (item[1]["ordinal"], item[0])
    ):
        actions = total_actions[unit_id]
        aggregate_transitions.update(transitions[unit_id])
        for phase, counts in phase_actions[unit_id].items():
            aggregate_phase[phase].update(counts)
        rows.append(
            {
                "unit_id": unit_id,
                "ordinal": int(worker["ordinal"]),
                "spawn_turn": int(worker["spawn_turn"]),
                "spec": list(worker["spec"]),
                "active_turns": int(worker["active_turns"]),
                "issued_actions": dict(sorted(actions.items())),
                "phase_actions": {
                    phase: dict(sorted(phase_actions[unit_id][phase].items()))
                    for phase, _, _ in PHASES
                },
                "transitions": dict(sorted(transitions[unit_id].items())),
                "multi_role": actions["HARVEST"] >= 3 and actions["CHOP"] >= 3,
            }
        )
    return {
        "workers": rows,
        "phase_actions": {
            phase: dict(sorted(aggregate_phase[phase].items()))
            for phase, _, _ in PHASES
        },
        "transitions": dict(sorted(aggregate_transitions.items())),
    }


def snapshots_and_intervals(
    trajectory: list[dict],
    final_inventory: tuple[list[int], list[int]],
    events: list[dict],
    player: int,
) -> tuple[dict, list[dict]]:
    final_turn = len(trajectory)
    cuts = [50, 100, 150, 200, 250, final_turn]
    cuts = sorted(set(min(cut, final_turn) for cut in cuts if min(cut, final_turn) > 0))
    snapshots = {}
    for cut in cuts:
        inventory = inventory_after(trajectory, final_inventory, player, cut)
        snapshots[str(cut)] = side_snapshot(inventory, events, cut)
    intervals = []
    previous_turn = 0
    previous = {
        "score": sum(trajectory[0][f"inv{player}"][:4])
        + 4 * trajectory[0][f"inv{player}"][5],
        "fruit": sum(trajectory[0][f"inv{player}"][:4]),
        "wood": trajectory[0][f"inv{player}"][5],
        "workers": 1,
        "successful_plants": 0,
        "harvested_fruit": 0,
        "chops_landed": 0,
        "dropped_items": 0,
    }
    for cut in cuts:
        current = snapshots[str(cut)]
        turns = cut - previous_turn
        increments = {field: current[field] - previous[field] for field in SNAPSHOT_FIELDS}
        intervals.append(
            {
                "start_turn": previous_turn + 1,
                "end_turn": cut,
                "turns": turns,
                "increments": increments,
                "per_turn": {
                    field: increments[field] / turns for field in SNAPSHOT_FIELDS
                },
            }
        )
        previous_turn = cut
        previous = current
    return snapshots, intervals


def final_signature(snapshot: dict) -> dict:
    return {field: snapshot[field] for field in SNAPSHOT_FIELDS}


def analyze_game(game: dict, record: dict) -> dict:
    game_id = int(record["game_id"])
    if int(game["gameId"]) != game_id:
        raise ValueError(f"fetched wrong game for {game_id}")
    player = 1 - int(record["candidate_arena_seat"])
    parser = corpus_parser()
    map_data, _trolls, inv0, inv1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, final_inventory = parser.extract_turns(game["frames"], inv0, inv1)
    decoded_map, states, unknown_updates = decoded_states(game, trajectory)
    if decoded_map["rows"] != map_data["rows"]:
        raise ValueError(f"map decode mismatch in game {game_id}")
    if len(states) - 1 != len(trajectory):
        raise ValueError(f"decoded/command turn mismatch in game {game_id}")
    if unknown_updates:
        raise ValueError(f"unknown replay diff updates in game {game_id}: {unknown_updates}")
    analyses = analyze_players(states, trajectory)
    analysis = analyses[player]
    training_events = verified_training_events(
        analysis, states, player, bool(map_data["iron"])
    )
    if len(analysis["workers"]) != 1 + len(training_events):
        raise ValueError(f"spawned worker/TRAIN mismatch in game {game_id}")
    scheduler = worker_scheduler(states, trajectory, player, analysis["workers"])
    events = successful_events(game["frames"])[player]
    snapshots, intervals = snapshots_and_intervals(
        trajectory, final_inventory, events, player
    )
    final = snapshots[str(len(trajectory))]
    expected = record["actual"]["final"]
    if final_signature(final) != final_signature(expected):
        raise ValueError(f"final signature mismatch in game {game_id}")
    transitions = Counter(scheduler["transitions"])
    workers = scheduler["workers"]
    later_events = [event for event in training_events if event["ordinal"] >= 2]
    third_worker_turn = next(
        (event["turn"] for event in training_events if event["ordinal"] == 2),
        301,
    )
    t100 = snapshots.get("100") or final
    return {
        "game_id": game_id,
        "partition": partition(game_id),
        "opponent": record["opponent"],
        "opponent_agent_id": record["opponent_agent_id"],
        "turns": len(trajectory),
        "has_iron": bool(map_data["iron"]),
        "training_events": training_events,
        "final_worker_count": len(workers),
        "third_worker_turn_or_301": third_worker_turn,
        "trained_workers": max(0, len(workers) - 1),
        "hybrid_trained_workers": sum(
            worker["ordinal"] > 0 and worker["spec"][2] > 0 and worker["spec"][3] > 0
            for worker in workers
        ),
        "active_50_workers": sum(worker["active_turns"] >= 50 for worker in workers),
        "multi_role_active_50_workers": sum(
            worker["active_turns"] >= 50 and worker["multi_role"] for worker in workers
        ),
        "later_training_events": len(later_events),
        "coordinated_later_training_events": sum(
            event["useful_funding_contributor_count"] >= 2 for event in later_events
        ),
        "has_harvest_to_plant": transitions["HARVEST->PLANT"] > 0,
        "has_chop_to_drop": transitions["CHOP->DROP"] > 0,
        "late_plant_share": (
            (final["successful_plants"] - t100["successful_plants"])
            / final["successful_plants"]
            if final["successful_plants"]
            else 0.0
        ),
        "late_wood_share": (
            (final["wood"] - t100["wood"]) / final["wood"]
            if final["wood"]
            else 0.0
        ),
        "scheduler": scheduler,
        "snapshots": snapshots,
        "intervals": intervals,
        "integrity": {
            "trajectory_turns": len(trajectory),
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": unknown_updates,
            "spawned_workers_matched": True,
            "final_signature_exact": True,
        },
    }


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def mean_counter(rows: list[dict], path: tuple[str, ...]) -> dict:
    total = Counter()
    for row in rows:
        value = row
        for key in path:
            value = value[key]
        total.update(value)
    return {key: value / len(rows) for key, value in sorted(total.items())}


def partition_summary(rows: list[dict]) -> dict:
    final_workers = [row["final_worker_count"] for row in rows]
    third_turns = [row["third_worker_turn_or_301"] for row in rows]
    later = sum(row["later_training_events"] for row in rows)
    coordinated = sum(row["coordinated_later_training_events"] for row in rows)
    trained = sum(row["trained_workers"] for row in rows)
    hybrids = sum(row["hybrid_trained_workers"] for row in rows)
    active = sum(row["active_50_workers"] for row in rows)
    multi = sum(row["multi_role_active_50_workers"] for row in rows)
    final_plants = sum(
        row["snapshots"][str(row["turns"])]["successful_plants"] for row in rows
    )
    late_plants = sum(
        row["snapshots"][str(row["turns"])]["successful_plants"]
        - (row["snapshots"].get("100") or row["snapshots"][str(row["turns"])])[
            "successful_plants"
        ]
        for row in rows
    )
    final_wood = sum(row["snapshots"][str(row["turns"])]["wood"] for row in rows)
    late_wood = sum(
        row["snapshots"][str(row["turns"])]["wood"]
        - (row["snapshots"].get("100") or row["snapshots"][str(row["turns"])])[
            "wood"
        ]
        for row in rows
    )
    specs_by_ordinal = defaultdict(Counter)
    training_turns_by_ordinal = defaultdict(list)
    phase_actions = defaultdict(Counter)
    transitions = Counter()
    for row in rows:
        for event in row["training_events"]:
            specs_by_ordinal[str(event["ordinal"])]["/".join(map(str, event["spec"]))] += 1
            training_turns_by_ordinal[str(event["ordinal"])].append(event["turn"])
        for phase, counts in row["scheduler"]["phase_actions"].items():
            phase_actions[phase].update(counts)
        transitions.update(row["scheduler"]["transitions"])
    metrics = {
        "front_loaded_scale": {
            "median_third_worker_turn_or_301": statistics.median(third_turns),
            "four_plus_games": sum(value >= 4 for value in final_workers),
            "four_plus_rate": ratio(sum(value >= 4 for value in final_workers), len(rows)),
        },
        "coordinated_later_funding": {
            "later_training_events": later,
            "coordinated_events": coordinated,
            "rate": ratio(coordinated, later),
        },
        "hybrid_workers": {
            "trained_workers": trained,
            "hybrid_trained_workers": hybrids,
            "hybrid_rate": ratio(hybrids, trained),
            "active_50_workers": active,
            "multi_role_active_50_workers": multi,
            "multi_role_rate": ratio(multi, active),
        },
        "late_renewable_loop": {
            "late_plant_share": ratio(late_plants, final_plants),
            "late_wood_share": ratio(late_wood, final_wood),
            "harvest_to_plant_games": sum(row["has_harvest_to_plant"] for row in rows),
            "harvest_to_plant_rate": ratio(
                sum(row["has_harvest_to_plant"] for row in rows), len(rows)
            ),
            "chop_to_drop_games": sum(row["has_chop_to_drop"] for row in rows),
            "chop_to_drop_rate": ratio(
                sum(row["has_chop_to_drop"] for row in rows), len(rows)
            ),
        },
    }
    checks = {
        "front_loaded_scale": (
            metrics["front_loaded_scale"]["median_third_worker_turn_or_301"] <= 100
            and metrics["front_loaded_scale"]["four_plus_rate"] is not None
            and metrics["front_loaded_scale"]["four_plus_rate"] >= 0.60
        ),
        "coordinated_later_funding": (
            metrics["coordinated_later_funding"]["rate"] is not None
            and metrics["coordinated_later_funding"]["rate"] >= 0.50
        ),
        "hybrid_workers": (
            metrics["hybrid_workers"]["hybrid_rate"] is not None
            and metrics["hybrid_workers"]["hybrid_rate"] >= 0.50
            and metrics["hybrid_workers"]["multi_role_rate"] is not None
            and metrics["hybrid_workers"]["multi_role_rate"] >= 0.40
        ),
        "late_renewable_loop": (
            metrics["late_renewable_loop"]["late_plant_share"] is not None
            and metrics["late_renewable_loop"]["late_plant_share"] >= 0.45
            and metrics["late_renewable_loop"]["late_wood_share"] is not None
            and metrics["late_renewable_loop"]["late_wood_share"] >= 0.45
            and metrics["late_renewable_loop"]["harvest_to_plant_rate"] is not None
            and metrics["late_renewable_loop"]["harvest_to_plant_rate"] >= 0.60
            and metrics["late_renewable_loop"]["chop_to_drop_rate"] is not None
            and metrics["late_renewable_loop"]["chop_to_drop_rate"] >= 0.60
        ),
    }
    return {
        "games": len(rows),
        "opponents": dict(sorted(Counter(row["opponent"] for row in rows).items())),
        "final_worker_distribution": dict(sorted(Counter(final_workers).items())),
        "training_specs_by_ordinal": {
            ordinal: dict(counts.most_common())
            for ordinal, counts in sorted(specs_by_ordinal.items())
        },
        "training_turns_by_ordinal": {
            ordinal: {
                "events": len(turns),
                "median": statistics.median(turns),
                "minimum": min(turns),
                "maximum": max(turns),
            }
            for ordinal, turns in sorted(training_turns_by_ordinal.items())
        },
        "mean_issued_actions_by_phase": {
            phase: {verb: count / len(rows) for verb, count in sorted(counts.items())}
            for phase, counts in sorted(phase_actions.items())
        },
        "mean_transition_counts": {
            transition: count / len(rows) for transition, count in sorted(transitions.items())
        },
        "mechanism_metrics": metrics,
        "mechanism_checks": checks,
    }


def analyze(rows: list[dict]) -> dict:
    if len(rows) != 21 or len({row["game_id"] for row in rows}) != 21:
        raise ValueError("expected exactly 21 unique rich-immediate games")
    grouped = {
        name: [row for row in rows if row["partition"] == name]
        for name in ("discovery", "confirmation")
    }
    if {name: len(values) for name, values in grouped.items()} != {
        "discovery": 12,
        "confirmation": 9,
    }:
        raise ValueError("unexpected frozen rich cohort split")
    summaries = {name: partition_summary(values) for name, values in grouped.items()}
    replicated = {
        mechanism: summaries["discovery"]["mechanism_checks"][mechanism]
        and summaries["confirmation"]["mechanism_checks"][mechanism]
        for mechanism in (
            "front_loaded_scale",
            "coordinated_later_funding",
            "hybrid_workers",
            "late_renewable_loop",
        )
    }
    return {
        "schema": 1,
        "scope": "observational consumed rich-opponent scheduler reconstruction",
        "games": 21,
        "integrity": {
            "unique_games": 21,
            "all_turn_streams_exact": all(
                row["integrity"]["trajectory_turns"]
                == row["integrity"]["decoded_turns"]
                for row in rows
            ),
            "unknown_diff_updates": sum(
                row["integrity"]["unknown_diff_updates"] for row in rows
            ),
            "all_spawned_workers_matched": all(
                row["integrity"]["spawned_workers_matched"] for row in rows
            ),
            "all_final_signatures_exact": all(
                row["integrity"]["final_signature_exact"] for row in rows
            ),
        },
        "partition_summaries": summaries,
        "replicated_mechanisms": replicated,
        "eligible_v2_mechanisms": [
            mechanism for mechanism, passed in replicated.items() if passed
        ],
        "rows": sorted(rows, key=lambda row: row["game_id"]),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def cohort_records(observed: dict, baseline: dict) -> list[dict]:
    baseline_by_game = {
        int(row["game_id"]): row for row in baseline.get("game_rows") or []
    }
    records = [
        record
        for record in observed.get("records") or []
        if not baseline_by_game[int(record["game_id"])]["fully_supported"]
        and archetype_key(record) == RICH_ARCHETYPE
    ]
    if len(records) != 21:
        raise ValueError(f"expected 21 rich records, got {len(records)}")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        raise SystemExit("--jobs must be between 1 and 32")
    records = cohort_records(
        json.loads(args.observed.read_text()), json.loads(args.baseline.read_text())
    )

    def fetch(record: dict) -> dict:
        game = arena.call("gameResult/findByGameId", [int(record["game_id"]), None])
        return analyze_game(game, record)

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        rows = list(executor.map(fetch, records))
    payload = analyze(rows)
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "integrity": payload["integrity"],
        "partition_summaries": payload["partition_summaries"],
        "replicated_mechanisms": payload["replicated_mechanisms"],
        "eligible_v2_mechanisms": payload["eligible_v2_mechanisms"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
