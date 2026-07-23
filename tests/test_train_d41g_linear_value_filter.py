import numpy as np

from cgauto.train_d41g_linear_value_filter import (
    FEATURES,
    discovery_metrics,
    feature_vector,
    fit_ridge,
    target_values,
    threshold_for_share,
)


def test_feature_vector_has_exact_frozen_layout():
    zero = np.arange(44, dtype=np.float32)
    one = zero + 2
    vector = feature_vector(zero, one, 0.25, 384)
    assert vector.shape == (FEATURES,)
    np.testing.assert_array_equal(vector[:17], zero[:17])
    np.testing.assert_array_equal(vector[17:44], zero[17:44])
    np.testing.assert_array_equal(vector[44:71], one[17:44])
    np.testing.assert_array_equal(vector[71:98], np.full(27, 2, dtype=np.float32))
    np.testing.assert_allclose(vector[98:], [0.25, 0.5])


def test_ridge_raw_coefficients_match_standardized_predictions():
    rng = np.random.default_rng(7)
    features = rng.normal(size=(80, 5))
    target = features @ np.asarray([2, -1, 0.5, 0, 3]) + 4
    fitted = fit_ridge(features, target, 0.1)
    assert fitted["maximum_raw_parity_error"] < 1e-10
    assert np.mean((fitted["prediction"] - target) ** 2) < 1e-3


def test_threshold_share_and_targets_are_deterministic():
    scores = np.arange(10, dtype=np.float64)
    assert threshold_for_share(scores, 0.4) == 6
    margin = np.asarray([-120, -20, 0, 60, 140], dtype=np.float64)
    np.testing.assert_array_equal(target_values("clip100", margin), [-100, -20, 0, 60, 100])
    np.testing.assert_array_equal(target_values("clip50", margin), [-50, -20, 0, 50, 50])
    np.testing.assert_array_equal(target_values("positive", margin), [0, 0, 0, 1, 1])


def test_discovery_gate_tracks_below_boundary_coverage():
    size = 320
    data = {
        "residual_gap": np.linspace(0.21, 0.33, size),
        "margin_delta": np.full(size, 20.0),
        "phase": np.arange(size) % 2,
        "fold": np.arange(size) % 8,
        "opponent": np.arange(size) % 8,
    }
    scores = np.arange(size, dtype=np.float64)
    report = discovery_metrics(data, scores, threshold_for_share(scores, 0.8))
    assert report["below_0280"] >= 64
    assert report["pass"]
