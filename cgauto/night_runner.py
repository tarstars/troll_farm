#!/usr/bin/env python3
"""Deterministic M-1 paired-night runner — no LLM, laptop-independent.

Executes the per-mark ritual of a paired arena night exactly as specified in
the night ledger: wait out each arm's ~2 h window, take the mature read,
append the ledger row, submit the other arm (fail-closed, via
api_submit_once.py), push, repeat; after the final read compute the
pre-registered verdict arithmetic and stop. State lives in a JSON file next to
the ledger so a restart resumes exactly where it stopped.

Safety posture (unattended): NO automatic retry of submissions. Any anomaly —
submit failure, unparseable read, git push failure after one rebase retry —
writes a HALT block to the ledger, pushes it, and exits nonzero. Losing a
window costs little; an ambiguous double-submission costs the night.

A halt file (NIGHT-HALT in the repo root) stops the runner at the next loop.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
RANK_RE = re.compile(
    r"ARENA-ROOM: \S+ rank (\d+)/(\d+) (\S+) score ([\d.]+) .*agentId=(\d+)")
BATTLES_RE = re.compile(r"battles listed: (\d+)")

MIN_WINDOW_MIN = 115          # earliest read, minutes after submission
FORCE_READ_MIN = 170          # read regardless of battle count after this
MATURE_BATTLES = 150
POLL_SECONDS = 180

WINNER_BAR = 1.315            # 1.96 * 1.5/sqrt(5), owner-adopted sigma_pair
MATERIALITY_FLOOR = 1.0


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def stamp(t: dt.datetime | None = None) -> str:
    return (t or utcnow()).strftime("%H:%M:%SZ")


def run(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                          timeout=timeout)


def read_arena() -> dict:
    rank = run([sys.executable, "cgauto/cg_rank.py"])
    battles = run([sys.executable, "cgauto/battles.py", "12"], timeout=240)
    m = RANK_RE.search(rank.stdout)
    b = BATTLES_RE.search(battles.stdout)
    if not m or not b:
        raise RuntimeError(
            f"unparseable read: rank_rc={rank.returncode} "
            f"battles_rc={battles.returncode} out={rank.stdout[:200]!r}")
    return {"rank": int(m.group(1)), "total": int(m.group(2)),
            "league": m.group(3), "score": float(m.group(4)),
            "agent_id": m.group(5), "battles": int(b.group(1)),
            "read_at": stamp()}


def submit(arm: dict) -> dict:
    proc = run([sys.executable, "cgauto/api_submit_once.py", arm["source"],
                "--expected-sha256", arm["sha256"]], timeout=120)
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        payload = {}
    if proc.returncode != 0 or not payload.get("accepted"):
        raise RuntimeError(
            f"submit FAILED rc={proc.returncode} payload={payload!r} "
            f"stderr={proc.stderr[:200]!r}")
    return payload


def git_publish(state_path: pathlib.Path, ledger: pathlib.Path, msg: str) -> None:
    run(["git", "add", str(state_path), str(ledger)])
    run(["git", "commit", "-m", msg])
    for attempt in (1, 2):
        push = run(["git", "push", "origin", "agent/local_claude_1"])
        if push.returncode == 0:
            break
        if attempt == 1:
            run(["git", "pull", "--rebase", "origin", "agent/local_claude_1"])
        else:
            raise RuntimeError(f"git push failed twice: {push.stderr[:300]}")
    run(["git", "push", "origin", "agent/local_claude_1:main"])


def append(ledger: pathlib.Path, text: str) -> None:
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(text)


def halt(state_path, ledger, state, reason: str) -> None:
    note = (f"\n**HALT {utcnow().isoformat(timespec='seconds')}** — "
            f"night_runner stopped: {reason}. No further mutations; resume "
            f"or rule manually.\n")
    append(ledger, note)
    state["halted"] = reason
    state_path.write_text(json.dumps(state, indent=1))
    try:
        git_publish(state_path, ledger, f"night_runner HALT: {reason[:80]}")
    finally:
        sys.exit(2)


def verdict_block(state) -> str:
    pairs = []
    reads = state["reads"]
    for i in range(0, len(reads) - 1, 2):
        pairs.append(round(reads[i]["score"] - reads[i + 1]["score"], 2))
    mean = sum(pairs) / len(pairs)
    n = len(pairs)
    var = sum((p - mean) ** 2 for p in pairs) / (n - 1) if n > 1 else 0.0
    sd = var ** 0.5
    if abs(mean) >= WINNER_BAR:
        outcome = ("WINNER: challenger" if mean > 0 else "WINNER: champion")
    elif abs(mean) < MATERIALITY_FLOOR:
        outcome = "IMMATERIAL (below the 1.0 floor)"
    else:
        outcome = "BETWEEN floor and bar -> M-1 prescribes one extension"
    return (f"\n## BLOCK COMPLETE ({utcnow().isoformat(timespec='seconds')}, "
            f"computed by night_runner)\n\n"
            f"- Pairs (A-B): {pairs} -> mean {mean:+.3f}\n"
            f"- Pre-registered arithmetic: sigma_pair 1.5, winner bar "
            f"{WINNER_BAR}, floor {MATERIALITY_FLOOR}\n"
            f"- Empirical pair SD (honesty clause): {sd:.3f}\n"
            f"- Arithmetic outcome: **{outcome}** — KEEP/REVERT is the "
            f"OWNER'S ruling; the nine named costs travel with this.\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--once", action="store_true",
                    help="one loop iteration then exit (testing)")
    ap.add_argument("--dry-run", action="store_true",
                    help="reads only; never submits, never pushes")
    args = ap.parse_args()
    state_path = pathlib.Path(args.state)
    ledger = pathlib.Path(args.ledger)
    state = json.loads(state_path.read_text())

    while True:
        if (REPO / "NIGHT-HALT").exists():
            halt(state_path, ledger, state, "halt file present")
        reads_done = len(state["reads"])
        if reads_done >= len(state["plan"]):
            break
        cur = state["plan"][reads_done]        # the arm currently on the ladder
        sub_at = dt.datetime.fromisoformat(state["submissions"][reads_done]["at"])
        elapsed_min = (utcnow() - sub_at).total_seconds() / 60
        if elapsed_min < MIN_WINDOW_MIN:
            if args.once:
                print(f"not due: {elapsed_min:.0f}m elapsed")
                return 0
            time.sleep(POLL_SECONDS)
            continue
        try:
            reading = read_arena()
        except Exception as exc:
            if elapsed_min > FORCE_READ_MIN + 60:
                halt(state_path, ledger, state, f"reads failing: {exc}")
            time.sleep(POLL_SECONDS)
            continue
        if reading["battles"] < MATURE_BATTLES and elapsed_min < FORCE_READ_MIN:
            if args.once:
                print(f"immature: {reading}")
                return 0
            time.sleep(POLL_SECONDS)
            continue
        if args.dry_run:
            print(f"DRY: would record {cur['label']} = {reading}")
            return 0
        # 1. record the read
        state["reads"].append({"label": cur["label"], **reading})
        row = (f"| {cur['label']} | {cur['arm']} | "
               f"{state['submissions'][reads_done]['at'][11:19]}Z | "
               f"{state['submissions'][reads_done]['id']} | "
               f"{reading['agent_id']} | {reading['read_at']} | "
               f"{reading['battles']} | {reading['score']} | "
               f"{reading['rank']}/{reading['total']} |\n")
        append(ledger, row)
        # 2. submit the next arm, unless the block is complete
        if len(state["reads"]) < len(state["plan"]):
            nxt = state["plan"][len(state["reads"])]
            arm = state["arms"][nxt["arm"]]
            try:
                payload = submit(arm)
            except Exception as exc:
                halt(state_path, ledger, state, str(exc))
            state["submissions"].append(
                {"at": utcnow().isoformat(timespec="seconds"),
                 "id": payload["submission_id"], "arm": nxt["arm"]})
            append(ledger, f"- {nxt['label']} swap {stamp()}: accepted, "
                           f"sha verified, submission "
                           f"{payload['submission_id']} (night_runner)\n")
        else:
            append(ledger, verdict_block(state))
        state_path.write_text(json.dumps(state, indent=1))
        git_publish(state_path, ledger,
                    f"night_runner: {cur['label']} read "
                    f"{reading['score']}@{reading['rank']}"
                    + ("; next arm submitted"
                       if len(state["reads"]) < len(state["plan"])
                       else "; BLOCK COMPLETE"))
        if args.once:
            return 0
    print("block complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
