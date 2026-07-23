#!/usr/bin/env python3
"""Audit executable first-crop archetypes in frozen public top-policy replays."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import (  # noqa: E402
    atomic_write_new,
    load_open_inputs,
    read_jsonl,
    sha256_file,
)
from cgauto.analyze_d69a_opening_capitalization_window import (  # noqa: E402
    phase_metrics,
    reconstruct_generations,
)
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    adjacent,
    analyze_players,
    assigned_unit_commands,
    bfs,
    cargo_delta,
    player_commands,
    terrain,
)


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
EXPECTED_SNAPSHOT = "20260721T105508Z-d61p"
PROTOCOL = ANALYSIS / "d70a-opening-establishment-archetype-audit-protocol-2026-07-21.md"
D69_REPORT = ANALYSIS / "d69a-opening-capitalization-window-result.json"
PARTITIONS = ("discovery", "validation")
FRUITS = ("PLUM", "LEMON", "APPLE", "BANANA")
D40_PRODUCER_FRUIT_BILL = (5, 5, 2, 0)
SPECIES_RULES = ("largest_bank", "largest_d40_surplus", "banana_else_largest")


def action_history(states: list[dict], trajectory: list[dict]) -> dict[tuple[int, int], list[dict]]:
    result: dict[tuple[int, int], list[dict]] = {}
    usable = min(len(states) - 1, len(trajectory))
    for turn in range(1, usable + 1):
        before = states[turn - 1]
        after = states[turn]
        before_units = {int(unit["id"]): unit for unit in before["units"]}
        after_units = {int(unit["id"]): unit for unit in after["units"]}
        for player in (0, 1):
            units = [unit for unit in before["units"] if int(unit["player"]) == player]
            assigned = assigned_unit_commands(
                player_commands(trajectory[turn - 1], player), units
            )
            for unit_id, command in assigned.items():
                unit = before_units.get(unit_id)
                if unit is None:
                    continue
                fields = command.split()
                verb = fields[0].upper() if fields else ""
                gained, spent = cargo_delta(unit, after_units.get(unit_id))
                result.setdefault((player, unit_id), []).append(
                    {
                        "turn": turn,
                        "verb": verb,
                        "gained": gained,
                        "spent": spent,
                        "cell": [int(unit["x"]), int(unit["y"])],
                    }
                )
    return result


def largest_index(values: list[int] | tuple[int, ...], positive_only: bool = True) -> int | None:
    candidates = [
        index for index, value in enumerate(values[:4]) if not positive_only or value > 0
    ]
    return min(candidates, key=lambda index: (-values[index], index)) if candidates else None


def species_rule_choices(bank: list[int]) -> dict[str, int | None]:
    largest = largest_index(bank)
    surplus = [bank[index] - D40_PRODUCER_FRUIT_BILL[index] for index in range(4)]
    positive_surplus = largest_index(surplus)
    return {
        "largest_bank": largest,
        "largest_d40_surplus": (
            positive_surplus if positive_surplus is not None else largest
        ),
        "banana_else_largest": 3 if bank[3] > 0 else largest,
    }


def transaction_details(
    decoded_map: dict,
    states: list[dict],
    records: list[dict],
    history: dict[tuple[int, int], list[dict]],
    analysis: dict,
    player: int,
    first_train_turn: int | None,
    third_worker_turn: int | None,
) -> dict | None:
    owned = sorted(
        (record for record in records if record["creators"] == [player]),
        key=lambda record: (record["birth_turn"], record["cell"]),
    )
    if not owned:
        return None
    record = owned[0]
    birth = int(record["birth_turn"])
    kind = FRUITS.index(record["type"])
    creator_ids = record["creator_units"].get(str(player), [])
    creator_id = creator_ids[0] if len(creator_ids) == 1 else None
    metadata = {int(worker["unit_id"]): worker for worker in analysis["workers"]}
    creator = metadata.get(creator_id) if creator_id is not None else None

    acquisition = None
    if creator_id is not None:
        acquisition = next(
            (
                event
                for event in reversed(history.get((player, creator_id), []))
                if event["turn"] < birth and event["gained"][kind] > 0
            ),
            None,
        )
    if acquisition is None:
        seed_provenance = "unresolved"
        choice_state_turn = birth - 1
    elif acquisition["verb"] == "PICK":
        seed_provenance = "bank_pick"
        choice_state_turn = acquisition["turn"] - 1
    elif acquisition["verb"] == "HARVEST":
        seed_provenance = "board_harvest"
        choice_state_turn = acquisition["turn"] - 1
    else:
        seed_provenance = "unresolved"
        choice_state_turn = acquisition["turn"] - 1
    choice_state_turn = max(0, min(choice_state_turn, len(states) - 1))
    bank = [int(value) for value in states[choice_state_turn]["inventories"][player]]
    choices = species_rule_choices(bank)

    if first_train_turn is None or birth < first_train_turn:
        relation = "crop_before_worker2"
    elif birth == first_train_turn:
        relation = "same_turn"
    else:
        relation = "worker2_before_crop"

    board = terrain(decoded_map)
    cell = tuple(record["cell"])
    own_doors = [door for door in adjacent(board["shacks"][player]) if door in board["walkable"]]
    opponent_doors = [
        door for door in adjacent(board["shacks"][1 - player]) if door in board["walkable"]
    ]
    own_distance = bfs(board["walkable"], own_doors).get(cell)
    opponent_distance = bfs(board["walkable"], opponent_doors).get(cell)
    player_favored = (
        own_distance is not None
        and opponent_distance is not None
        and own_distance < opponent_distance
    )
    broad_d40_domain = player_favored and own_distance <= 4
    water_adjacent = any(neighbor in board["water"] for neighbor in adjacent(cell))

    own_contacts = [
        contact
        for contact in record["contacts"]
        if contact["player"] == player
        and contact["verb"] == "HARVEST"
        and contact["fruit_gained"] > 0
    ]
    opponent_contacts = [
        contact
        for contact in record["contacts"]
        if contact["player"] == 1 - player
        and contact["verb"] in {"CHOP", "HARVEST"}
    ]
    first_receipt = min((contact["turn"] for contact in own_contacts), default=None)
    first_opponent_contact = min(
        (contact["turn"] for contact in opponent_contacts), default=None
    )
    receipt_before_third = (
        first_receipt is not None
        and third_worker_turn is not None
        and first_receipt < third_worker_turn
    )
    before_birth_workers = sum(
        int(unit["player"]) == player for unit in states[birth - 1]["units"]
    )
    return {
        "birth_turn": birth,
        "early_by_turn_10": birth <= 10,
        "species": record["type"],
        "creator_unit_id": creator_id,
        "creator_unit_ambiguous": len(creator_ids) != 1,
        "creator_worker_ordinal": creator.get("ordinal") if creator else None,
        "creator_worker_spec": creator.get("spec") if creator else None,
        "own_workers_before_birth": before_birth_workers,
        "worker_two_relation": relation,
        "seed_provenance": seed_provenance,
        "seed_acquisition_turn": acquisition["turn"] if acquisition else None,
        "seed_acquisition_verb": acquisition["verb"] if acquisition else None,
        "choice_state_turn": choice_state_turn,
        "choice_bank": bank,
        "species_rule_choices": {
            rule: FRUITS[index] if index is not None else None
            for rule, index in choices.items()
        },
        "species_rule_matches": {
            rule: index == kind for rule, index in choices.items()
        },
        "cell": list(cell),
        "own_shack_door_distance": own_distance,
        "opponent_shack_door_distance": opponent_distance,
        "player_favored": player_favored,
        "water_adjacent": water_adjacent,
        "broad_d40_source_domain": broad_d40_domain,
        "death_turn": record["death_turn"],
        "first_generation_receipt_turn": first_receipt,
        "first_generation_receipt_units": sum(
            contact["fruit_gained"] for contact in own_contacts
        ),
        "first_opponent_contact_turn": first_opponent_contact,
        "receipt_before_worker_three": receipt_before_third,
        "survived_to_first_receipt": first_receipt is not None,
    }


def extract_task(task: dict) -> list[dict]:
    game = task["game"]
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    decoded_map, states, unknown = decoded_states(raw, trajectory)
    expected_final = [
        list(game["per_player"][str(player)]["final_inv"]) for player in (0, 1)
    ]
    analyses = analyze_players(states, trajectory)
    records, generation_integrity = reconstruct_generations(states, trajectory)
    history = action_history(states, trajectory)
    game_players = {int(row["index"]): row for row in game["players"]}
    result = []
    for target in task["targets"]:
        player = int(target["seat"])
        player_row = game_players[player]
        if int(player_row["agentId"]) != int(target["agent_id"]):
            raise ValueError(f"D69 identity mismatch in game {game['gameId']}")
        training = analyses[player]["training_events"]
        first_train = next(
            (int(event["turn"]) for event in training if event["ordinal"] == 1), None
        )
        second_train = next(
            (int(event["turn"]) for event in training if event["ordinal"] == 2), None
        )
        phase = phase_metrics(records, player, second_train, len(trajectory))
        transaction = transaction_details(
            decoded_map,
            states,
            records,
            history,
            analyses[player],
            player,
            first_train,
            second_train,
        )
        milestone_exact = all(
            phase[field] == target[field]
            for field in (
                "first_owned_crop_turn",
                "first_renewable_receipt_turn",
                "first_reinvestment_turn",
                "first_opponent_contact_turn",
            )
        )
        result.append(
            {
                "game_id": int(game["gameId"]),
                "agent_id": int(target["agent_id"]),
                "agent_name": player_row.get("name"),
                "seat": player,
                "partition": target["partition"],
                "cohort": target["cohort"],
                "turns": len(trajectory),
                "first_train_turn": first_train,
                "second_train_turn": second_train,
                "transaction": transaction,
                "integrity": {
                    "trajectory_turns": len(trajectory),
                    "decoded_turns": len(states) - 1,
                    "unknown_diff_updates": unknown,
                    "final_inventory_exact": states[-1]["inventories"] == expected_final,
                    "first_train_exact": first_train == target["first_train_turn"],
                    "second_train_exact": second_train == target["second_train_turn"],
                    "d69_milestones_exact": milestone_exact,
                    **generation_integrity,
                },
            }
        )
    return result


def rate(rows: list[dict], predicate) -> float | None:
    return sum(bool(predicate(row)) for row in rows) / len(rows) if rows else None


def median_or_none(values) -> float | None:
    values = [value for value in values if value is not None]
    return statistics.median(values) if values else None


def transaction_summary(rows: list[dict]) -> dict:
    transactions = [row["transaction"] for row in rows if row["transaction"] is not None]
    early = [transaction for transaction in transactions if transaction["early_by_turn_10"]]
    return {
        "appearances": len(rows),
        "agents": len({row["agent_id"] for row in rows}),
        "with_owned_crop": len(transactions),
        "early_by_turn_10": len(early),
        "early_by_turn_10_rate": len(early) / len(rows) if rows else None,
        "median_birth_turn": median_or_none(
            transaction["birth_turn"] for transaction in transactions
        ),
        "worker_two_relations": dict(
            sorted(Counter(t["worker_two_relation"] for t in transactions).items())
        ),
        "seed_provenance": dict(
            sorted(Counter(t["seed_provenance"] for t in transactions).items())
        ),
        "species": dict(sorted(Counter(t["species"] for t in transactions).items())),
        "creator_worker_ordinals": dict(
            sorted(Counter(str(t["creator_worker_ordinal"]) for t in transactions).items())
        ),
        "player_favored_rate": rate(transactions, lambda t: t["player_favored"]),
        "water_adjacent_rate": rate(transactions, lambda t: t["water_adjacent"]),
        "broad_d40_source_domain_rate": rate(
            transactions, lambda t: t["broad_d40_source_domain"]
        ),
        "first_generation_receipt_rate": rate(
            transactions, lambda t: t["survived_to_first_receipt"]
        ),
        "first_generation_receipt_before_worker_three_rate": rate(
            transactions, lambda t: t["receipt_before_worker_three"]
        ),
        "median_first_generation_receipt_units": median_or_none(
            t["first_generation_receipt_units"] for t in transactions
        ),
        "species_rule_match_rates": {
            rule: rate(transactions, lambda t, rule=rule: t["species_rule_matches"][rule])
            for rule in SPECIES_RULES
        },
    }


def signature_label(transaction: dict) -> str:
    return f"{transaction['worker_two_relation']}+{transaction['seed_provenance']}"


def signature_report(rows: list[dict], label: str) -> dict:
    selected = [
        row
        for row in rows
        if row["transaction"] is not None
        and row["transaction"]["early_by_turn_10"]
        and signature_label(row["transaction"]) == label
    ]
    partitions = {}
    for partition in PARTITIONS:
        part = [row for row in selected if row["partition"] == partition]
        partitions[partition] = {
            "appearances": len(part),
            "agents": len({row["agent_id"] for row in part}),
            "receipt_before_worker_three_rate": rate(
                part, lambda row: row["transaction"]["receipt_before_worker_three"]
            ),
            "broad_d40_source_domain_rate": rate(
                part, lambda row: row["transaction"]["broad_d40_source_domain"]
            ),
            "species": dict(
                sorted(Counter(row["transaction"]["species"] for row in part).items())
            ),
        }
    checks = {
        "discovery_at_least_3": partitions["discovery"]["appearances"] >= 3,
        "validation_at_least_5": partitions["validation"]["appearances"] >= 5,
        "two_agents_each_partition": all(
            partitions[partition]["agents"] >= 2 for partition in PARTITIONS
        ),
        "receipt_rate_at_least_0_70_each_partition": all(
            (partitions[partition]["receipt_before_worker_three_rate"] or 0.0) >= 0.70
            for partition in PARTITIONS
        ),
        "d40_domain_rate_at_least_0_70_each_partition": all(
            (partitions[partition]["broad_d40_source_domain_rate"] or 0.0) >= 0.70
            for partition in PARTITIONS
        ),
    }
    return {
        "label": label,
        "appearances": len(selected),
        "agents": len({row["agent_id"] for row in selected}),
        "partitions": partitions,
        "checks": checks,
        "eligible": all(checks.values()),
    }


def archetype_gate(later_rows: list[dict]) -> dict:
    labels = sorted(
        {
            signature_label(row["transaction"])
            for row in later_rows
            if row["transaction"] is not None
            and row["transaction"]["early_by_turn_10"]
        }
    )
    reports = [signature_report(later_rows, label) for label in labels]
    reports.sort(
        key=lambda report: (
            -min(
                report["partitions"][partition]["appearances"]
                for partition in PARTITIONS
            ),
            -report["appearances"],
            report["label"],
        )
    )
    nominated = [report for report in reports if report["eligible"]][:2]
    nominated_labels = {report["label"] for report in nominated}
    nominated_rows = [
        row
        for row in later_rows
        if row["transaction"] is not None
        and row["transaction"]["early_by_turn_10"]
        and signature_label(row["transaction"]) in nominated_labels
    ]
    coverage = {
        partition: {
            "covered": sum(row["partition"] == partition for row in nominated_rows),
            "total": sum(row["partition"] == partition for row in later_rows),
        }
        for partition in PARTITIONS
    }
    for row in coverage.values():
        row["rate"] = row["covered"] / row["total"] if row["total"] else None
    coverage_pass = bool(nominated) and all(
        (coverage[partition]["rate"] or 0.0) >= 0.60 for partition in PARTITIONS
    )

    species = []
    for rule in SPECIES_RULES:
        matches = {
            partition: {
                "matches": sum(
                    row["partition"] == partition
                    and row["transaction"]["species_rule_matches"][rule]
                    for row in nominated_rows
                ),
                "total": sum(row["partition"] == partition for row in nominated_rows),
            }
            for partition in PARTITIONS
        }
        for value in matches.values():
            value["rate"] = (
                value["matches"] / value["total"] if value["total"] else None
            )
        species.append(
            {
                "rule": rule,
                "partitions": matches,
                "total_matches": sum(value["matches"] for value in matches.values()),
                "eligible": bool(nominated_rows)
                and all(
                    (matches[partition]["rate"] or 0.0) >= 0.50
                    for partition in PARTITIONS
                ),
            }
        )
    species.sort(
        key=lambda report: (
            -min(
                report["partitions"][partition]["rate"] or 0.0
                for partition in PARTITIONS
            ),
            -report["total_matches"],
            report["rule"],
        )
    )
    selected_species = next(
        (report for report in species if report["eligible"]), None
    )
    return {
        "catalog": reports,
        "nominated_signatures": [report["label"] for report in nominated],
        "coverage": coverage,
        "coverage_pass": coverage_pass,
        "species_rules": species,
        "selected_species_rule": selected_species["rule"] if selected_species else None,
        "species_rule_pass": selected_species is not None,
        "pass": coverage_pass and selected_species is not None,
    }


def build_report(loaded: dict, d69: dict, rows: list[dict]) -> dict:
    rows.sort(key=lambda row: (row["agent_id"], row["game_id"], row["seat"]))
    expected_keys = {
        (row["game_id"], row["agent_id"], row["seat"])
        for row in d69["rows"]
        if row["turn100_eligible"]
    }
    actual_keys = {(row["game_id"], row["agent_id"], row["seat"]) for row in rows}
    integrity = {
        "qa_pass": bool(loaded["qa"]["pass"]),
        "d69_identity_exact": actual_keys == expected_keys and len(rows) == len(expected_keys),
        "appearances": len(rows),
        "all_turn_streams_exact": all(
            row["integrity"]["trajectory_turns"] == row["integrity"]["decoded_turns"]
            for row in rows
        ),
        "unknown_diff_updates": sum(
            row["integrity"]["unknown_diff_updates"] for row in rows
        ),
        "all_final_inventories_exact": all(
            row["integrity"]["final_inventory_exact"] for row in rows
        ),
        "all_train_turns_exact": all(
            row["integrity"]["first_train_exact"]
            and row["integrity"]["second_train_exact"]
            for row in rows
        ),
        "all_d69_milestones_exact": all(
            row["integrity"]["d69_milestones_exact"] for row in rows
        ),
        "active_alignment_failures": sum(
            row["integrity"]["active_alignment_failures"] for row in rows
        ),
        "confirmation_products_read": False,
        "outcomes_read": False,
    }
    integrity["pass"] = (
        integrity["qa_pass"]
        and integrity["d69_identity_exact"]
        and integrity["appearances"] == 150
        and integrity["all_turn_streams_exact"]
        and integrity["unknown_diff_updates"] == 0
        and integrity["all_final_inventories_exact"]
        and integrity["all_train_turns_exact"]
        and integrity["all_d69_milestones_exact"]
        and integrity["active_alignment_failures"] == 0
        and not integrity["confirmation_products_read"]
        and not integrity["outcomes_read"]
    )

    later = [row for row in rows if row["cohort"] == "later_scaler"]
    non_scaler = [row for row in rows if row["cohort"] == "eligible_non_scaler"]
    gate = archetype_gate(later)
    if not integrity["pass"]:
        status = "invalid"
        next_experiment = "repair_opening_transaction_attribution"
    elif gate["pass"]:
        status = "pass"
        next_experiment = "fresh_bounded_opening_prefix_causal_preflight"
    elif gate["coverage_pass"]:
        status = "species_rule_fail"
        next_experiment = "closed_loop_or_enumerated_opening_species_policy"
    else:
        status = "transaction_coverage_fail"
        next_experiment = "closed_loop_opening_policy_portfolio"
    return {
        "schema": "troll-farm-d70a-opening-establishment-archetype-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_id": loaded["snapshot_id"],
        "scope": (
            "outcome-blind executable first-crop archetype audit on exact D69 open rows; "
            "no value, candidate, or platform claim"
        ),
        "inputs": {
            "source_open_loader": loaded["input_hashes"],
            "protocol": sha256_file(PROTOCOL),
            "d69_report": sha256_file(D69_REPORT),
            "analyzer": sha256_file(Path(__file__)),
        },
        "integrity": integrity,
        "cohorts": {
            "later_scaler": {
                "overall": transaction_summary(later),
                "partitions": {
                    partition: transaction_summary(
                        [row for row in later if row["partition"] == partition]
                    )
                    for partition in PARTITIONS
                },
            },
            "eligible_non_scaler": {
                "overall": transaction_summary(non_scaler),
                "partitions": {
                    partition: transaction_summary(
                        [row for row in non_scaler if row["partition"] == partition]
                    )
                    for partition in PARTITIONS
                },
            },
        },
        "gates": {"archetype": gate},
        "decision": {
            "status": status,
            "next_experiment": next_experiment,
            "nominated_signatures": gate["nominated_signatures"] if integrity["pass"] else [],
            "selected_species_rule": (
                gate["selected_species_rule"] if integrity["pass"] else None
            ),
            "construct_candidate": False,
            "train_policy": False,
            "open_confirmation": False,
            "platform_action": False,
        },
        "rows": rows,
    }


def load_d69() -> dict:
    report = json.loads(D69_REPORT.read_text())
    if report.get("schema") != "troll-farm-d69a-opening-capitalization-window-v1":
        raise ValueError("unexpected D69 report schema")
    if report.get("snapshot_id") != EXPECTED_SNAPSHOT:
        raise ValueError("D69 report uses another snapshot")
    if not report.get("integrity", {}).get("pass"):
        raise ValueError("D69 integrity did not pass")
    return report


def analyze(snapshot: Path, output: Path, jobs: int) -> dict:
    if not 1 <= jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    loaded = load_open_inputs(snapshot)
    if loaded["snapshot_id"] != EXPECTED_SNAPSHOT:
        raise ValueError(f"D70a is frozen to snapshot {EXPECTED_SNAPSHOT}")
    d69 = load_d69()
    targets_by_game: dict[int, list[dict]] = {}
    for row in d69["rows"]:
        if not row["turn100_eligible"]:
            continue
        cohort = "later_scaler" if int(row["turn100_label"] or 0) == 1 else "eligible_non_scaler"
        targets_by_game.setdefault(int(row["game_id"]), []).append(
            {
                "agent_id": int(row["agent_id"]),
                "seat": int(row["seat"]),
                "partition": row["partition"],
                "cohort": cohort,
                "first_train_turn": row["first_train_turn"],
                "second_train_turn": row["second_train_turn"],
                "first_owned_crop_turn": row["first_owned_crop_turn"],
                "first_renewable_receipt_turn": row["first_renewable_receipt_turn"],
                "first_reinvestment_turn": row["first_reinvestment_turn"],
                "first_opponent_contact_turn": row["first_opponent_contact_turn"],
            }
        )
    loaded_by_game = {int(task["game"]["gameId"]): task for task in loaded["tasks"]}
    tasks = []
    for game_id, targets in sorted(targets_by_game.items()):
        if game_id not in loaded_by_game:
            raise ValueError(f"D69 game {game_id} is absent from open inputs")
        task = dict(loaded_by_game[game_id])
        task["targets"] = targets
        tasks.append(task)
    if jobs == 1:
        nested = [extract_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            nested = list(executor.map(extract_task, tasks, chunksize=2))
    rows = [row for group in nested for row in group]
    report = build_report(loaded, d69, rows)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(args.snapshot, args.output, args.jobs)
    print(
        json.dumps(
            {
                "integrity": report["integrity"],
                "gates": report["gates"],
                "decision": report["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
