#!/usr/bin/env python3
"""Validate a recorded-command turn-75 option labeler on consumed official games."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import traceback

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d29c_official_field_activation import distribution
from cgauto.recent_resident_field_census import (
    corpus_parser,
    current_player,
    decoded_states,
    player_name,
)
from cgauto.replay_conformance import action_commands


ANALYSIS = REPO / "data/analysis/live-agent-6553250"
CHECKPOINT = ANALYSIS / "d29b-pretransfer-resident-checkpoint-2026-07-20.json"
D29C = ANALYSIS / "d29c-official-field-activation-audit-2026-07-20.json"
BINARY = REPO / "rust/target/release/d31_replay_conditioned_option"
OUTPUT = ANALYSIS / "d31-replay-conditioned-option-labeler-development-2026-07-20.json"
EXPECTED_AGENT = 6561795
EXPECTED_SUBMISSION = 41015603
ROOT_TURN = 75
CHECKPOINT_TURN = 125
HORIZON = 50


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_rows(rows: list[str], seat: int) -> list[str]:
    if seat == 0:
        return rows
    return [row.translate(str.maketrans({"0": "1", "1": "0"})) for row in rows]


def transcript(map_data: dict, states: list[dict], trajectory: list[dict], seat: int) -> bytes:
    if len(states) < CHECKPOINT_TURN or len(trajectory) < ROOT_TURN - 1 + HORIZON:
        raise ValueError("official replay does not cover frozen D31 horizon")
    lines = [f"{map_data['width']} {map_data['height']}"]
    lines.extend(normalized_rows(map_data["rows"], seat))
    for state in states[:CHECKPOINT_TURN]:
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
            relative_player = int(unit["player"] != seat)
            carry = " ".join(map(str, unit["carry"]))
            lines.append(
                f"{unit['id']} {relative_player} {unit['x']} {unit['y']} {unit['ms']} "
                f"{unit['cc']} {unit['hp']} {unit['chop']} {carry}"
            )
    lines.append(f"COMMANDS {HORIZON}")
    for turn in range(ROOT_TURN, ROOT_TURN + HORIZON):
        row = trajectory[turn - 1]
        ours = action_commands(row.get(f"commands{seat}"))
        theirs = action_commands(row.get(f"commands{1 - seat}"))
        lines.append(";".join(ours))
        lines.append(";".join(theirs))
    return ("\n".join(lines) + "\n").encode()


def evaluate_one(checkpoint_row: dict, binary: Path) -> dict:
    from cgauto import battle_taxonomy as arena

    game_id = int(checkpoint_row["game_id"])
    game = arena.call("gameResult/findByGameId", [game_id, None])
    seat = current_player(game)
    agents = game.get("agents") or []
    if seat is None or agents[seat].get("agentId") != EXPECTED_AGENT:
        raise ValueError(f"resident identity differs for {game_id}")
    frames = game.get("frames") or []
    parser = corpus_parser()
    _, _, inventory0, inventory1 = parser.parse_frame0(frames[0]["view"])
    trajectory, _ = parser.extract_turns(frames, inventory0, inventory1)
    map_data, states, unknown = decoded_states(game, trajectory)
    if unknown:
        raise ValueError(f"unknown replay updates for {game_id}: {unknown}")
    completed = subprocess.run(
        [binary],
        input=transcript(map_data, states, trajectory, seat),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        timeout=10,
    )
    result = json.loads(completed.stdout)
    return {
        "game_id": game_id,
        "seat": seat,
        "opponent": player_name(agents[1 - seat]),
        "opponent_agent_id": agents[1 - seat].get("agentId"),
        "official_resolved_turns": len(states) - 1,
        "unknown_updates": unknown,
        **result,
    }


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    left_mean = statistics.mean(left)
    right_mean = statistics.mean(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_scale = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_scale = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    return numerator / (left_scale * right_scale) if left_scale and right_scale else None


def summarize(checkpoint_path: Path, binary: Path, rows: list[dict], failures: list[dict]) -> dict:
    d29c = json.loads(D29C.read_text())
    predictions = {int(row["game_id"]): row for row in d29c["rows"]}
    for row in rows:
        prediction = predictions[row["game_id"]]
        row["d29b_raw_prediction"] = float(prediction["raw_prediction"])
        row["d29b_switch"] = int(prediction["switch"])

    exact_turns = sum(int(row["exact_command_turns"]) for row in rows)
    total_turns = len(rows) * HORIZON
    control_actions = sum(int(row["control_opponent_actions"]) for row in rows)
    control_supported = sum(int(row["control_opponent_supported"]) for row in rows)
    option_actions = sum(int(row["option_opponent_actions"]) for row in rows)
    option_supported = sum(int(row["option_opponent_supported"]) for row in rows)
    error0 = [abs(int(row["control_score0"]) - int(row["official_score0"])) for row in rows]
    error1 = [abs(int(row["control_score1"]) - int(row["official_score1"])) for row in rows]
    margin_error = [abs(int(row["control_margin"]) - int(row["official_margin"])) for row in rows]
    deltas = [float(row["option_minus_control_margin"]) for row in rows]
    raw = [float(row["d29b_raw_prediction"]) for row in rows]
    gates = {
        "all_80_complete_identity_clean": len(rows) == 80 and not failures,
        "root_command_exact_80_of_80": sum(bool(row["root_command_exact"]) for row in rows) == 80,
        "control_command_turn_rate_at_least_95_percent": (
            exact_turns / total_turns >= 0.95 if total_turns else False
        ),
        "at_least_60_games_all_50_commands_exact": sum(
            int(row["exact_command_turns"]) == HORIZON for row in rows
        ) >= 60,
        "at_least_72_material_exact": sum(bool(row["material_exact"]) for row in rows) >= 72,
        "at_least_64_positions_exact": sum(bool(row["positions_exact"]) for row in rows) >= 64,
        "at_least_60_full_exact": sum(bool(row["full_exact"]) for row in rows) >= 60,
        "mean_abs_score0_error_at_most_2": statistics.mean(error0) <= 2 if error0 else False,
        "mean_abs_score1_error_at_most_2": statistics.mean(error1) <= 2 if error1 else False,
        "mean_abs_margin_error_at_most_3": statistics.mean(margin_error) <= 3 if margin_error else False,
        "control_opponent_applicability_at_least_99_percent": (
            control_supported / control_actions >= 0.99 if control_actions else False
        ),
        "option_opponent_applicability_at_least_95_percent": (
            option_supported / option_actions >= 0.95 if option_actions else False
        ),
    }
    switched = [row for row in rows if row["d29b_switch"]]
    stayed = [row for row in rows if not row["d29b_switch"]]
    return {
        "schema": 1,
        "complete": all(gates.values()),
        "scope": "D31 consumed-prefix recorded-command labeler fidelity; no Arena action",
        "sample": {
            "requested": 80,
            "completed": len(rows),
            "failures": failures,
            "root_turn": ROOT_TURN,
            "checkpoint_turn": CHECKPOINT_TURN,
            "horizon": HORIZON,
        },
        "control_fidelity": {
            "root_commands_exact": sum(bool(row["root_command_exact"]) for row in rows),
            "exact_command_turns": exact_turns,
            "command_turns": total_turns,
            "exact_command_rate": exact_turns / total_turns if total_turns else None,
            "games_all_50_commands_exact": sum(
                int(row["exact_command_turns"]) == HORIZON for row in rows
            ),
            "exact_prefix_length": distribution(
                [float(row["exact_command_prefix"]) for row in rows]
            ),
            "scores_exact": sum(bool(row["scores_exact"]) for row in rows),
            "inventories_exact": sum(bool(row["inventories_exact"]) for row in rows),
            "unit_economy_exact": sum(bool(row["unit_economy_exact"]) for row in rows),
            "plants_exact": sum(bool(row["plants_exact"]) for row in rows),
            "positions_exact": sum(bool(row["positions_exact"]) for row in rows),
            "material_exact": sum(bool(row["material_exact"]) for row in rows),
            "full_exact": sum(bool(row["full_exact"]) for row in rows),
            "absolute_score0_error": distribution([float(value) for value in error0]),
            "absolute_score1_error": distribution([float(value) for value in error1]),
            "absolute_margin_error": distribution([float(value) for value in margin_error]),
        },
        "recorded_opponent_applicability": {
            "control": {
                "actions": control_actions,
                "supported": control_supported,
                "rate": control_supported / control_actions if control_actions else None,
            },
            "option": {
                "actions": option_actions,
                "supported": option_supported,
                "rate": option_supported / option_actions if option_actions else None,
            },
        },
        "descriptive_fixed_action_branch_delta": {
            "all": distribution(deltas),
            "d29b_switched": distribution(
                [float(row["option_minus_control_margin"]) for row in switched]
            ),
            "d29b_stayed": distribution(
                [float(row["option_minus_control_margin"]) for row in stayed]
            ),
            "d29b_prediction_delta_pearson": pearson(raw, deltas),
            "positive_delta_count": sum(value > 0 for value in deltas),
            "selected_positive_delta_count": sum(
                int(row["option_minus_control_margin"]) > 0 for row in switched
            ),
            "warning": "descriptive only; forbidden as a training or threshold label if any gate fails",
        },
        "gates": gates,
        "decision": (
            "eligible_for_separately_frozen_prospective_validation"
            if all(gates.values())
            else "reject_recorded_command_labeler"
        ),
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "d29c_sha256": sha256(D29C),
        "binary": str(binary),
        "binary_sha256": sha256(binary),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--binary", type=Path, default=BINARY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    checkpoint = json.loads(args.checkpoint.read_text())
    if checkpoint.get("agent_id") != EXPECTED_AGENT:
        parser.error("resident agent differs")
    if checkpoint.get("submission_id") != EXPECTED_SUBMISSION:
        parser.error("resident submission differs")
    requested = checkpoint.get("rows", [])[:80]
    if len(requested) != 80:
        parser.error("D31 requires exactly the frozen first 80 rows")

    rows = []
    failures = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(evaluate_one, row, args.binary): int(row["game_id"])
            for row in requested
        }
        for index, future in enumerate(as_completed(futures), 1):
            game_id = futures[future]
            try:
                rows.append(future.result())
            except Exception as error:  # noqa: BLE001 - complete frozen audit
                failures.append(
                    {
                        "game_id": game_id,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
            if index % 10 == 0 or index == 80:
                print(f"evaluated {index}/80 replay-conditioned roots", flush=True)
    order = {int(row["game_id"]): index for index, row in enumerate(requested)}
    rows.sort(key=lambda row: order[row["game_id"]])
    failures.sort(key=lambda row: order[row["game_id"]])
    result = summarize(args.checkpoint, args.binary, rows, failures)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {
                "complete": result["complete"],
                "control_fidelity": result["control_fidelity"],
                "opponent_applicability": result["recorded_opponent_applicability"],
                "branch_delta": result["descriptive_fixed_action_branch_delta"],
                "failed_gates": [
                    name for name, passed in result["gates"].items() if not passed
                ],
                "output": str(args.output),
            },
            indent=1,
        )
    )
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
