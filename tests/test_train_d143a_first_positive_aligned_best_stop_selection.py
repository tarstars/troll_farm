from __future__ import annotations

import pytest
import torch
from torch.nn import functional

from cgauto import train_d137a_task_sequence_best_stop_gate_q6 as d137
from cgauto import train_d140a_eight_block_best_stop_selection as d140
from cgauto import train_d143a_first_positive_aligned_best_stop_selection as d143


def test_multi_positive_hard_loss_matches_frozen_class_mass() -> None:
    logits = torch.tensor(
        [[2.0, 1.0, -1.0], [1.0, -1.0, 9.0], [0.5, -0.5, 9.0]]
    )
    valid = torch.tensor(
        [[True, True, True], [True, True, False], [True, True, False]]
    )
    targets = torch.tensor(
        [[True, True, False], [False, False, False], [True, True, False]]
    )
    actual = d143.multi_positive_hard_stop_losses(logits, valid, targets)
    expected = torch.stack(
        (
            0.5
            * (
                torch.stack(
                    (
                        functional.softplus(torch.tensor(-2.0)),
                        functional.softplus(torch.tensor(-1.0)),
                    )
                ).mean()
                + functional.softplus(torch.tensor(-1.0))
            ),
            torch.stack(
                (
                    functional.softplus(torch.tensor(1.0)),
                    functional.softplus(torch.tensor(-1.0)),
                )
            ).mean(),
            torch.stack(
                (
                    functional.softplus(torch.tensor(-0.5)),
                    functional.softplus(torch.tensor(0.5)),
                )
            ).mean(),
        )
    )
    assert torch.allclose(actual, expected)


def test_duplicate_same_class_root_does_not_change_task_class_mass() -> None:
    base = d143.multi_positive_hard_stop_losses(
        torch.tensor([[1.5, -0.5]]),
        torch.tensor([[True, True]]),
        torch.tensor([[True, False]]),
    )
    duplicated = d143.multi_positive_hard_stop_losses(
        torch.tensor([[1.5, 1.5, -0.5]]),
        torch.tensor([[True, True, True]]),
        torch.tensor([[True, True, False]]),
    )
    assert torch.equal(base, duplicated)


def test_first_positive_dataset_labels_every_positive_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sequence = {
        "values": torch.tensor([[3.0, 1.0, -2.0], [-1.0, -2.0, float("-inf")]]),
        "valid": torch.tensor([[True, True, True], [True, True, False]]),
        "hard_stop_targets": torch.tensor(
            [[True, False, False], [False, False, False]]
        ),
        "summary": {"positive_stop_tasks": 1, "hard_positive_roots": 1},
    }
    monkeypatch.setattr(d143.d137, "sequence_dataset", lambda ranker, dataset: sequence)
    result = d143.first_positive_sequence_dataset(object(), {})
    assert torch.equal(
        result["hard_stop_targets"],
        torch.tensor([[True, True, False], [False, False, False]]),
    )
    assert result["summary"]["positive_stop_tasks"] == 1
    assert result["summary"]["hard_positive_roots"] == 2


def test_hard_loss_rejects_target_outside_valid_roots() -> None:
    with pytest.raises(ValueError, match="outside valid roots"):
        d143.multi_positive_hard_stop_losses(
            torch.zeros((1, 2)),
            torch.tensor([[True, False]]),
            torch.tensor([[False, True]]),
        )


def test_d143_retains_eight_block_seed_and_worker_contract() -> None:
    assert d143.BLOCKS == d140.BLOCKS == 8
    assert d143.WORKERS == d140.WORKERS == 4
    assert d137.SEED_PAIRS == (
        (13_401, 13_701),
        (13_402, 13_702),
        (13_403, 13_703),
        (13_404, 13_704),
    )
