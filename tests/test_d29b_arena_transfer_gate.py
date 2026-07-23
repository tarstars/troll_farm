from datetime import datetime, timedelta, timezone

from cgauto.d29b_arena_transfer_gate import (
    checkpoint_120,
    early_gate,
    health_gate,
    terminal_gate,
)


BASE = datetime(2026, 7, 20, tzinfo=timezone.utc)


def checkpoint(
    *,
    games: int,
    score: float,
    minutes: int = 0,
    catastrophic_rate: float = 0.10,
    negative_mass: float | None = None,
    pending: int = 0,
    clean: bool = True,
) -> dict:
    return {
        "observed_at": (BASE + timedelta(minutes=minutes)).isoformat(),
        "matching_finished": games,
        "matching_pending": pending,
        "parsed_results": games,
        "identity_clean": clean,
        "unexpected_rows": [],
        "fetch_failures": [],
        "arena": {"score": score},
        "summary": {
            "catastrophic_rate": catastrophic_rate,
            "negative_margin_mass": (
                games * 10 if negative_mass is None else negative_mass
            ),
            "validity_runtime_signals": [],
        },
    }


def control() -> dict:
    rows = [{"margin": -100.0 if index % 10 == 0 else 10.0} for index in range(171)]
    result = checkpoint(games=171, score=23.05)
    result["rows"] = rows
    return result


def test_health_gate_is_identity_only_after_ten_games() -> None:
    assert health_gate(checkpoint(games=9, score=0))["status"] == "wait"
    assert health_gate(checkpoint(games=10, score=0))["status"] == "pass"
    assert health_gate(checkpoint(games=10, score=0, clean=False))["status"] == "reject"


def test_early_gate_rejects_only_frozen_floor_or_health() -> None:
    assert early_gate(checkpoint(games=60, score=21.55))["status"] == "reject"
    assert early_gate(checkpoint(games=60, score=21.56))["status"] == "continue"
    assert early_gate(checkpoint(games=59, score=30))["status"] == "wait"


def test_120_gate_provisional_and_tail_rejection() -> None:
    good = checkpoint(games=120, score=23.85, catastrophic_rate=0.11)
    assert checkpoint_120(control(), good)["status"] == "provisional-continue"
    weak = checkpoint(games=120, score=22.54)
    assert checkpoint_120(control(), weak)["status"] == "reject"
    bad_tail = checkpoint(games=120, score=25, catastrophic_rate=0.121)
    assert checkpoint_120(control(), bad_tail)["status"] == "reject"


def test_terminal_requires_zero_pending_and_delayed_confirmation() -> None:
    candidate = checkpoint(games=160, score=23.60, catastrophic_rate=0.11)
    assert terminal_gate(control(), candidate)["status"] == "wait"
    too_early = checkpoint(
        games=160, score=23.60, minutes=14, catastrophic_rate=0.11
    )
    assert terminal_gate(control(), candidate, too_early)["status"] == "wait"
    confirmed = checkpoint(
        games=160, score=23.60, minutes=15, catastrophic_rate=0.11
    )
    assert terminal_gate(control(), candidate, confirmed)["status"] == "promote"
    pending = checkpoint(
        games=160, score=23.60, minutes=15, catastrophic_rate=0.11, pending=1
    )
    assert terminal_gate(control(), candidate, pending)["status"] == "reject"


def test_terminal_rejects_rating_or_negative_tail_mass() -> None:
    low = checkpoint(games=160, score=23.54)
    assert terminal_gate(control(), low)["status"] == "reject"
    bad_mass = checkpoint(games=160, score=25, negative_mass=1900)
    assert terminal_gate(control(), bad_mass)["status"] == "reject"
