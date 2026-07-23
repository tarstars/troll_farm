from __future__ import annotations

import pytest

from cgauto.arena_rollout_forensics import (
    PROBE_EXPRESSION,
    SELECT_EXPRESSION,
    instrument_source,
    manifest_records,
    outcome_summary,
    selection_marker,
)


def test_instrument_source_changes_only_unique_selector_expression() -> None:
    source = f"before{SELECT_EXPRESSION}after"
    assert instrument_source(source) == f"before{PROBE_EXPRESSION}after"
    with pytest.raises(ValueError):
        instrument_source("no selector")
    with pytest.raises(ValueError):
        instrument_source(SELECT_EXPRESSION * 2)


def test_selection_marker_requires_exactly_one_marker() -> None:
    assert selection_marker("ROLLOUT_OPTION\n") == "option"
    assert selection_marker("ROLLOUT_CONTROL\n") == "control"
    assert selection_marker("") == "unknown"
    assert selection_marker("ROLLOUT_OPTION ROLLOUT_CONTROL") == "unknown"


def test_manifest_records_preserves_windows_and_rejects_duplicates() -> None:
    manifest = {
        "windows": [
            {"name": "first", "game_ids": [3, 2]},
            {"name": "second", "game_ids": [1]},
        ]
    }
    assert manifest_records(manifest) == [(3, "first"), (2, "first"), (1, "second")]
    manifest["windows"][1]["game_ids"] = [2]
    with pytest.raises(ValueError):
        manifest_records(manifest)


def test_outcome_summary_handles_empty_and_observed_rows() -> None:
    assert outcome_summary([]) == {
        "games": 0,
        "wins": 0,
        "mean_margin": None,
        "median_margin": None,
    }
    assert outcome_summary(
        [
            {"won": True, "margin": 10},
            {"won": False, "margin": -4},
        ]
    ) == {
        "games": 2,
        "wins": 1,
        "mean_margin": 3,
        "median_margin": 3.0,
        "minimum_margin": -4,
        "maximum_margin": 10,
    }
