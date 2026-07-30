from copy import deepcopy

from cgauto.e2_banking_route_audit import (
    Action,
    SideAudit,
    actions_by_unit,
    home_doors,
    immediate_door_check,
    joint_assignment_check,
)
from sim.engine import recompute_scores, step
from sim.state import GameState, SimUnit


def fixture(units):
    shack0 = (2, 2)
    shack1 = (6, 2)
    walkable = {
        (x, y)
        for x in range(9)
        for y in range(5)
        if (x, y) not in {shack0, shack1}
    }
    game = GameState(
        width=9,
        height=5,
        walkable=walkable,
        shacks=[shack0, shack1],
        inventories=[[0] * 6, [0] * 6],
        units=units
        + [SimUnit(90, 1, 7, 2, 1, 1, 1, 1, [0] * 6)],
        plants=[],
        scores=[0, 0],
        turn=1,
        next_id=100,
    )
    recompute_scores(game)
    return game


def transition(audit, game, commands):
    before = deepcopy(game)
    step(game, commands, ["WAIT"])
    audit.observe_transition(before, game, commands)


def test_wait_actions_bind_to_sorted_unit_slots():
    units = [
        SimUnit(7, 0, 0, 0, 1, 1, 1, 1, [0] * 6),
        SimUnit(4, 0, 1, 0, 1, 1, 1, 1, [0] * 6),
    ]
    actions = actions_by_unit(["WAIT", "MOVE 7 2 2"], units)
    assert actions[4] == Action("WAIT", 4, "WAIT", None)
    assert actions[7].target == (2, 2)


def test_home_doors_are_only_walkable_neighbors():
    unit = SimUnit(4, 0, 0, 0, 1, 1, 1, 1, [0] * 6)
    game = fixture([unit])
    game.walkable.remove((2, 1))
    assert set(home_doors(game, 0)) == {(3, 2), (2, 3), (1, 2)}


def test_immediate_check_respects_other_selected_target():
    cargo = [1, 0, 0, 0, 0, 0]
    first = SimUnit(4, 0, 0, 2, 1, 2, 1, 1, cargo)
    second = SimUnit(7, 0, 4, 2, 1, 2, 1, 1, [0] * 6)
    game = fixture([first, second])
    actions = {
        4: Action("MOVE", 4, "MOVE 4 1 2", (1, 2)),
        7: Action("MOVE", 7, "MOVE 7 3 2", (3, 2)),
    }
    check = immediate_door_check(game, 0, first, (1, 2), actions)
    assert check["identifiable"]
    assert [3, 2] not in check["eligible"]
    assert check["eta_regret"] == 0


def test_joint_assignment_finds_swappable_two_carrier_regret():
    cargo = [1, 0, 0, 0, 0, 0]
    first = SimUnit(4, 0, 0, 2, 1, 2, 1, 1, list(cargo))
    second = SimUnit(7, 0, 4, 2, 1, 2, 1, 1, list(cargo))
    game = fixture([first, second])
    actions = {
        4: Action("MOVE", 4, "MOVE 4 3 2", (3, 2)),
        7: Action("MOVE", 7, "MOVE 7 1 2", (1, 2)),
    }
    check = joint_assignment_check(
        game, 0, actions, {4: "episode-a", 7: "episode-b"}
    )
    assert check is not None
    assert check["identifiable"]
    assert check["eta_regret"] > 0


def test_target_change_deposit_and_next_target_are_bound():
    cargo = [1, 0, 0, 0, 0, 0]
    unit = SimUnit(4, 0, 0, 1, 1, 2, 1, 1, list(cargo))
    game = fixture([unit])
    audit = SideAudit(12, 0, game.walkable, game.shacks[0])

    transition(audit, game, ["MOVE 4 2 1"])
    transition(audit, game, ["MOVE 4 1 2"])
    transition(audit, game, ["DROP 4"])
    transition(audit, game, ["MOVE 4 8 4"])
    audit.finalize()

    assert len(audit.episodes) == 1
    episode = audit.episodes[0]
    assert episode.status == "deposited_bound"
    assert episode.target_changes == 1
    assert episode.deposit_door == (1, 2)
    assert episode.next_target == (8, 4)
    assert episode.total_hindsight_eta_regret is not None


def test_deposit_without_next_target_remains_unidentifiable():
    cargo = [1, 0, 0, 0, 0, 0]
    unit = SimUnit(4, 0, 1, 2, 1, 2, 1, 1, list(cargo))
    game = fixture([unit])
    audit = SideAudit(13, 0, game.walkable, game.shacks[0])

    transition(audit, game, ["DROP 4"])
    audit.finalize()

    assert audit.episodes[0].status == "deposited_unbound"
    assert audit.episodes[0].next_target is None


def test_nonbank_action_interrupts_provisional_door_move():
    cargo = [0, 0, 0, 0, 0, 1]
    unit = SimUnit(4, 0, 0, 2, 1, 2, 1, 1, list(cargo))
    game = fixture([unit])
    audit = SideAudit(14, 0, game.walkable, game.shacks[0])

    transition(audit, game, ["MOVE 4 1 2"])
    transition(audit, game, ["WAIT"])
    audit.finalize()

    assert audit.episodes[0].status == "unidentified_interrupted"
    assert audit.ambiguous_carrying_door_moves == 1
