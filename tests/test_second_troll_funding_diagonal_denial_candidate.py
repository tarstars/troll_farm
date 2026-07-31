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
from cgauto.make_second_troll_funding_diagonal_denial_candidate import (
    PARENT,
    make_candidate,
)
from sim.engine import recompute_scores
from sim.state import GameState, SimPlant, SimUnit


CARDINAL = (8, 2)
DIAGONAL = (8, 1)
PLUM_TREE = (3, 1)
LEMON_TREE = (3, 3)


def fixture(*, workers: int, ring_cell: tuple[int, int], turn: int = 1) -> GameState:
    width, height = 11, 5
    shacks = [(1, 2), (9, 2)]
    walkable = {
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in shacks
    }
    units = [
        SimUnit(0, 0, 5, 1, 1, 1, 1, 1, [0] * 6),
        SimUnit(1, 1, 9, 2, 1, 1, 1, 1, [0] * 6),
    ]
    if workers == 2:
        units.append(SimUnit(2, 0, 5, 3, 1, 1, 1, 1, [0] * 6))
    game = GameState(
        width=width,
        height=height,
        walkable=walkable,
        shacks=shacks,
        inventories=[[0, 0, 10, 10, 0, 0], [0] * 6],
        units=units,
        plants=[
            SimPlant("BANANA", ring_cell[0], ring_cell[1], 3, 6, 3, 6),
            SimPlant("PLUM", PLUM_TREE[0], PLUM_TREE[1], 4, 12, 3, 8),
            SimPlant("LEMON", LEMON_TREE[0], LEMON_TREE[1], 4, 12, 3, 8),
        ],
        scores=[0, 0],
        turn=turn,
        next_id=3,
    )
    recompute_scores(game)
    return game


def unit_command(line: str, unit_id: int) -> str:
    unit_ids = [0, 2]
    slot = 0
    for command in action_commands(line):
        fields = command.split()
        if not fields or fields[0] in {"MSG", "TRAIN"}:
            continue
        positional_id = unit_ids[slot]
        slot += 1
        if fields[0] == "WAIT" and positional_id == unit_id:
            return command
        if len(fields) >= 2 and fields[1] == str(unit_id):
            return command
    raise AssertionError(f"no command for unit {unit_id}: {line}")


def target(command: str, positions: dict[int, tuple[int, int]]):
    fields = command.split()
    if fields[0] == "MOVE":
        return int(fields[2]), int(fields[3])
    if fields[0] == "CHOP":
        return positions[int(fields[1])]
    return None


def compiled_pair():
    candidate = make_candidate(PARENT.read_text(encoding="utf-8"))
    directory = tempfile.TemporaryDirectory(prefix="funding-diagonal-denial-test-")
    root = Path(directory.name)
    candidate_source = root / "candidate.rs"
    candidate_source.write_text(candidate, encoding="utf-8")
    parent_binary = root / "parent"
    candidate_binary = root / "candidate"
    compile_source(PARENT, parent_binary, "funding_diagonal_parent_test")
    compile_source(
        candidate_source,
        candidate_binary,
        "funding_diagonal_candidate_test",
    )
    return directory, parent_binary, candidate_binary, candidate


def test_one_worker_opening_collection_overrides_cardinal_denial():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        game = fixture(workers=1, ring_cell=CARDINAL)
        stream = grid_text(game, 0) + turn_text(game, 0)
        parent, parent_stderr = run_batch(parent_binary, stream)
        candidate, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        positions = {0: game.units[0].pos}
        parent_step = target(unit_command(parent[0], 0), positions)
        candidate_step = target(unit_command(candidate[0], 0), positions)
        assert parent_step != candidate_step
        assert candidate_step is not None and candidate_step[0] < positions[0][0]


def test_one_worker_opening_collection_also_overrides_diagonal_denial():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        game = fixture(workers=1, ring_cell=DIAGONAL)
        stream = grid_text(game, 0) + turn_text(game, 0)
        parent, parent_stderr = run_batch(parent_binary, stream)
        candidate, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        assert action_commands(parent[0]) == action_commands(candidate[0])
        positions = {0: game.units[0].pos}
        candidate_step = target(unit_command(candidate[0], 0), positions)
        assert candidate_step is not None and candidate_step[0] < positions[0][0]


def test_two_workers_activate_diagonal_denial():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        game = fixture(workers=2, ring_cell=DIAGONAL)
        stream = grid_text(game, 0) + turn_text(game, 0)
        parent, parent_stderr = run_batch(parent_binary, stream)
        candidate, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        positions = {unit.id: unit.pos for unit in game.units if unit.player == 0}
        candidate_steps = {
            unit_id: target(unit_command(candidate[0], unit_id), positions)
            for unit_id in (0, 2)
        }
        assert any(
            step is not None and step[0] > positions[unit_id][0]
            for unit_id, step in candidate_steps.items()
        )
        assert action_commands(parent[0]) != action_commands(candidate[0])


def test_abandoned_one_worker_opening_activates_diagonal_denial():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        initial = fixture(workers=1, ring_cell=DIAGONAL)
        abandoned = copy.deepcopy(initial)
        abandoned.turn = 35
        stream = (
            grid_text(initial, 0)
            + turn_text(initial, 0) * 34
            + turn_text(abandoned, 0)
        )
        candidate, stderr = run_batch(candidate_binary, stream)
        assert stderr == ""
        positions = {0: abandoned.units[0].pos}
        candidate_step = target(unit_command(candidate[34], 0), positions)
        assert candidate_step is not None and candidate_step[0] > positions[0][0]


def test_rebuild_is_deterministic_and_bounded():
    parent = PARENT.read_text(encoding="utf-8")
    first = make_candidate(parent)
    second = make_candidate(parent)
    assert first == second
    assert len(first.encode()) < 100_000
    assert "yamo-funding-first-diagonal-denial-rust" in first
