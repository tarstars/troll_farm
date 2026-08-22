from __future__ import annotations

import copy
from pathlib import Path
import tempfile

from cgauto.idle_harvest_study import (
    action_commands,
    compile_source,
    grid_text,
    run_batch,
    turn_text,
)
from cgauto.make_onsite_tree_owner_candidate import PARENT, make_candidate
from sim.engine import recompute_scores
from sim.state import GameState, SimPlant, SimUnit


TREE = (7, 1)


def fixture() -> GameState:
    width, height = 12, 3
    shacks = [(1, 1), (10, 1)]
    walkable = {
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in shacks
    }
    game = GameState(
        width=width,
        height=height,
        walkable=walkable,
        shacks=shacks,
        inventories=[[0] * 6, [0] * 6],
        units=[
            SimUnit(0, 0, TREE[0], TREE[1], 1, 1, 0, 1, [0, 0, 0, 0, 0, 1]),
            SimUnit(1, 1, 9, 1, 1, 1, 0, 1, [0] * 6),
            SimUnit(2, 0, 6, 1, 2, 1, 0, 2, [0, 0, 0, 0, 0, 1]),
        ],
        plants=[
            SimPlant("LEMON", TREE[0], TREE[1], 4, 9, 3, 8),
            SimPlant("PLUM", 11, 2, 4, 12, 3, 8),
        ],
        scores=[0, 0],
        turn=1,
        next_id=3,
    )
    recompute_scores(game)
    return game


def unit_command(line: str, unit_id: int) -> str:
    slot = {0: 0, 2: 1}[unit_id]
    commands = [
        command
        for command in action_commands(line)
        if command.split()[0] not in {"MSG", "TRAIN"}
    ]
    return commands[slot]


def compiled_pair():
    candidate = make_candidate(PARENT.read_text(encoding="utf-8"))
    directory = tempfile.TemporaryDirectory(prefix="onsite-tree-owner-test-")
    root = Path(directory.name)
    candidate_source = root / "candidate.rs"
    candidate_source.write_text(candidate, encoding="utf-8")
    parent_binary = root / "parent"
    candidate_binary = root / "candidate"
    compile_source(PARENT, parent_binary, "onsite_tree_owner_parent_test")
    compile_source(
        candidate_source, candidate_binary, "onsite_tree_owner_candidate_test"
    )
    return directory, parent_binary, candidate_binary, candidate


def test_capable_onsite_worker_keeps_tree_candidate():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        game = fixture()
        stream = grid_text(game, 0) + turn_text(game, 0)
        parent, parent_stderr = run_batch(parent_binary, stream)
        candidate, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        assert unit_command(parent[0], 0) == "WAIT"
        assert unit_command(parent[0], 2).startswith("MOVE 2 ")
        assert unit_command(candidate[0], 0) == "CHOP 0"
        assert action_commands(candidate[0]) != action_commands(parent[0])


def test_incapable_onsite_unit_does_not_reserve_tree():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        game = fixture()
        game.units[0].chop = 0
        recompute_scores(game)
        stream = grid_text(game, 0) + turn_text(game, 0)
        parent, parent_stderr = run_batch(parent_binary, stream)
        candidate, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        assert action_commands(candidate[0]) == action_commands(parent[0])


def test_off_tree_state_is_exact_parent_and_rebuild_is_bounded():
    directory, parent_binary, candidate_binary, candidate = compiled_pair()
    with directory:
        game = fixture()
        game.units[0].x, game.units[0].y = 5, 1
        recompute_scores(game)
        stream = grid_text(game, 0) + turn_text(game, 0)
        parent, parent_stderr = run_batch(parent_binary, stream)
        rebuilt, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        assert action_commands(rebuilt[0]) == action_commands(parent[0])
        assert candidate == make_candidate(PARENT.read_text(encoding="utf-8"))
        assert len(candidate.encode()) < 100_000
        assert "yamo-onsite-tree-owner-rust" in candidate
