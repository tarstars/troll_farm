# Day 3 of the dataset — the 400-way vocabulary, the census over the whole teacher set, the shard

Card `coordination/tasks/20260829-nn-bot-way-b-dataset.md`, day 3. Builder `claude_1`, 2026-08-29.
Script: `local_claude_1/nn-bot/build_dataset.py`. Machine: the VM (4 cores), free disk **2.2 GB
(89 % used) before and after** — the day's outputs are 206 kB.

The coordinator's handoff of 17:58Z ruled the three questions the day-2 pilot left open, and this
is what they cost: the vocabulary is 400 (amendment 8), the shard carries states and never planes
(ruling 1), and the padding and seat conventions are signed as they stood (ruling 3). All three are
in. One new question comes back up, at the bottom.

## 1. The vocabulary guard over the whole teacher set: **zero**

The coordinator asked that my census function stay as the total-label guard and return zero over
the full teacher set. It is now a mode of the builder and it does:

```
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/build_dataset.py \
    --census-tables local_claude_1/reconstructions/fits/tables
```

```
census over 4 teachers, 784 games, 1725 TRAINs
  vocabulary: PLAN_ACTION_SIZE = 400; distinct labels used 106; indices 6..363
  OUT OF VOCABULARY: 0  (zero)
  TRAINs per teacher: {'Bubaptik': 425, 'MSz': 444, 'delineate': 412, 'norxondor': 444}
  tuples the card's mask forbids: 44 {'harvest>carry': 44}
```

It exits 0 only on a zero count, so it can gate a build. Independently of the ruling I also
re-counted the old vocabulary from the same tables and reproduce the coordinator's census exactly:
**267 of 1,725 (15.5 %) outside the 144** — speed 4 in 209, harvest 3 in 33, chop 4 in 16, carry 5
in 10; per teacher, Bubaptik 222 of its 425 purchases (52 %), norxondor 29, MSz 16, delineate 0.
The maxima seen over all 784 games are exactly **(4, 5, 3, 4)**, which is the box amendment 8 draws;
the game itself caps nothing (`sim/engine.py::apply_train` charges `n + stat²` per talent and
refuses only on affordability and on an occupied shack), so the box is the teachers' box, not the
rules', and a self-play policy could walk out of it. That is the right trade for behaviour cloning
and worth remembering at PPO.

Only 106 of the 400 indices are ever used by the teachers. The head is `(2,2,2,2)` 138,
`(2,3,1,2)` 115, `(2,2,2,1)` 111, `(2,4,1,3)` 106, `(2,4,1,2)` 100.

## 2. The codec, migrated and self-tested

`plan_index` / `plan_talents` are now `(((speed−1)·5 + (carry−1))·4 + harvest)·5 + chop` over
speed 1–4 × carry 1–5 × harvest 0–3 × chop 0–4, and `--self-test` proves what the codec claims:

```
self-test OK: 400-way codec bijective, mask reported not coerced, seat swap involutive,
split deterministic (18.4 % at --holdout 20)
```

It checks all 400 tuples round-trip, that index 0 is exactly `(1,1,0,0)`, that five out-of-box
tuples return `None` rather than folding onto a neighbour (chatgpt_1's mask-totality point of
18:02Z), that the seat swap is an involution on the label, and that the by-game split is
deterministic.

`(1,1,0,0)` is a legal purchase in the game, so index 0 carries two meanings: "train nothing" and
"train the cheapest useless troll". No teacher ever buys it (0 of 1,725), so nothing is lost, but
the two are distinguishable in the shard anyway — a "train nothing" row carries `troll = −2` and a
real plan row `troll = −1`.

## 3. The shard: labels, states, metadata — never planes

Ruling 1 in code. `--out` writes three files:

| file | what | size on the pilot |
|---|---|---|
| `labels-pilot.npz` | nine int32 columns: game, turn, seat, kind, troll, verb, label, aug, split | 31,419 B for 20,118 rows = **1,562 B per 1,000 rows** |
| `states-pilot.jsonl.gz` | the compact pre-turn state each row observes, one JSON line a turn | 170,777 B for 2,954 turns = **58 B a turn** |
| `labels-pilot-meta.json` | per game: player, seat, turns, w×h, reconstruction mismatches, split; plus the verb census, the out-of-vocabulary census, the mask census, `plan_action_size` | 3,455 B |

At the teacher set's scale (784 games, ~236,000 turns) that is about **14 MB of states and 1.5 MB
of labels** where the materialised planes would have been ~20 TB. (Day 2 put the state corpus at
~45 MB; that estimate multiplied by rows rather than by turns — one state serves the turn's plan row
and all its troll rows — and 58 B × ~236,000 turns is the corrected figure.) The planes are built at load time
from the states by the same Rust `tf_full_obs_from_state` the environment uses; the exact wire form
the Rust builder reads is Phase 1's to fix, and this file writes the reconstruction's own state
schema until then — one `state:` object a line, so the format can change without rebuilding labels.

## 4. Seat-swap augmentation and the held-out split

Both are in and both are cheap because the observation is player-relative. **The seat swap is not a
second copy of the state**: the loader passes the flipped seat to the same builder, and only the
label moves — 180° inside the map's own `w × h`, the transform `relative` already applies. The plan
label is a talent tuple and does not move at all. The pilot with `--seat-swap` is 20,118 rows from
the same 2,954 states.

The split is by game and deterministic (`sha1(game_id) % 100 < percent`), so the same game lands on
the same side on the VM and on the host. `--holdout 20` on the ten-game slice holds out one game
(893255096, MSz) — 12.9 % of rows; over 1,000 ids it lands at 18.4 %.

## 5. The pilot, rebuilt under everything above

```
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/build_dataset.py \
    --replays local_claude_1/nn-bot/replays-slice-10 \
    --out local_claude_1/nn-bot/results/pilot --name pilot \
    --seat-swap --holdout 20 --show 6 --report
```

2.5 s for ten games. 20,118 rows = 5,908 plan + 14,210 command, from 2,954 turn states; 0
out-of-vocabulary; "train nothing" 3,984 of 5,908 plan rows. The verb histogram is the day-2 one
unchanged (MOVE 47.4 %, CHOP 20.0 %, DROP 12.5 %, HARVEST 10.5 %) — with one correction to the
day-2 write-up: its table omitted a row, `PLANT_PLUM 71 (1.0 %)`. The counts in the pilot's meta
file were right; the markdown table was short. Nothing else changes.

The plan labels moved index because the vocabulary did: game 891153730's first plan label was 67
under the 144 and is 128 under the 400, both decoding to `(2, 2, 1, 3)`. That is the migration
working; it is also exactly why a 400-label shard must refuse to load against a 144-logit runtime,
as chatgpt_1 asks — `plan_action_size` is written into every shard's meta file for that check, and
`train_clone.py` will import the constant rather than hard-code either number.

## 6. One question back: the mask forbids 44 labels the teachers actually issued

The parent card masks `harvest == 0 and chop == 0` and `harvest > carry`. **Neither is a rule of
the game.** `apply_train` imposes no relation between the talents. And the teachers break the second
one: **44 of 1,725 TRAINs have harvest > carry** — all 44 Bubaptik's, sixteen distinct tuples, the
commonest `(2,1,2,2)` nine times — and the referee accepted every one, in real Arena games.

Under a masked cross-entropy those 44 labels sit on logits the mask has set to −inf: the loss is
undefined, or the rows are silently dropped, or (worst) the label is quietly moved to a legal
neighbour. The builder does none of these — it labels them honestly and counts them, and the count
is in every shard's meta as `mask_forbids`. But the mask itself belongs to the signed interface,
so the repair is the coordinator's to rule. Three ways out, in the order I would take them:

1. **Drop the `harvest > carry` rule** from the mask (keep `harvest == 0 and chop == 0`, which no
   teacher issues either but which really does buy a troll that can neither harvest nor chop). The
   vocabulary stays 400, the masks get simpler, and no real label is unreachable.
2. Keep the rule and drop the 44 rows — 2.6 % of the plan labels, all from the teacher whose
   purchases are already the most distinctive.
3. Keep the rule and let the loss skip masked-label rows — the same as (2), less visibly.

Whichever it is, `harvest == 0 and chop == 0` should stay masked only if the trainer never meets a
teacher row that violates it; over the whole teacher set it never does (0 of 1,725).

## What is still deferred

The Python plane builder and the drift test still wait on a signed `local_claude_1/nn-bot/OBS-PLANES.md`
and on Phase 1's `tf_full_obs_from_state`. `train_clone.py` waits on nothing but the constant:
it imports `PLAN_ACTION_SIZE` and `forward_with_plan()` from `cgauto/train_level1_ppo.py`, which
the coordinator said lands on `main` within the hour and had not at 18:2xZ.
