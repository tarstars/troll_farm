"""Tests for D72's frozen recurrent population generator."""

from __future__ import annotations

import numpy as np

from cgauto.make_d72a_recurrent_population import HIDDEN, POLICIES, population


def test_population_is_deterministic_finite_and_orthogonal() -> None:
    first = population()
    second = population()
    assert len(first) == POLICIES
    assert [row["policy"] for row in first] == [f"rnn_{index:02d}" for index in range(POLICIES)]
    for left, right in zip(first, second):
        assert np.array_equal(left["values"], right["values"])
        assert np.isfinite(left["values"]).all()
        wh = left["values"][HIDDEN * 72 : HIDDEN * 72 + HIDDEN * HIDDEN].reshape(HIDDEN, HIDDEN)
        assert np.allclose(wh.T @ wh, np.eye(HIDDEN) * 0.49, atol=1e-10)
