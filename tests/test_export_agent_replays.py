import gzip
import json
from pathlib import Path

from cgauto.export_agent_replays import export_corpus


def fixture(raw_root: Path, battle_list: Path) -> None:
    battle_list.write_text(
        json.dumps(
            [
                {
                    "done": True,
                    "gameId": 7,
                    "players": [
                        {
                            "playerAgentId": 11,
                            "submissionId": 22,
                            "position": 0,
                            "nickname": "Private Name",
                            "userId": 88,
                            "avatar": 99,
                            "publicHandle": "secret-handle",
                            "testSessionHandle": "secret-session",
                        },
                        {
                            "playerAgentId": 33,
                            "submissionId": 44,
                            "position": 1,
                            "nickname": "Opponent Name",
                        },
                    ],
                }
            ]
        )
    )
    raw_root.mkdir()
    (raw_root / "7.json").write_text(
        json.dumps(
            {
                "gameId": 7,
                "agents": [
                    {
                        "index": 0,
                        "agentId": 11,
                        "score": 1.5,
                        "valid": True,
                        "codingamer": {
                            "userId": 88,
                            "pseudo": "Private Name",
                            "avatar": 99,
                        },
                    },
                    {
                        "index": 1,
                        "agentId": 33,
                        "score": 2.5,
                        "valid": True,
                        "codingamer": {"userId": 77, "pseudo": "Opponent Name"},
                    },
                ],
                "scores": [1, 2],
                "ranks": [1, 0],
                "refereeInput": "seed=1\n",
                "tooltips": [],
                "frames": [{"agentId": 0, "stdout": "WAIT"}],
                "metadata": {"private": "do not copy"},
            }
        )
    )


def test_export_is_sanitized_and_deterministic(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw"
    battle_list = tmp_path / "battles.json"
    fixture(raw_root, battle_list)
    first = tmp_path / "first"
    second = tmp_path / "second"
    args = dict(
        agent_id=11,
        submission_id=22,
        battle_list=battle_list,
        raw_root=raw_root,
        observed_at_utc="2026-08-03T18:00:00Z",
    )
    manifest = export_corpus(output_dir=first, **args)
    export_corpus(output_dir=second, **args)

    package = first / manifest["package"]
    replay = json.loads(gzip.decompress(package.read_bytes()).decode())
    index = json.loads((first / manifest["battle_index"]).read_text())
    rendered = package.read_bytes() + (first / manifest["battle_index"]).read_bytes()

    assert [agent["codingamer"]["pseudo"] for agent in replay["agents"]] == [
        "PLAYER_0",
        "PLAYER_1",
    ]
    assert [player["pseudo"] for player in index[0]["players"]] == ["PLAYER_0", "PLAYER_1"]
    assert b"Private Name" not in rendered
    assert b"Opponent Name" not in rendered
    assert b"secret-handle" not in rendered
    assert b"secret-session" not in rendered
    assert "metadata" not in replay
    assert package.read_bytes() == (second / manifest["package"]).read_bytes()
    assert (first / manifest["battle_index"]).read_bytes() == (
        second / manifest["battle_index"]
    ).read_bytes()
