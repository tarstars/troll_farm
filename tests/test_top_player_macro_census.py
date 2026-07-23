import json

from cgauto.top_player_macro_census import (
    role_of,
    successful_trains_from_replay,
    summarize_occurrences,
)


def test_roles_distinguish_wood_harvest_and_hybrid() -> None:
    assert role_of([2, 2, 0, 2]) == "wood_specialist"
    assert role_of([2, 2, 2, 2]) == "hybrid_chopper"
    assert role_of([2, 2, 2, 1]) == "harvest_specialist"


def test_successful_trains_are_new_units_after_initial_frame(tmp_path) -> None:
    initial = {
        "global": {"inputmodule": "5 1\n0...1"},
        "frame": {
            "diff": "10 W 01001111;20 W 14011111",
            "inputmodule": "0 0 0 0 0 0\n0 0 0 0 0 0",
        },
    }
    after = {"diff": "30 W 02102302", "inputmodule": ""}
    replay = {
        "frames": [
            {"view": " 0\n" + json.dumps(initial), "keyframe": True},
            {"view": " 1\n" + json.dumps(after), "keyframe": True},
        ]
    }
    path = tmp_path / "game.json"
    path.write_text(json.dumps(replay))

    result = successful_trains_from_replay(path)

    assert result[0] == [[1, [2, 3, 0, 2]]]
    assert result[1] == []


def test_summary_counts_final_worker_architecture() -> None:
    row = {
        "agent_id": 7,
        "turns": 100,
        "successful_trains": [[5, [2, 2, 0, 2]], [40, [2, 2, 2, 1]]],
        "successful_train_count": 2,
        "final_worker_count": 3,
        "command_counts": {"MOVE": 80},
        "planted_ok": {"BANANA": 4},
        "collected_wood": 10,
        "final_wood": 9,
        "score": 40,
        "margin": 5,
        "won": True,
    }

    result = summarize_occurrences([row])

    assert result["final_worker_count_distribution"] == {3: 1}
    assert result["successful_roles"] == {
        "wood_specialist": 1,
        "harvest_specialist": 1,
    }
    assert result["commands_per_100_turns"]["MOVE"] == 80
