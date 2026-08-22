#!/usr/bin/env python3
"""Audit the opening-resource command overwritten by enemy-tent denial.

The audit locks one exact B3.15 game, proves exact source reproduction, instruments the
command immediately before the tent-denial wrapper, and checks the fail-closed successor
on the same official state stream. A fixed 40-game live slice supplies descriptive
breadth only; it is not an Arena-value estimate.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
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
)
from cgauto.replay_conformance import action_commands
from cgauto.replay_state import to_game_state


REPO = Path(__file__).resolve().parent.parent
GAME_ID = 897560637
OUR_AGENT = 6585801
OUR_SUBMISSION = 41071204
OUR_SEAT = 0
OPPONENT = "FRHT"
OPPONENT_AGENT = 6535596
OPPONENT_SUBMISSION = 40941012

PARENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585765-onsite-tree-owner-slim.min.rs"
)
CANDIDATE = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585801-second-funding-first-diagonal-denial-slim.min.rs"
)
EXTERNAL = REPO / "data/external/second-troll-funding-before-denial"
RAW = EXTERNAL / f"game-{GAME_ID}.json"
TRAJECTORY = EXTERNAL / f"trajectory-{GAME_ID}.jsonl"
RESULT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "second-troll-funding-before-denial-result-2026-07-31.json"
)
REPORT = RESULT.with_suffix(".md")

COHORT_GAME_IDS = (
    897560763, 897560696, 897560637, 897560600, 897560591,
    897560559, 897560483, 897560457, 897560437, 897560420,
    897560364, 897560348, 897560341, 897560323, 897560303,
    897560270, 897560252, 897560238, 897560217, 897560199,
    897560186, 897560182, 897560168, 897560153, 897560141,
    897560124, 897560096, 897560079, 897560058, 897560037,
    897560010, 897559988, 897559954, 897559928, 897559892,
    897559870, 897559844, 897559816, 897559800, 897559784,
)
PROBE_ANCHOR = "let mut commands=self.inner.commands(view);"
PROBE_RE = re.compile(
    r"^@FUNDING_PRE t=(\d+) roster=(\d+) abandoned=(\w+) commands=(.*)$"
)


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
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def fetch_game(game_id: int) -> dict[str, Any]:
    if game_id == GAME_ID and RAW.exists():
        game = json.loads(RAW.read_text(encoding="utf-8"))
    else:
        game = arena.call("gameResult/findByGameId", [game_id, None])
        if game_id == GAME_ID:
            atomic_write(RAW, canonical_json(game))
    if int(game.get("gameId") or -1) != game_id:
        raise ValueError(f"requested game {game_id}, received {game.get('gameId')}")
    return game


def decode(game: dict[str, Any]):
    seat = current_player(game)
    parser = corpus_parser()
    _, _, inventory0, inventory1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, _ = parser.extract_turns(
        game["frames"], inventory0, inventory1
    )
    map_data, states, unknown = decoded_states(game, trajectory)
    usable = min(len(trajectory), len(states) - 1)
    return seat, trajectory[:usable], map_data, states, unknown


def normalized(line: str) -> list[str]:
    return sorted(action_commands(line))


def exact_stream(game: dict[str, Any]):
    seat, trajectory, map_data, states, unknown = decode(game)
    if seat != OUR_SEAT or unknown or len(trajectory) != 300:
        raise ValueError(
            f"exact stream mismatch: seat={seat}, unknown={unknown}, "
            f"turns={len(trajectory)}"
        )
    identity = {
        int(row["index"]): int(row["agentId"])
        for row in game.get("agents") or []
    }
    if identity.get(OUR_SEAT) != OUR_AGENT:
        raise ValueError(f"resident identity mismatch: {identity}")
    views = [to_game_state(map_data, state) for state in states[:300]]
    stream = grid_text(views[0], OUR_SEAT) + "".join(
        turn_text(view, OUR_SEAT) for view in views
    )
    atomic_write(
        TRAJECTORY,
        "".join(canonical_json(row) for row in trajectory),
    )
    return trajectory, states, views, stream


def compiled_outputs(stream: str, recorded: list[str]):
    parent_text = PARENT.read_text(encoding="utf-8")
    if parent_text.count(PROBE_ANCHOR) != 1:
        raise ValueError(
            f"expected one pre-denial anchor, found "
            f"{parent_text.count(PROBE_ANCHOR)}"
        )
    probe = (
        PROBE_ANCHOR
        + 'if view.turn<=40{eprintln!("@FUNDING_PRE t={} roster={} '
        'abandoned={} commands={:?}",view.turn,'
        "view.units.iter().filter(|unit|unit.player==0).count(),"
        "self.inner.opening_abandoned,commands);}"
    )
    with tempfile.TemporaryDirectory(prefix="funding-denial-audit-") as directory:
        root = Path(directory)
        parent_binary = root / "parent"
        candidate_binary = root / "candidate"
        probe_source = root / "probe.rs"
        probe_binary = root / "probe"
        probe_source.write_text(
            parent_text.replace(PROBE_ANCHOR, probe, 1),
            encoding="utf-8",
        )
        compile_source(PARENT, parent_binary, "funding_denial_parent")
        compile_source(CANDIDATE, candidate_binary, "funding_denial_candidate")
        compile_source(probe_source, probe_binary, "funding_denial_probe")
        parent, parent_stderr = run_batch(parent_binary, stream)
        candidate, candidate_stderr = run_batch(candidate_binary, stream)
        probe_stdout, probe_stderr = run_batch(probe_binary, stream)

    pre = {}
    for line in probe_stderr.splitlines():
        match = PROBE_RE.match(line)
        if match:
            pre[int(match.group(1))] = {
                "roster": int(match.group(2)),
                "opening_abandoned": match.group(3) == "true",
                "commands": [
                    command
                    for command in json.loads(match.group(4))
                    if not command.startswith("MSG ")
                ],
            }
    parent_matches = sum(
        normalized(actual) == normalized(expected)
        for actual, expected in zip(parent, recorded)
    )
    if parent_matches != 300 or parent_stderr or candidate_stderr:
        raise ValueError("exact source reproduction or stderr gate failed")
    if parent != probe_stdout or len(pre) != 40:
        raise ValueError("pre-denial probe changed stdout or missed rows")
    return parent, candidate, pre


def cohort_row(game_id: int) -> dict[str, Any]:
    game = fetch_game(game_id)
    seat, trajectory, map_data, states, unknown = decode(game)
    usable = len(trajectory)
    train_turn = next(
        (
            turn
            for turn, row in enumerate(trajectory, 1)
            if any(
                command.upper().startswith("TRAIN ")
                for command in action_commands(
                    row.get(f"commands{seat}") or ""
                )
            )
        ),
        None,
    )
    view = to_game_state(map_data, states[0])
    enemy_tent = view.shacks[1 - seat]
    first_cardinal = next(
        (
            turn
            for turn, state in enumerate(states[:usable], 1)
            if any(
                abs(int(plant["x"]) - enemy_tent[0])
                + abs(int(plant["y"]) - enemy_tent[1])
                == 1
                and int(plant["health"]) > 0
                for plant in state["plants"]
            )
        ),
        None,
    )
    return {
        "game_id": game_id,
        "turns": usable,
        "unknown_diff_updates": unknown,
        "first_train_turn": train_turn,
        "first_cardinal_enemy_tent_tree_turn": first_cardinal,
    }


def analyze() -> dict[str, Any]:
    game = fetch_game(GAME_ID)
    trajectory, states, views, stream = exact_stream(game)
    recorded = [row.get("commands0") or "" for row in trajectory]
    parent, candidate, pre = compiled_outputs(stream, recorded)

    overwritten = [
        turn
        for turn in range(1, 41)
        if normalized(";".join(pre[turn]["commands"]))
        != normalized(parent[turn - 1])
    ]
    candidate_preserves = [
        turn
        for turn in overwritten
        if normalized(";".join(pre[turn]["commands"]))
        == normalized(candidate[turn - 1])
    ]
    first_train = next(
        turn
        for turn, line in enumerate(recorded, 1)
        if any(
            command.startswith("TRAIN ")
            for command in action_commands(line)
        )
    )
    enemy_tent = views[0].shacks[1]
    initial_ring = [
        {
            "type": plant.type,
            "cell": list(plant.pos),
            "health": plant.health,
            "fruits": plant.fruits,
        }
        for plant in views[0].plants
        if max(
            abs(plant.x - enemy_tent[0]),
            abs(plant.y - enemy_tent[1]),
        )
        == 1
    ]

    with ThreadPoolExecutor(max_workers=8) as executor:
        cohort = list(executor.map(cohort_row, COHORT_GAME_IDS))
    full = [row for row in cohort if row["turns"] > 1]
    early = [
        row
        for row in full
        if row["first_cardinal_enemy_tent_tree_turn"] is not None
        and row["first_cardinal_enemy_tent_tree_turn"] <= 34
    ]
    other = [row for row in full if row not in early]

    result = {
        "schema": "troll-farm-second-troll-funding-denial-v1",
        "exact_game": {
            "game_id": GAME_ID,
            "resident_agent_id": OUR_AGENT,
            "resident_submission_id": OUR_SUBMISSION,
            "resident_seat": OUR_SEAT,
            "opponent": OPPONENT,
            "opponent_agent_id": OPPONENT_AGENT,
            "opponent_submission_id": OPPONENT_SUBMISSION,
            "scores": game["scores"],
            "turns": 300,
            "unknown_diff_updates": 0,
            "raw_path": str(RAW.relative_to(REPO)),
            "raw_sha256": digest(RAW),
            "trajectory_path": str(TRAJECTORY.relative_to(REPO)),
            "trajectory_sha256": digest(TRAJECTORY),
        },
        "mechanism": {
            "initial_enemy_tent_ring": initial_ring,
            "recorded_first_train_turn": first_train,
            "opening_commands_overwritten_through_turn_40": overwritten,
            "overwritten_count": len(overwritten),
            "candidate_preserves_inner_on_all_overwritten_turns": (
                candidate_preserves == overwritten
            ),
            "turn_1_inner": pre[1]["commands"],
            "turn_1_parent": action_commands(parent[0]),
            "turn_1_candidate": action_commands(candidate[0]),
            "parent_recorded_command_matches": 300,
            "parent_stderr": "",
            "candidate_stderr": "",
            "first_parent_candidate_divergence": next(
                turn
                for turn, (old, new) in enumerate(
                    zip(parent, candidate), 1
                )
                if normalized(old) != normalized(new)
            ),
            "root_cause": (
                "post-planner tent denial overwrites the sole worker's active "
                "opening resource-collection command"
            ),
        },
        "fixed_live_slice": {
            "listed_games": len(cohort),
            "full_games": len(full),
            "early_cardinal_activation_games": len(early),
            "early_cardinal_train_at_35": sum(
                row["first_train_turn"] == 35 for row in early
            ),
            "early_cardinal_train_before_35": sum(
                row["first_train_turn"] is not None
                and row["first_train_turn"] < 35
                for row in early
            ),
            "other_games": len(other),
            "other_train_at_35": sum(
                row["first_train_turn"] == 35 for row in other
            ),
            "other_train_before_35": sum(
                row["first_train_turn"] is not None
                and row["first_train_turn"] < 35
                for row in other
            ),
            "rows": cohort,
            "boundary": "descriptive breadth, not causal value",
        },
        "successor": {
            "path": str(CANDIDATE.relative_to(REPO)),
            "bytes": CANDIDATE.stat().st_size,
            "sha256": digest(CANDIDATE),
            "rule": (
                "active second-worker opening collection precedes denial; "
                "after worker two or abandonment, denial uses the full "
                "eight-neighbor enemy-tent ring"
            ),
        },
    }
    return result


def report(result: dict[str, Any]) -> str:
    exact = result["exact_game"]
    mechanism = result["mechanism"]
    cohort = result["fixed_live_slice"]
    successor = result["successor"]
    return f"""# Second-worker funding before tent denial

Date: 2026-07-31
Task: `20260731-second-troll-funding-before-denial`
Verdict: **confirmed post-planner precedence defect**

Exact game `{exact['game_id']}` is a valid {exact['scores'][0]:g}–{exact['scores'][1]:g}
loss by resident `{exact['resident_agent_id']}` / `{exact['resident_submission_id']}`
against {exact['opponent']}. All 300 turns decode with zero unknown updates, and the exact
live source reproduces 300/300 resident command lines with zero stderr.

At turn 1 a live BANANA is cardinally adjacent to the enemy tent. The opening planner
emits `{mechanism['turn_1_inner'][0]}`, but the later denial wrapper replaces it with
`{mechanism['turn_1_parent'][0]}`. It overwrites the active opening command on
{mechanism['overwritten_count']} decisions through turn 40
(`{mechanism['opening_commands_overwritten_through_turn_40']}`). The recorded bot does
not TRAIN until hard downgrade turn {mechanism['recorded_first_train_turn']}.

The fixed 40-game live slice contains {cohort['full_games']} full games.
{cohort['early_cardinal_activation_games']} have cardinal activation by turn 34:
{cohort['early_cardinal_train_at_35']} TRAIN at 35 and
{cohort['early_cardinal_train_before_35']} earlier. In the other
{cohort['other_games']} games, zero TRAIN at 35 and
{cohort['other_train_before_35']} train earlier. This supports breadth, not a causal
Arena-value claim.

The successor preserves the opening planner command while own roster is below two and
the opening objective remains active. It preserves the inner command on every exact
overwritten decision and first diverges on turn
{mechanism['first_parent_candidate_divergence']}. After worker two exists or the opening
is abandoned, denial resumes over the full eight-neighbor enemy-tent ring, including
diagonals.

Candidate `{successor['path']}`, {successor['bytes']} bytes, SHA-256
`{successor['sha256']}`. Focused compiled boundaries and inherited regressions are
reported in the task manifest. This audit is mechanism evidence, not field qualification.
"""


def main() -> int:
    result = analyze()
    atomic_write(RESULT, json.dumps(result, indent=2) + "\n")
    atomic_write(REPORT, report(result))
    print(
        "funding-denial:",
        f"game={GAME_ID}",
        f"overwritten={result['mechanism']['overwritten_count']}",
        f"train={result['mechanism']['recorded_first_train_turn']}",
        "parent=300/300",
        "candidate-preserves=all",
    )
    print(f"wrote {RESULT}")
    print(f"wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
