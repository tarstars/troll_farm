#!/usr/bin/env python3
"""Audit the scope and branching premise of an exact endgame solver.

The empirical component runs the exact live resident on reused maps and captures
public states at three late turns.  At each root it enumerates exact distinct
same-side position outcomes from movement-only command vectors.  The product
across both players is a strict lower bound on full simultaneous one-ply state
branching because every non-MOVE action is omitted.

This is a read-only feasibility census, not a solver, policy, candidate, or
Arena predictor.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
import hashlib
from itertools import product
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import bfs_distances  # noqa: E402
from cgauto.e4_orchard_mother_tie_audit import (  # noqa: E402
    canonical_bytes,
    compile_runtime_shim,
    LIVE_SHA256,
    LIVE_SOURCE,
    OPPONENT_NAMES,
    rows_sha256,
    SACRED_SHA256,
    SACRED_SOURCE,
    sha256_bytes,
    sha256_path,
    terminal_state_payload,
    update_stream_hash,
    validate_commands,
)
from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from cgauto.offline_policy_league import OPPONENT_SOURCES  # noqa: E402
from sim.engine import has_stalled, stall_reason, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

SEEDS = tuple(range(60))
SNAPSHOT_TURNS = (251, 276, 291)


def endpoint_options(game, unit) -> tuple[tuple[int, int], ...]:
    """All cells a direct MOVE can reach this turn, including staying put."""

    distances = bfs_distances(game.walkable, [unit.pos])
    return tuple(
        sorted(
            cell
            for cell, distance in distances.items()
            if distance <= unit.ms
        )
    )


def resolve_player_positions(
    units,
    targets: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int, int], ...]:
    """Reproduce ``apply_moves`` for one player's direct endpoint vector."""

    ordered = sorted(units, key=lambda unit: unit.id)
    if len(ordered) != len(targets):
        raise ValueError("one movement target is required for every unit")
    positions = {unit.id: unit.pos for unit in ordered}
    target_by_id = {
        unit.id: target for unit, target in zip(ordered, targets, strict=True)
    }
    occupied = set(positions.values())
    movers = [
        unit.id
        for unit in sorted(ordered, key=lambda unit: -unit.id)
        if target_by_id[unit.id] != positions[unit.id]
    ]
    progress = True
    resolve_blocking = False
    while progress:
        progress = False
        frequencies = Counter(target_by_id[unit_id] for unit_id in movers)
        for unit_id in list(movers):
            cell = target_by_id[unit_id]
            if (
                (resolve_blocking or frequencies[cell] == 1)
                and cell not in occupied
            ):
                occupied.discard(positions[unit_id])
                occupied.add(cell)
                positions[unit_id] = cell
                movers.remove(unit_id)
                progress = True
                resolve_blocking = False
        if progress:
            continue

        position_to_unit = {positions[unit_id]: unit_id for unit_id in movers}
        for start in list(movers):
            path = [start]
            while True:
                next_unit = position_to_unit.get(target_by_id[path[-1]])
                if next_unit is None:
                    break
                if next_unit == path[0]:
                    for unit_id in path:
                        positions[unit_id] = target_by_id[unit_id]
                        movers.remove(unit_id)
                    progress = True
                    break
                if next_unit in path:
                    break
                path.append(next_unit)
            if progress:
                break
        if not progress and not resolve_blocking:
            resolve_blocking = True
            progress = True

    return tuple(
        (unit.id, positions[unit.id][0], positions[unit.id][1])
        for unit in ordered
    )


def movement_outcome_summary(game, player: int) -> dict:
    units = sorted(
        (unit for unit in game.units if unit.player == player),
        key=lambda unit: unit.id,
    )
    choices = [endpoint_options(game, unit) for unit in units]
    intent_vectors = math.prod(len(options) for options in choices)
    outcomes = {
        resolve_player_positions(units, targets)
        for targets in product(*choices)
    }
    return {
        "player": player,
        "unit_ids": [unit.id for unit in units],
        "movement_speeds": [unit.ms for unit in units],
        "endpoint_option_counts": [len(options) for options in choices],
        "movement_intent_vectors": intent_vectors,
        "distinct_position_outcomes": len(outcomes),
    }


def root_payload(
    game,
    seed: int,
    opponent_name: str,
    policy_seat: int,
) -> dict:
    movement = [
        movement_outcome_summary(game, player) for player in (0, 1)
    ]
    own = movement[policy_seat]
    opponent = movement[1 - policy_seat]
    units = [
        sorted(
            (unit for unit in game.units if unit.player == player),
            key=lambda unit: unit.id,
        )
        for player in (0, 1)
    ]
    return {
        "seed": seed,
        "opponent": opponent_name,
        "policy_seat": policy_seat,
        "turn": game.turn,
        "remaining_nominal_turns": 301 - game.turn,
        "public_state_sha256": sha256_bytes(
            canonical_bytes(terminal_state_payload(game))
        ),
        "walkable_cells": len(game.walkable),
        "live_plants": sum(plant.health > 0 for plant in game.plants),
        "occupied_cells": len({unit.pos for unit in game.units}),
        "unit_counts": [len(player_units) for player_units in units],
        "movement_speeds": [
            [unit.ms for unit in player_units] for player_units in units
        ],
        "positive_inventory_slots": [
            sum(value > 0 for value in game.inventories[player])
            for player in (0, 1)
        ],
        "movement": movement,
        "own_movement_outcomes": own["distinct_position_outcomes"],
        "opponent_movement_outcomes": opponent[
            "distinct_position_outcomes"
        ],
        "joint_movement_only_state_outcomes": (
            own["distinct_position_outcomes"]
            * opponent["distinct_position_outcomes"]
        ),
    }


def run_game(
    seed: int,
    opponent_name: str,
    policy_seat: int,
    policy_binary: Path,
    opponent_binary: Path,
) -> dict:
    game = generate_bronze(seed)
    binaries = (
        (policy_binary, opponent_binary)
        if policy_seat == 0
        else (opponent_binary, policy_binary)
    )
    sessions = [
        BotSession(binaries[0], game, 0),
        BotSession(binaries[1], game, 1),
    ]
    stream_hashes = [hashlib.sha256(), hashlib.sha256()]
    command_counts = [Counter(), Counter()]
    roots = []
    turns_until_end = 0
    ended_by_stall = False
    stderrs = ["", ""]
    try:
        while game.turn <= 300:
            if game.turn in SNAPSHOT_TURNS:
                roots.append(
                    root_payload(
                        copy.deepcopy(game),
                        seed,
                        opponent_name,
                        policy_seat,
                    )
                )
            turn = game.turn
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            for seat in (0, 1):
                validate_commands(commands[seat])
                update_stream_hash(stream_hashes[seat], turn, lines[seat])
                command_counts[seat].update(
                    command.split()[0].upper()
                    for command in commands[seat]
                )
            step(game, commands[0], commands[1])
            ended_by_stall, turns_until_end = has_stalled(
                game, turns_until_end
            )
            if ended_by_stall:
                break
    finally:
        for seat, session in enumerate(sessions):
            stderrs[seat] = session.close()

    if any(stderrs):
        raise RuntimeError(
            f"unexpected stderr bytes: {[len(value) for value in stderrs]}"
        )
    reason = (
        (stall_reason(game, turns_until_end) or "stalled")
        if ended_by_stall
        else "turn_cap"
    )
    for root in roots:
        root["terminal_turn"] = game.turn - 1
        root["terminal_reason"] = reason
    return {
        "seed": seed,
        "opponent": opponent_name,
        "policy_seat": policy_seat,
        "terminal_turn": game.turn - 1,
        "terminal_reason": reason,
        "ended_by_stall": ended_by_stall,
        "action_stream_sha256": [
            hasher.hexdigest() for hasher in stream_hashes
        ],
        "command_counts": [
            dict(sorted(counts.items())) for counts in command_counts
        ],
        "terminal_state_sha256": sha256_bytes(
            canonical_bytes(terminal_state_payload(game))
        ),
        "malformed_commands": 0,
        "unexpected_stderr_bytes": 0,
        "roots": roots,
    }


def percentile(values: list[int], probability: float):
    if not values:
        return None
    ordered = sorted(values)
    index = math.ceil(probability * len(ordered)) - 1
    return ordered[max(0, index)]


def root_group_summary(rows: list[dict], turn: int) -> dict:
    selected = [row for row in rows if row["turn"] == turn]
    joint = [row["joint_movement_only_state_outcomes"] for row in selected]
    own = [row["own_movement_outcomes"] for row in selected]
    opponent = [row["opponent_movement_outcomes"] for row in selected]
    unit_totals = [sum(row["unit_counts"]) for row in selected]
    return {
        "turn": turn,
        "root_count": len(selected),
        "game_reach_rate": len(selected) / 720,
        "remaining_nominal_turns": 301 - turn,
        "joint_movement_outcomes": {
            "minimum": min(joint, default=None),
            "median": statistics.median(joint) if joint else None,
            "p90": percentile(joint, 0.9),
            "maximum": max(joint, default=None),
            "above_4096": sum(value > 4096 for value in joint),
        },
        "own_movement_outcomes": {
            "minimum": min(own, default=None),
            "median": statistics.median(own) if own else None,
            "maximum": max(own, default=None),
        },
        "opponent_movement_outcomes": {
            "minimum": min(opponent, default=None),
            "median": statistics.median(opponent) if opponent else None,
            "maximum": max(opponent, default=None),
        },
        "total_units": {
            "minimum": min(unit_totals, default=None),
            "median": statistics.median(unit_totals)
            if unit_totals
            else None,
            "maximum": max(unit_totals, default=None),
        },
        "family_root_counts": {
            opponent_name: sum(
                row["opponent"] == opponent_name for row in selected
            )
            for opponent_name in OPPONENT_NAMES
        },
    }


def structural_classification() -> dict:
    objects = {
        "full_simultaneous_game": {
            "objective": "terminal score margin",
            "both_players_primitive_actions": True,
            "referee_chance_nodes_required": True,
            "realized_referee_rng_visible_to_bot": False,
            "opponent_process_clone_required": False,
            "distinct_from_closed_candidate_interfaces": True,
            "deployable_50ms": False,
            "reason": (
                "full exactness requires simultaneous opponent and referee-chance "
                "branching over the remaining horizon"
            ),
        },
        "known_policy_continuation": {
            "objective": "terminal score margin against one local policy",
            "bot_session_serializable": False,
            "bot_session_forkable": False,
            "prefix_replay_possible": True,
            "exact_counterfactual_clone": False,
            "deployable_50ms": False,
            "reason": (
                "external bot processes expose stdin/stdout only; every branch "
                "requires restart and prefix replay"
            ),
        },
        "resident_candidate_restriction": {
            "full_primitive_action_space": False,
            "exact_game_solver": False,
            "overlaps": ["N4", "D36", "S3"],
            "novel": False,
            "reason": (
                "restricting to resident candidate pairs or overlays is a "
                "closed/owned approximation, not exact S1"
            ),
        },
        "known_latency_boundaries_ms_p95": {
            "online_shared_state_mc": 279.46,
            "primitive_move_residual": 92.852,
            "live_turn_budget": 50.0,
        },
    }
    return {
        "verdict": "FULL_EXACT_INFEASIBLE",
        "objects": objects,
        "reason": (
            "the only distinct object is the full simultaneous stochastic game; "
            "the known-policy object is not clonable and the tractable candidate "
            "restriction duplicates closed interfaces"
        ),
    }


def validate_numeric_finiteness(value) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise RuntimeError(f"nonfinite value encountered: {value}")
    if isinstance(value, dict):
        for child in value.values():
            validate_numeric_finiteness(child)
    elif isinstance(value, list):
        for child in value:
            validate_numeric_finiteness(child)


def run_audit(jobs: int) -> dict:
    source_hash = sha256_path(LIVE_SOURCE)
    sacred_hash = sha256_path(SACRED_SOURCE)
    if source_hash != LIVE_SHA256:
        raise RuntimeError(f"live source hash mismatch: {source_hash}")
    if sacred_hash != SACRED_SHA256:
        raise RuntimeError(f"sacred source hash mismatch: {sacred_hash}")

    game_rows = []
    with tempfile.TemporaryDirectory(
        prefix="s1-endgame-solver-feasibility-"
    ) as directory:
        temp = Path(directory)
        binaries = {}
        compile_source(LIVE_SOURCE, temp / "control", "s1_control")
        binaries["control"] = temp / "control"
        for index, opponent_name in enumerate(OPPONENT_NAMES):
            compile_source(
                OPPONENT_SOURCES[opponent_name],
                temp / opponent_name,
                f"s1_opponent_{index}_{opponent_name}",
            )
            binaries[opponent_name] = temp / opponent_name
        runtime_shim = compile_runtime_shim(temp)
        print(
            "compiled control, six opponents, and deterministic runtime",
            flush=True,
        )

        previous_preload = os.environ.get("LD_PRELOAD")
        os.environ["LD_PRELOAD"] = (
            str(runtime_shim)
            if not previous_preload
            else f"{runtime_shim}:{previous_preload}"
        )
        try:
            tasks = [
                (seed, opponent_name, policy_seat)
                for seed in SEEDS
                for opponent_name in OPPONENT_NAMES
                for policy_seat in (0, 1)
            ]
            with ThreadPoolExecutor(max_workers=jobs) as executor:
                futures = {
                    executor.submit(
                        run_game,
                        seed,
                        opponent_name,
                        policy_seat,
                        binaries["control"],
                        binaries[opponent_name],
                    ): (seed, opponent_name, policy_seat)
                    for seed, opponent_name, policy_seat in tasks
                }
                for completed, future in enumerate(as_completed(futures), 1):
                    game_rows.append(future.result())
                    if completed % 60 == 0 or completed == len(tasks):
                        print(
                            f"completed {completed}/{len(tasks)} control games",
                            flush=True,
                        )
        finally:
            if previous_preload is None:
                os.environ.pop("LD_PRELOAD", None)
            else:
                os.environ["LD_PRELOAD"] = previous_preload

    game_rows.sort(
        key=lambda row: (row["seed"], row["opponent"], row["policy_seat"])
    )
    root_rows = [
        root for game in game_rows for root in game.pop("roots")
    ]
    root_rows.sort(
        key=lambda row: (
            row["turn"],
            row["seed"],
            row["opponent"],
            row["policy_seat"],
        )
    )
    game_keys = [
        (row["seed"], row["opponent"], row["policy_seat"])
        for row in game_rows
    ]
    root_keys = [
        (
            row["seed"],
            row["opponent"],
            row["policy_seat"],
            row["turn"],
        )
        for row in root_rows
    ]
    coverage = {
        "games": len(game_rows),
        "unique_game_keys": len(set(game_keys)),
        "roots": len(root_rows),
        "unique_root_keys": len(set(root_keys)),
        "complete": len(game_rows) == 720 and len(set(game_keys)) == 720,
    }
    if not coverage["complete"]:
        raise RuntimeError(f"coverage failed: {coverage}")
    if len(root_keys) != len(set(root_keys)):
        raise RuntimeError("duplicate snapshot root key")
    if any(
        row["malformed_commands"] or row["unexpected_stderr_bytes"]
        for row in game_rows
    ):
        raise RuntimeError("command or stderr integrity failed")
    if any(row["turn"] not in SNAPSHOT_TURNS for row in root_rows):
        raise RuntimeError("snapshot captured outside the frozen turn set")

    census = {
        "by_turn": [
            root_group_summary(root_rows, turn) for turn in SNAPSHOT_TURNS
        ],
        "all_roots": {
            "count": len(root_rows),
            "joint_movement_outcome_minimum": min(
                (
                    row["joint_movement_only_state_outcomes"]
                    for row in root_rows
                ),
                default=None,
            ),
            "joint_movement_outcome_median": (
                statistics.median(
                    row["joint_movement_only_state_outcomes"]
                    for row in root_rows
                )
                if root_rows
                else None
            ),
            "joint_movement_outcome_maximum": max(
                (
                    row["joint_movement_only_state_outcomes"]
                    for row in root_rows
                ),
                default=None,
            ),
        },
    }
    payload = {
        "schema": 1,
        "scope": (
            "read-only exact-live endgame solver scope and movement-only "
            "branching audit on reused maps; not a solver, policy, candidate, "
            "or Arena predictor"
        ),
        "jobs": jobs,
        "sources": {
            "control": {
                "path": str(LIVE_SOURCE.relative_to(REPO)),
                "sha256": source_hash,
            },
            "sacred_resident": {
                "path": str(SACRED_SOURCE.relative_to(REPO)),
                "sha256": sacred_hash,
            },
            "opponents": {
                name: {
                    "path": str(OPPONENT_SOURCES[name].relative_to(REPO)),
                    "sha256": sha256_path(OPPONENT_SOURCES[name]),
                }
                for name in OPPONENT_NAMES
            },
        },
        "panel": {
            "seeds": list(SEEDS),
            "opponents": list(OPPONENT_NAMES),
            "policy_seats": [0, 1],
            "snapshot_turns": list(SNAPSHOT_TURNS),
        },
        "coverage": coverage,
        "classification": structural_classification(),
        "census": census,
        "hashes": {
            "game_rows_sha256": rows_sha256(game_rows),
            "root_rows_sha256": rows_sha256(root_rows),
        },
        "game_rows": game_rows,
        "root_rows": root_rows,
    }
    validate_numeric_finiteness(payload)
    return payload


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def self_test() -> None:
    from sim.state import SimUnit

    units = [
        SimUnit(1, 0, 0, 0, 1, 1, 1, 1, [0] * 6),
        SimUnit(2, 0, 1, 0, 1, 1, 1, 1, [0] * 6),
    ]
    assert resolve_player_positions(units, ((1, 0), (0, 0))) == (
        (1, 1, 0),
        (2, 0, 0),
    )
    collision = resolve_player_positions(units, ((0, 1), (0, 1)))
    assert collision == ((1, 0, 0), (2, 0, 1))
    classification = structural_classification()
    assert classification["verdict"] == "FULL_EXACT_INFEASIBLE"
    assert not classification["objects"]["resident_candidate_restriction"][
        "novel"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "s1-endgame-solver-feasibility-result-2026-07-31.json",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    if args.self_test:
        self_test()
        print("self-test: ok")
        return 0

    payload = run_audit(args.jobs)
    save(args.output, payload)
    census = payload["census"]["all_roots"]
    print(
        f"verdict: {payload['classification']['verdict']}; "
        f"roots={census['count']}; "
        f"movement median={census['joint_movement_outcome_median']}; "
        f"maximum={census['joint_movement_outcome_maximum']}",
        flush=True,
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
