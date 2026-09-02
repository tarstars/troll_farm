#!/usr/bin/env python3
"""Track E, deliverable 1: the command mix by phase, per bot, from the per-turn corpus.

Reads the turn corpus in place (`/data/scratch/turns.jsonl.gz`, one row per game/turn/seat, schema
of `scripts/extract_turns.py`; no board) and aggregates, per bot name and phase
(1-100, 101-200, 201-250, 251-300):
  turns, games, the verb counts (MOVE HARVEST CHOP PLANT PICK DROP MINE TRAIN), no-op turns
  (a turn whose command line carries no unit verb: WAIT or empty), active units (units that issued
  a unit verb this turn) and the roster proxy (distinct unit ids seen so far in the game-seat; a
  troll never dies, so this is the roster as far as the commands reveal it).
Per game-seat it also keeps the phase totals so per-game / per-troll / per-turn rates and their
spread can be read, and the top four's late-game MOVE count per game answers the 8-vs-32 question.
The corpus has no board: 'idle because nothing is reachable' cannot be read here (deliverable 2
uses the raw replays of the champion's collected games for that).
"""
from __future__ import annotations
import argparse, gzip, json, sys, collections, hashlib

PHASES = (("p1_100", 1, 100), ("p101_200", 101, 200), ("p201_250", 201, 250), ("p251_300", 251, 300))
VERBS = ("MOVE", "HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE", "TRAIN")
UNIT_VERBS = {"MOVE", "HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE"}
EXPECTED_SHA = "1e0ea236a3f0b813eae29d5ba4ec01564ab013984c0064be0ed8330fa5a66726"


def phase_of(turn):
    for name, lo, hi in PHASES:
        if lo <= turn <= hi:
            return name
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="/data/scratch/turns.jsonl.gz")
    ap.add_argument("--out", default="claude_1/endgame-gap/phase-mix.json")
    ap.add_argument("--names", default="delineate,norxondor_gorgonax,MSz,Bubaptik")
    ap.add_argument("--min-games", type=int, default=100, help="other bots kept if they have this many game-seats")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip-hash", action="store_true")
    a = ap.parse_args()
    if not a.skip_hash:
        h = hashlib.sha256()
        with open(a.corpus, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 22), b""):
                h.update(chunk)
        if h.hexdigest() != EXPECTED_SHA:
            sys.exit(f"REFUSED: corpus sha {h.hexdigest()} != {EXPECTED_SHA}")
    want = set(a.names.split(","))
    # per (name, phase) aggregate
    agg = collections.defaultdict(lambda: collections.Counter())
    # per game-seat: roster ids seen; per (game-seat, phase) counters
    roster = {}
    per_game = collections.defaultdict(lambda: collections.Counter())  # key (name, gameId, seat, phase)
    game_names = {}
    n = 0
    with gzip.open(a.corpus, "rt") as fh:
        for line in fh:
            n += 1
            if a.limit and n > a.limit:
                break
            r = json.loads(line)
            name = r.get("name") or "?"
            ph = phase_of(r["turn"])
            if ph is None:
                continue
            key = (r["gameId"], r["seat"])
            game_names[key] = name
            seen = roster.setdefault(key, set())
            units_now = set()
            c = collections.Counter()
            for cmd in r["cmds"]:
                v = cmd["verb"]
                if v in VERBS:
                    c[v] += 1
                if v in UNIT_VERBS and cmd["unit"] is not None:
                    units_now.add(cmd["unit"])
            seen |= units_now
            noop = 1 if not any(v in UNIT_VERBS for v in c) else 0
            g = per_game[(name, r["gameId"], r["seat"], ph)]
            g["turns"] += 1
            g["noop_turns"] += noop
            g["active_units"] += len(units_now)
            g["roster"] += len(seen)
            for v in VERBS:
                g[v] += c[v]
    # fold per-game into per-name aggregates, keep per-game rows for the named bots
    games_per_name = collections.Counter()
    for (name, gid, seat, ph), g in per_game.items():
        games_per_name[(name, ph)] += 1
    kept = {}
    for (name, gid, seat, ph), g in per_game.items():
        if name not in want and games_per_name[(name, "p1_100")] < a.min_games:
            continue
        A = agg[(name, ph)]
        A["games"] += 1
        for k, v in g.items():
            A[k] += v
        # late-game per-game MOVE distribution for the named bots
        if name in want and ph == "p251_300":   # per-game rows only for the phase the report reads per game
            kept.setdefault(name, {}).setdefault(ph, []).append(
                {"gameId": gid, "seat": seat, "turns": g["turns"], "MOVE": g["MOVE"], "CHOP": g["CHOP"],
                 "HARVEST": g["HARVEST"], "PLANT": g["PLANT"], "PICK": g["PICK"], "DROP": g["DROP"],
                 "noop_turns": g["noop_turns"], "active_units": g["active_units"], "roster": g["roster"]})
    out = {"corpus": a.corpus, "corpus_sha256": EXPECTED_SHA, "rows_read": n, "phases": PHASES,
           "by_name_phase": {}, "per_game": kept}
    for (name, ph), A in sorted(agg.items()):
        t = A["turns"] or 1
        row = dict(A)
        row["per_turn"] = {v: round(A[v] / t, 3) for v in VERBS}
        row["active_units_per_turn"] = round(A["active_units"] / t, 3)
        row["roster_per_turn"] = round(A["roster"] / t, 3)
        row["noop_share"] = round(A["noop_turns"] / t, 4)
        row["MOVE_per_game"] = round(A["MOVE"] / max(A["games"], 1), 2)
        row["MOVE_per_troll_turn"] = round(A["MOVE"] / max(A["roster"], 1), 4)
        out["by_name_phase"].setdefault(name, {})[ph] = row
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    # short table on stdout
    for name in sorted(out["by_name_phase"]):
        for ph, _, _ in PHASES:
            row = out["by_name_phase"][name].get(ph)
            if not row:
                continue
            pt = row["per_turn"]
            print(f"{name:22s} {ph:9s} games {row['games']:5d} turns {row['turns']:7d} roster/turn {row['roster_per_turn']:.2f} "
                  f"active/turn {row['active_units_per_turn']:.2f} noop {row['noop_share']:.3f} | "
                  + " ".join(f"{v[:4]} {pt[v]:.2f}" for v in VERBS) + f" | MOVE/game {row['MOVE_per_game']}")


if __name__ == "__main__":
    main()
