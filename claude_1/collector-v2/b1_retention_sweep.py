#!/usr/bin/env python3
"""B1 follow-up — is `gameResult/findByGameId` failure age-shaped or auth-shaped?

The first B1 run found the three read services all answer cookieless, but three game ids
already cached in `data/raw/games/` returned HTTP 422 `{"id":548,"message":"Game not found"}`.
Two explanations fit that single observation and they lead to opposite decisions:

  (a) RETENTION — the platform expires replay bodies after some age. Cookieless reads are
      fine; collector v2 simply has to fetch promptly, and the backfill corpus is
      irreplaceable. B4 proceeds.
  (b) AUTHORIZATION — anonymous callers can only read some subset (e.g. games still
      referenced by a live battle window), and a session cookie would widen it. B1's gate
      trips and the coordinator provisions a cookie.

They are distinguishable without ever holding a cookie: (a) predicts a MONOTONE boundary in
game id (ids are allocated increasing over time — every id above some threshold resolves,
every id below it 422s), and predicts that an OLD id still listed in a live battle window
fails too. (b) predicts failure tracks listing/visibility, not age — an old-but-listed id
would resolve.

So the sweep probes ids sampled across the whole observed range, tagging each as
`listed_live` (present in a battle list fetched this run) or `cached_only` (present in this
checkout's `data/raw/games/` and not in any list), and reports the boundary.

Read-only. Writes nothing under `data/raw/`; emits one JSON evidence record at `--out`.
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


def sample(values: list[int], count: int) -> list[int]:
    """Evenly spaced sample across a sorted list, endpoints always included."""
    if len(values) <= count:
        return list(values)
    step = (len(values) - 1) / (count - 1)
    picked = sorted({values[round(i * step)] for i in range(count)})
    return picked


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B1 retention-vs-authorization sweep")
    ap.add_argument("--out", required=True)
    ap.add_argument("--agent-id", type=int, default=6479768,
                    help="leaderboard agent whose battle list supplies live ids")
    ap.add_argument("--listed-samples", type=int, default=8)
    ap.add_argument("--cached-samples", type=int, default=8)
    ap.add_argument("--games-dir", default=str(REPO / "data/raw/games"))
    args = ap.parse_args(argv)

    client = PublicClient()
    battles = completed_battles(
        client.post("gamesPlayersRanking/findLastBattlesByAgentId", [args.agent_id, None]).payload
    )
    listed = sorted({int(row["gameId"]) for row in battles if row.get("gameId")})
    cached = sorted(int(p.stem) for p in Path(args.games_dir).glob("*.json") if p.stem.isdigit())
    cached_only = [gid for gid in cached if gid not in set(listed)]

    targets = [(gid, "listed_live") for gid in sample(listed, args.listed_samples)]
    targets += [(gid, "cached_only") for gid in sample(cached_only, args.cached_samples)]
    targets.sort()

    probes = []
    for game_id, origin in targets:
        record = {"game_id": game_id, "origin": origin}
        try:
            response = client.post("gameResult/findByGameId", [game_id, None])
        except urllib.error.HTTPError as error:
            body = error.read()[:200].decode(errors="replace")
            record.update(status="http_error", http_status=error.code, error=body)
        except Exception as error:  # noqa: BLE001
            record.update(status="error", error=f"{type(error).__name__}: {error}"[:300])
        else:
            valid, frames, shape_error = replay_shape(response.payload)
            record.update(status="ok", replay_valid=valid, frames=frames,
                          shape_error=shape_error, response_bytes=len(response.raw))
        probes.append(record)

    resolved = [p["game_id"] for p in probes if p["status"] == "ok"]
    failed = [p["game_id"] for p in probes if p["status"] != "ok"]
    monotone = bool(resolved) and bool(failed) and min(resolved) > max(failed)
    listed_failures = [p["game_id"] for p in probes
                       if p["origin"] == "listed_live" and p["status"] != "ok"]

    if not failed:
        shape = "NO_FAILURES"
    elif monotone and listed_failures:
        shape = "AGE_SHAPED"       # boundary is id/time, and being listed does not rescue
    elif monotone:
        shape = "AGE_SHAPED_UNCONFIRMED"  # clean boundary, but no old listed id was sampled
    else:
        shape = "NOT_AGE_SHAPED"   # failures interleave with successes — look at auth

    report = {
        "check": "b1-retention-vs-authorization",
        "task_id": "20260811-s3-collector-v2",
        "run_utc": utc_now(),
        "agent_id": args.agent_id,
        "listed_ids_count": len(listed),
        "listed_id_range": [listed[0], listed[-1]] if listed else None,
        "cached_only_count": len(cached_only),
        "cached_only_range": [cached_only[0], cached_only[-1]] if cached_only else None,
        "probes": probes,
        "resolved_count": len(resolved),
        "failed_count": len(failed),
        "lowest_resolved_id": min(resolved) if resolved else None,
        "highest_failed_id": max(failed) if failed else None,
        "boundary_monotone_in_game_id": monotone,
        "listed_but_failed": listed_failures,
        "shape": shape,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("shape", "resolved_count", "failed_count", "lowest_resolved_id",
                       "highest_failed_id", "listed_but_failed")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
