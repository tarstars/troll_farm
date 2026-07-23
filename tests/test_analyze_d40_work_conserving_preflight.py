from __future__ import annotations

from cgauto.analyze_d40_work_conserving_preflight import analyze


OPPONENTS = tuple(f"opponent_{index}" for index in range(8))


def rows(policy: str, *, weak: bool = False) -> list[dict]:
    output = []
    for seed in (1, 2):
        for seat in (0, 1):
            for opponent in OPPONENTS:
                if policy == "work_conserving":
                    margin = 40 if weak else 100
                    workers = 2 if weak else 3
                    idle = 1
                elif policy == "evacuation":
                    margin = 30
                    workers = 2
                    idle = 4
                else:
                    margin = 0
                    workers = 2
                    idle = 1
                own = 200 if policy == "work_conserving" else 100
                opponent_score = own - margin
                action_counts = {
                    "train_none": 1,
                    "train_producer": 1,
                    "train_chopper": 1,
                    "idle": idle,
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
                        "own_workers": workers,
                        "opponent_workers": 2,
                        "successful_trains": workers - 1,
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


def report(work: list[dict], *, repeat_verified: bool = True) -> dict:
    return analyze(
        work,
        rows("evacuation"),
        rows("random"),
        repeat_verified=repeat_verified,
        expected_seeds={1, 2},
        opponents=OPPONENTS,
    )


def test_passing_preflight_opens_behavior_learning() -> None:
    result = report(rows("work_conserving"))
    assert result["preflight_pass"] is True
    assert result["decision"] == "open_behavior_learning_protocol"
    assert result["idle_ratio_vs_evacuation"] == 0.25


def test_weak_workforce_and_margin_close_teacher() -> None:
    result = report(rows("work_conserving", weak=True))
    assert result["preflight_pass"] is False
    assert result["gates"]["margin_advantage_over_random_at_least_50"] is False
    assert result["gates"]["worker_three_rate_at_least_50pct"] is False


def test_idle_gate_is_independent() -> None:
    work = rows("work_conserving")
    for row in work:
        row["selected_decisions"] += 2
        row["idle"] += 2
    result = report(work)
    assert result["gates"]["idle_at_most_half_evacuation"] is False


def test_integrity_failure_is_hard() -> None:
    work = rows("work_conserving")
    work[0]["deposit_prediction_failures"] = 1
    result = report(work)
    assert result["gates"]["work_conserving_integrity"] is False
    assert result["preflight_pass"] is False


def test_repeat_mismatch_is_hard() -> None:
    result = report(rows("work_conserving"), repeat_verified=False)
    assert result["gates"]["work_conserving_repeat_byte_identical"] is False
    assert result["preflight_pass"] is False
