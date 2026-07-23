from __future__ import annotations

import pytest

from cgauto.arena_rollout_model_audit import EXPECTED_MODELS, audit


def rollout_rows(game_ids: list[int], models: tuple[str, ...]) -> dict:
    return {
        (game_id, seat, model): {
            "control_margin": 10,
            "option_margin": 10 + (40 if model in ("gold_elite", "compact_gold") else -5),
            "delta": 40 if model in ("gold_elite", "compact_gold") else -5,
        }
        for game_id in game_ids
        for seat in (0, 1)
        for model in models
    }


def test_audit_reconstructs_selection_and_model_disagreement() -> None:
    forensics = {
        "rows": [
            {
                "game_id": 7,
                "selection": "option",
                "opponent": "field",
                "margin": -3,
                "won": False,
            }
        ]
    }
    result = audit(
        forensics,
        rollout_rows([7], EXPECTED_MODELS),
        rollout_rows([7], ("compact_gold",)),
    )
    assert result["selector_reconstruction"]["exact"]
    assert result["compact_gold_vs_gold_elite_exact_cells"] == 2
    assert result["selected_game_summary"] == {
        "games": 1,
        "arena_wins": 0,
        "all_models_positive": 0,
        "single_positive_model": 1,
        "negative_worst_model": 1,
    }


def test_audit_rejects_incomplete_rollout_coverage() -> None:
    forensics = {
        "rows": [
            {
                "game_id": 7,
                "selection": "control",
                "opponent": "field",
                "margin": 1,
                "won": True,
            }
        ]
    }
    with pytest.raises(ValueError, match="coverage mismatch"):
        audit(forensics, {}, {})
