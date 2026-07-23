#!/usr/bin/env python3
"""Reproduce the live agent's repeated-loss and orchard-signature analysis.

The analysis is deliberately observational.  It uses the checked-in processed corpus and turn
trajectories; it performs no network calls and cannot submit or play a game.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import statistics

REPO = Path(__file__).resolve().parent.parent
GAMES = REPO / "data/processed/games.jsonl"
TRAJECTORIES = REPO / "data/processed/trajectories"
LIVE_AGENT = 6553250
TARGETS = ("delineate", "wala", "norxondor_gorgonax")


def mean(rows: list[dict], field: str) -> float | None:
    values = [row[field] for row in rows if row.get(field) is not None]
    return statistics.mean(values) if values else None


def summarize(rows: list[dict]) -> dict:
    fields = (
        "margin",
        "my_score",
        "opp_score",
        "my_wood",
        "opp_wood",
        "my_fruit",
        "opp_fruit",
        "wood_gap_t100",
        "wood_gap_t200",
        "wood_gap_t300",
        "my_trained",
        "opp_trained",
        "my_planted",
        "opp_planted",
        "my_harvested",
        "opp_harvested",
        "my_chops_landed",
        "opp_chops_landed",
        "my_wood_per_chop",
        "opp_wood_per_chop",
    )
    return {
        "games": len(rows),
        "wins": sum(row["won"] for row in rows),
        "means": {field: mean(rows, field) for field in fields},
    }


def player_index(game: dict, agent_id: int) -> int | None:
    return next(
        (player["index"] for player in game["players"] if player["agentId"] == agent_id),
        None,
    )


def game_row(game: dict, agent_id: int) -> dict | None:
    me = player_index(game, agent_id)
    if me is None:
        return None
    opponent = next(player for player in game["players"] if player["index"] == 1 - me)
    mine = game["per_player"][str(me)]
    theirs = game["per_player"][str(1 - me)]
    my_curve = mine["wood_curve"]
    opp_curve = theirs["wood_curve"]
    my_chops = mine["effects"].get("chops_landed", 0)
    opp_chops = theirs["effects"].get("chops_landed", 0)

    def gap(index: int) -> int | None:
        if my_curve[index] is None or opp_curve[index] is None:
            return None
        return my_curve[index] - opp_curve[index]

    return {
        "game_id": game["gameId"],
        "opponent": opponent["name"],
        "seat": me,
        "won": game["ranks"][me] == 0,
        "margin": game["scores"][me] - game["scores"][1 - me],
        "my_score": game["scores"][me],
        "opp_score": game["scores"][1 - me],
        "my_wood": mine["final_inv"][5],
        "opp_wood": theirs["final_inv"][5],
        "my_fruit": sum(mine["final_inv"][:4]),
        "opp_fruit": sum(theirs["final_inv"][:4]),
        "wood_gap_t100": gap(0),
        "wood_gap_t200": gap(1),
        "wood_gap_t300": gap(2),
        "my_trained": mine["effects"].get("trained", 0),
        "opp_trained": theirs["effects"].get("trained", 0),
        "my_planted": sum(mine["planted_ok"].values()),
        "opp_planted": sum(theirs["planted_ok"].values()),
        "my_harvested": sum(mine["harvested"].values()),
        "opp_harvested": sum(theirs["harvested"].values()),
        "my_chops_landed": my_chops,
        "opp_chops_landed": opp_chops,
        "my_wood_per_chop": mine["final_inv"][5] / my_chops if my_chops else None,
        "opp_wood_per_chop": theirs["final_inv"][5] / opp_chops if opp_chops else None,
        "initial_trees": len(game["map"]["trees0"]),
    }


def starter_actions(game: dict, seat: int, trajectory: Path) -> dict[int, str]:
    starter = min(troll["id"] for troll in game["trolls0"] if troll["player"] == seat)
    actions = {}
    for line in trajectory.open():
        turn = json.loads(line)
        commands = turn.get(f"commands{seat}") or ""
        for raw in re.split(r"[;\n]+", commands):
            fields = raw.strip().split()
            if len(fields) < 2:
                continue
            try:
                unit = int(fields[1])
            except ValueError:
                continue
            if unit == starter:
                actions[turn["t"]] = fields[0].upper()
    return actions


def longest_harvest_drop_run(actions: dict[int, str]) -> int:
    harvest_drop = {
        turn for turn, verb in actions.items() if verb == "HARVEST" and actions.get(turn + 1) == "DROP"
    }
    longest = 0
    for turn in harvest_drop:
        if turn - 2 in harvest_drop:
            continue
        length = 1
        while turn + 2 * length in harvest_drop:
            length += 1
        longest = max(longest, length)
    return longest


def pattern_counts(losses: list[dict]) -> dict:
    patterns = {
        "wood_ahead_t100_then_behind_t300": lambda row: row["wood_gap_t100"] is not None
        and row["wood_gap_t300"] is not None
        and row["wood_gap_t100"] > 0
        and row["wood_gap_t300"] < 0,
        "opponent_at_least_20_plants_and_20_harvested": lambda row: row["opp_planted"] >= 20
        and row["opp_harvested"] >= 20,
        "opponent_trained_at_least_two": lambda row: row["opp_trained"] >= 2,
        "opponent_at_least_60_chops_landed": lambda row: row["opp_chops_landed"] >= 60,
        "opponent_at_least_70_final_wood": lambda row: row["opp_wood"] >= 70,
    }
    return {
        name: {"count": sum(predicate(row) for row in losses), "games": len(losses)}
        for name, predicate in patterns.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/matchup-loss-analysis.json",
    )
    args = parser.parse_args()

    games = [json.loads(line) for line in GAMES.open()]
    live_games = [game for game in games if player_index(game, LIVE_AGENT) is not None]
    rows = [game_row(game, LIVE_AGENT) for game in live_games]
    rows = [row for row in rows if row is not None]
    target_rows = [row for row in rows if row["opponent"] in TARGETS]
    losses = [row for row in target_rows if not row["won"]]

    orchard_rows = []
    for game, row in zip(live_games, rows, strict=True):
        actions = starter_actions(
            game,
            row["seat"],
            TRAJECTORIES / f"{game['gameId']}.jsonl",
        )
        run = longest_harvest_drop_run(actions)
        if run >= 3:
            orchard_rows.append(
                {
                    "game_id": row["game_id"],
                    "opponent": row["opponent"],
                    "won": row["won"],
                    "margin": row["margin"],
                    "longest_harvest_drop_run": run,
                    "my_wood": row["my_wood"],
                    "opp_wood": row["opp_wood"],
                    "my_fruit": row["my_fruit"],
                }
            )

    by_opponent = {}
    for opponent in TARGETS:
        group = [row for row in target_rows if row["opponent"] == opponent]
        by_opponent[opponent] = {
            "all": summarize(group),
            "wins": summarize([row for row in group if row["won"]]),
            "losses": summarize([row for row in group if not row["won"]]),
        }

    payload = {
        "schema": 1,
        "agent_id": LIVE_AGENT,
        "live_games": summarize(rows),
        "targets": list(TARGETS),
        "target_aggregate": {
            "all": summarize(target_rows),
            "wins": summarize([row for row in target_rows if row["won"]]),
            "losses": summarize(losses),
        },
        "target_loss_patterns": pattern_counts(losses),
        "by_opponent": by_opponent,
        "orchard_signature": {
            "definition": "starter has at least three consecutive HARVEST/DROP two-turn cycles",
            "games": len(orchard_rows),
            "sustained_definition": "starter has at least ten consecutive cycles",
            "sustained_games": sum(
                row["longest_harvest_drop_run"] >= 10 for row in orchard_rows
            ),
            "rows": orchard_rows,
        },
        "target_rows": target_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload["target_loss_patterns"], indent=1))
    print(f"orchard signatures: {len(orchard_rows)}/{len(rows)}")
    print(f"saved {args.output}")


if __name__ == "__main__":
    main()
