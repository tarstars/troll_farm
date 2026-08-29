#!/usr/bin/env python3
"""The clone's dataset builder (Track N, Phase 2, card
`coordination/tasks/20260829-nn-bot-way-b-dataset.md`) -- **the label half**.

From the exact reconstruction (`local_claude_1/reconstructions/fits/reconstruct.py`) this writes,
for every turn of a teacher's game, the rows the clone is trained on:

  * one **plan row** per turn: label = the 144-way index of the talents of the **next TRAIN the
    teacher actually issues** after this turn, or 0 ("train nothing") if it issues none before the
    end.  The vocabulary is the parent card's: speed 1-3 x carry 1-4 x harvest 0-2 x chop 0-3,
    index `(((speed-1)*4 + (carry-1))*3 + harvest)*4 + chop`, so index 0 (speed 1, carry 1, no
    harvest, no chop) is the illegal-by-mask combination repurposed as "train nothing".
  * one **command row** per own troll per turn, in troll-id order: label = the flat index
    `plane*242 + y*22 + x` with the July decoding (0 MOVE, 1 HARVEST, 2 CHOP, 3 DROP, 4 MINE,
    5-8 PLANT plum/lemon/apple/banana, 9-12 PICK plum/lemon/apple/banana).  **A MOVE label is the
    cell the troll actually reached in the next snapshot -- the referee's step, not the intent** --
    and a troll given no command (or WAIT) is labelled MOVE to the cell it is standing on, which is
    the encoding of WAIT.  Every non-MOVE verb is labelled at the troll's own pre-turn cell, where
    the mask marks it legal.

The row order inside a turn is the environment's mini-step order: the plan row first, then the
troll rows in troll-id order (parent card, amendment 4).

**What this file does NOT do yet, and why.**  The 104 observation planes are not built here: the
plane table `local_claude_1/nn-bot/OBS-PLANES.md` is not signed yet, and a plane builder written
before the table would be a second source of truth rather than the drift test's independent second
implementation.  This half is separable because the labels come out of the reconstruction and do
not depend on the plane layout at all.  `--out` therefore writes label shards; the observation
shard is added when the table is signed and its per-row cost is stated below in the report.

**Plan labels are censused, not frozen** (chatgpt_1's blocker, 2026-08-29 17:44Z): teachers buy
talents outside the 144-way vocabulary (Bubaptik buys speed 4).  This script never coerces such a
tuple.  It counts it, names it, and labels the row `OOV` (-1); the coordinator's ruling decides
whether the vocabulary widens or the teacher population narrows.

Usage:

    # the day-2 pilot on the 10-game slice
    python3 local_claude_1/nn-bot/build_dataset.py \
        --replays local_claude_1/nn-bot/replays-slice-10 \
        --out local_claude_1/nn-bot/results/pilot --report

    # one game, printing the first rows
    python3 local_claude_1/nn-bot/build_dataset.py --replays <dir> --game 891203441 --show 5
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))                                   # sim.engine, sim.state
sys.path.insert(0, str(REPO / "local_claude_1" / "reconstructions" / "fits"))

import reconstruct as rc                                        # noqa: E402

# --- the action vocabulary (parent card, "The actions") ------------------------------------

GRID_W, GRID_H = 22, 11                                         # the padded board of the tensor
CELLS = GRID_W * GRID_H                                         # 242
VERBS = ("MOVE", "HARVEST", "CHOP", "DROP", "MINE",
         "PLANT_PLUM", "PLANT_LEMON", "PLANT_APPLE", "PLANT_BANANA",
         "PICK_PLUM", "PICK_LEMON", "PICK_APPLE", "PICK_BANANA")
PLANE_OF_VERB = {v: i for i, v in enumerate(VERBS)}
TYPES = ("PLUM", "LEMON", "APPLE", "BANANA")

PLAN_SPEED, PLAN_CARRY, PLAN_HARVEST, PLAN_CHOP = (1, 3), (1, 4), (0, 2), (0, 3)
PLAN_NOTHING = 0                                                # index 0, repurposed
OOV = -1


def plan_index(speed, carry, harvest, chop):
    """The 144-way index, or None when the tuple is outside the signed vocabulary."""
    for v, (lo, hi) in ((speed, PLAN_SPEED), (carry, PLAN_CARRY),
                        (harvest, PLAN_HARVEST), (chop, PLAN_CHOP)):
        if not (lo <= v <= hi):
            return None
    return (((speed - 1) * 4 + (carry - 1)) * 3 + harvest) * 4 + chop


def plan_talents(index):
    """The inverse, for reading a shard back."""
    chop = index % 4
    harvest = (index // 4) % 3
    carry = (index // 12) % 4 + 1
    speed = index // 48 + 1
    return speed, carry, harvest, chop


def flat(plane, x, y):
    return plane * CELLS + y * GRID_W + x


def unflat(index):
    plane, rest = divmod(index, CELLS)
    y, x = divmod(rest, GRID_W)
    return plane, x, y


def relative(x, y, seat, w, h):
    """The board is always presented player-relative: seat 1 sees it rotated 180 degrees.

    The rotation is over the map's own `w x h`, not over the padded 22x11 grid, and the padded
    grid is top-left aligned.  Both choices are open questions for the signed OBS-PLANES.md and
    are reported as such -- they change no label on a 22x11 map, which every map in the slice is.
    """
    if seat == 1:
        return w - 1 - x, h - 1 - y
    return x, y


# --- one game ------------------------------------------------------------------------------

def rows_for_game(game_id, replay_dir, teacher_seat, census):
    """Every row of one game for one seat, in mini-step order.  Returns (rows, meta)."""
    rc.RAW = Path(replay_dir)
    r, states = rc.reconstruct(game_id)
    w, h = r.map["w"], r.map["h"]

    # every TRAIN the teacher issues, turn -> talents (the referee accepts one a turn)
    trains = {}
    for t in range(1, r.n_turns + 1):
        for cmd in r.commands(t)[teacher_seat]:
            p = cmd.split()
            if p and p[0].upper() == "TRAIN":
                trains[t] = tuple(int(v) for v in p[1:5])

    # the hindsight plan label: the next TRAIN at or after this turn
    turns_with_train = sorted(trains)
    plan_label = {}
    nxt = 0
    for t in range(r.n_turns, 0, -1):
        if t in trains:
            nxt = t
        if nxt:
            tal = trains[nxt]
            idx = plan_index(*tal)
            if idx is None:
                census["oov_tuples"][tal] += 1
                plan_label[t] = OOV
            else:
                plan_label[t] = idx
        else:
            plan_label[t] = PLAN_NOTHING

    rows = []
    for t in range(1, r.n_turns + 1):
        pre, post = states[t - 1], states[t]
        assert pre["turn"] == t
        cmds = r.commands(t)[teacher_seat]
        mine = sorted((u for u in pre["units"] if u["player"] == teacher_seat),
                      key=lambda u: u["id"])
        pos_after = {u["id"]: (u["x"], u["y"]) for u in post["units"]}

        rows.append(dict(game=game_id, turn=t, seat=teacher_seat, kind=0, troll=-1,
                         verb=-1, label=plan_label[t]))

        given = {}
        for cmd in cmds:
            p = cmd.split()
            if not p:
                continue
            verb = p[0].upper()
            if verb in ("TRAIN", "MSG", "WAIT"):
                continue
            uid = int(p[1])
            if uid in given:                      # the referee keeps the first command per troll
                continue
            given[uid] = (verb, p[2:])

        for u in mine:
            uid = u["id"]
            cx, cy = relative(u["x"], u["y"], teacher_seat, w, h)
            if uid not in given:
                plane, x, y = 0, cx, cy           # no command, or WAIT -> MOVE to own cell
                census["verbs"]["WAIT_or_silent"] += 1
            else:
                verb, args = given[uid]
                if verb == "MOVE":
                    ax, ay = pos_after.get(uid, (u["x"], u["y"]))
                    x, y = relative(ax, ay, teacher_seat, w, h)
                    plane = 0
                    census["verbs"]["MOVE" if (x, y) != (cx, cy) else "MOVE_stayed"] += 1
                elif verb in ("PLANT", "PICK"):
                    kind = args[0].upper()
                    if kind not in TYPES:
                        census["unparsed"][cmd] += 1
                        continue
                    plane = PLANE_OF_VERB[f"{verb}_{kind}"]
                    x, y = cx, cy
                    census["verbs"][f"{verb}_{kind}"] += 1
                elif verb in ("HARVEST", "CHOP", "DROP", "MINE"):
                    plane, x, y = PLANE_OF_VERB[verb], cx, cy
                    census["verbs"][verb] += 1
                else:
                    census["unparsed"][cmd] += 1
                    continue
            rows.append(dict(game=game_id, turn=t, seat=teacher_seat, kind=1, troll=uid,
                             verb=plane, label=flat(plane, x, y)))

    meta = dict(game=game_id, turns=r.n_turns, w=w, h=h, seat=teacher_seat,
                mismatch=dict(r.mismatch), trains=len(trains),
                train_turns=turns_with_train[:8])
    return rows, meta


# --- shards --------------------------------------------------------------------------------

FIELDS = ("game", "turn", "seat", "kind", "troll", "verb", "label")


def write_shard(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {f: np.array([r[f] for r in rows], dtype=np.int32) for f in FIELDS}
    np.savez_compressed(path, **arrays)
    return path.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replays", required=True)
    ap.add_argument("--index", default=None, help="index.json naming the teacher seat per game")
    ap.add_argument("--game", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    replay_dir = Path(a.replays)
    index_path = Path(a.index) if a.index else replay_dir / "index.json"
    index = {int(g["gameId"]): g for g in json.loads(index_path.read_text())}
    games = [int(a.game)] if a.game else sorted(index)

    census = dict(verbs=Counter(), oov_tuples=Counter(), unparsed=Counter())
    all_rows, metas = [], []
    for gid in games:
        rows, meta = rows_for_game(gid, replay_dir, int(index[gid]["seat"]), census)
        meta["player"] = index[gid]["player"]
        meta["rows"] = len(rows)
        all_rows.extend(rows)
        metas.append(meta)
        print(f"game {gid} ({meta['player']}, seat {meta['seat']}): {len(rows)} rows, "
              f"{meta['turns']} turns, {meta['w']}x{meta['h']}, {meta['trains']} TRAINs, "
              f"reconstruction mismatches {meta['mismatch'] or '{}'}", flush=True)

    if a.show:
        print(f"\nfirst {a.show} rows:")
        for r in all_rows[:a.show]:
            if r["kind"] == 0:
                tal = "nothing" if r["label"] == PLAN_NOTHING else (
                    "OUT OF VOCABULARY" if r["label"] == OOV else plan_talents(r["label"]))
                print(f"  plan  game {r['game']} turn {r['turn']} seat {r['seat']} "
                      f"label {r['label']} -> {tal}")
            else:
                plane, x, y = unflat(r["label"])
                print(f"  troll {r['troll']} game {r['game']} turn {r['turn']} seat {r['seat']} "
                      f"label {r['label']} -> {VERBS[plane]} at ({x},{y})")

    size = None
    if a.out:
        size = write_shard(all_rows, Path(a.out) / "labels-pilot.npz")
        (Path(a.out) / "labels-pilot-meta.json").write_text(json.dumps(
            dict(games=metas, verbs=dict(census["verbs"]),
                 oov=[[list(k), v] for k, v in census["oov_tuples"].items()],
                 unparsed=dict(census["unparsed"]), rows=len(all_rows), bytes=size), indent=1))

    if a.report:
        n = len(all_rows)
        plan = [r for r in all_rows if r["kind"] == 0]
        cmd = [r for r in all_rows if r["kind"] == 1]
        print(f"\nrows: {n} total = {len(plan)} plan + {len(cmd)} command "
              f"({len(games)} games)")
        print("command labels per verb:")
        for v, c in sorted(census["verbs"].items(), key=lambda kv: -kv[1]):
            print(f"  {v:18s} {c:6d}  {100*c/max(1,len(cmd)):5.1f} %")
        hist = Counter(r["label"] for r in plan)
        print(f"plan labels: {len(hist)} distinct; "
              f"nothing {hist[PLAN_NOTHING]}, out-of-vocabulary {hist[OOV]}")
        for lab, c in hist.most_common(8):
            name = "nothing" if lab == PLAN_NOTHING else (
                "OUT OF VOCABULARY" if lab == OOV else plan_talents(lab))
            print(f"  {lab:5d} {str(name):22s} {c:6d}")
        if census["oov_tuples"]:
            print("out-of-vocabulary TRAIN tuples (speed carry harvest chop -> plan rows):")
            for tup, c in census["oov_tuples"].most_common():
                print(f"  {tup} -> {c}")
        if census["unparsed"]:
            print("unparsed commands:", dict(census["unparsed"]))
        if size:
            print(f"shard: {size} bytes for {n} rows = "
                  f"{1000*size/max(1,n):.0f} bytes per 1,000 label rows")
            print(f"the observation half, when the plane table is signed, is "
                  f"104*11*22 = {104*CELLS} bytes a row uncompressed "
                  f"({104*CELLS*1000/1e6:.1f} MB per 1,000 rows)")


if __name__ == "__main__":
    main()
