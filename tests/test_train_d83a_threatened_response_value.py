import numpy as np

from cgauto.train_d83a_threatened_response_value import (
    fit_ridge,
    frozen_gates,
    predict,
    rankdata,
)


def test_ridge_recovers_simple_linear_signal() -> None:
    x = np.arange(40, dtype=np.float64).reshape(20, 2)
    y = 3.0 + 2.0 * x[:, 0] - x[:, 1]
    model = fit_ridge(x, y, penalty=1.0e-6)
    assert np.max(np.abs(predict(model, x) - y)) < 1.0e-5


def test_rankdata_uses_average_tie_ranks() -> None:
    actual = rankdata(np.asarray([3.0, 1.0, 1.0, 2.0]))
    assert np.array_equal(actual, np.asarray([3.0, 0.5, 0.5, 2.0]))


def test_frozen_gate_conjunction() -> None:
    metrics = {
        "mean_margin_gain": 2.0,
        "rooted_strict_improvement_rate": 0.30,
        "rooted_regression_rate": 0.30,
        "mean_own_score_delta": 0.0,
        "mean_opponent_score_delta": 1.0,
        "opponent_family_mean_margin_gains": {
            f"o{index}": 0.0 for index in range(8)
        },
        "intervention_rate_on_rooted_tasks": 0.5,
        "selected_arm_counts": {"fell": 8, "harvest": 8, "renew": 0},
        "fold_mean_margin_gains": {str(index): 0.0 for index in range(8)},
    }
    assert all(frozen_gates(metrics).values())
