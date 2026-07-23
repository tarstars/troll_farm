"""Tests for D65a source-repair analysis primitives."""

from __future__ import annotations

from cgauto.analyze_d65a_missing_currency_seed_source import paired_delta, summarize


def row(own: int, opponent: int, workers: int, activations: int = 0) -> dict[str, str]:
    return {
        "own_score": str(own),
        "opponent_score": str(opponent),
        "margin": str(own - opponent),
        "own_workers": str(workers),
        "own_created_crops": "1",
        "activations": str(activations),
        "activation_plum": str(activations),
        "activation_lemon": "0",
        "activation_apple": "0",
        "activation_banana": "0",
    }


def test_paired_delta_keeps_score_signs() -> None:
    key = (9_830_002, 0, "resident")
    repair = {key: row(40, 10, 2)}
    control = {key: row(20, 15, 1)}

    report = paired_delta(repair, control, [key])

    assert report["mean_own_score_delta"] == 20
    assert report["mean_opponent_score_delta"] == -5
    assert report["mean_margin_delta"] == 25
    assert report["strict_margin_improvements"] == 1


def test_summary_counts_worker_two_and_species_activations() -> None:
    report = summarize([row(20, 15, 1, 0), row(30, 10, 2, 2)])

    assert report["tasks"] == 2
    assert report["worker_two_rate"] == 0.5
    assert report["activations"] == 2
    assert report["activation_species"]["plum"] == 2
