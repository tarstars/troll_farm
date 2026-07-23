"""Tests for D65i planted-source lifecycle parsing and classification."""

from __future__ import annotations

from cgauto.analyze_d65i_source_survival import expected_source, parse_source_states


def test_parse_source_states_preserves_replacement_species() -> None:
    states = parse_source_states(
        "plum@6,2:1:plum:own:4:12:2:7;lemon@5,2:1:plum:own:1:6:0:3"
    )

    assert expected_source(states[("plum", 6, 2)], "plum")
    assert not expected_source(states[("lemon", 5, 2)], "lemon")
    assert states[("lemon", 5, 2)]["actual"] == "plum"


def test_parse_absent_source_is_not_expected_source() -> None:
    state = parse_source_states("lemon@5,2:0:none:none:-1:-1:-1:-1")

    assert not expected_source(state[("lemon", 5, 2)], "lemon")
