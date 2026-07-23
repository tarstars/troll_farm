"""Pure tests for zero-commitment terminal bundle pricing."""

from cgauto.idle_harvest_study import fixed_fixture
from cgauto.terminal_bundle_study import best_fell_cycle_from_home, feasible_episode_count


def test_best_fell_cycle_from_home_prices_travel_chop_and_return() -> None:
    game = fixed_fixture()
    unit = game.units[0]

    cycle = best_fell_cycle_from_home(game, unit)

    assert cycle is not None
    assert cycle["tree"] == [3, 2]
    assert cycle["wood"] == 1
    assert cycle["eta"] > 1


def test_best_fell_cycle_requires_chop_capacity() -> None:
    game = fixed_fixture()
    game.units[0].chop = 0

    assert best_fell_cycle_from_home(game, game.units[0]) is None


def test_feasible_episode_count_collapses_consecutive_frames() -> None:
    def event(turn: int, *, tree: list[int] = [3, 2]) -> dict:
        return {
            "kind": "harvest_bank_fell",
            "feasible": True,
            "turn": turn,
            "unit": 7,
            "home_cycle": {"tree": tree},
        }

    rows = [
        {"opportunities": [event(10), event(11), event(14)]},
        {"opportunities": [event(20)]},
    ]

    assert feasible_episode_count(rows, "harvest_bank_fell") == 3
