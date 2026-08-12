#!/usr/bin/env python3
"""B1 follow-up 2 — is the unlisted-game boundary a sharp cutoff or scattered?

The sweep (`b1-retention-sweep-2026-08-11.json`) found that among games NOT referenced by
any live battle window, the newest cached ids resolve and older ones return HTTP 422, while
listed games resolve at every age. Two mechanisms still fit:

  SHARP  — a single id/time cutoff among unlisted games (a retention GC with a horizon),
           with live-window membership extending retention past it.
  RAGGED — availability scattered across the id range (per-game visibility, not a horizon).

The distinction matters only for how the report states the cause, not for whether B4
proceeds; it is measured rather than assumed because "right finding, wrong reason" is the
failure mode this project pays most for.

Method: binary search the boundary over this checkout's `data/raw/games/` ids that are NOT
in the live battle window, then verify the claimed cutoff by probing the immediate
neighbours on both sides. A SHARP verdict requires every sampled id below the cutoff to
fail and every one above it to resolve — the verification probes are what can falsify it.

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


def resolves(client: PublicClient, game_id: int, log: list) -> bool:
    record = {"game_id": game_id}
    try:
        response = client.post("gameResult/findByGameId", [game_id, None])
    except urllib.error.HTTPError as error:
        record.update(status="http_error", http_status=error.code,
                      error=error.read()[:160].decode(errors="replace"))
        log.append(record)
        return False
    valid, frames, _ = replay_shape(response.payload)
    record.update(status="ok", replay_valid=valid, frames=frames)
    log.append(record)
    return bool(valid)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B1 unlisted-game boundary bisect")
    ap.add_argument("--out", required=True)
    ap.add_argument("--agent-id", type=int, default=6479768)
    ap.add_argument("--games-dir", default=str(REPO / "data/raw/games"))
    ap.add_argument("--neighbours", type=int, default=3,
                    help="ids to verify on each side of the claimed cutoff")
    args = ap.parse_args(argv)

    client = PublicClient()
    battles = completed_battles(
        client.post("gamesPlayersRanking/findLastBattlesByAgentId", [args.agent_id, None]).payload
    )
    listed = {int(row["gameId"]) for row in battles if row.get("gameId")}
    cached = sorted(int(p.stem) for p in Path(args.games_dir).glob("*.json") if p.stem.isdigit())
    unlisted = [gid for gid in cached if gid not in listed]
    if len(unlisted) < 4:
        print("not enough unlisted ids to bisect")
        return 2

    probes: list[dict] = []
    lo, hi = 0, len(unlisted) - 1
    lo_ok = resolves(client, unlisted[lo], probes)
    hi_ok = resolves(client, unlisted[hi], probes)
    verdict_note = None
    if lo_ok and hi_ok:
        verdict_note = "all sampled unlisted ids resolve — no boundary in this population"
    elif not lo_ok and not hi_ok:
        verdict_note = "no sampled unlisted id resolves — boundary lies above this population"
    else:
        # invariant: unlisted[lo] fails, unlisted[hi] resolves; shrink to adjacency
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if resolves(client, unlisted[mid], probes):
                hi = mid
            else:
                lo = mid

    cutoff_low, cutoff_high = unlisted[lo], unlisted[hi]
    verification = []
    if verdict_note is None:
        below = [gid for gid in unlisted if gid <= cutoff_low][-args.neighbours:]
        above = [gid for gid in unlisted if gid >= cutoff_high][: args.neighbours]
        for gid in below:
            verification.append({"game_id": gid, "side": "below_cutoff",
                                 "resolves": resolves(client, gid, probes)})
        for gid in above:
            verification.append({"game_id": gid, "side": "above_cutoff",
                                 "resolves": resolves(client, gid, probes)})

    consistent = all(not v["resolves"] for v in verification if v["side"] == "below_cutoff") and \
        all(v["resolves"] for v in verification if v["side"] == "above_cutoff")
    if verdict_note is not None:
        shape = "NO_BOUNDARY_IN_POPULATION"
    elif consistent:
        shape = "SHARP"
    else:
        shape = "RAGGED"

    report = {
        "check": "b1-unlisted-boundary-bisect",
        "task_id": "20260811-s3-collector-v2",
        "run_utc": utc_now(),
        "agent_id": args.agent_id,
        "unlisted_population": len(unlisted),
        "unlisted_range": [unlisted[0], unlisted[-1]],
        "cutoff_between": None if verdict_note else [cutoff_low, cutoff_high],
        "cutoff_note": verdict_note,
        "verification": verification,
        "verification_consistent": None if verdict_note else consistent,
        "shape": shape,
        "requests_issued": len(probes) + 1,
        "probes": probes,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("shape", "cutoff_between", "cutoff_note", "verification_consistent",
                       "requests_issued")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
