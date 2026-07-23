from __future__ import annotations

from cgauto.top_policy_objective_study import (
    cross_validate,
    objective_label,
    row_features,
)


def test_objective_label_distinguishes_resource_targets() -> None:
    context = {
        "own_shack": (0, 0),
        "opponent_shack": (9, 9),
        "iron": {(3, 3)},
        "plants": {
            (4, 4): {"fruits": 2},
            (5, 5): {"fruits": 0},
        },
    }
    assert objective_label("MOVE 7 0 0", context) == "MOVE_BANK"
    assert objective_label("MOVE 7 3 3", context) == "MOVE_IRON"
    assert objective_label("MOVE 7 4 4", context) == "MOVE_TREE_RIPE"
    assert objective_label("MOVE 7 5 5", context) == "MOVE_TREE"
    assert objective_label("PICK 7 BANANA", context) == "PICK_BANANA"


def test_row_features_use_only_current_state_and_map() -> None:
    state = {
        "inventories": [[5, 5, 0, 0, 5, 0], [0, 0, 0, 0, 0, 0]],
        "units": [
            {
                "id": 0,
                "player": 0,
                "x": 1,
                "y": 0,
                "ms": 1,
                "cc": 1,
                "hp": 1,
                "chop": 1,
                "carry": [0, 0, 0, 0, 0, 0],
            }
        ],
        "plants": [{"x": 2, "y": 0, "fruits": 2}],
    }
    map_terrain = {
        "shacks": [(0, 0), (9, 9)],
        "iron": {(4, 0)},
        "walkable": set(),
        "water": set(),
    }
    features = row_features(state, map_terrain, 0, state["units"][0], 0, 1)

    assert features["phase"] == "01-05"
    assert features["on_cell"] == "bank_edge"
    assert features["nearest_ripe"] == "1"
    assert features["cheap_train_affordable"] == "True"


def test_cross_validation_never_uses_held_group() -> None:
    rows = []
    for group, label in ((0, "CHOP"), (1, "HARVEST")):
        for _ in range(3):
            rows.append(
                {
                    "group": group,
                    "label": label,
                    "features": {
                        "phase": "01-05",
                        "ordinal": "0",
                        "role": "starter",
                        "carry_class": "empty",
                        "full": "False",
                        "bank_distance": "1",
                        "on_cell": "open",
                        "unit_count": "1",
                        "score_bucket": "-9..9",
                        "nearest_ripe": "1",
                        "nearest_tree": "1",
                        "nearest_iron": "none",
                        "cheap_train_affordable": "False",
                    },
                }
            )
    result = cross_validate(rows, "group", [0, 1])

    assert result["rows"] == 6
    assert result["accuracy"] == 0
