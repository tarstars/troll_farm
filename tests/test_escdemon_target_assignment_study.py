from __future__ import annotations

from cgauto.escdemon_target_assignment_study import (
    move_target,
    replay_prediction,
    singleton_targets,
)


def test_singleton_targets_only_emit_unique_semantic_coordinates() -> None:
    context = {
        "own_shack": (0, 0),
        "opponent_shack": (9, 9),
        "iron": {(3, 3)},
        "plants": {
            (4, 4): {"fruits": 1},
            (5, 5): {"fruits": 0},
            (6, 6): {"fruits": 0},
        },
    }

    result = singleton_targets(context)

    assert result["MOVE_BANK"] == (0, 0)
    assert result["MOVE_IRON"] == (3, 3)
    assert result["MOVE_TREE_RIPE"] == (4, 4)
    assert "MOVE_TREE" not in result


def test_replay_prediction_carries_its_own_exact_target_commitment() -> None:
    base = {
        "game_id": 1,
        "unit_id": 4,
        "turn": 1,
        "label": "MOVE_TREE",
        "actual_target": (5, 5),
        "singleton_targets": {"MOVE_TREE": (5, 5)},
    }
    rows = [
        dict(base),
        {
            **base,
            "turn": 2,
            "label": "MOVE_TREE_RIPE",
            "actual_target": (5, 5),
            "singleton_targets": {},
        },
    ]

    result = replay_prediction(rows, ["MOVE_TREE", "MOVE_OTHER"])

    assert result["move_target_exact"] == 2
    assert result["all_worker_commands_exact"] == 2


def test_move_target_rejects_non_move_commands() -> None:
    assert move_target("MOVE 7 3 4") == (3, 4)
    assert move_target("CHOP 7") is None
