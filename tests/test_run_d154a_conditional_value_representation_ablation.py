from cgauto import run_d154a_conditional_value_representation_ablation as d154


def test_behavior_signature_excludes_training_float_noise():
    candidate = {
        "representation": "semantic109",
        "seed": 15301,
        "held_counts": {"groups": 2},
        "held_gates": {"mean": False},
        "eligible": False,
        "folds": [
            {
                "held_counts": {"groups": 1},
                "model_hash": "left",
                "training": {"loss": 1.0},
            },
            {
                "held_counts": {"groups": 1},
                "model_hash": "right",
                "training": {"loss": 2.0},
            },
        ],
    }
    left = {"candidates": [candidate]}
    changed = {
        "candidates": [
            {
                **candidate,
                "folds": [
                    {**candidate["folds"][0], "model_hash": "changed"},
                    candidate["folds"][1],
                ],
            }
        ]
    }
    assert d154.behavior_signature(left) == d154.behavior_signature(changed)
