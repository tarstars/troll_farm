#!/usr/bin/env python3
"""Build the compact open-data corpus for the 2026-08-02 top-player review.

The source is one immutable D61p snapshot.  Only ``processed/open/games.jsonl`` is
eligible for tabular rows; the sibling sealed-confirmation directory is never traversed.
One direct current-vs-top20 replay is copied in sanitized form for exact sequence review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


CURRENT_AGENT = 6589709
CURRENT_SUBMISSION = 41079653
TOP_CUTOFF = 20
VERBS = (
    "MOVE",
    "TRAIN",
    "PICK",
    "PLANT",
    "HARVEST",
    "DROP",
    "MINE",
    "CHOP",
    "WAIT",
    "MSG",
)
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
PLANTS = ("PLUM", "LEMON", "APPLE", "BANANA")
SCORE_TURNS = (50, 100, 150, 200, 250, 300)
WOOD_TURNS = (100, 200, 300)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compact_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def pick(values: list[Any] | None, index: int) -> Any:
    if not values or index >= len(values):
        return None
    return values[index]


def harvested_units(values: dict[str, Any], item: str) -> int:
    return int(values.get(item, 0) or 0) + int(values.get(f"{item}s", 0) or 0)


def source_has_group(game: dict[str, Any], group: str) -> bool:
    return any(
        group in (source.get("groups") or [])
        for source in (game.get("acquisition", {}).get("sources") or [])
    )


def player_is_top(player: dict[str, Any], top_ids: set[int]) -> bool:
    return int(player.get("agentId", -1)) in top_ids


def side_row(
    game: dict[str, Any],
    seat: int,
    *,
    top_ids: set[int],
    top20_source: bool,
    current_new: bool,
    direct: bool,
) -> dict[str, Any]:
    player = game["players"][seat]
    opponent = game["players"][1 - seat]
    features = game["per_player"][str(seat)]
    commands = features.get("commands_summary") or {}
    effects = features.get("effects") or {}
    plants_cmd = features.get("plants_by_type") or {}
    planted_ok = features.get("planted_ok") or {}
    harvested = features.get("harvested") or {}
    trains = features.get("trains") or []
    final_inv = features.get("final_inv") or []
    map_obj = game.get("map") or {}
    trees = map_obj.get("trees0") or []
    tree_counts = {kind: 0 for kind in PLANTS}
    for tree in trees:
        kind = str(tree.get("type", "")).upper()
        if kind in tree_counts:
            tree_counts[kind] += 1

    score = game["scores"][seat]
    opponent_score = game["scores"][1 - seat]
    row: dict[str, Any] = {
        "game_id": int(game["gameId"]),
        "split": game.get("split"),
        "acquisition_status": game["acquisition"]["status"],
        "current_new_game": int(current_new),
        "top20_source_game": int(top20_source),
        "direct_current_vs_top20": int(direct),
        "turns": int(game["n_turns"]),
        "map_w": map_obj.get("w"),
        "map_h": map_obj.get("h"),
        "initial_trees": len(trees),
        "initial_iron_cells": len(map_obj.get("iron") or []),
        "initial_water_cells": len(map_obj.get("water") or []),
        "seat": seat,
        "agent_id": int(player["agentId"]),
        "name": player.get("name"),
        "snapshot_rank": player.get("globalRank"),
        "arena_score": player.get("arenaScore"),
        "is_current": int(int(player["agentId"]) == CURRENT_AGENT),
        "is_top20": int(player_is_top(player, top_ids)),
        "opponent_agent_id": int(opponent["agentId"]),
        "opponent_name": opponent.get("name"),
        "opponent_snapshot_rank": opponent.get("globalRank"),
        "opponent_arena_score": opponent.get("arenaScore"),
        "opponent_is_top20": int(player_is_top(opponent, top_ids)),
        "score": score,
        "opponent_score": opponent_score,
        "margin": score - opponent_score,
        "win": int(score > opponent_score),
        "tie": int(score == opponent_score),
        "loss": int(score < opponent_score),
        "train_count": len(trains),
        "roster_final": 1 + int(effects.get("trained", len(trains)) or 0),
        "first_train_turn": trains[0][0] if trains else None,
        "second_train_turn": trains[1][0] if len(trains) > 1 else None,
        "third_train_turn": trains[2][0] if len(trains) > 2 else None,
        "train_sequence_json": compact_json(trains),
        "effect_failed": int(effects.get("failed", 0) or 0),
        "effect_trained": int(effects.get("trained", 0) or 0),
        "effect_chops_landed": int(effects.get("chops_landed", 0) or 0),
        "effect_collected_wood": int(effects.get("collected_WOOD", 0) or 0),
        "effect_collected_iron": int(effects.get("collected_IRON", 0) or 0),
        "effect_dropped_items": int(effects.get("dropped_item", 0) or 0)
        + int(effects.get("dropped_items", 0) or 0),
    }
    for kind in PLANTS:
        lower = kind.lower()
        row[f"initial_{lower}_trees"] = tree_counts[kind]
        row[f"plant_cmd_{lower}"] = int(plants_cmd.get(kind, 0) or 0)
        row[f"planted_ok_{lower}"] = int(planted_ok.get(kind, 0) or 0)
        row[f"harvested_{lower}_units"] = harvested_units(harvested, kind)
    for verb in VERBS:
        row[f"cmd_{verb.lower()}"] = int(commands.get(verb, 0) or 0)
    for item_index, item in enumerate(ITEMS):
        lower = item.lower()
        row[f"picked_{lower}"] = int(effects.get(f"picked_{item}", 0) or 0)
        row[f"final_{lower}"] = pick(final_inv, item_index)
    for index, turn in enumerate(SCORE_TURNS):
        row[f"score_t{turn}"] = pick(features.get("score_curve"), index)
    for index, turn in enumerate(WOOD_TURNS):
        row[f"wood_t{turn}"] = pick(features.get("wood_curve"), index)
    return row


def sanitize_direct_replay(payload: dict[str, Any]) -> dict[str, Any]:
    agents = []
    for agent in payload.get("agents") or []:
        codingamer = agent.get("codingamer") or {}
        agents.append(
            {
                "agentId": agent.get("agentId"),
                "index": agent.get("index"),
                "score": agent.get("score"),
                "valid": agent.get("valid"),
                "codingamer": {
                    "userId": codingamer.get("userId"),
                    "pseudo": codingamer.get("pseudo"),
                },
            }
        )
    return {
        "gameId": payload.get("gameId"),
        "agents": agents,
        "scores": payload.get("scores"),
        "ranks": payload.get("ranks"),
        "frames": payload.get("frames"),
    }


def build(snapshot: Path, output_prefix: Path, expected_manifest_sha256: str) -> dict[str, Any]:
    snapshot = snapshot.resolve()
    manifest_path = snapshot / "manifest.json"
    players_path = snapshot / "players.json"
    qa_path = snapshot / "processed" / "qa.json"
    open_games_path = snapshot / "processed" / "open" / "games.jsonl"
    for path in (manifest_path, players_path, qa_path, open_games_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    observed_manifest_sha256 = sha256(manifest_path)
    if observed_manifest_sha256 != expected_manifest_sha256:
        raise ValueError(
            f"snapshot manifest hash mismatch: {observed_manifest_sha256} != "
            f"{expected_manifest_sha256}"
        )
    manifest = json.loads(manifest_path.read_text())
    qa = json.loads(qa_path.read_text())
    if not manifest.get("complete") or not manifest.get("all_wanted_games_classified"):
        raise ValueError("snapshot is not complete")
    if not qa.get("pass") or int(qa["counts"]["parse_failures"]) != 0:
        raise ValueError("snapshot QA did not pass cleanly")

    roster = json.loads(players_path.read_text())
    top_rows = sorted(
        (
            row
            for row in roster
            if row.get("legend_order") is not None
            and int(row["legend_order"]) <= TOP_CUTOFF
        ),
        key=lambda row: int(row["legend_order"]),
    )
    top_ids = {int(row["agent_id"]) for row in top_rows}
    if len(top_ids) != TOP_CUTOFF:
        raise ValueError(f"expected {TOP_CUTOFF} top identities, got {len(top_ids)}")

    games: list[dict[str, Any]] = []
    all_new_open = 0
    for line in open_games_path.read_text().splitlines():
        game = json.loads(line)
        if game["acquisition"]["status"] == "fetched":
            all_new_open += 1
        current_new = game["acquisition"]["status"] == "fetched" and any(
            int(player["agentId"]) == CURRENT_AGENT for player in game["players"]
        )
        top20_source = source_has_group(game, "legend_top20")
        if current_new or top20_source:
            games.append(game)

    side_rows: list[dict[str, Any]] = []
    direct_games: list[dict[str, Any]] = []
    current_new_games = 0
    top20_source_games = 0
    new_top20_source_games = 0
    top20_vs_top20_games = 0
    top20_side_rows = 0
    current_outcomes = {"wins": 0, "ties": 0, "losses": 0}
    current_seats = {"0": 0, "1": 0}
    current_splits: dict[str, int] = {}
    for game in games:
        current_new = game["acquisition"]["status"] == "fetched" and any(
            int(player["agentId"]) == CURRENT_AGENT for player in game["players"]
        )
        top20_source = source_has_group(game, "legend_top20")
        direct = current_new and any(
            int(player["agentId"]) != CURRENT_AGENT and player_is_top(player, top_ids)
            for player in game["players"]
        )
        current_new_games += int(current_new)
        top20_source_games += int(top20_source)
        new_top20_source_games += int(
            top20_source and game["acquisition"]["status"] == "fetched"
        )
        top_count = sum(player_is_top(player, top_ids) for player in game["players"])
        top20_vs_top20_games += int(top_count == 2)
        top20_side_rows += top_count
        if current_new:
            current_seat = next(
                seat
                for seat, player in enumerate(game["players"])
                if int(player["agentId"]) == CURRENT_AGENT
            )
            current_seats[str(current_seat)] += 1
            split = str(game.get("split"))
            current_splits[split] = current_splits.get(split, 0) + 1
            own_score = game["scores"][current_seat]
            other_score = game["scores"][1 - current_seat]
            if own_score > other_score:
                current_outcomes["wins"] += 1
            elif own_score == other_score:
                current_outcomes["ties"] += 1
            else:
                current_outcomes["losses"] += 1
        if direct:
            direct_games.append(game)
        for seat in (0, 1):
            side_rows.append(
                side_row(
                    game,
                    seat,
                    top_ids=top_ids,
                    top20_source=top20_source,
                    current_new=current_new,
                    direct=direct,
                )
            )

    if len(direct_games) != 1:
        raise ValueError(f"expected exactly one direct open matchup, got {len(direct_games)}")
    direct_id = int(direct_games[0]["gameId"])
    raw_root = snapshot.parent.parent
    raw_direct_path = raw_root / "games" / f"{direct_id}.json"
    trajectory_path = (
        snapshot / "processed" / "open" / "trajectories" / f"{direct_id}.jsonl"
    )
    if not raw_direct_path.is_file() or not trajectory_path.is_file():
        raise FileNotFoundError("direct open replay or trajectory is missing")

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    sides_path = Path(f"{output_prefix}.sides.csv")
    direct_path = Path(f"{output_prefix}.direct-game.json")
    trajectory_output = Path(f"{output_prefix}.direct-trajectory.json")
    manifest_output = Path(f"{output_prefix}.manifest.json")
    if not side_rows:
        raise ValueError("shared corpus is empty")
    with sides_path.open("w", newline="") as target:
        writer = csv.DictWriter(
            target, fieldnames=list(side_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(side_rows)
    write_json(direct_path, sanitize_direct_replay(json.loads(raw_direct_path.read_text())))
    write_json(
        trajectory_output,
        [json.loads(line) for line in trajectory_path.read_text().splitlines()],
    )

    files = {}
    for path in (sides_path, direct_path, trajectory_output):
        files[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "physical_lines": sum(1 for _ in path.open("rb")),
        }
    output = {
        "schema": "troll-farm-top-player-new-games-shared-v1",
        "task_id": "20260802-top-player-new-games-multiagent-analysis",
        "snapshot": {
            "snapshot_id": manifest["snapshot_id"],
            "completed_at_utc": manifest["completed_at_utc"],
            "manifest_sha256": observed_manifest_sha256,
            "qa_sha256": sha256(qa_path),
        },
        "definitions": {
            "current_agent_id": CURRENT_AGENT,
            "current_submission_id": CURRENT_SUBMISSION,
            "new": "acquisition.status == fetched",
            "top20": "snapshot players legend_order 1..20",
            "shared_rows": "union(current new open games, all open top20-source games)",
            "sealed_policy": "only processed/open was read; sealed_confirmation was excluded",
        },
        "counts": {
            "all_new_open_games": all_new_open,
            "current_new_open_games": current_new_games,
            "top20_source_open_games": top20_source_games,
            "new_top20_source_open_games": new_top20_source_games,
            "top20_vs_top20_open_games": top20_vs_top20_games,
            "top20_side_rows": top20_side_rows,
            "union_open_games": len(games),
            "side_rows": len(side_rows),
            "direct_current_vs_top20_games": len(direct_games),
            "direct_game_id": direct_id,
            "sealed_games_excluded": int(qa["counts"]["sealed_confirmation_games"]),
            "current_open_outcomes": current_outcomes,
            "current_open_seats": current_seats,
            "current_open_splits": dict(sorted(current_splits.items())),
        },
        "top20_roster": [
            {
                "rank": int(row["legend_order"]),
                "agent_id": int(row["agent_id"]),
                "name": row["pseudo"],
                "score": row.get("score"),
            }
            for row in top_rows
        ],
        "inputs": {
            "players_sha256": sha256(players_path),
            "open_games_sha256": sha256(open_games_path),
            "direct_raw_sha256": sha256(raw_direct_path),
            "direct_trajectory_sha256": sha256(trajectory_path),
        },
        "files": files,
    }
    write_json(manifest_output, output)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--expect-manifest-sha256", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build(args.snapshot, args.output_prefix, args.expect_manifest_sha256)
    print(json.dumps({"status": "ok", "counts": result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
