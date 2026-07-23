from __future__ import annotations

import random

from cgauto.norxondor_shared_state_forest_study import (
    candidate_thresholds,
    fit_extra_tree,
    tree_predict,
)


def test_random_thresholds_are_bounded_and_deterministic() -> None:
    first = candidate_thresholds(list(range(20)), random.Random(7))
    second = candidate_thresholds(list(range(20)), random.Random(7))
    assert first == second
    assert len(first) == 8
    assert all(0 < value < 19 for value in first)


def test_extra_tree_learns_simple_deployable_split() -> None:
    keys = list(range(40))
    features = {item: {"signal": item, "noise": item % 3} for item in keys}
    labels = {item: item >= 25 for item in keys}
    tree = fit_extra_tree(
        keys,
        features,
        labels,
        random.Random(1),
        max_depth=3,
        min_leaf=3,
        negative_weight=1,
        max_features=2,
    )
    predictions = {item: tree_predict(tree, features[item]) for item in keys}
    assert predictions == labels
