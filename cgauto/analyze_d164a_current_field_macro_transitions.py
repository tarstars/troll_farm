#!/usr/bin/env python3
"""Analyze open D164 field replays for macro episodes missing from local proxies."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import statistics
import tempfile

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d101a_production_suppression import (
    MATERIAL_VERBS,
    reconstruct_generation_actions,
)
from cgauto.analyze_d61p_field_snapshot import (
    load_open_inputs,
    read_jsonl,
    sha256_file,
)
from cgauto.recent_resident_field_census import decoded_states
from cgauto.rich_opponent_scheduler_transition_study import (
    verified_training_events,
    worker_scheduler,
)
from cgauto.top_player_opening_analysis import analyze_players, player_commands


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = BASE / "d164a-current-field-macro-transition-audit-protocol-2026-07-23.md"
LOCK = BASE / "d164a-current-field-macro-transition-audit-lock.json"
DEFAULT_SNAPSHOT = (
    ROOT / "data/external/arena-corpus/snapshots/20260723T074715Z-d164a"
)
DEFAULT_OUTPUT = BASE / "d164a-current-field-macro-transition-audit-result.json"
CUTS = (75, 100, 125, 150, 175, 200, 225)
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")

MOTIFS = (
    "own_crop_reaping",
    "same_worker_renewal_cycle",
    "same_worker_reap_bank_cycle",
    "opponent_crop_reaping",
    "coordinated_later_training",
    "pre_scale_renewal_and_coordinated_training",
    "production_suppression_overlap",
    "strict_producer_suppressor_separation",
    "bidirectional_producer_suppressor_handoff",
    "one_way_producer_to_suppressor_handoff",
    "foundation_production_with_later_suppression",
)

HISTORY = {
    "own_crop_reaping": {
        "status": "closed_as_standalone",
        "references": ["D87", "D89", "D102"],
        "reason": "renewal exists and can be valuable, but fixed/unconditional transfer is unsafe",
        "open": False,
        "scores": (4, 2, 3),
    },
    "same_worker_renewal_cycle": {
        "status": "closed_as_fixed_cycle",
        "references": ["D26", "D87", "D89", "D102"],
        "reason": "fixed pulses, immediate regeneration, and wholesale productive transfer all failed safety",
        "open": False,
        "scores": (3, 2, 2),
    },
    "same_worker_reap_bank_cycle": {
        "status": "closed_as_resource_route",
        "references": ["D89", "D163"],
        "reason": "banking/routing without the complete competitive schedule did not transport",
        "open": False,
        "scores": (4, 3, 3),
    },
    "opponent_crop_reaping": {
        "status": "causally_rejected",
        "references": ["opponent-crop-harvest-on-contact"],
        "reason": "the exact one-action harvest residual lost margin and increased opponent score",
        "open": False,
        "scores": (5, 5, 2),
    },
    "coordinated_later_training": {
        "status": "closed_as_serialized_funding",
        "references": ["D94", "D95", "D162"],
        "reason": "joint funding is real, but reserve/bridge implementations starved productive work",
        "open": False,
        "scores": (3, 2, 2),
    },
    "pre_scale_renewal_and_coordinated_training": {
        "status": "closed_as_fixed_complete_transfer",
        "references": ["D94", "D95", "D102"],
        "reason": "known field invariant; existing fixed and wholesale controllers failed resident-relative value",
        "open": False,
        "scores": (2, 1, 2),
    },
    "production_suppression_overlap": {
        "status": "closed_as_wholesale_scheduler",
        "references": ["D101", "D102"],
        "reason": "the architecture is established, but complete D40 transfer raised opponent output",
        "open": False,
        "scores": (2, 1, 2),
    },
    "strict_producer_suppressor_separation": {
        "status": "closed_as_static_role_split",
        "references": ["D92", "D101", "D102"],
        "reason": "static targeting and complete role schedulers did not preserve resident value",
        "open": False,
        "scores": (2, 1, 2),
    },
    "bidirectional_producer_suppressor_handoff": {
        "status": "potentially_new_coordination_primitive",
        "references": ["D24", "D26", "D95"],
        "reason": "per-worker stateful return differs from the rejected global fixed-duration handoffs",
        "open": True,
        "scores": (3, 4, 3),
    },
    "one_way_producer_to_suppressor_handoff": {
        "status": "potentially_new_coordination_primitive",
        "references": ["D24", "D26", "D95"],
        "reason": "a state-triggered per-worker lifecycle differs from a global turn-cut policy swap",
        "open": True,
        "scores": (4, 4, 3),
    },
    "foundation_production_with_later_suppression": {
        "status": "closed_as_complete_scaler",
        "references": ["D95", "D101", "D102"],
        "reason": "the invariant is known; the complete resident transfer failed value and tail gates",
        "open": False,
        "scores": (2, 1, 2),
    },
}


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    return numerator / denominator if denominator else None


def mean(values) -> float | None:
    selected = list(values)
    return statistics.mean(selected) if selected else None


def atomic_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as target:
            json.dump(value, target, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def verify_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    if lock.get("schema") != "troll-farm-d164a-lock-v1":
        raise ValueError("unknown D164 lock schema")
    for relative, expected in lock["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"D164 frozen input differs: {relative}")
    return lock


def compressed_roles(events: list[dict]) -> list[str]:
    return [row["role"] for row in compressed_role_events(events)]


def compressed_role_events(events: list[dict]) -> list[dict]:
    result = []
    for event in sorted(events, key=lambda row: (row["turn"], row["ordinal"])):
        role = None
        if event["verb"] == "PLANT" and event["created_origin"] == "actor":
            role = "P"
        elif event["verb"] == "HARVEST" and event["target_origin"] == "actor":
            role = "P"
        elif event["verb"] == "CHOP" and event["target_origin"] == "opponent":
            role = "S"
        if role is not None and (not result or result[-1]["role"] != role):
            result.append(
                {
                    "role": role,
                    "turn": int(event["turn"]),
                    "ordinal": int(event["ordinal"]),
                    "workforce": int(event["workforce"]),
                }
            )
    return result


def has_subsequence(values: list[str], target: tuple[str, ...]) -> bool:
    index = 0
    for value in values:
        if value == target[index]:
            index += 1
            if index == len(target):
                return True
    return False


def first_role_subsequence(
    events: list[dict], target: tuple[str, ...]
) -> list[dict] | None:
    selected = []
    index = 0
    for event in events:
        if event["role"] == target[index]:
            selected.append(event)
            index += 1
            if index == len(target):
                return selected
    return None


def later_same_worker(
    earlier: list[dict], later: list[dict], *, horizon: int = 32
) -> bool:
    return any(
        first["ordinal"] == second["ordinal"]
        and first["turn"] < second["turn"] <= first["turn"] + horizon
        for first in earlier
        for second in later
    )


def joint_plant_creators(
    before: dict,
    after: dict,
    trajectory_row: dict,
    cell: tuple[int, int],
) -> set[int]:
    """Return exact simultaneous creators for one observed same-kind birth."""

    before_units = {int(unit["id"]): unit for unit in before["units"]}
    after_plant = next(
        (
            plant
            for plant in after["plants"]
            if (int(plant["x"]), int(plant["y"])) == cell
        ),
        None,
    )
    if after_plant is None:
        return set()
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
                and fields[2].upper() == after_plant["type"]
            ):
                creators.add(player)
    return creators


def resolve_joint_births(
    events: list[dict],
    generations: dict[str, dict],
    quality: dict,
    states: list[dict],
    trajectory: list[dict],
) -> int:
    """Convert exact simultaneous two-player births from ambiguous to joint."""

    repaired = set()
    for identifier, generation in generations.items():
        if generation["origin"] != "ambiguous":
            continue
        turn = int(generation["birth_turn"])
        cell = tuple(int(value) for value in generation["cell"])
        if (
            0 < turn < len(states)
            and turn <= len(trajectory)
            and joint_plant_creators(
                states[turn - 1], states[turn], trajectory[turn - 1], cell
            )
            == {0, 1}
        ):
            generation["origin"] = "joint"
            repaired.add(identifier)
    if repaired:
        for event in events:
            if event.get("created_generation") in repaired:
                event["created_origin"] = "joint"
            if event.get("target_generation") in repaired:
                event["target_origin"] = "joint"
        quality["ambiguous_births"] = max(
            0, quality.get("ambiguous_births", 0) - len(repaired)
        )
        quality["joint_births"] = quality.get("joint_births", 0) + len(repaired)
    return len(repaired)


def state_metrics(
    state: dict,
    lineage: dict[tuple[int, int], str],
    generations: dict[str, dict],
    actor: int,
    events: list[dict],
    cut: int,
) -> dict:
    inventory = list(state["inventories"][actor])
    units = [unit for unit in state["units"] if int(unit["player"]) == actor]
    opponent_units = [
        unit for unit in state["units"] if int(unit["player"]) == 1 - actor
    ]
    carry = [
        sum(int(unit["carry"][item]) for unit in units) for item in range(len(ITEMS))
    ]
    plants = {
        (int(plant["x"]), int(plant["y"])): plant for plant in state["plants"]
    }
    assets = {
        origin: {"plants": 0, "fruit": 0, "health": 0}
        for origin in ("actor", "opponent", "natural", "joint")
    }
    for cell, identifier in lineage.items():
        plant = plants.get(cell)
        if plant is None:
            continue
        origin = generations[identifier]["origin"]
        if origin not in assets:
            continue
        assets[origin]["plants"] += 1
        assets[origin]["fruit"] += int(plant["fruits"])
        assets[origin]["health"] += int(plant["health"])

    by_worker: dict[int, list[dict]] = defaultdict(list)
    for event in events:
        if event["success"] and event["turn"] <= cut:
            by_worker[int(event["ordinal"])].append(event)
    role_counts = Counter()
    for ordinal in sorted(by_worker):
        roles = set(compressed_roles(by_worker[ordinal]))
        if roles == {"P", "S"}:
            role_counts["producer_and_suppressor"] += 1
        elif roles == {"P"}:
            role_counts["producer_only"] += 1
        elif roles == {"S"}:
            role_counts["suppressor_only"] += 1
        else:
            role_counts["other"] += 1
    role_counts["other"] += max(0, len(units) - sum(role_counts.values()))

    return {
        "bank_score": sum(inventory[:4]) + 4 * inventory[5],
        "bank_fruit": sum(inventory[:4]),
        "bank_iron": inventory[4],
        "bank_wood": inventory[5],
        "carry_fruit": sum(carry[:4]),
        "carry_iron": carry[4],
        "carry_wood": carry[5],
        "workers": len(units),
        "opponent_workers": len(opponent_units),
        "own_live_crops": assets["actor"]["plants"],
        "own_live_crop_fruit": assets["actor"]["fruit"],
        "own_live_crop_health": assets["actor"]["health"],
        "opponent_live_crops": assets["opponent"]["plants"],
        "opponent_live_crop_fruit": assets["opponent"]["fruit"],
        "opponent_live_crop_health": assets["opponent"]["health"],
        "natural_live_plants": assets["natural"]["plants"],
        "joint_live_crops": assets["joint"]["plants"],
        "joint_live_crop_fruit": assets["joint"]["fruit"],
        **{f"roles_{key}": role_counts[key] for key in (
            "producer_only",
            "suppressor_only",
            "producer_and_suppressor",
            "other",
        )},
    }


def analyze_occurrence(task: dict, actor_id: int, metadata: dict) -> dict:
    game = task["game"]
    player_row = next(
        row for row in game["players"] if int(row.get("agentId", -1)) == actor_id
    )
    actor = int(player_row["index"])
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    _map, states, unknown = decoded_states(raw, trajectory)
    if unknown or len(states) != len(trajectory) + 1:
        raise ValueError(f"D164 decoded-state mismatch in game {game['gameId']}")
    analyses = analyze_players(states, trajectory)
    analysis = analyses[actor]
    worker_ordinals = {
        int(worker["unit_id"]): int(worker["ordinal"])
        for worker in analysis["workers"]
    }
    events, generations, lineage, quality = reconstruct_generation_actions(
        states, trajectory, actor, worker_ordinals
    )
    joint_repairs = resolve_joint_births(
        events, generations, quality, states, trajectory
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
    opponent_harvests = [
        event
        for event in successful
        if event["verb"] == "HARVEST" and event["target_origin"] == "opponent"
    ]
    opponent_chops = [
        event
        for event in successful
        if event["verb"] == "CHOP" and event["target_origin"] == "opponent"
    ]
    drops = [event for event in successful if event["verb"] == "DROP"]

    scheduler = worker_scheduler(
        states, trajectory, actor, analysis["workers"]
    )
    training_events = verified_training_events(
        analysis, states, actor, bool(game["map"]["iron"])
    )
    later_trains = [event for event in training_events if event["ordinal"] >= 2]
    third_worker_turn = next(
        (event["turn"] for event in later_trains if event["ordinal"] == 2), None
    )
    coordinated_later = bool(
        later_trains
        and all(event["useful_funding_contributor_count"] >= 2 for event in later_trains)
    )

    by_worker: dict[int, list[dict]] = defaultdict(list)
    for event in successful:
        by_worker[int(event["ordinal"])].append(event)
    role_episode_events = {
        ordinal: compressed_role_events(rows) for ordinal, rows in by_worker.items()
    }
    role_sequences = {
        ordinal: [event["role"] for event in rows]
        for ordinal, rows in role_episode_events.items()
    }
    handoff_cycles = []
    one_way_handoffs = []
    for ordinal, episodes in sorted(role_episode_events.items()):
        cycle = first_role_subsequence(episodes, ("P", "S", "P"))
        if cycle is not None:
            handoff_cycles.append(
                {
                    "ordinal": ordinal,
                    "producer_turn": cycle[0]["turn"],
                    "suppressor_turn": cycle[1]["turn"],
                    "return_turn": cycle[2]["turn"],
                    "suppression_duration": cycle[2]["turn"] - cycle[1]["turn"],
                    "workforce_at_suppression": cycle[1]["workforce"],
                }
            )
            continue
        one_way = first_role_subsequence(episodes, ("P", "S"))
        if one_way is not None and episodes[-1]["role"] == "S":
            one_way_handoffs.append(
                {
                    "ordinal": ordinal,
                    "producer_turn": one_way[0]["turn"],
                    "suppressor_turn": one_way[1]["turn"],
                    "workforce_at_suppression": one_way[1]["workforce"],
                }
            )
    bidirectional_handoff = bool(handoff_cycles)
    one_way_handoff = bool(one_way_handoffs)

    planted_workers = {event["ordinal"] for event in plants}
    reaping_workers = {event["ordinal"] for event in own_harvests}
    strict_producers = planted_workers & reaping_workers
    suppressors = {event["ordinal"] for event in opponent_chops}
    strict_separation = any(
        producer != suppressor
        for producer in strict_producers
        for suppressor in suppressors
    )
    first_plant = min((event["turn"] for event in plants), default=None)
    last_harvest = max((event["turn"] for event in own_harvests), default=None)
    overlap = bool(
        first_plant is not None
        and last_harvest is not None
        and any(first_plant <= event["turn"] <= last_harvest for event in opponent_chops)
    )

    renewal_cycle = later_same_worker(own_harvests, plants)
    reap_bank = later_same_worker(own_harvests, drops)
    pre_scale_renewal = bool(
        third_worker_turn is not None
        and coordinated_later
        and later_same_worker(
            [event for event in own_harvests if event["turn"] < third_worker_turn],
            [event for event in plants if event["turn"] < third_worker_turn],
        )
    )
    foundation_production = bool(
        third_worker_turn is not None
        and any(
            event["ordinal"] <= 1 and event["turn"] >= third_worker_turn
            for event in own_harvests
        )
        and any(
            event["ordinal"] >= 2 and event["turn"] >= third_worker_turn
            for event in opponent_chops
        )
    )
    motifs = {
        "own_crop_reaping": bool(own_harvests),
        "same_worker_renewal_cycle": renewal_cycle,
        "same_worker_reap_bank_cycle": reap_bank,
        "opponent_crop_reaping": bool(opponent_harvests),
        "coordinated_later_training": coordinated_later,
        "pre_scale_renewal_and_coordinated_training": pre_scale_renewal,
        "production_suppression_overlap": overlap,
        "strict_producer_suppressor_separation": strict_separation,
        "bidirectional_producer_suppressor_handoff": bidirectional_handoff,
        "one_way_producer_to_suppressor_handoff": one_way_handoff,
        "foundation_production_with_later_suppression": foundation_production,
    }
    if set(motifs) != set(MOTIFS):
        raise AssertionError("D164 motif catalog drift")

    cut_states = {}
    for cut in CUTS:
        if cut >= len(states):
            continue
        cut_states[str(cut)] = state_metrics(
            states[cut], lineage[cut], generations, actor, successful, cut
        )

    origin_actions = Counter(
        f"{event['verb']}:{event['target_origin'] or event['created_origin'] or 'none'}"
        for event in successful
    )
    return {
        "game_id": int(game["gameId"]),
        "agent_id": actor_id,
        "agent": metadata["pseudo"],
        "source_rank": metadata["source_rank"],
        "cohort": metadata["cohort"],
        "seat": actor,
        "turns": len(trajectory),
        "score": int(game["scores"][actor]),
        "opponent_score": int(game["scores"][1 - actor]),
        "margin": int(game["scores"][actor]) - int(game["scores"][1 - actor]),
        "final_workers": len(analysis["workers"]),
        "motifs": motifs,
        "role_sequences": {
            str(ordinal): sequence for ordinal, sequence in sorted(role_sequences.items())
        },
        "handoff_cycles": handoff_cycles,
        "one_way_handoffs": one_way_handoffs,
        "successful_actions_by_origin": dict(sorted(origin_actions.items())),
        "training_events": training_events,
        "cut_states": cut_states,
        "integrity": {
            "decoded_turns": len(states) - 1,
            "trajectory_turns": len(trajectory),
            "unknown_diff_updates": unknown,
            "unknown_births": quality.get("unknown_births", 0),
            "ambiguous_births": quality.get("ambiguous_births", 0),
            "missing_live_generations": quality.get("missing_live_generations", 0),
            "missing_worker_ordinals": quality.get("missing_worker_ordinals", 0),
            "unassigned_cargo_deltas": quality.get("unassigned_cargo_deltas", 0),
            "joint_births": quality.get("joint_births", 0),
            "joint_birth_repairs": joint_repairs,
            "workers": len(analysis["workers"]),
            "successful_trains": len(training_events),
        },
    }


def mean_cut_states(rows: list[dict]) -> dict:
    result = {}
    for cut in CUTS:
        key = str(cut)
        available = [row["cut_states"][key] for row in rows if key in row["cut_states"]]
        fields = sorted({field for row in available for field in row})
        result[key] = {
            "games": len(available),
            "mean": {
                field: mean(row[field] for row in available)
                for field in fields
            },
        }
    return result


def mean_cut_transitions(cut_states: dict) -> dict:
    result = {}
    for before, after in zip(CUTS, CUTS[1:]):
        left = cut_states[str(before)]
        right = cut_states[str(after)]
        if not left["games"] or not right["games"]:
            continue
        # Means are computed on the same frozen cohort at each cut; the report
        # retains the denominators so attrition is explicit.
        fields = sorted(set(left["mean"]) & set(right["mean"]))
        result[f"{before}-{after}"] = {
            "games_at_start": left["games"],
            "games_at_end": right["games"],
            "mean_delta": {
                field: right["mean"][field] - left["mean"][field]
                for field in fields
            },
        }
    return result


def summary(values) -> dict:
    selected = list(values)
    return {
        "count": len(selected),
        "mean": mean(selected),
        "median": statistics.median(selected) if selected else None,
        "minimum": min(selected) if selected else None,
        "maximum": max(selected) if selected else None,
    }


def handoff_summary(rows: list[dict]) -> dict:
    selected = [row for row in rows if row["handoff_cycles"]]
    first = [
        min(row["handoff_cycles"], key=lambda event: event["suppressor_turn"])
        for row in selected
    ]
    return {
        "games": len(selected),
        "rate": ratio(len(selected), len(rows)),
        "distinct_agents": len({row["agent_id"] for row in selected}),
        "both_seats": {row["seat"] for row in selected} == {0, 1},
        "worker_ordinals": dict(
            sorted(Counter(event["ordinal"] for event in first).items())
        ),
        "producer_turn": summary(event["producer_turn"] for event in first),
        "suppressor_turn": summary(event["suppressor_turn"] for event in first),
        "return_turn": summary(event["return_turn"] for event in first),
        "suppression_duration": summary(
            event["suppression_duration"] for event in first
        ),
        "workforce_at_suppression": dict(
            sorted(Counter(event["workforce_at_suppression"] for event in first).items())
        ),
        "mean_margin_descriptive_only": mean(row["margin"] for row in selected),
    }


def cut_contrast(rows: list[dict], motif: str) -> dict:
    selected = [row for row in rows if row["motifs"][motif]]
    comparison = [row for row in rows if not row["motifs"][motif]]
    selected_cuts = mean_cut_states(selected)
    comparison_cuts = mean_cut_states(comparison)
    result = {}
    for cut in CUTS:
        key = str(cut)
        left = selected_cuts[key]
        right = comparison_cuts[key]
        fields = sorted(set(left["mean"]) & set(right["mean"]))
        result[key] = {
            "motif_games": left["games"],
            "comparison_games": right["games"],
            "mean_difference": {
                field: left["mean"][field] - right["mean"][field]
                for field in fields
            },
        }
    return result


def summarize_cohort(rows: list[dict], *, top5: bool = False) -> dict:
    motif_counts = {
        motif: sum(row["motifs"][motif] for row in rows) for motif in MOTIFS
    }
    per_agent = {}
    for agent_id in sorted({row["agent_id"] for row in rows}):
        selected = [row for row in rows if row["agent_id"] == agent_id]
        per_agent[str(agent_id)] = {
            "agent": selected[0]["agent"],
            "source_rank": selected[0]["source_rank"],
            "games": len(selected),
            "motif_rates": {
                motif: ratio(
                    sum(row["motifs"][motif] for row in selected), len(selected)
                )
                for motif in MOTIFS
            },
        }
    cut_states = mean_cut_states(rows)
    result = {
        "games": len(rows),
        "agents": len({row["agent_id"] for row in rows}),
        "seat_counts": dict(sorted(Counter(row["seat"] for row in rows).items())),
        "mean_margin": mean(row["margin"] for row in rows),
        "mean_score": mean(row["score"] for row in rows),
        "mean_opponent_score": mean(row["opponent_score"] for row in rows),
        "mean_final_workers": mean(row["final_workers"] for row in rows),
        "bidirectional_handoff": handoff_summary(rows),
        "motif_counts": motif_counts,
        "motif_rates": {
            motif: ratio(motif_counts[motif], len(rows)) for motif in MOTIFS
        },
        "cut_states": cut_states,
        "cut_transitions": mean_cut_transitions(cut_states),
        "per_agent": per_agent,
    }
    if top5:
        result["motif_agent_support"] = {
            motif: sum(
                agent["motif_rates"][motif] is not None
                and agent["motif_rates"][motif] >= 0.30
                for agent in per_agent.values()
            )
            for motif in MOTIFS
        }
    return result


def axis_score(rate: float, thresholds: tuple[float, ...]) -> int:
    return 1 + sum(rate >= threshold for threshold in thresholds)


def build_matrix(cohorts: dict) -> list[dict]:
    top5 = cohorts["rank_1_5"]
    reference = cohorts["rank_6_20"]
    resident = cohorts["resident"]
    rows = []
    for motif in MOTIFS:
        top_rate = top5["motif_rates"][motif] or 0.0
        reference_rate = reference["motif_rates"][motif] or 0.0
        resident_rate = resident["motif_rates"][motif] or 0.0
        gap = top_rate - resident_rate
        support = top5["motif_agent_support"][motif]
        field_stable = bool(
            top_rate >= 0.30
            and support >= 3
            and reference_rate >= 0.20
            and gap >= 0.15
        )
        history = HISTORY[motif]
        breadth = axis_score(
            min(top_rate, reference_rate), (0.20, 0.30, 0.45, 0.60)
        )
        resident_gap = axis_score(gap, (0.15, 0.25, 0.40, 0.60))
        isolatability, fallback, tail = history["scores"]
        total = breadth + resident_gap + isolatability + fallback + tail
        rows.append(
            {
                "motif": motif,
                "top5_rate": top_rate,
                "top5_agent_support": support,
                "rank6_20_rate": reference_rate,
                "resident_rate": resident_rate,
                "resident_gap": gap,
                "field_stable_missing": field_stable,
                "history": {
                    key: history[key] for key in ("status", "references", "reason", "open")
                },
                "scores": {
                    "breadth": breadth,
                    "resident_gap": resident_gap,
                    "causal_isolatability": isolatability,
                    "exact_resident_fallback_compatibility": fallback,
                    "tail_safety": tail,
                    "total": total,
                },
                "eligible_new_primitive": bool(field_stable and history["open"]),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            row["eligible_new_primitive"],
            row["field_stable_missing"],
            row["scores"]["total"],
            row["top5_agent_support"],
            row["resident_gap"],
            row["motif"],
        ),
        reverse=True,
    )


def analyze(rows: list[dict], loaded: dict, lock: dict) -> dict:
    rows = sorted(rows, key=lambda row: (row["agent_id"], row["game_id"], row["seat"]))
    top_counts = Counter(
        row["agent_id"] for row in rows if row["cohort"] != "resident"
    )
    resident = [row for row in rows if row["cohort"] == "resident"]
    top5 = [row for row in rows if row["cohort"] == "rank_1_5"]
    reference = [row for row in rows if row["cohort"] == "rank_6_20"]
    top = top5 + reference
    unique = {(row["game_id"], row["agent_id"]) for row in rows}
    integrity = {
        "snapshot_qa_pass": bool(loaded["qa"]["pass"]),
        "confirmation_products_unread": True,
        "resident_identity_exact": int(loaded["resident_agent_id"]) == 6561795,
        "at_least_160_resident_games": len(resident) >= 160,
        "at_least_15_top20_agents": len(top_counts) >= 15,
        "at_least_150_top20_appearances": len(top) >= 150,
        "at_most_10_appearances_per_top_agent": bool(top_counts)
        and max(top_counts.values()) <= 10,
        "unique_actor_game_occurrences": len(unique) == len(rows),
        "both_seats_in_every_cohort": all(
            {row["seat"] for row in cohort} == {0, 1}
            for cohort in (top5, reference, resident)
        ),
        "all_state_streams_exact": all(
            row["integrity"]["decoded_turns"]
            == row["integrity"]["trajectory_turns"]
            and row["integrity"]["unknown_diff_updates"] == 0
            for row in rows
        ),
        "zero_unknown_or_ambiguous_births": all(
            row["integrity"]["unknown_births"] == 0
            and row["integrity"]["ambiguous_births"] == 0
            and row["integrity"]["missing_live_generations"] == 0
            for row in rows
        ),
        "all_workers_and_training_events_agree": all(
            row["integrity"]["workers"]
            == 1 + row["integrity"]["successful_trains"]
            and row["integrity"]["missing_worker_ordinals"] == 0
            for row in rows
        ),
    }
    integrity_pass = all(integrity.values())
    cohorts = {
        "rank_1_5": summarize_cohort(top5, top5=True),
        "rank_6_20": summarize_cohort(reference),
        "resident": summarize_cohort(resident),
    }
    matrix = build_matrix(cohorts) if integrity_pass else []
    eligible = [row for row in matrix if row["eligible_new_primitive"]]
    if eligible:
        selected = eligible[0]["motif"]
        decision = {
            "verdict": "freeze_bounded_per_worker_stateful_handoff_hypothesis",
            "selected_motif": selected,
            "next_experiment": (
                "exact-resident bounded per-worker producer/suppressor handoff on consumed maps; "
                "activate from observable role history, return to the warmed resident, and require "
                "activation, parity, mean, own-score, breadth, and tail gates"
            ),
            "construct_candidate": False,
            "arena_or_submission": False,
        }
    else:
        decision = {
            "verdict": "no_new_fixed_motif_change_to_trajectory_conditioned_action_value",
            "selected_motif": None,
            "next_experiment": (
                "resident-native trajectory-conditioned one-deviation value corpus over existing "
                "semantic actions; preserve exact KEEP and learn whether/when to enter and exit "
                "multi-worker jobs instead of writing another fixed reserve rule"
            ),
            "construct_candidate": False,
            "arena_or_submission": False,
        }
    selected_diagnostics = (
        {
            "motif": decision["selected_motif"],
            "cohort_handoff_timing": {
                name: handoff_summary(rows)
                for name, rows in (
                    ("rank_1_5", top5),
                    ("rank_6_20", reference),
                    ("resident", resident),
                )
            },
            "top5_cut_state_contrast_descriptive_only": cut_contrast(
                top5, decision["selected_motif"]
            ),
        }
        if integrity_pass and decision.get("selected_motif") is not None
        else None
    )
    return {
        "schema": "troll-farm-d164a-current-field-macro-transition-v1",
        "snapshot_id": loaded["snapshot_id"],
        "scope": "open-only immutable public replay diagnosis; no platform mutation",
        "input_hashes": {
            **loaded["input_hashes"],
            "d164_protocol": sha256_file(PROTOCOL),
            "d164_lock": sha256_file(LOCK),
            "d164_analyzer": sha256_file(Path(__file__)),
        },
        "lock": lock,
        "integrity": integrity,
        "integrity_pass": integrity_pass,
        "population": {
            "actor_occurrences": len(rows),
            "resident_games": len(resident),
            "top20_appearances": len(top),
            "top20_agents": len(top_counts),
            "top_appearances_per_agent": dict(sorted(top_counts.items())),
        },
        "cohorts": cohorts,
        "attack_matrix": matrix,
        "selected_motif_diagnostics": selected_diagnostics,
        "decision": decision if integrity_pass else {
            "verdict": "invalid_integrity",
            "construct_candidate": False,
            "arena_or_submission": False,
        },
    }


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as target:
        for row in sorted(
            rows, key=lambda item: (item["agent_id"], item["game_id"], item["seat"])
        ):
            target.write(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n")


def run(snapshot: Path, output: Path, rows_output: Path, jobs: int) -> dict:
    if not 1 <= jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    lock = verify_lock()
    loaded = load_open_inputs(snapshot)
    players = json.loads((Path(snapshot).resolve() / "players.json").read_text())
    top = {
        int(row["agent_id"]): row
        for row in players
        if "legend_top20" in (row.get("groups") or [])
    }
    resident_id = int(loaded["resident_agent_id"])
    resident_row = next(
        row for row in players if int(row["agent_id"]) == resident_id
    )
    occurrences = []
    for task in loaded["tasks"]:
        present = {int(row.get("agentId", -1)) for row in task["game"]["players"]}
        for actor_id in sorted(set(task["top_source_ids"]) & present):
            source = top[actor_id]
            occurrences.append(
                (
                    task,
                    actor_id,
                    {
                        "pseudo": source["pseudo"],
                        "source_rank": int(source["source_rank"]),
                        "cohort": (
                            "rank_1_5"
                            if int(source["source_rank"]) <= 5
                            else "rank_6_20"
                        ),
                    },
                )
            )
        if resident_id in present:
            occurrences.append(
                (
                    task,
                    resident_id,
                    {
                        "pseudo": resident_row["pseudo"],
                        "source_rank": int(resident_row["source_rank"]),
                        "cohort": "resident",
                    },
                )
            )
    occurrences.sort(key=lambda item: (item[1], int(item[0]["game"]["gameId"])))
    if jobs == 1:
        rows = [analyze_occurrence(*occurrence) for occurrence in occurrences]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            rows = list(
                executor.map(
                    analyze_occurrence,
                    (task for task, _, _ in occurrences),
                    (actor for _, actor, _ in occurrences),
                    (metadata for _, _, metadata in occurrences),
                    chunksize=2,
                )
            )
    result = analyze(rows, loaded, lock)
    write_rows(rows_output, rows)
    result["rows_artifact"] = {
        "path": str(rows_output),
        "rows": len(rows),
        "sha256": sha256_file(rows_output),
    }
    atomic_write(output, result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rows-output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    result = run(args.snapshot, args.output, args.rows_output, args.jobs)
    print(
        json.dumps(
            {
                "integrity_pass": result["integrity_pass"],
                "population": result["population"],
                "field_stable": [
                    row["motif"]
                    for row in result["attack_matrix"]
                    if row["field_stable_missing"]
                ],
                "eligible_new": [
                    row["motif"]
                    for row in result["attack_matrix"]
                    if row["eligible_new_primitive"]
                ],
                "decision": result["decision"],
                "output": str(args.output),
                "rows_output": str(args.rows_output),
            },
            indent=1,
            sort_keys=True,
        )
    )
    return 0 if result["integrity_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
