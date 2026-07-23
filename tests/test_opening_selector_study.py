from cgauto.opening_selector_study import (
    contiguous_blocks,
    evaluate_predictions,
    fit_stump,
    max_affordable_level,
    predict,
)


def test_max_affordable_level_matches_square_cost_boundaries() -> None:
    assert [max_affordable_level(value) for value in (1, 2, 4, 5, 9, 10)] == [
        1,
        1,
        1,
        2,
        2,
        3,
    ]


def test_contiguous_blocks_keep_neighboring_seeds_together() -> None:
    assert contiguous_blocks(list(range(12)), 3) == {
        **{seed: 0 for seed in range(4)},
        **{seed: 1 for seed in range(4, 8)},
        **{seed: 2 for seed in range(8, 12)},
    }


def test_cost_sensitive_stump_selects_only_the_positive_leaf() -> None:
    seeds = list(range(10))
    features = {seed: {"bank": seed} for seed in seeds}
    outcomes = {seed: (-5 if seed < 5 else 8) for seed in seeds}

    model = fit_stump(seeds, features, outcomes, ("bank",), 0.2, 1.5)

    assert model["feature"] == "bank"
    assert model["left_select"] is False
    assert model["right_select"] is True
    assert [predict(model, features[seed]) for seed in seeds] == [False] * 5 + [
        True
    ] * 5


def test_selector_evaluation_keeps_seed_as_independent_unit() -> None:
    seeds = [1, 2, 3]
    outcomes = {1: 6, 2: -3, 3: 9}
    by_opponent = {
        1: {"a": 4, "b": 8},
        2: {"a": -2, "b": -4},
        3: {"a": 7, "b": 11},
    }
    predictions = {1: True, 2: False, 3: True}

    result = evaluate_predictions(
        seeds, predictions, outcomes, by_opponent, ("a", "b")
    )

    assert result["summary"]["mean"] == 5
    assert result["activation_count"] == 2
    assert result["opponent_means"] == {"a": 11 / 3, "b": 19 / 3}
    assert result["selected_seeds"] == [1, 3]
