import numpy as np

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d154a_conditional_value_representations as d154
from tests.test_train_d153a_conditional_value_policy import tiny_dataset


def test_frozen_representation_dimensions_and_parameter_budgets():
    dataset = tiny_dataset()
    expected = {
        "full443": (443, 7121),
        "no_expert_ids379": (379, 6097),
        "semantic_context115": (115, 1873),
        "semantic109": (109, 1777),
        "semantic_supporters173": (173, 2801),
        "action_semantic_context51": (51, 849),
    }
    for representation in d154.REPRESENTATIONS:
        features = d154.represented_features(dataset, representation)
        width, parameters = expected[representation.name]
        assert features.shape == (4, 3, width)
        assert representation.inputs == width
        assert representation.parameters == parameters


def test_short_semantic_context_fit_preserves_exact_control_anchor():
    dataset = tiny_dataset()
    representation = d154.BY_NAME["semantic_context115"]
    model, summary = d154.train_model(
        dataset, representation, 15301, epochs=2, threads=1
    )
    assert d115.parameter_count(model) == 1873
    scores = d154.predict_margin_values(model, dataset, representation)
    assert np.array_equal(scores[:, 0], np.zeros(4, dtype=np.float32))
    assert np.isfinite(scores).all()
    assert summary["representation"] == "semantic_context115"
