import torch

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto.train_d137a_task_sequence_best_stop_gate_q6 import (
    selection_key,
    sequence_dataset,
)


def _ranker_selecting_first_slot():
    ranker = d115.CompactActClassifier()
    with torch.no_grad():
        ranker.hidden.weight.zero_()
        ranker.hidden.bias.zero_()
        ranker.hidden.weight[0, 0] = 1.0
        ranker.output.weight.zero_()
        ranker.output.bias.zero_()
        ranker.output.weight[0, 0] = 1.0
    return ranker


def test_sequence_target_marks_earliest_best_root_and_explicit_wait():
    roots = [
        ((1, 0, "resident"), 0),
        ((1, 0, "resident"), 1),
        ((1, 0, "resident"), 2),
        ((2, 0, "resident"), 0),
    ]
    actions = torch.zeros((4, 2, 379))
    actions[:, 0, 0] = 1.0
    dataset = {
        "action_features": actions,
        "valid": torch.ones((4, 2), dtype=torch.bool),
        "state_features": torch.zeros((4, 64)),
        "proposal_values": torch.tensor(
            [[5.0, -1.0], [8.0, -1.0], [8.0, -1.0], [-2.0, -3.0]]
        ),
        "root_order": roots,
    }
    result = sequence_dataset(_ranker_selecting_first_slot(), dataset)
    assert result["hard_stop_targets"].tolist() == [
        [False, True, False],
        [False, False, False],
    ]
    assert result["summary"]["positive_stop_tasks"] == 1
    assert torch.allclose(
        result["soft_stop_targets"].sum(dim=1), torch.ones(2)
    )
    assert result["soft_stop_targets"][1, -1] > result["soft_stop_targets"][1, 0]


def test_selection_prioritizes_family_floor_before_worst_block():
    safer_family = {
        "ranker_seed": 1,
        "held_policy_metrics": {
            "worst_family": 1.0,
            "block_mean_margin_delta": {"0": 1.0},
            "mean_margin_delta": 2.0,
            "strict_improvement_rate": 0.4,
            "intervention_rate": 0.5,
        },
    }
    better_block = {
        "ranker_seed": 2,
        "held_policy_metrics": {
            "worst_family": 0.0,
            "block_mean_margin_delta": {"0": 10.0},
            "mean_margin_delta": 10.0,
            "strict_improvement_rate": 0.8,
            "intervention_rate": 0.5,
        },
    }
    assert selection_key(safer_family) > selection_key(better_block)
