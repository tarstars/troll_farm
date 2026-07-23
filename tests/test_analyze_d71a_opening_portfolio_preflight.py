"""Tests for D71a mechanics-only analysis helpers."""

from __future__ import annotations

from pathlib import Path

from cgauto.analyze_d71a_opening_portfolio_preflight import (
    parse_elapsed,
    parse_timing,
    validate_anchor,
)


def test_parse_elapsed_supports_minute_and_hour_formats() -> None:
    assert parse_elapsed("1:15.42") == 75.42
    assert parse_elapsed("1:02:03") == 3723
    assert parse_elapsed("9.5") == 9.5


def test_parse_host_timing_computes_effective_cores(tmp_path: Path) -> None:
    path = tmp_path / "time.txt"
    path.write_text(
        """User time (seconds): 120.0
System time (seconds): 1.0
Percent of CPU this job got: 1210%
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:10.00
Maximum resident set size (kbytes): 1234
"""
    )
    report = parse_timing(path)
    assert report["elapsed_seconds"] == 10
    assert report["effective_cpu_cores"] == 12.1
    assert report["reported_cpu_percent"] == 1210


def test_anchor_requires_exact_terminal_and_hash_fields() -> None:
    reference = []
    actual = []
    for seat in (0, 1):
        for opponent in (
            "resident",
            "gold_adaptive",
            "compact_gold",
            "norx_native_three",
            "legend_balanced",
            "mybot",
            "script_boss",
            "silver_boss",
        ):
            shared = {
                "map_seed": "9801000",
                "seat": str(seat),
                "opponent": opponent,
                "turn": "301",
                "own_score": "10",
                "opponent_score": "9",
                "own_workers": "3",
                "opponent_workers": "2",
                "successful_trains": "2",
                "own_created_crops": "4",
                "opponent_created_crops": "3",
                "ambiguous_created_crops": "0",
                "action_hash": "1",
                "state_hash": "2",
            }
            reference.append(
                {**shared, "policy": "d62_zero_linear_balanced_reference"}
            )
            actual.append(dict(shared))
    assert validate_anchor(actual, reference)["pass"]
    actual[0]["state_hash"] = "3"
    assert not validate_anchor(actual, reference)["pass"]
