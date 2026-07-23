#!/usr/bin/env python3
"""Stress the D61p open analyzer on all consumed historical official replays."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import (  # noqa: E402
    analyze_open_game,
    atomic_write_new,
    sha256_file,
)


REPO = Path(__file__).resolve().parent.parent
GAMES = REPO / "data/processed/games.jsonl"
RAW = REPO / "data/raw/games"
TRAJECTORIES = REPO / "data/processed/trajectories"
PROTOCOL = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d61p-historical-analyzer-stress-protocol-2026-07-21.md"
)
EXPECTED_GAMES = 1_302


def read_games(path: Path = GAMES) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    rows.sort(key=lambda row: int(row["gameId"]))
    ids = [int(row["gameId"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("historical processed index contains duplicate game IDs")
    return rows


def analysis_ids(game: dict, resident_seat: int) -> tuple[list[dict], int, int]:
    """Return noncolliding player IDs while preserving every available platform ID."""

    game_id = int(game["gameId"])
    players = [dict(row) for row in game["players"]]
    by_seat = {int(row["index"]): row for row in players}
    if set(by_seat) != {0, 1}:
        raise ValueError(f"game {game_id} lacks seats 0 and 1")
    used = set()
    for seat in (0, 1):
        value = by_seat[seat].get("agentId")
        if value is None or int(value) in used:
            value = -(game_id * 2 + seat + 1)
            by_seat[seat]["agentId"] = value
        value = int(value)
        used.add(value)
    return players, int(by_seat[resident_seat]["agentId"]), int(
        by_seat[1 - resident_seat]["agentId"]
    )


def make_task(game: dict, raw_root: Path = RAW, trajectory_root: Path = TRAJECTORIES) -> dict:
    game_id = int(game["gameId"])
    resident_seat = game_id % 2
    players, resident_id, top_id = analysis_ids(game, resident_seat)
    open_game = dict(game)
    open_game["players"] = players
    open_game["split"] = "discovery"
    return {
        "analysis_task": {
            "game": open_game,
            "raw_path": str(raw_root / f"{game_id}.json"),
            "trajectory_path": str(trajectory_root / f"{game_id}.jsonl"),
            "resident_agent_id": resident_id,
            "top_source_ids": [top_id],
        },
        "resident_seat": resident_seat,
    }


def audit_task(task: dict) -> dict:
    game_id = int(task["analysis_task"]["game"]["gameId"])
    try:
        result = analyze_open_game(task["analysis_task"])
        resident = result["resident"]
        if resident is None:
            raise ValueError("pseudo-resident row was not reconstructed")
        if len(result["players"]) != 2:
            raise ValueError("both selected player schedulers were not reconstructed")
        schedules = [row["scheduler"] for row in result["players"]]
        crop_quality = resident["crop_attribution_quality"]
        return {
            "game_id": game_id,
            "success": True,
            "turns": result["integrity"]["trajectory_turns"],
            "decoded_turns": result["integrity"]["decoded_turns"],
            "unknown_diff_updates": result["integrity"]["unknown_diff_updates"],
            "final_inventory_exact": result["integrity"]["final_inventory_exact"],
            "resident_seat": task["resident_seat"],
            "player_schedulers": len(result["players"]),
            "final_workers": [row["final_worker_count"] for row in schedules],
            "successful_trains": [len(row["training_events"]) for row in schedules],
            "resident_crops_created": resident["own_crops_created"],
            "opponent_crops_attributed": resident["opponent_crop_summary"]["crops"],
            "crop_trajectory_turns": crop_quality["trajectory_turns"],
            "crop_decoded_turns": crop_quality["decoded_turns"],
            "crop_unknown_diff_updates": crop_quality["unknown_diff_updates"],
        }
    except Exception as error:  # noqa: BLE001 - preserve every audit failure
        return {
            "game_id": game_id,
            "success": False,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(limit=8),
            "resident_seat": task["resident_seat"],
        }


def rusage_cpu() -> float:
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def id_digest(game_ids: list[int]) -> str:
    payload = "\n".join(str(game_id) for game_id in game_ids).encode() + b"\n"
    return hashlib.sha256(payload).hexdigest()


def summarize(rows: list[dict], indexed_games: int, missing: list[dict], timing: dict) -> dict:
    successes = [row for row in rows if row["success"]]
    failures = [row for row in rows if not row["success"]]
    seats = Counter(row["resident_seat"] for row in successes)
    workers = Counter(
        worker for row in successes for worker in row.get("final_workers", [])
    )
    trains = Counter(
        count for row in successes for count in row.get("successful_trains", [])
    )
    gates = {
        "exactly_1302_indexed_games": indexed_games == EXPECTED_GAMES,
        "all_indexed_files_present": not missing,
        "all_1302_tasks_succeeded": len(successes) == EXPECTED_GAMES and not failures,
        "all_command_turn_counts_exact": all(
            row["turns"] == row["decoded_turns"] for row in successes
        ),
        "zero_unknown_diff_updates": all(
            row["unknown_diff_updates"] == 0 for row in successes
        ),
        "all_final_inventories_exact": all(
            row["final_inventory_exact"] for row in successes
        ),
        "both_player_schedulers_reconstructed": all(
            row["player_schedulers"] == 2 for row in successes
        ),
        "all_crop_streams_exact": all(
            row["crop_trajectory_turns"] == row["crop_decoded_turns"]
            and row["crop_unknown_diff_updates"] == 0
            for row in successes
        ),
        "both_pseudo_resident_seats_at_least_600": seats[0] >= 600
        and seats[1] >= 600,
    }
    return {
        "schema": "troll-farm-d61p-historical-analyzer-stress-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "infrastructure-only stress audit on consumed historical official replays; "
            "not field evidence or candidate selection"
        ),
        "inputs": {
            "games_index": str(GAMES.relative_to(REPO)),
            "games_index_sha256": sha256_file(GAMES),
            "game_ids_sha256": id_digest(
                [int(row["game_id"]) for row in rows]
                + [int(row["game_id"]) for row in missing]
            ),
            "protocol_sha256": sha256_file(PROTOCOL),
            "field_analyzer_sha256": sha256_file(
                REPO / "cgauto/analyze_d61p_field_snapshot.py"
            ),
            "audit_runner_sha256": sha256_file(Path(__file__)),
        },
        "counts": {
            "indexed_games": indexed_games,
            "tasks_run": len(rows),
            "successes": len(successes),
            "failures": len(failures),
            "missing_files": len(missing),
            "pseudo_resident_seats": dict(sorted(seats.items())),
            "resolved_turns": sum(row["turns"] for row in successes),
            "player_schedulers": sum(row["player_schedulers"] for row in successes),
            "crop_attributions": len(successes),
        },
        "timing": timing,
        "distributions": {
            "final_workers_per_player": dict(sorted(workers.items())),
            "successful_trains_per_player": dict(sorted(trains.items())),
            "resident_crops_created": dict(
                sorted(Counter(row["resident_crops_created"] for row in successes).items())
            ),
            "opponent_crops_attributed": dict(
                sorted(
                    Counter(
                        row["opponent_crops_attributed"] for row in successes
                    ).items()
                )
            ),
        },
        "gates": gates,
        "pass": all(gates.values()),
        "missing": missing,
        "failures": failures,
        "rows": rows,
        "decision": {
            "current_snapshot_analyzer_ready": all(gates.values()),
            "field_claim": False,
            "construct_candidate": False,
            "platform_action": False,
        },
    }


def run(output: Path, jobs: int) -> dict:
    if jobs < 1 or jobs > 32:
        raise ValueError("jobs must be between 1 and 32")
    games = read_games()
    tasks = []
    missing = []
    for game in games:
        task = make_task(game)
        absent = [
            path
            for path in (
                Path(task["analysis_task"]["raw_path"]),
                Path(task["analysis_task"]["trajectory_path"]),
            )
            if not path.is_file()
        ]
        if absent:
            missing.append(
                {
                    "game_id": int(game["gameId"]),
                    "paths": [str(path.relative_to(REPO)) for path in absent],
                }
            )
        else:
            tasks.append(task)

    wall_start = time.perf_counter()
    cpu_start = rusage_cpu()
    if jobs == 1:
        rows = [audit_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            rows = list(executor.map(audit_task, tasks, chunksize=2))
    cpu_seconds = rusage_cpu() - cpu_start
    wall_seconds = time.perf_counter() - wall_start
    rows.sort(key=lambda row: row["game_id"])
    timing = {
        "jobs": jobs,
        "wall_seconds": wall_seconds,
        "cpu_seconds_parent_plus_children": cpu_seconds,
        "effective_cores": cpu_seconds / wall_seconds if wall_seconds else None,
        "games_per_second": len(rows) / wall_seconds if wall_seconds else None,
    }
    report = summarize(rows, len(games), missing, timing)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = run(args.output, args.jobs)
    print(
        json.dumps(
            {
                "pass": report["pass"],
                "counts": report["counts"],
                "timing": report["timing"],
                "failed_gates": [
                    name for name, value in report["gates"].items() if not value
                ],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
