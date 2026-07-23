from collections import deque

from cgauto.analyze_d86a_two_worker_renewable_role import (
    FEATURES,
    consume_provenance,
    fit_tree,
    predict,
)


def synthetic_row(value: int, label: bool) -> dict:
    opening = {feature: 0 for feature in FEATURES}
    opening["own_private_fruit"] = value
    return {
        "game_id": value,
        "opening": opening,
        "renewable_mode": label,
    }


def test_provenance_consumption_is_acquisition_ordered() -> None:
    pool = deque(["O", "H", "H", "O"])
    assert consume_provenance(pool, 3) == (2, 1)
    assert list(pool) == ["O"]


def test_provenance_underflow_remains_other() -> None:
    pool = deque(["H"])
    assert consume_provenance(pool, 3) == (1, 2)
    assert not pool


def test_depth_limited_selector_is_deterministic_and_predictive() -> None:
    rows = [synthetic_row(value, value >= 6) for value in range(12)]
    first = fit_tree(rows, 2)
    second = fit_tree(rows, 2)
    assert first == second
    assert first["balanced_accuracy_in_sample"] == 1.0
    assert [predict(first["model"], row) for row in rows] == [
        row["renewable_mode"] for row in rows
    ]


def test_missing_selector_feature_is_nonrenewable() -> None:
    rows = [synthetic_row(value, value >= 6) for value in range(12)]
    model = fit_tree(rows, 1)["model"]
    row = synthetic_row(10, True)
    row["opening"]["own_private_fruit"] = None
    assert predict(model, row) is False
