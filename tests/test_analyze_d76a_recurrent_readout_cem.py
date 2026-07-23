"""Tests for D76 search and validation analysis helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from cgauto.analyze_d76a_recurrent_readout_cem import (
    anchor_summary,
    distribution,
    population_integrity,
)
from cgauto.run_d76a_recurrent_readout_cem import (
    READOUT_PARAMETERS,
    fixed_reservoir,
    write_population,
)


def test_distribution_reports_exact_rates_and_tail() -> None:
    report = distribution([-10, 0, 10, 20])
    assert report["mean"] == 5.0
    assert report["positive_rate"] == 0.5
    assert report["tie_rate"] == 0.25
    assert report["negative_rate"] == 0.25


def test_anchor_summary_detects_action_hash_change() -> None:
    base = {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        **{field: "0" for field in __import__(
            "cgauto.analyze_d76a_recurrent_readout_cem", fromlist=["ANCHOR_FIELDS"]
        ).ANCHOR_FIELDS},
    }
    initial = {**base, "policy": "initial"}
    balanced = {**base, "policy": "balanced"}
    assert anchor_summary([balanced, initial])["pass"]
    initial["action_hash"] = "1"
    assert not anchor_summary([balanced, initial])["pass"]


def test_population_integrity_uses_serialized_reservoir_bits(tmp_path: Path) -> None:
    reservoir = fixed_reservoir()
    readout = np.zeros(READOUT_PARAMETERS, dtype=np.float32)
    target = tmp_path / "population.tsv"
    write_population(target, reservoir, [("initial", readout)])
    assert population_integrity(target, [("initial", readout)], reservoir)["pass"]
