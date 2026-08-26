#!/usr/bin/env python3
"""Extract per-turn commands from the raw Troll Farm replays.

Reads every data/raw/games/*.json (read-only) and writes
    data/processed/turns.jsonl.gz    one line per (game, turn, seat)
    data/processed/turns.manifest.json

Turn/seat conventions follow data/scripts/parse.py:
  * frames[0] is the setup frame (agentId -1); real play starts at frames[1].
  * each frame carries `agentId` = the SEAT index (0/1) of the acting player
    and `stdout` = that seat's raw command line for the turn.
  * a turn is closed by a `keyframe` frame (stdout of that frame belongs to the
    turn being closed).  Turns are numbered from 1.
  * seat -> player identity comes from the replay's `agents` array
    (agents[i]["index"] is the seat), never from any battle listing.

Command grammar (see docs/statement.md + parse.py VERBS): commands are
separated by ';' (a MSG payload therefore cannot contain ';').  MSG is split
out into the `msg` field with its text kept verbatim (telemetry NOT decoded).

Output line schema:
  {gameId:int, turn:int, seat:0|1, agentId:int|null, name:str|null,
   stdout:str, cmds:[{verb, unit, args}], msg:str|null}

Output order is deterministic: sorted by (gameId, turn, seat).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RAW_GAMES = DATA / "raw" / "games"
PROC = DATA / "processed"

VERBS = ("MOVE", "HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK", "TRAIN",
         "WAIT", "MSG")
# verbs whose first argument is a troll id
UNIT_VERBS = ("MOVE", "HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK")


def parse_command(cmd: str):
    """cmd is one already-stripped, non-empty ';'-separated command."""
    parts = cmd.split()
    verb = parts[0].upper()
    if verb == "MSG":
        # keep the payload verbatim (everything after the first token)
        text = cmd.split(None, 1)[1] if len(parts) > 1 else ""
        return {"verb": "MSG", "unit": None, "args": []}, text
    unit = None
    args = parts[1:]
    if verb in UNIT_VERBS and args and args[0].lstrip("-").isdigit():
        unit = int(args[0])
        args = args[1:]
    rec = {"verb": verb if verb in VERBS else "OTHER", "unit": unit,
           "args": args}
    if rec["verb"] == "OTHER":
        rec["raw_verb"] = parts[0]
    return rec, None


def parse_stdout(so: str):
    cmds, msgs = [], []
    for chunk in so.replace("\n", ";").split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        rec, text = parse_command(chunk)
        cmds.append(rec)
        if text is not None:
            msgs.append(text)
    return cmds, ("\n".join(msgs) if msgs else None)


def sha256_file(p: Path) -> str:
    hh = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            hh.update(chunk)
    return hh.hexdigest()


def process_file(fp_str: str):
    """Return (gameId, lines, n_frames, n_turns, n_missing_stdout, error)."""
    fp = Path(fp_str)
    gid_s = fp.stem
    try:
        with open(fp, "rb") as fh:
            r = json.loads(fh.read())
        gid = int(gid_s)
        frames = r["frames"]
        seat_info = {}
        for a in r.get("agents", []) or []:
            idx = a.get("index")
            cg = a.get("codingamer") or {}
            boss = a.get("arenaboss")
            seat_info[idx] = (
                a.get("agentId"),
                cg.get("pseudo") or (boss or {}).get("nickname")
                or ("BOSS" if boss else None),
            )
        pending = {0: [], 1: []}
        turn = 1
        lines = []
        missing = 0
        for f in frames[1:]:
            a = f.get("agentId")
            so = f.get("stdout")
            if so is not None and a in (0, 1):
                pending[a].append(so.rstrip("\n"))
            if f.get("keyframe"):
                for seat in (0, 1):
                    if not pending[seat]:
                        missing += 1
                        continue
                    raw = "\n".join(pending[seat])
                    cmds, msg = parse_stdout(raw)
                    aid, name = seat_info.get(seat, (None, None))
                    lines.append(json.dumps(
                        {"gameId": gid, "turn": turn, "seat": seat,
                         "agentId": aid, "name": name, "stdout": raw,
                         "cmds": cmds, "msg": msg},
                        separators=(",", ":"), ensure_ascii=False))
                pending = {0: [], 1: []}
                turn += 1
        return gid_s, lines, len(frames), turn - 1, missing, None
    except Exception as e:  # noqa: BLE001
        return gid_s, [], 0, 0, 0, f"{type(e).__name__}: {e}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(PROC / "turns.jsonl.gz"))
    ap.add_argument("--manifest", default=str(PROC / "turns.manifest.json"))
    ap.add_argument("--limit", type=int, default=0,
                    help="process only the first N files (debug)")
    ap.add_argument("--games", default="",
                    help="comma-separated gameIds to process (debug)")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    args = ap.parse_args()

    t0 = time.time()
    files = sorted(RAW_GAMES.glob("*.json"), key=lambda p: p.stem)
    if args.games:
        want = set(args.games.split(","))
        files = [f for f in files if f.stem in want]
    if args.limit:
        files = files[:args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_games = n_lines = n_frames = n_missing = 0
    failures = []
    h = hashlib.sha256()
    strs = [str(f) for f in files]
    with gzip.open(out_path, "wt", encoding="utf-8", compresslevel=6) as out:
        def emit(lines):
            for ln in lines:
                b = (ln + "\n")
                out.write(b)
                h.update(b.encode("utf-8"))
        if args.jobs > 1:
            with Pool(args.jobs) as pool:
                it = pool.imap(process_file, strs, chunksize=8)
                for gid_s, lines, nf, nt, miss, err in it:
                    if err:
                        failures.append((gid_s, err))
                        continue
                    n_games += 1
                    n_frames += nf
                    n_missing += miss
                    n_lines += len(lines)
                    emit(lines)
        else:
            for s in strs:
                gid_s, lines, nf, nt, miss, err = process_file(s)
                if err:
                    failures.append((gid_s, err))
                    continue
                n_games += 1
                n_frames += nf
                n_missing += miss
                n_lines += len(lines)
                emit(lines)

    manifest = {
        "command_line": " ".join([sys.executable] + sys.argv),
        "output": str(out_path),
        "files_seen": len(files),
        "games_written": n_games,
        "frames_parsed": n_frames,
        "turn_records_written": n_lines,
        "seat_turns_without_stdout": n_missing,
        "parse_failures": len(failures),
        "parse_failure_examples": [{"gameId": g, "error": e}
                                   for g, e in failures[:20]],
        "output_bytes": out_path.stat().st_size,
        "output_sha256": sha256_file(out_path),
        "content_sha256": h.hexdigest(),
        "wall_seconds": round(time.time() - t0, 1),
        "jobs": args.jobs,
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=1))
    print(json.dumps({k: v for k, v in manifest.items()
                      if k != "parse_failure_examples"}, indent=1))


if __name__ == "__main__":
    main()
