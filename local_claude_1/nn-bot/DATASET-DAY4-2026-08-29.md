# Day 4 of the dataset — the mask's one rule, codec totality, no target memory, no seat swap

Card `coordination/tasks/20260829-nn-bot-way-b-dataset.md`, day 4. Builder `claude_1`, 2026-08-29.
Script: `local_claude_1/nn-bot/build_dataset.py`. Machine: the VM (4 cores), free disk **2.2 GB
(89 % used) before and after** — the day's outputs are 193 kB.

Two rulings landed on top of day 3: the coordinator's handoff of 18:16Z (codec totality, the
standing target, the widened scales, one generation id) and, an hour later, the parent card's
**second completion of amendment 8** at `origin/main` `bcf6ae88` — which withdraws two of the
things the 18:16Z handoff asked for. Where they disagree I built to the card, because the card is
later and is the signed interface. Everything below is in and runs.

## 1. The mask now has exactly one rule, and my day-3 question is answered

Day 3 asked what to do with the 44 real teacher TRAINs that have `harvest > carry`. The card's
answer is the first of the three ways I listed: **drop the rule**. Entry 0 is "train nothing" and
is always legal; every other in-range entry is legal too; `harvest == 0 and chop == 0` is not
masked either. Affordability never masks (the plan is a target, not a purchase), and the global
unit cap masks all but entry 0 at run time, which is the environment's business and not the
shard's.

So the count that mattered is now zero *by construction*, and the builder still prints it:

```
  MASKED LABELS (label the mask forbids): 0  (zero)
  under the withdrawn restrictions, for the record: {'harvest>carry': 44}
```

The 44 stay visible as history — they are why the rule went — but they are no longer a defect.

## 2. Codec totality: `(1,1,0,0)` is unsupported, never relabelled

The handoff's item 1. `plan_index_of_train()` is the label function for a purchase the teacher
really made, and it returns `None` twice: for a tuple outside the 400-way box, and for the
in-range tuple `(1,1,0,0)`, whose index is repurposed as "train nothing". Such a row is labelled
−1 and counted; it is never quietly turned into "the teacher trained nothing". No teacher issues
it (0 of 1,725), so nothing is lost — but the guard is there before the first self-play TRAIN is.

The second half of the handoff's item 1 (a zero-mask tuple labelled −1 and counted) is answered by
§1: under one rule there are no zero-mask tuples in range, so the count is zero. It is printed
anyway. A count that is only zero by argument is exactly the kind of check that rots silently.

The census over the whole teacher set, both counts, exit 0 only on both being zero:

```
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/build_dataset.py \
    --census-tables local_claude_1/reconstructions/fits/tables
```

```
census over 4 teachers, 784 games, 1725 TRAINs
  vocabulary: PLAN_ACTION_SIZE = 400 (v400-2026-08-29); distinct labels used 106; indices 6..363
  UNSUPPORTED (no label): 0  (zero)
  MASKED LABELS (label the mask forbids): 0  (zero)
  TRAINs per teacher: {'Bubaptik': 425, 'MSz': 444, 'delineate': 412, 'norxondor': 444}
  under the withdrawn restrictions, for the record: {'harvest>carry': 44}
```

## 3. No target memory in cloning — the column is there, and it is always "none"

The handoff of 18:16Z asked for a `standing_plan` column carrying the previous turn's hindsight
label. chatgpt_1's correction of 18:40Z showed that this leaks: between two purchases the previous
turn's hindsight label **is** this turn's label, so the scorer's "matches the current target" bit
would mark the right answer on almost every row, and holding games out does not remove it (the
leak is inside the row, not across games). The card accepted that at 18:5xZ.

So the column exists and is `0` on every row, and the plane builder must zero planes 59–71 with
it. Writing the column rather than dropping it is deliberate: a shard that says out loud "the
standing target here is none" cannot be silently re-filled by a later loader, and PPO — where the
standing target is the environment's own state and is honest — reads the same field name.

```
plan labels: 16 distinct; nothing 1992, unsupported 0; standing target: none on all 2954 plan
rows (no target memory in cloning)
```

## 4. Seat augmentation withdrawn

The card's point (d). The observation is already player-relative, so the seat is canonicalized
before the network sees anything; flipping a label onto a state rebuilt from the *other* seat is
not the same example twice, it is a different example wearing the first one's label. Day 3's
`seat_swapped()` is now a stub that raises, and the `--seat-swap` flag is gone. The pilot is back
to its honest size: **10,059 rows** (2,954 plan + 7,105 command) from 10 games, not 20,118.

## 5. One generation id, and a shard that refuses the wrong one

`PLAN_VOCAB_VERSION = "v400-2026-08-29"` is written into every shard's metadata beside
`plan_action_size`, and `read_shard()` refuses to load a shard whose pair does not match the
running code — a 400-label shard against a 144-logit runtime raises instead of training on
relabelled nonsense. The self-test proves it by rewriting a shard's metadata to the 144-way
generation and requiring the load to fail.

```
self-test OK: 400-way codec bijective (v400-2026-08-29), (1,1,0,0) unsupported not relabelled,
one mask rule forbidding no label, seat swap withdrawn, split deterministic (18.4 % at
--holdout 20), a foreign-generation shard refuses to load
```

## 6. The pilot, rebuilt under all of it

```
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/build_dataset.py \
    --replays local_claude_1/nn-bot/replays-slice-10 \
    --out local_claude_1/nn-bot/results/pilot --name pilot --holdout 20 --show 4 --report
```

3.4 s for ten games. 10,059 rows from 2,954 turn states; 0 unsupported, 0 masked labels; "train
nothing" 1,992 of 2,954 plan rows; held out 1,293 rows (12.9 %) from 1 of 10 games. The verb
histogram is unchanged from day 3 (MOVE 47.4 %, CHOP 20.0 %, DROP 12.5 %, HARVEST 10.5 %, …) —
the shares were always taken against un-augmented rows, so dropping the augmentation moves none of
them. Shard: labels 18,999 B for 10,059 rows = **1,889 B per 1,000 rows**; states 170,777 B for
2,954 turns = **58 B a turn**.

Shard fields, final for this phase: `game, turn, seat, kind, troll, verb, label, standing_plan,
split`. (`aug` is gone with the augmentation.)

## 7. Errata on day 3: the plane figure was wrong by a thousand

Day 3 (and day 2) put the materialised planes at **~20 TB**. One row is 104 × 11 × 22 = 25,168
bytes, and the teacher set is ~800,000 rows, so it is **~20 GB** — the card corrected this at
18:5xZ as point (e) and it is right. The builder's report now prints the corrected figure. The
compact-state shard stands on its real merits — ~14 MB of states against ~20 GB, and the drift
discipline of exactly one plane builder — not on an impossibility that was never there.

## 8. Two things the shipping code does not yet agree with

Both are statements about `origin/main` at `bcf6ae88`, checkable in one command each.

1. **`main`'s mask still has the old two rules.** `cgauto/train_level1_ppo.py::plan_index_is_legal`
   returns `False` for `harvest == 0 and chop == 0` and for `harvest > carry` — the rules the card
   withdrew an hour ago. Under it, 44 of Bubaptik's real purchases are masked to −inf. My builder
   implements the card's single rule, so the two disagree today.
2. **`PLAN_VOCAB_VERSION` is not on `main`.** The handoff says it is on `main` beside
   `PLAN_ACTION_SIZE = 400`; `git show origin/main:cgauto/train_level1_ppo.py | grep -c
   PLAN_VOCAB_VERSION` returns 0. My builder therefore defines the literal itself for now;
   `train_clone.py` will import it once it lands rather than keep a second copy.

## What is still deferred

The Python plane builder and the drift test still wait on a signed
`local_claude_1/nn-bot/OBS-PLANES.md` with amendment 8's widened scales (18/28 S→4, 19/29 S→5,
21/31 S→4, cargo 22–27 and 32–37 S→5, 72–87, 93–96 S→5, target 60–63 S 4/5/3/4, costs 64–71 S 48)
and on Phase 1's `tf_full_obs_from_state`. `train_clone.py` is day 5's; it waits on nothing but
imports, and it will import `PLAN_ACTION_SIZE`, `PLAN_VOCAB_VERSION` and `forward_with_plan()`
rather than restate any of them.
