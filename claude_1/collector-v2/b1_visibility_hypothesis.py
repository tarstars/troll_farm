#!/usr/bin/env python3
"""B1 follow-up 3 — does anonymous replay availability track participant battle windows?

The bisect (`b1-boundary-bisect-2026-08-11.json`) showed availability among unlisted games
is RAGGED, not a time horizon: adjacent ids interleave (895033310 fails, 895033321 resolves,
895033338 fails, 895033352 resolves), and the same id gives the same answer across runs, so
it is a stable per-game property. Age is therefore not the mechanism.

Hypothesis H: a replay is anonymously readable iff at least ONE of its two participants
still has that game in their `findLastBattlesByAgentId` window. The earlier sweep only
checked membership in one agent's window, which is why unlisted-and-resolving games looked
anomalous — the other participant's window was never consulted.

Test: take games measured as resolving and as failing, read their participant agent ids
from this checkout's cached bodies (no network needed for that), fetch each participant's
current battle window, and check membership. H predicts:

  resolving game  → present in at least one participant's window
  failing game    → present in neither

A single counterexample on either side falsifies H, and the script reports it as such
rather than scoring a majority.

Read-only; one JSON evidence record at `--out`.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from data.scripts.collect_snapshot import (  # noqa: E402
    PublicClient,
    completed_battles,
    replay_shape,
    utc_now,
)


def participants(games_dir: Path, game_id: int) -> list[int]:
    payload = json.loads((games_dir / f"{game_id}.json").read_text())
    return [int(a["agentId"]) for a in payload.get("agents", []) if a.get("agentId")]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B1 participant-window visibility test")
    ap.add_argument("--out", required=True)
    ap.add_argument("--games-dir", default=str(REPO / "data/raw/games"))
    ap.add_argument("--game", action="append", type=int, required=True,
                    help="game id to test (repeatable); availability is re-measured here")
    args = ap.parse_args(argv)

    games_dir = Path(args.games_dir)
    client = PublicClient()
    windows: dict[int, set[int]] = {}

    def window(agent_id: int) -> set[int]:
        if agent_id not in windows:
            payload = client.post(
                "gamesPlayersRanking/findLastBattlesByAgentId", [agent_id, None]).payload
            windows[agent_id] = {int(r["gameId"]) for r in completed_battles(payload)
                                 if r.get("gameId")}
        return windows[agent_id]

    cases = []
    for game_id in args.game:
        case = {"game_id": game_id, "participants": participants(games_dir, game_id)}
        try:
            response = client.post("gameResult/findByGameId", [game_id, None])
        except urllib.error.HTTPError as error:
            case.update(available=False, http_status=error.code,
                        error=error.read()[:160].decode(errors="replace"))
        except Exception as error:  # noqa: BLE001
            case.update(available=None, error=f"{type(error).__name__}: {error}"[:300])
        else:
            valid, frames, _ = replay_shape(response.payload)
            case.update(available=bool(valid), frames=frames)

        in_windows = {}
        for agent_id in case["participants"]:
            try:
                in_windows[str(agent_id)] = game_id in window(agent_id)
            except Exception as error:  # noqa: BLE001
                in_windows[str(agent_id)] = f"window unreadable: {type(error).__name__}"
        case["in_participant_window"] = in_windows
        truthy = [v for v in in_windows.values() if v is True]
        case["in_any_window"] = bool(truthy)
        if case["available"] is None:
            case["agrees_with_H"] = None
        else:
            case["agrees_with_H"] = (case["available"] == case["in_any_window"])
        cases.append(case)

    decided = [c for c in cases if c["agrees_with_H"] is not None]
    counterexamples = [c["game_id"] for c in decided if not c["agrees_with_H"]]
    if not decided:
        verdict = "UNDECIDED"
    elif counterexamples:
        verdict = "H_FALSIFIED"
    else:
        verdict = "H_CONSISTENT"

    report = {
        "check": "b1-participant-window-visibility",
        "task_id": "20260811-s3-collector-v2",
        "run_utc": utc_now(),
        "hypothesis": ("a replay is anonymously readable iff at least one participant's "
                       "findLastBattlesByAgentId window still contains it"),
        "cases": cases,
        "cases_decided": len(decided),
        "counterexamples": counterexamples,
        "verdict": verdict,
        "note": ("H_CONSISTENT is agreement on this sample, not proof of mechanism; the "
                 "platform's actual retention rule is not observable from here."),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "cases_decided": len(decided),
                      "counterexamples": counterexamples,
                      "summary": [{"game": c["game_id"], "available": c["available"],
                                   "in_any_window": c["in_any_window"]} for c in cases]},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
