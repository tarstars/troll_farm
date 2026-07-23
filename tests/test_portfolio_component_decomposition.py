from cgauto.portfolio_component_decomposition import (
    component_summary,
    decomposition_record,
    interaction_equivalence,
    seed_balanced,
)


def test_decomposition_record_computes_additive_interaction() -> None:
    row = decomposition_record(1, "race", 7, 2, 3)

    assert row["additive_prediction"] == 5
    assert row["interaction"] == 2


def test_seed_balanced_prevents_opponent_count_weighting() -> None:
    rows = [
        decomposition_record(1, "a", 2, 0, 0),
        decomposition_record(1, "b", 4, 0, 0),
        decomposition_record(2, "a", 9, 0, 0),
    ]

    assert seed_balanced(rows, "stack_delta") == [3, 9]
    assert component_summary(rows)["stack_delta"]["mean"] == 6


def test_interaction_equivalence_counts_exact_cells() -> None:
    rows = [
        decomposition_record(1, "a", 5, 2, 3),
        decomposition_record(2, "a", 6, 2, 3),
    ]

    result = interaction_equivalence(rows)

    assert result["exact_additive_cells"] == 1
    assert result["nonadditive_cells"] == 1
    assert result["mean_interaction"] == 0.5
