from cgauto.sparse_selector_validation import full_registry_summary, subset_summary


def test_sparse_summary_restores_structural_zeros() -> None:
    means = {4: 10.0, 8: -2.0}
    by_opponent = {4: {"a": 8.0, "b": 12.0}, 8: {"a": -4.0, "b": 0.0}}

    result = full_registry_summary(list(range(10)), means, by_opponent, ("a", "b"))

    assert result["seed_summary"]["mean"] == 0.8
    assert result["activation_count"] == 2
    assert result["activation_rate"] == 0.2
    assert result["opponent_means"] == {"a": 0.4, "b": 1.2}


def test_active_subset_uses_seed_as_the_independent_unit() -> None:
    means = {4: 10.0, 8: -2.0}
    by_opponent = {4: {"a": 8.0, "b": 12.0}, 8: {"a": -4.0, "b": 0.0}}

    result = subset_summary([4, 8], means, by_opponent, ("a", "b"), {4: 2, 8: 1})

    assert result["seed_summary"]["mean"] == 4.0
    assert result["opponent_means"] == {"a": 2.0, "b": 6.0}
    assert result["active_side_count_distribution"] == {1: 1, 2: 1}
