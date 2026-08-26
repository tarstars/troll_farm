#!/usr/bin/env python3
"""Collect one submission's Arena games before the battle window evicts them.

WHY THIS EXISTS, AND WHY IT MUST BE RUN BEFORE THE NEXT SUBMISSION
------------------------------------------------------------------
`gamesPlayersRanking/findLastBattlesByTestSessionHandle` returns roughly the last 160
battles for the session -- a ROLLING WINDOW, not a history.  Submitting the next arm
fills that window with the new agent's games and the previous read's battles become
unreachable: the game ids can no longer be enumerated, so the replays can no longer be
fetched.  On 2026-08-23 a query for submission 41182039, made 47 minutes after the next
arm went up, returned zero rows.  See `docs/METHODS-LEDGER.md`,
`collect-before-you-resubmit`.

WHAT IT DOES NOT DO
-------------------
It does not sanitise.  Sanitising is `cgauto/export_agent_replays.py`'s job and that tool
already existed when this one was written; re-implementing it is how the coordinator
committed 149 replays carrying other players' account ids on 2026-08-23
(`docs/METHODS-LEDGER.md`, `shared-runners`).  This script fetches raw into a scratch
directory and hands off.  Raw output is deliberately written OUTSIDE the repo.

It does not write to `data/raw/games/`, which is hazard-listed and owned by the 02:17 UTC
collector (`coordination/multi-agent-protocol.md` section 7).

CREDENTIAL
----------
Reads the platform session from `project_host` only.  Peer agents have no credential, so
collection is the Arena controller's job and cannot be chartered away.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import cgauto.field_panel as fp  # noqa: E402
from cgauto.api_submit_once import SESSION_FILE  # noqa: E402

# `field_panel` resolves the session relative to its own checkout, which is wrong from a
# worktree.  Reuse the submitter's constant rather than writing a fourth copy of this path.
fp.SESSION = SESSION_FILE

BASE = "https://www.codingame.com/services/"


def call(service: str, payload) -> dict | list:
    request = urllib.request.Request(
        BASE + service,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Cookie": fp.cookie(),
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)


def battle_rows(agent_id: int, submission_id: int) -> list[dict]:
    listing = call("gamesPlayersRanking/findLastBattlesByTestSessionHandle", [fp.TSH, None])
    rows = [
        row
        for row in listing
        if row.get("done")
        and any(
            (player or {}).get("playerAgentId") == agent_id
            and (player or {}).get("submissionId") == submission_id
            for player in (row.get("players") or [])
        )
    ]
    print(f"window holds {len(listing)} battles; {len(rows)} belong to "
          f"agent {agent_id} / submission {submission_id}", flush=True)
    if not rows:
        raise SystemExit(
            "REFUSED: zero battles for that agent/submission. Either it has not played "
            "yet, or a later submission has already evicted it from the window -- in "
            "which case those games are gone and cannot be recovered by this route."
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--submission-id", type=int, required=True)
    parser.add_argument("--scratch", type=pathlib.Path, required=True,
                        help="raw fetch directory, OUTSIDE the repo")
    parser.add_argument("--output-dir", type=pathlib.Path, required=True,
                        help="where export_agent_replays.py writes the sanitised package")
    parser.add_argument("--observed-at-utc", required=True)
    parser.add_argument("--sleep", type=float, default=0.35)
    args = parser.parse_args()

    rows = battle_rows(args.agent_id, args.submission_id)
    raw_root = args.scratch / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)

    fetched = 0
    for row in rows:
        game_id = int(row["gameId"])
        destination = raw_root / f"{game_id}.json"
        if destination.exists():
            fetched += 1
            continue
        try:
            replay = call("gameResult/findByGameId", [game_id, None])
        except Exception as error:  # noqa: BLE001 - one bad replay must not lose the rest
            print(f"  skip {game_id}: {type(error).__name__}", flush=True)
            continue
        destination.write_text(json.dumps(replay), encoding="utf-8")
        fetched += 1
        if fetched % 25 == 0:
            print(f"  fetched {fetched}/{len(rows)}", flush=True)
        time.sleep(args.sleep)

    battle_list = args.scratch / "battles.json"
    battle_list.write_text(json.dumps(rows), encoding="utf-8")
    print(f"raw fetched: {fetched}/{len(rows)}", flush=True)

    # Sanitising is the existing tool's job.  Do not inline it here.
    completed = subprocess.run(
        [sys.executable, str(REPO / "cgauto" / "export_agent_replays.py"),
         "--agent-id", str(args.agent_id),
         "--submission-id", str(args.submission_id),
         "--battle-list", str(battle_list),
         "--raw-root", str(raw_root),
         "--output-dir", str(args.output_dir),
         "--observed-at-utc", args.observed_at_utc],
        cwd=REPO, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
