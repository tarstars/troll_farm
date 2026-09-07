# Where the top players' 2x comes from, and what to measure instead — 2026-09-02

Everything below is measured from archived platform games with the team repository's validated
replay tooling (`profile_bot.py`, `parse.py`, used read-only), the referee's own source, and this
project's retained panels. Reproduction commands are at the end.

## 1. The bar

| fact | value |
|---|---|
| mature platform readings of this lineage, V54 to V440 (23, including V370's 25.21) | mean 23.1, spread 1.1, range 21.06 to 25.21, no trend |
| target | score at least 25.40 and a rank inside the top ten |
| rank-to-score map from this lineage's own readings (Sep 1) | rank 17 = 25.21; rank 20 = 24.8 to 25.0; rank 22 = 24.7; rank 25 = 24.0; rank 27 to 29 = 22.9 to 23.5 |
| leaderboard snapshot of 2026-07-22 (contest era, in the R1FA bundle) | rank 8 = 26.41, rank 9 = 25.62, rank 10 = 25.59, rank 11 = 25.31; rank 17 was 24.48 then, so today's rank ten is probably near 26.3 |
| chance that one more submission of the present economy reads 25.40 | about 2 % (two spreads above the mean) |

Nearly 400 versions of one-game repairs, each gated on "changes one loss in 960 archived games,
no worse result", left the platform reading where it was. The gate selects changes too small to
register against a reading whose spread is 1.1.

## 2. The rules that set the economy (referee source)

Wood is produced only when a tree is felled, and the amount is the tree's size at that moment.
Score is fruit banked plus four times wood banked. A planted tree starts at size 0 and gains one
size per growth cooldown; growth is much faster next to water.

| tree | cooldown per size (plain / next to water) | turns from planting to size 4 (plain / water) | health at size 1 | health at size 4 | wood at size 1 / size 4 | chops to fell size 4 at chop power 1 / 2 / 3 |
|---|---|---|---|---|---|---|
| PLUM | 8 / 3 | 32 / 12 | 6 | 12 | 1 / 4 | 12 / 6 / 4 |
| LEMON | 8 / 3 | 32 / 12 | 6 | 12 | 1 / 4 | 12 / 6 / 4 |
| APPLE | 9 / 2 | 36 / 8 | 11 | 20 | 1 / 4 | 20 / 10 / 7 |
| BANANA | 6 / 4 | 24 / 16 | 3 | 6 | 1 / 4 | 6 / 3 / 2 |

Consequences per troll-turn of chopping at chop power 2: a size-4 banana returns 1.33 wood per
chop (4 wood in 3 chops), a size-4 plum or lemon 0.67, a size-4 apple 0.40; a size-1 banana
returns 0.50 (1 wood in 2 chops), a size-1 plum or lemon 0.33, a size-1 apple 0.17. At chop
power 1 every figure halves. A size-4 tree also yields a fruit every cooldown, up to three,
each worth one point and usable as a seed.

## 3. Where the 2x comes from

Profiles over the archived games of each player (`/data/separate_troll_farm-working/profiles/2026-09-02/COMPARISON.md`):

| measure | tass-v440 (ours) | delineate | putibuzu | R1FA | astrobytes |
|---|---|---|---|---|---|
| games / win rate | 160 / 0.606 | 141 / 0.801 | 123 / 0.634 | 133 / 0.647 | 139 / 0.525 |
| mean score / opponent | 215 / 197 | 415 / 250 | 246 / 220 | 248 / 222 | 258 / 237 |
| wood points / fruit points | 184 / 31 | 387 / 28 | 185 / 61 | 241 / 8 | 237 / 23 |
| wood per game | 46.1 | 98.1 | 46.5 | 61.9 | 60.2 |
| CHOP commands per game | 166.8 | 169.8 | 104.7 | 144.4 | 122.1 |
| wood per CHOP command | 0.28 | 0.58 | 0.44 | 0.43 | 0.49 |
| share of CHOP commands at chop power 1 / 2 / 3 | 0.60 / 0.26 / 0.14 | 0.21 / 0.42 / 0.37 | 0.33 / 0.61 / 0.06 | 0.46 / 0.28 / 0.27 | 0.28 / 0.50 / 0.22 |
| wood per game in turns 1-100 / 101-200 / 201-300 | 14.8 / 16.5 / 14.7 | 7.6 / 31.9 / 58.6 | 13.1 / 18.3 / 15.1 | 1.0 / 24.7 / 36.1 | 1.0 / 22.0 / 37.3 |
| CHOP commands early / mid / late | 54 / 55 / 58 | 28 / 50 / 92 | 34 / 38 / 32 | 4 / 59 / 82 | 2 / 39 / 81 |
| chops on own-planted / wild / opponent trees | 0.31 / 0.32 / 0.37 | 0.64 / 0.12 / 0.23 | 0.48 / 0.29 / 0.23 | 0.60 / 0.34 / 0.06 | 0.66 / 0.27 / 0.07 |
| successful plants per game | 12.3 | 40.6 | 19.4 | 27.8 | 34.8 |
| plants early / mid / late | 0.5 / 4.1 / 7.7 | 8.0 / 14.2 / 18.3 | 6.1 / 7.6 / 5.8 | 11.7 / 10.1 / 6.0 | 9.4 / 11.5 / 13.9 |
| own trees still alive at the end | 0.17 | 3.37 | 0.38 | 0.29 | 2.17 |
| fruits harvested per game | 31 | 87 | 72 | 60 | 74 |
| iron mined per game | 0.6 | 11.3 | 0.5 | 26.8 | 13.4 |
| trolls at the end | 1.99 | 2.92 | 1.98 | 3.67 | 2.76 |
| second troll's talents (speed carry harvest chop), top choice | 2 2 0 2 (17 %) | 2 2 2 2 (23 %) | 2 2 2 2 (41 %) | 2 2 1 1 (100 %) | 2 2 2 2 (56 %) |
| third troll (median turn, share of games) | never | 106, 56 % | never | 97, 87 % | 96, 52 % |
| WAIT share of commands in the last 30 turns | 0.22 | 0.00 | 0.07 | 0.00 | 0.00 |
| starting troll's first ten commands, most common | MMMMMMMMMM | MKPKMPMMMM | MMMMMHMMMM | MKPKMMPKMP | MKPKMMPKMM |

Reading the rows together:

1. **Same number of chops, half the wood.** V440 issues as many CHOP commands as delineate and
   gets 0.28 wood per command against 0.58. Sixty per cent of our chops are made at chop power 1
   (the starting troll); delineate makes 79 % of its chops at power 2 or 3, its second troll
   harvests as well as chops, and its third troll (carry 4, chop 3) arrives around turn 106.
2. **Our wood income is flat; theirs compounds.** V440 banks about 15 wood in each hundred
   turns. Delineate banks 8, then 32, then 59: it plants 41 trees a game (eight in the first
   hundred turns, opening with plant-pick-plant), lets them grow, and chops mostly its own
   size-4 trees late, with 3.4 of its own trees still standing at the end. V440 plants 12, mostly
   after turn 200, and fells its own trees at size 1 about five turns after planting (1,702 of
   its 1,931 own fellings were at size 1). By the rules table that is a quarter of the wood per
   chop that the same seed gives at size 4.
3. **Fruit is not the gap.** Our apple engine already banks 31 fruit points, more than delineate's
   28. Putibuzu's 61 shows fruit can add another 30, but wood is what separates 215 from 415.
4. **The third troll is a consequence, not a cause.** R1FA and astrobytes mine 13 to 27 iron a
   game and train three or four trolls, but their wood at turn 100 is 1.0 (they farm first and
   chop from turn 130 on). Delineate wins with fewer trolls than R1FA by having more mature trees.
   Local experiments that bolted a third troll onto V440's flat economy found nothing to fund it
   with, which is the observation the README records.
5. **Idle time.** V440 spends 22 % of its endgame commands waiting; none of the four spend any.

## 4. Score curves (mean own score after turn t; opponents' means in the archive at the same turns)

| turn | tass-v440 | delineate | putibuzu | R1FA | astrobytes | V440's opponents | delineate's opponents |
|---|---|---|---|---|---|---|---|
| 50 | 40 | 25 | 33 | 19 | 18 | 24 | 24 |
| 100 | 77 | 50 | 75 | 24 | 27 | 46 | 43 |
| 150 | 116 | 91 | 122 | 49 | 47 | 73 | 70 |
| 200 | 151 | 178 | 167 | 110 | 110 | 109 | 120 |
| 250 | 183 | 291 | 207 | 189 | 189 | 152 | 183 |
| 300 | 215 | 415 | 246 | 248 | 258 | 197 | 250 |

V440 leads every top player at turn 100 and is overtaken by all of them between turns 175 and
250. Its slope after turn 100 is 0.7 points a turn; delineate's last hundred turns run at 2.4 a
turn, R1FA's and astrobytes's at about 1.4. The full table at 25-turn steps and the per-game
curves are in `/data/separate_troll_farm-working/profiles/2026-09-02/score-curves.{md,json}`.

## 5. Who beats us

Pooled over the lineage's 40 archived submissions (6,297 games), opponents met at least 15 times,
by our loss rate: putibuzu 17 % wins for us, tonigineer 25 %, R1FA 30 %, FreZzz 30 %,
FredericBautista 34 %, Bondo416 36 %, laconic_pixel 37 %, Pech1 41 %, tsukammo 43 %, gaha 45 %,
a76a44 46 %, DoubtinGiyov 46 %, BoatBuilder 47 %, icecuber 48 %. These are the games a top-ten
rating is made of.

## 6. The new gate

Candidates were selected by "no recorded win becomes a loss over 960 archived games". That
measure cannot see an economy change: it is dominated by ties against the project's own
synthetic opponents (the platform produced zero ties in V440's 160 games) and it rewards
changes that touch one game. From now on:

1. **Primary:** on the fresh paired panel against V440 (same maps, both seats, the eight opponent
   families), a candidate's mean own score must be at or above V440's at turns 100, 200 and 300,
   and at turn 300 it must be at least **+40** (the distance from 215 to the 246 to 258 band of
   players rated 24.7 to 26.7). The curve comes from `score_curve.py` over a corpus built with
   `build_profile_corpus.py`, or from the panel TSVs' own-score columns for the endpoint.
2. **Secondary:** the platform-archive counterfactual replay (opponent moves fixed) must not
   lower own score before the trajectories diverge.
3. **Safety only:** the old no-regression count over archived games remains a check against
   protocol errors and jams; it no longer selects candidates.
4. **Submission discipline:** with a reading spread of 1.1, a candidate expected below +2 true
   points is not worth a 160-game slot; treat the score half of the target as needing an
   expected reading near 26.

## 7. What was ruled out, re-read with the new yardstick

The door-factory line V441 to V454 grafted putibuzu's tent-door plant/chop/drop cycle onto V440.
On the retained panels the mean own score against the V440 baseline changed by: V441 +1.0,
V442 -38.9, V443 +4.1 (8 maps) and -0.1 (16 fresh maps), V444 -5.3, V448 +2.4 and -0.5,
V450 +3.6 and +1.8, V451 +1.9, V452 -4.6, V453 -28.4, V454 -39.0. None approached +40; the
line copied the door cycle's visible actions, not the growth-to-size-4 economy behind them.
V425, a reconstruction of R1FA's decision tables, was built on 2026-09-01 but never measured.

## 8. Reproduction

```sh
cd /home/tarstars/prj/separate_troll_farm
PY=/home/tarstars/venvs/nn-bot/bin/python
export TMPDIR=/data/separate_troll_farm-working/tmp
$PY build_profile_corpus.py \
  /data/public-v440-early-exhausted-one-wood-swap-agent6684947 \
  /data/top1-delineate-agent6479768-20260831 /data/public-putibuzu-agent6479779 \
  /data/public-r1fa-agent6479863-current /data/public-astrobytes-agent6482167 \
  --out /data/separate_troll_farm-working/profiles/2026-09-02/corpus
$PY profile_players.py --corpus-data /data/separate_troll_farm-working/profiles/2026-09-02/corpus/data \
  --out /data/separate_troll_farm-working/profiles/2026-09-02 \
  --player tass-v440=6684947 --player delineate=6479768 --player putibuzu=6479779 \
  --player R1FA=6479863 --player astrobytes=6482167
$PY score_curve.py --games /data/separate_troll_farm-working/profiles/2026-09-02/corpus/data/processed/games.jsonl \
  --player tass-v440=6684947 --player delineate=6479768 --player putibuzu=6479779 \
  --player R1FA=6479863 --player astrobytes=6482167 \
  --out /data/separate_troll_farm-working/profiles/2026-09-02/score-curves.json \
  --table /data/separate_troll_farm-working/profiles/2026-09-02/score-curves.md
$PY -m pytest -q -p no:cacheprovider test_build_profile_corpus.py test_profile_players.py test_score_curve.py
```

Corpus: 691 distinct games, no parse failures. Referee constants: `Constants.java`, `Plant.java`,
`ChopTask.java` under `/data/strong-bot-sources/eulerscheZahl-Troll-Farm/src/main/java/engine/`.
