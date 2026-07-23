"""Tests for D78b referee-confirmed CHOP attribution."""

from cgauto.analyze_d78b_opponent_commitment import referee_chop_events


def test_referee_chop_events_include_damage_and_fell_wood() -> None:
    frames = [
        {},
        {
            "keyframe": True,
            "view": "{x}",
            "summary": (
                "$0: troll 2 damaged a tree\n"
                "$1: troll 7 collected 3 WOOD\n"
                "$1: troll 8 collected 1 IRON\n"
            ),
        },
        {
            "keyframe": True,
            "view": "{y}",
            "summary": "$0: [failed] troll 2 damaged a tree\n$0: troll 3 damaged a tree\n",
        },
    ]
    assert referee_chop_events(frames) == [(1, 0, 2), (1, 1, 7), (2, 0, 3)]
