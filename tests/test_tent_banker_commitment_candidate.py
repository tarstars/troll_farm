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
from cgauto.make_tent_banker_commitment_candidate import PARENT, make_candidate
from sim.engine import recompute_scores
from sim.state import GameState, SimPlant, SimUnit


ADJACENT = (8, 2)
OTHER_TREE = (8, 4)


def initial_fixture() -> GameState:
    width, height = 11, 5
    shacks = [(1, 2), (9, 2)]
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
            SimUnit(0, 0, ADJACENT[0], ADJACENT[1], 1, 2, 0, 2, [0] * 6),
            SimUnit(1, 1, 9, 1, 1, 1, 1, 1, [0] * 6),
        ],
        plants=[
            SimPlant("BANANA", ADJACENT[0], ADJACENT[1], 1, 1, 0, 6),
            SimPlant("PLUM", OTHER_TREE[0], OTHER_TREE[1], 4, 12, 3, 8),
        ],
        scores=[0, 0],
        turn=1,
        next_id=2,
    )
    recompute_scores(game)
    return game


def carried_state(cell: tuple[int, int], *, at_bank: bool = False) -> GameState:
    game = initial_fixture()
    game.plants = [plant for plant in game.plants if (plant.x, plant.y) != ADJACENT]
    game.units[0].x, game.units[0].y = cell
    game.units[0].carry[5] = 1
    if at_bank:
        assert abs(cell[0] - game.shacks[0][0]) + abs(cell[1] - game.shacks[0][1]) == 1
    recompute_scores(game)
    return game


def released_state() -> GameState:
    game = carried_state((2, 2), at_bank=True)
    game.units[0].carry[5] = 0
    recompute_scores(game)
    return game


def unit_command(line: str, unit_id: int = 0) -> str:
    for command in action_commands(line):
        fields = command.split()
        if not fields or fields[0] in {"MSG", "TRAIN"}:
            continue
        if fields[0] == "WAIT" or len(fields) >= 2 and fields[1] == str(unit_id):
            return command
    raise AssertionError(f"no command for unit {unit_id}: {line}")


def compiled_pair():
    candidate = make_candidate(PARENT.read_text(encoding="utf-8"))
    directory = tempfile.TemporaryDirectory(prefix="tent-banker-commitment-test-")
    root = Path(directory.name)
    candidate_source = root / "candidate.rs"
    candidate_source.write_text(candidate, encoding="utf-8")
    parent_binary = root / "parent"
    candidate_binary = root / "candidate"
    compile_source(PARENT, parent_binary, "tent_banker_parent_test")
    compile_source(candidate_source, candidate_binary, "tent_banker_candidate_test")
    return directory, parent_binary, candidate_binary, candidate


def test_bank_commitment_survives_trigger_loss_until_drop():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        initial = initial_fixture()
        first_carried = carried_state(ADJACENT)
        next_carried = carried_state((7, 2))
        at_bank = carried_state((2, 2), at_bank=True)
        released = released_state()
        stream = (
            grid_text(initial, 0)
            + turn_text(initial, 0)
            + turn_text(first_carried, 0)
            + turn_text(next_carried, 0)
            + turn_text(at_bank, 0)
            + turn_text(released, 0)
        )
        parent_lines, parent_stderr = run_batch(parent_binary, stream)
        candidate_lines, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        assert unit_command(parent_lines[0]) == unit_command(candidate_lines[0]) == "CHOP 0"
        assert unit_command(candidate_lines[1]) == "MOVE 0 7 2"
        assert unit_command(candidate_lines[2]) == "MOVE 0 6 2"
        assert unit_command(candidate_lines[3]) == "DROP 0"
        assert unit_command(candidate_lines[4]) != "DROP 0"


def test_zero_trigger_without_prior_commitment_is_exact_parent():
    directory, parent_binary, candidate_binary, _candidate = compiled_pair()
    with directory:
        initial = initial_fixture()
        zero = copy.deepcopy(initial)
        zero.plants = [plant for plant in zero.plants if (plant.x, plant.y) != ADJACENT]
        recompute_scores(zero)
        stream = grid_text(initial, 0) + turn_text(zero, 0)
        parent_lines, parent_stderr = run_batch(parent_binary, stream)
        candidate_lines, candidate_stderr = run_batch(candidate_binary, stream)
        assert parent_stderr == candidate_stderr == ""
        assert action_commands(parent_lines[0]) == action_commands(candidate_lines[0])


def test_rebuild_is_deterministic_and_bounded():
    parent = PARENT.read_text(encoding="utf-8")
    first = make_candidate(parent)
    second = make_candidate(parent)
    assert first == second
    assert len(first.encode()) < 100_000
    assert "yamo-tent-banker-commitment-rust" in first
