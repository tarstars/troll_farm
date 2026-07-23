"""Tests for D77 lineage analysis helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from cgauto.analyze_d77a_full_recurrent_lineage_search import (
    distribution,
    population_integrity,
)
from cgauto.run_d77a_full_recurrent_lineage_search import (
    random_network,
    write_full_population,
)


def test_distribution_reports_rates() -> None:
    result = distribution([-1, 0, 2, 3])
    assert result["mean"] == 1.0
    assert result["positive_rate"] == 0.5
    assert result["tie_rate"] == 0.25


def test_population_integrity_round_trip(tmp_path: Path) -> None:
    vector = random_network(np.random.default_rng(7701), zero_readout=True)
    target = tmp_path / "population.tsv"
    write_full_population(target, [("zero", vector)])
    assert population_integrity(target, [("zero", vector)])["pass"]
