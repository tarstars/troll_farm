#!/usr/bin/env python3
"""Audit the opening-to-capitalization phase order in frozen public replays."""

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
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    analyze_players,
    assigned_unit_commands,
    cargo_delta,
    player_commands,
)


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
EXPECTED_SNAPSHOT = "20260721T105508Z-d61p"
PROTOCOL = ANALYSIS / "d69a-opening-capitalization-window-audit-protocol-2026-07-21.md"
D63_REPORT = ANALYSIS / "d63a-agent-held-workforce-transition-2026-07-21.json"
FIELD_REPORT = ANALYSIS / "d61p-field-transfer-20260721T105508Z.json"
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
ITEM_INDEX = {item: index for index, item in enumerate(ITEMS)}
PARTITIONS = ("discovery", "validation")


def plant_map(state: dict) -> dict[tuple[int, int], dict]:
    return {(int(plant["x"]), int(plant["y"])): plant for plant in state["plants"]}


def reconstruct_generations(
    states: list[dict], trajectory: list[dict]
) -> tuple[list[dict], dict]:
    """Track every post-opening crop generation and the actions touching it."""

    usable_turns = min(len(states) - 1, len(trajectory))
    active: dict[tuple[int, int], dict] = {}
    records: list[dict] = []
    active_alignment_failures = 0
    births_without_matching_command = 0

    for turn in range(1, usable_turns + 1):
        before = states[turn - 1]
        after = states[turn]
        before_plants = plant_map(before)
        after_plants = plant_map(after)
        before_units = {int(unit["id"]): unit for unit in before["units"]}
        after_units = {int(unit["id"]): unit for unit in after["units"]}
        assigned: dict[int, dict[int, str]] = {}
        for player in (0, 1):
            units = [unit for unit in before["units"] if int(unit["player"]) == player]
            assigned[player] = assigned_unit_commands(
                player_commands(trajectory[turn - 1], player), units
            )

        for cell, record in list(active.items()):
            if cell not in before_plants:
                active_alignment_failures += 1
                record["death_turn"] = turn - 1
                active.pop(cell, None)
                continue
            for player in (0, 1):
                for unit_id, command in assigned[player].items():
                    unit = before_units.get(unit_id)
                    if unit is None or (int(unit["x"]), int(unit["y"])) != cell:
                        continue
                    fields = command.split()
                    verb = fields[0].upper() if fields else ""
                    if verb not in {"CHOP", "HARVEST"}:
                        continue
                    gained, _ = cargo_delta(unit, after_units.get(unit_id))
                    record["contacts"].append(
                        {
                            "turn": turn,
                            "player": player,
                            "unit_id": unit_id,
                            "verb": verb,
                            "fruit_gained": sum(gained[:4]),
                            "wood_gained": gained[ITEM_INDEX["WOOD"]],
                        }
                    )
            if cell not in after_plants:
                record["death_turn"] = turn
                active.pop(cell, None)

        for cell, plant in after_plants.items():
            if cell in before_plants:
                continue
            creator_units: dict[int, list[int]] = {0: [], 1: []}
            for player in (0, 1):
                for unit_id, command in assigned[player].items():
                    fields = command.split()
                    unit = before_units.get(unit_id)
                    if (
                        len(fields) >= 3
                        and fields[0].upper() == "PLANT"
                        and unit is not None
                        and (int(unit["x"]), int(unit["y"])) == cell
                        and fields[2].upper() == plant["type"]
                    ):
                        creator_units[player].append(unit_id)
            creators = [player for player in (0, 1) if creator_units[player]]
            births_without_matching_command += int(not creators)
            record = {
                "cell": list(cell),
                "type": plant["type"],
                "birth_turn": turn,
                "death_turn": None,
                "creators": creators,
                "creator_units": {
                    str(player): sorted(unit_ids)
                    for player, unit_ids in creator_units.items()
                    if unit_ids
                },
                "contacts": [],
            }
            records.append(record)
            active[cell] = record

    for record in active.values():
        record["survived_to_end"] = True
    return records, {
        "usable_turns": usable_turns,
        "crop_births": len(records),
        "sole_creator_births": sum(len(record["creators"]) == 1 for record in records),
        "ambiguous_creator_births": sum(
            len(record["creators"]) > 1 for record in records
        ),
        "births_without_matching_command": births_without_matching_command,
        "active_alignment_failures": active_alignment_failures,
    }


def first_or_none(values) -> int | None:
    values = list(values)
    return min(values) if values else None


def phase_metrics(
    records: list[dict], player: int, third_worker_turn: int | None, turns: int
) -> dict:
    """Compute phase milestones without looking past the relevant decision point."""

    opponent = 1 - player
    owned = [record for record in records if record["creators"] == [player]]
    first_owned = first_or_none(record["birth_turn"] for record in owned)
    receipts = sorted(
        contact["turn"]
        for record in owned
        for contact in record["contacts"]
        if contact["player"] == player
        and contact["verb"] == "HARVEST"
        and contact["fruit_gained"] > 0
    )
    first_receipt = first_or_none(receipts)
    first_reinvestment = (
        first_or_none(
            record["birth_turn"]
            for record in owned
            if record["birth_turn"] > first_receipt
        )
        if first_receipt is not None
        else None
    )
    opponent_contacts = sorted(
        contact["turn"]
        for record in owned
        for contact in record["contacts"]
        if contact["player"] == opponent
        and contact["verb"] in {"CHOP", "HARVEST"}
    )
    first_opponent_contact = first_or_none(opponent_contacts)

    cutoff = third_worker_turn - 1 if third_worker_turn is not None else min(100, turns)
    cutoff_owned = [record for record in owned if record["birth_turn"] <= cutoff]
    renewable_units = sum(
        contact["fruit_gained"]
        for record in cutoff_owned
        for contact in record["contacts"]
        if contact["player"] == player
        and contact["verb"] == "HARVEST"
        and contact["turn"] <= cutoff
    )
    ended = [
        record
        for record in cutoff_owned
        if record["death_turn"] is not None and record["death_turn"] <= cutoff
    ]
    opponent_destroyed = [
        record
        for record in ended
        if any(
            contact["player"] == opponent
            and contact["verb"] == "CHOP"
            and contact["turn"] == record["death_turn"]
            for contact in record["contacts"]
        )
    ]
    live_at_third = None
    if third_worker_turn is not None:
        # This is the state visible immediately before the TRAIN action resolves.
        live_at_third = sum(
            record["birth_turn"] < third_worker_turn
            and (
                record["death_turn"] is None
                or record["death_turn"] >= third_worker_turn
            )
            for record in owned
        )

    def before_third(turn: int | None) -> bool | None:
        if third_worker_turn is None:
            return None
        return turn is not None and turn < third_worker_turn

    return {
        "first_owned_crop_turn": first_owned,
        "first_renewable_receipt_turn": first_receipt,
        "first_reinvestment_turn": first_reinvestment,
        "first_opponent_contact_turn": first_opponent_contact,
        "owned_crop_before_third": before_third(first_owned),
        "renewable_receipt_before_third": before_third(first_receipt),
        "reinvestment_before_third": before_third(first_reinvestment),
        "live_owned_generations_at_third": live_at_third,
        "owned_crop_by_100": first_owned is not None and first_owned <= 100,
        "renewable_receipt_by_100": first_receipt is not None and first_receipt <= 100,
        "reinvestment_by_100": (
            first_reinvestment is not None and first_reinvestment <= 100
        ),
        "flow_cutoff_turn": cutoff,
        "owned_seeds_invested": len(cutoff_owned),
        "own_renewable_units_harvested": renewable_units,
        "owned_generations_destroyed": len(ended),
        "opponent_destroyed_owned_generations": len(opponent_destroyed),
        "renewable_flow_net": renewable_units - len(cutoff_owned),
        "owned_generations_total": len(owned),
    }


def extract_task(task: dict) -> list[dict]:
    game = task["game"]
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    _, states, unknown = decoded_states(raw, trajectory)
    expected_final = [
        list(game["per_player"][str(player)]["final_inv"]) for player in (0, 1)
    ]
    final_exact = states[-1]["inventories"] == expected_final
    analyses = analyze_players(states, trajectory)
    records, generation_integrity = reconstruct_generations(states, trajectory)
    game_players = {int(row["index"]): row for row in game["players"]}

    rows = []
    for target in task["targets"]:
        player = int(target["seat"])
        player_row = game_players[player]
        if int(player_row["agentId"]) != int(target["agent_id"]):
            raise ValueError(f"D63 identity mismatch in game {game['gameId']}")
        training_events = analyses[player]["training_events"]
        first_train = next(
            (int(event["turn"]) for event in training_events if event["ordinal"] == 1),
            None,
        )
        second_train = next(
            (int(event["turn"]) for event in training_events if event["ordinal"] == 2),
            None,
        )
        sole_owned = sum(record["creators"] == [player] for record in records)
        successful_plants = sum(
            int(value)
            for value in game["per_player"][str(player)]
            .get("planted_ok", {})
            .values()
        )
        attribution_rate = (
            sole_owned / successful_plants if successful_plants else 1.0
        )
        metrics = phase_metrics(records, player, second_train, len(trajectory))
        rows.append(
            {
                "game_id": int(game["gameId"]),
                "agent_id": int(target["agent_id"]),
                "agent_name": player_row.get("name"),
                "leaderboard_rank": player_row.get("localRank"),
                "seat": player,
                "partition": target["partition"],
                "turns": len(trajectory),
                "turn100_eligible": bool(target["turn100_eligible"]),
                "turn100_label": target["turn100_label"],
                "first_train_turn": first_train,
                "second_train_turn": second_train,
                "third_worker_turn": second_train,
                **metrics,
                "integrity": {
                    "trajectory_turns": len(trajectory),
                    "decoded_turns": len(states) - 1,
                    "unknown_diff_updates": unknown,
                    "final_inventory_exact": final_exact,
                    "d63_third_worker_turn_exact": (
                        second_train == target["third_worker_turn"]
                    ),
                    "successful_plant_events": successful_plants,
                    "sole_attributed_plant_generations": sole_owned,
                    "sole_attribution_rate": attribution_rate,
                    **generation_integrity,
                },
            }
        )
    return rows


def median_or_none(values) -> float | None:
    values = [value for value in values if value is not None]
    return statistics.median(values) if values else None


def mean_or_none(values) -> float | None:
    values = [value for value in values if value is not None]
    return statistics.mean(values) if values else None


def cohort_summary(rows: list[dict], mode: str) -> dict:
    if mode not in {"third", "through100"}:
        raise ValueError(f"unknown cohort mode {mode!r}")
    prefix = "before_third" if mode == "third" else "by_100"
    establish_field = (
        "owned_crop_before_third" if mode == "third" else "owned_crop_by_100"
    )
    receipt_field = (
        "renewable_receipt_before_third"
        if mode == "third"
        else "renewable_receipt_by_100"
    )
    reinvest_field = (
        "reinvestment_before_third" if mode == "third" else "reinvestment_by_100"
    )

    def count(field: str) -> int:
        return sum(bool(row[field]) for row in rows)

    size = len(rows)
    result = {
        "appearances": size,
        "agents": len({row["agent_id"] for row in rows}),
        f"owned_crop_{prefix}_count": count(establish_field),
        f"owned_crop_{prefix}_rate": count(establish_field) / size if size else None,
        f"renewable_receipt_{prefix}_count": count(receipt_field),
        f"renewable_receipt_{prefix}_rate": count(receipt_field) / size if size else None,
        f"reinvestment_{prefix}_count": count(reinvest_field),
        f"reinvestment_{prefix}_rate": count(reinvest_field) / size if size else None,
        "median_first_owned_crop_turn": median_or_none(
            row["first_owned_crop_turn"] for row in rows
        ),
        "median_first_renewable_receipt_turn": median_or_none(
            row["first_renewable_receipt_turn"] for row in rows
        ),
        "median_first_reinvestment_turn": median_or_none(
            row["first_reinvestment_turn"] for row in rows
        ),
        "median_first_opponent_contact_turn": median_or_none(
            row["first_opponent_contact_turn"] for row in rows
        ),
        "mean_owned_seeds_invested": mean_or_none(
            row["owned_seeds_invested"] for row in rows
        ),
        "mean_own_renewable_units_harvested": mean_or_none(
            row["own_renewable_units_harvested"] for row in rows
        ),
        "mean_owned_generations_destroyed": mean_or_none(
            row["owned_generations_destroyed"] for row in rows
        ),
        "mean_opponent_destroyed_owned_generations": mean_or_none(
            row["opponent_destroyed_owned_generations"] for row in rows
        ),
        "mean_renewable_flow_net": mean_or_none(
            row["renewable_flow_net"] for row in rows
        ),
        "median_renewable_flow_net": median_or_none(
            row["renewable_flow_net"] for row in rows
        ),
    }
    if mode == "third":
        result["median_live_owned_generations_at_third"] = median_or_none(
            row["live_owned_generations_at_third"] for row in rows
        )
        result["median_third_worker_turn"] = median_or_none(
            row["third_worker_turn"] for row in rows
        )
    return result


def partitioned_summary(rows: list[dict], mode: str) -> dict:
    return {
        "overall": cohort_summary(rows, mode),
        "partitions": {
            partition: cohort_summary(
                [row for row in rows if row["partition"] == partition], mode
            )
            for partition in PARTITIONS
        },
    }


def phase_gate(
    later_scaler: dict[str, list[dict]], eligible_non_scaler: dict[str, list[dict]]
) -> dict:
    by_partition = {}
    for partition in PARTITIONS:
        later = cohort_summary(later_scaler[partition], "third")
        non_scaler = cohort_summary(eligible_non_scaler[partition], "through100")
        checks = {
            "later_scaler_owned_crop_before_third_at_least_0_90": (
                (later["owned_crop_before_third_rate"] or 0.0) >= 0.90
            ),
            "later_scaler_renewable_receipt_before_third_at_least_0_70": (
                (later["renewable_receipt_before_third_rate"] or 0.0) >= 0.70
            ),
            "later_scaler_reinvestment_before_third_at_least_0_50": (
                (later["reinvestment_before_third_rate"] or 0.0) >= 0.50
            ),
            "later_scaler_median_live_owned_at_third_at_least_2": (
                (later["median_live_owned_generations_at_third"] or 0.0) >= 2
            ),
            "eligible_non_scaler_owned_crop_by_100_at_least_0_70": (
                (non_scaler["owned_crop_by_100_rate"] or 0.0) >= 0.70
            ),
        }
        by_partition[partition] = {
            "later_scaler_appearances": later["appearances"],
            "eligible_non_scaler_appearances": non_scaler["appearances"],
            "checks": checks,
            "pass": bool(later["appearances"] and non_scaler["appearances"])
            and all(checks.values()),
        }
    return {
        "partitions": by_partition,
        "pass": all(row["pass"] for row in by_partition.values()),
    }


def integrity_pass(integrity: dict) -> bool:
    return (
        integrity["qa_pass"]
        and integrity["d63_identity_exact"]
        and integrity["appearances"] == 200
        and integrity["agents"] == 20
        and integrity["ten_appearances_per_agent"]
        and integrity["all_turn_streams_exact"]
        and integrity["unknown_diff_updates"] == 0
        and integrity["all_final_inventories_exact"]
        and integrity["all_d63_third_worker_turns_exact"]
        and integrity["active_alignment_failures"] == 0
        and integrity["sole_plant_attribution_rate"] >= 0.95
        and not integrity["confirmation_products_read"]
    )


def build_report(loaded: dict, d63: dict, rows: list[dict]) -> dict:
    rows.sort(key=lambda row: (row["agent_id"], row["game_id"], row["seat"]))
    expected_keys = {
        (int(row["game_id"]), int(row["agent_id"]), int(row["seat"]))
        for row in d63["rows"]
    }
    actual_keys = {
        (row["game_id"], row["agent_id"], row["seat"]) for row in rows
    }
    per_agent = Counter(row["agent_id"] for row in rows)
    total_successful_plants = sum(
        row["integrity"]["successful_plant_events"] for row in rows
    )
    total_sole_attributed = sum(
        row["integrity"]["sole_attributed_plant_generations"] for row in rows
    )
    integrity = {
        "qa_pass": bool(loaded["qa"]["pass"]),
        "d63_identity_exact": actual_keys == expected_keys and len(rows) == len(expected_keys),
        "appearances": len(rows),
        "agents": len(per_agent),
        "appearances_per_agent": dict(sorted(per_agent.items())),
        "ten_appearances_per_agent": set(per_agent.values()) == {10},
        "all_turn_streams_exact": all(
            row["integrity"]["trajectory_turns"]
            == row["integrity"]["decoded_turns"]
            for row in rows
        ),
        "unknown_diff_updates": sum(
            row["integrity"]["unknown_diff_updates"] for row in rows
        ),
        "all_final_inventories_exact": all(
            row["integrity"]["final_inventory_exact"] for row in rows
        ),
        "all_d63_third_worker_turns_exact": all(
            row["integrity"]["d63_third_worker_turn_exact"] for row in rows
        ),
        "successful_top_player_plants": total_successful_plants,
        "sole_attributed_top_player_generations": total_sole_attributed,
        "sole_plant_attribution_rate": (
            total_sole_attributed / total_successful_plants
            if total_successful_plants
            else 1.0
        ),
        "births_without_matching_command": sum(
            row["integrity"]["births_without_matching_command"] for row in rows
        ),
        "active_alignment_failures": sum(
            row["integrity"]["active_alignment_failures"] for row in rows
        ),
        "confirmation_products_read": False,
    }

    third_worker = [row for row in rows if row["third_worker_turn"] is not None]
    later_scaler = [
        row
        for row in rows
        if row["turn100_eligible"] and int(row["turn100_label"] or 0) == 1
    ]
    eligible_non_scaler = [
        row
        for row in rows
        if row["turn100_eligible"] and int(row["turn100_label"] or 0) == 0
    ]
    later_by_partition = {
        partition: [row for row in later_scaler if row["partition"] == partition]
        for partition in PARTITIONS
    }
    non_scaler_by_partition = {
        partition: [
            row for row in eligible_non_scaler if row["partition"] == partition
        ]
        for partition in PARTITIONS
    }
    gate = phase_gate(later_by_partition, non_scaler_by_partition)
    valid = integrity_pass(integrity)
    establishment_common = all(
        details["checks"][
            "later_scaler_owned_crop_before_third_at_least_0_90"
        ]
        and details["checks"][
            "eligible_non_scaler_owned_crop_by_100_at_least_0_70"
        ]
        for details in gate["partitions"].values()
    )
    if not valid:
        next_representation = "repair_open_replay_generation_attribution"
        status = "invalid"
    elif gate["pass"]:
        next_representation = "recurrent_phase_conditioned_batch_option_preflight"
        status = "pass"
    elif establishment_common:
        next_representation = "closed_loop_policy_portfolio"
        status = "phase_order_fail"
    else:
        next_representation = "opening_establishment_policy"
        status = "establishment_separates"

    return {
        "schema": "troll-farm-d69a-opening-capitalization-window-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_id": loaded["snapshot_id"],
        "scope": (
            "outcome-blind crop-generation and capitalization-order audit on the "
            "exact D63 open appearances; no value, candidate, or platform claim"
        ),
        "definitions": {
            "owned_generation": "post-opening crop with exactly one creator player",
            "renewable_receipt": (
                "positive fruit cargo gained by HARVEST on that player's owned generation"
            ),
            "reinvestment": "a later-turn owned-generation birth after first receipt",
            "live_at_third": "owned generation present immediately before worker-three TRAIN",
            "destroyed": "owned generation absent by the flow cutoff for any cause",
            "opponent_destroyed": "destroyed with an opponent CHOP contact on its death turn",
            "flow_net": "renewable fruit units harvested minus owned generations planted",
        },
        "inputs": {
            "source_open_loader": loaded["input_hashes"],
            "protocol": sha256_file(PROTOCOL),
            "d63_report": sha256_file(D63_REPORT),
            "d61p_field_report": sha256_file(FIELD_REPORT),
            "analyzer": sha256_file(Path(__file__)),
        },
        "integrity": {**integrity, "pass": valid},
        "cohorts": {
            "all_third_worker": partitioned_summary(third_worker, "third"),
            "later_scaler": partitioned_summary(later_scaler, "third"),
            "eligible_non_scaler": partitioned_summary(
                eligible_non_scaler, "through100"
            ),
        },
        "gates": {"phase_order": gate},
        "decision": {
            "status": status,
            "establishment_common": establishment_common,
            "next_representation": next_representation,
            "mechanical_preflight_only": valid and gate["pass"],
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
        "rows": rows,
    }


def load_d63() -> dict:
    report = json.loads(D63_REPORT.read_text())
    if report.get("schema") != "troll-farm-d63a-agent-held-workforce-transition-v1":
        raise ValueError("unexpected D63 report schema")
    if report.get("snapshot_id") != EXPECTED_SNAPSHOT:
        raise ValueError("D63 report uses another snapshot")
    if report.get("integrity", {}).get("confirmation_products_read") is not False:
        raise ValueError("D63 report does not attest sealed confirmation")
    if len(report.get("rows") or []) != 200:
        raise ValueError("D63 report does not contain the frozen 200 appearances")
    return report


def analyze(snapshot: Path, output: Path, jobs: int) -> dict:
    if not 1 <= jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    loaded = load_open_inputs(snapshot)
    if loaded["snapshot_id"] != EXPECTED_SNAPSHOT:
        raise ValueError(f"D69a is frozen to snapshot {EXPECTED_SNAPSHOT}")
    d63 = load_d63()
    targets_by_game: dict[int, list[dict]] = {}
    for row in d63["rows"]:
        targets_by_game.setdefault(int(row["game_id"]), []).append(
            {
                "agent_id": int(row["agent_id"]),
                "seat": int(row["seat"]),
                "partition": row["partition"],
                "third_worker_turn": row["third_worker_turn"],
                "turn100_eligible": bool(row["turn100_eligible"]),
                "turn100_label": row["turn100_label"],
            }
        )
    tasks = []
    loaded_by_game = {int(task["game"]["gameId"]): task for task in loaded["tasks"]}
    for game_id, targets in sorted(targets_by_game.items()):
        if game_id not in loaded_by_game:
            raise ValueError(f"D63 game {game_id} is absent from open inputs")
        task = dict(loaded_by_game[game_id])
        task["targets"] = targets
        tasks.append(task)
    if jobs == 1:
        nested = [extract_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            nested = list(executor.map(extract_task, tasks, chunksize=2))
    rows = [row for group in nested for row in group]
    report = build_report(loaded, d63, rows)
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
    print(json.dumps({"integrity": report["integrity"], "gates": report["gates"], "decision": report["decision"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
