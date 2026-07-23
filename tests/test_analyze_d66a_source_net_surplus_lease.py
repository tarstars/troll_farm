"""Tests for D66a consumed lease analysis primitives."""

from __future__ import annotations

from cgauto.analyze_d66a_source_net_surplus_lease import paired, summary


def row(own: int, opponent: int, workers: int, drops: int = 0) -> dict[str, str]:
    result = {
        "own_score": str(own),
        "opponent_score": str(opponent),
        "margin": str(own - opponent),
        "own_workers": str(workers),
        "own_created_crops": "1",
        "activations": "1",
        "lease_failures": str(int(drops == 0)),
        "bootstrap_failures": "0",
        "duration_turns": "20",
    }
    for command in ("pick", "plant", "harvest", "drop", "wait"):
        result[f"{command}_commands"] = str(drops if command == "drop" else 1)
    return result


def test_paired_signs_are_candidate_minus_control() -> None:
    task = (9_830_002, 0, "resident")
    report = paired({task: row(30, 10, 2)}, {task: row(20, 15, 1)}, [task])

    assert report["mean_own_score_delta"] == 10
    assert report["mean_opponent_score_delta"] == -5
    assert report["mean_margin_delta"] == 15


def test_summary_counts_zero_drops_and_failures() -> None:
    report = summary([row(30, 10, 2, 1), row(20, 30, 1, 0)])

    assert report["worker_two_rate"] == 0.5
    assert report["commands"]["drop"] == 1
    assert report["lease_failures"] == 1
