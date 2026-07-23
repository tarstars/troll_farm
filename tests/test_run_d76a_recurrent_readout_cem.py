"""Tests for D76's frozen recurrent-readout CEM helpers."""

from __future__ import annotations

import numpy as np

from cgauto.run_d76a_recurrent_readout_cem import (
    PARAMETERS,
    READOUT_PARAMETERS,
    fixed_reservoir,
    full_parameters,
    population_readouts,
    update_distribution,
)


def test_reservoir_and_full_parameter_geometry_are_deterministic() -> None:
    first = fixed_reservoir()
    second = fixed_reservoir()
    assert np.array_equal(first, second)
    assert full_parameters(first, np.zeros(READOUT_PARAMETERS)).shape == (PARAMETERS,)


def test_population_is_mean_plus_antithetic_pairs() -> None:
    mean = np.linspace(-0.1, 0.1, READOUT_PARAMETERS)
    std = np.full(READOUT_PARAMETERS, 0.2)
    rows = population_readouts(mean, std, np.random.default_rng(1), 1)
    assert len(rows) == 33
    assert np.allclose(rows[0][1], mean, atol=1.0e-7)
    for pair in range(16):
        plus = rows[1 + 2 * pair][1]
        minus = rows[2 + 2 * pair][1]
        assert np.allclose((plus + minus) / 2.0, mean, atol=1.0e-7)


def test_distribution_update_respects_std_floor() -> None:
    mean = np.zeros(READOUT_PARAMETERS)
    std = np.full(READOUT_PARAMETERS, 0.1)
    readouts = {f"p{index}": np.zeros(READOUT_PARAMETERS) for index in range(8)}
    new_mean, new_std = update_distribution(mean, std, readouts, list(readouts))
    assert np.array_equal(new_mean, mean)
    assert np.all(new_std[:48] >= 0.03)
    assert np.all(new_std[48:] >= 0.01)
