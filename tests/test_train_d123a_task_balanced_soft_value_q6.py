import torch

from cgauto.train_d123a_task_balanced_soft_value_q6 import (
    relative_held_gates,
    soft_cross_entropy_per_root,
    task_balanced_root_weights,
)


def test_task_balanced_weights_equalize_total_task_mass():
    first = ((1, 0, "a"), 0)
    second = ((1, 0, "a"), 1)
    third = ((2, 0, "b"), 0)
    weights = task_balanced_root_weights([first, second, third])
    assert torch.isclose(weights[0] + weights[1], weights[2])
    assert torch.isclose(weights.mean(), torch.tensor(1.0))


def test_soft_cross_entropy_returns_one_finite_loss_per_root():
    logits = torch.tensor([[2.0, 0.0], [1.0, -10.0]])
    targets = torch.tensor([[0.75, 0.25], [1.0, 0.0]])
    valid = torch.tensor([[True, True], [True, False]])
    losses = soft_cross_entropy_per_root(logits, targets, valid)
    assert losses.shape == (2,)
    assert bool(torch.isfinite(losses).all())
    assert losses[1] == 0.0


def test_relative_crop_gate_accepts_control_equivalence():
    metrics = {
        "mean_margin_delta": 2.0,
        "strict_improvement_rate": 0.40,
        "worst_family": -3.0,
        "positive_families": 6,
        "mean_own_score_delta": 0.0,
        "mean_opponent_score_delta": 1.0,
        "intervention_rate": 0.85,
        "crop_rate": 0.998,
        "worker_three_rate": 0.85,
        "control_worker_three_rate": 0.90,
    }
    assert all(relative_held_gates(metrics, 0.998).values())
    assert not relative_held_gates(metrics, 0.999)["crop_not_below_control"]
