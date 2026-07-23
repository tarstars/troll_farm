from __future__ import annotations

from cgauto.analyze_d38_macro_deficit_preflight import analyze


OPPONENTS = tuple(f"opponent_{index}" for index in range(8))


def rows(policy: str, *, strong: bool = True) -> list[dict]:
    output = []
    for seed in (1, 2):
        for seat in (0, 1):
            for opponent in OPPONENTS:
                deficit = policy == "deficit"
                margin = 80 if deficit and strong else (20 if deficit else 0)
                own = 180 if deficit else 100
                opponent_score = own - margin
                action_counts = {
                    "train_none": 1,
                    "train_producer": 1,
                    "train_chopper": 1,
                    "idle": 1,
                    "bank": 1,
                    "fell_bank": 1,
                    "harvest_bank": 1,
                    "renew": 1,
                    "mine_bank": 1,
                }
                output.append(
                    {
                        "map_seed": seed,
                        "seat": seat,
                        "opponent": opponent,
                        "policy": policy,
                        "turn": 301,
                        "own_score": own,
                        "opponent_score": opponent_score,
                        "margin": margin,
                        "own_return": own / 100,
                        "opponent_return": opponent_score / 100,
                        "margin_return": margin / 100,
                        "own_workers": 3 if deficit and strong else 2,
                        "opponent_workers": 2,
                        "successful_trains": 2 if deficit and strong else 1,
                        "completed_jobs": 8,
                        "invalidated_jobs": 0,
                        "invalid_direct_commands": 0,
                        "provenance_failures": 0,
                        "deposit_prediction_failures": 0,
                        "selected_decisions": sum(action_counts.values()),
                        "selected_jobs": 6,
                        "selected_nonidle_jobs": 5,
                        "selected_renew_jobs": 1,
                        "own_created_crops": 1,
                        "opponent_created_crops": 1,
                        "ambiguous_created_crops": 0,
                        "action_hash": 1,
                        "state_hash": 2,
                        **action_counts,
                    }
                )
    return output


def test_passing_preflight_opens_behavior_learning() -> None:
    report = analyze(
        rows("deficit"),
        rows("random"),
        repeat_verified=True,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )
    assert report["preflight_pass"] is True
    assert report["decision"] == "open_behavior_learning_protocol"
    assert report["nonnegative_opponent_families"] == 8


def test_weak_teacher_is_closed_before_learning() -> None:
    report = analyze(
        rows("deficit", strong=False),
        rows("random"),
        repeat_verified=True,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )
    assert report["preflight_pass"] is False
    assert report["gates"]["deficit_worker_three_rate_at_least_15pct"] is False
    assert report["gates"]["deficit_margin_advantage_at_least_50"] is False


def test_deposit_prediction_corruption_is_a_hard_integrity_failure() -> None:
    deficit = rows("deficit")
    deficit[0]["deposit_prediction_failures"] = 1
    report = analyze(
        deficit,
        rows("random"),
        repeat_verified=True,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )
    assert report["integrity"]["deficit"]["complete"] is False
    assert report["gates"]["deficit_integrity"] is False


def test_family_regression_gate_is_independent_of_global_mean() -> None:
    deficit = rows("deficit")
    for row in deficit:
        if row["opponent"] == OPPONENTS[0]:
            row["margin"] = -20
            row["opponent_score"] = row["own_score"] + 20
            row["opponent_return"] = row["opponent_score"] / 100
            row["margin_return"] = -0.2
    report = analyze(
        deficit,
        rows("random"),
        repeat_verified=True,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )
    assert report["gates"]["deficit_margin_advantage_at_least_50"] is True
    assert report["gates"]["no_opponent_family_below_minus_10"] is False


def test_repeat_mismatch_is_a_hard_failure() -> None:
    report = analyze(
        rows("deficit"),
        rows("random"),
        repeat_verified=False,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )
    assert report["preflight_pass"] is False
    assert report["gates"]["deficit_repeat_byte_identical"] is False
