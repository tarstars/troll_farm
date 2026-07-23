#!/usr/bin/env python3
"""Repair D78 labels using exact referee-confirmed, unit-attributed CHOP effects."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import re

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import analyze_d78a_opponent_commitment as d78a  # noqa: E402
from cgauto.analyze_d61p_field_snapshot import (  # noqa: E402
    atomic_write_new,
    load_open_inputs,
    read_jsonl,
    sha256_file,
)
from cgauto.recent_resident_field_census import (  # noqa: E402
    crop_provenance,
    decoded_states,
)
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.top_player_opening_analysis import assigned_unit_commands  # noqa: E402


REPO = d78a.REPO
ANALYSIS = d78a.ANALYSIS
SNAPSHOT = d78a.SNAPSHOT
PROTOCOL = ANALYSIS / "d78b-opponent-commitment-label-repair-protocol-2026-07-21.md"
OUTPUT = ANALYSIS / "d78b-opponent-commitment-observability-result.json"
ROWS_OUTPUT = ANALYSIS / "d78b-opponent-commitment-rows.tsv"
SUMMARY_RE = re.compile(
    r"\$([01]): troll (\d+) (?:damaged a tree|collected \d+ WOOD)$"
)


def referee_chop_events(frames: list[dict]) -> list[tuple[int, int, int]]:
    """Return ``(turn, player, unit_id)`` for successful damage and fell effects."""

    events = []
    turn = 1
    for frame in frames[1:]:
        for line in (frame.get("summary") or "").splitlines():
            match = SUMMARY_RE.fullmatch(line)
            if match:
                events.append((turn, int(match.group(1)), int(match.group(2))))
        view = frame.get("view") or ""
        if frame.get("keyframe") and "{" in view:
            turn += 1
    return events


def confirmed_chop_cells(
    raw: dict,
    trajectory: list[dict],
    states: list[dict],
    player: int,
) -> dict[tuple[int, int], set[int]]:
    """Map target cells to turns with a referee-confirmed CHOP by ``player``."""

    result: dict[tuple[int, int], set[int]] = {}
    for turn, event_player, unit_id in referee_chop_events(raw["frames"]):
        if event_player != player or not 1 <= turn < len(states):
            continue
        before = states[turn - 1]
        units = [unit for unit in before["units"] if int(unit["player"]) == player]
        unit = next((unit for unit in units if int(unit["id"]) == unit_id), None)
        if unit is None:
            raise ValueError(f"D78b successful CHOP has no pre-action unit at turn {turn}")
        assigned = assigned_unit_commands(
            action_commands(trajectory[turn - 1].get(f"commands{player}")), units
        )
        command = assigned.get(unit_id, "")
        if command.split()[:1] != ["CHOP"]:
            raise ValueError(
                f"D78b successful CHOP lacks assigned CHOP command at turn {turn}"
            )
        cell = (int(unit["x"]), int(unit["y"]))
        if d78a.plant_at(before, cell) is None:
            raise ValueError(f"D78b successful CHOP targets no live plant at turn {turn}")
        result.setdefault(cell, set()).add(turn)
    return result


def extract_task(task: dict) -> dict:
    attempted = d78a.extract_task(task)
    if attempted["integrity"] is None:
        return attempted
    game = task["game"]
    resident_id = int(task["resident_agent_id"])
    resident_row = next(
        player
        for player in game["players"]
        if int(player.get("agentId", -1)) == resident_id
    )
    resident = int(resident_row["index"])
    attacker = 1 - resident
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    _, states, unknown = decoded_states(raw, trajectory)
    if unknown:
        raise ValueError(f"D78b unknown state updates in game {game['gameId']}")
    records, _ = crop_provenance(raw, trajectory, attacker)
    by_identity = {
        (tuple(int(value) for value in record["cell"]), ordinal): record
        for ordinal, record in enumerate(records)
    }
    attacker_confirmed = confirmed_chop_cells(raw, trajectory, states, attacker)
    resident_confirmed = confirmed_chop_cells(raw, trajectory, states, resident)
    attempted_attack = confirmed_attack = 0
    for ordinal, record in enumerate(records):
        cell = tuple(int(value) for value in record["cell"])
        old = {int(value) for value in record["our_chop_turns"]}
        new = attacker_confirmed.get(cell, set())
        relevant = {
            turn
            for turn in new
            if int(record["birth_turn"]) <= turn
            and (record["death_turn"] is None or turn <= int(record["death_turn"]))
        }
        if not relevant.issubset(old):
            raise ValueError(
                f"D78b confirmed CHOP is absent from attempted attribution in game {game['gameId']}"
            )
        attempted_attack += len(old)
        confirmed_attack += len(relevant)
        by_identity[(cell, ordinal)]["confirmed_attack_chops"] = sorted(relevant)
        by_identity[(cell, ordinal)]["confirmed_resident_chops"] = sorted(
            turn
            for turn in resident_confirmed.get(cell, set())
            if int(record["birth_turn"]) <= turn
            and (record["death_turn"] is None or turn <= int(record["death_turn"]))
        )

    for row in attempted["rows"]:
        cell = (int(row["cell_x"]), int(row["cell_y"]))
        record = by_identity[(cell, int(row["crop_ordinal"]))]
        turn = int(row["turn"])
        future = {
            value
            for value in record["confirmed_attack_chops"]
            if turn < value <= turn + d78a.HORIZON
        }
        resident_future = {
            value
            for value in record["confirmed_resident_chops"]
            if turn < value <= turn + d78a.HORIZON
        }
        death = record["death_turn"]
        row["label"] = int(bool(future))
        row["resident_future_chop"] = int(bool(resident_future))
        row["terminal_chop"] = int(
            death is not None
            and turn < int(death) <= turn + d78a.HORIZON
            and int(death) in future
        )
    attempted["integrity"].update(
        {
            "attempted_attack_chops": attempted_attack,
            "confirmed_attack_chops": confirmed_attack,
            "filtered_attack_chops": attempted_attack - confirmed_attack,
        }
    )
    return attempted


def build_report(loaded: dict, extracted: list[dict], rows_path: Path) -> dict:
    report = d78a.build_report(loaded, extracted, rows_path)
    integrity_rows = [item["integrity"] for item in extracted if item["integrity"]]
    attribution = {
        "attempted_attack_chops": sum(
            row["attempted_attack_chops"] for row in integrity_rows
        ),
        "confirmed_attack_chops": sum(
            row["confirmed_attack_chops"] for row in integrity_rows
        ),
        "filtered_attack_chops": sum(
            row["filtered_attack_chops"] for row in integrity_rows
        ),
    }
    attribution_checks = {
        "confirmed_is_nonzero": attribution["confirmed_attack_chops"] > 0,
        "repair_filters_at_least_one_attempt": attribution["filtered_attack_chops"] > 0,
        "confirmed_not_above_attempted": attribution["confirmed_attack_chops"]
        <= attribution["attempted_attack_chops"],
    }
    report["schema"] = "troll-farm-d78b-opponent-commitment-observability-v1"
    report["scope"] = (
        "open-only current-field behavior observability with referee-confirmed CHOP labels; "
        "no causal value or candidate claim"
    )
    report["inputs"]["d78a_attempt_analyzer"] = report["inputs"]["analyzer"]
    report["inputs"]["d78b_protocol"] = sha256_file(PROTOCOL)
    report["inputs"]["analyzer"] = sha256_file(Path(__file__))
    report["integrity"]["attribution"] = attribution
    report["integrity"]["attribution_checks"] = attribution_checks
    report["integrity"]["checks"].update(attribution_checks)
    if not all(attribution_checks.values()):
        report["gates"]["full_integrity_and_support"] = False
        report["gates"]["spatial"]["pass"] = False
        report["gates"]["history"]["pass"] = False
        report["decision"]["status"] = "attribution_integrity_failure"
        report["decision"]["next_controller_interface"] = "quarantine_or_insufficient"
    report["artifacts"]["rows"] = str(rows_path.relative_to(REPO))
    report["artifacts"]["rows_sha256"] = sha256_file(rows_path)
    return report


def analyze(snapshot: Path, output: Path, rows_output: Path, jobs: int) -> dict:
    if not 1 <= jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    loaded = load_open_inputs(snapshot)
    if loaded["snapshot_id"] != d78a.EXPECTED_SNAPSHOT:
        raise ValueError(f"D78b is frozen to snapshot {d78a.EXPECTED_SNAPSHOT}")
    tasks = [
        task
        for task in loaded["tasks"]
        if any(
            int(player.get("agentId", -1)) == d78a.EXPECTED_RESIDENT
            for player in task["game"]["players"]
        )
    ]
    if jobs == 1:
        extracted = [extract_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            extracted = list(executor.map(extract_task, tasks, chunksize=2))
    report = build_report(loaded, extracted, rows_output)
    atomic_write_new(output, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--rows-output", type=Path, default=ROWS_OUTPUT)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = analyze(args.snapshot, args.output, args.rows_output, args.jobs)
    print(
        json.dumps(
            {
                "attribution": report["integrity"]["attribution"],
                "rows": report["integrity"]["selected_rows"],
                "comparison": report["comparison"],
                "gates": report["gates"],
                "decision": report["decision"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
