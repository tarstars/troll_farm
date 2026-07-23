from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d135a_winner_conditioned_action_gate_q6 as d135
from cgauto import train_d141a_task_balanced_best_stop_selection as d141
from cgauto import train_d142a_shared_ranker_dual_gate_selection as d142


class _FeatureGate(nn.Module):
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return features[..., 0]


def _sequence() -> dict:
    logits = torch.tensor([[2.0, -1.0, 0.5], [-0.5, 1.0, 9.0]])
    features = torch.zeros((2, 3, d135.GATE_INPUTS))
    features[..., 0] = logits
    valid = torch.tensor([[True, True, True], [True, True, False]])
    targets = torch.tensor([[True, False, False], [False, False, False]])
    values = torch.tensor([[4.0, -2.0, 1.0], [-1.0, -3.0, float("-inf")]])
    augmented_values = torch.cat((values, torch.zeros((2, 1))), dim=1)
    maximum = augmented_values.max(dim=1, keepdim=True).values
    return {
        "features": features,
        "valid": valid,
        "hard_stop_targets": targets,
        "soft_stop_targets": torch.softmax((augmented_values - maximum) / 10.0, dim=1),
        "augmented_valid": torch.cat(
            (valid, torch.ones((2, 1), dtype=torch.bool)), dim=1
        ),
        "task_order": [0, 1],
    }


def test_dual_gate_has_one_shared_ranker_and_7475_parameters() -> None:
    ranker = d115.CompactActClassifier()
    model = d142.DualGateController(ranker, d135.WinnerGate(), d135.WinnerGate())
    assert model.ranker is ranker
    assert d115.parameter_count(model) == d142.PARAMETERS == 7_475


def test_gate_composition_is_exact_arithmetic_mean() -> None:
    root = torch.tensor([-2.0, 1.0, 7.0])
    task = torch.tensor([4.0, 3.0, -1.0])
    assert torch.equal(
        d142.average_gate_tensors(root, task), torch.tensor([1.0, 2.0, 3.0])
    )


def test_dual_losses_reproduce_source_hard_normalizations() -> None:
    gate = _FeatureGate()
    sequence = _sequence()
    indices = torch.arange(2)
    _, root_hard = d142.gate_sequence_losses(
        gate, sequence, indices, "root-weighted"
    )
    _, task_hard = d142.gate_sequence_losses(
        gate, sequence, indices, "task-balanced"
    )
    logits = gate(sequence["features"])
    valid = sequence["valid"]
    targets = sequence["hard_stop_targets"]
    assert torch.equal(
        root_hard,
        functional.binary_cross_entropy_with_logits(
            logits[valid], targets[valid].float()
        ),
    )
    assert torch.equal(
        task_hard,
        d141.task_balanced_hard_stop_losses(logits, valid, targets).mean(),
    )


def test_component_hash_uses_source_controller_state_names() -> None:
    ranker = d115.CompactActClassifier()
    gate = d135.WinnerGate()
    source = d135.WinnerController(ranker)
    source.gate = gate
    assert d142.component_hash(ranker, gate) == d115.canonical_model_hash(source)


def test_expected_component_matrix_covers_every_fold_and_seed() -> None:
    matrix = d142.expected_component_hashes()
    assert len(matrix) == 32
    assert {block for block, _ in matrix} == set(range(8))
    assert {seed for _, seed in matrix} == {13_401, 13_402, 13_403, 13_404}
    assert all(
        set(value) == {"root_weighted", "task_balanced"}
        for value in matrix.values()
    )
