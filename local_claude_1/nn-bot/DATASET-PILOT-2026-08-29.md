# The day-2 dataset pilot — the labels on the 10-game slice

Card `coordination/tasks/20260829-nn-bot-way-b-dataset.md`, day 2. Builder `claude_1`, 2026-08-29.
Script: `local_claude_1/nn-bot/build_dataset.py`. Machine: the VM (4 cores), free disk **2.3 GB
(89 % used) before and after** — the pilot's outputs are 18 kB.

Command, verbatim:

```
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/build_dataset.py \
    --replays local_claude_1/nn-bot/replays-slice-10 \
    --out local_claude_1/nn-bot/results/pilot --show 6 --report
```

It runs in **2.2 seconds** for ten games (0.22 s a game, the reconstruction included).

## What a row is

Per turn of a teacher's game, in the environment's mini-step order (parent card, amendment 4):
the **plan row** first, then one **command row** per own troll in troll-id order.

- **plan row** — label = the 144-way index of the talents of the *next* TRAIN the teacher actually
  issues at or after this turn; `0` = "train nothing before the end". Index
  `(((speed-1)·4 + (carry-1))·3 + harvest)·4 + chop`, so index 0 is exactly the combination the
  mask calls illegal (speed 1, carry 1, no harvest, no chop) and is free to be repurposed.
- **command row** — label = the flat index `plane·242 + y·22 + x`, July's decoding (0 MOVE,
  1 HARVEST, 2 CHOP, 3 DROP, 4 MINE, 5–8 PLANT plum/lemon/apple/banana, 9–12 PICK …). A **MOVE
  label is the cell the troll actually reached in the next snapshot** — the referee's step, not
  the intent, and the replay's `diff` is the authority for that position. A troll given no command,
  or WAIT, is labelled MOVE to the cell it stands on, which is the encoding of WAIT.

## Five sample rows (the first rows of game 891153730, delineate on seat 1)

```
plan  game 891153730 turn 1 seat 1 label 67   -> TRAIN (speed 2, carry 2, harvest 1, chop 3)
troll 1 game 891153730 turn 1 seat 1 label 31   -> MOVE at (9,1)      [the cell reached]
plan  game 891153730 turn 2 seat 1 label 67   -> TRAIN (2, 2, 1, 3)
troll 1 game 891153730 turn 2 seat 1 label 999  -> MINE at (9,1)
troll 0 game 891203441 turn 2 seat 0 label 2533 -> PICK_LEMON at (3,5)
```

## Row counts

| | |
|---|---|
| games | 10 (the slice: delineate ×3, norxondor ×3, MSz ×2, Bubaptik ×2) |
| turns | 2,954 (one game ends at 254, the rest at 300) |
| rows | **10,059** = 2,954 plan + 7,105 command |
| rows a game | 600 – 1,293 (it tracks the number of trolls the teacher trains) |
| reconstruction mismatches | only `growth_engine_only(expected)` and troll-position ties (`unit_x`/`unit_y`), which the replay's diff corrects — no inventory, carry or score disagreement in any of the ten games |

## The label histogram per verb (7,105 command rows)

| verb | rows | share |
|---|---|---|
| MOVE | 3,365 | 47.4 % |
| CHOP | 1,418 | 20.0 % |
| DROP | 891 | 12.5 % |
| HARVEST | 746 | 10.5 % |
| PLANT_BANANA | 206 | 2.9 % |
| PLANT_LEMON | 83 | 1.2 % |
| PICK_BANANA | 82 | 1.2 % |
| WAIT / no command | 72 | 1.0 % |
| MOVE that stayed put | 57 | 0.8 % |
| MINE | 48 | 0.7 % |
| PICK_LEMON | 29 | 0.4 % |
| PICK_PLUM | 23 | 0.3 % |
| PLANT_APPLE | 9 | 0.1 % |
| PICK_APPLE | 5 | 0.1 % |

Plan rows: 16 distinct labels; "train nothing" 1,992 of 2,954 (67 %); the head of the rest
90 = (2,4,1,2) 243, 111 = (3,2,0,3) 153, 87 = (2,4,0,3) 78, 83 = (2,3,2,3) 78.

## Bytes

`labels-pilot.npz` (seven int32 columns, compressed): **18,419 bytes for 10,059 rows =
1,831 bytes per 1,000 label rows**. At the full teacher set's scale — 784 games, about 1,000 rows a
game, so roughly 800,000 rows — the labels are **about 1.5 MB**.

## Three findings for the coordinator

**1. The observation half cannot be materialised, and does not need to be.** One row's planes are
104 × 11 × 22 = **25,168 bytes**; 800,000 rows is **about 20 TB uncompressed**, and even a
20× compression leaves ~1 TB — larger than the host's corpus by two orders of magnitude. The
per-turn *state* the planes are built from, on the other hand, is **53 bytes a turn gzipped**
(measured: game 891203441's 301 snapshots are 472,337 bytes of JSON, 16,222 bytes deflated), so the
whole teacher corpus of states is **about 45 MB**. The shard should therefore carry the compact
state plus the labels, and the planes should be built **at load time by the same Rust
`tf_full_obs_from_state`** the environment uses — which is also the only arrangement in which the
drift test compares two independent implementations rather than a thing to itself. This changes the
card's `obs u8[N,104,11,22]` shard line; it is your ruling, not mine, so I have not written a plane
shard either way.

**2. The 144-way vocabulary census is in and returns zero on this slice — which does not settle
chatgpt_1's blocker.** The builder never coerces a TRAIN tuple: out-of-vocabulary tuples are
counted, named and labelled −1. On these ten games there are **0** — but the slice holds only two
Bubaptik games (one with no TRAIN at all, one with two in-vocabulary buys), so the slice is simply
too small to reproduce the 178 movement-4 purchases chatgpt_1 counted over 191 games. The census
runs over the full teacher set on the host in about three minutes at this speed, and I will report
its exact numbers there rather than argue about the blocker from a slice that cannot see it. **No
plan shard is frozen until you rule.**

**3. Two label choices are mine by default and want your signature.** (a) *Padding*: three of the
four board sizes are smaller than 11 × 22 (the slice has 18×9, 20×10 and 22×11); I align the map
top-left in the padded grid, so a label's `y·22 + x` is the map's own coordinate. (b) *The seat
frame*: seat 1 is rotated 180° over the map's own `w × h`, not over the padded grid. Both are
invisible on a 22×11 map and change every label on the others, and both belong in the signed
`OBS-PLANES.md` rather than in my script — this is the same seat-frame hole chatgpt_1's interface
audit names as finding 1. A third, smaller one: **57 of 3,365 MOVE labels (1.7 %) resolve to the
cell the troll was already standing on** — a blocked or already-arrived move — and so are
indistinguishable from WAIT under the reached-cell rule. That is the rule working as written, not a
bug, but the clone will learn "wait" from them.
