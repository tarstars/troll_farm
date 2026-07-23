"""Tests for D77 full-recurrent lineage helpers."""

from __future__ import annotations

import numpy as np

from cgauto.run_d77a_full_recurrent_lineage_search import (
    BO_END,
    PARAMETERS,
    mutate,
    normalized_vector,
    random_network,
)


def test_founder_generation_is_deterministic_and_zero_readout_is_balanced_capable() -> None:
    first = random_network(np.random.default_rng(7701), zero_readout=True)
    second = random_network(np.random.default_rng(7701), zero_readout=True)
    assert np.array_equal(first, second)
    assert first.shape == (PARAMETERS,)
    assert np.count_nonzero(first[-52:]) == 0


def test_mutation_is_deterministic_and_does_not_modify_parent() -> None:
    parent = np.zeros(PARAMETERS, dtype=np.float32)
    original = parent.copy()
    first = mutate(parent, np.random.default_rng(3))
    second = mutate(parent, np.random.default_rng(3))
    assert np.array_equal(parent, original)
    assert np.array_equal(first, second)
    assert np.count_nonzero(first) > 0
    assert len(first) == BO_END


def test_normalized_vector_is_serialization_idempotent() -> None:
    values = np.linspace(-1.0, 1.0, PARAMETERS)
    first = normalized_vector(values)
    second = normalized_vector(first)
    assert np.array_equal(first, second)
