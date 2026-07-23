#!/usr/bin/env python3
"""Audit frozen D29b decisions on exact current-resident Arena trajectories."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import traceback

from cgauto.recent_resident_field_census import (
    corpus_parser,
    current_player,
    decoded_states,
    player_name,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
DEFAULT_CHECKPOINT = ANALYSIS / "d29b-pretransfer-resident-checkpoint-2026-07-20.json"
DEFAULT_BINARY = ROOT / "rust/target/release/d29c_field_activation"
DEFAULT_OUTPUT = ANALYSIS / "d29c-official-field-activation-audit-2026-07-20.json"
REFERENCE_PREDICTIONS = ANALYSIS / "d29b-predictions-confirmation-run1-53720-53839.tsv"
EXPECTED_AGENT = 6561795
EXPECTED_SUBMISSION = 41015603
THRESHOLD = 4.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def distribution(values: list[float]) -> dict:
    return {
        "count": len(values),
        "minimum": min(values) if values else None,
        "p05": quantile(values, 0.05),
        "p25": quantile(values, 0.25),
        "median": quantile(values, 0.50),
        "p75": quantile(values, 0.75),
        "p95": quantile(values, 0.95),
        "maximum": max(values) if values else None,
        "mean": statistics.mean(values) if values else None,
    }


def normalized_rows(rows: list[str], seat: int) -> list[str]:
    if seat == 0:
        return rows
    return [row.translate(str.maketrans({"0": "1", "1": "0"})) for row in rows]


def protocol_transcript(map_data: dict, states: list[dict], seat: int) -> bytes:
    lines = [f"{map_data['width']} {map_data['height']}"]
    lines.extend(normalized_rows(map_data["rows"], seat))
    for state in states[:75]:
        for player in (seat, 1 - seat):
            lines.append(" ".join(map(str, state["inventories"][player])))
        lines.append(str(len(state["plants"])))
        for plant in state["plants"]:
            lines.append(
                f"{plant['type']} {plant['x']} {plant['y']} {plant['size']} "
                f"{plant['health']} {plant['fruits']} {plant['cooldown']}"
            )
        lines.append(str(len(state["units"])))
        for unit in state["units"]:
            player = int(unit["player"] != seat)
            carry = " ".join(map(str, unit["carry"]))
            lines.append(
                f"{unit['id']} {player} {unit['x']} {unit['y']} {unit['ms']} "
                f"{unit['cc']} {unit['hp']} {unit['chop']} {carry}"
            )
    return ("\n".join(lines) + "\n").encode()


def reference_distribution() -> dict:
    import csv

    with REFERENCE_PREDICTIONS.open(newline="") as stream:
        values = [
            float(row["raw_prediction"])
            for row in csv.DictReader(stream, delimiter="\t")
        ]
    return distribution(values)


def group_summary(rows: list[dict], field: str) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[str(row[field])].append(row)
    return {
        name: {
            "games": len(group),
            "switches": sum(row["switch"] for row in group),
            "switch_rate": sum(row["switch"] for row in group) / len(group),
            "mean_raw_prediction": statistics.mean(
                row["raw_prediction"] for row in group
            ),
            "mean_observed_resident_margin": statistics.mean(
                row["observed_resident_margin"] for row in group
            ),
        }
        for name, group in sorted(grouped.items())
    }


def audit(checkpoint_path: Path, binary: Path, limit: int) -> dict:
    from cgauto import battle_taxonomy as arena

    checkpoint = json.loads(checkpoint_path.read_text())
    if checkpoint.get("agent_id") != EXPECTED_AGENT:
        raise ValueError("checkpoint resident agent differs")
    if checkpoint.get("submission_id") != EXPECTED_SUBMISSION:
        raise ValueError("checkpoint resident submission differs")
    requested = checkpoint.get("rows", [])[:limit]
    rows = []
    failures = []
    short_games = []
    identity_failures = []
    unknown_update_games = []
    for index, checkpoint_row in enumerate(requested, 1):
        game_id = int(checkpoint_row["game_id"])
        try:
            game = arena.call("gameResult/findByGameId", [game_id, None])
            seat = current_player(game)
            agents = game.get("agents") or []
            target = agents[seat] if seat is not None and seat < len(agents) else {}
            if seat is None or target.get("agentId") != EXPECTED_AGENT:
                identity_failures.append(game_id)
                continue
            frames = game.get("frames") or []
            parser = corpus_parser()
            _, _, inventory0, inventory1 = parser.parse_frame0(frames[0]["view"])
            trajectory, _ = parser.extract_turns(frames, inventory0, inventory1)
            map_data, states, unknown_updates = decoded_states(game, trajectory)
            if len(states) < 75:
                short_games.append(game_id)
                continue
            if unknown_updates:
                unknown_update_games.append(
                    {"game_id": game_id, "unknown_updates": unknown_updates}
                )
            completed = subprocess.run(
                [binary],
                input=protocol_transcript(map_data, states, seat),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            prediction = json.loads(completed.stdout)
            opponent = 1 - seat
            scores = [int(value) for value in game["scores"]]
            margin = scores[seat] - scores[opponent]
            outcome = (
                "catastrophic"
                if margin <= -100
                else "ordinary_loss"
                if margin < 0
                else "tie"
                if margin == 0
                else "win"
            )
            rows.append(
                {
                    "game_id": game_id,
                    "seat": seat,
                    "opponent": player_name(agents[opponent]),
                    "opponent_agent_id": agents[opponent].get("agentId"),
                    "resolved_turns": len(states) - 1,
                    "unknown_diff_updates": unknown_updates,
                    "observed_resident_margin": margin,
                    "outcome": outcome,
                    **prediction,
                }
            )
        except Exception as error:  # noqa: BLE001 - preserve complete readiness audit
            failures.append(
                {
                    "game_id": game_id,
                    "error": f"{type(error).__name__}: {error}",
                    "traceback": traceback.format_exc(),
                }
            )
        if index % 10 == 0 or index == len(requested):
            print(f"audited {index}/{len(requested)} official games", flush=True)

    raw = [float(row["raw_prediction"]) for row in rows]
    normalized = [float(row["normalized_prediction"]) for row in rows]
    switches = sum(int(row["switch"]) for row in rows)
    switch_rate = switches / len(rows) if rows else 0.0
    gates = {
        "requested_80": len(requested) == 80,
        "all_fetched": not failures and len(rows) + len(short_games) == len(requested),
        "identity_clean": not identity_failures,
        "at_least_60_reached_turn75": len(rows) >= 60,
        "zero_unknown_updates": not unknown_update_games,
        "finite_predictions": all(
            row["finite"]
            and math.isfinite(float(row["raw_prediction"]))
            and math.isfinite(float(row["normalized_prediction"]))
            for row in rows
        ),
        "exactly_two_workers": all(int(row["workers"]) == 2 for row in rows),
        "both_decisions_at_least_10": switches >= 10 and len(rows) - switches >= 10,
        "activation_rate_17_to_67_percent": 0.17 <= switch_rate <= 0.67,
    }
    return {
        "schema": 1,
        "complete": all(gates.values()),
        "scope": "read-only D29b activation audit on frozen current-resident Arena games",
        "expected_agent": EXPECTED_AGENT,
        "expected_submission": EXPECTED_SUBMISSION,
        "requested_games": len(requested),
        "reached_turn75": len(rows),
        "short_games": short_games,
        "fetch_failures": failures,
        "identity_failures": identity_failures,
        "unknown_update_games": unknown_update_games,
        "switches": switches,
        "stays": len(rows) - switches,
        "switch_rate": switch_rate,
        "raw_prediction": distribution(raw),
        "normalized_prediction": distribution(normalized),
        "distance_from_threshold": {
            "minimum": min((abs(value - THRESHOLD) for value in raw), default=None),
            "within_1": sum(abs(value - THRESHOLD) <= 1 for value in raw),
            "within_4": sum(abs(value - THRESHOLD) <= 4 for value in raw),
        },
        "generated_confirmation_raw_prediction": reference_distribution(),
        "by_seat": group_summary(rows, "seat"),
        "by_opponent": group_summary(rows, "opponent"),
        "by_observed_outcome": group_summary(rows, "outcome"),
        "gates": gates,
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "diagnostic_binary": str(binary),
        "diagnostic_binary_sha256": sha256(binary),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY)
    parser.add_argument("--max-games", type=int, default=80)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.max_games != 80:
        parser.error("D29c frozen protocol requires exactly 80 games")
    result = audit(args.checkpoint, args.binary, args.max_games)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(
        f"reached={result['reached_turn75']}/80 switches={result['switches']} "
        f"rate={result['switch_rate']:.1%} complete={result['complete']}"
    )
    print(f"saved {args.output}")
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
