#!/usr/bin/env python3
"""Evaluate the accepted P4b per-troll stall definition across narrator dialects."""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib
import json
import sys
from pathlib import Path

W = K = 60
TRIPWIRE = 45
CONCRETE_PREFIXES = ("SHACK", "BANK(", "CELL(", "TREE(")


def concrete(value: str) -> bool:
    return value == "SHACK" or value.startswith(CONCRETE_PREFIXES[1:])


def progress_event(tr, uid: int, turn: int) -> bool:
    """Exact restatement of dance_facts.progress_event."""
    if turn + 1 > tr.T:
        return True
    u0, u1 = tr.unit(uid, turn), tr.unit(uid, turn + 1)
    if u0 is None or u1 is None:
        return True
    if u0.carry != u1.carry:
        return True
    cmd = tr.cmd_of(uid, turn)
    if cmd is not None and cmd.verb in ("DROP", "PICK"):
        if tr.state(turn).inventories[0] != tr.state(turn + 1).inventories[0]:
            return True
    p0 = tr.state(turn).plant_at(u0.cell)
    p1 = tr.state(turn + 1).plant_at(u0.cell)
    return (p0 is None) != (p1 is None)


def maximal_runs(turn_rows: list[dict]) -> list[dict]:
    """Maximal consecutive all-available/progress-free runs."""
    runs, start, end = [], None, None
    for row in turn_rows:
        good = row["available_concrete"] and not row["progress"]
        contiguous = end is not None and row["turn"] == end + 1
        if good and (start is None or contiguous):
            start = row["turn"] if start is None else start
            end = row["turn"]
        elif good:
            if end - start + 1 >= W:
                runs.append({"start": start, "end": end, "length": end - start + 1,
                             "available_count": end - start + 1, "progress_count": 0})
            start = end = row["turn"]
        else:
            if start is not None and end - start + 1 >= W:
                runs.append({"start": start, "end": end, "length": end - start + 1,
                             "available_count": end - start + 1, "progress_count": 0})
            start = end = None
    if start is not None and end - start + 1 >= W:
        runs.append({"start": start, "end": end, "length": end - start + 1,
                     "available_count": end - start + 1, "progress_count": 0})
    return runs


def percentile(values: list[int], q: float) -> int | None:
    if not values:
        return None
    values = sorted(values)
    return values[round((len(values) - 1) * q)]


def archive_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def narrator_fragments(line: str) -> list[str]:
    """Return MSG fragments that actually contain a NARRATE payload."""
    return [frag for frag in line.split(";")
            if frag.lstrip().upper().startswith("MSG ") and "NARRATE" in frag.split()]


def decode_units(narrator, payload: str):
    """Dialect-neutral boundary: P4b consumes only turn and per-unit availability/branch."""
    turn, units, _order, _banner, _meta = narrator.decode(payload)
    for uid, unit in units.items():
        if len(unit) < 4:
            raise ValueError(f"unit {uid} decoder tuple has {len(unit)} fields, expected >=4")
    return turn, units


def evaluate_not_applicable(path: Path) -> dict:
    """Validate an explicitly narrator-less arm without inventing P4b observations."""
    errors, games, map_seats = [], 0, collections.Counter()
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for row_number, line in enumerate(fh, 1):
            game = json.loads(line)
            games += 1
            map_seats[game["map_id"]] += 1
            commands = game["artifacts"]["candidate_commands"]
            narrated = sum(bool(narrator_fragments(command))
                           for command in commands.rstrip("\n").split("\n"))
            if narrated:
                errors.append(f"row {row_number} {game['map_id']}:{game['seat']}: "
                              f"declared none but found {narrated} NARRATE turns")
    return {"archive": str(path), "archive_sha256": archive_sha(path), "dialect": "none",
            "status": "GATE_UNREADY" if errors else "NOT_APPLICABLE",
            "reason": ("declared narrator-less arm contains NARRATE telemetry" if errors else
                       "arm explicitly declared narrator-less; P4b wire gate does not apply"),
            "errors": errors, "games": games, "map_ids": len(map_seats),
            "both_seats_per_map": bool(map_seats) and all(v == 2 for v in map_seats.values()),
            "totals": {}, "failed_units": [], "failed_games": [], "unit_rows": []}


def evaluate(path: Path, td, narrator, dialect: str) -> dict:
    games, unit_rows, errors = [], [], []
    seen_games, map_seats = set(), collections.Counter()
    totals = collections.Counter()
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        source_rows = [json.loads(line) for line in fh]
    for game in source_rows:
        game_key = (game["map_id"], int(game["seat"]))
        if game_key in seen_games:
            errors.append(f"duplicate game {game_key}")
            continue
        seen_games.add(game_key); map_seats[game["map_id"]] += 1
        commands = game["artifacts"]["candidate_commands"]
        tr = td.build_trace(game["artifacts"]["candidate_transcript"], commands)
        lines = commands.rstrip("\n").split("\n")
        telemetry = {}
        branches = {}
        for index, line in enumerate(lines, 1):
            msgs = narrator.msg_fragments(line)
            if len(msgs) != 1:
                errors.append(f"{game_key} turn {index}: {len(msgs)} telemetry rows")
                continue
            try:
                turn, units = decode_units(narrator, msgs[0].strip())
            except Exception as exc:
                errors.append(f"{game_key} turn {index}: telemetry decode: {exc}")
                continue
            if turn != index:
                errors.append(f"{game_key} turn {index}: telemetry says turn {turn}")
            for uid, (_, available, branch, _) in units.items():
                key = (turn, uid)
                if key in telemetry:
                    errors.append(f"{game_key} turn {turn} unit {uid}: duplicate telemetry")
                telemetry[key] = available
                branches[key] = branch

        own_by_turn = {}
        for turn in range(1, tr.T + 1):
            own_by_turn[turn] = sorted(u.id for u in tr.state(turn).own_units())
            tele_ids = sorted(uid for (t, uid) in telemetry if t == turn)
            if own_by_turn[turn] != tele_ids:
                errors.append(f"{game_key} turn {turn}: roster {own_by_turn[turn]} != telemetry {tele_ids}")
        uids = sorted({uid for ids in own_by_turn.values() for uid in ids})
        game_failed = []
        for uid in uids:
            alive = [t for t in range(1, tr.T + 1) if uid in own_by_turn[t]]
            intervals = []
            for t in alive:
                if not intervals or t != intervals[-1][-1] + 1:
                    intervals.append([t])
                else:
                    intervals[-1].append(t)
            if len(intervals) != 1:
                errors.append(f"{game_key} unit {uid}: non-contiguous life {intervals}")
            life_start, life_end = alive[0], alive[-1]
            rows = []
            for turn in range(life_start, life_end):
                if uid not in own_by_turn[turn + 1]:
                    continue
                available = telemetry.get((turn, uid))
                if available is None:
                    errors.append(f"{game_key} turn {turn} unit {uid}: missing telemetry")
                    continue
                prog = progress_event(tr, uid, turn)
                rows.append({"turn": turn, "available": available,
                             "available_concrete": concrete(available), "progress": prog})
                totals["observable_transitions"] += 1
                totals["available_turns"] += int(concrete(available))
                totals["progress_turns"] += int(prog)
            episodes = maximal_runs(rows)
            longest = 0
            current = 0
            for row in rows:
                current = current + 1 if row["available_concrete"] and not row["progress"] else 0
                longest = max(longest, current)
            windows_evaluated = max(0, len(rows) - W + 1)
            all_available_windows = sum(
                all(r["available_concrete"] for r in rows[i:i + W])
                for i in range(windows_evaluated))
            totals["windows_evaluated"] += windows_evaluated
            totals["all_available_windows"] += all_available_windows
            totals["episodes"] += len(episodes)
            branch_turns = [branches[(t, uid)] for t in alive if (t, uid) in branches]
            idle = sum(b in ("H", "W") for b in branch_turns)
            share = 100.0 * idle / len(branch_turns) if branch_turns else 0.0
            if len(rows) < W:
                blind = "life_shorter_than_60"
            elif errors:
                blind = None
            elif all_available_windows:
                blind = None
            elif any(r["available"] == "ABSENT" for r in rows):
                blind = "ABSENT_in_every_window"
            else:
                blind = "NONE_in_every_window"
            rec = {"map_id": game_key[0], "seat": game_key[1], "unit_id": uid,
                   "alive_interval": [life_start, life_end], "observable_transitions": len(rows),
                   "idle_with_work_share_pct": round(share, 6),
                   "longest_all_available_progress_free_run": longest,
                   "windows_evaluated": windows_evaluated,
                   "all_available_windows": all_available_windows, "blind_cause": blind,
                   "episodes": episodes}
            unit_rows.append(rec)
            totals["unit_lives"] += 1
            if episodes:
                game_failed.append(uid)
        games.append({"map_id": game_key[0], "seat": game_key[1],
                      "failed_units": sorted(game_failed)})

    failed_units = sorted([{"map_id": r["map_id"], "seat": r["seat"], "unit_id": r["unit_id"],
                            "longest": max((e["length"] for e in r["episodes"]), default=0),
                            "episodes": r["episodes"]} for r in unit_rows if r["episodes"]],
                          key=lambda r: (r["map_id"], r["seat"], r["unit_id"]))
    lengths = [r["longest_all_available_progress_free_run"] for r in unit_rows]
    blind = collections.defaultdict(list)
    for r in unit_rows:
        if r["all_available_windows"] == 0:
            blind[r["blind_cause"] or "no_stall_evaluable_window"].append(
                [r["map_id"], r["seat"], r["unit_id"]])
    above = []
    for r in unit_rows:
        if r["idle_with_work_share_pct"] > 1.5:
            above.append({"map_id": r["map_id"], "seat": r["seat"], "unit_id": r["unit_id"],
                          "share_pct": r["idle_with_work_share_pct"],
                          "p4b_failure": bool(r["episodes"]),
                          "longest_run": r["longest_all_available_progress_free_run"],
                          "explanation": ("P4b episode" if r["episodes"] else "run below W")})
    return {"archive": str(path), "archive_sha256": archive_sha(path), "dialect": dialect,
            "status": "GATE_UNREADY" if errors else "READY", "errors": errors,
            "games": len(games), "map_ids": len(map_seats),
            "both_seats_per_map": all(v == 2 for v in map_seats.values()),
            "totals": dict(totals), "failed_units": failed_units,
            "failed_games": [g for g in games if g["failed_units"]],
            "unit_rows": sorted(unit_rows, key=lambda r: (r["map_id"], r["seat"], r["unit_id"])),
            "blind_population": {k: {"count": len(v), "keys": sorted(v)} for k, v in sorted(blind.items())},
            "longest_run_distribution": {"min": min(lengths), "q1": percentile(lengths, .25),
                "median": percentile(lengths, .5), "q3": percentile(lengths, .75), "max": max(lengths)},
            "idle_share_above_1_5_pct": above,
            "tripwire_45": [r for r in above if not r["p4b_failure"] and r["longest_run"] >= TRIPWIRE]}


def unit_key(row):
    return (row["map_id"], row["seat"], row["unit_id"])


def compare(base: dict, candidate: dict) -> dict:
    if base["status"] == "NOT_APPLICABLE" or candidate["status"] == "NOT_APPLICABLE":
        return {"status": "NOT_APPLICABLE", "reason": "one or both arms are narrator-less",
                "roster_lifetime_mismatches": [], "added_unit_keys": [],
                "removed_unit_keys": [], "added_game_keys": [], "removed_game_keys": [],
                "common_failure_longest_deltas": []}
    b_life = {unit_key(r): r["alive_interval"] for r in base["unit_rows"]}
    c_life = {unit_key(r): r["alive_interval"] for r in candidate["unit_rows"]}
    mismatch = []
    for key in sorted(set(b_life) | set(c_life)):
        if b_life.get(key) != c_life.get(key):
            mismatch.append({"key": list(key), "base": b_life.get(key), "candidate": c_life.get(key)})
    bf = {unit_key(r): r for r in base["failed_units"]}
    cf = {unit_key(r): r for r in candidate["failed_units"]}
    common = sorted(set(bf) & set(cf))
    growth = [{"key": list(k), "candidate_minus_base": cf[k]["longest"] - bf[k]["longest"]}
              for k in common]
    ready = (base["status"] == candidate["status"] == "READY" and not mismatch)
    added, removed = sorted(set(cf) - set(bf)), sorted(set(bf) - set(cf))
    return {"status": "GATE_UNREADY" if not ready else ("BLOCK" if added else "PASS"),
            "roster_lifetime_mismatches": mismatch, "added_unit_keys": [list(k) for k in added],
            "removed_unit_keys": [list(k) for k in removed],
            "added_game_keys": [list(k) for k in sorted({k[:2] for k in added})],
            "removed_game_keys": [list(k) for k in sorted({k[:2] for k in removed})],
            "common_failure_longest_deltas": sorted(growth, key=lambda r: (-r["candidate_minus_base"], r["key"]))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module-root", required=True,
                    help="root containing banana-restoration-r2 and narrate4/5/6")
    ap.add_argument("--arm", action="append", required=True, help="LABEL=archive.jsonl.gz")
    ap.add_argument("--dialect", action="append", required=True,
                    help="LABEL=v4|v5|v6|none; required for every --arm")
    ap.add_argument("--base", default="champion")
    ap.add_argument("--json", required=True)
    args = ap.parse_args(argv)
    root = Path(args.module_root)
    sys.path[:0] = [str(root / "banana-restoration-r2")]
    import trace_detectors as td
    arms = dict(item.split("=", 1) for item in args.arm)
    dialects = dict(item.split("=", 1) for item in args.dialect)
    if set(dialects) != set(arms):
        raise SystemExit(f"--dialect labels {sorted(dialects)} do not match --arm labels "
                         f"{sorted(arms)}")
    unknown = sorted({value for value in dialects.values()} - {"v4", "v5", "v6", "none"})
    if unknown:
        raise SystemExit(f"unsupported dialect(s): {unknown}")
    narrators = {}
    for dialect in sorted(set(dialects.values()) - {"none"}):
        sys.path.insert(0, str(root / f"narrate{dialect[1:]}"))
        narrators[dialect] = importlib.import_module(f"narrate{dialect[1:]}")
    evaluated = {}
    for label, path in sorted(arms.items()):
        dialect = dialects[label]
        evaluated[label] = (evaluate_not_applicable(Path(path)) if dialect == "none" else
                            evaluate(Path(path), td, narrators[dialect], dialect))
    if args.base not in evaluated:
        raise SystemExit(f"base arm {args.base!r} not supplied")
    comparisons = {label: compare(evaluated[args.base], row) for label, row in evaluated.items()
                   if label != args.base}
    applicable = [r for r in evaluated.values() if r["status"] != "NOT_APPLICABLE"]
    poison = evaluated.get("poison_a", {})
    k1 = next((r for r in poison.get("failed_units", [])
               if unit_key(r) == ("m014", 1, 2) and r["longest"] >= 60), None)
    controls = {"K1_m014_seat1_unit2": {"applicable": bool(poison),
                                         "pass": k1 is not None, "row": k1},
                "K3_tripwire_clear": all(not r["tripwire_45"] for r in applicable),
                "K5_exact_240": all(r["games"] == 240 and r["map_ids"] == 120 and
                                    r["both_seats_per_map"] for r in evaluated.values()),
                "all_applicable_arms_ready": all(r["status"] == "READY" for r in applicable)}
    packet = {"schema": "p4b-g1/1", "definition": {"W": W, "k": K, "tripwire": TRIPWIRE},
              "arms": evaluated, "comparisons": comparisons,
              "controls": controls}
    Path(args.json).write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"controls": packet["controls"],
                      "failed_units": {k: len(v["failed_units"]) for k, v in evaluated.items()},
                      "comparisons": {k: v["status"] for k, v in comparisons.items()}}, indent=2))
    required = [controls["K3_tripwire_clear"], controls["K5_exact_240"],
                controls["all_applicable_arms_ready"]]
    if controls["K1_m014_seat1_unit2"]["applicable"]:
        required.append(controls["K1_m014_seat1_unit2"]["pass"])
    return 0 if all(required) else 2


if __name__ == "__main__":
    raise SystemExit(main())
