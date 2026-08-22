#!/usr/bin/env python3
"""Repeat the frozen E7a sector analysis on agent 6590141's public Arena games.

Read-only services only.  The script never submits code, starts a TestSession game, or
changes Arena state.  It filters every battle by exact agent/submission identity, decodes
the official turn-1 state, applies the already-frozen E7a geometry rule without refitting,
and publishes compact game rows plus descriptive transfer statistics.

The resulting selected-vs-unselected comparison is observational: map sector, opponent,
seat, and matchmaking are not randomized, and every game uses the E7a candidate.
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import statistics
import sys
import time
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.top_player_opening_analysis import adjacent, bfs, opening_features, terrain

AGENT_ID = 6590141
SUBMISSION_ID = 41081503
USER_ID = 1302251
PID = "spring-challenge-2026-troll-farm"
TSH = "77167730956ef53402472b3c52474908f5b73026"
BASE = "https://www.codingame.com/services/"
BATTLE_SERVICE = "gamesPlayersRanking/findLastBattlesByAgentId"
GAME_SERVICE = "gameResult/findByGameId"
LEADERBOARD_SERVICE = "Leaderboards/getFilteredPuzzleLeaderboard"
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
DEFAULT_CSV = ROOT / "chatgpt_1/new-agent-6590141-live-sector-games-2026-08-02.csv"
DEFAULT_JSON = ROOT / "chatgpt_1/new-agent-6590141-live-sector-analysis-2026-08-02.json"

CSV_FIELDS = (
    "game_id",
    "observed_order",
    "seat",
    "opponent",
    "opponent_agent_id",
    "opponent_rank",
    "opponent_ladder_score",
    "turns",
    "our_score",
    "opponent_score",
    "margin",
    "won",
    "tied",
    "catastrophe",
    "static_map_fingerprint",
    "initial_state_fingerprint",
    "lemon_distance_sum",
    "plum_distance_sum",
    "parent_default_species",
    "plum_minus_lemon_distance",
    "frozen_sector_selected",
    "candidate_species",
    "initial_self_plum",
    "initial_self_lemon",
    "initial_self_apple",
    "initial_self_banana",
    "initial_self_iron",
    "initial_self_wood",
    "initial_opp_plum",
    "initial_opp_lemon",
    "initial_opp_apple",
    "initial_opp_banana",
    "initial_opp_iron",
    "initial_opp_wood",
    "initial_lemon_count",
    "initial_plum_count",
    "initial_lemon_health",
    "initial_plum_health",
    "initial_lemon_fruits",
    "initial_plum_fruits",
    "tree_total",
    "fruit_total",
    "own_door_count",
    "shack_door_distance",
)


def parser_module():
    path = ROOT / "data/scripts/parse.py"
    spec = importlib.util.spec_from_file_location("troll_farm_parse", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load parser from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def post(service: str, payload: Any, retries: int = 4) -> Any:
    last: Exception | None = None
    for attempt in range(retries):
        request = Request(
            BASE + service,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "troll-farm-read-only-live-sector-audit/1",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=90) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError) as error:
            last = error
            if attempt + 1 == retries:
                break
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"public service failed: {service}: {last}")


def battle_players(battle: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for player in battle.get("players") or []:
        rows.append(
            {
                "agent_id": int(player.get("playerAgentId") or -1),
                "submission_id": (
                    int(player["submissionId"]) if player.get("submissionId") is not None else None
                ),
                "position": int(player.get("position") or 0),
                "pseudo": player.get("nickname"),
                "user_id": (
                    int(player["userId"]) if player.get("userId") is not None else None
                ),
            }
        )
    return rows


def exact_battles() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw = post(BATTLE_SERVICE, [AGENT_ID, None])
    if not isinstance(raw, list):
        raise ValueError(f"battle endpoint returned {type(raw).__name__}, expected list")
    matching = []
    unexpected = []
    for order, battle in enumerate(raw):
        players = battle_players(battle)
        target = [row for row in players if row["agent_id"] == AGENT_ID]
        if len(target) != 1 or target[0]["submission_id"] != SUBMISSION_ID:
            unexpected.append(
                {
                    "game_id": battle.get("gameId"),
                    "done": battle.get("done"),
                    "players": players,
                }
            )
            continue
        matching.append(
            {
                "game_id": int(battle["gameId"]),
                "done": bool(battle.get("done")),
                "observed_order": order,
                "players": players,
            }
        )
    return matching, {
        "listed": len(raw),
        "matching": len(matching),
        "matching_finished": sum(row["done"] for row in matching),
        "matching_pending": sum(not row["done"] for row in matching),
        "unexpected": unexpected,
        "response_sha256": digest(raw),
    }


def leaderboard() -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    try:
        raw = post(
            LEADERBOARD_SERVICE,
            [PID, TSH, "global", {"active": False, "column": "", "filter": ""}],
        )
    except Exception as error:  # leaderboard adjustment is optional, game identity is not
        return {}, {"available": False, "error": str(error)}
    rows: dict[int, dict[str, Any]] = {}
    for user in raw.get("users") or []:
        agent_id = user.get("agentId")
        if agent_id is None:
            continue
        rows[int(agent_id)] = {
            "rank": int(user.get("rank") or 0),
            "score": float(user.get("score") or 0.0),
            "pseudo": user.get("pseudo"),
        }
    return rows, {
        "available": True,
        "agent_count": len(rows),
        "response_sha256": digest(raw),
    }


def target_agent(game: dict[str, Any]) -> tuple[dict[str, Any], int]:
    matches = [agent for agent in game.get("agents") or [] if int(agent.get("agentId") or -1) == AGENT_ID]
    if len(matches) != 1:
        raise ValueError(f"game {game.get('gameId')} has {len(matches)} target agents")
    agent = matches[0]
    codingamer = agent.get("codingamer") or {}
    user_id = codingamer.get("userId")
    if user_id is not None and int(user_id) != USER_ID:
        raise ValueError(f"game {game.get('gameId')} target user mismatch: {user_id}")
    return agent, int(agent["index"])


def initial_sector(map_data: dict[str, Any], seat: int) -> dict[str, Any]:
    board = terrain(map_data)
    shack = board["shacks"][seat]
    doors = [cell for cell in adjacent(shack) if cell in board["walkable"]]
    distances = bfs(board["walkable"], doors)
    sums = {}
    for species in ("LEMON", "PLUM"):
        sums[species] = sum(
            distances.get((int(plant["x"]), int(plant["y"])), 10_000)
            for plant in map_data["trees0"]
            if str(plant["type"]).upper() == species
        )
    parent = "LEMON" if sums["LEMON"] <= sums["PLUM"] else "PLUM"
    delta = sums["PLUM"] - sums["LEMON"]
    selected = parent == "LEMON" and delta <= 8
    return {
        "lemon_distance_sum": sums["LEMON"],
        "plum_distance_sum": sums["PLUM"],
        "parent_default_species": parent,
        "plum_minus_lemon_distance": delta,
        "frozen_sector_selected": selected,
        "candidate_species": "PLUM" if selected else parent,
    }


def game_row(
    metadata: dict[str, Any],
    ladder: dict[int, dict[str, Any]],
    parse: Any,
) -> dict[str, Any]:
    game = post(GAME_SERVICE, [metadata["game_id"], None])
    if int(game.get("gameId") or -1) != metadata["game_id"]:
        raise ValueError(f"game-result mismatch for {metadata['game_id']}")
    agent, seat = target_agent(game)
    frames = game.get("frames") or []
    if not frames:
        raise ValueError(f"game {metadata['game_id']} has no frames")
    map_data, trolls, inv0, inv1 = parse.parse_frame0(frames[0]["view"])
    if inv0 is None or inv1 is None:
        raise ValueError(f"game {metadata['game_id']} lacks initial inventories")
    inventories = [inv0, inv1]
    initial_state = {
        "inventories": inventories,
        "units": trolls,
        "plants": map_data["trees0"],
    }
    opening = opening_features(map_data, initial_state, seat)
    sector = initial_sector(map_data, seat)
    scores = [int(value) for value in game.get("scores") or []]
    if len(scores) != 2:
        raise ValueError(f"game {metadata['game_id']} has invalid scores")
    opponent_agents = [
        row for row in game.get("agents") or [] if int(row.get("index") or -1) == 1 - seat
    ]
    if len(opponent_agents) != 1:
        raise ValueError(f"game {metadata['game_id']} lacks unique opponent")
    opponent_agent = opponent_agents[0]
    opponent_id = int(opponent_agent.get("agentId") or -1)
    opponent_codingamer = opponent_agent.get("codingamer") or {}
    opponent_name = opponent_codingamer.get("pseudo") or "?"
    opponent_ladder = ladder.get(opponent_id, {})
    plants = map_data["trees0"]
    counts = {
        species: [plant for plant in plants if str(plant["type"]).upper() == species]
        for species in ("LEMON", "PLUM")
    }
    static_fingerprint = digest({"rows": map_data["rows"], "seat": seat})
    initial_fingerprint = digest(
        {
            "rows": map_data["rows"],
            "seat": seat,
            "inventories": inventories,
            "trolls": sorted(trolls, key=lambda row: int(row["id"])),
            "plants": sorted(
                plants,
                key=lambda row: (
                    int(row["x"]), int(row["y"]), str(row["type"]), int(row["stage"])
                ),
            ),
        }
    )
    turns, _final_inventory = parse.extract_turns(frames, inv0, inv1)
    margin = scores[seat] - scores[1 - seat]
    row: dict[str, Any] = {
        "game_id": metadata["game_id"],
        "observed_order": metadata["observed_order"],
        "seat": seat,
        "opponent": opponent_name,
        "opponent_agent_id": opponent_id,
        "opponent_rank": opponent_ladder.get("rank"),
        "opponent_ladder_score": opponent_ladder.get("score"),
        "turns": len(turns),
        "our_score": scores[seat],
        "opponent_score": scores[1 - seat],
        "margin": margin,
        "won": margin > 0,
        "tied": margin == 0,
        "catastrophe": margin <= -100,
        "static_map_fingerprint": static_fingerprint,
        "initial_state_fingerprint": initial_fingerprint,
        **sector,
    }
    for index, name in enumerate(ITEMS):
        row[f"initial_self_{name.lower()}"] = inventories[seat][index]
        row[f"initial_opp_{name.lower()}"] = inventories[1 - seat][index]
    for species in ("LEMON", "PLUM"):
        prefix = species.lower()
        row[f"initial_{prefix}_count"] = len(counts[species])
        row[f"initial_{prefix}_health"] = sum(int(plant["health"]) for plant in counts[species])
        row[f"initial_{prefix}_fruits"] = sum(int(plant["fruits"]) for plant in counts[species])
    row["tree_total"] = opening["tree_total"]
    row["fruit_total"] = opening["fruit_total"]
    row["own_door_count"] = opening["own_door_count"]
    row["shack_door_distance"] = opening["shack_door_distance"]
    return row


def mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def median(values: Iterable[float]) -> float | None:
    values = sorted(values)
    return statistics.median(values) if values else None


def bootstrap_mean(values: list[float], repetitions: int, seed: int) -> dict[str, Any] | None:
    if not values:
        return None
    rng = random.Random(seed)
    n = len(values)
    draws = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(repetitions))
    return {
        "repetitions": repetitions,
        "seed": seed,
        "lower_95": draws[int(0.025 * repetitions)],
        "median": draws[repetitions // 2],
        "upper_95": draws[min(repetitions - 1, int(0.975 * repetitions))],
        "probability_le_zero": sum(value <= 0 for value in draws) / repetitions,
    }


def bootstrap_difference(
    selected: list[float], other: list[float], repetitions: int, seed: int
) -> dict[str, Any] | None:
    if not selected or not other:
        return None
    rng = random.Random(seed)
    a = len(selected)
    b = len(other)
    draws = sorted(
        sum(selected[rng.randrange(a)] for _ in range(a)) / a
        - sum(other[rng.randrange(b)] for _ in range(b)) / b
        for _ in range(repetitions)
    )
    return {
        "repetitions": repetitions,
        "seed": seed,
        "lower_95": draws[int(0.025 * repetitions)],
        "median": draws[repetitions // 2],
        "upper_95": draws[min(repetitions - 1, int(0.975 * repetitions))],
        "probability_le_zero": sum(value <= 0 for value in draws) / repetitions,
    }


def summarize(rows: list[dict[str, Any]], repetitions: int, seed: int) -> dict[str, Any]:
    margins = [float(row["margin"]) for row in rows]
    return {
        "games": len(rows),
        "wins": sum(row["won"] for row in rows),
        "ties": sum(row["tied"] for row in rows),
        "losses": sum(row["margin"] < 0 for row in rows),
        "win_rate": sum(row["won"] for row in rows) / len(rows) if rows else None,
        "mean_margin": mean(margins),
        "median_margin": median(margins),
        "mean_score": mean(float(row["our_score"]) for row in rows),
        "mean_opponent_score": mean(float(row["opponent_score"]) for row in rows),
        "catastrophes": sum(row["catastrophe"] for row in rows),
        "catastrophe_rate": sum(row["catastrophe"] for row in rows) / len(rows) if rows else None,
        "negative_margin_mass": sum(-row["margin"] for row in rows if row["margin"] < 0),
        "seats": {str(seat): sum(row["seat"] == seat for row in rows) for seat in (0, 1)},
        "distinct_opponents": len({row["opponent_agent_id"] for row in rows}),
        "mean_opponent_ladder_score": mean(
            float(row["opponent_ladder_score"])
            for row in rows
            if row["opponent_ladder_score"] is not None
        ),
        "root_bootstrap_mean_margin": bootstrap_mean(margins, repetitions, seed),
    }


def same_opponent_contrast(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_opponent: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_opponent.setdefault(int(row["opponent_agent_id"]), []).append(row)
    contrasts = []
    for opponent_id, group in by_opponent.items():
        selected = [row["margin"] for row in group if row["frozen_sector_selected"]]
        other = [row["margin"] for row in group if not row["frozen_sector_selected"]]
        if selected and other:
            contrasts.append(
                {
                    "opponent_agent_id": opponent_id,
                    "opponent": group[0]["opponent"],
                    "selected_games": len(selected),
                    "other_games": len(other),
                    "selected_minus_other_margin": statistics.mean(selected) - statistics.mean(other),
                }
            )
    return {
        "opponents_with_both_sectors": len(contrasts),
        "contrasts": sorted(contrasts, key=lambda row: row["opponent_agent_id"]),
        "mean_of_opponent_contrasts": mean(
            float(row["selected_minus_other_margin"]) for row in contrasts
        ),
        "median_of_opponent_contrasts": median(
            float(row["selected_minus_other_margin"]) for row in contrasts
        ),
    }


def build_report(
    rows: list[dict[str, Any]],
    identity: dict[str, Any],
    ladder_meta: dict[str, Any],
    repetitions: int,
) -> dict[str, Any]:
    rows = sorted(rows, key=lambda row: row["observed_order"])
    selected = [row for row in rows if row["frozen_sector_selected"]]
    other = [row for row in rows if not row["frozen_sector_selected"]]
    parent_plum = [row for row in rows if row["parent_default_species"] == "PLUM"]
    lemon_clear = [
        row
        for row in rows
        if row["parent_default_species"] == "LEMON" and not row["frozen_sector_selected"]
    ]
    report = {
        "schema": "troll-farm-new-agent-live-sector-analysis/1",
        "identity": {
            "agent_id": AGENT_ID,
            "submission_id": SUBMISSION_ID,
            "user_id": USER_ID,
            **identity,
        },
        "services": {
            "base": BASE,
            "battle": BATTLE_SERVICE,
            "game": GAME_SERVICE,
            "leaderboard": LEADERBOARD_SERVICE,
            "read_only": True,
            "leaderboard_meta": ladder_meta,
        },
        "frozen_rule": {
            "refit": False,
            "definition": (
                "parent default is LEMON and PLUM aggregate BFS distance minus LEMON "
                "aggregate BFS distance is <= 8"
            ),
            "unreachable_penalty": 10_000,
            "parent_tie_break": "LEMON",
        },
        "overall": summarize(rows, repetitions, 2026080201),
        "sectors": {
            "e7a_selected": summarize(selected, repetitions, 2026080202),
            "not_selected": summarize(other, repetitions, 2026080203),
            "parent_plum": summarize(parent_plum, repetitions, 2026080204),
            "parent_lemon_clear": summarize(lemon_clear, repetitions, 2026080205),
        },
        "selected_minus_not_selected": {
            "raw_mean_margin_difference": (
                statistics.mean(row["margin"] for row in selected)
                - statistics.mean(row["margin"] for row in other)
                if selected and other
                else None
            ),
            "bootstrap": bootstrap_difference(
                [float(row["margin"]) for row in selected],
                [float(row["margin"]) for row in other],
                repetitions,
                2026080206,
            ),
            "same_opponent_descriptive": same_opponent_contrast(rows),
        },
        "support": {
            "selected_games": len(selected),
            "selected_fraction": len(selected) / len(rows) if rows else None,
            "distinct_static_maps": len({row["static_map_fingerprint"] for row in rows}),
            "duplicate_static_map_games": len(rows)
            - len({row["static_map_fingerprint"] for row in rows}),
        },
        "interpretation": {
            "candidate_only_observational": True,
            "same_window_parent_control": False,
            "causal_treatment_effect_identified": False,
            "allowed_claim": (
                "live performance heterogeneity across the frozen initial map sector"
            ),
            "forbidden_claim": (
                "selected-minus-unselected outcome difference equals the causal value of E7a"
            ),
        },
        "rows_sha256": digest(rows),
    }
    return report


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: item["observed_order"]):
            writer.writerow({field: row.get(field) for field in CSV_FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--bootstrap", type=int, default=100_000)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 16:
        raise SystemExit("--jobs must be in 1..16")
    parse = parser_module()
    battles, identity = exact_battles()
    finished = [row for row in battles if row["done"]]
    if not finished:
        raise RuntimeError("no exact finished games")
    ladder, ladder_meta = leaderboard()
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(game_row, metadata, ladder, parse): metadata
            for metadata in finished
        }
        for completed, future in enumerate(as_completed(futures), 1):
            metadata = futures[future]
            try:
                rows.append(future.result())
            except Exception as error:
                failures.append({"game_id": metadata["game_id"], "error": str(error)})
            if completed % 20 == 0 or completed == len(futures):
                print(f"processed {completed}/{len(futures)} games; failures={len(failures)}")
    if failures:
        raise RuntimeError(f"game extraction failed closed: {failures[:10]}")
    if len(rows) != identity["matching_finished"]:
        raise RuntimeError(
            f"row count {len(rows)} != exact finished count {identity['matching_finished']}"
        )
    report = build_report(rows, identity, ladder_meta, args.bootstrap)
    write_csv(args.csv, rows)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"saved {len(rows)} games; selected={report['support']['selected_games']}; "
        f"overall mean={report['overall']['mean_margin']:+.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
