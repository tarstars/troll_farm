import numpy as np

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d155a_first_action_memory_value_models as d155
from tests.test_train_d153a_conditional_value_policy import tiny_dataset


def memory_dataset() -> dict:
    dataset = tiny_dataset()
    first = np.zeros((4, 379), dtype=np.float32)
    first[np.arange(4), np.arange(4)] = 1.0
    dataset.update(
        {
            "first_action_features": first,
            "first_state_features": np.zeros((4, 64), dtype=np.float32),
            "first_slots": np.ones(4, dtype=np.int64),
        }
    )
    return dataset


def test_frozen_history_architecture_shapes_and_parameters():
    dataset = memory_dataset()
    expected = {
        "snapshot_compact": 1873,
        "history_concat_compact": 2689,
        "history_bilinear_compact": 2688,
        "history_concat_full": 13185,
        "history_bilinear_full": 13184,
    }
    for architecture in d155.ARCHITECTURES:
        prepared = d155.prepared_features(dataset, architecture)
        assert all(value.shape[0] == 4 for value in prepared.values())
        assert architecture.parameters == expected[architecture.name]
        assert d115.parameter_count(d155.make_model(architecture)) == expected[
            architecture.name
        ]


def test_short_bilinear_history_fit_preserves_zero_control():
    dataset = memory_dataset()
    architecture = d155.BY_NAME["history_bilinear_compact"]
    model, summary = d155.train_model(
        dataset, architecture, 15301, epochs=2, threads=1
    )
    scores = d155.predict_margin_values(model, dataset, architecture)
    assert np.array_equal(scores[:, 0], np.zeros(4, dtype=np.float32))
    assert np.isfinite(scores).all()
    assert summary["parameters"] == 2688
