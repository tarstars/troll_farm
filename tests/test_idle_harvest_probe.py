"""Tests for the mechanical idle-harvest diagnostic transform."""

from pathlib import Path

import pytest

from cgauto.make_idle_harvest_probe import instrument, instrument_minified

REPO = Path(__file__).resolve().parent.parent
LIVE = REPO / "rust" / "src" / "bin" / "yamo_orchard_live.rs"
LIVE_MIN = REPO / "cgauto" / "submissions" / "agent-6553250-yamo-orchard-live.min.rs"


def test_probe_instruments_each_distinct_decision_layer() -> None:
    probed = instrument(LIVE.read_text())

    assert probed.count("@IH_CAND") == 1
    assert probed.count("@IH_SELECT") == 1
    assert probed.count("@IH_ORCHARD_FORCE") == 1
    assert "YamoBot::tuned_carry_regeneration_transit_idle_harvest()" in probed


def test_probe_refuses_source_drift() -> None:
    with pytest.raises(RuntimeError, match="instrumentation anchor"):
        instrument("fn main() {}")


def test_minified_probe_stays_under_submission_size_and_keeps_live_policy() -> None:
    probed = instrument_minified(LIVE_MIN.read_text())

    assert len(probed.encode()) < 100_000
    assert probed.count("@IH_CAND") == 1
    assert probed.count("@IH_SELECT") == 1
    assert probed.count("@IH_ORCHARD_FORCE") == 1
    assert "YamoBot::tuned_carry_regeneration_transit_idle_harvest()" in probed
