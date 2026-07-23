#!/usr/bin/env python3
"""Audit a compact persistent-job vocabulary on frozen rich field replays."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import battle_taxonomy as arena
from cgauto.recent_resident_field_census import corpus_parser, decoded_states
from cgauto.replay_conformance import action_commands
from cgauto.rich_opponent_scheduler_transition_study import (
    analyze_game as parent_analyze_game,
)
from cgauto.top_player_opening_analysis import (
    analyze_players,
    assigned_unit_commands,
)


JOB_LABELS = (
    "RENEW",
    "FELL_BANK",
    "PRESSURE",
    "MINE_BANK",
    "MIXED_BANK",
    "IDLE",
    "UNKNOWN",
)
DIRECT_PRODUCTIVE = {"HARVEST", "PICK", "PLANT", "CHOP", "DROP", "MINE"}
NON_IDLE = set(JOB_LABELS) - {"IDLE", "UNKNOWN"}
LOOKAHEAD_ACTIVE_TURNS = 12


def cell(unit: dict) -> tuple[int, int]:
    return int(unit["x"]), int(unit["y"])


def move_target(command: str) -> tuple[int, int] | None:
    fields = command.split()
    if len(fields) != 4 or fields[0].upper() != "MOVE":
        return None
    try:
        return int(fields[2]), int(fields[3])
    except ValueError:
        return None


def direct_job_label(
    command: str,
    unit: dict,
    crop_creators: dict[tuple[int, int], frozenset[int]],
    player: int,
) -> str | None:
    """Return a direct semantic job, or None when MOVE needs look-ahead."""

    fields = command.split()
    if not fields:
        return "UNKNOWN"
    verb = fields[0].upper()
    if verb == "MOVE":
        return None
    if verb == "WAIT":
        return "IDLE"
    if verb in {"HARVEST", "PICK", "PLANT"}:
        return "RENEW"
    if verb == "MINE":
        return "MINE_BANK"
    if verb == "CHOP":
        creators = crop_creators.get(cell(unit), frozenset())
        return "PRESSURE" if creators == frozenset({1 - player}) else "FELL_BANK"
    if verb == "DROP":
        cargo = [int(value) for value in unit.get("carry", [0] * 6)]
        families = []
        if sum(cargo[:4]) > 0:
            families.append("RENEW")
        if cargo[4] > 0:
            families.append("MINE_BANK")
        if cargo[5] > 0:
            families.append("FELL_BANK")
        if len(families) == 1:
            return families[0]
        if len(families) > 1:
            return "MIXED_BANK"
        return "IDLE"
    return "UNKNOWN"


def command_plant_claims(
    commands: dict[int, str], units: dict[int, dict], plants_after: dict
) -> dict[tuple[int, int], set[int]]:
    claims = defaultdict(set)
    for unit_id, command in commands.items():
        fields = command.split()
        unit = units.get(unit_id)
        if (
            len(fields) >= 3
            and fields[0].upper() == "PLANT"
            and unit is not None
            and cell(unit) in plants_after
            and fields[2].upper() == plants_after[cell(unit)]["type"]
        ):
            claims[cell(unit)].add(unit_id)
    return dict(claims)


def provenance_and_events(
    states: list[dict], trajectory: list[dict], player: int
) -> tuple[list[dict], dict]:
    """Build pre-turn provenance and unit command events for the analyzed side."""

    usable = min(len(states) - 1, len(trajectory))
    crop_creators: dict[tuple[int, int], frozenset[int]] = {}
    preturn_provenance = []
    events_by_unit = defaultdict(list)
    train_turns = set()
    exclusive_plants = Counter()
    ambiguous_plants = 0

    for turn in range(1, usable + 1):
        before = states[turn - 1]
        after = states[turn]
        before_plants = {cell(plant): plant for plant in before["plants"]}
        after_plants = {cell(plant): plant for plant in after["plants"]}
        before_units = {int(unit["id"]): unit for unit in before["units"]}
        assigned = {}
        for side in (0, 1):
            side_units = [unit for unit in before["units"] if unit["player"] == side]
            commands = action_commands(trajectory[turn - 1].get(f"commands{side}"))
            assigned[side] = assigned_unit_commands(commands, side_units)
            if any(command.split()[:1] == ["TRAIN"] for command in commands):
                if side == player:
                    train_turns.add(turn)

        crop_creators = {
            target: creators
            for target, creators in crop_creators.items()
            if target in before_plants
        }
        preturn_provenance.append(dict(crop_creators))
        for unit_id, command in assigned[player].items():
            unit = before_units.get(unit_id)
            if unit is None:
                continue
            direct = direct_job_label(command, unit, crop_creators, player)
            events_by_unit[unit_id].append(
                {
                    "turn": turn,
                    "command": command,
                    "verb": command.split()[0].upper() if command.split() else "",
                    "target": move_target(command),
                    "direct_label": direct,
                    "label": direct,
                }
            )

        new_cells = set(after_plants) - set(before_plants)
        claims_by_side = {}
        for side in (0, 1):
            claims_by_side[side] = command_plant_claims(
                assigned[side], before_units, after_plants
            )
        for target in new_cells:
            creators = frozenset(
                side for side in (0, 1) if target in claims_by_side[side]
            )
            if not creators:
                continue
            crop_creators[target] = creators
            if len(creators) == 1:
                exclusive_plants[next(iter(creators))] += 1
            else:
                ambiguous_plants += 1

    return preturn_provenance, {
        "events_by_unit": dict(events_by_unit),
        "train_turns": train_turns,
        "exclusive_plants": dict(exclusive_plants),
        "ambiguous_plants": ambiguous_plants,
        "usable_turns": usable,
    }


def resolve_move_jobs(events: list[dict], lookahead: int = LOOKAHEAD_ACTIVE_TURNS) -> None:
    """Resolve MOVE events in place from future direct jobs or stable prior routes."""

    for index, event in enumerate(events):
        if event["direct_label"] is not None:
            continue
        inherited = next(
            (
                future["direct_label"]
                for future in events[index + 1 : index + 1 + lookahead]
                if future["direct_label"] in NON_IDLE
            ),
            None,
        )
        if inherited is not None:
            event["label"] = inherited
            continue
        if index > 0:
            previous = events[index - 1]
            if (
                event["target"] is not None
                and event["target"] == previous["target"]
                and previous["label"] in NON_IDLE
            ):
                event["label"] = previous["label"]
                continue
        event["label"] = "UNKNOWN"


def run_lengths(events_by_unit: dict[int, list[dict]]) -> list[int]:
    lengths = []
    for events in events_by_unit.values():
        current = None
        length = 0
        for event in events:
            label = event["label"]
            if label not in NON_IDLE:
                if length:
                    lengths.append(length)
                current = None
                length = 0
            elif label == current:
                length += 1
            else:
                if length:
                    lengths.append(length)
                current = label
                length = 1
        if length:
            lengths.append(length)
    return lengths


def analyze_job_stream(
    states: list[dict], trajectory: list[dict], player: int, workers: list[dict]
) -> dict:
    _provenance, decoded = provenance_and_events(states, trajectory, player)
    events_by_unit = decoded["events_by_unit"]
    for events in events_by_unit.values():
        resolve_move_jobs(events)

    ordinal = {int(worker["unit_id"]): int(worker["ordinal"]) for worker in workers}
    by_turn = defaultdict(dict)
    labels = Counter()
    labels_by_ordinal = defaultdict(Counter)
    total_unit_turns = 0
    covered_unit_turns = 0
    direct_total = 0
    direct_covered = 0
    move_total = 0
    move_resolved = 0
    pressure_targets = 0
    transitions = Counter()
    for unit_id, events in events_by_unit.items():
        previous_nonidle = None
        for event in events:
            label = event["label"]
            by_turn[event["turn"]][unit_id] = label
            labels[label] += 1
            labels_by_ordinal[ordinal.get(unit_id, -1)][label] += 1
            total_unit_turns += 1
            covered_unit_turns += int(label != "UNKNOWN")
            if event["verb"] in DIRECT_PRODUCTIVE:
                direct_total += 1
                direct_covered += int(label != "UNKNOWN")
            if event["verb"] == "MOVE":
                move_total += 1
                move_resolved += int(label != "UNKNOWN")
            if label == "PRESSURE":
                pressure_targets += 1
            if label in NON_IDLE:
                if previous_nonidle is not None and previous_nonidle != label:
                    transitions[f"{previous_nonidle}->{label}"] += 1
                previous_nonidle = label

    joint_signatures = Counter()
    multiworker_turns = 0
    distinct_role_turns = 0
    for turn in range(1, decoded["usable_turns"] + 1):
        active = sorted(by_turn.get(turn, {}).items(), key=lambda item: ordinal.get(item[0], 999))
        signature = (int(turn in decoded["train_turns"]), *(label for _, label in active))
        joint_signatures["|".join(map(str, signature))] += 1
        nonidle = [label for _, label in active if label in NON_IDLE]
        if len(active) >= 2:
            multiworker_turns += 1
            distinct_role_turns += int(len(set(nonidle)) >= 2)

    return {
        "turns": decoded["usable_turns"],
        "unit_turns": total_unit_turns,
        "covered_unit_turns": covered_unit_turns,
        "direct_productive_turns": direct_total,
        "covered_direct_productive_turns": direct_covered,
        "move_turns": move_total,
        "resolved_move_turns": move_resolved,
        "labels": dict(labels),
        "labels_by_ordinal": {
            str(worker_ordinal): dict(counts)
            for worker_ordinal, counts in sorted(labels_by_ordinal.items())
        },
        "run_lengths": run_lengths(events_by_unit),
        "joint_signatures": dict(joint_signatures),
        "multiworker_turns": multiworker_turns,
        "distinct_role_multiworker_turns": distinct_role_turns,
        "job_transitions": dict(transitions),
        "pressure_labeled_turns": pressure_targets,
        "exclusive_plants": decoded["exclusive_plants"],
        "ambiguous_plants": decoded["ambiguous_plants"],
    }


def analyze_fetched_game(game: dict, record: dict) -> dict:
    parent = parent_analyze_game(game, record)
    player = 1 - int(record["candidate_arena_seat"])
    parser = corpus_parser()
    _map, _trolls, inv0, inv1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, _final = parser.extract_turns(game["frames"], inv0, inv1)
    _decoded_map, states, unknown_updates = decoded_states(game, trajectory)
    workers = analyze_players(states, trajectory)[player]["workers"]
    jobs = analyze_job_stream(states, trajectory, player, workers)
    return {
        "game_id": int(record["game_id"]),
        "partition": parent["partition"],
        "opponent": parent["opponent"],
        "player": player,
        "workers": len(workers),
        "jobs": jobs,
        "integrity": {
            **parent["integrity"],
            "job_decoded_turns": jobs["turns"],
            "unknown_diff_updates": unknown_updates,
        },
    }


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def top_k_coverage(counter: Counter, k: int) -> float | None:
    total = sum(counter.values())
    return ratio(sum(value for _, value in counter.most_common(k)), total)


def partition_summary(rows: list[dict]) -> dict:
    labels = Counter()
    labels_by_ordinal = defaultdict(Counter)
    joint = Counter()
    transitions = Counter()
    run_values = []
    totals = Counter()
    for row in rows:
        jobs = row["jobs"]
        labels.update(jobs["labels"])
        for ordinal, counts in jobs["labels_by_ordinal"].items():
            labels_by_ordinal[ordinal].update(counts)
        joint.update(jobs["joint_signatures"])
        transitions.update(jobs["job_transitions"])
        run_values.extend(jobs["run_lengths"])
        for key in (
            "turns",
            "unit_turns",
            "covered_unit_turns",
            "direct_productive_turns",
            "covered_direct_productive_turns",
            "move_turns",
            "resolved_move_turns",
            "multiworker_turns",
            "distinct_role_multiworker_turns",
            "pressure_labeled_turns",
            "ambiguous_plants",
        ):
            totals[key] += jobs[key]
    nonidle_total = sum(labels[label] for label in NON_IDLE)
    role_shares = {
        label: ratio(labels[label], nonidle_total) for label in sorted(NON_IDLE)
    }
    metrics = {
        "unit_turn_coverage": ratio(
            totals["covered_unit_turns"], totals["unit_turns"]
        ),
        "direct_productive_coverage": ratio(
            totals["covered_direct_productive_turns"],
            totals["direct_productive_turns"],
        ),
        "move_resolution_rate": ratio(
            totals["resolved_move_turns"], totals["move_turns"]
        ),
        "median_nonidle_run_length": statistics.median(run_values) if run_values else 0,
        "joint_signature_types": len(joint),
        "top8_joint_signature_coverage": top_k_coverage(joint, 8),
        "top16_joint_signature_coverage": top_k_coverage(joint, 16),
        "top32_joint_signature_coverage": top_k_coverage(joint, 32),
        "distinct_role_multiworker_rate": ratio(
            totals["distinct_role_multiworker_turns"], totals["multiworker_turns"]
        ),
        "role_shares_of_nonidle": role_shares,
        "pressure_or_mine_share": ratio(
            labels["PRESSURE"] + labels["MINE_BANK"], nonidle_total
        ),
    }
    checks = {
        "replay_integrity": all(
            row["integrity"]["trajectory_turns"]
            == row["integrity"]["decoded_turns"]
            == row["integrity"]["job_decoded_turns"]
            and row["integrity"]["unknown_diff_updates"] == 0
            and row["integrity"]["spawned_workers_matched"]
            and row["integrity"]["final_signature_exact"]
            for row in rows
        ),
        "direct_productive_coverage_100pct": metrics[
            "direct_productive_coverage"
        ]
        == 1.0,
        "unit_turn_coverage_at_least_95pct": metrics["unit_turn_coverage"] >= 0.95,
        "move_resolution_at_least_90pct": metrics["move_resolution_rate"] >= 0.90,
        "median_run_at_least_3": metrics["median_nonidle_run_length"] >= 3,
        "top32_joint_coverage_at_least_90pct": metrics[
            "top32_joint_signature_coverage"
        ]
        >= 0.90,
        "renew_share_at_least_15pct": role_shares["RENEW"] >= 0.15,
        "fell_share_at_least_15pct": role_shares["FELL_BANK"] >= 0.15,
        "pressure_or_mine_share_at_least_1pct": metrics[
            "pressure_or_mine_share"
        ]
        >= 0.01,
        "distinct_joint_roles_at_least_25pct": metrics[
            "distinct_role_multiworker_rate"
        ]
        >= 0.25,
    }
    return {
        "games": len(rows),
        "totals": dict(totals),
        "labels": dict(sorted(labels.items())),
        "labels_by_ordinal": {
            ordinal: dict(sorted(counts.items()))
            for ordinal, counts in sorted(labels_by_ordinal.items())
        },
        "run_length_summary": {
            "runs": len(run_values),
            "median": statistics.median(run_values) if run_values else None,
            "mean": statistics.mean(run_values) if run_values else None,
            "maximum": max(run_values) if run_values else None,
        },
        "joint_signatures": dict(joint.most_common()),
        "job_transitions": dict(transitions.most_common()),
        "metrics": metrics,
        "checks": checks,
        "passes": all(checks.values()),
    }


def analyze(rows: list[dict]) -> dict:
    if len(rows) != 21 or len({row["game_id"] for row in rows}) != 21:
        raise ValueError("expected exactly 21 unique frozen rich games")
    partitions = {
        name: partition_summary([row for row in rows if row["partition"] == name])
        for name in ("discovery", "confirmation")
    }
    if {name: value["games"] for name, value in partitions.items()} != {
        "discovery": 12,
        "confirmation": 9,
    }:
        raise ValueError("unexpected frozen 12/9 partition")
    passed = all(value["passes"] for value in partitions.values())
    return {
        "schema": 1,
        "scope": "D35a frozen rich-field joint persistent-job vocabulary audit",
        "games": len(rows),
        "partitions": partitions,
        "passes": passed,
        "decision": (
            "authorize_d35b_joint_job_executor_and_oracle"
            if passed
            else "reject_or_source_expand_job_vocabulary_before_executor"
        ),
        "rows": sorted(rows, key=lambda row: row["game_id"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cohort",
        type=Path,
        default=Path(
            "data/analysis/live-agent-6553250/"
            "rich-opponent-scheduler-transition-2026-07-19.json"
        ),
    )
    parser.add_argument(
        "--observed",
        type=Path,
        default=Path(
            "data/analysis/live-agent-6553250/"
            "field-continuation-phase21-candidate-160-observed.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/analysis/live-agent-6553250/"
            "d35a-joint-persistent-job-vocabulary-2026-07-20.json"
        ),
    )
    parser.add_argument("--jobs", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 24:
        raise SystemExit("--jobs must be between 1 and 24")

    cohort = json.loads(args.cohort.read_text())
    frozen_rows = cohort.get("rows") or []
    frozen_ids = [int(row["game_id"]) for row in frozen_rows]
    if len(frozen_ids) != 21 or len(set(frozen_ids)) != 21:
        raise ValueError("cohort must contain 21 unique game ids")
    observed = json.loads(args.observed.read_text())
    records = {
        int(record["game_id"]): record for record in observed.get("records") or []
    }
    selected = [records[game_id] for game_id in frozen_ids]
    frozen_partition = {
        int(row["game_id"]): row["partition"] for row in frozen_rows
    }

    def fetch(record: dict) -> dict:
        game_id = int(record["game_id"])
        game = arena.call("gameResult/findByGameId", [game_id, None])
        row = analyze_fetched_game(game, record)
        if row["partition"] != frozen_partition[game_id]:
            raise ValueError(f"partition drift for game {game_id}")
        return row

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        rows = list(executor.map(fetch, selected))
    report = analyze(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    compact = {
        "decision": report["decision"],
        "passes": report["passes"],
        "partitions": {
            name: {
                "passes": value["passes"],
                "metrics": value["metrics"],
                "failed_checks": [
                    check for check, passed in value["checks"].items() if not passed
                ],
            }
            for name, value in report["partitions"].items()
        },
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

