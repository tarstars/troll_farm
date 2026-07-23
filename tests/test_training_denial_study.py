"""Pure tests for training-denial telemetry helpers."""

from cgauto.training_denial_study import aggregate, annotate_commitment, training_command


def test_training_command_extracts_talents() -> None:
    assert training_command(["MOVE 0 1 1", "TRAIN 2 3 0 2"]) == (2, 3, 0, 2)
    assert training_command(["WAIT"]) is None


def test_annotate_commitment_prices_eventual_training_deficit() -> None:
    row = annotate_commitment(
        {
            "turn": 3,
            "tree": "LEMON",
            "focus": "LEMON",
            "opponent_inventory": [5, 1, 1, 0, 5, 0],
        },
        {"turn": 8, "talents": [2, 2, 0, 2]},
    )

    assert row["turns_before_train"] == 5
    assert row["eventual_deficits"]["LEMON"] == 4
    assert row["target_is_max_train_deficit"]
    assert row["focus_matches_raw_scarcer_kind"]
    assert row["raw_inventory_scarcer_is_max_train_deficit"]


def test_aggregate_separates_same_turn_from_actionable_denial() -> None:
    base = {
        "opponent_train": {"turn": 4, "talents": [2, 2, 0, 2]},
        "target_deficit": 4,
        "target_is_max_train_deficit": True,
        "target_is_max_plum_lemon_deficit": True,
        "focus_matches_raw_scarcer_kind": True,
        "raw_inventory_scarcer_deficit": 4,
        "raw_inventory_scarcer_is_max_train_deficit": True,
        "raw_inventory_scarcer_is_max_plum_lemon_deficit": True,
        "player": 0,
    }
    rows = [
        {
            "seed": 0,
            "training": [
                {"turn": 1, "talents": [2, 2, 0, 2]},
                {"turn": 4, "talents": [2, 2, 0, 2]},
            ],
            "focus_commitments_before_opponent_train": [
                {**base, "turns_before_train": 2},
                {**base, "turns_before_train": 0},
            ],
        }
    ]

    result = aggregate(rows)

    assert result["focus_commitments_before_opponent_train"] == 2
    assert result["actionable_commitments_at_least_one_turn_early"] == 1
    assert result["sides_with_actionable_commitment"] == 1
