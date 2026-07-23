"""Pure aggregation tests for terminal/race telemetry."""

from cgauto.terminal_race_study import aggregate


def test_aggregate_counts_terminal_and_race_discriminators() -> None:
    race = {
        "turn": 100,
        "player": 0,
        "command": "MOVE 0 3 2",
        "tree": {"x": 3, "y": 2},
        "selected": {"unit": 0, "bank_eta": 5},
        "opponent_fastest": {"bank_eta": 4},
        "opponent_beats_selected_fell": False,
        "opponent_beats_selected_bank": True,
        "focus_gate_active": True,
    }
    row = {
        "seed": 7,
        "ended_by_stall": True,
        "terminal_turn": 120,
        "end_reason": "mercy_player_0",
        "margin_player_0": -4,
        "low_supply_races": [race],
        "last_tree_transitions": [
            {"transition": "last_tree_removed"},
            {"transition": "empty_board_replanted"},
        ],
        "final": {
            "margin_player_0": -4,
            "projected_margin_player_0": 2,
            "players": [
                {"carried_value": 8, "value_within_implied_grace": 4},
                {"carried_value": 2, "value_within_implied_grace": 0},
            ],
        },
    }

    result = aggregate([row])

    assert result["end_reasons"] == {"mercy_player_0": 1}
    assert result["games_where_cargo_changes_projected_outcome"] == 1
    assert result["last_tree_transitions"]["games_with_replant"] == 1
    assert result["completion_races"]["focus_gate_active_and_opponent_beats_bank"] == 1
    assert result["completion_races"]["unique_unit_tree_commitments"] == 1


def test_aggregate_accepts_empty_input() -> None:
    assert aggregate([])["games"] == 0
