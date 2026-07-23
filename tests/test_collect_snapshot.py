"""Tests for immutable, outcome-blind D61p replay acquisition."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from data.scripts.collect_snapshot import (
    ApiResponse,
    PublicClient,
    battle_has_visible_boss,
    collect_snapshot,
    select_players,
)


def user(agent_id: int, rank: int, league: int = 5) -> dict:
    return {
        "agentId": agent_id,
        "pseudo": f"player-{agent_id}",
        "rank": rank + 100,
        "localRank": rank,
        "score": 20.0 - rank / 100.0,
        "league": {"divisionIndex": league},
        "codingamer": {"userId": agent_id + 10_000},
    }


def battle(game_id: int, *, boss: bool = False, done: bool = True) -> dict:
    nickname = "Boss 5" if boss else "ordinary"
    return {
        "gameId": game_id,
        "done": done,
        "players": [{"nickname": nickname}],
    }


class FakeClient:
    def __init__(self, leaderboard: dict, battles: dict[int, list[dict]]) -> None:
        self.leaderboard = leaderboard
        self.battles = battles
        self.calls: list[tuple[str, object]] = []

    def post(self, service: str, body: object) -> ApiResponse:
        self.calls.append((service, body))
        if service == "Leaderboards/getFilteredPuzzleLeaderboard":
            return ApiResponse.from_payload(self.leaderboard)
        if service == "gamesPlayersRanking/findLastBattlesByAgentId":
            return ApiResponse.from_payload(self.battles[int(body[0])])
        if service == "gameResult/findByGameId":
            game_id = int(body[0])
            return ApiResponse.from_payload(
                {"gameId": game_id, "frames": [{"view": f"game-{game_id}"}]}
            )
        raise AssertionError(service)


def test_select_players_keeps_twenty_legend_plus_absent_resident() -> None:
    users = [user(agent_id, agent_id) for agent_id in range(1, 26)]
    selected = select_players(users, resident_agent_id=99)

    assert len(selected) == 21
    assert selected[0]["agent_id"] == 99
    assert selected[0]["groups"] == ["resident"]
    legends = [row for row in selected if "legend_top20" in row["groups"]]
    assert [row["agent_id"] for row in legends] == list(range(1, 21))


def test_resident_inside_top_twenty_is_requested_once_with_both_groups() -> None:
    users = [user(agent_id, agent_id) for agent_id in range(1, 26)]
    selected = select_players(users, resident_agent_id=5)

    assert len(selected) == 20
    resident = next(row for row in selected if row["agent_id"] == 5)
    assert resident["groups"] == ["legend_top20", "resident"]
    assert selected[0] is resident


@pytest.mark.parametrize(
    "row",
    [
        {"gameId": 1, "done": True, "arenaBoss": 5},
        {"gameId": 1, "done": True, "players": [{"isBoss": True}]},
        {"gameId": 1, "done": True, "players": [{"nickname": "Boss 5"}]},
    ],
)
def test_visible_boss_detection(row: dict) -> None:
    assert battle_has_visible_boss(row)
    assert not battle_has_visible_boss(battle(2))


def test_snapshot_is_immutable_deduplicated_and_does_not_touch_singletons(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    (raw / "battles").mkdir(parents=True)
    (raw / "games").mkdir()
    sentinels = {
        raw / "leaderboard.json": b"old-leaderboard",
        raw / "players.json": b"old-players",
        raw / "fetch_log.json": b"old-fetch-log",
        raw / "battles" / "legacy.json": b"old-battles",
    }
    for path, content in sentinels.items():
        path.write_bytes(content)

    existing = ApiResponse.from_payload({"gameId": 100, "frames": [{"view": "old"}]})
    (raw / "games" / "100.json").write_bytes(existing.raw)
    legend_one = [battle(game_id) for game_id in range(220, 208, -1)]
    legend_one.append(battle(150, boss=True))
    client = FakeClient(
        {"users": [user(1, 1), user(2, 2), user(99, 30, league=4)]},
        {
            99: [battle(100)],
            1: legend_one,
            2: [battle(220)],
        },
    )
    ticks = iter(f"2026-07-21T12:00:{index:02d}.000Z" for index in range(100))

    snapshot = collect_snapshot(
        raw_root=raw,
        snapshot_id="20260721T120000Z-d61p-test",
        resident_agent_id=99,
        client=client,
        timestamp=lambda: next(ticks),
    )

    for path, content in sentinels.items():
        assert path.read_bytes() == content
    assert (raw / "games" / "100.json").read_bytes() == existing.raw
    assert (snapshot / "manifest.json").exists()
    manifest = json.loads((snapshot / "manifest.json").read_text())
    games = json.loads((snapshot / "games.json").read_text())
    by_id = {row["game_id"]: row for row in games}
    assert manifest["complete"]
    assert manifest["counts"]["unique_games_wanted"] == 12
    assert manifest["counts"]["game_statuses"] == {
        "already_present": 1,
        "fetched": 11,
    }
    assert set(by_id) == {100, 150, *range(211, 221)}
    assert 209 not in by_id and 210 not in by_id
    assert by_id[150]["boss_visible"]
    assert [source["agent_id"] for source in by_id[220]["sources"]] == [1, 2]
    replay_calls = [
        int(body[0])
        for service, body in client.calls
        if service == "gameResult/findByGameId"
    ]
    assert 100 not in replay_calls
    assert set(replay_calls) == set(by_id) - {100}
    assert all(row["request_body_sha256"] for row in games)
    assert all(row["response_sha256"] for row in games)

    with pytest.raises(FileExistsError):
        collect_snapshot(
            raw_root=raw,
            snapshot_id="20260721T120000Z-d61p-test",
            resident_agent_id=99,
            client=client,
        )


def test_invalid_existing_cache_is_classified_and_never_replaced(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    (raw / "games").mkdir(parents=True)
    invalid = b'{"gameId":100,"frames":[]}'
    (raw / "games" / "100.json").write_bytes(invalid)
    client = FakeClient(
        {"users": [user(99, 1)]},
        {99: [battle(100)]},
    )

    snapshot = collect_snapshot(
        raw_root=raw,
        snapshot_id="invalid-cache-d61p-test",
        resident_agent_id=99,
        client=client,
    )

    assert (raw / "games" / "100.json").read_bytes() == invalid
    games = json.loads((snapshot / "games.json").read_text())
    assert games[0]["status"] == "failed_existing_invalid"
    manifest = json.loads((snapshot / "manifest.json").read_text())
    assert manifest["counts"]["failures"] == 1
    assert not any(
        service == "gameResult/findByGameId" for service, _ in client.calls
    )


def test_public_client_enforces_interval_and_timeout() -> None:
    class Clock:
        def __init__(self) -> None:
            self.value = 0.0
            self.sleeps: list[float] = []

        def now(self) -> float:
            return self.value

        def sleep(self, seconds: float) -> None:
            self.sleeps.append(seconds)
            self.value += seconds

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"ok":true}'

    clock = Clock()
    timeouts = []

    def urlopen(_request: object, *, timeout: int) -> Response:
        timeouts.append(timeout)
        return Response()

    client = PublicClient(
        monotonic=clock.now,
        sleep=clock.sleep,
        urlopen=urlopen,
    )
    client.post("one", [1])
    client.post("two", [2])

    assert clock.sleeps == [pytest.approx(0.35)]
    assert timeouts == [20, 20]
    with pytest.raises(ValueError):
        PublicClient(request_interval=0.34)
    with pytest.raises(ValueError):
        PublicClient(timeout=19)
