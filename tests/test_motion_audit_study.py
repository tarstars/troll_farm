"""Pure transition tests for emitted-motion telemetry."""

import copy

from cgauto.motion_audit_study import audit_transition, move_commands
from sim.mapgen import generate_bronze


def test_move_commands_ignores_non_moves() -> None:
    assert move_commands(["MOVE 0 2 3", "CHOP 1", "WAIT"]) == {0: (2, 3)}


def test_audit_transition_detects_no_progress_and_reversal() -> None:
    before = generate_bronze(0)
    unit = next(unit for unit in before.units if unit.player == 0)
    after = copy.deepcopy(before)
    target = next(cell for cell in before.walkable if cell != unit.pos)

    blocked, _ = audit_transition(before, after, 0, {unit.id: target}, {})
    assert blocked["no_progress"] == 1

    after_unit = next(item for item in after.units if item.id == unit.id)
    previous = target
    after_unit.x, after_unit.y = previous
    reversed_counts, _ = audit_transition(
        before, after, 0, {unit.id: previous}, {unit.id: previous}
    )
    assert reversed_counts["one_turn_reversal"] == 1
