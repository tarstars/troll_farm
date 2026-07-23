from __future__ import annotations

import pytest
import torch
from torch.nn import functional

from cgauto import train_d137a_task_sequence_best_stop_gate_q6 as d137
from cgauto import train_d140a_eight_block_best_stop_selection as d140
from cgauto import train_d141a_task_balanced_best_stop_selection as d141


def test_task_balanced_hard_stop_losses_match_frozen_definition() -> None:
    logits = torch.tensor(
        [[2.0, -2.0, 0.0], [1.0, -1.0, 7.0], [0.5, 9.0, 9.0]]
    )
    valid = torch.tensor(
        [[True, True, True], [True, True, False], [True, False, False]]
    )
    targets = torch.tensor(
        [[True, False, False], [False, False, False], [True, False, False]]
    )

    actual = d141.task_balanced_hard_stop_losses(logits, valid, targets)
    expected = torch.stack(
        (
            0.5
            * (
                functional.softplus(torch.tensor(-2.0))
                + torch.stack(
                    (
                        functional.softplus(torch.tensor(-2.0)),
                        functional.softplus(torch.tensor(0.0)),
                    )
                ).mean()
            ),
            torch.stack(
                (
                    functional.softplus(torch.tensor(1.0)),
                    functional.softplus(torch.tensor(-1.0)),
                )
            ).mean(),
            functional.softplus(torch.tensor(-0.5)),
        )
    )
    assert torch.allclose(actual, expected)


def test_duplicate_negative_root_does_not_reweight_a_positive_task() -> None:
    base = d141.task_balanced_hard_stop_losses(
        torch.tensor([[1.5, -0.5]]),
        torch.tensor([[True, True]]),
        torch.tensor([[True, False]]),
    )
    duplicated = d141.task_balanced_hard_stop_losses(
        torch.tensor([[1.5, -0.5, -0.5]]),
        torch.tensor([[True, True, True]]),
        torch.tensor([[True, False, False]]),
    )
    assert torch.equal(base, duplicated)


def test_hard_stop_loss_rejects_invalid_targets() -> None:
    with pytest.raises(ValueError, match="outside valid roots"):
        d141.task_balanced_hard_stop_losses(
            torch.zeros((1, 2)),
            torch.tensor([[True, False]]),
            torch.tensor([[False, True]]),
        )
    with pytest.raises(ValueError, match="at most one positive"):
        d141.task_balanced_hard_stop_losses(
            torch.zeros((1, 2)),
            torch.ones((1, 2), dtype=torch.bool),
            torch.ones((1, 2), dtype=torch.bool),
        )


def test_d141_retains_d140_evidence_and_seed_contract() -> None:
    _, _, descriptors = d140.corpus_descriptors()
    assert [row["block_id"] for row in descriptors] == list(range(8))
    assert [row["start_seed"] for row in descriptors] == [
        9_844_000,
        9_844_016,
        9_844_032,
        9_844_048,
        9_844_064,
        9_844_080,
        9_844_096,
        9_844_112,
    ]
    assert d141.BLOCKS == d140.BLOCKS == 8
    assert d141.WORKERS == d140.WORKERS == 4
    assert d137.SEED_PAIRS == (
        (13_401, 13_701),
        (13_402, 13_702),
        (13_403, 13_703),
        (13_404, 13_704),
    )
