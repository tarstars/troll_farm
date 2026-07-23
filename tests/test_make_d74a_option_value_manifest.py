"""Tests for D74 outcome-blind state selection."""

from __future__ import annotations

import numpy as np

from cgauto.make_d74a_option_value_manifest import identity, select_rows


def test_select_rows_uses_hash_only_and_respects_quota() -> None:
    rows = []
    for ordinal in range(10):
        rows.append(
            {
                "partition": "discovery",
                "map_seed": 9_812_000 + ordinal,
                "task_index": ordinal,
                "seat": 0,
                "opponent_index": 0,
                "opponent": "resident",
                "decision_ordinal": ordinal,
                "turn": 50,
                "phase": "early",
                "legal_mask": "1111",
                "feature_hash": str(ordinal),
                "features": np.zeros(72, dtype=np.float32),
            }
        )
    selected = select_rows(rows)
    assert len(selected) == 6
    assert len({identity(row) for row in selected}) == 6
    assert [row["sample_id"] for row in selected] == list(range(6))
