import torch

from cgauto.train_d130a_cross_sign_pairwise_soft_ranker import (
    cross_sign_metrics,
    cross_sign_pairwise_loss,
    model_gates,
)


def test_pairwise_loss_balances_eligible_roots():
    raw = torch.tensor([[1.0, 0.0, 99.0], [0.0, 0.0, 0.0]])
    values = torch.tensor([[1.0, -1.0, float("-inf")], [1.0, -1.0, -2.0]])
    valid = torch.tensor([[True, True, False], [True, True, True]])
    loss = cross_sign_pairwise_loss(raw, values, valid)
    expected = (torch.nn.functional.softplus(torch.tensor(-1.0)) + torch.log(torch.tensor(2.0))) / 2
    assert torch.isclose(loss, expected)


def test_cross_sign_metrics_report_pair_and_winner_quality():
    raw = torch.tensor([[2.0, 1.0, 0.0], [0.0, 2.0, 1.0]])
    values = torch.tensor([[1.0, -1.0, -2.0], [1.0, -1.0, -2.0]])
    valid = torch.ones_like(raw, dtype=torch.bool)
    metrics = cross_sign_metrics(raw, values, valid)
    assert metrics["train_cross_sign_pair_accuracy"] == 0.5
    assert metrics["train_cross_sign_winner_positive_rate"] == 0.5
    assert metrics["train_mixed_sign_roots"] == 2


def test_model_gates_extend_d119_structure():
    summary = {
        "train_mean_proposal_regret": 18.0,
        "train_within_10_rate": 0.45,
        "train_gate_balanced_accuracy": 0.60,
        "train_gate_act_recall": 0.50,
        "train_gate_wait_recall": 0.50,
        "train_cross_sign_pair_accuracy": 0.70,
        "train_cross_sign_winner_positive_rate": 0.50,
    }
    assert all(model_gates(summary).values())
