from __future__ import annotations

from pathlib import Path
import tempfile

from cgauto.idle_harvest_study import (
    action_commands,
    compile_source,
    grid_text,
    run_batch,
    turn_text,
)
from cgauto.make_far_denial_no_return_candidate import (
    DISTANCE_THRESHOLD,
    make_candidate,
)
from cgauto.make_opponent_crop_candidate import PARENT
from sim.engine import recompute_scores
from sim.state import GameState, SimPlant, SimUnit


def fixture(route_distance: int) -> GameState:
    width, height = 11, 5
    shacks = [(1, 2), (9, 2)]
    walkable = {
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in shacks
    }
    target = (2 + route_distance, 2)
    game = GameState(
        width=width,
        height=height,
        walkable=walkable,
        shacks=shacks,
        inventories=[[0] * 6, [0] * 6],
        units=[
            SimUnit(0, 0, target[0], target[1], 1, 1, 1, 1, [0, 0, 0, 0, 0, 1]),
            SimUnit(2, 0, 2, 1, 2, 3, 0, 0, [0] * 6),
            SimUnit(1, 1, 9, 2, 1, 1, 1, 1, [0] * 6),
            SimUnit(3, 1, 8, 1, 1, 1, 1, 1, [0] * 6),
        ],
        plants=[
            SimPlant("LEMON", target[0], target[1], 4, 12, 3, 8),
            SimPlant("PLUM", 8, 4, 4, 12, 3, 8),
        ],
        scores=[0, 0],
        turn=20,
        next_id=4,
    )
    recompute_scores(game)
    return game


def unit_command(line: str, unit_id: int) -> str:
    for command in action_commands(line):
        fields = command.split()
        if len(fields) >= 2 and fields[1] == str(unit_id):
            return command
    raise AssertionError(f"no command for unit {unit_id}: {line}")


def test_threshold_three_is_inclusive_and_four_suppresses_return():
    assert DISTANCE_THRESHOLD == 3
    candidate = make_candidate(PARENT.read_text())
    with tempfile.TemporaryDirectory(prefix="far-denial-d3-test-") as directory:
        source = Path(directory) / "candidate.rs"
        binary = Path(directory) / "candidate"
        source.write_text(candidate)
        compile_source(source, binary, "far_denial_d3_test")

        near = fixture(3)
        near_lines, near_stderr = run_batch(
            binary, grid_text(near, 0) + turn_text(near, 0)
        )
        assert near_stderr == ""
        assert len(near_lines) == 1
        assert unit_command(near_lines[0], 0).startswith("MOVE 0 ")

        far = fixture(4)
        far_lines, far_stderr = run_batch(
            binary, grid_text(far, 0) + turn_text(far, 0)
        )
        assert far_stderr == ""
        assert len(far_lines) == 1
        assert unit_command(far_lines[0], 0) == "CHOP 0"


def test_candidate_rebuild_is_deterministic_and_slim():
    first = make_candidate(PARENT.read_text())
    second = make_candidate(PARENT.read_text())
    assert first == second
    assert len(first.encode()) < 100_000
    assert "route_distance>3" in first
    assert "unit.free_capacity()<=0&&!far_initial_denial" in first
