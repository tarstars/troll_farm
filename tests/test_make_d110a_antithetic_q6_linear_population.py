import numpy as np

from cgauto.make_d110a_antithetic_q6_linear_population import (
    CONTROLLERS,
    DIRECTIONS,
    FEATURES,
    THRESHOLD_LEVELS,
    THRESHOLD_STEP,
    population,
    render,
    validate,
)


def test_population_is_paired_antithetic_and_outcome_blind():
    rows = population()
    validate(rows)
    assert len(rows) == 1 + 2 * CONTROLLERS
    for index in range(CONTROLLERS):
        one = rows[1 + 2 * index]
        four = rows[2 + 2 * index]
        assert one["parameters"] == four["parameters"]
        assert one["parameters"][0] == -THRESHOLD_STEP * (1 + index % THRESHOLD_LEVELS)
    for index in range(DIRECTIONS):
        positive = np.asarray(rows[1 + 2 * index]["parameters"])
        negative = np.asarray(rows[1 + 2 * (index + DIRECTIONS)]["parameters"])
        np.testing.assert_array_equal(positive[1:], -negative[1:])


def test_render_matches_d107_runner_schema():
    lines = render(population()).splitlines()
    assert len(lines) == 1 + 1 + 2 * CONTROLLERS
    assert all(len(line.split("\t")) == FEATURES + 3 for line in lines)
