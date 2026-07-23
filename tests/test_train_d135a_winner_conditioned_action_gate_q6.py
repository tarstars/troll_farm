import torch

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto.train_d135a_winner_conditioned_action_gate_q6 import (
    WinnerController,
    held_policy_gates,
    winner_context,
)


def _dataset():
    actions = torch.zeros((1, 2, 379), dtype=torch.float32)
    actions[0, 0, 0] = 1.0
    actions[0, 1, 1] = 1.0
    return {
        "action_features": actions,
        "valid": torch.tensor([[True, True]]),
        "state_features": torch.zeros((1, 64)),
        "proposal_values": torch.tensor([[10.0, -2.0]]),
        "root_order": [((1, 0, "resident"), 0)],
    }


def test_winner_target_describes_ranker_choice_not_oracle_best():
    ranker = d115.CompactActClassifier()
    with torch.no_grad():
        ranker.hidden.weight.zero_()
        ranker.hidden.bias.zero_()
        ranker.hidden.weight[0, 1] = 1.0
        ranker.output.weight.zero_()
        ranker.output.bias.zero_()
        ranker.output.weight[0, 0] = 1.0
    features, targets, values, selected = winner_context(ranker, _dataset())
    assert features.shape == (1, 84)
    assert selected.tolist() == [1]
    assert values.tolist() == [-2.0]
    assert targets.tolist() == [False]
    assert torch.isfinite(features).all()


def test_controller_meets_frozen_parameter_budget():
    model = WinnerController(d115.CompactActClassifier())
    assert d115.parameter_count(model) == 6_786


def test_held_gate_requires_each_block_activity_guardrail():
    metrics = {
        "mean_margin_delta": 3.0,
        "strict_improvement_rate": 0.5,
        "block_mean_margin_delta": {"0": 1.0, "1": 1.0, "2": 1.0, "3": 1.0},
        "worst_family": 0.0,
        "positive_families": 8,
        "mean_own_score_delta": 1.0,
        "mean_opponent_score_delta": -1.0,
        "intervention_rate": 0.80,
        "block_intervention_rate": {"0": 0.80, "1": 0.80, "2": 0.80, "3": 0.86},
        "crop_rate": 1.0,
        "control_crop_rate": 1.0,
        "worker_three_rate": 0.9,
        "control_worker_three_rate": 0.9,
    }
    assert not held_policy_gates(metrics)["every_block_activity_10_to_85pct"]
    metrics["block_intervention_rate"]["3"] = 0.85
    assert held_policy_gates(metrics)["every_block_activity_10_to_85pct"]
