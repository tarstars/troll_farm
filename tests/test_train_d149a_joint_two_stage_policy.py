import numpy as np

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d149a_joint_two_stage_policy as d149


def tiny_dataset():
    rng = np.random.default_rng(149)
    actions = rng.normal(size=(4, 2, 379)).astype(np.float32)
    valid = np.asarray([[1, 0], [1, 1], [1, 1], [1, 0]], dtype=np.bool_)
    actions[~valid] = 0.0
    return {
        "action_features": actions,
        "valid": valid,
        "candidate_slots": np.asarray([[1, 0], [1, 2], [1, 2], [1, 0]]),
        "state_features": rng.normal(size=(4, 64)).astype(np.float32),
        "rank_targets": np.asarray([-1, 1, 0, -1], dtype=np.int64),
        "gate_targets": np.asarray([0, 1, 1, 0], dtype=np.bool_),
        "folds": np.asarray([0, 0, 1, 1], dtype=np.int64),
        "tasks": [(1, 0, "resident"), (1, 0, "resident"), (2, 0, "resident"), (2, 0, "resident")],
        "stages": ["wait_before_first", "first", "second", "wait_before_first"],
    }


def test_winner_context_is_finite_with_single_proposal_groups():
    ranker = d115.CompactActClassifier()
    context, selected, logits = d149.winner_context(ranker, tiny_dataset())
    assert context.shape == (4, 84)
    assert selected.shape == (4,)
    assert logits.shape == (4, 2)
    assert np.isfinite(context.detach().numpy()).all()


def test_task_weights_balance_classes_and_tasks():
    data = tiny_dataset()
    weights = d149.class_balanced_task_weights(data["tasks"], data["gate_targets"])
    assert np.isclose(weights[data["gate_targets"]].sum(), 0.5)
    assert np.isclose(weights[~data["gate_targets"]].sum(), 0.5)


def test_short_training_keeps_slim_parameter_budget():
    model, summary = d149.train_model(
        tiny_dataset(), 14901, 14951, rank_epochs=2, gate_epochs=2, threads=1
    )
    assert d115.parameter_count(model) == 6786
    assert summary["ranker"]["groups"] == 2
    assert summary["gate"]["groups"] == 4
