from datetime import datetime, timedelta, timezone

from cgauto.arena_transfer_gate import (
    candidate_120_gate,
    candidate_180_gate,
    candidate_early_gate,
    control_gate,
)


BASE = datetime(2026, 7, 18, tzinfo=timezone.utc)


def checkpoint(
    *,
    games: int,
    score: float,
    minutes: int = 0,
    catastrophic_rate: float = 0.10,
    negative_mass: float = 1000,
    clean: bool = True,
) -> dict:
    return {
        "observed_at": (BASE + timedelta(minutes=minutes)).isoformat(),
        "matching_finished": games,
        "parsed_results": games,
        "identity_clean": clean,
        "unexpected_rows": [],
        "fetch_failures": [],
        "arena": {"score": score},
        "summary": {
            "catastrophic_rate": catastrophic_rate,
            "negative_margin_mass": negative_mass,
            "validity_runtime_signals": [],
        },
    }


def test_control_gate_requires_mature_delayed_read() -> None:
    initial = checkpoint(games=120, score=22.0)
    too_early = checkpoint(games=145, score=20.0, minutes=10)
    assert control_gate(initial)["status"] == "wait"
    assert control_gate(initial, too_early)["status"] == "wait"

    confirmed = checkpoint(games=140, score=21.3, minutes=15)
    assert control_gate(initial, confirmed)["status"] == "pass"


def test_control_gate_fails_floor_or_runtime_safety() -> None:
    assert control_gate(checkpoint(games=120, score=21.29))["status"] == "fail"
    dirty = checkpoint(games=120, score=24.0, clean=False)
    assert control_gate(dirty)["status"] == "fail"


def test_candidate_early_gate_only_rejects_clear_downside() -> None:
    control = checkpoint(games=60, score=24.0)
    reject = checkpoint(games=60, score=22.5)
    continue_ = checkpoint(games=60, score=22.51)
    assert candidate_early_gate(control, reject)["status"] == "reject"
    assert candidate_early_gate(control, continue_)["status"] == "continue"


def test_candidate_120_gate_extends_ambiguous_result() -> None:
    control = checkpoint(games=120, score=24.0)
    candidate = checkpoint(games=120, score=24.3, catastrophic_rate=0.11)
    report = candidate_120_gate(control, candidate)
    assert report["status"] == "extend-180"
    assert report["score_delta"] == 0.3000000000000007


def test_candidate_120_gate_requires_clean_delayed_confirmation() -> None:
    control = checkpoint(games=120, score=24.0)
    candidate = checkpoint(
        games=120,
        score=25.0,
        catastrophic_rate=0.11,
        negative_mass=1050,
    )
    assert candidate_120_gate(control, candidate)["status"] == "wait"
    confirm = checkpoint(games=145, score=25.1, minutes=15, negative_mass=1400)
    assert candidate_120_gate(control, candidate, confirm)["status"] == "promote"


def test_candidate_120_gate_rejects_tail_regression() -> None:
    control = checkpoint(games=120, score=24.0)
    candidate = checkpoint(
        games=120,
        score=25.0,
        catastrophic_rate=0.121,
        negative_mass=1000,
    )
    assert candidate_120_gate(control, candidate)["status"] == "reject"


def test_candidate_180_gate_requires_half_point_on_both_final_reads() -> None:
    control = checkpoint(games=180, score=24.0)
    candidate = checkpoint(games=180, score=24.5)
    confirm = checkpoint(games=205, score=24.6, minutes=15)
    assert candidate_180_gate(control, candidate, confirm)["status"] == "promote"
    weak_confirm = checkpoint(games=205, score=24.49, minutes=15)
    assert candidate_180_gate(control, candidate, weak_confirm)["status"] == "reject"
