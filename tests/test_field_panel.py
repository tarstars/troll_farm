"""Pure tests for the controlled field-panel orchestrator."""

import pytest

from cgauto.field_panel import (
    build_play_body,
    build_jobs,
    build_seeded_jobs,
    command_metrics,
    final_inventory,
    input_unit_counts,
    result_row,
    PanelStop,
    stdout_stream,
    stream_sha256,
    trace_evidence,
    validate_play_result,
    validate_seed_blocks,
    workforce_metrics,
)


def test_build_play_body_preserves_exact_game_options() -> None:
    assert build_play_body("source", 42, "seed=-7\n") == {
        "code": "source",
        "programmingLanguageId": "Rust",
        "multi": {"agentsIds": [-1, 42], "gameOptions": "seed=-7\n"},
    }


def test_validate_play_result_requires_exact_seed_echo() -> None:
    validate_play_result({"scores": [1, 0], "refereeInput": "seed=-7\n"}, "seed=-7\n")

    with pytest.raises(PanelStop, match="echo mismatch"):
        validate_play_result(
            {"scores": [1, 0], "refereeInput": "seed=-8\n"}, "seed=-7\n"
        )


def test_build_jobs_alternates_baseline_and_candidate() -> None:
    jobs = build_jobs({"one": 10, "two": 20}, games_per_cell=1)

    assert [(job["opponent"], job["bot"]) for job in jobs] == [
        ("one", "baseline"),
        ("one", "candidate"),
        ("two", "baseline"),
        ("two", "candidate"),
    ]


def test_validate_seed_blocks_and_build_seeded_jobs() -> None:
    blocks = validate_seed_blocks(
        {
            "blocks": [
                {
                    "opponent": "delineate",
                    "opponent_agent": 6479768,
                    "seed": -7,
                },
                {"opponent": "wala", "opponent_agent": 6481141, "seed": 8},
            ]
        }
    )

    jobs = build_seeded_jobs(blocks)
    assert [(job["opponent"], job["seed"], job["bot"]) for job in jobs] == [
        ("delineate", -7, "baseline"),
        ("delineate", -7, "candidate"),
        ("wala", 8, "baseline"),
        ("wala", 8, "candidate"),
    ]


def test_final_inventory_uses_last_keyframe_inventory() -> None:
    frames = [
        {"view": 'x {"inputmodule":"1 2 3 4 5 6\\n6 5 4 3 2 1"}'},
        {"view": 'x {"inputmodule":"2 3 4 5 6 7\\n7 6 5 4 3 2"}'},
    ]

    assert final_inventory(frames, 0) == [2, 3, 4, 5, 6, 7]
    assert final_inventory(frames, 1) == [7, 6, 5, 4, 3, 2]


def test_result_row_is_candidate_neutral() -> None:
    job = {"bot": "candidate", "opponent": "one", "opponent_agent": 10, "repetition": 0}
    result = {
        "gameId": 123,
        "refereeInput": "seed=-7\n",
        "scores": [30, 20],
        "frames": [
            {"keyframe": True, "view": "initial"},
            {
                "agentId": 0,
                "stdout": "MSG candidate;HARVEST 0",
                "keyframe": True,
                "view": 'x {"inputmodule":"1 1 0 0 0 7\\n0 0 0 0 0 5"}',
            },
        ],
    }

    row = result_row(job, result)

    assert row["win"] is True
    assert row["referee_input"] == "seed=-7\n"
    assert row["wood"] == [7, 5]
    assert row["fruit"] == [2, 0]
    assert row["turns"] == 1
    assert row["commands"]["harvest_turns"] == [1]


def test_command_metrics_tracks_turns_and_announcement() -> None:
    frames = [
        {"keyframe": True},
        {"agentId": 0, "stdout": "MSG baseline;MOVE 0 1 1"},
        {"agentId": 1, "stdout": "WAIT", "keyframe": True},
        {"agentId": 0, "stdout": "HARVEST 0", "keyframe": True},
    ]

    metrics = command_metrics(frames)

    assert metrics["counts"] == {"MSG": 1, "MOVE": 1, "HARVEST": 1}
    assert metrics["harvest_turns"] == [2]
    assert metrics["train_attempts"] == []
    assert metrics["announcements"] == ["baseline"]


def test_trace_evidence_preserves_stdout_and_agent_identity() -> None:
    result = {
        "frames": [
            {"agentId": 0, "stdout": "MSG x;MOVE 0 1 1\n"},
            {"agentId": 1, "stdout": "WAIT\n"},
            {"agentId": 0, "stdout": "HARVEST 0\n"},
        ],
        "agents": [
            {"index": 0, "agentId": -1},
            {
                "index": 1,
                "agentId": 42,
                "codingamer": {"userId": 7, "pseudo": "opponent"},
            },
        ],
    }

    player_zero = ["MSG x;MOVE 0 1 1\n", "HARVEST 0\n"]
    evidence = trace_evidence(result)

    assert stdout_stream(result["frames"], 0) == player_zero
    assert evidence["stdout"][0] == {
        "frames": 2,
        "sha256": stream_sha256(player_zero),
        "stream": player_zero,
    }
    assert evidence["agents"][1] == {
        "index": 1,
        "agent_id": 42,
        "user_id": 7,
        "pseudo": "opponent",
    }
    assert evidence["turn_one"] is None
    assert evidence["turn_one_error"].startswith("KeyError:")


def test_workforce_metrics_decode_inputmodule_units() -> None:
    frames = [
        {
            "view": 'x {"inputmodule":"0 0 0 0 0 0\\n0 0 0 0 0 0\\n0\\n2'
            '\\n0 0 1 1 1 1 1 1 0 0 0 0 0 0'
            '\\n1 1 8 8 1 1 1 1 0 0 0 0 0 0"}'
        },
        {
            "view": 'x {"inputmodule":"0 0 0 0 0 0\\n0 0 0 0 0 0\\n1'
            '\\nPLUM 2 2 1 6 0 0\\n4'
            '\\n0 0 1 1 1 1 1 1 0 0 0 0 0 0'
            '\\n2 0 1 2 2 2 1 1 0 0 0 0 0 0'
            '\\n3 0 1 3 2 3 1 2 0 0 0 0 0 0'
            '\\n1 1 8 8 1 1 1 1 0 0 0 0 0 0"}'
        },
    ]

    assert input_unit_counts(frames[0]) == [1, 1]
    assert workforce_metrics(frames) == {
        "source": "inputmodule",
        "snapshots": 2,
        "training_events": [0, 0],
        "training_turns": [[], []],
        "max": [3, 1],
        "final": [3, 1],
    }


def test_workforce_metrics_fall_back_to_successful_train_summaries() -> None:
    frames = [
        {"keyframe": True},
        {"keyframe": True, "summary": "$0: trained a troll\n$1: trained a troll\n"},
        {"keyframe": True, "summary": "$0: [failed] not enough resources\n"},
        {"keyframe": True, "summary": "$0: trained a troll\n"},
    ]

    assert workforce_metrics(frames) == {
        "source": "referee_summary",
        "snapshots": 0,
        "training_events": [2, 1],
        "training_turns": [[1, 3], [1]],
        "max": [3, 2],
        "final": [3, 2],
    }
