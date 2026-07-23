import numpy as np

from cgauto.run_d111a_diverse_q6_linear_lineage import (
    FEATURES,
    FROZEN,
    diverse_survivors,
    founder_vector,
    mutate,
    normalized_vector,
    runner_population,
)


def test_founders_and_mutations_are_deterministic_and_finite():
    first = founder_vector(np.random.default_rng(11101), 0)
    second = founder_vector(np.random.default_rng(11101), 0)
    assert np.array_equal(first, second)
    assert first.shape == (FEATURES,)
    parent = normalized_vector(np.zeros(FEATURES))
    child_a = mutate(parent, np.random.default_rng(7))
    child_b = mutate(parent, np.random.default_rng(7))
    assert np.array_equal(child_a, child_b)
    assert np.array_equal(parent, np.zeros(FEATURES, dtype=np.float32))
    assert np.isfinite(child_a).all()


def test_runner_population_preserves_each_actual_vector_as_matched_pair():
    labels = ["a", "b"]
    vectors = {
        "a": normalized_vector(np.arange(FEATURES) / FEATURES),
        "b": normalized_vector(-np.arange(FEATURES) / FEATURES),
    }
    rows = runner_population(labels, vectors)
    assert len(rows) == 1 + 2 * FROZEN["population"]
    assert rows[1]["parameters"] == rows[2]["parameters"] == vectors["a"].tolist()
    assert rows[3]["parameters"] == rows[4]["parameters"] == vectors["b"].tolist()


def test_diversity_cap_retains_multiple_founders():
    labels = [f"p{i}" for i in range(12)]
    lineage = {label: {"founder": f"f{i // 3}"} for i, label in enumerate(labels)}
    objectives = {label: {"eligible": True} for label in labels}
    selected = diverse_survivors(labels, lineage, objectives)
    counts = {}
    for label in selected:
        founder = lineage[label]["founder"]
        counts[founder] = counts.get(founder, 0) + 1
    assert len(selected) == FROZEN["survivors"]
    assert max(counts.values()) <= FROZEN["founder_survivor_cap"]
