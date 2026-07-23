from __future__ import annotations

from cgauto.norxondor_shared_state_distillation import (
    blocked_cross_validation,
    teacher_choice,
)


def test_teacher_is_strict_minimax_over_exact_models() -> None:
    group = [
        {"exact_prefix_transitions": 2, "margin_delta": 8},
        {"exact_prefix_transitions": 2, "margin_delta": -1},
        {"exact_prefix_transitions": 0, "margin_delta": 30},
    ]
    assert teacher_choice(group) is False
    group[1]["margin_delta"] = 1
    assert teacher_choice(group) is True


def test_blocked_validation_holds_out_whole_seed() -> None:
    keys = [(seed, 0, "a") for seed in range(6)]
    features = {item: {"value": float(item[0])} for item in keys}
    labels = {item: item[0] >= 4 for item in keys}
    report = blocked_cross_validation(
        keys,
        features,
        labels,
        {"max_depth": 2, "min_leaf": 1, "negative_weight": 1.0},
    )
    assert sum(
        report[name]
        for name in ("true_positive", "false_positive", "false_negative", "true_negative")
    ) == len(keys)
