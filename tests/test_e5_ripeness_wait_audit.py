from __future__ import annotations

import pytest

from cgauto.e5_ripeness_wait_audit import (
    adjudicate,
    ALTERNATE_FROM,
    ALTERNATE_TO,
    alternate_source,
    commands_by_unit,
    event_episode_summary,
    first_divergence,
    LIVE_SHA256,
    LIVE_SOURCE,
    mechanism_summary,
    OPPONENT_NAMES,
    parse_probe_events,
    PROBE_FROM,
    PROBE_TO,
    probe_source,
    sha256_path,
)


def test_exact_live_transforms_are_unique_and_reversible():
    source = LIVE_SOURCE.read_bytes()
    assert sha256_path(LIVE_SOURCE) == LIVE_SHA256
    assert source.count(ALTERNATE_FROM.encode()) == 1
    assert source.count(ALTERNATE_TO.encode()) == 0
    assert source.count(PROBE_FROM.encode()) == 1
    assert source.count(PROBE_TO.encode()) == 0

    alternate = alternate_source(source)
    probe = probe_source(source)

    assert alternate.count(ALTERNATE_TO.encode()) == 1
    assert alternate.replace(ALTERNATE_TO.encode(), ALTERNATE_FROM.encode(), 1) == source
    assert probe.count(PROBE_TO.encode()) == 1
    assert probe.replace(PROBE_TO.encode(), PROBE_FROM.encode(), 1) == source


def test_probe_event_parser_is_exact():
    event = parse_probe_events(
        "@E5_WAIT t=17 unit=2 cell=3,4 item=1 size=4 cooldown=2 target=3,4\n"
    )
    assert event == [
        {
            "turn": 17,
            "unit": 2,
            "cell": [3, 4],
            "item": 1,
            "size": 4,
            "cooldown": 2,
            "target": [3, 4],
        }
    ]
    with pytest.raises(RuntimeError, match="unexpected diagnostic stderr"):
        parse_probe_events("unclassified\n")


def test_commands_by_unit_skips_train_but_preserves_slots():
    assert commands_by_unit(
        ["TRAIN 1 2 0 3", "WAIT", "MOVE 9 4 5"], [3, 9]
    ) == {3: "WAIT", 9: "MOVE 9 4 5"}
    with pytest.raises(ValueError, match="more unit commands"):
        commands_by_unit(["WAIT", "WAIT"], [3])


def _match(policy_commands, opponent_commands, events):
    return {
        "policy_trace": [
            {
                "turn": turn,
                "commands": commands,
                "by_unit": {1: commands[0]},
            }
            for turn, commands in enumerate(policy_commands, 1)
        ],
        "opponent_trace": [
            {
                "turn": turn,
                "commands": commands,
                "by_unit": {2: commands[0]},
            }
            for turn, commands in enumerate(opponent_commands, 1)
        ],
        "events": events,
    }


def test_first_divergence_requires_matching_wait_event():
    control = _match(
        [["MOVE 1 2 2"], ["WAIT"]],
        [["WAIT"], ["MOVE 2 3 3"]],
        [
            {
                "turn": 2,
                "unit": 1,
                "cell": [4, 5],
                "item": 2,
                "size": 4,
                "cooldown": 1,
                "target": [4, 5],
            }
        ],
    )
    alternate = _match(
        [["MOVE 1 2 2"], ["MOVE 1 6 6"]],
        [["WAIT"], ["MOVE 2 3 3"]],
        [],
    )

    result = first_divergence(control, alternate)

    assert result["turn"] == 2
    assert result["common_prefix_turns"] == 1
    assert result["explanations"][0]["alternate_command"] == "MOVE 1 6 6"

    control["events"] = []
    with pytest.raises(RuntimeError, match="lacks an E5 wait explanation"):
        first_divergence(control, alternate)


def test_first_divergence_rejects_opponent_leading_policy():
    control = _match([["WAIT"]], [["WAIT"]], [])
    alternate = _match([["WAIT"]], [["MOVE 2 1 1"]], [])
    with pytest.raises(RuntimeError, match="opponent diverged before"):
        first_divergence(control, alternate)


def test_event_episode_summary_groups_consecutive_turns():
    rows = [
        {
            "diagnostic_events": [
                {"seat": 0, "unit": 1, "turn": 2, "item": 0},
                {"seat": 0, "unit": 1, "turn": 3, "item": 0},
                {"seat": 0, "unit": 1, "turn": 5, "item": 1},
                {"seat": 1, "unit": 8, "turn": 90, "item": 2},
            ]
        }
    ]
    summary = event_episode_summary(rows)
    assert summary["events"] == 4
    assert summary["episodes"] == 3
    assert summary["episode_length_maximum"] == 2
    assert summary["events_by_phase"] == {"later": 1, "opening": 3}


def test_mechanism_gate_requires_cell_seat_and_family_breadth():
    rows = []
    for index in range(24):
        rows.append(
            {
                "seed": index,
                "opponent": OPPONENT_NAMES[index % 4],
                "activated": index < 20,
                "seat_activated": [
                    index < 20 and index % 2 == 0,
                    index < 20 and index % 2 == 1,
                ],
            }
        )
    result = mechanism_summary(rows)
    assert result["status"] == "ACTIVE_WAIT"
    assert result["activated_cell_count"] == 20
    assert result["seat_game_counts"] == [10, 10]
    assert result["active_family_count"] == 4


def test_adjudication_precedence_and_material_gate():
    positive = {name: 1.0 for name in OPPONENT_NAMES}
    one_bad = dict(positive)
    one_bad["motion"] = -1.01
    assert adjudicate("WAIT_INERT", 2, [1, 1], positive)[0] == "WAIT_INERT"
    assert (
        adjudicate("ACTIVE_WAIT", 0, [1, 1], positive)[0]
        == "KEEP_RIPENESS_WAIT"
    )
    assert (
        adjudicate("ACTIVE_WAIT", 2, [-0.1, 1], positive)[0]
        == "KEEP_RIPENESS_WAIT"
    )
    assert (
        adjudicate("ACTIVE_WAIT", 2, [1, 1], one_bad)[0]
        == "KEEP_RIPENESS_WAIT"
    )
    assert (
        adjudicate("ACTIVE_WAIT", 0.99, [1, 1], positive)[0]
        == "WAIT_RESIDUAL_NONMATERIAL"
    )
    assert (
        adjudicate("ACTIVE_WAIT", 1, [0, 1], positive)[0]
        == "WAIT_RESIDUAL_MATERIAL_LOCAL"
    )
