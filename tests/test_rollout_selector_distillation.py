from cgauto.rollout_selector_distillation import (
    confusion,
    fit_tree,
    predict,
    turn_one_features,
)
from sim.mapgen import generate_bronze


def test_turn_one_features_are_seat_specific_for_iron_inventory() -> None:
    game = generate_bronze(0)
    first = turn_one_features(game, 0)
    second = turn_one_features(game, 1)

    assert first["own_iron"] == game.inventories[0][4]
    assert second["own_iron"] == game.inventories[1][4]
    assert first["enemy_iron"] == second["own_iron"]
    assert first["tree_count"] == second["tree_count"]


def test_weighted_tree_learns_a_clean_numeric_split() -> None:
    keys = [(seed, 0) for seed in range(12)]
    features = {key: {"value": float(key[0])} for key in keys}
    labels = {key: key[0] >= 8 for key in keys}

    tree = fit_tree(
        keys,
        features,
        labels,
        max_depth=2,
        min_leaf=2,
        negative_weight=2.0,
    )
    predictions = {key: predict(tree, features[key]) for key in keys}

    assert predictions == labels


def test_confusion_reports_precision_focused_metrics() -> None:
    truth = {1: True, 2: True, 3: False, 4: False}
    predictions = {1: True, 2: False, 3: True, 4: False}

    report = confusion(truth, predictions)

    assert report["true_positive"] == 1
    assert report["false_positive"] == 1
    assert report["false_negative"] == 1
    assert report["true_negative"] == 1
    assert report["precision"] == 0.5
    assert report["recall"] == 0.5
