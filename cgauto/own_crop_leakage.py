#!/usr/bin/env python3
"""Measure opponent capture of exact resident-created crops in official replays."""

from __future__ import annotations

import argparse
from collections import Counter
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
from cgauto.recent_resident_field_census import (
    corpus_parser,
    crop_provenance,
    current_player,
)


EXPECTED_AGENT = 6560240


def geometry_class(resident_distance: int | None, opponent_distance: int | None) -> str:
    if resident_distance is None or opponent_distance is None:
        return "unknown"
    difference = resident_distance - opponent_distance
    if difference <= -2:
        return "resident_favored"
    if difference >= 2:
        return "opponent_favored"
    return "contested"


def invert_record(record: dict) -> dict:
    resident_distance = record["opponent_shack_distance"]
    opponent_distance = record["our_shack_distance"]
    return {
        "cell": record["cell"],
        "type": record["type"],
        "birth_turn": record["birth_turn"],
        "death_turn": record["death_turn"],
        "survived_to_end": record.get("survived_to_end", False),
        "resident_eta_at_birth": record["opponent_eta_at_birth"],
        "opponent_eta_at_birth": record["our_eta_at_birth"],
        "resident_shack_distance": resident_distance,
        "opponent_shack_distance": opponent_distance,
        "geometry": geometry_class(resident_distance, opponent_distance),
        "resident_chop_turns": record["opponent_chop_turns"],
        "resident_harvest_turns": record["opponent_harvest_turns"],
        "opponent_chop_turns": record["our_chop_turns"],
        "opponent_harvest_turns": record["our_harvest_turns"],
        "resident_wood_collected": int(record["opponent_wood_collected"]),
        "opponent_wood_collected": int(record["our_wood_collected"]),
        "resident_fruit_harvested": int(record["opponent_fruit_harvested"]),
        "opponent_fruit_harvested": int(record["our_fruit_harvested"]),
    }


def analyze_game(game: dict, census_row: dict) -> dict:
    game_id = int(census_row["game_id"])
    if int(game.get("gameId") or -1) != game_id:
        raise ValueError(f"requested {game_id}, received {game.get('gameId')}")
    me = current_player(game)
    if me is None:
        raise ValueError(f"resident user missing from game {game_id}")
    agents = game.get("agents") or []
    if int(agents[me].get("agentId") or -1) != EXPECTED_AGENT:
        raise ValueError(f"game {game_id} is not exact agent {EXPECTED_AGENT}")
    parser = corpus_parser()
    _map_data, _units, inv0, inv1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, _final_inventory = parser.extract_turns(game["frames"], inv0, inv1)
    # crop_provenance reports crops exclusively created by 1-passed_player.
    # Passing the arena opponent therefore selects resident-created crops and
    # names their work as the returned record's "opponent" fields.
    relative, quality = crop_provenance(game, trajectory, 1 - me)
    records = [invert_record(record) for record in relative]
    return {
        "game_id": game_id,
        "opponent": census_row["opponent"],
        "margin": int(census_row["margin"]),
        "catastrophic": int(census_row["margin"]) <= -100,
        "quality": quality,
        "resident_crops": len(records),
        "records": records,
    }


def cohort(row: dict) -> str:
    if row["margin"] > 0:
        return "wins"
    if row["margin"] <= -100:
        return "catastrophic_losses"
    return "ordinary_losses"


def summarize(rows: list[dict]) -> dict:
    records = [record for row in rows for record in row["records"]]
    resident_wood = sum(record["resident_wood_collected"] for record in records)
    opponent_wood = sum(record["opponent_wood_collected"] for record in records)
    resident_fruit = sum(record["resident_fruit_harvested"] for record in records)
    opponent_fruit = sum(record["opponent_fruit_harvested"] for record in records)
    total_wood = resident_wood + opponent_wood
    geometry = {}
    for name in ("resident_favored", "contested", "opponent_favored", "unknown"):
        selected = [record for record in records if record["geometry"] == name]
        own = sum(record["resident_wood_collected"] for record in selected)
        theirs = sum(record["opponent_wood_collected"] for record in selected)
        geometry[name] = {
            "crops": len(selected),
            "resident_wood": own,
            "opponent_wood": theirs,
            "opponent_wood_share": theirs / (own + theirs) if own + theirs else 0.0,
            "opponent_contacted_crops": sum(
                bool(record["opponent_chop_turns"] or record["opponent_harvest_turns"])
                for record in selected
            ),
        }
    nonresident_favored_wood = (
        geometry["contested"]["opponent_wood"]
        + geometry["opponent_favored"]["opponent_wood"]
        + geometry["unknown"]["opponent_wood"]
    )
    capture_games = [
        row
        for row in rows
        if any(record["opponent_wood_collected"] > 0 for record in row["records"])
    ]
    return {
        "games": len(rows),
        "crops": len(records),
        "crop_types": dict(sorted(Counter(record["type"] for record in records).items())),
        "resident_wood": resident_wood,
        "opponent_wood": opponent_wood,
        "opponent_wood_per_game": opponent_wood / len(rows) if rows else None,
        "opponent_wood_share": opponent_wood / total_wood if total_wood else 0.0,
        "resident_fruit": resident_fruit,
        "opponent_fruit": opponent_fruit,
        "opponent_capture_games": len(capture_games),
        "opponent_capture_game_rate": len(capture_games) / len(rows) if rows else None,
        "opponent_contacted_crops": sum(
            bool(record["opponent_chop_turns"] or record["opponent_harvest_turns"])
            for record in records
        ),
        "geometry": geometry,
        "nonresident_favored_share_of_leaked_wood": (
            nonresident_favored_wood / opponent_wood if opponent_wood else 0.0
        ),
    }


def analyze(rows: list[dict], fetch_failures: list[dict]) -> dict:
    if len({int(row["game_id"]) for row in rows}) != len(rows):
        raise ValueError("duplicate games in own-crop audit")
    aggregate = summarize(rows)
    groups = {
        name: summarize([row for row in rows if cohort(row) == name])
        for name in ("wins", "ordinary_losses", "catastrophic_losses")
    }
    catastrophic = groups["catastrophic_losses"]
    gates = {
        "integrity": (
            len(rows) == 131
            and not fetch_failures
            and aggregate["crops"] >= 500
            and all(
                row["quality"]["decoded_turns"]
                == row["quality"]["trajectory_turns"]
                and row["quality"]["unknown_diff_updates"] == 0
                for row in rows
            )
        ),
        "overall_wood_leakage": aggregate["opponent_wood_share"] >= 0.15,
        "catastrophic_wood_leakage": (
            catastrophic["games"] > 0
            and catastrophic["opponent_wood_per_game"] is not None
            and catastrophic["opponent_wood_per_game"] >= 8.0
        ),
        "geometry_concentration": (
            aggregate["nonresident_favored_share_of_leaked_wood"] >= 0.60
        ),
        "capture_game_coverage": aggregate["opponent_capture_games"] >= 20,
    }
    passed = all(gates.values())
    return {
        "schema": 1,
        "scope": "observational consumed exact-resident own-crop leakage diagnostic",
        "expected_agent": EXPECTED_AGENT,
        "games": len(rows),
        "fetch_failures": fetch_failures,
        "aggregate": aggregate,
        "cohorts": groups,
        "gates": gates,
        "passed": passed,
        "decision": (
            "own-crop leakage passes; build exact-fallback private placement residual"
            if passed
            else "own-crop leakage is too small or diffuse; close placement residual"
        ),
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        raise SystemExit("--jobs must be between 1 and 32")
    census = json.loads(args.census.read_text())
    fixed = census.get("rows") or []
    if len(fixed) != 131 or {int(row["agent_id"]) for row in fixed} != {EXPECTED_AGENT}:
        raise SystemExit("census is not the exact 131-game Phase 21 control")

    def fetch(row: dict) -> tuple[dict | None, dict | None]:
        try:
            game = arena.call("gameResult/findByGameId", [int(row["game_id"]), None])
            return analyze_game(game, row), None
        except Exception as error:  # pragma: no cover - network failure path
            return None, {
                "game_id": int(row["game_id"]),
                "error": f"{type(error).__name__}: {error}",
            }

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        fetched = list(executor.map(fetch, fixed))
    rows = [row for row, error in fetched if row is not None]
    failures = [error for row, error in fetched if error is not None]
    payload = analyze(rows, failures)
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(
        json.dumps(
            {
                "games": payload["games"],
                "fetch_failures": payload["fetch_failures"],
                "aggregate": payload["aggregate"],
                "cohorts": payload["cohorts"],
                "gates": payload["gates"],
                "passed": payload["passed"],
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

