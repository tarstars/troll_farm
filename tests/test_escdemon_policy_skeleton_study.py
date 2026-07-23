from __future__ import annotations

from cgauto.escdemon_policy_skeleton_study import ranker_replay_prediction


def test_ranker_renderer_uses_held_fold_weights_and_keeps_commitment() -> None:
    left = (1, 1)
    right = (2, 2)
    event = {
        "candidates": [left, right],
        "features": {left: {"left": 1.0}, right: {"right": 1.0}},
    }
    base = {
        "game_id": 6,
        "unit_id": 3,
        "turn": 1,
        "label": "MOVE_TREE",
        "actual_target": right,
        "singleton_targets": {},
        "tree_options": {"MOVE_TREE": event},
    }
    rows = [
        base,
        {
            **base,
            "turn": 2,
            "label": "MOVE_TREE_RIPE",
            "tree_options": {},
        },
    ]
    weights = {fold: {"right": 2.0} for fold in range(5)}

    result = ranker_replay_prediction(
        rows, ["MOVE_TREE", "MOVE_OTHER"], weights
    )

    assert result["move_target_exact"] == 2
    assert result["all_worker_commands_exact"] == 2
