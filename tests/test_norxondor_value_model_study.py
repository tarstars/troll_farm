from __future__ import annotations

import numpy as np

from cgauto.norxondor_value_model_study import (
    candidate_rank,
    configuration_grid,
    fit_extra_tree,
    opponent_family_folds,
    predict_tree,
    seed_folds,
    trajectory_field_names,
)


def test_seed_folds_hold_contiguous_seed_blocks() -> None:
    seeds = np.asarray([seed for seed in range(10) for _ in range(2)])
    folds = seed_folds(seeds, 5)
    assert len(folds) == 5
    assert all(np.count_nonzero(fold) == 4 for fold in folds)
    assert np.all(sum(fold.astype(int) for fold in folds) == 1)
    assert set(seeds[folds[0]]) == {0, 1}


def test_opponent_fold_groups_duplicate_gold_models() -> None:
    opponents = np.asarray(
        ["compact_gold", "gold_elite", "gold_adaptive", "silver_boss"],
        dtype=object,
    )
    folds = opponent_family_folds(opponents)
    assert np.array_equal(folds[0], [True, True, False, False])
    assert np.all(sum(fold.astype(int) for fold in folds) == 1)


def test_small_extra_tree_learns_separable_values() -> None:
    matrix = np.asarray([[0.0], [1.0], [9.0], [10.0]])
    labels = np.asarray([False, False, True, True])
    indexes = np.arange(4)
    config = {
        "max_depth": 2,
        "min_leaf": 1,
        "negative_weight": 1.0,
        "max_features": 1,
        "thresholds_per_feature": 3,
    }
    tree = fit_extra_tree(matrix, labels, indexes, np.random.default_rng(1), config)
    output = np.zeros(4)
    predict_tree(tree, matrix, indexes, output)
    assert max(output[:2]) < min(output[2:])


def test_candidate_rank_accepts_threshold_report() -> None:
    policy = {
        "selection_rate": 0.1,
        "margin_delta_vs_resident": {"mean": 3.0},
    }
    classification = {"precision": 0.95, "f0_5": 0.5}
    report = {
        "config": {"trees": 8, "max_depth": 3},
        "gate_passed": True,
        "seed_cv": {"policy": policy, "classification": classification},
        "opponent_family_cv": {
            "policy": policy,
            "classification": classification,
        },
    }
    assert candidate_rank(report)[0]


def test_expanded_grid_contains_ten_frozen_directions() -> None:
    grid = configuration_grid("expanded")
    assert len(grid) == 10
    assert {config["training_margin_floor"] for config in grid} == {0, 10, 20}


def test_trajectory_schema_excludes_seed_seat_and_outcomes() -> None:
    fields = [
        "seed",
        "seat",
        "s0_turn",
        "s1_turn",
        "s2_turn",
        "s10_turn",
        "score_delta",
    ]
    assert trajectory_field_names(fields) == [
        "s0_turn",
        "s1_turn",
        "s2_turn",
        "s10_turn",
    ]
