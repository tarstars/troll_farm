#!/usr/bin/env python3
"""Measure direct harvest-on-contact opportunities on opponent-created crops."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import battle_taxonomy as arena
from cgauto.recent_resident_field_census import (
    corpus_parser,
    crop_provenance,
    current_player,
    decoded_states,
)
from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import assigned_unit_commands


REPO = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "phase21-candidate-field-census-2026-07-19.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "opponent-crop-harvest-contact-diagnostic-2026-07-19.json"
)
EXPECTED_AGENT = 6560269

GATE = {
    "minimum_opportunities": 80,
    "minimum_games": 30,
    "minimum_opponents": 12,
    "minimum_collectable_fruit": 80,
    "minimum_full_depletions": 40,
    "minimum_zero_immediate_wood": 60,
    "minimum_later_opponent_harvested_crops": 40,
    "minimum_later_opponent_fruit": 60,
    "minimum_catastrophic_opportunities": 25,
}


def record_key(record: dict[str, Any]) -> tuple[tuple[int, int], int]:
    return (int(record["cell"][0]), int(record["cell"][1])), int(
        record["birth_turn"]
    )


def active_crop(
    records: list[dict[str, Any]], cell: tuple[int, int], turn: int
) -> dict[str, Any] | None:
    matches = [
        record
        for record in records
        if tuple(record["cell"]) == cell
        and int(record["birth_turn"]) <= turn
        and (record["death_turn"] is None or turn <= int(record["death_turn"]))
    ]
    return max(matches, key=lambda record: int(record["birth_turn"]), default=None)


def free_capacity(unit: dict[str, Any]) -> int:
    return max(0, int(unit["cc"]) - sum(int(value) for value in unit["carry"]))


def analyze_game(game: dict[str, Any], census_row: dict[str, Any]) -> dict[str, Any]:
    me = current_player(game)
    if me is None:
        raise ValueError("our player is absent")
    agents = game.get("agents") or []
    if agents[me].get("agentId") != EXPECTED_AGENT:
        raise ValueError(
            f"expected candidate agent {EXPECTED_AGENT}, got {agents[me].get('agentId')}"
        )

    frames = game.get("frames") or []
    parser = corpus_parser()
    _, _, inv0, inv1 = parser.parse_frame0(frames[0]["view"])
    trajectory, _ = parser.extract_turns(frames, inv0, inv1)
    records, quality = crop_provenance(game, trajectory, me)
    _, states, unknown_updates = decoded_states(game, trajectory)
    usable = min(len(states) - 1, len(trajectory))

    work_events: dict[tuple[tuple[int, int], int], dict[int, list[dict[str, int]]]] = {
        record_key(record): {0: [], 1: []} for record in records
    }
    opportunities: dict[tuple[tuple[int, int], int], dict[str, Any]] = {}

    for turn in range(1, usable + 1):
        before = states[turn - 1]
        after = states[turn]
        before_units = {int(unit["id"]): unit for unit in before["units"]}
        after_units = {int(unit["id"]): unit for unit in after["units"]}
        plants = {
            (int(plant["x"]), int(plant["y"])): plant
            for plant in before["plants"]
        }

        for player in (0, 1):
            units = [unit for unit in before["units"] if unit["player"] == player]
            assigned = assigned_unit_commands(
                action_commands(trajectory[turn - 1].get(f"commands{player}")), units
            )
            for unit_id, command in assigned.items():
                fields = command.split()
                if not fields:
                    continue
                verb = fields[0].upper()
                if verb not in {"CHOP", "HARVEST"}:
                    continue
                unit = before_units.get(unit_id)
                if unit is None:
                    continue
                cell = int(unit["x"]), int(unit["y"])
                record = active_crop(records, cell, turn)
                if record is None:
                    continue
                key = record_key(record)
                after_unit = after_units.get(unit_id)
                gained = [0] * 6
                if after_unit is not None:
                    gained = [
                        max(
                            0,
                            int(after_unit["carry"][index])
                            - int(unit["carry"][index]),
                        )
                        for index in range(6)
                    ]
                if verb == "HARVEST":
                    work_events[key][player].append(
                        {"turn": turn, "fruit": sum(gained[:4])}
                    )

                if player != me or verb != "CHOP" or key in opportunities:
                    continue
                plant = plants.get(cell)
                free = free_capacity(unit)
                harvest_power = int(unit["hp"])
                if plant is None or int(plant["fruits"]) <= 0:
                    continue
                if harvest_power <= 0 or free <= 0:
                    continue
                visible_fruit = int(plant["fruits"])
                collectable = min(visible_fruit, harvest_power, free)
                opportunities[key] = {
                    "cell": list(cell),
                    "type": record["type"],
                    "birth_turn": int(record["birth_turn"]),
                    "death_turn": record["death_turn"],
                    "opportunity_turn": turn,
                    "unit_id": int(unit_id),
                    "unit_stats": {
                        "movement": int(unit["ms"]),
                        "carry": int(unit["cc"]),
                        "harvest": harvest_power,
                        "chop": int(unit["chop"]),
                    },
                    "unit_cargo": [int(value) for value in unit["carry"]],
                    "free_capacity": free,
                    "tree_size": int(plant["size"]),
                    "tree_health": int(plant["health"]),
                    "visible_fruit": visible_fruit,
                    "collectable_fruit": collectable,
                    "would_empty_crop": collectable >= visible_fruit,
                    "immediate_wood_from_actual_chop": gained[5],
                    "our_eventual_wood_from_crop": int(record["our_wood_collected"]),
                    "opponent_eventual_wood_from_crop": int(
                        record["opponent_wood_collected"]
                    ),
                    "opponent_eventual_fruit_from_crop": int(
                        record["opponent_fruit_harvested"]
                    ),
                }

    opponent = 1 - me
    enriched = []
    for key, opportunity in opportunities.items():
        later = [
            event
            for event in work_events[key][opponent]
            if event["turn"] > opportunity["opportunity_turn"] and event["fruit"] > 0
        ]
        opportunity["later_opponent_harvest_events"] = later
        opportunity["later_opponent_fruit"] = sum(
            event["fruit"] for event in later
        )
        opportunity["later_opponent_harvested"] = bool(later)
        enriched.append(opportunity)
    enriched.sort(key=lambda row: (row["opportunity_turn"], row["cell"]))

    return {
        "game_id": int(game["gameId"]),
        "opponent": census_row["opponent"],
        "seat": me,
        "margin": int(census_row["margin"]),
        "catastrophic": int(census_row["margin"]) <= -100,
        "crop_attribution_quality": quality,
        "second_decode_unknown_updates": unknown_updates,
        "opponent_crops": len(records),
        "opportunities": enriched,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    opportunities = [item for row in rows for item in row["opportunities"]]
    active_rows = [row for row in rows if row["opportunities"]]
    opponents = {row["opponent"] for row in active_rows}
    total_collectable = sum(item["collectable_fruit"] for item in opportunities)
    full_depletions = sum(item["would_empty_crop"] for item in opportunities)
    zero_wood = sum(
        item["immediate_wood_from_actual_chop"] == 0 for item in opportunities
    )
    later_harvested = sum(
        item["later_opponent_harvested"] for item in opportunities
    )
    later_fruit = sum(item["later_opponent_fruit"] for item in opportunities)
    catastrophic = sum(
        len(row["opportunities"]) for row in rows if row["catastrophic"]
    )
    checks = {
        "opportunities": len(opportunities) >= GATE["minimum_opportunities"],
        "games": len(active_rows) >= GATE["minimum_games"],
        "opponents": len(opponents) >= GATE["minimum_opponents"],
        "collectable_fruit": total_collectable
        >= GATE["minimum_collectable_fruit"],
        "full_depletions": full_depletions >= GATE["minimum_full_depletions"],
        "zero_immediate_wood": zero_wood >= GATE["minimum_zero_immediate_wood"],
        "later_opponent_harvested_crops": later_harvested
        >= GATE["minimum_later_opponent_harvested_crops"],
        "later_opponent_fruit": later_fruit
        >= GATE["minimum_later_opponent_fruit"],
        "catastrophic_opportunities": catastrophic
        >= GATE["minimum_catastrophic_opportunities"],
    }
    return {
        "games": len(rows),
        "opportunity_games": len(active_rows),
        "opportunity_opponents": len(opponents),
        "opponent_names": sorted(opponents),
        "opportunities": len(opportunities),
        "collectable_fruit": total_collectable,
        "full_depletions": full_depletions,
        "zero_immediate_wood": zero_wood,
        "later_opponent_harvested_crops": later_harvested,
        "later_opponent_fruit": later_fruit,
        "catastrophic_opportunities": catastrophic,
        "opportunities_by_type": dict(
            sorted(Counter(item["type"] for item in opportunities).items())
        ),
        "opportunities_by_seat": dict(
            sorted(Counter(str(row["seat"]) for row in active_rows for _ in row["opportunities"]).items())
        ),
        "gate_checks": checks,
        "gate_passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    census = json.loads(args.input.read_text())
    census_rows = census.get("rows") or []
    rows = []
    failures = []
    for index, census_row in enumerate(census_rows, 1):
        game_id = int(census_row["game_id"])
        try:
            game = arena.call("gameResult/findByGameId", [game_id, None])
            rows.append(analyze_game(game, census_row))
        except Exception as error:  # noqa: BLE001 - preserve a complete audit trail
            failures.append(
                {"game_id": game_id, "error": f"{type(error).__name__}: {error}"}
            )
        if index % 20 == 0 or index == len(census_rows):
            print(f"fetched {index}/{len(census_rows)} candidate replays", flush=True)

    report = summarize(rows)
    payload = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only Phase 21 exact-state diagnostic on consumed arena games; "
            "never candidate-qualification evidence"
        ),
        "input": str(args.input.relative_to(REPO)),
        "expected_agent": EXPECTED_AGENT,
        "requested_games": len(census_rows),
        "parsed_games": len(rows),
        "fetch_failures": failures,
        "gate": GATE,
        "summary": report,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(
        f"games={len(rows)} opportunities={report['opportunities']} "
        f"across={report['opportunity_games']} games/{report['opportunity_opponents']} opponents "
        f"fruit={report['collectable_fruit']} empty={report['full_depletions']} "
        f"zero_wood={report['zero_immediate_wood']} "
        f"later={report['later_opponent_harvested_crops']}/"
        f"{report['later_opponent_fruit']} cat={report['catastrophic_opportunities']} "
        f"gate={report['gate_passed']} failures={len(failures)}"
    )
    print(f"saved {args.output}")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
