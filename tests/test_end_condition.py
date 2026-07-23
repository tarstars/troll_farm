"""Parity tests for the referee grace/stuck/mercy end condition."""

from sim.engine import has_stalled, stall_reason
from sim.state import SimPlant, from_ascii


def base_state():
    return from_ascii(
        [
            "......",
            "0....1",
            "......",
            "......",
        ]
    )


def test_no_plants_without_grace_ends_immediately() -> None:
    ended, counter = has_stalled(base_state(), 0)

    assert ended
    assert counter == -1
    assert stall_reason(base_state(), counter) == "grace_expired"


def test_unit_on_tree_sets_walk_home_grace_and_it_counts_down() -> None:
    game = base_state()
    game.plants.append(SimPlant("BANANA", 3, 2, 1, 3, 0, 0))
    game.units[0].x = 3
    game.units[0].y = 2

    ended, counter = has_stalled(game, 0)
    assert not ended
    assert counter == 10

    game.plants.clear()
    game.inventories[0][0] = 1
    game.inventories[1][0] = 1
    for _ in range(9):
        ended, counter = has_stalled(game, counter)
        assert not ended
    ended, counter = has_stalled(game, counter)
    assert ended
    assert counter == 0


def test_mercy_ends_when_the_losing_player_is_stuck() -> None:
    game = base_state()
    game.inventories[0][3] = 2
    game.scores = [2, 0]

    ended, _ = has_stalled(game, 5)
    assert ended
    assert stall_reason(game, 4) == "mercy_player_1"

    game.scores[1] = 10
    ended, counter = has_stalled(game, 5)
    assert not ended
    assert counter == 4


def test_carried_iron_does_not_unstick_but_carried_wood_does() -> None:
    iron_only = base_state()
    iron_only.units[0].carry[4] = 2
    ended, _ = has_stalled(iron_only, 5)
    assert ended

    with_wood = base_state()
    with_wood.units[0].carry[5] = 1
    ended, _ = has_stalled(with_wood, 5)
    assert not ended
