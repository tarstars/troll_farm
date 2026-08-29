#!/usr/bin/env python3
"""The clone's dataset builder (Track N, Phase 2, card
`coordination/tasks/20260829-nn-bot-way-b-dataset.md`) -- **the label half**.

From the exact reconstruction (`local_claude_1/reconstructions/fits/reconstruct.py`) this writes,
for every turn of a teacher's game, the rows the clone is trained on:

  * one **plan row** per turn: label = the 400-way index of the talents of the **next TRAIN the
    teacher actually issues** after this turn, or 0 ("train nothing") if it issues none before the
    end.  The vocabulary is amendment 8 of the parent card (the coordinator's ruling of
    2026-08-29 17:58Z, from the census below): speed 1-4 x carry 1-5 x harvest 0-3 x chop 0-4,
    index `(((speed-1)*5 + (carry-1))*4 + harvest)*5 + chop`, and index 0 (speed 1, carry 1, no
    harvest, no chop) is repurposed as "train nothing".
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

**Plan labels are censused, never coerced** (chatgpt_1's blocker, 2026-08-29 17:44Z; ruled at
17:58Z).  A TRAIN tuple outside the vocabulary is counted, named and labelled `OOV` (-1) -- it is
never silently folded onto a neighbouring index, and in particular a parsed `(1,1,0,0)` reaches
index 0 only because that tuple really is "speed 1, carry 1, no harvest, no chop"; the
"train nothing" row carries `troll = -2` so the two are distinguishable in the shard
(chatgpt_1's mask-totality point, 18:02Z).  `--census-tables` runs the same guard over the whole
teacher set's exact tables and must report zero.

**The shard carries states, not planes** (the coordinator's ruling 1, 17:58Z).  The 104 planes are
about 25 kB a row -- ~20 TB over the teacher set -- while the per-turn state they are built from is
~54 bytes gzipped.  So `--out` writes the labels (`labels-*.npz`), the per-turn compact states
(`states-*.jsonl.gz`) and the metadata, and the planes are built at load time by the Rust
`tf_full_obs_from_state` the environment uses.  The Python plane builder stays the drift test's
second implementation and is not written here until `OBS-PLANES.md` is signed.

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
import gzip
import hashlib
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

PLAN_SPEED, PLAN_CARRY, PLAN_HARVEST, PLAN_CHOP = (1, 4), (1, 5), (0, 3), (0, 4)
PLAN_ACTION_SIZE = 400                                          # amendment 8
PLAN_NOTHING = 0                                                # index 0, repurposed
OOV = -1
KIND_PLAN, KIND_COMMAND = 0, 1
TROLL_PLAN, TROLL_NOTHING = -1, -2                              # the plan row's `troll` column


def plan_index(speed, carry, harvest, chop):
    """The 400-way index, or None when the tuple is outside the signed vocabulary."""
    for v, (lo, hi) in ((speed, PLAN_SPEED), (carry, PLAN_CARRY),
                        (harvest, PLAN_HARVEST), (chop, PLAN_CHOP)):
        if not (lo <= v <= hi):
            return None
    return (((speed - 1) * 5 + (carry - 1)) * 4 + harvest) * 5 + chop


def plan_talents(index):
    """The inverse, for reading a shard back."""
    chop = index % 5
    harvest = (index // 5) % 4
    carry = (index // 20) % 5 + 1
    speed = index // 100 + 1
    return speed, carry, harvest, chop


def plan_mask_forbids(speed, carry, harvest, chop):
    """The parent card's mask rules, as a *reported* predicate, never as a coercion.

    The card masks `harvest == 0 and chop == 0` and `harvest > carry`.  Neither is a rule of the
    game: `sim/engine.py::apply_train` charges `n + stat**2` per talent and refuses only on
    affordability and on an occupied shack.  Real teachers issue tuples this mask forbids, so the
    builder labels them honestly and counts them here rather than dropping the row."""
    reasons = []
    if harvest == 0 and chop == 0:
        reasons.append("harvest0_and_chop0")
    if harvest > carry:
        reasons.append("harvest>carry")
    return reasons


def flat(plane, x, y):
    return plane * CELLS + y * GRID_W + x


def unflat(index):
    plane, rest = divmod(index, CELLS)
    y, x = divmod(rest, GRID_W)
    return plane, x, y


def relative(x, y, seat, w, h):
    """The board is always presented player-relative: seat 1 sees it rotated 180 degrees.

    The rotation is over the map's own `w x h`, not over the padded 22x11 grid, and the padded
    grid is top-left aligned.  Both conventions were signed by the coordinator on 2026-08-29
    17:58Z (ruling 3, the wording of `OBS-PLANES.md`: "real coordinates are rotated inside the
    actual w by h board and then placed at the tensor's top left").
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
                for reason in plan_mask_forbids(*tal):
                    census["mask_forbids"][f"{reason} {tal}"] += 1
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

        lab = plan_label[t]
        rows.append(dict(game=game_id, turn=t, seat=teacher_seat, kind=KIND_PLAN,
                         troll=TROLL_NOTHING if lab == PLAN_NOTHING else TROLL_PLAN,
                         verb=-1, label=lab))

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
            rows.append(dict(game=game_id, turn=t, seat=teacher_seat, kind=KIND_COMMAND,
                             troll=uid, verb=plane, label=flat(plane, x, y)))

    meta = dict(game=game_id, turns=r.n_turns, w=w, h=h, seat=teacher_seat,
                mismatch=dict(r.mismatch), trains=len(trains),
                train_turns=turns_with_train[:8])
    # the compact per-turn state the planes are built from at load time (ruling 1): the state
    # every row of turn `t` observes, i.e. the pre-turn snapshot, keyed by (game, turn).
    turn_states = [dict(game=game_id, turn=t, seat=teacher_seat, state=states[t - 1])
                   for t in range(1, r.n_turns + 1)]
    return rows, meta, turn_states


# --- augmentation and the held-out split ----------------------------------------------------

def seat_swapped(rows, w, h):
    """The same game read from the other seat's frame (the card's seat-swap augmentation).

    The observation is player-relative, so a swap is not a second copy of the state: the loader
    passes the flipped seat to the same `tf_full_obs_from_state`, and only the *label* has to move
    -- 180 degrees inside the map's own `w x h`, exactly the transform `relative` applies.  The
    plan label is a talent tuple and does not move at all.
    """
    out = []
    for r in rows:
        q = dict(r, seat=1 - r["seat"], aug=1)
        if r["kind"] == KIND_COMMAND:
            plane, x, y = unflat(r["label"])
            q["label"] = flat(plane, w - 1 - x, h - 1 - y)
        out.append(q)
    return out


def held_out(game_id, percent):
    """A deterministic by-game split: the same game lands the same side on every machine."""
    if percent <= 0:
        return 0
    digest = hashlib.sha1(str(game_id).encode()).hexdigest()
    return 1 if int(digest[:8], 16) % 100 < percent else 0


# --- shards --------------------------------------------------------------------------------

FIELDS = ("game", "turn", "seat", "kind", "troll", "verb", "label", "aug", "split")


def write_shard(rows, turn_states, out_dir, name):
    """Labels, compact states and metadata -- never planes (the coordinator's ruling 1)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = out_dir / f"labels-{name}.npz"
    arrays = {f: np.array([r[f] for r in rows], dtype=np.int32) for f in FIELDS}
    np.savez_compressed(labels, **arrays)
    states = out_dir / f"states-{name}.jsonl.gz"
    with gzip.open(states, "wt", compresslevel=9) as fh:
        for entry in turn_states:
            fh.write(json.dumps(entry, separators=(",", ":")) + "\n")
    return labels.stat().st_size, states.stat().st_size


# --- the total-label guard over the whole teacher set ---------------------------------------

def census_tables(tables_dir):
    """The vocabulary guard the coordinator kept: every TRAIN of the exact reconstruction tables.

    It must report zero out-of-vocabulary tuples under the signed vocabulary.  It also reports the
    tuples the parent card's *mask* forbids, which is a different question and not zero.
    """
    files = sorted(Path(tables_dir).glob("*_turns.jsonl.gz"))
    if not files:
        raise SystemExit(f"no *_turns.jsonl.gz under {tables_dir}")
    oov, forbidden, per_player, games = Counter(), Counter(), Counter(), set()
    labels, total = Counter(), 0
    for path in files:
        player = path.name[:-len("_turns.jsonl.gz")]
        with gzip.open(path, "rt") as fh:
            for line in fh:
                row = json.loads(line)
                games.add((player, row["g"]))
                talents = row.get("train")
                if not talents:
                    continue
                total += 1
                per_player[player] += 1
                idx = plan_index(*talents)
                if idx is None:
                    oov[tuple(talents)] += 1
                    continue
                labels[idx] += 1
                for reason in plan_mask_forbids(*talents):
                    forbidden[reason] += 1
    print(f"census over {len(files)} teachers, {len(games)} games, {total} TRAINs")
    print(f"  vocabulary: PLAN_ACTION_SIZE = {PLAN_ACTION_SIZE}; distinct labels used "
          f"{len(labels)}; indices {min(labels)}..{max(labels)}")
    print(f"  OUT OF VOCABULARY: {sum(oov.values())}" + (f"  {dict(oov)}" if oov else "  (zero)"))
    print(f"  TRAINs per teacher: {dict(per_player)}")
    print(f"  tuples the card's mask forbids: {sum(forbidden.values())} "
          f"{dict(forbidden) or '(none)'}")
    for idx, count in labels.most_common(5):
        print(f"    {idx:5d} {str(plan_talents(idx)):16s} {count:5d}")
    return sum(oov.values())


def self_test():
    """The codec's own checks: the 400-way index is a bijection, the mask never coerces, and the
    seat swap is an involution.  Cheap enough to run before every build."""
    seen = set()
    for speed in range(1, 5):
        for carry in range(1, 6):
            for harvest in range(0, 4):
                for chop in range(0, 5):
                    idx = plan_index(speed, carry, harvest, chop)
                    assert idx is not None and 0 <= idx < PLAN_ACTION_SIZE, (speed, carry, idx)
                    assert plan_talents(idx) == (speed, carry, harvest, chop), idx
                    seen.add(idx)
    assert len(seen) == PLAN_ACTION_SIZE, len(seen)
    assert plan_index(1, 1, 0, 0) == PLAN_NOTHING
    # nothing outside the vocabulary is ever folded onto a valid index
    for bad in ((5, 1, 0, 0), (1, 6, 0, 0), (1, 1, 4, 0), (1, 1, 0, 5), (0, 1, 0, 0)):
        assert plan_index(*bad) is None, bad
    # a tuple the card's mask forbids is still labelled, and named
    assert plan_index(2, 1, 2, 2) is not None
    assert plan_mask_forbids(2, 1, 2, 2) == ["harvest>carry"]
    assert plan_mask_forbids(2, 2, 1, 1) == []
    # the seat swap is an involution on the label, and the plan label does not move
    w, h = 20, 10
    rows = [dict(game=1, turn=1, seat=0, kind=KIND_COMMAND, troll=3, verb=2,
                 label=flat(2, 7, 4), aug=0, split=0),
            dict(game=1, turn=1, seat=0, kind=KIND_PLAN, troll=TROLL_PLAN, verb=-1,
                 label=147, aug=0, split=0)]
    once = seat_swapped(rows, w, h)
    assert unflat(once[0]["label"]) == (2, w - 1 - 7, h - 1 - 4)
    assert once[1]["label"] == 147 and once[0]["seat"] == 1
    twice = seat_swapped(once, w, h)
    assert twice[0]["label"] == rows[0]["label"] and twice[0]["seat"] == 0
    # the by-game split is deterministic and roughly the requested size
    assert all(held_out(g, 0) == 0 for g in range(50))
    share = sum(held_out(g, 20) for g in range(1000)) / 1000
    assert 0.15 <= share <= 0.25, share
    assert held_out(891153730, 20) == held_out(891153730, 20)
    print(f"self-test OK: {PLAN_ACTION_SIZE}-way codec bijective, mask reported not coerced, "
          f"seat swap involutive, split deterministic ({100*share:.1f} % at --holdout 20)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replays", default=None)
    ap.add_argument("--index", default=None, help="index.json naming the teacher seat per game")
    ap.add_argument("--game", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--name", default="pilot", help="the shard's name")
    ap.add_argument("--seat-swap", action="store_true", help="add the seat-swapped rows")
    ap.add_argument("--holdout", type=int, default=0, help="percent of games held out, by game")
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--census-tables", default=None,
                    help="run the vocabulary guard over the teacher set's exact tables and exit")
    ap.add_argument("--self-test", action="store_true", help="check the codec and exit")
    a = ap.parse_args()

    if a.self_test:
        self_test()
        return
    if a.census_tables:
        sys.exit(0 if census_tables(a.census_tables) == 0 else 1)
    if not a.replays:
        raise SystemExit("--replays is required unless --census-tables is given")

    replay_dir = Path(a.replays)
    index_path = Path(a.index) if a.index else replay_dir / "index.json"
    index = {int(g["gameId"]): g for g in json.loads(index_path.read_text())}
    games = [int(a.game)] if a.game else sorted(index)

    census = dict(verbs=Counter(), oov_tuples=Counter(), unparsed=Counter(),
                  mask_forbids=Counter())
    all_rows, all_states, metas = [], [], []
    for gid in games:
        rows, meta, turn_states = rows_for_game(gid, replay_dir, int(index[gid]["seat"]), census)
        split = held_out(gid, a.holdout)
        for r in rows:
            r["aug"], r["split"] = 0, split
        if a.seat_swap:
            rows = rows + seat_swapped(rows, meta["w"], meta["h"])
        meta["player"] = index[gid]["player"]
        meta["rows"] = len(rows)
        meta["split"] = split
        all_rows.extend(rows)
        all_states.extend(turn_states)
        metas.append(meta)
        print(f"game {gid} ({meta['player']}, seat {meta['seat']}): {len(rows)} rows, "
              f"{meta['turns']} turns, {meta['w']}x{meta['h']}, {meta['trains']} TRAINs, "
              f"{'held out' if split else 'train'}, "
              f"reconstruction mismatches {meta['mismatch'] or '{}'}", flush=True)

    if a.show:
        print(f"\nfirst {a.show} rows:")
        for r in all_rows[:a.show]:
            if r["kind"] == KIND_PLAN:
                tal = "nothing" if r["troll"] == TROLL_NOTHING else (
                    "OUT OF VOCABULARY" if r["label"] == OOV else plan_talents(r["label"]))
                print(f"  plan  game {r['game']} turn {r['turn']} seat {r['seat']} "
                      f"label {r['label']} -> {tal}")
            else:
                plane, x, y = unflat(r["label"])
                print(f"  troll {r['troll']} game {r['game']} turn {r['turn']} seat {r['seat']} "
                      f"label {r['label']} -> {VERBS[plane]} at ({x},{y})")

    label_bytes = state_bytes = None
    if a.out:
        label_bytes, state_bytes = write_shard(all_rows, all_states, Path(a.out), a.name)
        (Path(a.out) / f"labels-{a.name}-meta.json").write_text(json.dumps(
            dict(plan_action_size=PLAN_ACTION_SIZE, games=metas, verbs=dict(census["verbs"]),
                 oov=[[list(k), v] for k, v in census["oov_tuples"].items()],
                 mask_forbids=dict(census["mask_forbids"]),
                 unparsed=dict(census["unparsed"]), rows=len(all_rows),
                 turn_states=len(all_states), label_bytes=label_bytes,
                 state_bytes=state_bytes, seat_swap=bool(a.seat_swap),
                 holdout_percent=a.holdout), indent=1))

    if a.report:
        n = len(all_rows)
        plan = [r for r in all_rows if r["kind"] == KIND_PLAN]
        cmd = [r for r in all_rows if r["kind"] == KIND_COMMAND]
        print(f"\nrows: {n} total = {len(plan)} plan + {len(cmd)} command "
              f"({len(games)} games, {len(all_states)} turn states)")
        if a.holdout:
            out = sum(1 for r in all_rows if r["split"])
            print(f"held out: {out} rows ({100*out/max(1,n):.1f} %) from "
                  f"{sum(1 for m in metas if m['split'])} of {len(metas)} games")
        # the census counts the teacher's own commands once; the seat-swapped rows carry the
        # same verbs, so the shares are taken against the un-augmented command rows.
        base = max(1, sum(1 for r in cmd if r["aug"] == 0))
        print(f"command labels per verb (of {base} un-augmented command rows):")
        for v, c in sorted(census["verbs"].items(), key=lambda kv: -kv[1]):
            print(f"  {v:18s} {c:6d}  {100*c/base:5.1f} %")
        hist = Counter(r["label"] for r in plan)
        nothing = sum(1 for r in plan if r["troll"] == TROLL_NOTHING)
        print(f"plan labels: {len(hist)} distinct; "
              f"nothing {nothing}, out-of-vocabulary {hist[OOV]}")
        for lab, c in hist.most_common(8):
            name = "OUT OF VOCABULARY" if lab == OOV else plan_talents(lab)
            print(f"  {lab:5d} {str(name):22s} {c:6d}")
        if census["oov_tuples"]:
            print("out-of-vocabulary TRAIN tuples (speed carry harvest chop -> plan rows):")
            for tup, c in census["oov_tuples"].most_common():
                print(f"  {tup} -> {c}")
        if census["mask_forbids"]:
            print("plan labels the card's mask forbids (labelled honestly, never coerced):")
            for reason, c in census["mask_forbids"].most_common():
                print(f"  {reason} -> {c} rows")
        if census["unparsed"]:
            print("unparsed commands:", dict(census["unparsed"]))
        if label_bytes:
            print(f"shard: labels {label_bytes} bytes for {n} rows = "
                  f"{1000*label_bytes/max(1,n):.0f} bytes per 1,000 label rows; "
                  f"states {state_bytes} bytes for {len(all_states)} turns = "
                  f"{state_bytes/max(1,len(all_states)):.0f} bytes a turn")
            print(f"the planes are NOT stored: one row is 104*11*22 = {104*CELLS} bytes "
                  f"({104*CELLS*1000/1e6:.1f} MB per 1,000 rows); they are built at load time "
                  f"from the states above by the same Rust builder the environment uses")


if __name__ == "__main__":
    main()
