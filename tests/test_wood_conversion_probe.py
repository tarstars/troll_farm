"""Tests for the exact-source wood-conversion telemetry transform."""

from pathlib import Path

import pytest

from cgauto.make_wood_conversion_probe import instrument_minified

REPO = Path(__file__).resolve().parent.parent
LIVE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"


def test_probe_instruments_state_selection_and_outer_override() -> None:
    result = instrument_minified(LIVE.read_text())

    assert result.count("@WC_STATE") == 1
    assert result.count("@WC_SELECT") == 1
    assert result.count("@WC_OVERRIDE") == 1
    assert len(result.encode()) < 100_000


def test_probe_refuses_source_drift() -> None:
    with pytest.raises(RuntimeError, match="wood-probe anchor"):
        instrument_minified("fn main() {}")
