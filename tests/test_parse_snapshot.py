"""Tests for snapshot-scoped D61p parsing, QA, and confirmation sealing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from data.scripts.parse_snapshot import (
    bucket_label,
    parse_snapshot,
    sha256_bytes,
    split_bucket,
)
from data.scripts.collect_snapshot import ApiResponse, collect_snapshot


RESIDENT = 6_561_795


def replay(game_id: int, opponent: int, tag: str) -> dict:
    initial_inventory = "1 1 1 1 1 0\n1 1 1 1 1 0"
    initial = {
        "global": {"inputmodule": "4 1\n0..1"},
        "frame": {
            "inputmodule": initial_inventory,
            "diff": ";".join(
                (
                    "0 W 00001111",
                    "1 W 13011111",
                    "2 P 1001128",
                    "3 P 2001128",
                )
            ),
        },
    }
    resolved = {"inputmodule": initial_inventory, "diff": ""}
    return {
        "gameId": game_id,
        "agents": [
            {
                "index": 0,
                "agentId": RESIDENT,
                "codingamer": {"userId": 1, "pseudo": "resident"},
            },
            {
                "index": 1,
                "agentId": opponent,
                "codingamer": {"userId": 2, "pseudo": f"opponent-{opponent}"},
            },
        ],
        "scores": [4, 4],
        "ranks": [0, 0],
        "frames": [
            {"view": " 0\n" + json.dumps(initial)},
            {"agentId": 0, "stdout": f"WAIT;MSG {tag}"},
            {
                "agentId": 1,
                "stdout": "WAIT",
                "keyframe": True,
                "view": " 1\n" + json.dumps(resolved),
            },
        ],
    }


def matching_pair(label: str, *, start: int) -> tuple[int, int]:
    for opponent in range(start, start + 10_000):
        if bucket_label(split_bucket("d61p-opponent:", opponent)) != label:
            continue
        for game_id in range(start * 10, start * 10 + 10_000):
            if bucket_label(split_bucket("d61p-resident:", game_id)) == label:
                return game_id, opponent
    raise AssertionError(f"no deterministic split pair for {label}")


def write_snapshot(
    tmp_path: Path,
    games: list[tuple[dict, str]],
    *,
    snapshot_id: str = "test-d61p",
) -> Path:
    raw = tmp_path / "raw"
    snapshot = raw / "snapshots" / snapshot_id
    cache = raw / "games"
    snapshot.mkdir(parents=True)
    cache.mkdir(parents=True)
    leaderboard = {
        "users": [
            {
                "agentId": RESIDENT,
                "codingamer": {"userId": 1},
                "league": {"divisionIndex": 5},
                "rank": 1,
                "localRank": 1,
                "score": 20.0,
            },
            {
                "agentId": games[0][0]["agents"][1]["agentId"],
                "codingamer": {"userId": 2},
                "league": {"divisionIndex": 5},
                "rank": 2,
                "localRank": 2,
                "score": 19.0,
            },
        ]
    }
    leaderboard_raw = json.dumps(leaderboard, separators=(",", ":")).encode()
    (snapshot / "leaderboard.json").write_bytes(leaderboard_raw)
    records = []
    for body, status in games:
        game_id = int(body["gameId"])
        raw_body = json.dumps(body, separators=(",", ":")).encode()
        (cache / f"{game_id}.json").write_bytes(raw_body)
        records.append(
            {
                "game_id": game_id,
                "status": status,
                "response_sha256": sha256_bytes(raw_body),
                "cache_file": f"games/{game_id}.json",
                "boss_visible": False,
                "sources": [
                    {
                        "agent_id": body["agents"][1]["agentId"],
                        "source_rank": 2,
                        "groups": ["legend_top20"],
                    }
                ],
            }
        )
    games_raw = (json.dumps(records, indent=2, sort_keys=True) + "\n").encode()
    (snapshot / "games.json").write_bytes(games_raw)
    manifest = {
        "schema": "troll-farm-d61p-snapshot-v1",
        "snapshot_id": snapshot_id,
        "complete": True,
        "all_wanted_games_classified": True,
        "config": {"resident_agent_id": RESIDENT},
        "files": {
            "leaderboard.json": {
                "bytes": len(leaderboard_raw),
                "sha256": sha256_bytes(leaderboard_raw),
            },
            "games.json": {
                "bytes": len(games_raw),
                "sha256": sha256_bytes(games_raw),
            },
        },
    }
    (snapshot / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return snapshot


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def test_parse_snapshot_seals_confirmation_and_preserves_open_products(
    tmp_path: Path,
) -> None:
    discovery_id, discovery_opponent = matching_pair("discovery", start=100)
    confirmation_id, confirmation_opponent = matching_pair("confirmation", start=200)
    snapshot = write_snapshot(
        tmp_path,
        [
            (replay(discovery_id, discovery_opponent, "open"), "fetched"),
            (replay(confirmation_id, confirmation_opponent, "sealed"), "already_present"),
        ],
    )
    base_processed = tmp_path / "raw" / "processed"
    base_processed.mkdir()
    (base_processed / "sentinel").write_text("untouched")

    processed = parse_snapshot(snapshot)

    assert (base_processed / "sentinel").read_text() == "untouched"
    open_games = read_jsonl(processed / "open" / "games.jsonl")
    sealed_games = read_jsonl(processed / "sealed_confirmation" / "games.jsonl")
    assert [game["gameId"] for game in open_games] == [discovery_id]
    assert [game["gameId"] for game in sealed_games] == [confirmation_id]
    assert (processed / "open" / "trajectories" / f"{discovery_id}.jsonl").exists()
    assert not (processed / "open" / "trajectories" / f"{confirmation_id}.jsonl").exists()
    assert (
        processed
        / "sealed_confirmation"
        / "trajectories"
        / f"{confirmation_id}.jsonl"
    ).exists()

    qa = json.loads((processed / "qa.json").read_text())
    assert qa["counts"]["parsed_games"] == 2
    assert qa["counts"]["sealed_confirmation_games"] == 1
    assert not qa["pass"]  # synthetic snapshot intentionally misses frozen volume gates
    assert all(
        value
        for name, value in qa["gates"].items()
        if name
        not in {
            "at_least_80_resident_games",
            "at_least_15_top20_source_agents",
            "at_least_75_top20_games",
        }
    )
    confirmation_qa = next(
        row for row in qa["rows"] if row["game_id"] == confirmation_id
    )
    assert confirmation_qa == {
        "game_id": confirmation_id,
        "split": "confirmation",
        "integrity_pass": True,
    }
    split_manifest = json.loads((processed / "split_manifest.json").read_text())
    assert all("scores" not in row for row in split_manifest["rows"])
    assert (processed / "manifest.json").exists()

    with pytest.raises(FileExistsError):
        parse_snapshot(snapshot)


def test_tampered_cache_is_a_qa_failure_not_silently_parsed(tmp_path: Path) -> None:
    game_id, opponent = matching_pair("discovery", start=300)
    snapshot = write_snapshot(tmp_path, [(replay(game_id, opponent, "original"), "fetched")])
    cache = tmp_path / "raw" / "games" / f"{game_id}.json"
    cache.write_text(cache.read_text() + " ")

    processed = parse_snapshot(snapshot)

    qa = json.loads((processed / "qa.json").read_text())
    assert qa["counts"]["parsed_games"] == 0
    assert qa["counts"]["parse_failures"] == 1
    assert not qa["gates"]["all_eligible_games_parsed"]
    assert read_jsonl(processed / "open" / "games.jsonl") == []


def test_tampered_snapshot_metadata_aborts_before_processed_output(tmp_path: Path) -> None:
    game_id, opponent = matching_pair("discovery", start=400)
    snapshot = write_snapshot(tmp_path, [(replay(game_id, opponent, "metadata"), "fetched")])
    (snapshot / "games.json").write_text("[]\n")

    with pytest.raises(ValueError, match="snapshot file"):
        parse_snapshot(snapshot)
    assert not (snapshot / "processed").exists()
    assert not (snapshot / ".processed.tmp").exists()


def test_split_hash_is_stable_and_requires_label_agreement() -> None:
    assert split_bucket("d61p-resident:", 123) == split_bucket(
        "d61p-resident:", 123
    )
    assert 0 <= split_bucket("d61p-opponent:", 456) <= 9


def test_collector_output_is_directly_consumable_by_snapshot_parser(
    tmp_path: Path,
) -> None:
    game_id, opponent = matching_pair("discovery", start=500)
    body = replay(game_id, opponent, "end-to-end")

    class Client:
        def post(self, service: str, request: object) -> ApiResponse:
            if service == "Leaderboards/getFilteredPuzzleLeaderboard":
                return ApiResponse.from_payload(
                    {
                        "users": [
                            {
                                "agentId": RESIDENT,
                                "pseudo": "resident",
                                "codingamer": {"userId": 1},
                                "league": {"divisionIndex": 5},
                                "rank": 1,
                                "localRank": 1,
                                "score": 20.0,
                            },
                            {
                                "agentId": opponent,
                                "pseudo": "opponent",
                                "codingamer": {"userId": 2},
                                "league": {"divisionIndex": 5},
                                "rank": 2,
                                "localRank": 2,
                                "score": 19.0,
                            },
                        ]
                    }
                )
            if service == "gamesPlayersRanking/findLastBattlesByAgentId":
                agent = int(request[0])
                return ApiResponse.from_payload(
                    [{"gameId": game_id, "done": True, "players": []}]
                    if agent in {RESIDENT, opponent}
                    else []
                )
            if service == "gameResult/findByGameId":
                assert int(request[0]) == game_id
                return ApiResponse.from_payload(body)
            raise AssertionError(service)

    snapshot = collect_snapshot(
        raw_root=tmp_path / "raw",
        snapshot_id="end-to-end-d61p",
        resident_agent_id=RESIDENT,
        client=Client(),
    )
    processed = parse_snapshot(snapshot)

    qa = json.loads((processed / "qa.json").read_text())
    assert qa["counts"]["eligible_replays"] == 1
    assert qa["counts"]["parsed_games"] == 1
    assert qa["counts"]["parse_failures"] == 0
    assert qa["gates"]["all_eligible_games_parsed"]
