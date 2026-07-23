"""Tests for D74 paired option-value analysis helpers."""

from __future__ import annotations

import numpy as np

from cgauto.analyze_d74a_paired_option_values import (
    fit_ridge,
    predict_ridge,
    selected_modes,
)


def test_ridge_recovers_simple_multioutput_signal() -> None:
    x = np.asarray([[0.0], [1.0], [2.0], [3.0]])
    y = np.concatenate((2.0 * x + 1.0, -x + 3.0), axis=1)
    coefficients, mean, scale = fit_ridge(x, y, alpha=0.0)
    prediction = predict_ridge(x, coefficients, mean, scale)
    assert np.allclose(prediction, y)


def test_selector_uses_positive_best_and_action_order_ties() -> None:
    prediction = np.asarray(
        [
            [-1.0, -2.0, -3.0],
            [2.0, 2.0, 1.0],
            [0.0, 0.0, 0.1],
        ]
    )
    assert selected_modes(prediction).tolist() == [0, 1, 3]
