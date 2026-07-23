from __future__ import annotations

from cgauto.norxondor_parallel_latency_study import analyze, percentile


def test_percentile_uses_nearest_rank() -> None:
    assert percentile([9, 1, 5, 3], 0.5) == 3
    assert percentile(list(range(1, 101)), 0.95) == 95


def test_latency_gate_uses_total_p95() -> None:
    rows = []
    for index, latency in enumerate([40_000, 45_000, 60_000]):
        rows.append(
            {
                "seed": index,
                "seat": 0,
                "actual_opponent": "model",
                "decision_turn": 3,
                "compatible_count": 1,
                "compatibility_us": 1_000,
                "parallel_rollout_us": latency - 1_000,
                "total_prediction_us": latency,
                "branch_elapsed_sum_us": latency * 2,
                "slowest_branch_us": latency - 2_000,
                "selected": 0,
            }
        )
    report = analyze(rows)
    assert report["latency_gate"]["within_budget"] == 2
    assert report["latency_gate"]["p95_us"] == 60_000
    assert not report["latency_gate"]["passed"]
