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
17:58Z, completed 18:16Z).  A TRAIN the teacher really issued gets a label only if the codec has
one for it: a tuple outside the box, *and the in-range tuple `(1,1,0,0)` whose index is repurposed
as "train nothing"*, are counted, named and labelled `OOV` (-1) rather than folded onto a
neighbour.  A "train nothing" row carries `troll = -2` and a real plan row `troll = -1`, so the
two are distinguishable in the shard.  `--census-tables` runs the same guard over the whole
teacher set's exact tables and must report zero on both counts.

**The mask has exactly one rule** (the card's second completion of amendment 8, 18:5xZ): entry 0
is "train nothing" and every in-range entry is legal.  Day 3's census is what turned the ruling:
`harvest > carry` was delineate's restriction and Bubaptik breaks it in 44 of its 425 purchases,
and `harvest 0 and chop 0` is legal in the game and issued by no teacher (0 of 1,725).  So no real
label is unreachable and the codec is total under the mask.

**No target memory in cloning, and no seat augmentation** (the same ruling, points (b) and (d),
on chatgpt_1's correction of 18:40Z; the row kinds separated by the coordinator's ruling 2 of
18:23Z).  A **plan row** carries `standing_plan = 0` ("none") and the plane builder zeroes planes
59-71 with it: between two purchases the previous turn's hindsight label *is* this turn's label,
so feeding it as the standing target would mark the answer on almost every row -- held-out games
do not remove a leak that lives inside the row.  A **troll row** carries the turn's own hindsight
plan, which is exactly what the environment shows once the plan mini-step has been taken, and is
no leak, because a troll's label is a command and not the plan.  And the seat swap is withdrawn: the observation
is already player-relative, so flipping a label onto a state rebuilt from the other seat is a
different example wearing the first one's label, not an augmentation of it.

**One generation id.** `PLAN_VOCAB_VERSION = "v400-2026-08-29"` is written into every shard's
metadata and checked by `read_shard`, so a 400-label shard cannot be trained against a 144-logit
runtime or the reverse.

**The shard carries states, not planes** (the coordinator's ruling 1, 17:58Z).  The 104 planes are
about 25 kB a row -- ~20 GB over the teacher set's ~800,000 rows -- while the per-turn state they
are built from is ~58 bytes gzipped.  (Day 3's write-up said 20 TB; it was wrong by a thousand,
corrected by the card at 18:5xZ.  The compact shard stands on size and on the drift discipline of
one plane builder, not on impossibility.)  So `--out` writes the labels (`labels-*.npz`), the per-turn compact states
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
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))                                   # nn_runtime
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
PLAN_VOCAB_VERSION = "v400-2026-08-29"                          # amendment 8's generation id
PLAN_NOTHING = 0                                                # index 0, repurposed
OOV = -1
KIND_PLAN, KIND_COMMAND = 0, 1
#: The standing target the row's planes 59-71 must show, by row kind (the coordinator's ruling 2
#: of 18:23Z, on chatgpt_1's leakage correction).
#:
#: * A **plan row** carries `STANDING_PLAN_NONE` and the plane builder zeroes 59-71 with it.  In
#:   behaviour cloning the standing target would be the previous turn's hindsight label, and
#:   between two purchases that *is* this turn's label -- it would mark the answer on almost every
#:   row, and holding games out does not remove a leak that lives inside the row.  In PPO the
#:   standing target is the environment's own state (the policy's previous choice) and is honest.
#: * A **troll row** carries the turn's own hindsight plan, which is what the environment really
#:   shows after the plan mini-step has been taken, and is no leak: the troll's label is a command,
#:   not the plan.
STANDING_PLAN_NONE = 0
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


def plan_index_is_legal(index):
    """Amendment 8's mask, second completion (the card, 18:5xZ): **exactly one rule**.

    Entry 0 ("train nothing") is always legal, and so is every other in-range entry.  The two
    rules the card carried before -- `harvest == 0 and chop == 0` and `harvest > carry` -- were
    delineate's own restrictions, not the game's: `sim/engine.py::apply_train` charges
    `n + stat**2` per talent and refuses only on affordability and on an occupied shack, and
    Bubaptik issues `harvest > carry` in 44 of its 425 purchases (day 3's census, which is what
    the ruling turned on).  Affordability never masks either -- the plan is a target the trolls
    collect towards.  At run time the global unit cap masks all but entry 0; that is the
    environment's business, not the shard's.
    """
    return 0 <= index < PLAN_ACTION_SIZE


def plan_index_of_train(talents):
    """The label of a TRAIN the teacher really issued, or None when it is unsupported.

    Codec totality (the coordinator's handoff of 18:16Z, item 1).  Two ways a real purchase has
    no label: a talent outside the 400-way box, and the tuple `(1, 1, 0, 0)` -- a legal purchase
    in the game, but index 0 is repurposed as "train nothing", so a *parsed* `(1,1,0,0)` is
    reported unsupported and is never quietly relabelled "the teacher trained nothing".
    (No teacher issues it: 0 of 1,725.)
    """
    idx = plan_index(*talents)
    if idx is None or idx == PLAN_NOTHING:
        return None
    return idx


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
            idx = plan_index_of_train(tal)
            if idx is None:
                census["unsupported"][tal] += 1
                plan_label[t] = OOV
            else:
                plan_label[t] = idx
                if not plan_index_is_legal(idx):        # cannot happen under the single rule
                    census["masked_label"][str(tal)] += 1
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
        # what the troll rows of this turn see in planes 59-71: the plan just decided.  An
        # unsupported label has no index to show, so those rows fall back to "none" and are
        # counted (the count is zero over the teacher set).
        standing = lab if lab != OOV else STANDING_PLAN_NONE
        if lab == OOV:
            census["standing_unsupported"] += 1
        rows.append(dict(game=game_id, turn=t, seat=teacher_seat, kind=KIND_PLAN,
                         troll=TROLL_NOTHING if lab == PLAN_NOTHING else TROLL_PLAN,
                         verb=-1, label=lab, standing_plan=STANDING_PLAN_NONE))

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
                             troll=uid, verb=plane, label=flat(plane, x, y),
                             standing_plan=standing))

    meta = dict(game=game_id, turns=r.n_turns, w=w, h=h, seat=teacher_seat,
                mismatch=dict(r.mismatch), trains=len(trains),
                train_turns=turns_with_train[:8],
                # the game's map, kept out of the per-turn states because one map serves every
                # turn; `write_shard` puts it in `maps-<name>.json`, which is what the load-time
                # plane builder needs and what the day-4 shard was missing (day 6).
                map=dict(w=w, h=h, rows=list(r.map["rows"])))
    # the compact per-turn state the planes are built from at load time (ruling 1): the state
    # every row of turn `t` observes, i.e. the pre-turn snapshot, keyed by (game, turn).
    turn_states = [dict(game=game_id, turn=t, seat=teacher_seat, state=states[t - 1])
                   for t in range(1, r.n_turns + 1)]
    return rows, meta, turn_states


# --- augmentation and the held-out split ----------------------------------------------------

def seat_swapped(*_args, **_kwargs):
    """Withdrawn by the card (second completion of amendment 8, point (d), 18:5xZ).

    The observation is already player-relative, so the seat is canonicalized before the network
    ever sees it; flipping the label while the state is rebuilt from the *other* seat is not an
    augmentation of the same example but a different example with the first one's label.  Kept as
    a raising stub so that no caller silently gets the old behaviour back.
    """
    raise RuntimeError("seat-swap augmentation was withdrawn by the card on 2026-08-29 18:5xZ")


def check_standing_target(rows):
    """Ruling 2 of 18:23Z, checked on the rows actually built, not argued for in a comment.

    A plan row's standing target is "none"; a troll row's is its own turn's plan label (or "none"
    when that label is unsupported).  Raises on the first row that breaks it.
    """
    plan_of_turn = {(r["game"], r["turn"], r["seat"]): r["label"]
                    for r in rows if r["kind"] == KIND_PLAN}
    for r in rows:
        key = (r["game"], r["turn"], r["seat"])
        if r["kind"] == KIND_PLAN:
            want = STANDING_PLAN_NONE
        else:
            lab = plan_of_turn[key]
            want = STANDING_PLAN_NONE if lab == OOV else lab
        if r["standing_plan"] != want:
            raise AssertionError(f"standing target {r['standing_plan']} != {want} on {r}")
    return len(rows)


def held_out(game_id, percent):
    """A deterministic by-game split: the same game lands the same side on every machine."""
    if percent <= 0:
        return 0
    digest = hashlib.sha1(str(game_id).encode()).hexdigest()
    return 1 if int(digest[:8], 16) % 100 < percent else 0


# --- shards --------------------------------------------------------------------------------

FIELDS = ("game", "turn", "seat", "kind", "troll", "verb", "label",
          "standing_plan", "split")


def read_shard(out_dir, name):
    """Read a shard back, refusing one built by a different vocabulary generation.

    The generation id (`PLAN_VOCAB_VERSION`, amendment 8) is written into every shard's metadata
    and checked here on the way in: a 400-label shard loaded against a 144-logit runtime, or the
    reverse, raises instead of training on relabelled nonsense.  The trainer and the exporter make
    the same check against a checkpoint's `config`.
    """
    out_dir = Path(out_dir)
    meta = json.loads((out_dir / f"labels-{name}-meta.json").read_text())
    got = (meta.get("plan_vocab_version"), meta.get("plan_action_size"))
    want = (PLAN_VOCAB_VERSION, PLAN_ACTION_SIZE)
    if got != want:
        raise ValueError(f"shard {name} was built by plan vocabulary {got}, this code is {want}; "
                         f"refusing to load")
    with np.load(out_dir / f"labels-{name}.npz") as z:
        arrays = {f: z[f] for f in FIELDS}
    return arrays, meta


def read_maps(out_dir, name):
    """`{game id (str) -> {w, h, rows}}` for a shard, or a refusal naming the repair.

    The planes are built at load time from the compact state and its map (`nn_runtime`), so a
    shard without its maps cannot be trained on.  Shards built before 2026-08-30 have no maps
    file; rebuilding them costs the two minutes the coordinator offered.
    """
    path = Path(out_dir) / f"maps-{name}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing: this shard predates the maps file (2026-08-30) and the "
            f"load-time plane builder cannot place a state without its map -- rebuild the "
            f"shard with this builder")
    return json.loads(path.read_text())


def write_shard(rows, turn_states, out_dir, name, maps=None):
    """Labels, compact states, the maps and metadata -- never planes (the coordinator's ruling 1)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = out_dir / f"labels-{name}.npz"
    arrays = {f: np.array([r[f] for r in rows], dtype=np.int32) for f in FIELDS}
    np.savez_compressed(labels, **arrays)
    states = out_dir / f"states-{name}.jsonl.gz"
    with gzip.open(states, "wt", compresslevel=9) as fh:
        for entry in turn_states:
            fh.write(json.dumps(entry, separators=(",", ":")) + "\n")
    maps_path = out_dir / f"maps-{name}.json"
    maps_path.write_text(json.dumps(maps or {}, separators=(",", ":"), sort_keys=True))
    return labels.stat().st_size, states.stat().st_size, maps_path.stat().st_size


# --- the total-label guard over the whole teacher set ---------------------------------------

def census_tables(tables_dir):
    """The total-label guard over every TRAIN of the exact reconstruction tables.

    It reports the two counts the coordinator's handoff of 18:16Z asks for, and exits non-zero if
    either is non-zero: **unsupported** purchases (outside the 400-way box, or the parsed
    `(1,1,0,0)` whose index is repurposed) and **masked-label** purchases (a real TRAIN whose
    label the mask forbids).  Under the second completion of amendment 8 the mask has one rule,
    entry 0, so the second count is zero by construction; it is printed anyway, because a count
    that is only zero by argument is exactly the kind of check that rots silently.  The withdrawn
    restrictions are counted separately and labelled as history, not as a verdict.
    """
    files = sorted(Path(tables_dir).glob("*_turns.jsonl.gz"))
    if not files:
        raise SystemExit(f"no *_turns.jsonl.gz under {tables_dir}")
    unsupported, masked, withdrawn = Counter(), Counter(), Counter()
    per_player, games = Counter(), set()
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
                idx = plan_index_of_train(tuple(talents))
                if idx is None:
                    unsupported[tuple(talents)] += 1
                    continue
                labels[idx] += 1
                if not plan_index_is_legal(idx):
                    masked[str(tuple(talents))] += 1
                speed, carry, harvest, chop = talents
                if harvest > carry:
                    withdrawn["harvest>carry"] += 1
                if harvest == 0 and chop == 0:
                    withdrawn["harvest0_and_chop0"] += 1
    print(f"census over {len(files)} teachers, {len(games)} games, {total} TRAINs")
    print(f"  vocabulary: PLAN_ACTION_SIZE = {PLAN_ACTION_SIZE} "
          f"({PLAN_VOCAB_VERSION}); distinct labels used {len(labels)}; "
          f"indices {min(labels)}..{max(labels)}")
    print(f"  UNSUPPORTED (no label): {sum(unsupported.values())}"
          + (f"  {dict(unsupported)}" if unsupported else "  (zero)"))
    print(f"  MASKED LABELS (label the mask forbids): {sum(masked.values())}"
          + (f"  {dict(masked)}" if masked else "  (zero)"))
    print(f"  TRAINs per teacher: {dict(per_player)}")
    print(f"  under the withdrawn restrictions, for the record: {dict(withdrawn) or '(none)'}")
    for idx, count in labels.most_common(5):
        print(f"    {idx:5d} {str(plan_talents(idx)):16s} {count:5d}")
    return sum(unsupported.values()) + sum(masked.values())


def self_test():
    """The codec's own checks, cheap enough to run before every build.

    Six things: the 400-way index is a bijection over the box; nothing outside the box is folded
    onto a valid index; a *parsed* `(1,1,0,0)` is reported unsupported rather than relabelled
    "train nothing"; the mask has exactly one rule and forbids no in-range label; the withdrawn
    seat swap raises rather than quietly returning; the by-game split is deterministic; and a
    shard built by another vocabulary generation refuses to load.
    """
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
    for bad in ((5, 1, 0, 0), (1, 6, 0, 0), (1, 1, 4, 0), (1, 1, 0, 5), (0, 1, 0, 0)):
        assert plan_index(*bad) is None, bad
        assert plan_index_of_train(bad) is None, bad
    # codec totality: the one in-range tuple that has no label of its own says so
    assert plan_index_of_train((1, 1, 0, 0)) is None
    assert plan_index_of_train((2, 2, 1, 3)) == plan_index(2, 2, 1, 3)
    # the mask, second completion: one rule, and it forbids no in-range label
    assert all(plan_index_is_legal(i) for i in range(PLAN_ACTION_SIZE))
    assert plan_index_is_legal(PLAN_NOTHING)
    assert not plan_index_is_legal(PLAN_ACTION_SIZE) and not plan_index_is_legal(-1)
    # the two withdrawn restrictions really are inside the vocabulary now
    assert plan_index_is_legal(plan_index(2, 1, 2, 2))      # harvest > carry, 44 of Bubaptik's
    assert plan_index_is_legal(plan_index(2, 2, 0, 0))      # harvest 0 and chop 0
    assert STANDING_PLAN_NONE == 0
    # the withdrawn augmentation raises instead of returning the old rows
    try:
        seat_swapped([], 20, 10)
    except RuntimeError:
        pass
    else:                                                   # pragma: no cover
        raise AssertionError("seat_swapped must raise; it was withdrawn")
    # the by-game split is deterministic and roughly the requested size
    assert all(held_out(g, 0) == 0 for g in range(50))
    share = sum(held_out(g, 20) for g in range(1000)) / 1000
    assert 0.15 <= share <= 0.25, share
    assert held_out(891153730, 20) == held_out(891153730, 20)
    # a shard of another vocabulary generation refuses to load
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        rows = [dict(game=1, turn=1, seat=0, kind=KIND_PLAN, troll=TROLL_PLAN, verb=-1,
                     label=147, standing_plan=STANDING_PLAN_NONE, split=0)]
        write_shard(rows, [], tmp, "t", maps={"1": {"w": 20, "h": 10, "rows": ["." * 20] * 10}})
        meta = dict(plan_action_size=PLAN_ACTION_SIZE, plan_vocab_version=PLAN_VOCAB_VERSION)
        (tmp / "labels-t-meta.json").write_text(json.dumps(meta))
        arrays, _ = read_shard(tmp, "t")
        assert arrays["label"][0] == 147 and arrays["standing_plan"][0] == STANDING_PLAN_NONE
        (tmp / "labels-t-meta.json").write_text(json.dumps(
            dict(plan_action_size=144, plan_vocab_version="v144-2026-08-28")))
        try:
            read_shard(tmp, "t")
        except ValueError:
            pass
        else:                                               # pragma: no cover
            raise AssertionError("a 144-way shard must refuse to load against the 400-way codec")
    print(f"self-test OK: {PLAN_ACTION_SIZE}-way codec bijective ({PLAN_VOCAB_VERSION}), "
          f"(1,1,0,0) unsupported not relabelled, one mask rule forbidding no label, "
          f"seat swap withdrawn, split deterministic ({100*share:.1f} % at --holdout 20), "
          f"a foreign-generation shard refuses to load")


def codec_test(out_dir, name, library, limit=0):
    """**The builder's slice test against the amended codec** (the card's day-6/7 item 3).

    Every label this builder writes is put back through the compiled runtime the environment and
    the trainer use, on the shard's own rows:

    1. a command row's label decodes to a command (`tf_full_decode_action`) and that command text
       encodes back to the same index (`tf_full_encode_command`) -- the amended helpers take the
       absolute seat and rotate inside the real board, so this is the seat-1 rotation tested on
       real seat-1 games, not argued for;
    2. the decoded verb is the plane the builder recorded;
    3. a plan row's label decodes to the same talents the builder's own Python codec gives
       (`tf_full_decode_plan` against `plan_talents`);
    4. **the label is legal under the mask the environment would show at that row** -- the
       spatial mask for a command row, the plan mask for a plan row, with the earlier trolls of
       the turn staged exactly as the environment stages them.  This is the check that would
       catch a builder and an environment that had drifted apart: a label the mask forbids is a
       row the clone can never be trained on.

    A refusal is a failure with the row printed, never a repair.
    """
    import nn_runtime as nr                                        # noqa: PLC0415

    out_dir = Path(out_dir)
    arrays, meta = read_shard(out_dir, name)
    maps = read_maps(out_dir, name)
    states = {}
    with gzip.open(out_dir / f"states-{name}.jsonl.gz", "rt") as fh:
        for line in fh:
            entry = json.loads(line)
            states[(entry["game"], entry["turn"], entry["seat"])] = entry["state"]
    builder = nr.PlaneBuilder(library)

    failures, checked, seen = [], Counter(), 0
    for context in nr.shard_contexts(arrays, states, maps):
        if limit and seen >= limit:
            break
        seen += 1
        label, seat, w, h = context["label"], context["seat"], context["w"], context["h"]
        if context["kind"] == KIND_PLAN:
            checked["plan"] += 1
            _, _, plan_mask = builder.observe(
                context["state"], seat, -1, nr.PHASE_PLAN, 0,
                want_mask=False, want_plan_mask=True)
            if label == OOV:                       # censused, never labelled: nothing to check
                checked["plan_unsupported"] += 1
                continue
            if label == PLAN_NOTHING:
                # `ENV-API.md`: "Plan 0 decodes to four zeros" -- index 0 is repurposed as
                # "train nothing", so the arithmetic tuple (1,1,0,0) is deliberately not what
                # the runtime returns, and the builder never labels a real purchase 0.
                if tuple(builder.decode_plan(0)) != (0, 0, 0, 0):
                    failures.append(f"the runtime decodes plan 0 as {builder.decode_plan(0)}, "
                                    f"not the four zeros ENV-API.md specifies")
                checked["plan_nothing"] += 1
            elif tuple(builder.decode_plan(label)) != tuple(plan_talents(label)):
                failures.append(f"plan row {context['index']}: the runtime decodes {label} as "
                                f"{builder.decode_plan(label)}, the builder as "
                                f"{plan_talents(label)}")
            if not plan_mask[label]:
                failures.append(f"plan row {context['index']} (game {context['game']} turn "
                                f"{context['turn']}): the plan mask forbids label {label}")
            continue

        checked["command"] += 1
        unit = next(u for u in context["state"]["units"] if u["id"] == context["active_troll"])
        text = builder.decode_action(label, context["active_troll"], seat, w, h)
        back = builder.encode_command(text, context["active_troll"], seat, w, h,
                                      unit["x"], unit["y"])
        if back != label:
            failures.append(f"command row {context['index']}: {label} decodes to {text!r} which "
                            f"encodes back to {back}")
        plane, _, _ = unflat(label)
        if plane != context["verb"]:
            failures.append(f"command row {context['index']}: label plane {plane} "
                            f"({VERBS[plane]}) but the builder recorded verb {context['verb']}")
        _, mask, _ = builder.observe(
            context["state"], seat, context["active_troll"], nr.PHASE_TROLL,
            context["plan_index"], want_mask=True, want_plan_mask=False)
        if not mask[label]:
            failures.append(f"command row {context['index']} (game {context['game']} turn "
                            f"{context['turn']} troll {context['active_troll']}): the mask "
                            f"forbids label {label} = {text!r}")
        checked[VERBS[plane]] += 1

    print(f"codec test on shard {name!r} ({meta.get('plan_vocab_version')}, library "
          f"{builder.plan_version}): {checked['plan']} plan rows, {checked['command']} command "
          f"rows")
    for verb in VERBS:
        if checked[verb]:
            print(f"  {verb:14s} {checked[verb]:6d}")
    if checked["plan_nothing"]:
        print(f"  plan rows labelled \"train nothing\" (index 0, four zeros): "
              f"{checked['plan_nothing']}")
    if checked["plan_unsupported"]:
        print(f"  plan rows labelled unsupported (no label to check): "
              f"{checked['plan_unsupported']}")
    for line in failures[:20]:
        print("  FAIL " + line)
    print(f"codec test: {'PASS' if not failures else 'FAIL'} ({len(failures)} failures)")
    return 0 if not failures else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replays", default=None)
    ap.add_argument("--index", default=None, help="index.json naming the teacher seat per game")
    ap.add_argument("--game", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--name", default="pilot", help="the shard's name")
    ap.add_argument("--holdout", type=int, default=0, help="percent of games held out, by game")
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--census-tables", default=None,
                    help="run the vocabulary guard over the teacher set's exact tables and exit")
    ap.add_argument("--self-test", action="store_true", help="check the codec and exit")
    ap.add_argument("--codec-test", default=None,
                    help="a shard directory: put every label back through the compiled codec "
                         "and the environment's own mask, and exit")
    ap.add_argument("--library", default=None,
                    help="libtroll_farm.so for --codec-test (default: the release build)")
    ap.add_argument("--limit", type=int, default=0, help="with --codec-test: stop after N rows")
    a = ap.parse_args()

    if a.self_test:
        self_test()
        return
    if a.codec_test:
        import nn_runtime as nr                                    # noqa: PLC0415
        sys.exit(codec_test(a.codec_test, a.name, a.library or nr.DEFAULT_LIBRARY, a.limit))
    if a.census_tables:
        sys.exit(0 if census_tables(a.census_tables) == 0 else 1)
    if not a.replays:
        raise SystemExit("--replays is required unless --census-tables is given")

    replay_dir = Path(a.replays)
    index_path = Path(a.index) if a.index else replay_dir / "index.json"
    index = {int(g["gameId"]): g for g in json.loads(index_path.read_text())}
    games = [int(a.game)] if a.game else sorted(index)

    census = dict(verbs=Counter(), unsupported=Counter(), unparsed=Counter(),
                  masked_label=Counter(), standing_unsupported=0)
    all_rows, all_states, metas, all_maps = [], [], [], {}
    for gid in games:
        rows, meta, turn_states = rows_for_game(gid, replay_dir, int(index[gid]["seat"]), census)
        split = held_out(gid, a.holdout)
        for r in rows:
            r["split"] = split
        meta["player"] = index[gid]["player"]
        meta["rows"] = len(rows)
        meta["split"] = split
        all_rows.extend(rows)
        all_states.extend(turn_states)
        all_maps[str(gid)] = meta.pop("map")
        metas.append(meta)
        print(f"game {gid} ({meta['player']}, seat {meta['seat']}): {len(rows)} rows, "
              f"{meta['turns']} turns, {meta['w']}x{meta['h']}, {meta['trains']} TRAINs, "
              f"{'held out' if split else 'train'}, "
              f"reconstruction mismatches {meta['mismatch'] or '{}'}", flush=True)

    check_standing_target(all_rows)

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

    label_bytes = state_bytes = map_bytes = None
    if a.out:
        label_bytes, state_bytes, map_bytes = write_shard(
            all_rows, all_states, Path(a.out), a.name, maps=all_maps)
        (Path(a.out) / f"labels-{a.name}-meta.json").write_text(json.dumps(
            dict(plan_action_size=PLAN_ACTION_SIZE,
                 plan_vocab_version=PLAN_VOCAB_VERSION,
                 fields=list(FIELDS),
                 standing_plan=("none (0) on plan rows; the turn's hindsight plan on troll "
                                "rows -- see the module head"),
                 standing_unsupported=census["standing_unsupported"],
                 seat_augmentation=False, games=metas, verbs=dict(census["verbs"]),
                 unsupported=[[list(k), v] for k, v in census["unsupported"].items()],
                 masked_label=dict(census["masked_label"]),
                 unparsed=dict(census["unparsed"]), rows=len(all_rows),
                 turn_states=len(all_states), label_bytes=label_bytes,
                 state_bytes=state_bytes, map_bytes=map_bytes, maps=len(all_maps),
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
        base = max(1, len(cmd))
        print(f"command labels per verb (of {base} command rows):")
        for v, c in sorted(census["verbs"].items(), key=lambda kv: -kv[1]):
            print(f"  {v:18s} {c:6d}  {100*c/base:5.1f} %")
        hist = Counter(r["label"] for r in plan)
        nothing = sum(1 for r in plan if r["troll"] == TROLL_NOTHING)
        print(f"plan labels: {len(hist)} distinct; "
              f"nothing {nothing}, unsupported {hist[OOV]}; "
              f"standing target: none on all {len(plan)} plan rows (no target memory in "
              f"cloning), the turn's plan on the {len(cmd)} troll rows "
              f"({sum(1 for r in cmd if r['standing_plan'] != STANDING_PLAN_NONE)} nonzero)")
        for lab, c in hist.most_common(8):
            name = ("UNSUPPORTED" if lab == OOV else
                    "train nothing" if lab == PLAN_NOTHING else plan_talents(lab))
            print(f"  {lab:5d} {str(name):22s} {c:6d}")
        print(f"unsupported TRAIN tuples: {sum(census['unsupported'].values())}"
              + ("" if census["unsupported"] else "  (zero)"))
        for tup, c in census["unsupported"].most_common():
            print(f"  {tup} -> {c} plan rows labelled {OOV}")
        print(f"labels the mask forbids: {sum(census['masked_label'].values())}"
              + ("" if census["masked_label"] else "  (zero -- the mask has one rule, entry 0)"))
        for tup, c in census["masked_label"].most_common():
            print(f"  {tup} -> {c}")
        if census["unparsed"]:
            print("unparsed commands:", dict(census["unparsed"]))
        if label_bytes:
            print(f"maps: {len(all_maps)} games, {map_bytes} bytes "
                  f"(maps-{a.name}.json -- the load-time plane builder places a state on its "
                  f"own map)")
            print(f"shard: labels {label_bytes} bytes for {n} rows = "
                  f"{1000*label_bytes/max(1,n):.0f} bytes per 1,000 label rows; "
                  f"states {state_bytes} bytes for {len(all_states)} turns = "
                  f"{state_bytes/max(1,len(all_states)):.0f} bytes a turn")
            print(f"the planes are NOT stored: one row is 104*11*22 = {104*CELLS} bytes "
                  f"({104*CELLS*1000/1e6:.1f} MB per 1,000 rows, ~20 GB over the teacher set's "
                  f"~800,000 rows); they are built at load time from the states above by the "
                  f"same Rust builder the environment uses -- for size and for the drift "
                  f"discipline of one builder, not because storing them is impossible")


if __name__ == "__main__":
    main()
