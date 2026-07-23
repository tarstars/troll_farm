from cgauto.option_rollout_selector_study import (
    held_out_evaluation,
    select_from_rollouts,
)


def test_unanimous_rule_rejects_one_disagreeing_continuation() -> None:
    assert select_from_rollouts([3, 2, 1], "unanimous-positive", 0)
    assert not select_from_rollouts([3, -1, 2], "unanimous-positive", 0)
    assert select_from_rollouts([3, -1, 2], "positive-mean", 0)


def test_held_out_unanimity_preserves_cross_continuation_winner() -> None:
    seeds = [1, 2]
    opponents = ("a", "b", "c")
    matrix = {
        1: {"a": 6, "b": 6, "c": 6},
        2: {"a": 5, "b": -4, "c": -2},
    }

    result = held_out_evaluation(
        seeds, matrix, opponents, "unanimous-positive"
    )

    assert result["seed_clustered_summary"]["mean"] == 3
    assert result["seed_clustered_summary"]["losses"] == 0
    assert result["worst_held_opponent_mean"] == 3
    assert result["full_terminal_games_per_decision"] == 4
