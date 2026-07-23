import numpy as np
import torch

from cgauto.train_d118a_soft_value_q6_ranker_state_gate import (
    fit_policy_gates,
    model_fit_gates,
    soft_cross_entropy,
    train_soft_value_model,
)


def test_soft_value_targets_are_shift_invariant_and_prefer_better_arms():
    first = torch.softmax(torch.tensor([0.0, -1.0, -2.0]), dim=0)
    second = torch.softmax(torch.tensor([100.0, 99.0, 98.0]), dim=0)
    assert torch.allclose(first, second)
    assert first[0] > first[1] > first[2]
    logits = torch.tensor([[1.0, 0.0, float("-inf")]])
    targets = torch.tensor([[0.75, 0.25, 0.0]])
    valid = torch.tensor([[True, True, False]])
    assert torch.isfinite(soft_cross_entropy(logits, targets, valid))


def test_soft_value_training_is_deterministic_and_finite():
    generator = np.random.Generator(np.random.PCG64(118))
    actions = generator.normal(size=(8, 3, 379)).astype(np.float32)
    actions[:, :, 0] = 1.0
    states = generator.normal(size=(8, 64)).astype(np.float32)
    values = torch.tensor(
        [[3.0, 2.0, 1.0], [1.0, 3.0, 2.0]] * 4,
        dtype=torch.float32,
    )
    dataset = {
        "action_features": torch.from_numpy(actions),
        "valid": torch.ones((8, 3), dtype=torch.bool),
        "state_features": torch.from_numpy(states),
        "soft_rank_targets": torch.softmax(values / 10.0, dim=1),
        "proposal_values": values,
        "act_targets": torch.tensor([True, False] * 4),
    }
    first, first_summary = train_soft_value_model(
        dataset, 11801, epochs=2, root_batch_size=4
    )
    second, second_summary = train_soft_value_model(
        dataset, 11801, epochs=2, root_batch_size=4
    )
    assert first_summary["model_hash"] == second_summary["model_hash"]
    assert first_summary["parameters"] == 6_626
    assert np.isfinite(first_summary["final_soft_rank_cross_entropy"])
    assert all(
        torch.equal(first.state_dict()[name], second.state_dict()[name])
        for name in first.state_dict()
    )


def test_regret_and_policy_fit_gates_accept_useful_model():
    summary = {
        "train_mean_proposal_regret": 15.0,
        "train_within_10_rate": 0.5,
        "train_gate_balanced_accuracy": 0.7,
        "train_gate_act_recall": 0.65,
        "train_gate_wait_recall": 0.75,
    }
    metrics = {
        "mean_margin_delta": 4.0,
        "strict_improvement_rate": 0.4,
        "fold_mean_margin_delta": {"0": 3.0, "1": 5.0},
        "worst_family": -2.0,
        "positive_families": 7,
        "intervention_rate": 0.5,
        "crop_rate": 1.0,
        "worker_three_rate": 0.9,
        "control_worker_three_rate": 0.92,
    }
    assert all(model_fit_gates(summary).values())
    assert all(fit_policy_gates(metrics).values())
