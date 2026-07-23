from __future__ import annotations

from cgauto.analyze_d39_shack_evacuation_preflight import analyze


OPPONENTS = tuple(f"opponent_{index}" for index in range(8))


def rows(policy: str, *, weak: bool = False) -> list[dict]:
    output = []
    for seed in (1, 2):
        for seat in (0, 1):
            for opponent in OPPONENTS:
                if policy == "evacuation":
                    margin = 30 if weak else 80
                    own_workers = 2 if weak else 3
                elif policy == "deficit":
                    margin = 20
                    own_workers = 2 if seat == 0 else 1
                else:
                    margin = 0
                    own_workers = 2
                own = 180 if policy == "evacuation" else 100
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
                        "own_workers": own_workers,
                        "opponent_workers": 2,
                        "successful_trains": own_workers - 1,
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


def report(evacuation: list[dict], *, repeat_verified: bool = True) -> dict:
    return analyze(
        evacuation,
        rows("deficit"),
        rows("random"),
        repeat_verified=repeat_verified,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )


def test_passing_preflight_opens_behavior_learning() -> None:
    result = report(rows("evacuation"))
    assert result["preflight_pass"] is True
    assert result["decision"] == "open_behavior_learning_protocol"


def test_margin_and_workforce_gates_reject_weak_evacuation() -> None:
    result = report(rows("evacuation", weak=True))
    assert result["preflight_pass"] is False
    assert result["gates"]["margin_advantage_over_random_at_least_50"] is False
    assert result["gates"]["margin_advantage_over_deficit_at_least_50"] is False
    assert result["gates"]["worker_two_improvement_over_deficit_at_least_40pp"] is True


def test_control_integrity_failure_is_hard() -> None:
    deficit = rows("deficit")
    deficit[0]["deposit_prediction_failures"] = 1
    result = analyze(
        rows("evacuation"),
        deficit,
        rows("random"),
        repeat_verified=True,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )
    assert result["gates"]["deficit_ablation_integrity"] is False
    assert result["preflight_pass"] is False


def test_family_regression_is_independent_of_global_margin() -> None:
    evacuation = rows("evacuation")
    for row in evacuation:
        if row["opponent"] == OPPONENTS[0]:
            row["margin"] = -20
            row["opponent_score"] = row["own_score"] + 20
            row["opponent_return"] = row["opponent_score"] / 100
            row["margin_return"] = -0.2
    result = report(evacuation)
    assert result["gates"]["margin_advantage_over_random_at_least_50"] is True
    assert result["gates"]["no_opponent_family_below_minus_10"] is False


def test_repeat_mismatch_is_hard() -> None:
    result = report(rows("evacuation"), repeat_verified=False)
    assert result["gates"]["evacuation_repeat_byte_identical"] is False
    assert result["preflight_pass"] is False
