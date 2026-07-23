"""Tests for behavior-neutral terminal and tree-race telemetry."""

from sim.state import SimPlant, SimUnit, from_ascii
from sim.terminal import (
    cashout_eta,
    focus_kind,
    selected_tree_races,
    terminal_snapshot,
)


def corridor_state():
    game = from_ascii(["0.....1"], talents=(1, 1, 1, 1))
    game.units[0].x = 1
    game.units[1].x = 5
    return game


def test_focus_kind_reproduces_smaller_home_distance_sum() -> None:
    game = corridor_state()
    game.plants = [
        SimPlant("PLUM", 2, 0, 4, 12, 0, 2),
        SimPlant("LEMON", 5, 0, 4, 12, 0, 2),
    ]

    assert focus_kind(game, 0) == "PLUM"


def test_cashout_eta_includes_drop_command() -> None:
    game = corridor_state()
    game.units[0].carry[5] = 1

    assert cashout_eta(game, game.units[0]) == 1
    game.units[0].x = 4
    assert cashout_eta(game, game.units[0]) == 4


def test_selected_tree_race_flags_faster_opponent_completion() -> None:
    game = corridor_state()
    game.plants = [SimPlant("PLUM", 3, 0, 2, 6, 0, 2)]
    game.units[1] = SimUnit(1, 1, 3, 0, 1, 3, 0, 3, [0] * 6)

    races = selected_tree_races(game, 0, ["MOVE 0 3 0"], "PLUM")

    assert len(races) == 1
    assert races[0]["focus_gate_active"]
    assert races[0]["opponent_beats_selected_fell"]
    assert races[0]["opponent_beats_selected_bank"]


def test_terminal_snapshot_prices_bankable_cargo_inside_grace() -> None:
    game = corridor_state()
    game.units[0].carry[5] = 1
    game.scores = [8, 4]

    snapshot = terminal_snapshot(game, 3)

    assert snapshot["players"][0]["carried_value"] == 4
    assert snapshot["players"][0]["value_within_implied_grace"] == 4
    assert snapshot["projected_margin_player_0"] == 8
