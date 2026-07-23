#!/usr/bin/env python3
"""Parse and QA one immutable D61p replay snapshot without touching the base corpus."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cgauto.replay_conformance import action_commands, effective_chop_unit_ids
from cgauto.replay_state import decode_replay
from data.scripts.parse import extract_turns, parse_frame0, player_features
from data.scripts.qa import MAXW, score_status


ELIGIBLE_STATUSES = {"fetched", "already_present", "already_present_race"}
OPEN_SPLITS = {
    "discovery",
    "validation",
    "calibration_only",
    "top_legend_observation",
}
LEAGUE_NAMES = {
    0: "Wood2",
    1: "Wood1",
    2: "Bronze",
    3: "Silver",
    4: "Gold",
    5: "Legend",
}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha1_map(rows: list[str]) -> str:
    return hashlib.sha1("\n".join(rows).encode()).hexdigest()[:16]


def split_bucket(prefix: str, value: int) -> int:
    digest = hashlib.sha256(f"{prefix}{value}".encode()).hexdigest()
    return int(digest, 16) % 10


def bucket_label(bucket: int) -> str:
    if 0 <= bucket <= 5:
        return "discovery"
    if bucket <= 7:
        return "validation"
    return "confirmation"


def agent_id(agent: dict) -> int | None:
    value = agent.get("agentId")
    return int(value) if value is not None else None


def player_identity(agent: dict) -> str | None:
    codingamer = agent.get("codingamer") or {}
    boss = agent.get("arenaboss") or {}
    value = (
        codingamer.get("pseudo")
        or boss.get("nickname")
        or agent.get("name")
        or agent_id(agent)
    )
    return str(value) if value is not None else None


def resident_split(game_id: int, agents: list[dict], resident_agent_id: int) -> dict:
    ids = [agent_id(agent) for agent in agents]
    if resident_agent_id not in ids:
        return {
            "label": "top_legend_observation",
            "resident_game_bucket": None,
            "opponent_bucket": None,
            "opponent_agent_id": None,
        }
    opponent_ids = [value for value in ids if value is not None and value != resident_agent_id]
    if len(opponent_ids) != 1:
        return {
            "label": "calibration_only",
            "resident_game_bucket": split_bucket("d61p-resident:", game_id),
            "opponent_bucket": None,
            "opponent_agent_id": None,
        }
    opponent = opponent_ids[0]
    game_bucket = split_bucket("d61p-resident:", game_id)
    opponent_bucket = split_bucket("d61p-opponent:", opponent)
    game_label = bucket_label(game_bucket)
    opponent_label = bucket_label(opponent_bucket)
    return {
        "label": game_label if game_label == opponent_label else "calibration_only",
        "resident_game_bucket": game_bucket,
        "opponent_bucket": opponent_bucket,
        "opponent_agent_id": opponent,
    }


def point_symmetric_map(map_obj: dict) -> bool:
    rows = map_obj["rows"]
    width, height = map_obj["w"], map_obj["h"]
    swap = {"0": "1", "1": "0"}
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            mirrored = rows[height - 1 - y][width - 1 - x]
            if mirrored != swap.get(char, char):
                return False
    return True


def point_symmetric_plants(map_obj: dict) -> bool:
    width, height = map_obj["w"], map_obj["h"]
    fields = ("type", "size", "fruits", "stage", "health", "cur_cd", "cd_eff")
    signatures = {
        (plant["x"], plant["y"], *(plant[field] for field in fields))
        for plant in map_obj["trees0"]
    }
    return all(
        (width - 1 - plant["x"], height - 1 - plant["y"], *(plant[field] for field in fields))
        in signatures
        for plant in map_obj["trees0"]
    )


def validate_map(map_obj: dict, trolls: list[dict]) -> None:
    width, height = map_obj["w"], map_obj["h"]
    if width <= 0 or height <= 0 or len(map_obj["rows"]) != height:
        raise ValueError("invalid map dimensions")
    if any(len(row) != width for row in map_obj["rows"]):
        raise ValueError("invalid map row width")
    if set(map_obj["shacks"]) != {"p0", "p1"}:
        raise ValueError("map does not contain exactly two labeled shacks")
    if len(trolls) != 2 or sorted(troll["player"] for troll in trolls) != [0, 1]:
        raise ValueError("initial state does not contain one troll per player")
    if not map_obj["trees0"]:
        raise ValueError("initial state has no plants")
    for plant in map_obj["trees0"]:
        if not (0 <= plant["x"] < width and 0 <= plant["y"] < height):
            raise ValueError("initial plant outside map")
        if not 1 <= plant["stage"] <= 7:
            raise ValueError("initial plant stage outside [1, 7]")
        if plant["type"] not in MAXW:
            raise ValueError("unknown initial plant type")
        if plant["cd_eff"] > MAXW[plant["type"]] or plant["cur_cd"] > plant["cd_eff"]:
            raise ValueError("invalid initial plant cooldown")
    if not point_symmetric_map(map_obj):
        raise ValueError("terrain is not point-symmetric")
    if not point_symmetric_plants(map_obj):
        raise ValueError("initial plants are not point-symmetric")


def trajectory_bytes(turns: list[dict]) -> bytes:
    return b"".join(
        (json.dumps(row, separators=(",", ":")) + "\n").encode() for row in turns
    )


def validate_agents(replay: dict) -> list[dict]:
    agents = replay.get("agents")
    if not isinstance(agents, list) or len(agents) != 2:
        raise ValueError("replay does not contain exactly two agents")
    if any(player_identity(agent) is None for agent in agents):
        raise ValueError("replay contains an unidentified agent")
    if not isinstance(replay.get("scores"), list) or len(replay["scores"]) != 2:
        raise ValueError("replay does not contain two scores")
    if not isinstance(replay.get("ranks"), list) or len(replay["ranks"]) != 2:
        raise ValueError("replay does not contain two ranks")
    return agents


def league_lookup(leaderboard: dict) -> dict[int, dict]:
    result = {}
    for user in leaderboard.get("users") or []:
        user_id = (user.get("codingamer") or {}).get("userId")
        if user_id is None:
            continue
        league = (user.get("league") or {}).get("divisionIndex")
        result[int(user_id)] = {
            "leagueIndex": league,
            "league": LEAGUE_NAMES.get(league),
            "globalRank": user.get("rank"),
            "localRank": user.get("localRank"),
            "arenaScore": user.get("score"),
        }
    return result


def parse_replay(path: Path, acquisition: dict, by_user: dict[int, dict]) -> dict:
    replay = json.loads(path.read_text())
    game_id = int(acquisition["game_id"])
    if int(replay.get("gameId", -1)) != game_id:
        raise ValueError("cache body game ID differs from acquisition manifest")
    frames = replay.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("replay has no frames")
    agents = validate_agents(replay)
    map_obj, trolls, inv0, inv1 = parse_frame0(frames[0]["view"])
    if inv0 is None or inv1 is None or len(inv0) != 6 or len(inv1) != 6:
        raise ValueError("initial inventories are not two six-item rows")
    validate_map(map_obj, trolls)
    turns, final_inv = extract_turns(frames, inv0, inv1)
    if not turns:
        raise ValueError("replay has no resolved turns")
    features = player_features(turns, frames, final_inv)

    chop_ids = []
    for turn in turns:
        commands = action_commands(turn.get("commands0")) + action_commands(
            turn.get("commands1")
        )
        chop_ids.append(effective_chop_unit_ids(commands))
    decoded = decode_replay(path, chop_unit_ids_by_turn=chop_ids)
    if decoded["unknown_updates"]:
        raise ValueError(f"unknown replay diff updates: {decoded['unknown_updates'][:3]}")
    if len(decoded["states"]) != len(turns) + 1:
        raise ValueError("official decoded-state/trajectory turn mismatch")
    decoded_final = decoded["states"][-1]["inventories"]
    if decoded_final != [list(final_inv[0]), list(final_inv[1])]:
        raise ValueError("official decoded and parsed final inventories differ")
    score_class, derived_scores = score_status(replay["scores"], decoded_final)
    if score_class == "unexpected":
        raise ValueError(
            f"unexpected final score mismatch official={replay['scores']} derived={derived_scores}"
        )

    players = []
    for index, agent in enumerate(agents):
        codingamer = agent.get("codingamer") or {}
        user_id = codingamer.get("userId")
        league = by_user.get(int(user_id), {}) if user_id is not None else {}
        boss = agent.get("arenaboss")
        players.append(
            {
                "index": agent.get("index", index),
                "agentId": agent_id(agent),
                "userId": user_id,
                "name": player_identity(agent),
                "isBoss": boss is not None,
                **league,
            }
        )

    map_hash = sha1_map(map_obj["rows"])
    trajectory = trajectory_bytes(turns)
    game = {
        "gameId": game_id,
        "players": players,
        "scores": replay["scores"],
        "ranks": replay["ranks"],
        "n_turns": len(turns),
        "map_hash": map_hash,
        "map": {
            key: map_obj[key]
            for key in ("w", "h", "rows", "shacks", "iron", "water", "trees0")
        },
        "trolls0": trolls,
        "per_player": features,
        "acquisition": {
            "status": acquisition["status"],
            "sources": acquisition.get("sources") or [],
            "boss_visible": bool(acquisition.get("boss_visible")),
            "response_sha256": acquisition["response_sha256"],
        },
    }
    qa = {
        "game_id": game_id,
        "turns": len(turns),
        "decoded_states": len(decoded["states"]),
        "unknown_diff_updates": 0,
        "score_status": score_class,
        "terrain_point_symmetric": True,
        "plants_point_symmetric": True,
        "trajectory_sha256": sha256_bytes(trajectory),
    }
    return {"game": game, "trajectory": trajectory, "map_obj": map_obj, "qa": qa}


def safe_child(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"path escapes root: {relative!r}")
    return path


def verify_snapshot_files(snapshot: Path, manifest: dict) -> None:
    if manifest.get("schema") != "troll-farm-d61p-snapshot-v1":
        raise ValueError("unknown D61p snapshot schema")
    if not manifest.get("complete") or not manifest.get("all_wanted_games_classified"):
        raise ValueError("D61p snapshot is incomplete")
    for relative, expected in (manifest.get("files") or {}).items():
        path = safe_child(snapshot, relative)
        if not path.is_file():
            raise ValueError(f"missing snapshot file: {relative}")
        if path.stat().st_size != int(expected["bytes"]):
            raise ValueError(f"snapshot file size mismatch: {relative}")
        if sha256_file(path) != expected["sha256"]:
            raise ValueError(f"snapshot file hash mismatch: {relative}")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as target:
        for row in rows:
            target.write(json.dumps(row, separators=(",", ":")) + "\n")


def build_map_record(map_hash: str, map_obj: dict, game_ids: list[int]) -> dict:
    tree_counts = collections.Counter(plant["type"] for plant in map_obj["trees0"])
    return {
        "map_hash": map_hash,
        "w": map_obj["w"],
        "h": map_obj["h"],
        "rows": map_obj["rows"],
        "shacks": map_obj["shacks"],
        "counts": map_obj["counts"],
        "iron_cells": map_obj["iron"],
        "water_cells": map_obj["water"],
        "tree_total": len(map_obj["trees0"]),
        "tree_counts": dict(tree_counts),
        "trees0": map_obj["trees0"],
        "n_games": len(game_ids),
        "gameIds": sorted(game_ids),
    }


def parse_snapshot(snapshot: Path) -> Path:
    snapshot = Path(snapshot).resolve()
    manifest_path = snapshot / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    processed = snapshot / "processed"
    temporary = snapshot / ".processed.tmp"
    if processed.exists() or temporary.exists():
        raise FileExistsError("snapshot already has processed or temporary output")
    manifest = json.loads(manifest_path.read_text())
    verify_snapshot_files(snapshot, manifest)
    raw_root = snapshot.parent.parent.resolve()
    games_manifest_path = snapshot / "games.json"
    leaderboard_path = snapshot / "leaderboard.json"
    if not games_manifest_path.is_file() or not leaderboard_path.is_file():
        raise ValueError("snapshot lacks games.json or leaderboard.json")
    acquisitions = json.loads(games_manifest_path.read_text())
    if not isinstance(acquisitions, list):
        raise ValueError("snapshot games manifest is not a list")
    raw_ids = [int(row["game_id"]) for row in acquisitions]
    duplicate_raw_ids = len(raw_ids) - len(set(raw_ids))
    if duplicate_raw_ids:
        raise ValueError("snapshot games manifest contains duplicate game IDs")
    leaderboard = json.loads(leaderboard_path.read_text())
    by_user = league_lookup(leaderboard)
    resident_agent_id = int(manifest["config"]["resident_agent_id"])

    temporary.mkdir()
    (temporary / "open" / "trajectories").mkdir(parents=True)
    (temporary / "sealed_confirmation" / "trajectories").mkdir(parents=True)
    parsed = []
    failures = []
    sealed_failures = []
    acquisition_failed = []
    splits = []
    trajectory_hash_to_games: dict[str, list[int]] = collections.defaultdict(list)
    map_groups: dict[str, dict] = {}
    eligible = 0
    for acquisition in sorted(acquisitions, key=lambda row: int(row["game_id"])):
        game_id = int(acquisition["game_id"])
        if acquisition.get("status") not in ELIGIBLE_STATUSES:
            acquisition_failed.append(
                {
                    "game_id": game_id,
                    "status": acquisition.get("status"),
                    "error": acquisition.get("error"),
                }
            )
            continue
        eligible += 1
        split = None
        try:
            cache_path = safe_child(raw_root, acquisition["cache_file"])
            if not cache_path.is_file():
                raise ValueError("referenced replay cache file is missing")
            if sha256_file(cache_path) != acquisition["response_sha256"]:
                raise ValueError("replay cache hash differs from acquisition record")
            raw_replay = json.loads(cache_path.read_text())
            split = resident_split(
                game_id,
                raw_replay.get("agents") or [],
                resident_agent_id,
            )
            result = parse_replay(cache_path, acquisition, by_user)
            result["game"]["split"] = split["label"]
            result["qa"]["split"] = split["label"]
            map_hash = result["game"]["map_hash"]
            group = map_groups.setdefault(
                map_hash, {"map_obj": result["map_obj"], "game_ids": []}
            )
            if group["map_obj"]["rows"] != result["map_obj"]["rows"]:
                raise ValueError("map-hash collision")
            group["game_ids"].append(game_id)
            parsed.append(result)
            trajectory_hash_to_games[result["qa"]["trajectory_sha256"]].append(game_id)
            split_row = {"game_id": game_id, **split}
            splits.append(split_row)
        except Exception as error:  # noqa: BLE001 - classify all snapshot games
            detail = {"game_id": game_id, "error": f"{type(error).__name__}: {error}"}
            if split is not None and split["label"] == "confirmation":
                sealed_failures.append(detail)
                failures.append(
                    {"game_id": game_id, "split": "confirmation", "error": "sealed"}
                )
            else:
                failures.append(detail)

    parsed.sort(key=lambda result: result["game"]["gameId"])
    splits.sort(key=lambda row: row["game_id"])
    open_games = []
    sealed_games = []
    for result in parsed:
        game = result["game"]
        game_id = int(game["gameId"])
        if game["split"] == "confirmation":
            sealed_games.append(game)
            destination = temporary / "sealed_confirmation" / "trajectories"
        else:
            if game["split"] not in OPEN_SPLITS:
                raise RuntimeError(f"unknown D61p split: {game['split']}")
            open_games.append(game)
            destination = temporary / "open" / "trajectories"
        (destination / f"{game_id}.jsonl").write_bytes(result["trajectory"])

    write_jsonl(temporary / "open" / "games.jsonl", open_games)
    write_jsonl(temporary / "sealed_confirmation" / "games.jsonl", sealed_games)
    maps = [
        build_map_record(map_hash, group["map_obj"], group["game_ids"])
        for map_hash, group in sorted(map_groups.items())
    ]
    write_jsonl(temporary / "maps.jsonl", maps)
    write_json(temporary / "parse_failures.json", failures)
    write_json(
        temporary / "sealed_confirmation" / "parse_failures.json", sealed_failures
    )

    split_counts = collections.Counter(row["label"] for row in splits)
    split_manifest = {
        "schema": "troll-farm-d61p-splits-v1",
        "resident_agent_id": resident_agent_id,
        "rule": {
            "game": 'SHA256("d61p-resident:" + gameId) mod 10',
            "opponent": 'SHA256("d61p-opponent:" + opponentAgentId) mod 10',
            "buckets": {"0-5": "discovery", "6-7": "validation", "8-9": "confirmation"},
            "agreement_required": True,
        },
        "counts": dict(sorted(split_counts.items())),
        "rows": splits,
    }
    write_json(temporary / "split_manifest.json", split_manifest)

    parsed_ids = {result["game"]["gameId"] for result in parsed}
    resident_games = [
        result
        for result in parsed
        if resident_agent_id
        in {player["agentId"] for player in result["game"]["players"]}
    ]
    top_source_agents = set()
    top_games = 0
    for result in parsed:
        has_top = False
        for source in result["game"]["acquisition"]["sources"]:
            if "legend_top20" in (source.get("groups") or []):
                top_source_agents.add(int(source["agent_id"]))
                has_top = True
        top_games += int(has_top)
    trajectory_duplicates = {
        digest: ids
        for digest, ids in trajectory_hash_to_games.items()
        if len(ids) > 1
    }
    qa_rows_internal = [result["qa"] for result in parsed]
    qa_rows = [
        (
            {
                "game_id": row["game_id"],
                "split": "confirmation",
                "integrity_pass": True,
            }
            if row["split"] == "confirmation"
            else row
        )
        for row in qa_rows_internal
    ]
    score_counts = collections.Counter(row["score_status"] for row in qa_rows_internal)
    gates = {
        "all_acquisition_rows_eligible": not acquisition_failed,
        "all_eligible_games_parsed": len(parsed) == eligible and not failures,
        "zero_duplicate_game_ids": duplicate_raw_ids == 0
        and len(parsed_ids) == len(parsed),
        "zero_duplicate_trajectories": not trajectory_duplicates,
        "zero_unexpected_scores": score_counts.get("unexpected", 0) == 0,
        "all_turns_have_decoded_states": all(
            row["decoded_states"] == row["turns"] + 1 for row in qa_rows_internal
        ),
        "zero_unknown_diff_updates": all(
            row["unknown_diff_updates"] == 0 for row in qa_rows_internal
        ),
        "all_maps_and_plants_symmetric": all(
            row["terrain_point_symmetric"] and row["plants_point_symmetric"]
            for row in qa_rows_internal
        ),
        "at_least_80_resident_games": len(resident_games) >= 80,
        "at_least_15_top20_source_agents": len(top_source_agents) >= 15,
        "at_least_75_top20_games": top_games >= 75,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    qa = {
        "schema": "troll-farm-d61p-qa-v1",
        "snapshot_id": manifest["snapshot_id"],
        "counts": {
            "acquisition_rows": len(acquisitions),
            "eligible_replays": eligible,
            "acquisition_failed": len(acquisition_failed),
            "parsed_games": len(parsed),
            "parse_failures": len(failures),
            "resident_games": len(resident_games),
            "top20_source_agents": len(top_source_agents),
            "top20_games": top_games,
            "maps": len(maps),
            "open_games": len(open_games),
            "sealed_confirmation_games": len(sealed_games),
            "score_statuses": dict(sorted(score_counts.items())),
            "duplicate_trajectory_groups": len(trajectory_duplicates),
        },
        "acquisition_failures": acquisition_failed,
        "trajectory_duplicates": trajectory_duplicates,
        "rows": qa_rows,
        "gates": gates,
        "pass": all(gates.values()),
        "confirmation_content_exposed": False,
    }
    write_json(temporary / "qa.json", qa)
    stats = {
        "games_parsed": len(parsed),
        "resident_games": len(resident_games),
        "top20_games": top_games,
        "unique_maps": len(maps),
        "open_turn_histogram": dict(
            sorted(
                collections.Counter(game["n_turns"] for game in open_games).items()
            )
        ),
        "split_counts": dict(sorted(split_counts.items())),
    }
    write_json(temporary / "stats.json", stats)

    output_files = sorted(path for path in temporary.rglob("*") if path.is_file())
    product_manifest = {
        "schema": "troll-farm-d61p-processed-v1",
        "source_snapshot_id": manifest["snapshot_id"],
        "source_manifest_sha256": sha256_file(manifest_path),
        "files": {
            path.relative_to(temporary).as_posix(): {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in output_files
        },
    }
    write_json(temporary / "manifest.json", product_manifest)
    if processed.exists():
        raise FileExistsError(processed)
    os.rename(temporary, processed)
    return processed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    processed = parse_snapshot(args.snapshot)
    qa = json.loads((processed / "qa.json").read_text())
    print(
        json.dumps(
            {
                "processed": str(processed),
                "pass": qa["pass"],
                "counts": qa["counts"],
                "gates": qa["gates"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
