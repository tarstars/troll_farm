import numpy as np

from cgauto.make_d107a_q6_proposal_controller_population import (
    FEATURES,
    RANDOM_CONTROLLERS,
    SEED,
    THRESHOLD_LEVELS,
    THRESHOLD_STEP,
    WEIGHT_SD,
    population,
    render,
    validate,
)


def test_population_reconstructs_seed_thresholds_and_matched_budgets():
    rows = population()
    validate(rows)
    assert len(rows) == 129
    assert rows[0]["policy"] == "zero_control"
    assert rows[0]["kind"] == "zero"
    assert rows[0]["budget"] == 4

    rng = np.random.Generator(np.random.PCG64(SEED))
    expected = np.round(
        rng.normal(0.0, WEIGHT_SD, size=(RANDOM_CONTROLLERS, FEATURES)), 8
    )
    for index in range(RANDOM_CONTROLLERS):
        one = rows[1 + 2 * index]
        four = rows[2 + 2 * index]
        threshold = -THRESHOLD_STEP * (1 + index % THRESHOLD_LEVELS)
        expected[index, 0] = threshold
        assert one["policy"] == f"one_{index:02d}"
        assert four["policy"] == f"four_{index:02d}"
        assert one["budget"] == 1
        assert four["budget"] == 4
        assert one["parameters"] == four["parameters"]
        np.testing.assert_array_equal(one["parameters"], expected[index])


def test_render_has_exact_schema_and_decimal_round_trip():
    content = render(population())
    lines = content.splitlines()
    assert len(lines) == 130
    assert len(lines[0].split("\t")) == FEATURES + 3
    assert all(len(line.split("\t")) == FEATURES + 3 for line in lines[1:])
    assert "\t-0.15000000\t" in lines[2]
