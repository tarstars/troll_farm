import numpy as np

from cgauto.train_d41h_relu_value_filter import (
    TARGETS,
    fits_bit_exact,
    fit_relu,
    initialization_seed,
    maximum_raw_parity_error,
    raw_parameters,
    raw_predict,
    scalar_parameters,
    standardized_predict,
    target_values,
)


def test_frozen_seed_formula_and_size_budget():
    assert initialization_seed(0, 0, 0, 0) == 431
    assert initialization_seed(2, 1, 1, 8) == 1649
    assert scalar_parameters(8) == 818
    assert scalar_parameters(16) == 1634


def test_frozen_target_definitions():
    margin = np.asarray([-80, -1, 0, 1, 80], dtype=np.float32)
    np.testing.assert_array_equal(
        target_values("clip50_mse", margin),
        np.asarray([-1, -0.02, 0, 0.02, 1], dtype=np.float32),
    )
    np.testing.assert_array_equal(
        target_values("positive_bce", margin), [0, 0, 0, 1, 1]
    )
    np.testing.assert_array_equal(
        target_values("nonnegative_bce", margin), [0, 0, 1, 1, 1]
    )
    assert TARGETS == ("clip50_mse", "positive_bce", "nonnegative_bce")


def test_relu_fit_is_repeat_exact_and_raw_export_matches():
    rng = np.random.default_rng(41)
    features = rng.normal(size=(64, 7)).astype(np.float32)
    margin = (
        20 * (features[:, 0] * features[:, 1] > 0)
        - 10 * (features[:, 2] > 0)
    ).astype(np.float32)
    arguments = {
        "target_name": "positive_bce",
        "width": 8,
        "weight_decay": 0.0001,
        "seed": 431,
    }
    first = fit_relu(features, margin, **arguments)
    second = fit_relu(features, margin, **arguments)
    assert fits_bit_exact(first, second)
    assert maximum_raw_parity_error(first, features) <= 1e-5
    np.testing.assert_allclose(
        standardized_predict(first, features),
        raw_predict(raw_parameters(first), features),
        atol=1e-5,
        rtol=0,
    )
