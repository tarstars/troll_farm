import numpy as np

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d153a_conditional_value_policy as d153


def tiny_dataset() -> dict:
    groups = 4
    width = 3
    actions = np.zeros((groups, width, 379), dtype=np.float32)
    for group in range(groups):
        actions[group, 1, group] = 1.0
        actions[group, 2, group + 4] = 1.0
    return {
        "action_features": actions,
        "state_features": np.eye(groups, 64, dtype=np.float32),
        "valid": np.ones((groups, width), dtype=np.bool_),
        "candidate_slots": np.tile(np.arange(width), (groups, 1)),
        "target_values": np.asarray(
            [[0, 20, -10], [0, -5, 15], [0, 10, 5], [0, -20, -10]],
            dtype=np.float32,
        ),
        "folds": np.arange(groups, dtype=np.int64),
        "target_active": np.ones(groups, dtype=np.bool_),
        "tasks": [(group, 0, "resident") for group in range(groups)],
        "opponents": ["resident"] * groups,
    }


def test_relative_value_model_has_frozen_shape_and_exact_zero_control():
    dataset = tiny_dataset()
    model, summary = d153.train_model(dataset, 15301, epochs=2, threads=1)
    assert d115.parameter_count(model) == 7121
    predicted = d153.predict_margin_values(model, dataset)
    assert predicted.shape == (4, 3)
    assert np.array_equal(predicted[:, 0], np.zeros(4, dtype=np.float32))
    assert np.isfinite(predicted).all()
    assert summary["groups"] == 4
    assert summary["actions"] == 12


def test_grouped_loss_is_finite_with_padding():
    relative = __import__("torch").tensor([[0.0, 0.2, 9.0], [0.0, -0.1, 0.3]])
    targets = __import__("torch").tensor([[0.0, 0.4, 0.0], [0.0, -0.2, 0.2]])
    valid = __import__("torch").tensor([[True, True, False], [True, True, True]])
    losses = d153.grouped_losses(relative, targets, valid)
    assert all(bool(__import__("torch").isfinite(loss)) for loss in losses)
