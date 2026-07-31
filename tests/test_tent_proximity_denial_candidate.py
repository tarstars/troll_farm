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
from cgauto.make_tent_proximity_denial_candidate import PARENT, make_candidate
from sim.engine import recompute_scores
from sim.state import GameState, SimPlant, SimUnit


ADJACENT = ((8, 2), (9, 1), (9, 3))
OUTSIDE = (6, 4)


def fixture(
    adjacent_count: int,
    *,
    planted_outside: bool = False,
    carried: bool = False,
) -> GameState:
    width, height = 11, 5
    shacks = [(1, 2), (9, 2)]
    walkable = {
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in shacks
    }
    plants = [
        SimPlant("BANANA", cell[0], cell[1], 2, 4, 0, 6)
        for cell in ADJACENT[:adjacent_count]
    ]
    if planted_outside:
        plants.append(SimPlant("APPLE", OUTSIDE[0], OUTSIDE[1], 2, 8, 0, 9))
    carry = [0, 0, 0, 0, 0, 1] if carried else [0] * 6
    game = GameState(
        width=width,
        height=height,
        walkable=walkable,
        shacks=shacks,
        inventories=[[0] * 6, [0] * 6],
        units=[
            SimUnit(0, 0, 8, 2, 2, 2, 1, 2, list(carry)),
            SimUnit(2, 0, 6, 4, 2, 2, 1, 2, list(carry)),
            SimUnit(1, 1, 9, 2, 1, 1, 1, 1, [0] * 6),
        ],
        plants=plants,
        scores=[0, 0],
        turn=2,
        next_id=3,
    )
    recompute_scores(game)
    return game


def empty_initial() -> GameState:
    game = fixture(0)
    game.turn = 1
    return game


def unit_command(line: str, unit_id: int) -> str:
    action_slot = 0
    unit_ids = (0, 2)
    for command in action_commands(line):
        fields = command.split()
        if not fields or fields[0] in {"MSG", "TRAIN"}:
            continue
        positional_id = unit_ids[action_slot] if action_slot < len(unit_ids) else None
        action_slot += 1
        if fields[0] == "WAIT" and positional_id == unit_id:
            return command
        if len(fields) >= 2 and fields[1] == str(unit_id):
            return command
    raise AssertionError(f"no command for unit {unit_id}: {line}")


def target(command: str, positions: dict[int, tuple[int, int]]) -> tuple[int, int] | None:
    fields = command.split()
    if fields[0] == "MOVE":
        return int(fields[2]), int(fields[3])
    if fields[0] == "CHOP":
        return positions[int(fields[1])]
    return None


def compiled_candidate():
    candidate = make_candidate(PARENT.read_text(encoding="utf-8"))
    directory = tempfile.TemporaryDirectory(prefix="tent-denial-test-")
    source = Path(directory.name) / "candidate.rs"
    binary = Path(directory.name) / "candidate"
    source.write_text(candidate, encoding="utf-8")
    compile_source(source, binary, "tent_denial_test")
    return directory, binary, candidate


def test_zero_and_one_two_split_boundaries():
    directory, binary, _candidate = compiled_candidate()
    with directory:
        zero = fixture(0, planted_outside=True)
        lines, stderr = run_batch(
            binary,
            grid_text(zero, 0) + turn_text(empty_initial(), 0) + turn_text(zero, 0),
        )
        assert stderr == ""
        assert len(lines) == 2
        positions = {0: (8, 2), 2: (6, 4)}
        assert all(
            target(unit_command(lines[1], unit_id), positions) not in ADJACENT
            for unit_id in (0, 2)
        )

        for count in (1, 2):
            game = fixture(count, planted_outside=True)
            lines, stderr = run_batch(
                binary,
                grid_text(game, 0)
                + turn_text(empty_initial(), 0)
                + turn_text(game, 0),
            )
            assert stderr == ""
            commands = {unit_id: unit_command(lines[1], unit_id) for unit_id in (0, 2)}
            positions = {0: (8, 2), 2: (6, 4)}
            targets = {unit_id: target(command, positions) for unit_id, command in commands.items()}
            assert sum(cell in ADJACENT[:count] for cell in targets.values()) >= 1
            assert len({cell for cell in targets.values() if cell is not None}) == 2


def test_split_banker_returns_while_nonbank_worker_keeps_chopping():
    directory, binary, _candidate = compiled_candidate()
    with directory:
        active = fixture(1, planted_outside=True)
        carried = fixture(1, planted_outside=True, carried=True)
        lines, stderr = run_batch(
            binary,
            grid_text(active, 0)
            + turn_text(empty_initial(), 0)
            + turn_text(active, 0)
            + turn_text(carried, 0),
        )
        assert stderr == ""
        assert len(lines) == 3
        assert unit_command(lines[1], 0) == "CHOP 0"
        assert unit_command(lines[1], 2) == "CHOP 2"
        assert unit_command(lines[2], 0).startswith("MOVE 0 ")
        assert unit_command(lines[2], 2) == "CHOP 2"


def test_more_than_two_uses_both_workers_without_return():
    directory, binary, candidate = compiled_candidate()
    with directory:
        active = fixture(3)
        carried = fixture(3, carried=True)
        lines, stderr = run_batch(
            binary,
            grid_text(active, 0)
            + turn_text(empty_initial(), 0)
            + turn_text(active, 0)
            + turn_text(carried, 0),
        )
        assert stderr == ""
        assert len(lines) == 3
        positions = {0: (8, 2), 2: (6, 4)}
        for line in lines[1:]:
            commands = [unit_command(line, unit_id) for unit_id in (0, 2)]
            assert commands[0] == "CHOP 0"
            assert commands[1] == "MOVE 2 7 3"
            assert all(not command.startswith("DROP ") for command in commands)
        assert len(candidate.encode()) < 100_000
        assert "yamo-tent-proximity-denial-split-rust" in candidate


def test_preexisting_cargo_banks_before_full_denial_role():
    directory, binary, _candidate = compiled_candidate()
    with directory:
        initial = empty_initial()
        initial.units[1].carry[5] = 1
        recompute_scores(initial)
        active = fixture(3)
        active.units[1].carry[5] = 1
        recompute_scores(active)
        lines, stderr = run_batch(
            binary,
            grid_text(active, 0) + turn_text(initial, 0) + turn_text(active, 0),
        )
        assert stderr == ""
        assert len(lines) == 2
        assert unit_command(lines[1], 0) == "CHOP 0"
        assert unit_command(lines[1], 2).startswith("MOVE 2 ")
        assert unit_command(lines[1], 2) != "MOVE 2 7 3"


def test_rebuild_is_deterministic():
    first = make_candidate(PARENT.read_text(encoding="utf-8"))
    second = make_candidate(PARENT.read_text(encoding="utf-8"))

    assert first == second
