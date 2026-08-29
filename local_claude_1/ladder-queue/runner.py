#!/usr/bin/env python3
"""The ladder queue, unattended (owner 2026-08-28 05:5xZ: "I'm going to go offline for 8 hours
with this computer. So I propose to move ladder queue to VM. let's put three_heroes to the start
and other tasks later. I want to submit (a)").

One tick (run by cron on the VM every 5 minutes, in the checkout /home/tarstars/prj/troll_farm):

  * if nothing is on the ladder: submit the next pending item of `queue.json`
    (`cgauto/api_submit_once.py <file> --expected-sha256 <sha>`), record the submission id and
    time in `state.json`, commit;
  * if the item on the ladder is READ_AFTER_MIN minutes old: read the arena room (rank, score,
    agent id -- the number the site shows, `cgauto/cg_rank.py::arena_room`, plain urllib), then
    collect its games (`local_claude_1/narrate/collect_submission_games.py`) into
    `local_claude_1/ladder-queue/games-<submission id>/`; if the batch is not complete
    (fewer than GAMES_PER_BATCH games marked done in the battle index) and the item is younger than
    GIVE_UP_MIN minutes, wait for the next tick; otherwise accept what there is. Append the reading
    to `readings.jsonl`, move the item to `done`, commit, push -- and submit the next item in the
    same tick, so the ladder is never idle.
  * every commit is pushed to origin/main (fast-forward; on refusal `git pull --rebase` once and
    retry). The runner never touches anything outside `local_claude_1/ladder-queue/`.
  * a failed or ambiguous submission STOPS the queue (`state.json: halted`) -- nothing is
    resubmitted blindly; the log says why. A failed read/collect is retried on the next tick.

    python3 local_claude_1/ladder-queue/runner.py            # one tick
    python3 local_claude_1/ladder-queue/runner.py --status   # print the state, do nothing
"""
from __future__ import annotations

import datetime as dt
import fcntl
import json
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "cgauto"))

QUEUE = HERE / "queue.json"
STATE = HERE / "state.json"
READINGS = HERE / "readings.jsonl"
LOG = Path("/home/tarstars/ladder-queue-runner.log")   # outside the repo: a tracked log dirtied the checkout and broke `git pull --rebase` (06:24Z)
LOCK = Path("/home/tarstars/ladder-queue.lock")
SCRATCH = Path("/home/tarstars/ladder-queue-scratch")
READ_AFTER_MIN = 62
GIVE_UP_MIN = 110
GAMES_PER_BATCH = 160


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def stamp(t: dt.datetime | None = None) -> str:
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def log(msg: str) -> None:
    line = f"{stamp()} {msg}"
    print(line)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


def load(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def run(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)


def git_commit_push(message: str) -> None:
    run(["git", "add", "-A", str(HERE.relative_to(REPO))])
    r = run(["git", "commit", "-q", "-m", message])
    if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
        log(f"git commit failed: {(r.stdout + r.stderr)[-500:]}")
        return
    for attempt in (1, 2):
        r = run(["git", "push", "-q", "origin", "HEAD:main"], timeout=300)
        if r.returncode == 0:
            return
        log(f"git push refused (attempt {attempt}): {(r.stdout + r.stderr)[-300:]}")
        run(["git", "pull", "-q", "--rebase", "origin", "main"], timeout=300)
    log("git push FAILED twice; the commit stays local and the next tick retries")


def arena_room() -> dict | None:
    import cg_rank
    for _ in range(3):
        ar = cg_rank.arena_room()
        if ar and isinstance(ar, dict) and "rank" in ar:
            return ar
    return None


def submit(item: dict) -> dict:
    r = run([sys.executable, "cgauto/api_submit_once.py", item["file"],
             "--expected-sha256", item["sha256"]], timeout=300)
    text = (r.stdout + r.stderr).strip()
    result = None
    for line in reversed(text.splitlines()):
        if line.startswith("{"):
            try:
                result = json.loads(line)
                break
            except json.JSONDecodeError:
                pass
    if result is None:
        return {"accepted": False, "ambiguous": True, "raw": text[-800:]}
    return result


def collect(item_state: dict) -> tuple[Path | None, int, int]:
    """Collect the games; returns (package dir, games in package, games marked done)."""
    sid = item_state["submission_id"]
    out = HERE / f"games-{sid}"
    if out.exists():
        shutil.rmtree(out)
    scratch = SCRATCH / str(sid)
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    r = run([sys.executable, "local_claude_1/narrate/collect_submission_games.py",
             "--agent-id", str(item_state["agent_id"]), "--submission-id", str(sid),
             "--scratch", str(scratch), "--output-dir", str(out),
             "--observed-at-utc", stamp()], timeout=2400)
    tail = (r.stdout + r.stderr)[-600:]
    log(f"collector rc={r.returncode}: {tail.strip().splitlines()[-1] if tail.strip() else ''}")
    shutil.rmtree(scratch, ignore_errors=True)
    if r.returncode != 0 or not out.exists():
        return None, 0, 0
    manifest = load(out / "manifest.json", {})
    games = int(manifest.get("game_count", 0))
    index = load(out / manifest.get("battle_index", "missing"), [])
    done = sum(1 for b in index if isinstance(b, dict) and b.get("done"))
    return out, games, done


def next_pending(queue: dict, state: dict) -> dict | None:
    done_ids = {d["id"] for d in state.get("done", [])}
    for item in queue["items"]:
        if item["id"] not in done_ids and item["id"] != (state.get("current") or {}).get("id"):
            return item
    return None


def submit_next(queue: dict, state: dict) -> None:
    item = next_pending(queue, state)
    if item is None:
        log("queue empty: nothing more to submit; the last bot stays on the ladder")
        return
    log(f"submitting {item['id']}: {item['file']} ({item['sha256'][:8]})")
    result = submit(item)
    if result.get("accepted") and not result.get("ambiguous"):
        state["current"] = {"id": item["id"], "label": item["label"], "file": item["file"],
                            "sha256": item["sha256"], "submission_id": int(result["submission_id"]),
                            "submitted_at": stamp(), "agent_id": None, "early_looks": []}
        save(STATE, state)
        log(f"submitted {item['id']} as {result['submission_id']}")
        git_commit_push(f"ladder queue (VM): submitted {item['id']} as {result['submission_id']}")
    else:
        state["halted"] = {"at": stamp(), "item": item["id"], "result": result}
        save(STATE, state)
        log(f"SUBMISSION NOT ACCEPTED -- queue halted: {json.dumps(result)[:400]}")
        git_commit_push(f"ladder queue (VM): HALTED at {item['id']} (submission not accepted)")


def read_current(queue: dict, state: dict) -> None:
    cur = state["current"]
    age_min = (now() - parse(cur["submitted_at"])).total_seconds() / 60
    ar = arena_room()
    if ar is None:
        log("arena room unreadable this tick; retrying next tick")
        return
    if cur.get("agent_id") is None:
        cur["agent_id"] = ar.get("agentId")
    look = {"at": stamp(), "age_min": round(age_min, 1), "score": ar.get("score"),
            "rank": ar.get("rank"), "total": ar.get("total"), "agent_id": ar.get("agentId")}
    if age_min < READ_AFTER_MIN:
        cur.setdefault("early_looks", []).append(look)
        save(STATE, state)
        log(f"early look {cur['id']} at {age_min:.0f} min: {look['score']} rank {look['rank']}")
        return
    package, games, done = collect(cur)
    if package is None:
        log("collection failed; retrying next tick")
        return
    if done < GAMES_PER_BATCH and age_min < GIVE_UP_MIN:
        log(f"batch not complete ({done}/{GAMES_PER_BATCH} done, {games} in the window) at "
            f"{age_min:.0f} min; waiting for the next tick")
        return
    manifest = load(package / "manifest.json", {})
    reading = {
        "id": cur["id"], "label": cur["label"], "file": cur["file"], "sha256": cur["sha256"],
        "submission_id": cur["submission_id"], "agent_id": cur["agent_id"],
        "submitted_at": cur["submitted_at"], "read_at": stamp(), "age_min": round(age_min, 1),
        "score": ar.get("score"), "rank": ar.get("rank"), "total": ar.get("total"),
        "games_in_package": games, "games_done": done,
        "package": str(package.relative_to(REPO)),
        "package_sha256": manifest.get("package_sha256"),
        "early_looks": cur.get("early_looks", []),
    }
    with open(READINGS, "a") as fh:
        fh.write(json.dumps(reading, sort_keys=True) + "\n")
    state.setdefault("done", []).append(reading)
    state["current"] = None
    save(STATE, state)
    log(f"READ {cur['id']} ({cur['submission_id']}): score {reading['score']} rank "
        f"{reading['rank']}/{reading['total']}, {done}/{games} games done, package {package.name}")
    git_commit_push(f"ladder queue (VM): {cur['id']} read {reading['score']} at rank "
                    f"{reading['rank']} ({cur['submission_id']}); games collected")
    submit_next(queue, state)


def tick() -> None:
    queue = load(QUEUE, {"items": []})
    state = load(STATE, {"current": None, "done": []})
    if state.get("halted"):
        log(f"queue halted since {state['halted']['at']} at {state['halted']['item']}; nothing done")
        return
    if state.get("current") is None:
        submit_next(queue, state)
    else:
        read_current(queue, state)


def main() -> int:
    if "--status" in sys.argv:
        print(json.dumps(load(STATE, {}), indent=2, sort_keys=True))
        return 0
    with open(LOCK, "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("another tick is running")
            return 0
        try:
            tick()
        except Exception:
            log("tick crashed:\n" + traceback.format_exc()[-1500:])
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
