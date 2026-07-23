#!/usr/bin/env python3
"""Audit all-turn natural third-worker capital windows in cached resident replays."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.recent_resident_field_census import (
    corpus_parser,
    current_player,
    decoded_states,
)
from cgauto.top_player_opening_analysis import terrain


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/analysis/live-agent-6553250"
DEFAULT_D159 = BASE / "d159a-current-resident-all-finished-effect-refresh-raw.json"
DEFAULT_HISTORY = BASE / "d23-current-resident-field-refresh-2026-07-20.json"
DEFAULT_GAME_DIR = ROOT / "data/raw/games"
DEFAULT_OUTPUT = BASE / "d160a-resident-natural-capital-window-result.json"
EXPECTED_AGENT = 6561795
EXPECTED_D159_SHA256 = (
    "97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443"
)
KNOWN_SCORE_MISMATCHES = {896349139}
MAX_DECISION_TURN = 225
GATE_MAX_TURN = 200
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
SPECS = {
    "minimal_1101": (1, 1, 0, 1),
    "balanced_2202": (2, 2, 0, 2),
    "hybrid_2212": (2, 2, 1, 2),
    "carry_2302": (2, 3, 0, 2),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def training_cost(spec: tuple[int, int, int, int], has_iron: bool) -> list[int]:
    movement, carry, harvest, chop = spec
    return [
        2 + movement * movement,
        2 + carry * carry,
        2 + harvest * harvest,
        0,
        2 + chop * chop if has_iron else 0,
        0,
    ]


def max_consecutive(turns: list[int]) -> int:
    best = current = 0
    previous = None
    for turn in sorted(set(turns)):
        current = current + 1 if previous is not None and turn == previous + 1 else 1
        best = max(best, current)
        previous = turn
    return best


def _deficit(stock: list[int], cost: list[int]) -> list[int]:
    return [max(0, cost[index] - stock[index]) for index in range(6)]


def game_spec_report(
    states: list[dict],
    *,
    seat: int,
    shack: tuple[int, int],
    has_iron: bool,
    spec: tuple[int, int, int, int],
) -> dict:
    cost = training_cost(spec, has_iron)
    stock_turns = []
    liquid_turns = []
    executable_turns = []
    eligible_states = 0
    closest = None
    for state in states:
        decision_turn = int(state["resolved_turn"]) + 1
        if decision_turn > MAX_DECISION_TURN:
            continue
        own_units = [unit for unit in state["units"] if unit["player"] == seat]
        if len(own_units) != 2:
            continue
        eligible_states += 1
        bank = list(state["inventories"][seat])
        liquid = [
            bank[index] + sum(unit["carry"][index] for unit in own_units)
            for index in range(6)
        ]
        bank_deficit = _deficit(bank, cost)
        total_deficit = sum(bank_deficit)
        if closest is None or (total_deficit, decision_turn) < (
            closest["total_deficit"],
            closest["turn"],
        ):
            closest = {
                "turn": decision_turn,
                "total_deficit": total_deficit,
                "deficit": bank_deficit,
                "bank": bank,
                "liquid": liquid,
            }
        stock_affordable = total_deficit == 0
        liquid_affordable = sum(_deficit(liquid, cost)) == 0
        shack_clear = not any(
            (unit["x"], unit["y"]) == shack for unit in state["units"]
        )
        if stock_affordable:
            stock_turns.append(decision_turn)
        if liquid_affordable:
            liquid_turns.append(decision_turn)
        if stock_affordable and shack_clear:
            executable_turns.append(decision_turn)
    gate_turns = [turn for turn in executable_turns if turn <= GATE_MAX_TURN]
    if closest is None:
        closest = {
            "turn": None,
            "total_deficit": None,
            "deficit": None,
            "bank": None,
            "liquid": None,
        }
    limiting = []
    if closest["deficit"] is not None:
        limiting = [
            ITEMS[index]
            for index, value in enumerate(closest["deficit"])
            if value > 0
        ]
    return {
        "cost": cost,
        "eligible_states": eligible_states,
        "stock_affordable_turns": stock_turns,
        "liquid_affordable_turns": liquid_turns,
        "executable_turns": executable_turns,
        "first_executable_turn": executable_turns[0] if executable_turns else None,
        "last_executable_turn": executable_turns[-1] if executable_turns else None,
        "maximum_consecutive_executable": max_consecutive(executable_turns),
        "gate_executable_before_or_at_200": bool(gate_turns),
        "gate_maximum_consecutive": max_consecutive(gate_turns),
        "closest_state": {**closest, "limiting_resources": limiting},
    }


def score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[5]


def summarize_spec(rows: list[dict], spec_name: str) -> dict:
    reports = [(row, row["specs"][spec_name]) for row in rows]
    executable = [
        (row, report)
        for row, report in reports
        if report["gate_executable_before_or_at_200"]
    ]
    persistent = [
        (row, report)
        for row, report in reports
        if report["gate_maximum_consecutive"] >= 2
    ]
    minimum_deficits = [
        report["closest_state"]["total_deficit"]
        for _, report in reports
        if report["closest_state"]["total_deficit"] is not None
    ]
    limiting = Counter(
        resource
        for _, report in reports
        for resource in report["closest_state"]["limiting_resources"]
    )
    return {
        "games": len(rows),
        "games_stock_affordable_by_225": sum(
            bool(report["stock_affordable_turns"]) for _, report in reports
        ),
        "games_liquid_affordable_by_225": sum(
            bool(report["liquid_affordable_turns"]) for _, report in reports
        ),
        "games_executable_by_225": sum(
            bool(report["executable_turns"]) for _, report in reports
        ),
        "games_executable_by_200": len(executable),
        "games_with_two_turn_window_by_200": len(persistent),
        "executable_opponents": len({row["opponent"] for row, _ in executable}),
        "executable_seats": sorted({row["seat"] for row, _ in executable}),
        "executable_outcomes": dict(
            sorted(Counter(row["outcome"] for row, _ in executable).items())
        ),
        "minimum_deposited_deficit": {
            "minimum": min(minimum_deficits) if minimum_deficits else None,
            "median": statistics.median(minimum_deficits) if minimum_deficits else None,
            "maximum": max(minimum_deficits) if minimum_deficits else None,
            "within_1_games": sum(value <= 1 for value in minimum_deficits),
            "within_2_games": sum(value <= 2 for value in minimum_deficits),
            "within_4_games": sum(value <= 4 for value in minimum_deficits),
        },
        "closest_state_limiting_resources": dict(sorted(limiting.items())),
    }


def cohort_report(rows: list[dict]) -> dict:
    return {name: summarize_spec(rows, name) for name in SPECS}


def analyze(d159_path: Path, history_path: Path, game_dir: Path) -> dict:
    d159 = json.loads(d159_path.read_text())
    history = json.loads(history_path.read_text())
    d159_by_id = {int(row["game_id"]): row for row in d159["rows"]}
    history_ids = {int(row["game_id"]) for row in history["rows"]}
    duplicate_d159_ids = len(d159_by_id) != len(d159["rows"])
    rows = []
    failures = []
    identity_mismatches = []
    unknown_updates = []
    score_mismatches = []
    missing = []
    for game_id in sorted(d159_by_id):
        path = game_dir / f"{game_id}.json"
        if not path.exists():
            missing.append(game_id)
            continue
        try:
            game = json.loads(path.read_text())
            seat = current_player(game)
            agents = game.get("agents") or []
            if (
                game.get("gameId") != game_id
                or seat is None
                or seat >= len(agents)
                or agents[seat].get("agentId") != EXPECTED_AGENT
            ):
                identity_mismatches.append(game_id)
                continue
            parser = corpus_parser()
            decoded_map, _, inventory0, inventory1 = parser.parse_frame0(
                game["frames"][0]["view"]
            )
            trajectory, _ = parser.extract_turns(
                game["frames"], inventory0, inventory1
            )
            map_data, states, unknown = decoded_states(game, trajectory)
            if unknown:
                unknown_updates.append({"game_id": game_id, "unknown": unknown})
            board = terrain(map_data)
            opponent = 1 - seat
            final_inventory = states[-1]["inventories"]
            official_scores = [int(value) for value in game["scores"]]
            if (
                score(final_inventory[seat]) != official_scores[seat]
                or score(final_inventory[opponent]) != official_scores[opponent]
            ):
                score_mismatches.append(game_id)
            margin = official_scores[seat] - official_scores[opponent]
            d159_row = d159_by_id[game_id]
            rows.append(
                {
                    "game_id": game_id,
                    "partition": "historical80" if game_id in history_ids else "suffix",
                    "seat": seat,
                    "opponent": d159_row["opponent"],
                    "margin": margin,
                    "outcome": (
                        "catastrophic"
                        if margin <= -100
                        else "ordinary_loss"
                        if margin < 0
                        else "tie"
                        if margin == 0
                        else "win"
                    ),
                    "decoded_states": len(states),
                    "has_iron": bool(board["iron"]),
                    "specs": {
                        name: game_spec_report(
                            states,
                            seat=seat,
                            shack=board["shacks"][seat],
                            has_iron=bool(board["iron"]),
                            spec=spec,
                        )
                        for name, spec in SPECS.items()
                    },
                }
            )
        except Exception as error:  # noqa: BLE001 - preserve a complete audit
            failures.append(
                {"game_id": game_id, "error": f"{type(error).__name__}: {error}"}
            )
    historical = [row for row in rows if row["partition"] == "historical80"]
    suffix = [row for row in rows if row["partition"] == "suffix"]
    cohorts = {
        "historical80_cached": cohort_report(historical),
        "suffix_cached": cohort_report(suffix),
        "all_cached": cohort_report(rows),
    }
    balanced = cohorts["suffix_cached"]["balanced_2202"]
    gate_conditions = {
        "at_least_12_suffix_games_executable_by_200": balanced[
            "games_executable_by_200"
        ]
        >= 12,
        "at_least_8_suffix_games_with_two_turn_window": balanced[
            "games_with_two_turn_window_by_200"
        ]
        >= 8,
        "at_least_6_opponents": balanced["executable_opponents"] >= 6,
        "both_seats": balanced["executable_seats"] == [0, 1],
    }
    integrity_gates = {
        "d159_hash_exact": sha256(d159_path) == EXPECTED_D159_SHA256,
        "d159_has_200_unique_ids": len(d159_by_id) == 200 and not duplicate_d159_ids,
        "at_least_190_cached_games": len(rows) >= 190,
        "at_least_110_cached_suffix_games": len(suffix) >= 110,
        "no_decode_failures": not failures,
        "exact_resident_identity": not identity_mismatches,
        "zero_unknown_updates": not unknown_updates,
        "score_mismatches_only_known_penalties": set(score_mismatches)
        <= KNOWN_SCORE_MISMATCHES,
    }
    integrity_pass = all(integrity_gates.values())
    active_probe_warrant = integrity_pass and all(gate_conditions.values())
    return {
        "schema": "troll-farm-d160a-resident-natural-capital-window-v1",
        "inputs": {
            "d159_sha256": sha256(d159_path),
            "history_sha256": sha256(history_path),
            "expected_agent": EXPECTED_AGENT,
            "maximum_decision_turn": MAX_DECISION_TURN,
            "field_gate_maximum_turn": GATE_MAX_TURN,
            "specs": {name: list(spec) for name, spec in SPECS.items()},
        },
        "coverage": {
            "d159_games": len(d159_by_id),
            "cached_games": len(rows),
            "cached_historical80": len(historical),
            "cached_suffix": len(suffix),
            "missing_cached_game_ids": missing,
            "failures": failures,
            "identity_mismatch_game_ids": identity_mismatches,
            "unknown_updates": unknown_updates,
            "score_mismatch_game_ids": score_mismatches,
        },
        "integrity": {"gates": integrity_gates, "pass": integrity_pass},
        "cohorts": cohorts,
        "field_probe_gate": {
            "spec": "balanced_2202",
            "conditions": gate_conditions,
            "pass": active_probe_warrant,
        },
        "decision": {
            "create_testsession_games": False,
            "active_probe_warrant": active_probe_warrant,
            "construct_opportunistic_train_wrapper": False,
            "next_experiment": (
                "freeze a common-map exact-resident A/B probe"
                if active_probe_warrant
                else "build an exact-resident-fallback funding/controller representation; natural "
                "capital cannot support a production-grade opportunistic TRAIN probe"
            ),
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d159", type=Path, default=DEFAULT_D159)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--game-dir", type=Path, default=DEFAULT_GAME_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = analyze(args.d159, args.history, args.game_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    suffix = payload["cohorts"]["suffix_cached"]
    for name in SPECS:
        report = suffix[name]
        print(
            f"{name}: executable<=200={report['games_executable_by_200']}/"
            f"{report['games']} liquid<=225={report['games_liquid_affordable_by_225']} "
            f"median_min_deficit={report['minimum_deposited_deficit']['median']}"
        )
    print(
        f"integrity={payload['integrity']['pass']} "
        f"field_probe={payload['field_probe_gate']['pass']} saved={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
