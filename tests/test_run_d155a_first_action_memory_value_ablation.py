from cgauto import run_d155a_first_action_memory_value_ablation as d155


def test_behavior_signature_ignores_model_hash_noise():
    candidate = {
        "architecture": "history_concat_compact",
        "seed": 15301,
        "held_counts": {"groups": 2},
        "held_gates": {"mean": False},
        "eligible": False,
        "folds": [
            {"held_counts": {"groups": 1}, "model_hash": "a"},
            {"held_counts": {"groups": 1}, "model_hash": "b"},
        ],
    }
    left = {"candidates": [candidate]}
    right = {
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
    assert d155.behavior_signature(left) == d155.behavior_signature(right)
