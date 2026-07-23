"""Pure tests for matched historical terminal-fixture selection."""

from cgauto.historical_terminal_fixtures import (
    match_close_controls,
    preseed_opportunities,
)
from sim.state import SimUnit, from_ascii


def record(game_id: int, turns: int, trees: int, margin: int, seat: int = 0) -> dict:
    return {
        "game_id": game_id,
        "n_turns": turns,
        "initial_trees": trees,
        "margin": margin,
        "seat": seat,
        "opponent": "opponent",
    }


def test_match_close_controls_uses_unique_nearest_wins() -> None:
    losses = [record(1, 100, 10, -2), record(2, 200, 20, -8)]
    wins = [record(3, 102, 10, 3), record(4, 198, 20, 9), record(5, 300, 24, 1)]

    pairs = match_close_controls(losses, wins)

    assert [(loss["game_id"], win["game_id"]) for loss, win in pairs] == [
        (1, 3),
        (2, 4),
    ]


def test_preseed_opportunity_requires_empty_worker_at_fruited_home_door() -> None:
    game = from_ascii(["0....1"], talents=(1, 1, 1, 1))
    game.units[0].x = 1
    game.units.append(SimUnit(2, 0, 2, 0, 1, 1, 1, 1, [0] * 6))
    game.inventories[0][0] = 1
    game.turn = 100

    opportunities = preseed_opportunities(game, 0, ["MOVE 0 3 0", "WAIT"])

    assert len(opportunities) == 1
    assert opportunities[0]["unit"] == 0
    assert opportunities[0]["would_change_selection"]
