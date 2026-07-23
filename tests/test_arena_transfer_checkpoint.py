from cgauto.arena_transfer_checkpoint import parse_game, summarize, target_player


def test_target_player_requires_agent_and_our_user() -> None:
    battle = {
        "players": [
            {"playerAgentId": 7, "userId": 1302251, "submissionId": 11},
            {"playerAgentId": 8, "userId": 22, "submissionId": 12},
        ]
    }
    assert target_player(battle, 7) == battle["players"][0]
    assert target_player(battle, 8) is None


def test_parse_game_extracts_margin_and_target_runtime_signal() -> None:
    game = {
        "gameId": 99,
        "agents": [
            {
                "agentId": 7,
                "index": 1,
                "valid": False,
                "codingamer": {"pseudo": "us"},
            },
            {
                "agentId": 8,
                "index": 0,
                "valid": True,
                "codingamer": {"pseudo": "them"},
            },
        ],
        "scores": [150, 25],
        "ranks": [0, 1],
        "metadata": {},
        "tooltips": [],
        "frames": [{"agentId": 1, "summary": "$1 exceeded the time limit"}],
    }
    row = parse_game(game, 7)
    assert row["opponent"] == "them"
    assert row["margin"] == -125
    assert row["rank"] == 1
    assert row["valid"] is False
    assert row["runtime_markers"] == ["exceeded", "time limit"]


def test_parse_game_does_not_charge_opponent_timeout_to_target() -> None:
    game = {
        "gameId": 100,
        "agents": [
            {"agentId": 7, "index": 0, "valid": True, "codingamer": {"pseudo": "us"}},
            {
                "agentId": 8,
                "index": 1,
                "valid": True,
                "codingamer": {"pseudo": "them"},
            },
        ],
        "scores": [114, -2],
        "ranks": [0, 1],
        "metadata": {},
        "tooltips": ['{"text":"$1 timeout!"}'],
        "frames": [{"agentId": 1, "summary": "$1 exceeded the time limit"}],
    }
    row = parse_game(game, 7)
    assert row["valid"] is True
    assert row["runtime_markers"] == []


def test_parse_game_uses_player_reference_not_frame_owner_for_timeout() -> None:
    game = {
        "gameId": 101,
        "agents": [
            {
                "agentId": 8,
                "index": 0,
                "valid": True,
                "codingamer": {"pseudo": "them"},
            },
            {"agentId": 7, "index": 1, "valid": True, "codingamer": {"pseudo": "us"}},
        ],
        "scores": [-2, 260],
        "ranks": [1, 0],
        "metadata": {},
        "tooltips": ['{"text":"$0 timeout!"}'],
        "frames": [
            {
                "agentId": 1,
                "stdout": "CHOP 1;WAIT",
                "summary": "$0: timeout\n$1: troll 1 damaged a tree",
            }
        ],
    }
    row = parse_game(game, 7)
    assert row["valid"] is True
    assert row["runtime_markers"] == []


def test_summarize_reports_protocol_safety_metrics() -> None:
    rows = [
        {"game_id": 1, "margin": 10, "valid": True, "runtime_markers": []},
        {"game_id": 2, "margin": -20, "valid": True, "runtime_markers": []},
        {"game_id": 3, "margin": -100, "valid": True, "runtime_markers": []},
    ]
    report = summarize(rows)
    assert report["games"] == 3
    assert report["wins"] == 1
    assert report["losses"] == 2
    assert report["catastrophic_losses"] == 1
    assert report["catastrophic_rate"] == 1 / 3
    assert report["negative_margin_mass"] == 120
    assert report["validity_runtime_signals"] == []
