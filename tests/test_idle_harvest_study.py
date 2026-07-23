"""Pure tests for the causal idle-harvest study harness."""

from cgauto.idle_harvest_study import (
    action_commands,
    fixed_fixture,
    grid_text,
    parse_probe_events,
    turn_text,
)


def test_parse_probe_events_keeps_inner_and_outer_layers_distinct() -> None:
    events = parse_probe_events(
        "noise\n"
        "@IH_CAND t=280 unit=0 commands=HARVEST 0|MOVE 0 3 2\n"
        "@IH_SELECT t=280 unit=0 command=HARVEST 0\n"
        "@IH_ORCHARD_FORCE t=290 unit=0 command=HARVEST 0\n"
    )

    assert [event["kind"] for event in events] == ["cand", "select", "orchard_force"]
    assert [event["turn"] for event in events] == [280, 280, 290]


def test_action_commands_ignores_announcement_only_drift() -> None:
    assert action_commands("MSG one;MOVE 0 2 2;WAIT") == ["MOVE 0 2 2", "WAIT"]
    assert action_commands("MSG two;MOVE 0 2 2;WAIT") == ["MOVE 0 2 2", "WAIT"]


def test_fixture_serializes_relative_seats() -> None:
    game = fixed_fixture()

    seat0 = grid_text(game, 0)
    seat1 = grid_text(game, 1)
    assert ".0...1." in seat0
    assert ".1...0." in seat1
    assert "0 0 3 2 1 1 1 1" in turn_text(game, 0)
    assert "0 1 3 2 1 1 1 1" in turn_text(game, 1)
