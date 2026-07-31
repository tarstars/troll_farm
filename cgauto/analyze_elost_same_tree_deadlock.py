#!/usr/bin/env python3
"""Reconstruct the exact Elost same-tree occupancy deadlock.

The audit is intentionally one-game and read-only with respect to Arena. It caches the
immutable game under external-backed storage, decodes official states, proves source
reproduction, and instruments the existing collision resolver without changing stdout.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import battle_taxonomy as arena
from cgauto.idle_harvest_study import (
    compile_source,
    grid_text,
    run_batch,
    turn_text,
)
from cgauto.recent_resident_field_census import (
    corpus_parser,
    current_player,
    decoded_states,
    score,
)
from cgauto.replay_conformance import action_commands
from cgauto.replay_state import to_game_state
from cgauto.top_player_opening_analysis import assigned_unit_commands


REPO = Path(__file__).resolve().parent.parent
GAME_ID = 897556967
OUR_AGENT = 6585765
OUR_SUBMISSION = 41071067
OPPONENT_AGENT = 6579290
OPPONENT_SUBMISSION = 40706516
OUR_SEAT = 1
OCCUPANT_ID = 1
MOVER_ID = 2
TREE_CELL = (19, 6)

EXTERNAL_DIR = REPO / "data/external/elost-same-tree-occupancy-deadlock"
RAW_CACHE = EXTERNAL_DIR / f"game-{GAME_ID}.json"
TRAJECTORY_CACHE = EXTERNAL_DIR / f"trajectory-{GAME_ID}.jsonl"
RESULT_JSON = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "elost-same-tree-occupancy-deadlock-result-2026-07-31.json"
)
RESULT_MD = RESULT_JSON.with_suffix(".md")

CURRENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs"
)
TENT_PARENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585578-owner-tent-proximity-denial-split-slim.min.rs"
)
FAR_PARENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs"
)

RESOLVER_ANCHOR = (
    "fn resolve_move_conflicts_with_priority_and_forbidden(view:&GameState,"
    "commands:&mut[String],priority_ids:&BTreeSet<i32>,"
    "forbidden_for_non_priority:&BTreeSet<Cell>,){"
)
RESOLVER_PROBE = (
    RESOLVER_ANCHOR
    + 'if view.turn>=55&&view.turn<=69{eprintln!("@RESOLVE t={} before={:?}",'
    "view.turn,commands);}"
)
PROBE_RE = re.compile(r"^@RESOLVE t=(\d+) before=(\[.*\])$")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            result.update(block)
    return result.hexdigest()


def fetch_game() -> dict[str, Any]:
    if RAW_CACHE.exists():
        game = json.loads(RAW_CACHE.read_text(encoding="utf-8"))
    else:
        game = arena.call("gameResult/findByGameId", [GAME_ID, None])
        atomic_write(RAW_CACHE, canonical_json(game))
    if int(game.get("gameId") or -1) != GAME_ID:
        raise ValueError(f"requested game {GAME_ID}, received {game.get('gameId')}")
    return game


def exact_stream(
    game: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    if current_player(game) != OUR_SEAT:
        raise ValueError(f"resident seat mismatch: expected {OUR_SEAT}")
    agents = game.get("agents") or []
    identity = {int(row["index"]): int(row["agentId"]) for row in agents}
    if identity != {0: OPPONENT_AGENT, 1: OUR_AGENT}:
        raise ValueError(f"exact-agent mismatch: {identity}")
    if any(row.get("valid") is not True for row in agents):
        raise ValueError("one or both agents are invalid")

    parser = corpus_parser()
    _, _, inventory0, inventory1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, _ = parser.extract_turns(
        game["frames"], inventory0, inventory1
    )
    map_data, states, unknown = decoded_states(game, trajectory)
    if unknown:
        raise ValueError(f"unknown official diff updates: {unknown}")
    usable = min(len(trajectory), len(states) - 1)
    if usable != 300:
        raise ValueError(f"expected 300 turns, received {usable}")
    views = [to_game_state(map_data, state) for state in states[:usable]]
    stream = grid_text(views[0], OUR_SEAT) + "".join(
        turn_text(view, OUR_SEAT) for view in views
    )
    atomic_write(
        TRAJECTORY_CACHE,
        "".join(canonical_json(row) for row in trajectory[:usable]),
    )
    return trajectory[:usable], states[: usable + 1], stream


def unit_commands(
    state: dict[str, Any], row: dict[str, Any]
) -> dict[int, str]:
    units = [
        unit for unit in state["units"] if int(unit["player"]) == OUR_SEAT
    ]
    return assigned_unit_commands(
        action_commands(row.get(f"commands{OUR_SEAT}")), units
    )


def incident_rows(
    trajectory: list[dict[str, Any]], states: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = []
    for turn in range(55, 70):
        state = states[turn - 1]
        next_state = states[turn]
        units = {
            int(unit["id"]): unit
            for unit in state["units"]
            if int(unit["player"]) == OUR_SEAT
        }
        next_units = {
            int(unit["id"]): unit
            for unit in next_state["units"]
            if int(unit["player"]) == OUR_SEAT
        }
        plants = {
            (int(plant["x"]), int(plant["y"])): plant
            for plant in state["plants"]
        }
        commands = unit_commands(state, trajectory[turn - 1])
        occupant = units[OCCUPANT_ID]
        mover = units[MOVER_ID]
        plant = plants.get(TREE_CELL)
        rows.append(
            {
                "turn": turn,
                "occupant_position": [int(occupant["x"]), int(occupant["y"])],
                "occupant_stats": [
                    int(occupant[key]) for key in ("ms", "cc", "hp", "chop")
                ],
                "occupant_carry": [int(value) for value in occupant["carry"]],
                "occupant_command": commands[OCCUPANT_ID],
                "mover_position": [int(mover["x"]), int(mover["y"])],
                "mover_next_position": [
                    int(next_units[MOVER_ID]["x"]),
                    int(next_units[MOVER_ID]["y"]),
                ],
                "mover_stats": [
                    int(mover[key]) for key in ("ms", "cc", "hp", "chop")
                ],
                "mover_carry": [int(value) for value in mover["carry"]],
                "mover_command": commands[MOVER_ID],
                "tree": (
                    None
                    if plant is None
                    else {
                        "type": plant["type"],
                        "health": int(plant["health"]),
                        "size": int(plant["size"]),
                        "fruits": int(plant["fruits"]),
                    }
                ),
            }
        )
    return rows


def normalized(line: str) -> list[str]:
    return sorted(action_commands(line))


def compile_outputs(
    source: Path, stream: str, recorded: list[str], label: str, root: Path
) -> dict[str, Any]:
    binary = root / label
    compile_source(source, binary, f"elost_{label}_20260731")
    output, stderr = run_batch(binary, stream)
    matches = [
        turn
        for turn, (actual, expected) in enumerate(
            zip(output, recorded), 1
        )
        if normalized(actual) == normalized(expected)
    ]
    return {
        "source": str(source.relative_to(REPO)),
        "source_sha256": digest(source),
        "stdout_lines": len(output),
        "recorded_command_matches": len(matches),
        "first_divergence_turn": next(
            (
                turn
                for turn, (actual, expected) in enumerate(
                    zip(output, recorded), 1
                )
                if normalized(actual) != normalized(expected)
            ),
            None,
        ),
        "stderr": stderr,
    }


def resolver_probe(source: Path, stream: str, root: Path) -> list[dict[str, Any]]:
    text = source.read_text(encoding="utf-8")
    if text.count(RESOLVER_ANCHOR) != 1:
        raise ValueError(
            f"expected one resolver anchor, found {text.count(RESOLVER_ANCHOR)}"
        )
    probe_source = root / "resolver_probe.rs"
    probe_source.write_text(
        text.replace(RESOLVER_ANCHOR, RESOLVER_PROBE, 1), encoding="utf-8"
    )
    binary = root / "resolver_probe"
    compile_source(probe_source, binary, "elost_resolver_probe_20260731")
    _, stderr = run_batch(binary, stream)
    rows = []
    for line in stderr.splitlines():
        match = PROBE_RE.match(line)
        if match:
            rows.append(
                {
                    "turn": int(match.group(1)),
                    "commands_before_collision_resolution": json.loads(
                        match.group(2)
                    ),
                }
            )
    return rows


def analyze(game: dict[str, Any]) -> dict[str, Any]:
    trajectory, states, stream = exact_stream(game)
    recorded = [
        row.get(f"commands{OUR_SEAT}") or "" for row in trajectory
    ]
    rows = incident_rows(trajectory, states)
    with tempfile.TemporaryDirectory(prefix="elost-deadlock-") as directory:
        root = Path(directory)
        reproductions = {
            "current": compile_outputs(
                CURRENT, stream, recorded, "current", root
            ),
            "tent_parent": compile_outputs(
                TENT_PARENT, stream, recorded, "tent_parent", root
            ),
            "far_parent": compile_outputs(
                FAR_PARENT, stream, recorded, "far_parent", root
            ),
        }
        probe = resolver_probe(CURRENT, stream, root)

    for result in reproductions.values():
        if (
            result["recorded_command_matches"] != 300
            or result["first_divergence_turn"] is not None
            or result["stderr"]
        ):
            raise ValueError(f"source reproduction failed: {result}")

    wait_turns = [
        row["turn"] for row in rows if row["occupant_command"] == "WAIT"
    ]
    ping_pong_rows = [row for row in rows if 61 <= row["turn"] <= 68]
    ping_pong_positions = [
        tuple(row["mover_position"]) for row in ping_pong_rows
    ]
    expected_positions = [
        (18, 5),
        (18, 6),
        (18, 5),
        (18, 6),
        (18, 5),
        (18, 6),
        (18, 5),
        (18, 6),
    ]
    if wait_turns != list(range(58, 68)):
        raise ValueError(f"unexpected WAIT interval: {wait_turns}")
    if ping_pong_positions != expected_positions:
        raise ValueError(f"unexpected ping-pong states: {ping_pong_positions}")
    high_target = {
        row["turn"]: row["commands_before_collision_resolution"]
        for row in probe
    }
    for turn in range(58, 68):
        if high_target.get(turn) != ["WAIT", "MOVE 2 19 6"]:
            raise ValueError(
                f"unexpected pre-resolver pair at turn {turn}: "
                f"{high_target.get(turn)}"
            )

    final_scores = [score(inventory) for inventory in states[-1]["inventories"]]
    return {
        "schema": "troll-farm-elost-same-tree-deadlock-v1",
        "game": {
            "game_id": GAME_ID,
            "resident_agent_id": OUR_AGENT,
            "resident_submission_id": OUR_SUBMISSION,
            "resident_seat": OUR_SEAT,
            "resident_score": final_scores[OUR_SEAT],
            "opponent": "Elost",
            "opponent_agent_id": OPPONENT_AGENT,
            "opponent_submission_id": OPPONENT_SUBMISSION,
            "opponent_seat": 1 - OUR_SEAT,
            "opponent_score": final_scores[1 - OUR_SEAT],
            "valid": True,
            "turns": len(trajectory),
            "unknown_diff_updates": 0,
            "raw_path": str(RAW_CACHE.relative_to(REPO)),
            "raw_sha256": digest(RAW_CACHE),
            "trajectory_path": str(TRAJECTORY_CACHE.relative_to(REPO)),
            "trajectory_sha256": digest(TRAJECTORY_CACHE),
        },
        "incident": {
            "tree_cell": list(TREE_CELL),
            "tree_type": "LEMON",
            "occupant_unit_id": OCCUPANT_ID,
            "occupant_stats": [1, 1, 1, 1],
            "occupant_full_wood": 1,
            "occupant_chop_before": [55, 56, 57],
            "occupant_wait_first": 58,
            "occupant_wait_last": 67,
            "occupant_wait_commands": 10,
            "occupant_resume_chop": 68,
            "mover_unit_id": MOVER_ID,
            "mover_stats": [2, 1, 0, 2],
            "mover_full_wood": 1,
            "same_tree_high_target_first": 58,
            "same_tree_high_target_last": 67,
            "same_tree_high_target_commands": 10,
            "ping_pong_state_first": 61,
            "ping_pong_state_last": 68,
            "ping_pong_states": 8,
            "ping_pong_cells": [[18, 5], [18, 6]],
            "root_cause": (
                "the pair selector gives the sole far-denial tree to the faster "
                "off-tree chopper while the capable on-tree unit takes WAIT; "
                "single-turn collision detours then alternate"
            ),
            "inherited_from_far_denial_parent": True,
        },
        "source_reproduction": reproductions,
        "resolver_probe": probe,
        "rows": rows,
        "scientific_boundary": (
            "exact mechanism evidence only; no terminal-value estimate"
        ),
    }


def report(result: dict[str, Any]) -> str:
    game = result["game"]
    incident = result["incident"]
    return f"""# Elost same-tree occupancy deadlock

Date: 2026-07-31
Task: `20260731-elost-same-tree-occupancy-deadlock`
Verdict: **exact inherited same-tree assignment/collision loop**

## Exact game

- Game `{game['game_id']}`, resident `{game['resident_agent_id']}` /
  `{game['resident_submission_id']}` seat {game['resident_seat']}, valid
  {game['resident_score']}–{game['opponent_score']} loss to Elost
  `{game['opponent_agent_id']}` / `{game['opponent_submission_id']}`.
- 300 turns, zero unknown official diff updates.
- Raw SHA-256 `{game['raw_sha256']}`.
- Trajectory SHA-256 `{game['trajectory_sha256']}`.

## Exact failure

Resident unit 1 (stats 1/1/1/1) is full with one wood on the LEMON at `(19,6)`.
It CHOPs on turns 55–57, then emits ten consecutive WAITs on turns 58–67.
Resident unit 2 (stats 2/1/0/2), also full with one wood, is assigned that same tree
before collision resolution on every turn 58–67.

After approaching, unit 2 alternates between `(18,5)` and `(18,6)` across eight
decision states on turns 61–68. The selector's exact pre-resolver pair is
`WAIT` plus `MOVE 2 19 6`; collision resolution prevents co-occupancy but its
single-turn detour does not reserve the capable on-tree worker's target. Unit 1 resumes
`CHOP 1` only on turn 68.

The current sticky-bank artifact, its tent-proximity parent, and the far-denial parent
each reproduce all 300 recorded command lines with zero stderr. The loop is therefore
inherited and is not caused by sticky banking.

## Narrow correction boundary

When a capable own worker already occupies a live tree, another worker must not receive
that tree's chop candidate for the current decision. This preserves the on-site worker's
CHOP candidate and prevents the selector from replacing it with `WAIT + off-tree MOVE`.
It is a same-tree ownership/compatibility rule, not a global oscillation tie-break or a
tree-order/value claim. Local materialization and focused validation may follow; no Arena
action follows from this audit.
"""


def main() -> int:
    result = analyze(fetch_game())
    atomic_write(RESULT_JSON, json.dumps(result, indent=2) + "\n")
    atomic_write(RESULT_MD, report(result))
    print(
        "elost-deadlock:",
        f"game={GAME_ID}",
        "waits=10",
        "same-tree-targets=10",
        "ping-pong-states=8",
        "reproductions=3x300",
    )
    print(f"wrote {RESULT_JSON}")
    print(f"wrote {RESULT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
