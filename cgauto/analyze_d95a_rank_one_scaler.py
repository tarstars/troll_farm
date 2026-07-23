#!/usr/bin/env python3
"""Reconstruct the concurrent two-worker foundation of current strong scalers.

This analyzer consumes only manifest-verified open D61p replay products.  It deliberately
separates the rank-one scheduler from the older experiment that merely attached a hybrid worker
to Yamo's continuation.
"""

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
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402
from cgauto.rich_opponent_scheduler_transition_study import (  # noqa: E402
    useful_contributors,
)
from cgauto.top_player_opening_analysis import (  # noqa: E402
    ITEMS,
    analyze_players,
    assigned_unit_commands,
    player_commands,
)


REPO = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = REPO / "data/raw/snapshots/20260721T105508Z-d61p"
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d95a-rank-one-concurrent-scaler-result.json"
)
PROTOCOL = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d95a-rank-one-concurrent-scaler-archaeology-protocol-2026-07-21.md"
)
TARGETS = {
    6479768: {"name": "delineate", "role": "rank_one"},
    6480540: {"name": "norxondor_gorgonax", "role": "reference"},
    6481141: {"name": "wala", "role": "reference"},
}
ITEM_INDEX = {name: index for index, name in enumerate(ITEMS)}
FRUIT_ITEMS = set(ITEMS[:4])
MATERIAL_VERBS = {"HARVEST", "PLANT", "CHOP", "PICK", "MINE", "DROP"}
ORIGINS = ("natural", "actor", "opponent", "ambiguous", "unknown")


def item_dict(values) -> dict[str, int]:
    return {name: int(values[index]) for index, name in enumerate(ITEMS)}


def add_items(target: Counter, values) -> None:
    for index, value in enumerate(values):
        if value:
            target[ITEMS[index]] += int(value)


def mean(values) -> float | None:
    selected = list(values)
    return statistics.mean(selected) if selected else None


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def cargo_delta(before: dict, after: dict | None) -> tuple[list[int], list[int]]:
    after_carry = after["carry"] if after is not None else [0] * len(ITEMS)
    gained = [
        max(0, int(after_carry[index]) - int(before["carry"][index]))
        for index in range(len(ITEMS))
    ]
    spent = [
        max(0, int(before["carry"][index]) - int(after_carry[index]))
        for index in range(len(ITEMS))
    ]
    return gained, spent


def command_births(
    before: dict,
    after: dict,
    assigned: dict[int, dict[int, str]],
) -> dict[tuple[int, int], str]:
    before_plants = {(plant["x"], plant["y"]): plant for plant in before["plants"]}
    after_plants = {(plant["x"], plant["y"]): plant for plant in after["plants"]}
    before_units = {unit["id"]: unit for unit in before["units"]}
    result = {}
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
        creators = sorted(set(creators))
        if len(creators) == 1:
            result[cell] = str(creators[0])
        elif creators:
            result[cell] = "ambiguous"
        else:
            result[cell] = "unknown"
    return result


def successful_action(
    verb: str,
    before_unit: dict,
    after_unit: dict | None,
    before_plant: dict | None,
    after_plant: dict | None,
    gained: list[int],
    spent: list[int],
    birth_origin: str | None,
) -> bool:
    if verb == "MOVE":
        return bool(
            after_unit
            and (after_unit["x"], after_unit["y"])
            != (before_unit["x"], before_unit["y"])
        )
    if verb == "HARVEST":
        return any(gained[index] > 0 for index in range(4))
    if verb == "PLANT":
        return birth_origin is not None
    if verb == "CHOP":
        return bool(
            before_plant
            and (
                after_plant is None
                or int(after_plant["health"]) < int(before_plant["health"])
            )
        )
    if verb == "PICK":
        return any(gained)
    if verb == "MINE":
        return gained[ITEM_INDEX["IRON"]] > 0
    if verb == "DROP":
        return any(spent)
    return False


def reconstruct_actions(
    states: list[dict],
    trajectory: list[dict],
    actor: int,
    worker_ordinals: dict[int, int],
) -> tuple[list[dict], list[dict], dict]:
    """Return actor unit actions and the live crop-origin map at every state."""

    active = {
        (plant["x"], plant["y"]): "natural" for plant in states[0]["plants"]
    }
    lineage_by_state = [dict(active)]
    events = []
    unassigned_cargo_deltas = 0
    unknown_births = 0

    for turn in range(1, min(len(states) - 1, len(trajectory)) + 1):
        before = states[turn - 1]
        after = states[turn]
        before_units = {unit["id"]: unit for unit in before["units"]}
        after_units = {unit["id"]: unit for unit in after["units"]}
        assigned = {}
        for player in (0, 1):
            units = [unit for unit in before["units"] if unit["player"] == player]
            assigned[player] = assigned_unit_commands(
                player_commands(trajectory[turn - 1], player), units
            )
        births = command_births(before, after, assigned)
        birth_categories = {}
        for cell, creator in births.items():
            if creator == "ambiguous":
                birth_categories[cell] = "ambiguous"
            elif creator == "unknown":
                birth_categories[cell] = "unknown"
                unknown_births += 1
            elif int(creator) == actor:
                birth_categories[cell] = "actor"
            else:
                birth_categories[cell] = "opponent"

        before_plants = {(plant["x"], plant["y"]): plant for plant in before["plants"]}
        after_plants = {(plant["x"], plant["y"]): plant for plant in after["plants"]}
        actor_before_units = {
            unit_id: unit
            for unit_id, unit in before_units.items()
            if unit["player"] == actor
        }
        for unit_id, unit in actor_before_units.items():
            after_unit = after_units.get(unit_id)
            gained, spent = cargo_delta(unit, after_unit)
            command = assigned[actor].get(unit_id)
            if command is None:
                if any(gained) or any(spent):
                    unassigned_cargo_deltas += 1
                continue
            fields = command.split()
            verb = fields[0].upper() if fields else "WAIT"
            cell = (unit["x"], unit["y"])
            before_plant = before_plants.get(cell)
            after_plant = after_plants.get(cell)
            target_kind = before_plant["type"] if before_plant else None
            target_origin = active.get(cell) if before_plant else None
            created_origin = birth_categories.get(cell)
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
                    "unit_id": int(unit_id),
                    "ordinal": int(worker_ordinals[unit_id]),
                    "workforce": sum(
                        candidate["player"] == actor for candidate in before["units"]
                    ),
                    "verb": verb,
                    "success": success,
                    "target_kind": target_kind,
                    "target_origin": target_origin,
                    "created_origin": created_origin,
                    "gained": item_dict(gained),
                    "spent": item_dict(spent),
                }
            )

        next_active = {}
        for cell in after_plants:
            if cell in before_plants:
                next_active[cell] = active.get(cell, "unknown")
            else:
                next_active[cell] = birth_categories.get(cell, "unknown")
        active = next_active
        lineage_by_state.append(dict(active))

    return events, lineage_by_state, {
        "unassigned_cargo_deltas": unassigned_cargo_deltas,
        "unknown_births": unknown_births,
    }


def material_transitions(events: list[dict]) -> Counter:
    result = Counter()
    previous = {}
    for event in sorted(events, key=lambda row: (row["turn"], row["unit_id"])):
        if not event["success"] or event["verb"] not in MATERIAL_VERBS:
            continue
        unit_id = event["unit_id"]
        if unit_id in previous:
            result[f"{previous[unit_id]}->{event['verb']}"] += 1
        previous[unit_id] = event["verb"]
    return result


def summarize_worker_events(events: list[dict]) -> dict:
    issued = Counter(event["verb"] for event in events)
    successful = Counter(event["verb"] for event in events if event["success"])
    gained = Counter()
    spent = Counter()
    harvest_by_origin = Counter()
    harvest_by_kind = Counter()
    domains = set()
    for event in events:
        if not event["success"]:
            continue
        add_items(gained, [event["gained"][name] for name in ITEMS])
        add_items(spent, [event["spent"][name] for name in ITEMS])
        if event["verb"] in {"HARVEST", "PLANT"}:
            domains.add("fruit")
        elif event["verb"] == "MINE":
            domains.add("mine")
        elif event["verb"] == "CHOP":
            domains.add("wood")
        if event["verb"] == "HARVEST":
            amount = sum(event["gained"][item] for item in FRUIT_ITEMS)
            harvest_by_origin[event["target_origin"] or "unknown"] += amount
            if event["target_kind"]:
                harvest_by_kind[event["target_kind"]] += amount
    transitions = material_transitions(events)
    return {
        "turns_with_commands": len({event["turn"] for event in events}),
        "issued": dict(sorted(issued.items())),
        "successful": dict(sorted(successful.items())),
        "gained": dict(sorted(gained.items())),
        "spent": dict(sorted(spent.items())),
        "harvest_by_origin": dict(sorted(harvest_by_origin.items())),
        "harvest_by_kind": dict(sorted(harvest_by_kind.items())),
        "domains": sorted(domains),
        "transitions": dict(sorted(transitions.items())),
    }


def summarize_phase(events: list[dict]) -> dict:
    by_worker = defaultdict(list)
    for event in events:
        by_worker[event["ordinal"]].append(event)
    return {
        "workers": {
            str(ordinal): summarize_worker_events(rows)
            for ordinal, rows in sorted(by_worker.items())
        },
        "transitions": dict(sorted(material_transitions(events).items())),
    }


def crop_portfolio(
    state: dict, lineage: dict[tuple[int, int], str]
) -> dict[str, dict[str, dict[str, int]]]:
    result = {
        origin: {
            kind: {"plants": 0, "ripe_plants": 0, "fruits": 0}
            for kind in ITEMS[:4]
        }
        for origin in ORIGINS
    }
    for plant in state["plants"]:
        origin = lineage.get((plant["x"], plant["y"]), "unknown")
        kind = plant["type"]
        row = result[origin][kind]
        row["plants"] += 1
        row["ripe_plants"] += int(plant["fruits"] > 0)
        row["fruits"] += int(plant["fruits"])
    return result


def simplify_training_event(event: dict, has_iron: bool) -> dict:
    useful = set(useful_contributors(event, has_iron))
    contributors = []
    for row in event["funding_contributors"]:
        contributors.append(
            {
                "unit_id": int(row["unit_id"]),
                "ordinal": row["ordinal"],
                "role": row["role"],
                "spec": row["spec"],
                "useful": int(row["unit_id"]) in useful,
                "dropped": row["dropped"],
                "material_gained": row["material_gained"],
                "commands": row["commands"],
            }
        )
    return {
        "ordinal": int(event["ordinal"]),
        "turn": int(event["turn"]),
        "n_before": int(event["n_before"]),
        "new_unit_id": int(event["new_unit_id"]),
        "spec": list(event["spec"]),
        "role": event["role"],
        "cost": event["cost"],
        "starting_bank_funded": bool(event["starting_bank_funded"]),
        "first_affordable_turn": event["first_affordable_turn"],
        "delay_after_affordable": event["delay_after_affordable"],
        "useful_contributor_count": len(useful),
        "useful_contributor_ordinals": sorted(
            row["ordinal"] for row in contributors if row["useful"]
        ),
        "contributors": contributors,
    }


def analyze_occurrence(task: dict, actor_id: int) -> dict:
    game = task["game"]
    player_row = next(
        row for row in game["players"] if int(row.get("agentId", -1)) == actor_id
    )
    actor = int(player_row["index"])
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    _map, states, unknown = decoded_states(raw, trajectory)
    if len(states) - 1 != len(trajectory):
        raise ValueError(f"turn mismatch in {game['gameId']}")
    analyses = analyze_players(states, trajectory)
    analysis = analyses[actor]
    worker_ordinals = {
        int(worker["unit_id"]): int(worker["ordinal"])
        for worker in analysis["workers"]
    }
    events, lineage_by_state, lineage_quality = reconstruct_actions(
        states, trajectory, actor, worker_ordinals
    )
    training_events = [
        simplify_training_event(event, bool(game["map"]["iron"]))
        for event in analysis["training_events"]
    ]
    if not training_events:
        raise ValueError(f"selected actor has no TRAIN in {game['gameId']}")

    first_turn = training_events[0]["turn"]
    third_turn = next(
        (event["turn"] for event in training_events if event["ordinal"] == 2),
        None,
    )
    pair_end = third_turn if third_turn is not None else len(trajectory)
    pair_events = [
        event for event in events if first_turn < event["turn"] <= pair_end
    ]
    anchor = first_turn + 40
    if anchor >= len(states):
        raise ValueError(f"pair-age-40 is censored in {game['gameId']}")
    age40_events = [
        event for event in events if first_turn < event["turn"] <= anchor
    ]
    anchor_state = states[anchor]
    portfolio = crop_portfolio(anchor_state, lineage_by_state[anchor])
    later_events = [event for event in events if event["ordinal"] >= 2]
    later_successes = Counter(
        event["verb"]
        for event in later_events
        if event["success"] and event["verb"] in MATERIAL_VERBS
    )
    later_total = sum(later_successes.values())

    pair_summary = summarize_phase(pair_events)
    first_trained = pair_summary["workers"].get("1", {})
    pair_transitions = Counter(pair_summary["transitions"])
    scaler = third_turn is not None
    return {
        "game_id": int(game["gameId"]),
        "agent_id": actor_id,
        "agent": TARGETS[actor_id]["name"],
        "agent_role": TARGETS[actor_id]["role"],
        "seat": actor,
        "turns": len(trajectory),
        "score": int(game["scores"][actor]),
        "opponent_score": int(game["scores"][1 - actor]),
        "margin": int(game["scores"][actor]) - int(game["scores"][1 - actor]),
        "final_workers": len(analysis["workers"]),
        "scaler": scaler,
        "training_events": training_events,
        "pair_foundation": {
            "start_turn": first_turn,
            "end_turn": pair_end,
            "turns": pair_end - first_turn,
            **pair_summary,
            "renewable": pair_transitions["HARVEST->PLANT"] > 0,
            "capitalization": (
                pair_transitions["MINE->DROP"] > 0
                or pair_transitions["CHOP->DROP"] > 0
            ),
            "first_trained_domains": first_trained.get("domains", []),
        },
        "pair_age_40": {
            "turn": anchor,
            "bank": item_dict(anchor_state["inventories"][actor]),
            "workers": sum(unit["player"] == actor for unit in anchor_state["units"]),
            "crop_portfolio": portfolio,
            "actions": summarize_phase(age40_events),
        },
        "post_scale": {
            "successful_material_actions": dict(sorted(later_successes.items())),
            "successful_material_action_count": later_total,
            "chop_drop_share": ratio(
                later_successes["CHOP"] + later_successes["DROP"], later_total
            ),
            "workers": summarize_phase(later_events)["workers"],
        },
        "integrity": {
            "trajectory_turns": len(trajectory),
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": unknown,
            "workers": len(analysis["workers"]),
            "successful_trains": len(training_events),
            **lineage_quality,
        },
    }


def scalar_age40(row: dict) -> dict[str, int]:
    snapshot = row["pair_age_40"]
    portfolio = snapshot["crop_portfolio"]
    result = {f"bank_{name.lower()}": snapshot["bank"][name] for name in ITEMS}
    for origin in ("actor", "natural", "opponent"):
        result[f"{origin}_plants"] = sum(
            portfolio[origin][kind]["plants"] for kind in ITEMS[:4]
        )
        result[f"{origin}_ripe_fruit"] = sum(
            portfolio[origin][kind]["fruits"] for kind in ITEMS[:4]
        )
    for ordinal in (0, 1):
        worker = snapshot["actions"]["workers"].get(str(ordinal), {})
        successful = worker.get("successful", {})
        result[f"worker{ordinal}_harvest"] = successful.get("HARVEST", 0)
        result[f"worker{ordinal}_plant"] = successful.get("PLANT", 0)
        result[f"worker{ordinal}_mine"] = successful.get("MINE", 0)
        result[f"worker{ordinal}_chop"] = successful.get("CHOP", 0)
        result[f"worker{ordinal}_drop"] = successful.get("DROP", 0)
    return result


def age40_comparison(rows: list[dict]) -> dict:
    groups = {
        "eventual_scaler": [scalar_age40(row) for row in rows if row["scaler"]],
        "eventual_compact": [scalar_age40(row) for row in rows if not row["scaler"]],
    }
    fields = sorted({field for values in groups.values() for row in values for field in row})
    means = {
        name: {
            field: mean(row[field] for row in values)
            for field in fields
        }
        for name, values in groups.items()
    }
    return {
        "counts": {name: len(values) for name, values in groups.items()},
        "means": means,
        "scaler_minus_compact": {
            field: (
                means["eventual_scaler"][field] - means["eventual_compact"][field]
                if groups["eventual_scaler"] and groups["eventual_compact"]
                else None
            )
            for field in fields
        },
    }


def summarize_agent(rows: list[dict]) -> dict:
    scaler = [row for row in rows if row["scaler"]]
    later_trains = [
        event
        for row in rows
        for event in row["training_events"]
        if event["ordinal"] >= 2
    ]
    later_successes = Counter()
    for row in rows:
        later_successes.update(row["post_scale"]["successful_material_actions"])
    later_total = sum(later_successes.values())
    first_domain_counts = Counter(
        len(row["pair_foundation"]["first_trained_domains"]) for row in scaler
    )
    return {
        "games": len(rows),
        "scaler_games": len(scaler),
        "final_worker_distribution": dict(
            sorted(Counter(row["final_workers"] for row in rows).items())
        ),
        "mean_margin": mean(row["margin"] for row in rows),
        "later_train_events": len(later_trains),
        "later_train_delay_le1": sum(
            event["delay_after_affordable"] is not None
            and event["delay_after_affordable"] <= 1
            for event in later_trains
        ),
        "later_train_delay_le1_rate": ratio(
            sum(
                event["delay_after_affordable"] is not None
                and event["delay_after_affordable"] <= 1
                for event in later_trains
            ),
            len(later_trains),
        ),
        "later_train_two_plus_contributors": sum(
            event["useful_contributor_count"] >= 2 for event in later_trains
        ),
        "later_train_two_plus_contributor_rate": ratio(
            sum(event["useful_contributor_count"] >= 2 for event in later_trains),
            len(later_trains),
        ),
        "scaler_renewable_foundations": sum(
            row["pair_foundation"]["renewable"] for row in scaler
        ),
        "scaler_capitalization_foundations": sum(
            row["pair_foundation"]["capitalization"] for row in scaler
        ),
        "scaler_first_worker_two_plus_domains": sum(
            len(row["pair_foundation"]["first_trained_domains"]) >= 2
            for row in scaler
        ),
        "scaler_first_worker_domain_count_distribution": dict(
            sorted(first_domain_counts.items())
        ),
        "later_successful_material_actions": dict(sorted(later_successes.items())),
        "later_chop_drop_share": ratio(
            later_successes["CHOP"] + later_successes["DROP"], later_total
        ),
        "pair_age_40": age40_comparison(rows),
    }


def build_blueprint(rank_one: dict) -> dict:
    return {
        "entry": (
            "replace the resident's pure wood second-worker role with an explicitly scheduled "
            "hybrid foundation; do not hand paid harvest skill to the old continuation"
        ),
        "foundation_roles": {
            "starter": (
                "maintain renewable training-fruit cycles and bank fruit; use wood only when no "
                "renewable material job is ready"
            ),
            "first_trained": (
                "work across at least two domains: crop harvest/replant plus mining/chopping; "
                "bank bill material without suspending production"
            ),
        },
        "capitalization_boundary": (
            "TRAIN immediately when the jointly produced bill is deposited; reserve the bill "
            "against same-turn PICK/PLANT before emitting TRAIN"
        ),
        "post_scale": (
            "make worker three primarily CHOP/DROP logistics while the original pair keeps the "
            "renewable currency engine alive"
        ),
        "non_goals": [
            "no late D89 funding detour",
            "no max-bank worker followed by unchanged Yamo tasks",
            "no fitted pair-age-40 selector in D95",
            "no fixed universal worker count",
        ],
        "observed_rank_one_age40_difference": rank_one["pair_age_40"][
            "scaler_minus_compact"
        ],
    }


def analyze(rows: list[dict], input_hashes: dict) -> dict:
    rows = sorted(rows, key=lambda row: (row["agent_id"], row["game_id"], row["seat"]))
    grouped = {
        target["name"]: [row for row in rows if row["agent_id"] == agent_id]
        for agent_id, target in TARGETS.items()
    }
    summaries = {name: summarize_agent(values) for name, values in grouped.items()}
    rank_one = summaries["delineate"]
    reference_replication = {
        name: {
            "has_scaler_games": summary["scaler_games"] > 0,
            "all_scalers_renewable": (
                summary["scaler_games"] > 0
                and summary["scaler_renewable_foundations"] == summary["scaler_games"]
            ),
            "all_scalers_capitalizing": (
                summary["scaler_games"] > 0
                and summary["scaler_capitalization_foundations"]
                == summary["scaler_games"]
            ),
            "coordinated_later_funding": (
                summary["later_train_two_plus_contributor_rate"] is not None
                and summary["later_train_two_plus_contributor_rate"] >= 0.80
            ),
        }
        for name, summary in summaries.items()
        if name != "delineate"
    }
    integrity = {
        "exact_30_games": len(rows) == 30,
        "ten_per_agent": all(len(values) == 10 for values in grouped.values()),
        "unique_occurrences": len(
            {(row["game_id"], row["agent_id"]) for row in rows}
        )
        == 30,
        "turn_streams_exact": all(
            row["integrity"]["trajectory_turns"]
            == row["integrity"]["decoded_turns"]
            for row in rows
        ),
        "zero_unknown_diff_updates": all(
            row["integrity"]["unknown_diff_updates"] == 0 for row in rows
        ),
        "spawn_train_exact": all(
            row["integrity"]["workers"]
            == 1 + row["integrity"]["successful_trains"]
            for row in rows
        ),
        "all_have_first_train": all(row["training_events"] for row in rows),
        "zero_unassigned_cargo_deltas": all(
            row["integrity"]["unassigned_cargo_deltas"] == 0 for row in rows
        ),
    }
    gates = {
        "rank_one_scaler_games_at_least_4": rank_one["scaler_games"] >= 4,
        "rank_one_later_train_delay_le1_at_least_0.80": (
            rank_one["later_train_delay_le1_rate"] is not None
            and rank_one["later_train_delay_le1_rate"] >= 0.80
        ),
        "rank_one_later_train_two_plus_contributors_at_least_0.80": (
            rank_one["later_train_two_plus_contributor_rate"] is not None
            and rank_one["later_train_two_plus_contributor_rate"] >= 0.80
        ),
        "all_rank_one_scalers_renewable": (
            rank_one["scaler_renewable_foundations"] == rank_one["scaler_games"]
        ),
        "all_rank_one_scalers_capitalizing": (
            rank_one["scaler_capitalization_foundations"] == rank_one["scaler_games"]
        ),
        "all_rank_one_scaler_first_workers_two_plus_domains": (
            rank_one["scaler_first_worker_two_plus_domains"]
            == rank_one["scaler_games"]
        ),
        "rank_one_later_chop_drop_share_at_least_0.70": (
            rank_one["later_chop_drop_share"] is not None
            and rank_one["later_chop_drop_share"] >= 0.70
        ),
        "both_reference_agents_replicate_direction": all(
            all(values.values()) for values in reference_replication.values()
        ),
        "blueprint_structurally_new": True,
    }
    pass_integrity = all(integrity.values())
    blueprint_warrant = pass_integrity and all(gates.values())
    return {
        "schema": 1,
        "scope": "manifest-verified open D61p rank-one concurrent-scaler archaeology",
        "input_hashes": input_hashes,
        "integrity": integrity,
        "integrity_pass": pass_integrity,
        "agent_summaries": summaries,
        "reference_replication": reference_replication,
        "blueprint_gates": gates,
        "blueprint_warrant": blueprint_warrant,
        "blueprint": build_blueprint(rank_one) if blueprint_warrant else None,
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
    occurrences = []
    for task in inputs["tasks"]:
        source_ids = set(task["top_source_ids"])
        for player in task["game"]["players"]:
            agent_id = int(player.get("agentId", -1))
            if agent_id in TARGETS and agent_id in source_ids:
                occurrences.append((task, agent_id))
    occurrences.sort(key=lambda item: (item[1], int(item[0]["game"]["gameId"])))
    counts = Counter(agent_id for _, agent_id in occurrences)
    if counts != Counter({agent_id: 10 for agent_id in TARGETS}):
        raise ValueError(f"unexpected selected occurrence counts: {dict(counts)}")

    if args.jobs <= 1:
        rows = [analyze_occurrence(task, agent_id) for task, agent_id in occurrences]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            rows = list(
                executor.map(
                    analyze_occurrence,
                    (task for task, _ in occurrences),
                    (agent_id for _, agent_id in occurrences),
                )
            )

    input_hashes = {
        **inputs["input_hashes"],
        "d95_protocol": sha256_file(PROTOCOL),
        "d95_analyzer": sha256_file(Path(__file__)),
    }
    result = analyze(rows, input_hashes)
    atomic_write(args.output, result)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "integrity_pass": result["integrity_pass"],
                "blueprint_warrant": result["blueprint_warrant"],
                "agent_summaries": result["agent_summaries"],
                "blueprint_gates": result["blueprint_gates"],
            },
            indent=1,
            sort_keys=True,
        )
    )
    return 0 if result["integrity_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
