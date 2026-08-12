#!/usr/bin/env python3
"""Collector v2 — fetch, pack and upload one day of public games (B4).

Task `20260811-s3-collector-v2`. Runs unattended from a systemd timer at 05:47 UTC, clear of
`project_host`'s collection cron so the platform is not double-loaded. That cron fires at
**02:17 UTC**, not the 05:17 every document (including earlier versions of this one) claimed —
its crontab reads `17 5` on a Europe/Moscow machine. Measured by `local_claude_1` 2026-08-12.

Shape of a run:

  discover  leaderboard -> battle lists for a cohort of agents -> candidate game ids
  fetch     every unseen candidate, IMMEDIATELY (see below), into a staging directory
  pack      `packer.pack_day` over the staging directory — deterministic bytes
  upload    pack + manifest under `games/raw/daily/` and `games/manifest/`
  cursor    atomically record what was collected, so the next run knows what is new

**Fetch happens on discovery, in the same run, and a fetch failure is a real error.** B1
measured that a replay is anonymously readable only while a participant's battle window still
holds it: 5 of 8 ids sampled from an older local cache no longer resolve at all. A game not
fetched today is not "delayed", it is lost, so nothing here defers a fetch to a later run.

**Every upload is conditional (`If-None-Match: *`).** B2 measured that the service account's
grant blocks deletion but NOT overwriting — a plain PUT to an existing key succeeds. Append-only
is therefore a property of this code, not of the permissions. On a collision the run retries
under `daily-YYYY-MM-DD.rerun-N`, per the plan, rather than clobbering or failing outright.

**The cursor is written atomically** — temp file, fsync, `os.replace`, fsync of the directory —
because a torn cursor wedges every later run (control-plane self-review finding F8, which was
exactly this bug in the mirror).

Logging goes to stdout for journald, one structured line per phase, ending with an `exit=N`
marker so the cron-health guard pattern can see a truncated run.

Exit codes, chosen so an incomplete day never looks like a clean one:
  0  ran to completion, everything discovered was fetched and uploaded
  1  unexpected error — the run did not complete
  2  upload or post-upload verification failed; the cursor was NOT advanced, so the same
     games are retried on the next run
  3  the day is incomplete: at least one replay fetch failed. Permanent (HTTP 422, the game
     has left every participant's window) and transient failures both land here — the counts
     and the classification are in the log and the run record, but neither lets the run
     report success
  4  the S3 known-id set could not be built — the run stopped rather than re-fetch history
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback
import urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data.scripts.collect_snapshot import (  # noqa: E402
    PUZZLE,
    PublicClient,
    completed_battles,
    replay_shape,
)
import packer  # noqa: E402
from packer import pack_day  # noqa: E402
from s3client import S3Client, S3Error  # noqa: E402

DEFAULT_STATE = Path.home() / ".local/state/troll-farm"
DEFAULT_BUCKET = "troll-farm-data"
CURSOR_NAME = "collector-v2.json"
LEADERBOARD_BODY = [PUZZLE, None, "global", {"active": False, "column": "", "filter": ""}]
MAX_RERUN = 20


def log(event: str, **fields) -> None:
    """One structured line per phase. journald keeps these; humans can still read them."""
    payload = " ".join(f"{k}={json.dumps(v) if isinstance(v, (dict, list)) else v}"
                       for k, v in fields.items())
    print(f"collector-v2 {event} {payload}".rstrip(), flush=True)


def atomic_write_json(path: Path, value: object) -> None:
    """Write JSON so that a crash mid-write cannot leave a half-file behind.

    Control-plane self-review F8: a non-atomic cursor write corrupted the mirror's state and
    wedged every subsequent run. The directory fsync matters as much as the file one — without
    it the rename itself can be lost on power failure.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    data = json.dumps(value, indent=2, sort_keys=True) + "\n"
    with open(temporary, "w") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


class Cursor:
    """What this collector has already collected.

    `seen_game_ids` is bounded: only the highest `capacity` ids are kept. Game ids increase
    over time and battle windows only expose recent games, so older entries cannot be
    re-offered — but the bound IS a cap, so a run that drops entries says so in its log
    rather than trimming silently.
    """

    def __init__(self, path: Path, capacity: int = 200_000):
        self.path = path
        self.capacity = capacity
        self.data = {"schema": "collector-v2-cursor/1", "seen_game_ids": [],
                     "runs": [], "last_run_utc": None}
        if path.exists():
            self.data = json.loads(path.read_text())
        self.seen = set(self.data.get("seen_game_ids", []))

    def unseen(self, candidates: list[int]) -> list[int]:
        return sorted(set(candidates) - self.seen)

    def record(self, *, run: dict, collected: list[int]) -> int:
        self.seen.update(collected)
        ordered = sorted(self.seen)
        dropped = 0
        if len(ordered) > self.capacity:
            dropped = len(ordered) - self.capacity
            ordered = ordered[-self.capacity:]
            self.seen = set(ordered)
        self.data["seen_game_ids"] = ordered
        self.data["last_run_utc"] = run["finished_utc"]
        self.data.setdefault("runs", []).append(run)
        self.data["runs"] = self.data["runs"][-90:]
        atomic_write_json(self.path, self.data)
        return dropped


class KnownIdsUnavailable(RuntimeError):
    """The S3 known-id set could not be built. Never degrade to an empty set.

    An empty known-set re-fetches the entire visible history — the exact defect this task
    exists to remove, wearing a different hat — so the run stops instead (binding design 4).
    """


def known_ids_from_s3(s3: S3Client) -> tuple[set[int], dict]:
    """Every game id already in S3, read from the manifests each run.

    Sources are `games/manifest/backfill-*.jsonl` (the coordinator's corpus upload) and
    `games/manifest/daily-*.jsonl` including `.rerun-N` (this collector's own prior runs).

    Rebuilt every run and deliberately NOT cached in the cursor (binding design 2): a stale
    cache under-fetches silently, which is far more expensive than re-reading ~2 MB.

    Membership is by game id only. A held-but-corrupt object still counts as held — the
    manifests carry `sha256` and `size` for a future integrity pass, and nothing here should
    be read as proving the stored copy is good.
    """
    try:
        rows = s3.list_objects("games/manifest/")
    except Exception as error:  # noqa: BLE001
        raise KnownIdsUnavailable(f"could not list manifests: {type(error).__name__}: {error}")

    keys = [row["key"] for row in rows
            if row["key"].endswith(".jsonl")
            and (Path(row["key"]).name.startswith("backfill-")
                 or Path(row["key"]).name.startswith("daily-"))]
    if not keys:
        raise KnownIdsUnavailable(
            "no backfill or daily manifests found under games/manifest/ — refusing to treat "
            "an empty bucket listing as 'we hold nothing'")

    known: set[int] = set()
    sources = {"backfill": 0, "daily": 0}
    for key in sorted(keys):
        try:
            body = s3.get_object(key).decode()
        except Exception as error:  # noqa: BLE001
            raise KnownIdsUnavailable(f"could not read {key}: {type(error).__name__}: {error}")
        before = len(known)
        for line in body.splitlines():
            if line.strip():
                known.add(int(json.loads(line)["game_id"]))
        bucket = "backfill" if Path(key).name.startswith("backfill-") else "daily"
        sources[bucket] += len(known) - before

    # These two are INCREMENTAL contributions in read order (backfill sorts before daily),
    # not membership counts: `new_ids_from_daily` is how many ids the daily manifests add
    # that the backfill did not already have. On 2026-08-11 that was 0, which is the whole
    # reason this task exists.
    return known, {"manifests": len(keys), "ids": len(known),
                   "new_ids_from_backfill": sources["backfill"],
                   "new_ids_from_daily": sources["daily"]}


def discover(client: PublicClient, *, cohort: int) -> tuple[list[int], list[dict]]:
    """Leaderboard -> battle lists -> candidate game ids. Returns (ids, failures)."""
    failures: list[dict] = []
    payload = client.post("Leaderboards/getFilteredPuzzleLeaderboard", LEADERBOARD_BODY).payload
    users = payload.get("users") if isinstance(payload, dict) else None
    if not isinstance(users, list) or not users:
        raise RuntimeError("leaderboard response carried no users list")

    agent_ids: list[int] = []
    for user in users[:cohort]:
        agent_id = user.get("agentId") or (user.get("agent") or {}).get("agentId")
        if agent_id:
            agent_ids.append(int(agent_id))

    candidates: set[int] = set()
    for agent_id in agent_ids:
        try:
            rows = completed_battles(
                client.post("gamesPlayersRanking/findLastBattlesByAgentId",
                            [agent_id, None]).payload)
        except Exception as error:  # noqa: BLE001 — one bad agent must not lose the cohort
            failures.append({"stage": "battle_list", "agent_id": agent_id,
                             "error": f"{type(error).__name__}: {error}"[:300]})
            continue
        candidates.update(int(row["gameId"]) for row in rows if row.get("gameId"))
    return sorted(candidates), failures


def fetch(client: PublicClient, game_ids: list[int], staging: Path) -> tuple[list[int], list[dict]]:
    """Fetch each replay now. A failure is reported, never deferred — see module docstring."""
    staging.mkdir(parents=True, exist_ok=True)
    collected: list[int] = []
    failures: list[dict] = []
    for game_id in game_ids:
        try:
            response = client.post("gameResult/findByGameId", [game_id, None])
            valid, frames, error = replay_shape(response.payload)
            if not valid:
                raise ValueError(f"replay shape invalid: {error}")
        except urllib.error.HTTPError as error:
            failures.append({"stage": "replay", "game_id": game_id,
                             "http_status": error.code, "permanent": error.code == 422,
                             "error": error.read()[:160].decode(errors="replace")})
            continue
        except Exception as error:  # noqa: BLE001
            failures.append({"stage": "replay", "game_id": game_id,
                             "error": f"{type(error).__name__}: {error}"[:300]})
            continue
        (staging / f"{game_id}.json").write_bytes(response.raw)
        collected.append(game_id)
    return collected, failures


def upload_day(s3: S3Client, pack, *, date: str, dry_run: bool) -> dict:
    """Upload pack + manifest conditionally, escalating to `.rerun-N` on collision."""
    from packer import manifest_key_for, pack_key_for

    for rerun in range(0, MAX_RERUN + 1):
        pack_key = pack_key_for(date, rerun)
        manifest_key = manifest_key_for(date, rerun)
        if dry_run:
            return {"uploaded": False, "dry_run": True, "pack_key": pack_key,
                    "manifest_key": manifest_key, "rerun": rerun}
        try:
            # Content type follows the codec actually in use; hard-coding gzip mislabels
            # every object the moment `zstandard` is installed (found by codex_1 in review).
            put_pack = s3.put_object(pack_key, pack.pack_bytes,
                                     content_type=packer.CONTENT_TYPE, if_none_match=True)
            put_manifest = s3.put_object(manifest_key, pack.manifest_text.encode(),
                                         content_type="application/x-ndjson",
                                         if_none_match=True)
        except S3Error as error:
            if error.code in {"PreconditionFailed"} or error.status == 412:
                log("upload.collision", key=pack_key, rerun=rerun)
                continue
            raise
        return {"uploaded": True, "rerun": rerun, "pack_key": pack_key,
                "manifest_key": manifest_key, "pack_etag": put_pack.get("etag"),
                "manifest_etag": put_manifest.get("etag"),
                "pack_sha256": pack.pack_sha256, "manifest_sha256": pack.manifest_sha256}
    raise RuntimeError(f"{MAX_RERUN} rerun keys for {date} are all taken — refusing to guess")


def verify_upload(s3: S3Client, pack, result: dict) -> dict:
    """Download what was just written and re-hash it. An upload nobody checked is a hope."""
    body = s3.get_object(result["pack_key"])
    manifest = s3.get_object(result["manifest_key"])
    return {
        "pack_bytes_match": body == pack.pack_bytes,
        "pack_sha256_match": __import__("hashlib").sha256(body).hexdigest() == pack.pack_sha256,
        "manifest_match": manifest.decode() == pack.manifest_text,
    }


def prune_staging(staging: Path) -> dict:
    """Delete a day's staged replays. Only ever called AFTER the uploaded pack has been
    downloaded and re-hashed, so the bytes exist in the bucket before they leave this disk.

    This exists because the VM's root filesystem is 94% full (1.3 GB free at B4 time) and a
    day's staging is ~90 MB — unattended, unpruned, the service would fill the disk inside a
    fortnight and take coordd down with it. Staging is this service's own scratch: the
    plan's "nothing is deleted" rule is about the corpus and the cold archive, neither of
    which is touched here.
    """
    files = sorted(staging.glob("*.json"))
    freed = sum(path.stat().st_size for path in files)
    for path in files:
        path.unlink()
    try:
        staging.rmdir()
    except OSError:
        pass  # a non-empty or already-removed directory is not an error worth failing a run
    return {"files": len(files), "bytes": freed}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="collector v2 — one run")
    ap.add_argument("--state-dir", default=str(DEFAULT_STATE))
    ap.add_argument("--bucket", default=DEFAULT_BUCKET)
    ap.add_argument("--cohort", type=int, default=50,
                    help="how many leaderboard agents to read battle windows for")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to today (UTC)")
    ap.add_argument("--max-games", type=int, default=0,
                    help="0 = no limit; any other value is a cap and is logged as one")
    ap.add_argument("--dry-run", action="store_true",
                    help="discover, fetch and pack, but upload nothing")
    ap.add_argument("--prune-staging", action="store_true",
                    help="delete the day's staged replays once the upload is verified")
    ap.add_argument("--report", default=None, help="write a JSON run record here too")
    args = ap.parse_args(argv)

    started = time.time()
    started_utc = dt.datetime.now(dt.timezone.utc)
    date = args.date or started_utc.strftime("%Y-%m-%d")
    state = Path(args.state_dir)
    staging = state / "staging" / date
    cursor = Cursor(state / CURSOR_NAME)

    run: dict = {"started_utc": started_utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "date": date,
                 "dry_run": args.dry_run}
    exit_code = 0
    try:
        client = PublicClient()
        log("start", date=date, cohort=args.cohort, dry_run=args.dry_run,
            state_dir=str(state))

        # The known-id set is built BEFORE discovery costs anything, so a bucket problem stops
        # the run before it touches the platform at all.
        s3 = S3Client(args.bucket)
        known, known_stats = known_ids_from_s3(s3)
        log("known_ids", **known_stats)

        candidates, discover_failures = discover(client, cohort=args.cohort)
        # Skip BEFORE fetching (binding design 3): the budget is the scarce thing, so
        # already-held games must never reach the fetch loop. The cursor is a local
        # second opinion; S3 membership is what "we already have it" means.
        already_held = [gid for gid in candidates if gid in known]
        wanted = [gid for gid in cursor.unseen(candidates) if gid not in known]
        capped = 0
        if args.max_games and len(wanted) > args.max_games:
            capped = len(wanted) - args.max_games
            # Oldest-first (binding design 5): games leave participants' windows from the far
            # end, so the oldest un-held candidate is nearest to expiry and most urgent.
            wanted = wanted[:args.max_games]
            log("discover.capped", requested=args.max_games, dropped=capped)
        log("discover", candidates=len(candidates), already_held=len(already_held),
            unseen=len(wanted), battle_list_failures=len(discover_failures))

        if not wanted:
            # Binding design 6: nothing new is a success and must not read as a broken run.
            # No early return — an empty `wanted` flows through the ordinary path, which
            # already fetches nothing, packs nothing and uploads nothing. A second exit path
            # here would only duplicate that (and did: it recorded the run twice).
            log("fetch", fetched=0, reason="every discovered game is already in S3")

        collected, fetch_failures = fetch(client, wanted, staging)
        permanent = [f for f in fetch_failures if f.get("permanent")]
        log("fetch", collected=len(collected), failed=len(fetch_failures),
            permanently_gone=len(permanent))

        files = sorted(staging.glob("*.json"), key=lambda p: int(p.stem))
        pack = pack_day(date, files)
        log("pack", games=len(pack.game_ids), bytes=len(pack.pack_bytes),
            sha256=pack.pack_sha256, codec=pack.codec)

        upload: dict = {}
        verification: dict = {}
        if pack.game_ids:
            # An upload failure is handled here rather than thrown, so that the cursor guard
            # below is a live check with a test that can reach it — and so the run report
            # carries what went wrong instead of only a traceback.
            try:
                upload = upload_day(s3, pack, date=date, dry_run=args.dry_run)
            except S3Error as error:
                upload = {"uploaded": False, "error": f"{error.code}: {error.s3_message}",
                          "http_status": error.status}
                log("upload.failed", code=error.code, status=error.status)
                exit_code = 2
            else:
                log("upload", **{k: v for k, v in upload.items() if v is not None})
                if upload.get("uploaded"):
                    verification = verify_upload(s3, pack, upload)
                    log("verify", **verification)
                    if not all(verification.values()):
                        upload["uploaded"] = False
                        upload["error"] = f"verification failed: {verification}"
                        log("verify.failed", **verification)
                        exit_code = 2
        else:
            log("upload.skipped", reason="no games collected this run")

        run.update({
            "candidates": len(candidates), "already_held": len(already_held),
            "known_ids": known_stats, "unseen": len(wanted),
            "collected": len(collected), "capped_out": capped,
            "discover_failures": discover_failures,
            "fetch_failures": fetch_failures,
            "permanently_gone": len(permanent),
            "pack_sha256": pack.pack_sha256 if pack.game_ids else None,
            "upload": upload, "verification": verification,
        })
        if args.prune_staging and upload.get("uploaded") and verification and \
                all(verification.values()):
            freed = prune_staging(staging)
            log("staging.pruned", **freed)

        # Only games that are actually in an uploaded (or dry-run packed) object are recorded
        # as seen; otherwise a failed upload would make them invisible to every later run.
        # A run with nothing to upload still records itself — collected is empty, so nothing
        # is marked seen, but "the collector ran and found nothing new" is worth having in
        # the run history rather than looking like a run that never happened.
        if upload.get("uploaded") or args.dry_run or not pack.game_ids:
            run["finished_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            dropped = cursor.record(run=run, collected=collected)
            if dropped:
                log("cursor.trimmed", dropped=dropped, capacity=cursor.capacity)
            log("cursor", seen_total=len(cursor.seen), path=str(cursor.path))
        else:
            log("cursor.not_advanced", reason="nothing uploaded this run")

        if exit_code == 0 and fetch_failures:
            # EVERY replay-fetch failure makes the run nonzero, permanent ones included
            # (coordinator ruling `20260811T112547Z`: a same-day fetch failure is a real error
            # in the end marker, not a soft skip; finish the sweep, then exit nonzero with the
            # failure count). My first version gated this on `not permanent`, so an all-422 day
            # exited 0 — and worse, a MIXED day exited 0 too, because one permanent failure
            # masked every transient one beside it. Found by codex_1 in second review.
            # The permanent/transient distinction survives in the log and the run record, where
            # it informs; it no longer decides whether the run looks clean.
            exit_code = 3
    except KnownIdsUnavailable as error:
        # Distinct marker and exit code: proceeding with an empty known-set would re-fetch
        # everything, so this must never be mistaken for an ordinary failure.
        run["error"] = str(error)[:600]
        log("known_ids.failed", message=str(error)[:300])
        exit_code = 4
    except Exception as error:  # noqa: BLE001 — the exit marker must always be reached
        run["error"] = f"{type(error).__name__}: {error}"[:600]
        run["traceback"] = traceback.format_exc()[-1200:]
        log("error", type=type(error).__name__, message=str(error)[:300])
        exit_code = 1

    run.setdefault("finished_utc",
                   dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    run["seconds"] = round(time.time() - started, 1)
    run["exit"] = exit_code
    if args.report:
        atomic_write_json(Path(args.report), run)
    # The end marker the cron-health guard looks for. A run killed before this line has no
    # `exit=` line at all, which is exactly how a truncated run is detected.
    log("end", exit=exit_code, seconds=run["seconds"])
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
