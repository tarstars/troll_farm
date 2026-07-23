import numpy as np

from cgauto.fit_d114a_supervised_one_use_q6_linear_scorer import (
    FEATURES,
    admission,
    population,
    ridge,
    rounded,
)


def test_root_balanced_ridge_is_finite_and_deployable():
    x = np.zeros((3, FEATURES), dtype=np.float64)
    x[:, 0] = 1.0
    x[:, 1] = [1.0, -1.0, 0.5]
    y = np.asarray([10.0, -10.0, 5.0])
    weights = ridge(x, y, [("a",), ("a",), ("b",)], clip=50.0, alpha=10.0)
    deployed = rounded(weights, offset=2.0)
    assert weights.shape == deployed.shape == (FEATURES,)
    assert np.isfinite(deployed).all()
    rows = population(deployed)
    assert len(rows) == 129
    assert rows[1]["parameters"] == rows[2]["parameters"]
    assert any(rows[1]["parameters"])
    assert not any(rows[3]["parameters"])


def test_validation_admission_accepts_robust_sparse_controller():
    metrics = {
        "mean_margin_delta": 3.0,
        "strict_improvement_rate": 0.4,
        "fold_mean_margin_delta": {"0": 2.0, "1": 4.0},
        "worst_family": -2.0,
        "positive_families": 6,
        "mean_own_score_delta": 1.0,
        "mean_opponent_score_delta": -2.0,
        "intervention_rate": 0.5,
        "crop_rate": 1.0,
        "worker_three_rate": 0.9,
        "control_worker_three_rate": 0.92,
    }
    assert all(admission(metrics).values())
