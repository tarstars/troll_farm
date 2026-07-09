#!/usr/bin/env python3
"""Aggregate Rust @TFOWN ownership diagnostics from DEBUG raw games.

This is reporting glue only. The ownership model lives in the Rust bot and emits
@TFOWN/@TFOWNCFG rows from live per-turn State.

Usage:
  uv run --no-sync python cgauto/map_value_ownership.py [--csv out.csv] <raw files or dirs...>
"""
import argparse
import csv
import re
import statistics
from collections import defaultdict
from pathlib import Path

PHASES = (75, 150, 225, 300)
OWN_RE = re.compile(r"^@TFOWN\s+(.*)$")
CFG_RE = re.compile(r"^@TFOWNCFG\s+(.*)$")
LOG_RE = re.compile(r"# gameId (\d+)\s+(WIN|LOSS)\s+scores \[([0-9.]+), ([0-9.]+)\]")


def kvs(text):
    out = {}
    for part in text.split():
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        try:
            out[key] = int(value)
        except ValueError:
            out[key] = value
    return out


def raw_files(paths):
    for arg in paths:
        path = Path(arg)
        if path.is_dir():
            yield from sorted(path.rglob("game_*.raw"))
        elif path.suffix == ".raw":
            yield path


def game_meta(raw_path):
    game = re.search(r"game_(\d+)\.raw$", raw_path.name)
    game_id = game.group(1) if game else raw_path.stem
    opp = raw_path.parent.name
    log_path = raw_path.with_suffix(".log")
    won = None
    my_score = None
    opp_score = None
    if log_path.exists():
        for line in log_path.read_text(errors="replace").splitlines()[:3]:
            m = LOG_RE.match(line)
            if m:
                won = m.group(2) == "WIN"
                my_score = float(m.group(3))
                opp_score = float(m.group(4))
                break
    return game_id, opp, won, my_score, opp_score


def parse_raw(raw_path):
    game_id, opp, won, my_score, opp_score = game_meta(raw_path)
    cfg = {}
    rows = []
    for line in raw_path.read_text(errors="replace").splitlines():
        cm = CFG_RE.match(line)
        if cm:
            cfg.update(kvs(cm.group(1)))
            continue
        om = OWN_RE.match(line)
        if not om:
            continue
        row = kvs(om.group(1))
        row.update(
            {
                "game": game_id,
                "opp_id": opp,
                "won": won,
                "my_score": my_score,
                "opp_score": opp_score,
                "raw": str(raw_path),
            }
        )
        for key, value in cfg.items():
            row[f"cfg_{key}"] = value
        rows.append(row)
    return rows


def avg(rows, field):
    vals = [r[field] for r in rows if isinstance(r.get(field), int)]
    return statistics.mean(vals) if vals else None


def fmt(v):
    return "n/a" if v is None else f"{v:.1f}"


def phase_rows(rows):
    return [r for r in rows if r.get("t") in PHASES]


def print_summary(rows):
    phases = phase_rows(rows)
    by_game = {}
    for row in rows:
        by_game[row["game"]] = row
    games = list(by_game.values())
    print(f"rows={len(rows)} phase_rows={len(phases)} games={len(games)}")
    for opp, group in sorted(group_by(games, "opp_id").items()):
        wins = sum(1 for r in group if r.get("won"))
        known = sum(1 for r in group if r.get("won") is not None)
        print(f"opp={opp} games={len(group)} wins={wins}/{known}")

    print("\n== phase averages ==")
    print("t games total ours opp uncertain dead created_exposed own_half_exposed")
    for t in PHASES:
        group = [r for r in phases if r.get("t") == t]
        print(
            f"{t} {len(group)} {fmt(avg(group, 'total'))} {fmt(avg(group, 'ours'))} "
            f"{fmt(avg(group, 'opp'))} {fmt(avg(group, 'uncertain'))} {fmt(avg(group, 'dead'))} "
            f"{fmt(avg(group, 'created_exposed'))} {fmt(avg(group, 'own_half_exposed'))}"
        )

    print("\n== win/loss split, phase averages ==")
    for label, keep in (("wins", True), ("losses", False)):
        subset = [r for r in phases if r.get("won") is keep]
        print(f"\n{label}")
        for t in PHASES:
            group = [r for r in subset if r.get("t") == t]
            print(
                f"t={t} n={len(group)} total={fmt(avg(group, 'total'))} "
                f"ours={fmt(avg(group, 'ours'))} opp={fmt(avg(group, 'opp'))} "
                f"uncertain={fmt(avg(group, 'uncertain'))} "
                f"created_exposed={fmt(avg(group, 'created_exposed'))} "
                f"own_half_exposed={fmt(avg(group, 'own_half_exposed'))}"
            )

    for field in ("created_exposed", "own_half_exposed"):
        print(f"\n== top {field} t150/t225 ==")
        top = sorted(
            [r for r in phases if r.get("t") in (150, 225)],
            key=lambda r: (r.get(field, 0), r.get("opp", 0)),
            reverse=True,
        )[:5]
        for r in top:
            result = "W" if r.get("won") else "L"
            print(
                f"{field}={r.get(field)} game={r['game']} opp={r['opp_id']} {result} "
                f"t={r.get('t')} total={r.get('total')} ours={r.get('ours')} "
                f"opp_bucket={r.get('opp')} uncertain={r.get('uncertain')}"
            )


def group_by(rows, field):
    out = defaultdict(list)
    for row in rows:
        out[row.get(field)].append(row)
    return out


def write_csv(rows, path):
    fields = [
        "game",
        "opp_id",
        "won",
        "my_score",
        "opp_score",
        "t",
        "total",
        "ours",
        "opp",
        "uncertain",
        "dead",
        "created_exposed",
        "own_half_exposed",
        "cfg_margin",
        "cfg_future_seed",
        "cfg_created_near_tent_r",
        "cfg_farm_r",
        "raw",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="optional CSV output path")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()

    rows = []
    for raw_path in raw_files(args.paths):
        rows.extend(parse_raw(raw_path))
    rows.sort(key=lambda r: (r["opp_id"], r["game"], r.get("t", -1)))

    if args.csv:
        Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
        write_csv(rows, args.csv)
    print_summary(rows)


if __name__ == "__main__":
    main()
