import torch

from cgauto.train_d128a_absolute_value_anchored_soft_ranker import (
    absolute_value_metrics,
    model_gates,
    root_balanced_value_loss,
)


def test_value_loss_balances_roots_not_proposal_count():
    raw = torch.tensor([[1.0, 1.0, 100.0], [1.0, 0.0, 0.0]])
    values = torch.tensor([[0.0, 0.0, float("-inf")], [0.0, float("-inf"), float("-inf")]])
    valid = torch.tensor([[True, True, False], [True, False, False]])
    loss = root_balanced_value_loss(raw, values, valid)
    assert torch.isclose(loss, torch.tensor(0.5))


def test_absolute_value_metrics_reports_sign_and_regret():
    logits = torch.tensor([[2.0, 1.0], [-1.0, -2.0]])
    dataset = {
        "proposal_values": torch.tensor([[10.0, 20.0], [-2.0, -4.0]])
    }
    metrics = absolute_value_metrics(logits, dataset)
    assert metrics["train_mean_proposal_regret"] == 5.0
    assert metrics["train_value_sign_act_recall"] == 1.0
    assert metrics["train_value_sign_wait_recall"] == 1.0


def test_absolute_model_gates_extend_d119_structure():
    summary = {
        "train_mean_proposal_regret": 18.0,
        "train_within_10_rate": 0.45,
        "train_gate_balanced_accuracy": 0.60,
        "train_gate_act_recall": 0.50,
        "train_gate_wait_recall": 0.50,
        "train_value_sign_balanced_accuracy": 0.60,
        "train_value_sign_act_recall": 0.50,
        "train_value_sign_wait_recall": 0.50,
    }
    assert all(model_gates(summary).values())
