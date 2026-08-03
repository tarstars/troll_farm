#!/usr/bin/env python3
"""Teacher-force the locked candidate on every live E7a period-2 counterexample.

The selection comes from the immutable decoded top-15 audit: exact agent/submission rows
whose observed longest period-2 MOVE run is at least six.  Replay payloads are fetched
read-only and kept in memory.  No file under ``data/raw/games`` is read or written.

This is a liveness regression gate on official states, not a counterfactual value test:
candidate commands do not determine the next teacher-forced state.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto import battle_taxonomy as arena
from cgauto.recent_resident_field_census import corpus_parser, decoded_states


CANDIDATE = (
    REPO
    / "local_codex_1/e7a-half-size-logical-simplification/"
    "focused-yamo-bank-convoy-period2-lean-coordination.rs"
)
CANDIDATE_SHA256 = "9a202242afdac6ffbb463ac4caba1cc803376a90f37066767efabc5bb9584290"
AGENT_ID = 6_590_141
SUBMISSION_ID = 41_081_503
REQUIRED_GAME = 897_832_286
VALID_ARITIES = {
    "WAIT": 1,
    "MOVE": 4,
    "CHOP": 2,
    "HARVEST": 2,
    "DROP": 2,
    "PLANT": 3,
    "PICK": 3,
    "MINE": 2,
    "TRAIN": 5,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def perspective_rows(rows: list[str], seat: int) -> list[str]:
    if seat == 0:
        return rows
    translation = str.maketrans({"0": "1", "1": "0"})
    return [row.translate(translation) for row in rows]


def state_text(state: dict, seat: int) -> str:
    opponent = 1 - seat
    lines = [
        " ".join(map(str, state["inventories"][seat])),
        " ".join(map(str, state["inventories"][opponent])),
        str(len(state["plants"])),
    ]
    for plant in state["plants"]:
        lines.append(
            " ".join(
                map(
                    str,
                    (
                        plant["type"],
                        plant["x"],
                        plant["y"],
                        plant["size"],
                        plant["health"],
                        plant["fruits"],
                        plant["cooldown"],
                    ),
                )
            )
        )
    lines.append(str(len(state["units"])))
    for unit in state["units"]:
        lines.append(
            " ".join(
                map(
                    str,
                    (
                        unit["id"],
                        0 if unit["player"] == seat else 1,
                        unit["x"],
                        unit["y"],
                        unit["ms"],
                        unit["cc"],
                        unit["hp"],
                        unit["chop"],
                        *unit["carry"],
                    ),
                )
            )
        )
    return "\n".join(lines) + "\n"


def transcript(map_data: dict, states: list[dict], seat: int, turns: int) -> str:
    rows = perspective_rows(list(map_data["rows"]), seat)
    static = (
        f"{map_data['width']} {map_data['height']}\n"
        + "\n".join(rows)
        + "\n"
    )
    return static + "".join(state_text(state, seat) for state in states[:turns])


def parse_commands(line: str) -> list[str]:
    commands = [
        command.strip()
        for command in re.split(r"[;\n]+", line)
        if command.strip() and not command.strip().upper().startswith("MSG ")
    ]
    for command in commands:
        fields = command.split()
        verb = fields[0].upper() if fields else ""
        if verb not in VALID_ARITIES or len(fields) != VALID_ARITIES[verb]:
            raise ValueError(f"malformed candidate command: {command!r}")
        for value in fields[1:]:
            if verb not in ("PLANT", "PICK") or value != fields[-1]:
                int(value)
    return commands


def longest_period2(lines: list[str]) -> int:
    moves: dict[int, list[tuple[int, tuple[int, int]]]] = defaultdict(list)
    for turn, line in enumerate(lines, 1):
        for command in parse_commands(line):
            fields = command.split()
            if fields[0].upper() == "MOVE":
                moves[int(fields[1])].append(
                    (turn, (int(fields[2]), int(fields[3])))
                )
    longest = 0
    for sequence in moves.values():
        run = 0
        previous_turn = None
        previous = None
        two_back = None
        for turn, target in sequence:
            consecutive = previous_turn is not None and turn == previous_turn + 1
            if consecutive and two_back == target and previous != target:
                run += 1
            elif consecutive and previous != target:
                run = 2
            else:
                run = 1
            longest = max(longest, run)
            previous_turn, two_back, previous = turn, previous, target
    return longest


def compile_candidate(directory: Path) -> Path:
    if sha256(CANDIDATE) != CANDIDATE_SHA256:
        raise RuntimeError("candidate hash mismatch")
    binary = directory / "candidate"
    completed = subprocess.run(
        [
            "rustc",
            "--crate-name",
            "e7a_half_live_period2_candidate",
            "--edition=2021",
            "-O",
            "-Awarnings",
            str(CANDIDATE),
            "-o",
            str(binary),
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        timeout=180,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr[:4000])
    return binary


def select_rows(audit: dict) -> list[dict]:
    rows = [
        row
        for row in audit.get("rows") or []
        if int(row.get("agent_id", -1)) == AGENT_ID
        and int(row.get("submission_id", -1)) == SUBMISSION_ID
        and int(row["movement"]["longest_period2_move_run"]) >= 6
    ]
    rows.sort(key=lambda row: int(row["game_id"]))
    game_ids = [int(row["game_id"]) for row in rows]
    if len(rows) != 25 or len(set(game_ids)) != 25:
        raise RuntimeError(f"expected 25 unique counterexamples, got {len(rows)}")
    if REQUIRED_GAME not in game_ids:
        raise RuntimeError(f"required game {REQUIRED_GAME} is absent")
    return rows


def evaluate_game(binary: Path, selected: dict) -> dict:
    game_id = int(selected["game_id"])
    seat = int(selected["seat"])
    game = arena.call("gameResult/findByGameId", [game_id, None])
    if int(game.get("gameId", -1)) != game_id:
        raise RuntimeError(f"game identity mismatch for {game_id}")
    agents = game.get("agents") or []
    own = [agent for agent in agents if int(agent.get("agentId", -1)) == AGENT_ID]
    if len(own) != 1 or int(own[0].get("index", -1)) != seat:
        raise RuntimeError(f"agent/seat identity mismatch for {game_id}")

    parser = corpus_parser()
    _map0, _units0, inventory0, inventory1 = parser.parse_frame0(
        game["frames"][0]["view"]
    )
    trajectory, _final_inventory = parser.extract_turns(
        game["frames"], inventory0, inventory1
    )
    map_data, states, unknown_updates = decoded_states(game, trajectory)
    usable = min(len(states) - 1, len(trajectory))
    payload = transcript(map_data, states, seat, usable)
    completed = subprocess.run(
        [str(binary)],
        cwd=REPO,
        input=payload,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode:
        raise RuntimeError(
            f"candidate exited {completed.returncode} on {game_id}: "
            f"{completed.stderr[:1000]}"
        )
    if completed.stderr:
        raise RuntimeError(f"candidate stderr on {game_id}: {completed.stderr[:1000]}")
    lines = completed.stdout.splitlines()
    if len(lines) != usable:
        raise RuntimeError(
            f"command coverage mismatch on {game_id}: {len(lines)} != {usable}"
        )
    candidate_period2 = longest_period2(lines)
    return {
        "game_id": game_id,
        "seat": seat,
        "opponent": selected["opponent"],
        "turns": usable,
        "unknown_diff_updates": unknown_updates,
        "observed_live_period2": int(
            selected["movement"]["longest_period2_move_run"]
        ),
        "candidate_teacher_forced_period2": candidate_period2,
        "candidate_command_lines": len(lines),
        "candidate_stderr_bytes": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    audit = json.loads(arguments.audit.read_text())
    selected = select_rows(audit)
    with tempfile.TemporaryDirectory(prefix="e7a-live-period2-") as directory:
        binary = compile_candidate(Path(directory))
        rows = [evaluate_game(binary, row) for row in selected]
    candidate_maximum = max(
        row["candidate_teacher_forced_period2"] for row in rows
    )
    result = {
        "schema": "troll-farm-e7a-half-size-live-period2-counterexamples-v1",
        "evidence_boundary": (
            "teacher-forced liveness regression on official states; candidate commands "
            "do not determine next states; not a counterfactual value estimate"
        ),
        "selection": {
            "audit_path": str(arguments.audit),
            "audit_sha256": sha256(arguments.audit),
            "agent_id": AGENT_ID,
            "submission_id": SUBMISSION_ID,
            "observed_period2_minimum": 6,
            "required_game": REQUIRED_GAME,
            "games": len(rows),
        },
        "candidate": {
            "path": str(CANDIDATE.relative_to(REPO)),
            "bytes": CANDIDATE.stat().st_size,
            "sha256": CANDIDATE_SHA256,
        },
        "quality": {
            "games_fetched": len(rows),
            "unknown_diff_updates": sum(
                row["unknown_diff_updates"] for row in rows
            ),
            "command_lines": sum(row["candidate_command_lines"] for row in rows),
            "stderr_bytes": sum(row["candidate_stderr_bytes"] for row in rows),
        },
        "metrics": {
            "observed_live_maximum_period2": max(
                row["observed_live_period2"] for row in rows
            ),
            "candidate_maximum_period2": candidate_maximum,
            "candidate_games_period2_ge6": sum(
                row["candidate_teacher_forced_period2"] >= 6 for row in rows
            ),
        },
        "gates": {
            "all_25_counterexamples": len(rows) == 25,
            "required_game_present": any(
                row["game_id"] == REQUIRED_GAME for row in rows
            ),
            "zero_unknown_diff_updates": all(
                row["unknown_diff_updates"] == 0 for row in rows
            ),
            "zero_candidate_stderr": all(
                row["candidate_stderr_bytes"] == 0 for row in rows
            ),
            "no_candidate_period2_ge6": candidate_maximum < 6,
        },
        "rows": rows,
    }
    result["verdict"] = (
        "LIVE_PERIOD2_PACKET_PASS"
        if all(result["gates"].values())
        else "LIVE_PERIOD2_PACKET_FAIL"
    )
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "games": len(rows),
                "candidate_maximum_period2": candidate_maximum,
                "failed_gates": [
                    name for name, passed in result["gates"].items() if not passed
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if result["verdict"] == "LIVE_PERIOD2_PACKET_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
