import numpy as np

from cgauto.make_d79a_spatial_job_population import (
    HIDDEN,
    JOB_CONTEXT_FEATURES,
    JOB_FEATURES,
    PARAMETERS,
    RANDOM_POLICIES,
    SEED,
    SHARED_FEATURES,
    population,
    random_parameters,
)


def test_population_has_exact_zero_anchor_and_frozen_shape() -> None:
    rows = population()
    assert PARAMETERS == 889
    assert len(rows) == RANDOM_POLICIES + 1 == 33
    assert rows[0][0] == "zero"
    assert np.array_equal(rows[0][1], np.zeros(PARAMETERS))
    assert [label for label, _ in rows[1:]] == [
        f"random_{index:02d}" for index in range(RANDOM_POLICIES)
    ]
    assert all(values.shape == (PARAMETERS,) for _, values in rows)
    assert all(np.isfinite(values).all() for _, values in rows)


def test_random_policy_draw_order_and_rounding_are_frozen() -> None:
    rng = np.random.Generator(np.random.PCG64(SEED))
    first = random_parameters(rng)
    assert first.shape == (PARAMETERS,)
    assert np.array_equal(first, population()[1][1])
    assert np.array_equal(first, np.round(first, 8))

    offsets = np.cumsum(
        [
            0,
            HIDDEN * SHARED_FEATURES,
            HIDDEN,
            HIDDEN * JOB_FEATURES,
            HIDDEN,
            HIDDEN,
            JOB_CONTEXT_FEATURES,
            1,
        ]
    )
    assert offsets.tolist() == [0, 368, 376, 856, 864, 872, 888, 889]


def test_population_is_reproducible_and_independent() -> None:
    left = population()
    right = population()
    for (left_label, left_values), (right_label, right_values) in zip(left, right):
        assert left_label == right_label
        assert np.array_equal(left_values, right_values)
    assert len({values.tobytes() for _, values in left}) == len(left)
