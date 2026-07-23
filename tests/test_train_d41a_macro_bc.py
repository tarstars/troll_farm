from __future__ import annotations

import torch

from cgauto.train_d41a_macro_bc import (
    CandidateScorer,
    closed_loop_gate,
    macro_f1,
    masked_scores,
)


def test_candidate_scorer_has_frozen_parameter_count() -> None:
    model = CandidateScorer()
    assert sum(parameter.numel() for parameter in model.parameters()) == 1_985


def test_masked_scores_exclude_candidate_padding() -> None:
    model = CandidateScorer()
    features = torch.zeros((2, 5, 44))
    scores = masked_scores(model, features, torch.tensor([2, 4]))
    assert torch.all(scores[0, 2:] < -1e20)
    assert torch.all(scores[1, 4:] < -1e20)
    assert torch.all(scores[0, :2] > -1e20)


def test_macro_f1_is_exact_for_exact_planes() -> None:
    planes = list(range(9)) * 3
    assert macro_f1(planes, planes) == 1.0


def _rows(margin: int, workers: int) -> list[dict]:
    output = []
    for opponent in (
        "resident",
        "gold_adaptive",
        "compact_gold",
        "norx_native_three",
        "legend_balanced",
        "mybot",
        "script_boss",
        "silver_boss",
    ):
        output.append(
            {
                "opponent": opponent,
                "own_score": 200,
                "opponent_score": 200 - margin,
                "margin": margin,
                "own_workers": workers,
                "own_created_crops": 1,
                "invalid_direct_commands": 0,
                "provenance_failures": 0,
                "deposit_prediction_failures": 0,
            }
        )
    return output


def test_closed_loop_gate_compares_teacher_and_random() -> None:
    result = closed_loop_gate(_rows(110, 3), _rows(120, 3), _rows(0, 1))
    assert result["pass"] is True
    weak = closed_loop_gate(_rows(20, 2), _rows(120, 3), _rows(0, 1))
    assert weak["pass"] is False
