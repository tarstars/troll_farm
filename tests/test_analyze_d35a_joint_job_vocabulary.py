from cgauto.analyze_d35a_joint_job_vocabulary import (
    direct_job_label,
    move_target,
    resolve_move_jobs,
    run_lengths,
    top_k_coverage,
)


def unit(carry=None) -> dict:
    return {"x": 3, "y": 4, "carry": carry or [0, 0, 0, 0, 0, 0]}


def test_direct_jobs_distinguish_opponent_crop_and_natural_fell() -> None:
    target = (3, 4)
    assert direct_job_label("CHOP 7", unit(), {}, player=0) == "FELL_BANK"
    assert (
        direct_job_label(
            "CHOP 7", unit(), {target: frozenset({1})}, player=0
        )
        == "PRESSURE"
    )
    assert (
        direct_job_label(
            "CHOP 7", unit(), {target: frozenset({0, 1})}, player=0
        )
        == "FELL_BANK"
    )


def test_drop_label_uses_pre_step_cargo_families() -> None:
    assert direct_job_label("DROP 7", unit([1, 0, 0, 0, 0, 0]), {}, 0) == "RENEW"
    assert direct_job_label("DROP 7", unit([0, 0, 0, 0, 2, 0]), {}, 0) == "MINE_BANK"
    assert direct_job_label("DROP 7", unit([0, 0, 0, 0, 0, 2]), {}, 0) == "FELL_BANK"
    assert direct_job_label("DROP 7", unit([1, 0, 0, 0, 0, 2]), {}, 0) == "MIXED_BANK"


def test_move_resolution_uses_future_job_and_stable_target_fallback() -> None:
    events = [
        {
            "direct_label": None,
            "label": None,
            "target": (5, 5),
        },
        {
            "direct_label": "FELL_BANK",
            "label": "FELL_BANK",
            "target": None,
        },
        {
            "direct_label": None,
            "label": None,
            "target": (8, 8),
        },
        {
            "direct_label": None,
            "label": None,
            "target": (8, 8),
        },
    ]
    resolve_move_jobs(events, lookahead=1)
    assert events[0]["label"] == "FELL_BANK"
    assert events[2]["label"] == "UNKNOWN"
    assert events[3]["label"] == "UNKNOWN"


def test_run_and_signature_summaries_are_deterministic() -> None:
    events = {
        1: [
            {"label": "RENEW"},
            {"label": "RENEW"},
            {"label": "IDLE"},
            {"label": "FELL_BANK"},
        ]
    }
    assert run_lengths(events) == [2, 1]
    assert top_k_coverage(Counter({"a": 5, "b": 3, "c": 2}), 2) == 0.8
    assert move_target("MOVE 7 8 9") == (8, 9)
    assert move_target("CHOP 7") is None
from collections import Counter

