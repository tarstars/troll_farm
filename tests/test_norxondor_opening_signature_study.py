from __future__ import annotations

from cgauto.norxondor_opening_signature_study import (
    cross_validated_safe_selector,
    signature,
    turn_band,
)
from cgauto.norxondor_portfolio_upper_bound import RESIDENT, THREE_WORKER


def sample(opponent: str, seed: int, turn: int, stats=(2, 2, 0, 2)) -> dict:
    return {
        "opponent": opponent,
        "seed": seed,
        "opponent_second_worker_turn": turn,
        "candidate_third_worker_turn": 50,
        "opponent_second_ms": stats[0],
        "opponent_second_cc": stats[1],
        "opponent_second_hp": stats[2],
        "opponent_second_chop": stats[3],
    }


def test_signature_requires_strictly_prior_observation() -> None:
    assert signature(sample("alt", 0, 50)) == ("unobserved",)
    assert signature(sample("alt", 0, -1)) == ("unobserved",)
    assert signature(sample("alt", 0, 15)) == ("05-15", 2, 2, 0, 2)
    assert turn_band(61) == "61+"


def test_safe_selector_defaults_ambiguous_signature_to_resident() -> None:
    rows = []
    for seed in range(10):
        rows.append(sample("safe", seed, 3, (2, 2, 0, 2)))
        rows.append(sample("bad", seed, 3, (1, 1, 1, 1)))
        rows.append(sample("ambiguous_alt", seed, 3, (1, 1, 1, 0)))
        rows.append(sample("ambiguous_bad", seed, 3, (1, 1, 1, 0)))
    labels = {
        "safe": THREE_WORKER,
        "bad": RESIDENT,
        "ambiguous_alt": THREE_WORKER,
        "ambiguous_bad": RESIDENT,
    }

    report = cross_validated_safe_selector(rows, labels, include_turn=True)

    assert report["selected_alternative"] == 10
    assert report["false_alternative"] == 0
    assert report["alternative_recall"] == 0.5
