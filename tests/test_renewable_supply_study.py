"""Tests for renewable-supply timeline aggregation."""

import pytest

from cgauto.renewable_supply_study import summarize_rows


def row(score: int, wood: int, harvest: int, plant: int, last_plant: int | None) -> dict:
    checkpoints = {
        str(turn): {"trees": trees, "ripe_trees": trees // 2}
        for turn, trees in zip((1, 50, 100, 150, 200, 250, 300), range(7, 0, -1))
    }
    return {
        "final": {"score": score, "wood": wood},
        "command_counts": {"CHOP": 10, "HARVEST": harvest, "PLANT": plant},
        "supply_counts_after_150": {"HARVEST": harvest, "PICK": plant, "PLANT": plant},
        "last_supply_turn": {"HARVEST": 200 if harvest else None, "PICK": last_plant, "PLANT": last_plant},
        "checkpoints": checkpoints,
        "first_empty": {
            "turn": 180,
            "fruit": 1,
            "fruit_by_kind": {"PLUM": 0, "LEMON": 0, "APPLE": 0, "BANANA": 1},
        },
    }


def test_summarize_rows_reports_supply_timing_and_tree_decay() -> None:
    result = summarize_rows([row(100, 20, 2, 1, 220), row(120, 25, 0, 3, 260)])

    assert result["side_games"] == 2
    assert result["mean_final_score"] == 110
    assert result["mean_final_wood"] == 22.5
    assert result["mean_command_counts"]["CHOP"] == 10
    assert result["mean_supply_after_150"] == {"HARVEST": 1, "PICK": 2, "PLANT": 2}
    assert result["sides_with_supply_after_150"] == {"HARVEST": 1, "PICK": 2, "PLANT": 2}
    assert result["median_last_supply_turn"]["PLANT"] == 240
    assert result["mean_tree_count"]["1"] == 7
    assert result["mean_tree_count"]["300"] == 1
    assert result["first_empty"]["sides"] == 2
    assert result["first_empty"]["median_turn"] == 180
    assert result["first_empty"]["mean_fruit_by_kind"]["BANANA"] == 1
    assert result["terminal"] == {"ended_by_stall": 0, "median_turn": 300.0}
    assert result["grace_window"] == {
        "side_games_with_plant_command": 0,
        "plant_commands": 0,
        "matches_with_successful_replant": 0,
        "successful_replants": 0,
    }


def test_summarize_rows_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="empty"):
        summarize_rows([])
