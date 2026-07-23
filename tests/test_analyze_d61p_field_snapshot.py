"""Tests for sealed, open-only D61p field-transfer analysis."""

from __future__ import annotations

import json
from pathlib import Path

from cgauto.analyze_d61p_field_snapshot import (
    REQUIRED_QA_GATES,
    analyze_open_game,
    analyze_snapshot,
    attack_angle_matrix,
    load_open_inputs,
    resident_outcome_summary,
    sha256_file,
)
from data.scripts.collect_snapshot import ApiResponse, collect_snapshot
from data.scripts.parse_snapshot import (
    bucket_label,
    parse_replay,
    parse_snapshot,
    split_bucket,
)


RESIDENT = 6_561_795


def replay(game_id: int = 123, opponent: int = 777) -> dict:
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
                "codingamer": {"userId": 2, "pseudo": "opponent"},
            },
        ],
        "scores": [4, 4],
        "ranks": [0, 0],
        "frames": [
            {"view": " 0\n" + json.dumps(initial)},
            {"agentId": 0, "stdout": "WAIT"},
            {
                "agentId": 1,
                "stdout": "WAIT",
                "keyframe": True,
                "view": " 1\n" + json.dumps(resolved),
            },
        ],
    }


def matching_discovery_pair() -> tuple[int, int]:
    for opponent in range(700, 2_000):
        if bucket_label(split_bucket("d61p-opponent:", opponent)) != "discovery":
            continue
        for game_id in range(10_000, 20_000):
            if bucket_label(split_bucket("d61p-resident:", game_id)) == "discovery":
                return game_id, opponent
    raise AssertionError("no discovery pair")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def metadata(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def empty_passed_snapshot(tmp_path: Path) -> Path:
    snapshot = tmp_path / "raw" / "snapshots" / "open-only"
    processed = snapshot / "processed"
    (processed / "open").mkdir(parents=True)
    write_json(snapshot / "leaderboard.json", {"users": []})
    write_json(
        snapshot / "players.json",
        [
            {
                "agent_id": 777,
                "groups": ["legend_top20"],
                "source_rank": 1,
            }
        ],
    )
    write_json(snapshot / "games.json", [])
    manifest = {
        "schema": "troll-farm-d61p-snapshot-v1",
        "snapshot_id": "open-only",
        "complete": True,
        "all_wanted_games_classified": True,
        "config": {"resident_agent_id": RESIDENT},
        "files": {
            relative: metadata(snapshot / relative)
            for relative in ("leaderboard.json", "players.json", "games.json")
        },
    }
    write_json(snapshot / "manifest.json", manifest)
    write_json(
        processed / "qa.json",
        {
            "schema": "troll-farm-d61p-qa-v1",
            "pass": True,
            "confirmation_content_exposed": False,
            "gates": {name: True for name in sorted(REQUIRED_QA_GATES)},
        },
    )
    write_json(
        processed / "split_manifest.json",
        {
            "schema": "troll-farm-d61p-splits-v1",
            "resident_agent_id": RESIDENT,
            "rows": [],
        },
    )
    (processed / "open" / "games.jsonl").write_text("")
    product = {
        "schema": "troll-farm-d61p-processed-v1",
        "source_snapshot_id": "open-only",
        "source_manifest_sha256": sha256_file(snapshot / "manifest.json"),
        "files": {
            relative: metadata(processed / relative)
            for relative in (
                "qa.json",
                "split_manifest.json",
                "open/games.jsonl",
            )
        },
    }
    write_json(processed / "manifest.json", product)
    return snapshot


def test_loader_requires_no_sealed_confirmation_directory(tmp_path: Path) -> None:
    snapshot = empty_passed_snapshot(tmp_path)

    loaded = load_open_inputs(snapshot)

    assert loaded["tasks"] == []
    assert loaded["resident_agent_id"] == RESIDENT
    assert not (snapshot / "processed" / "sealed_confirmation").exists()


def test_exact_open_game_reconstructs_resident_and_selected_top_source(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "123.json"
    raw.write_text(json.dumps(replay()))
    parsed = parse_replay(
        raw,
        {
            "game_id": 123,
            "status": "fetched",
            "sources": [{"agent_id": 777, "groups": ["legend_top20"]}],
            "boss_visible": False,
            "response_sha256": "fixture",
        },
        {
            1: {"leagueIndex": 5, "league": "Legend", "localRank": 20},
            2: {"leagueIndex": 5, "league": "Legend", "localRank": 1},
        },
    )
    game = parsed["game"]
    game["split"] = "discovery"
    trajectory = tmp_path / "123.jsonl"
    trajectory.write_bytes(parsed["trajectory"])

    result = analyze_open_game(
        {
            "game": game,
            "raw_path": str(raw),
            "trajectory_path": str(trajectory),
            "resident_agent_id": RESIDENT,
            "top_source_ids": [777],
        }
    )

    assert result["integrity"] == {
        "trajectory_turns": 1,
        "decoded_turns": 1,
        "unknown_diff_updates": 0,
        "final_inventory_exact": True,
    }
    assert result["resident"]["own_crops_created"] == 0
    assert result["resident"]["crop_attribution_quality"]["unknown_diff_updates"] == 0
    assert [row["is_selected_top_source"] for row in result["players"]] == [False, True]


def test_collector_parser_analyzer_pipeline_runs_with_process_pool(
    tmp_path: Path,
) -> None:
    game_id, opponent = matching_discovery_pair()
    body = replay(game_id, opponent)

    class Client:
        def post(self, service: str, request: object) -> ApiResponse:
            if service == "Leaderboards/getFilteredPuzzleLeaderboard":
                return ApiResponse.from_payload(
                    {
                        "users": [
                            {
                                "agentId": opponent,
                                "pseudo": "opponent",
                                "codingamer": {"userId": 2},
                                "league": {"divisionIndex": 5},
                                "rank": 1,
                                "localRank": 1,
                                "score": 20.0,
                            },
                            {
                                "agentId": RESIDENT,
                                "pseudo": "resident",
                                "codingamer": {"userId": 1},
                                "league": {"divisionIndex": 5},
                                "rank": 20,
                                "localRank": 20,
                                "score": 19.0,
                            },
                        ]
                    }
                )
            if service == "gamesPlayersRanking/findLastBattlesByAgentId":
                return ApiResponse.from_payload([{"gameId": game_id, "done": True}])
            if service == "gameResult/findByGameId":
                return ApiResponse.from_payload(body)
            raise AssertionError(service)

    snapshot = collect_snapshot(
        raw_root=tmp_path / "raw",
        snapshot_id="pipeline",
        resident_agent_id=RESIDENT,
        client=Client(),
    )
    processed = parse_snapshot(snapshot)
    qa_path = processed / "qa.json"
    qa = json.loads(qa_path.read_text())
    # The one-game fixture emulates the already-enforced volume decision; real data can
    # reach this state only through parse_snapshot's frozen volume gates.
    qa["gates"] = {name: True for name in sorted(REQUIRED_QA_GATES)}
    qa["pass"] = True
    write_json(qa_path, qa)
    product_path = processed / "manifest.json"
    product = json.loads(product_path.read_text())
    product["files"]["qa.json"] = metadata(qa_path)
    write_json(product_path, product)
    output = tmp_path / "analysis.json"

    report = analyze_snapshot(snapshot, output, jobs=2)

    assert output.is_file()
    assert report["integrity"]["open_games"] == 1
    assert report["integrity"]["resident_target_games"] == 1
    assert report["integrity"]["top_source_appearances"] == 1
    assert report["integrity"]["confirmation_products_read"] is False
    assert {row["id"] for row in report["attack_angle_matrix"]} == {
        f"F{index}" for index in range(1, 11)
    }


def field_row(index: int, *, catastrophic: bool) -> dict:
    opponent_wood = 60 if catastrophic else 10
    crop_wood = 35 if catastrophic else 0
    return {
        "game_id": 1_000 + index,
        "split": "discovery" if index < 10 else "validation",
        "opponent": f"opponent-{index % 5}",
        "opponent_agent_id": 2_000 + index % 5,
        "score_status": "exact",
        "margin": -120 if catastrophic else 20,
        "won": not catastrophic,
        "starting_inventory": [10, 2, 2, 5, 4, 0],
        "own_crops_created": 0,
        "final": {"opponent_wood": opponent_wood, "resident_workers": 2},
        "opponent_crop_summary": {
            "opponent_wood_collected": crop_wood,
            "crops": 6 if catastrophic else 0,
        },
    }


def test_field_zero_crop_is_descriptive_while_repeated_tail_can_support_attack() -> None:
    rows = [field_row(index, catastrophic=index < 5) for index in range(20)]
    by_split = {
        split: [row for row in rows if row["split"] == split]
        for split in ("discovery", "validation")
    }

    summary = resident_outcome_summary(rows)
    matrix = attack_angle_matrix(rows, by_split, [], [], [])
    by_id = {row["id"]: row for row in matrix}

    assert summary["zero_crop_tail"]["rate"] == 1.0
    assert "descriptive only" in summary["zero_crop_tail"]["interpretation"]
    assert by_id["F1"]["status"] == "supported"
    assert by_id["F7"]["status"] == "supported"
    assert by_id["F8"]["status"] == "descriptive"
    assert by_id["F2"]["status"] == "insufficient"
