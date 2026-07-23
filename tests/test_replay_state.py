"""Tests for exact logical-state decoding from replay frame diffs."""

import json

from cgauto.replay_state import decode_replay, to_game_state


def test_decode_replay_applies_unit_carry_and_plant_updates(tmp_path) -> None:
    initial = {
        "global": {"inputmodule": "5 1\n0...1"},
        "frame": {
            "diff": "10 W 01001111;20 W 14011111;30 P 20042c8",
            "inputmodule": "1 2 3 4 0 0\n4 3 2 1 0 0",
        },
    }
    after = {
        "diff": "10 x2 51;30 h8 s5 c7;40 P 3101066",
        "inputmodule": "1 2 3 4 0 0\n4 3 2 1 0 0",
    }
    replay = {
        "gameId": 7,
        "scores": [10, 10],
        "ranks": [0, 1],
        "frames": [
            {"view": " 0\n" + json.dumps(initial), "keyframe": True},
            {"view": " 1\n", "keyframe": False},
            {"view": " 2\n" + json.dumps(after), "keyframe": True},
        ],
    }
    path = tmp_path / "7.json"
    path.write_text(json.dumps(replay))

    decoded = decode_replay(path)

    assert decoded["unknown_updates"] == []
    assert len(decoded["states"]) == 2
    assert decoded["states"][1]["units"][0]["carry"][5] == 1
    assert decoded["states"][1]["units"][0]["x"] == 2
    assert decoded["states"][1]["plants"][0]["health"] == 8
    assert decoded["states"][1]["plants"][0]["fruits"] == 1
    assert len(decoded["states"][1]["plants"]) == 2
    assert [plant["x"] for plant in decoded["states"][1]["plants"]] == [2, 3]

    game = to_game_state(decoded["map"], decoded["states"][1])
    assert game.turn == 2
    assert game.units[0].carry[5] == 1


def test_decode_replay_infers_implicit_plant_clock_updates(tmp_path) -> None:
    initial = {
        "global": {"inputmodule": "5 1\n0...1"},
        "frame": {
            "diff": "10 W 01001111;20 W 14011111;30 P 20041c2",
            "inputmodule": "0 0 0 0 0 0\n0 0 0 0 0 0",
        },
    }
    replay = {
        "gameId": 8,
        "scores": [0, 0],
        "ranks": [0, 1],
        "frames": [
            {"view": " 0\n" + json.dumps(initial), "keyframe": True},
            {
                "view": " 1\n"
                + json.dumps({"diff": "", "inputmodule": "0 0 0 0 0 0\n0 0 0 0 0 0"}),
                "keyframe": True,
            },
        ],
    }
    path = tmp_path / "8.json"
    path.write_text(json.dumps(replay))

    decoded = decode_replay(path)

    plant = decoded["states"][1]["plants"][0]
    assert plant["stage"] == 5
    assert plant["size"] == 4
    assert plant["fruits"] == 1
    assert plant["cooldown"] == 2


def test_decode_replay_infers_health_added_by_growth(tmp_path) -> None:
    initial = {
        "global": {"inputmodule": "5 1\n0...1"},
        "frame": {
            "diff": "10 W 01001111;20 W 14011111;30 P 20231b2",
            "inputmodule": "0 0 0 0 0 0\n0 0 0 0 0 0",
        },
    }
    replay = {
        "gameId": 9,
        "scores": [0, 0],
        "ranks": [0, 1],
        "frames": [
            {"view": " 0\n" + json.dumps(initial), "keyframe": True},
            {
                "view": " 1\n"
                + json.dumps({"diff": "", "inputmodule": "0 0 0 0 0 0\n0 0 0 0 0 0"}),
                "keyframe": True,
            },
        ],
    }
    path = tmp_path / "9.json"
    path.write_text(json.dumps(replay))

    plant = decode_replay(path)["states"][1]["plants"][0]

    assert plant["type"] == "APPLE"
    assert plant["size"] == 4
    assert plant["health"] == 14


def test_decode_replay_uses_chop_context_when_growth_cancels_damage(tmp_path) -> None:
    initial = {
        "global": {"inputmodule": "5 1\n0...1"},
        "frame": {
            "diff": "10 W 01001111;20 W 14011111;30 P 1032126",
            "inputmodule": "0 0 0 0 0 0\n0 0 0 0 0 0",
        },
    }
    replay = {
        "gameId": 10,
        "scores": [0, 0],
        "ranks": [0, 1],
        "frames": [
            {"view": " 0\n" + json.dumps(initial), "keyframe": True},
            {
                "view": " 1\n"
                + json.dumps(
                    {"diff": "", "inputmodule": "0 0 0 0 0 0\n0 0 0 0 0 0"}
                ),
                "keyframe": True,
            },
        ],
    }
    path = tmp_path / "10.json"
    path.write_text(json.dumps(replay))

    plant = decode_replay(path, chop_unit_ids_by_turn=[[0]])["states"][1]["plants"][0]

    assert plant["size"] == 3
    assert plant["health"] == 2
