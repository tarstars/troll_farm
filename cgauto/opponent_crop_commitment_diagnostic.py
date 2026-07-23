#!/usr/bin/env python3
"""Measure transient opponent-crop target abandonment in Phase 21 replays."""

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
    / "opponent-crop-commitment-diagnostic-2026-07-19.json"
)
EXPECTED_AGENT = 6560269

GATE = {
    "minimum_selected_crops": 80,
    "minimum_selected_games": 20,
    "minimum_abandonment_rate": 0.15,
    "minimum_abandoned_games": 10,
    "minimum_abandoned_opponents": 8,
    "minimum_abandoned_opponent_wood_share": 0.10,
    "minimum_catastrophic_abandoned_crops": 20,
}


def command_target(command: str, unit: dict[str, Any]) -> tuple[int, int] | None:
    fields = command.split()
    if not fields:
        return None
    verb = fields[0].upper()
    if verb == "MOVE" and len(fields) >= 4:
        try:
            return int(fields[2]), int(fields[3])
        except ValueError:
            return None
    if verb in {"CHOP", "HARVEST"}:
        return int(unit["x"]), int(unit["y"])
    return None


def selection_events(
    game: dict[str, Any], trajectory: list[dict], me: int, records: list[dict]
) -> dict[tuple[tuple[int, int], int], list[dict]]:
    _, states, _ = decoded_states(game, trajectory)
    usable = min(len(states) - 1, len(trajectory))
    events: dict[tuple[tuple[int, int], int], list[dict]] = {
        ((int(record["cell"][0]), int(record["cell"][1])), int(record["birth_turn"])): []
        for record in records
    }
    for turn in range(1, usable + 1):
        before = states[turn - 1]
        units = [unit for unit in before["units"] if unit["player"] == me]
        by_id = {unit["id"]: unit for unit in units}
        commands = assigned_unit_commands(
            action_commands(trajectory[turn - 1].get(f"commands{me}")), units
        )
        for unit_id, command in commands.items():
            unit = by_id.get(unit_id)
            if unit is None:
                continue
            target = command_target(command, unit)
            if target is None:
                continue
            active = [
                record
                for record in records
                if tuple(record["cell"]) == target
                and record["birth_turn"] <= turn
                and (record["death_turn"] is None or turn <= record["death_turn"])
            ]
            if not active:
                continue
            record = max(active, key=lambda candidate: candidate["birth_turn"])
            key = (target, int(record["birth_turn"]))
            events[key].append(
                {
                    "turn": turn,
                    "unit_id": unit_id,
                    "verb": command.split()[0].upper(),
                }
            )
    return events


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
    events = selection_events(game, trajectory, me, records)
    selected_records = []
    for record in records:
        key = (tuple(record["cell"]), int(record["birth_turn"]))
        selections = events.get(key, [])
        if not selections:
            continue
        first_selection = selections[0]["turn"]
        first_contact = record["first_our_contact_turn"]
        selected_records.append(
            {
                "cell": record["cell"],
                "type": record["type"],
                "birth_turn": record["birth_turn"],
                "death_turn": record["death_turn"],
                "our_eta_at_birth": record["our_eta_at_birth"],
                "first_selection_turn": first_selection,
                "first_contact_turn": first_contact,
                "selection_to_contact_turns": (
                    first_contact - first_selection if first_contact is not None else None
                ),
                "selection_events": selections,
                "abandoned": first_contact is None,
                "opponent_wood_collected": record["opponent_wood_collected"],
                "opponent_fruit_harvested": record["opponent_fruit_harvested"],
                "our_wood_collected": record["our_wood_collected"],
            }
        )
    return {
        "game_id": int(game["gameId"]),
        "opponent": census_row["opponent"],
        "margin": int(census_row["margin"]),
        "catastrophic": int(census_row["margin"]) <= -100,
        "crop_attribution_quality": quality,
        "opponent_crops": len(records),
        "selected_crops": len(selected_records),
        "abandoned_crops": sum(record["abandoned"] for record in selected_records),
        "selected_records": selected_records,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [record for row in rows for record in row["selected_records"]]
    abandoned = [record for record in selected if record["abandoned"]]
    abandoned_rows = [row for row in rows if row["abandoned_crops"]]
    catastrophic_abandoned = sum(
        row["abandoned_crops"] for row in rows if row["catastrophic"]
    )
    selected_opponent_wood = sum(
        record["opponent_wood_collected"] for record in selected
    )
    abandoned_opponent_wood = sum(
        record["opponent_wood_collected"] for record in abandoned
    )
    wood_share = (
        abandoned_opponent_wood / selected_opponent_wood
        if selected_opponent_wood
        else 0.0
    )
    abandonment_rate = len(abandoned) / len(selected) if selected else 0.0
    selected_games = sum(row["selected_crops"] > 0 for row in rows)
    abandoned_opponents = {row["opponent"] for row in abandoned_rows}
    checks = {
        "selected_crops": len(selected) >= GATE["minimum_selected_crops"],
        "selected_games": selected_games >= GATE["minimum_selected_games"],
        "abandonment_rate": abandonment_rate >= GATE["minimum_abandonment_rate"],
        "abandoned_games": len(abandoned_rows) >= GATE["minimum_abandoned_games"],
        "abandoned_opponents": len(abandoned_opponents)
        >= GATE["minimum_abandoned_opponents"],
        "abandoned_opponent_wood_share": wood_share
        >= GATE["minimum_abandoned_opponent_wood_share"],
        "catastrophic_abandoned_crops": catastrophic_abandoned
        >= GATE["minimum_catastrophic_abandoned_crops"],
    }
    return {
        "games": len(rows),
        "selected_games": selected_games,
        "selected_crops": len(selected),
        "abandoned_crops": len(abandoned),
        "abandonment_rate": abandonment_rate,
        "abandoned_games": len(abandoned_rows),
        "abandoned_opponents": len(abandoned_opponents),
        "abandoned_opponent_names": sorted(abandoned_opponents),
        "selected_opponent_wood": selected_opponent_wood,
        "abandoned_opponent_wood": abandoned_opponent_wood,
        "abandoned_opponent_wood_share": wood_share,
        "abandoned_opponent_fruit": sum(
            record["opponent_fruit_harvested"] for record in abandoned
        ),
        "catastrophic_abandoned_crops": catastrophic_abandoned,
        "abandoned_by_type": dict(
            sorted(Counter(record["type"] for record in abandoned).items())
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
        except Exception as error:  # noqa: BLE001 - retain complete diagnostic audit
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
            "read-only Phase 21 candidate replay diagnostic; consumed arena games only; "
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
        f"games={len(rows)} selected={report['selected_crops']} "
        f"abandoned={report['abandoned_crops']} "
        f"({report['abandonment_rate']:.1%}) "
        f"wood_share={report['abandoned_opponent_wood_share']:.1%} "
        f"catastrophic_abandoned={report['catastrophic_abandoned_crops']} "
        f"gate={report['gate_passed']} failures={len(failures)}"
    )
    print(f"saved {args.output}")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
