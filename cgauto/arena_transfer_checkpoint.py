#!/usr/bin/env python3
"""Capture a complete, submission-scoped arena transfer checkpoint.

The current battle endpoint is replaced whenever a new source is submitted.  This
reader therefore requires both the expected agent and submission identifiers and
rejects mixed or unexpected finished battles instead of silently comparing them.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from cgauto import battle_taxonomy as arena
except ModuleNotFoundError:  # direct ``python cgauto/<script>.py`` invocation
    import battle_taxonomy as arena


USER_ID = 1302251
RUNTIME_MARKERS = (
    "timeout",
    "time limit",
    "time-limit",
    "runtime error",
    "runtime-error",
    "exceeded",
    "invalid",
)


def target_player(battle: dict[str, Any], agent_id: int) -> dict[str, Any] | None:
    return next(
        (
            player
            for player in battle.get("players", [])
            if player.get("playerAgentId") == agent_id
            and player.get("userId") == USER_ID
        ),
        None,
    )


def parse_game(game: dict[str, Any], agent_id: int) -> dict[str, Any]:
    agents = game.get("agents") or []
    target = next((agent for agent in agents if agent.get("agentId") == agent_id), None)
    if target is None:
        raise ValueError(f"target agent {agent_id} absent from result")

    index = target.get("index")
    scores = game.get("scores") or []
    if not isinstance(index, int) or index < 0 or index >= len(scores):
        raise ValueError("target result index is missing or outside scores")
    opponent_indexes = [candidate for candidate in range(len(scores)) if candidate != index]
    if len(opponent_indexes) != 1:
        raise ValueError(f"expected one opponent, found {len(opponent_indexes)}")
    opponent_index = opponent_indexes[0]
    opponent = next(
        (agent for agent in agents if agent.get("index") == opponent_index), {}
    )

    target_frame_lines = []
    for frame in game.get("frames") or []:
        for field in ("summary", "gameInformation"):
            for line in str(frame.get(field) or "").splitlines():
                if f"${index}" in line:
                    target_frame_lines.append(line)
    target_tooltips = []
    for raw_tooltip in game.get("tooltips") or []:
        try:
            tooltip = json.loads(raw_tooltip) if isinstance(raw_tooltip, str) else raw_tooltip
        except json.JSONDecodeError:
            tooltip = raw_tooltip
        text = json.dumps(tooltip, sort_keys=True, default=str)
        if f"${index}" in text:
            target_tooltips.append(tooltip)
    audit_fields = {
        "target_agent": target,
        "target_frame_lines": target_frame_lines,
        "target_tooltips": target_tooltips,
    }
    audit_text = json.dumps(audit_fields, sort_keys=True, default=str).lower()
    markers = sorted({marker for marker in RUNTIME_MARKERS if marker in audit_text})
    valid = target.get("valid") is True
    margin = float(scores[index]) - float(scores[opponent_index])
    ranks = game.get("ranks") or []
    rank = ranks[index] if index < len(ranks) else None
    opponent_codingamer = opponent.get("codingamer") or {}
    return {
        "game_id": game.get("gameId"),
        "opponent": opponent_codingamer.get("pseudo"),
        "opponent_agent_id": opponent.get("agentId"),
        "our_score": float(scores[index]),
        "opponent_score": float(scores[opponent_index]),
        "margin": margin,
        "rank": rank,
        "valid": valid,
        "runtime_markers": markers,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    margins = [row["margin"] for row in rows]
    catastrophes = [margin for margin in margins if margin <= -100]
    negative_margins = [margin for margin in margins if margin < 0]
    validity_signals = [
        {
            "game_id": row["game_id"],
            "valid": row["valid"],
            "runtime_markers": row["runtime_markers"],
        }
        for row in rows
        if not row["valid"] or row["runtime_markers"]
    ]
    return {
        "games": len(rows),
        "wins": sum(margin > 0 for margin in margins),
        "ties": sum(margin == 0 for margin in margins),
        "losses": sum(margin < 0 for margin in margins),
        "mean_margin": sum(margins) / len(margins) if margins else None,
        "catastrophic_losses": len(catastrophes),
        "catastrophic_rate": len(catastrophes) / len(rows) if rows else None,
        "negative_margin_mass": sum(-margin for margin in negative_margins),
        "validity_runtime_signals": validity_signals,
    }


def capture(agent_id: int, submission_id: int, role: str) -> dict[str, Any]:
    battles = arena.call(
        "gamesPlayersRanking/findLastBattlesByTestSessionHandle", [arena.TSH, None]
    )
    room = arena.call(
        "Leaderboards/getUserArenaDivisionRoomRankingByTestSessionHandle",
        [arena.TSH, USER_ID],
    )
    leaderboard = arena.call(
        "Leaderboards/getFilteredPuzzleLeaderboard",
        [arena.PID, arena.TSH, "global", {"active": False, "column": "", "filter": ""}],
    )
    filtered = next(
        (
            user
            for user in leaderboard.get("users", [])
            if (user.get("codingamer") or {}).get("userId") == USER_ID
        ),
        {},
    )
    observed_at = datetime.now(timezone.utc).isoformat()
    expected = []
    unexpected = []
    for battle in battles:
        player = target_player(battle, agent_id)
        if player is None or player.get("submissionId") != submission_id:
            unexpected.append(
                {
                    "game_id": battle.get("gameId"),
                    "done": battle.get("done"),
                    "players": battle.get("players"),
                }
            )
            continue
        expected.append(battle)

    rows = []
    fetch_failures = []
    finished = [battle for battle in expected if battle.get("done")]
    for number, battle in enumerate(finished, 1):
        game_id = battle.get("gameId")
        try:
            game = arena.call("gameResult/findByGameId", [game_id, None])
            rows.append(parse_game(game, agent_id))
        except Exception as error:  # noqa: BLE001 - preserve the complete audit
            fetch_failures.append(
                {"game_id": game_id, "error": f"{type(error).__name__}: {error}"}
            )
        if number % 20 == 0 or number == len(finished):
            print(f"fetched {number}/{len(finished)} finished results", flush=True)

    payload = {
        "schema": 1,
        "observed_at": observed_at,
        "result_audit_completed_at": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "agent_id": agent_id,
        "submission_id": submission_id,
        "arena": {
            "agent_id": room.get("agentId"),
            "rank": room.get("rank"),
            "total": room.get("total"),
            "score": room.get("score"),
            "division_index": (room.get("league") or {}).get("divisionIndex"),
        },
        "filtered_ladder": {
            "agent_id": filtered.get("agentId"),
            "rank": filtered.get("localRank"),
            "score": filtered.get("score"),
            "division_index": (filtered.get("league") or {}).get("divisionIndex"),
        },
        "battle_rows_listed": len(battles),
        "matching_rows": len(expected),
        "matching_finished": len(finished),
        "matching_pending": len(expected) - len(finished),
        "unexpected_rows": unexpected,
        "parsed_results": len(rows),
        "fetch_failures": fetch_failures,
        "summary": summarize(rows),
        "rows": rows,
    }
    payload["identity_clean"] = bool(
        room.get("agentId") == agent_id
        and filtered.get("agentId") == agent_id
        and not unexpected
        and len(rows) == len(finished)
        and not fetch_failures
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--submission-id", type=int, required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = capture(args.agent_id, args.submission_id, args.role)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=1) + "\n")
    summary = payload["summary"]
    print(
        f"{args.role}: agent={args.agent_id} submission={args.submission_id} "
        f"games={payload['matching_finished']} parsed={payload['parsed_results']} "
        f"pending={payload['matching_pending']} score={payload['arena']['score']} "
        f"rank={payload['arena']['rank']}/{payload['arena']['total']} "
        f"catastrophic={summary['catastrophic_losses']} "
        f"({summary['catastrophic_rate'] or 0:.1%}) "
        f"negative_mass={summary['negative_margin_mass']:.0f} "
        f"signals={len(summary['validity_runtime_signals'])} "
        f"identity_clean={payload['identity_clean']}"
    )
    if args.output:
        print(f"saved {args.output}")
    return 0 if payload["identity_clean"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
