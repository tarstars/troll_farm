#!/usr/bin/env python3
"""Census successful training architectures and macro behavior in top replays."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_state import DiffDecoder, view_payload  # noqa: E402

LIVE_AGENT_ID = 6553250


def successful_trains_from_replay(path: Path) -> dict[int, list[list]]:
    """Read new-unit records directly from visual diffs, excluding starting units."""

    replay = json.loads(path.read_text())
    result = {0: [], 1: []}
    resolved_turn = 0
    for frame in replay["frames"][1:]:
        if not frame.get("keyframe"):
            continue
        payload = view_payload(frame.get("view") or "")
        if payload is None:
            continue
        resolved_turn += 1
        for raw in payload.get("diff", "").split(";"):
            fields = raw.strip().split()
            if len(fields) >= 3 and fields[1] == "W":
                unit = DiffDecoder._new_unit(fields[2])
                result[unit["player"]].append(
                    [
                        resolved_turn,
                        [unit["ms"], unit["cc"], unit["hp"], unit["chop"]],
                    ]
                )
    return result


def role_of(spec) -> str:
    ms, cc, hp, chop = spec
    if chop >= 2 and hp == 0:
        return "wood_specialist"
    if chop >= 2 and hp > 0:
        return "hybrid_chopper"
    if hp >= 2 and chop <= 1:
        return "harvest_specialist"
    if cc >= 3 and hp <= 1 and chop <= 1:
        return "carrier"
    return "generalist"


def spec_label(spec) -> str:
    return "/".join(str(value) for value in spec)


def occurrence(game, player, successful_trains, rank_by_agent) -> dict:
    index = player["index"]
    per_player = game["per_player"][str(index)]
    effects = per_player.get("effects", {})
    commands = per_player.get("commands_summary", {})
    planted = per_player.get("planted_ok", {})
    trains = successful_trains.get(index, [])
    opponent_score = game["scores"][1 - index]
    return {
        "game_id": game["gameId"],
        "agent_id": player["agentId"],
        "name": player["name"],
        "leaderboard_rank": rank_by_agent.get(player["agentId"]),
        "seat": index,
        "turns": game["n_turns"],
        "score": game["scores"][index],
        "opponent_score": opponent_score,
        "margin": game["scores"][index] - opponent_score,
        "won": game["scores"][index] > opponent_score,
        "successful_trains": trains,
        "successful_train_count": len(trains),
        "final_worker_count": 1 + len(trains),
        "attempted_trains": per_player.get("trains", []),
        "command_counts": commands,
        "planted_ok": planted,
        "collected_wood": effects.get("collected_WOOD", 0),
        "chops_landed": effects.get("chops_landed", 0),
        "final_wood": per_player.get("final_inv", [0] * 6)[5],
    }


def mean_or_none(values):
    values = list(values)
    return statistics.mean(values) if values else None


def summarize_occurrences(rows: list[dict]) -> dict:
    train_counts = Counter(row["successful_train_count"] for row in rows)
    worker_counts = Counter(row["final_worker_count"] for row in rows)
    all_specs = Counter()
    all_roles = Counter()
    role_presence = Counter()
    role_agents: dict[str, set[int]] = {}
    ordinal_specs: dict[int, Counter] = {}
    sequences = Counter()
    command_totals = Counter()
    planted_totals = Counter()
    first_turns = []
    for row in rows:
        specs = [train[1] for train in row["successful_trains"]]
        sequences[" -> ".join(spec_label(spec) for spec in specs) or "none"] += 1
        roles_seen = set()
        if row["successful_trains"]:
            first_turns.append(row["successful_trains"][0][0])
        for ordinal, (_, spec) in enumerate(row["successful_trains"], 1):
            label = spec_label(spec)
            role = role_of(spec)
            all_specs[label] += 1
            all_roles[role] += 1
            roles_seen.add(role)
            role_agents.setdefault(role, set()).add(row["agent_id"])
            ordinal_specs.setdefault(ordinal, Counter())[label] += 1
        role_presence.update(roles_seen)
        command_totals.update(row["command_counts"])
        planted_totals.update(row["planted_ok"])
    total_turns = sum(row["turns"] for row in rows)
    appearances = len(rows)
    return {
        "appearances": appearances,
        "distinct_agents": len({row["agent_id"] for row in rows}),
        "agent_ids": sorted({row["agent_id"] for row in rows}),
        "successful_train_count_distribution": dict(sorted(train_counts.items())),
        "final_worker_count_distribution": dict(sorted(worker_counts.items())),
        "mean_successful_trains": mean_or_none(
            row["successful_train_count"] for row in rows
        ),
        "median_first_train_turn": statistics.median(first_turns) if first_turns else None,
        "successful_specs": dict(all_specs.most_common()),
        "successful_roles": dict(all_roles.most_common()),
        "role_appearance_rates": {
            role: count / appearances if appearances else None
            for role, count in sorted(role_presence.items())
        },
        "role_distinct_agent_support": {
            role: len(agents) for role, agents in sorted(role_agents.items())
        },
        "ordinal_specs": {
            str(ordinal): dict(counts.most_common())
            for ordinal, counts in sorted(ordinal_specs.items())
        },
        "training_sequences": dict(sequences.most_common(15)),
        "commands_per_100_turns": {
            command: count * 100 / total_turns if total_turns else None
            for command, count in sorted(command_totals.items())
        },
        "mean_planted_per_game": {
            kind: count / appearances if appearances else None
            for kind, count in sorted(planted_totals.items())
        },
        "mean_collected_wood": mean_or_none(row["collected_wood"] for row in rows),
        "mean_final_wood": mean_or_none(row["final_wood"] for row in rows),
        "mean_score": mean_or_none(row["score"] for row in rows),
        "mean_margin": mean_or_none(row["margin"] for row in rows),
        "win_rate": mean_or_none(float(row["won"]) for row in rows),
    }


def macro_role_candidates(top: dict, live: dict) -> list[dict]:
    candidates = []
    roles = set(top["role_appearance_rates"]) | set(live["role_appearance_rates"])
    for role in sorted(roles):
        top_rate = top["role_appearance_rates"].get(role, 0.0)
        live_rate = live["role_appearance_rates"].get(role, 0.0)
        support = top["role_distinct_agent_support"].get(role, 0)
        passed = top_rate >= 0.25 and support >= 3 and live_rate <= 0.10
        candidates.append(
            {
                "role": role,
                "top5_appearance_rate": top_rate,
                "top5_distinct_agent_support": support,
                "live_appearance_rate": live_rate,
                "rate_gap": top_rate - live_rate,
                "stable_and_absent_gate": passed,
            }
        )
    return sorted(
        candidates,
        key=lambda row: (
            row["stable_and_absent_gate"],
            row["rate_gap"],
            row["top5_distinct_agent_support"],
        ),
        reverse=True,
    )


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/top-player-macro-census-2026-07-16.json",
    )
    args = parser.parse_args()
    leaderboard = json.loads((REPO / "data/raw/leaderboard.json").read_text())["users"]
    legend = [row for row in leaderboard if row.get("league", {}).get("divisionIndex") == 5]
    top20 = legend[:20]
    top5_ids = {row["agentId"] for row in legend[:5]}
    top20_ids = {row["agentId"] for row in top20}
    selected_ids = top20_ids | {LIVE_AGENT_ID}
    rank_by_agent = {row["agentId"]: row["rank"] for row in leaderboard}
    profile_by_agent = {
        row["agentId"]: {"name": row["pseudo"], "rank": row["rank"]}
        for row in leaderboard
        if row["agentId"] in selected_ids
    }

    rows = []
    missing_replays = []
    for line in (REPO / "data/processed/games.jsonl").read_text().splitlines():
        game = json.loads(line)
        selected_players = [
            player for player in game["players"] if player.get("agentId") in selected_ids
        ]
        if not selected_players:
            continue
        replay_path = REPO / f"data/raw/games/{game['gameId']}.json"
        if replay_path.exists():
            successful = successful_trains_from_replay(replay_path)
        else:
            missing_replays.append(game["gameId"])
            successful = {0: [], 1: []}
        rows.extend(
            occurrence(game, player, successful, rank_by_agent)
            for player in selected_players
        )

    cohorts = {
        "top5": summarize_occurrences(
            [row for row in rows if row["agent_id"] in top5_ids]
        ),
        "top20": summarize_occurrences(
            [row for row in rows if row["agent_id"] in top20_ids]
        ),
        "live": summarize_occurrences(
            [row for row in rows if row["agent_id"] == LIVE_AGENT_ID]
        ),
    }
    individual = {
        str(agent_id): {
            **profile,
            "summary": summarize_occurrences(
                [row for row in rows if row["agent_id"] == agent_id]
            ),
        }
        for agent_id, profile in sorted(
            profile_by_agent.items(), key=lambda item: item[1]["rank"]
        )
    }
    candidates = macro_role_candidates(cohorts["top5"], cohorts["live"])
    payload = {
        "schema": 1,
        "scope": "collected replay corpus; successful TRAINs decoded from new-unit diffs",
        "leaderboard_snapshot_agents": len(leaderboard),
        "selected_top20": top20,
        "replay_occurrences": len(rows),
        "missing_replays": sorted(set(missing_replays)),
        "cohorts": cohorts,
        "individual": individual,
        "macro_role_candidates": candidates,
        "stable_absent_roles": [
            row["role"] for row in candidates if row["stable_and_absent_gate"]
        ],
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps({
        "occurrences": len(rows),
        "top5": cohorts["top5"],
        "live": cohorts["live"],
        "stable_absent_roles": payload["stable_absent_roles"],
    }, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
