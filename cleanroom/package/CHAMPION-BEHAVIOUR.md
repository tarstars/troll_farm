# CHAMPION BEHAVIOUR — what the reference bot is observed to do

This document describes the play of the reference bot **as seen in its recorded matches**. It
was written by watching 160 real ranked matches and counting; it was not written by reading the
bot's program, and it does not describe the bot's program. Where the recordings determine a rule
exactly, the rule is stated with the count that supports it. Where they do not, the document
says so and gives the best approximation with its measured agreement, so you know how much room
you have.

**The evidence.** 160 ranked matches played by the reference bot on 2026-08-27 (agent 6667789,
submission 41202036). Seat 0 in 77 of them, seat 1 in 83. Map heights 8 (33 matches), 9 (43),
10 (45), 11 (39). 73 matches ran the full 300 turns; the shortest ended at turn 81.

**How to read a citation.** `game 900571119, turn 16` means: in the recording of match
900571119, on turn 16, you can see this happen. Every rule below carries at least one.

**Nothing in this document comes from the bot's own `MSG` output.** The recordings contain a
per-turn `MSG` line from this bot; it is that build's private debug channel, it describes its
internals, and it was stripped from the evidence before any of this was written.

---

## 1. In one sentence

**It is a logging bot.** It buys exactly one extra worker, walks the two of them around the map
felling trees, banks the wood, and in the last stretch of the match it converts the fruit sitting
in its shack into more wood by planting seeds at its own door and cutting them down.

**98.2 % of its final score is wood.** Across the 160 matches its shack ended with, on average,
45.07 wood, 2.36 apples, 0.55 bananas, 0.19 plums, 0.16 lemons, 0.74 iron — a mean final score
of 183.5, median 181.

The whole command budget over 160 matches:

| command | count | |
|---------|-------|--|
| MOVE    | 40,143 | |
| CHOP    | 26,149 | |
| DROP    |  5,171 | |
| WAIT    |  4,513 | |
| PICK    |  1,623 | the seed loop (§6) |
| PLANT   |  1,622 | the seed loop (§6) |
| TRAIN   |    160 | **exactly one per match** |
| MINE    |    130 | opening only (§3) |
| HARVEST |    130 | opening only (§3) |

It harvests fruit 130 times in 160 matches. Fruit, to this bot, is almost entirely a currency.

---

## 2. It never asks the referee to find a path — RULE, 40,143 / 40,143

Every `MOVE` it prints names a cell it can reach **this turn**. Over all 40,143 MOVE commands in
the corpus, the walking distance from the troll to the cell it names was never greater than the
troll's own movement speed; in 38,149 of them (95.0 %) it was **exactly** the speed, and in the
other 1,994 it was less (the troll is arriving).

The bot therefore does its own pathfinding and steps one turn at a time. It never hands the
referee a distant target and lets the referee route — so the referee's random tie-break between
equally short paths (RULES §4) never applies to it, and its movement is fully determined by its
own choice.

- game 900571119, turns 1 and 2: troll 1 is at (11,2) with speed 1 and prints `MOVE 1 11 3`;
  next turn it is at (11,3) and prints `MOVE 1 12 3`. Each target is one step away.

**Consequence for you:** if you name distant targets and let the referee walk, you are playing a
different game from this bot at every tie.

---

## 3. The opening

**Turn 1 is always a MOVE**, in all 160 matches: the starting troll leaves the shack cell
immediately. In 59 of the 160 it also prints a `TRAIN` on turn 1.

If it cannot afford the worker it wants on turn 1, it earns the difference and buys as soon as
it can (§4). Earning takes one of two forms, and which one depends on the map:

- **MINE** — 52 matches contain at least one, all inside the first 14 turns.
- **HARVEST** — 63 matches contain at least one, nearly all inside the first 10 turns.
- 12 matches contain both; **57 matches contain neither** — it could already afford its worker.

- game 900571119, turn 1: `MOVE 1 11 3` — the troll steps off the shack and nothing else.
- game 900571122, turn 1: `MOVE 0 3 3` — the same, from the other seat.
- game 900571119, turns 3 and 7: `MINE 1`, twice, before it can afford its worker at turn 16.
- game 900571120, turn 7 and game 900571121, turn 8: `HARVEST 1` in the opening.

Both of these all but vanish after the opening. The 130 HARVEST commands and 130 MINE commands
in the whole corpus are, with one exception late in one match, this opening behaviour.

---

## 4. It buys exactly one worker, and the choice is exact — RULE, 160 / 160

**One `TRAIN` per match. Never a second.** In all 160, the command is issued while it still has
exactly one troll. It finishes every match with two trolls.

**What it buys, exactly (160/160):** among every troll it could afford at that moment, it buys
the one with

- **harvestPower 0** — always, in all 160; the bought worker cannot pick fruit at all; and
- **the largest possible `movementSpeed + carryCapacity + chopPower`.**

In no match was a troll that is at least as good in all three of those and better in one
affordable and passed over. The commonest buys are `2/2/0/3` (24 matches), `2/2/0/2` (21),
`1/2/0/2` (13), `2/3/0/2` (12); the full spread runs from `1/1/0/2` to `3/3/0/3`.

Written as a command (RULES §8 argument order): `TRAIN ms cc 0 chop`.

- game 900571119, turn 16: shack holds `4 plum, 5 lemon, 8 apple, 7 banana, 5 iron`; it buys
  `1/2/0/2`, which costs 2 plum, 5 lemon, 1 apple, 5 iron — and it empties the lemon and the
  iron exactly.
- game 900571126, turn 1: shack `6/7/2/9/10`, buys `2/2/0/3` on the opening turn.
- game 900571124, turn 32: shack `4/10/4/9/8`, buys `1/3/0/2` — the latest purchase among the
  matches cited here (the latest in the corpus is turn 35).

**When it buys is not determined by the recordings.** Median turn 9, quartiles 1 and 14, range
1..35. In 159 of the 160, the turn it bought on was the *first* turn on which the exact bundle it
bought became affordable — so it is not saving up beyond its target. But what makes the target
`2/2/0/3` in one match and `1/2/0/1` in another, when a cheaper worker was affordable many turns
earlier, is not recoverable from what a spectator can see. **A reimplementation has to make its
own rule here.**

Two facts to build on. Because each talent's price is paid from its own resource (RULES §8),
"the largest `ms + cc + chop`" is simply "each talent at the largest value its own resource
affords" — the best affordable bundle was unique at all 160 purchases. And the simplest rule
tested — *wait until the best affordable worker has `ms + cc + chop >= 5`, then buy it; buy
unconditionally by turn 35* — buys on the same turn as this bot in only **63 of 160** matches;
in the other 97 it buys **earlier**, by a median of 10 turns and up to 27, and usually a weaker
worker (game 900571120: this bot buys `2/2/0/2` at turn 14; the rule buys `2/1/0/2` at turn 1).
Thresholds 4 and 6 do no better (60 and 59 of 160). So the bot waits for something a threshold
does not capture. The material to fit your own rule is in **`champion-purchases.json`**: for each
of the 160 matches, the shack's contents on every turn up to the purchase, whether the map has
iron, and what was bought on which turn.

---

## 5. Felling trees — the main loop

Between the opening and the endgame, both trolls do the same thing: walk to a tree, chop it
until it dies, carry the wood home, drop it, walk to the next tree.

### 5.1 It fells grown trees, and takes them all the way down

Of 12,971 chop commands aimed at trees that were on the map when the match began,
**12,217 (94.2 %) were on size-4 trees** — the biggest, worth 4 wood = 16 points. Sizes 1, 2 and
3 account for 142, 285 and 327. It does not nibble at saplings that grew on the map; it takes
the mature ones.

(The self-planted trees of §6 are a completely different pattern and are counted separately
there.)

### 5.2 Which tree it walks to — APPROXIMATE, best rule 39.7 %

This is the part the recordings do **not** pin down, and it is the most important thing to know
about this document.

A "journey" here is: a troll finishes a job, and some turns later chops a *different* tree. There
are 2,871 such journeys in the corpus where at least three trees were available. Measuring, at
the moment the troll set out, every tree it could have gone to instead — its walking turns
(`BFS distance / speed`) and its chopping turns (`tree health / chopPower`) — gives:

| candidate rule | picked the same tree | tree was in its top three |
|----------------|----------------------|---------------------------|
| **fewest turns to wood** (walking turns + chopping turns) | **39.7 %** | **82.0 %** |
| most wood per turn (`4 x size / (walking + chopping)`)   | 32.3 % | 66.7 % |
| nearest tree                                             | 32.8 % | 74.9 % |
| biggest tree first                                       | 24.9 % | 54.8 % |

And how far it walked compared with the nearest available tree:

| extra walking turns | 0 | 1 | 2 | 3 | 4 | 5+ |
|---------------------|---|---|---|---|---|----|
| journeys            | 1,277 | 586 | 432 | 208 | 137 | 231 |

44 % of the time it goes to the nearest tree; 65 % of the time it goes no more than one walking
turn further. It is *near-greedy*, and clearly not purely greedy.

- game 900571119, troll 3, turns 25 → 28: leaves, walks 3 turns to the tree at (11,4), which
  needs 6 chops — the nearest tree available.
- game 900571119, troll 1, turns 101 → 109: walks 8 turns to the tree at (4,0), 6 chops.
  Trees closer than that were on the board.

**Read this honestly.** No rule tested reproduces this bot's target choice. If you implement
"go to the tree that puts wood in your hands soonest, counting walking and chopping", you have a
bot that agrees with the reference on about two journeys in five and is within its top three
choices on four in five. That is the observable ceiling from replays alone; the remaining
difference is either information a spectator cannot see, or a tie-break, or a factor not measured
here.

### 5.3 It banks a full load — RULE, 4,371 / 5,171 (84.5 %)

`DROP` happens next to its own shack (the rules force that) and, in 84.5 % of drops, the troll is
carrying **exactly its full capacity**. The 800 short drops are almost all one item in a capacity
of 2 or 3 (622 + 149) — a troll going home part-loaded, which happens but is not the habit.

- game 900571119, troll 1 (capacity 1): drops at turns 5, 9, 15, 31 — every one at full load.
- game 900571119, troll 3 (capacity 2): drops 2 items at turns 24 and 35.

### 5.4 It stands still rather than make work

4,513 WAIT commands. They are not evenly spread: the median WAIT is at turn 235, and 68 % of
them come after turn 200. In 860 of them a troll is standing **on** a living tree (waiting, not
walking away); in 1,436 there is not a single tree left alive anywhere on the map.

- game 900571120, turns 291-293: troll 2 stands on the tree at (8,1) and WAITs three turns
  running instead of leaving it.
- game 900571120, turns 296-297: no tree is alive anywhere and it WAITs out the clock.

---

## 6. The endgame: turning fruit into wood at its own door

This is the most distinctive thing the bot does, and it is fully determined by the recordings.

Fruit in the shack is worth 1 point. Wood in the shack is worth 4. A seed taken back out of the
shack, planted, and cut down as a sapling turns 1 point into 4. The bot runs that conversion in
a loop:

1. a troll stands on a GRASS cell **orthogonally adjacent to its own shack**;
2. `PICK` — it takes one fruit out of the shack;
3. `PLANT` — next turn it plants that fruit on the cell it is standing on;
4. `CHOP` — the sapling ticks to size 1 the turn it is created (RULES §7), so it can be felled
   at once, for 1 wood;
5. `DROP` — the wood goes into the shack. Net: **+3 points every few turns, per troll.**

The counts that fix each step:

- **1,623 PICKs and 1,622 PLANTs** — they come in pairs.
- **Every plant is at Manhattan distance 1 from its own shack**: 1,621 of 1,622. (The single
  exception is at distance 2.) It never plants out on the map.
- **Self-planted trees are chopped as saplings**: of 6,664 chops on cells it planted itself,
  5,536 (83 %) were on a size-1 tree. Compare §5.1, where 94 % of chops on the map's own trees
  were on size-4.

- game 900571119: troll 3 plants a banana at (11,3) — its shack is at (11,2) — on turns 260,
  265, 270, 275, and troll 1 plants at (10,2), the shack's other neighbour, on turns 266 and 272.
  The matching PICKs are at turns 259, 264, 265, 269, 271, 274.

### 6.1 Which seed it takes — RULE, 1,609 / 1,623 (99.1 %)

Given what is in the shack, it takes the first available in this order:

> **BANANA, then PLUM, then LEMON, then APPLE.**

Measured, by what the shack held at that moment:

| shack held | took |
|------------|------|
| all four | BANANA 240, PLUM 4 |
| plum, apple, banana | BANANA 208, PLUM 1 |
| lemon, apple, banana | BANANA 202, LEMON 2 |
| apple, banana | BANANA 257, APPLE 1 |
| plum, lemon, apple | PLUM 65, LEMON 3 |
| plum, apple | PLUM 68, APPLE 2 |
| lemon, apple | LEMON 130, APPLE 1 |
| apple only | APPLE 439 |

The order is the order of how cheap the sapling is to fell: a size-1 banana has 3 health, a
size-1 plum or lemon 6, a size-1 apple 11 (RULES §6). With a chopPower of 1 or 2, an apple
sapling costs several turns and a banana one or two.

The 14 exceptions are all turns where **both** trolls picked at once and the second took the next
species down.

- game 900571119, turns 259, 264, 265, 269, 271, 274: shack holds plums and apples and bananas
  each time, and it takes BANANA every time.

### 6.2 When the loop starts — RULE, on 152 of 160 matches

The bot starts converting under **either** of two conditions, and the boundary is sharp:

- **Once the map is nearly logged out.** In 102 matches the loop started before turn 251, and in
  every one of those there were **at most 4 living trees left on the whole map** (median 2). The
  earliest was turn 41.
- **Or from turn 251, regardless.** In the other 50 matches the first PICK falls between turn
  251 and turn 267 (median 8 trees still alive, up to 24).

There is no match in the corpus where it started converting before turn 251 with five or more
trees standing. Turn 251 is the last fiftieth of a 300-turn match.

- game 900571125, turn 176: only 2 trees left of the 16 the map started with — it starts.
- game 900571119, turn 259: 24 trees alive (both sides have been planting) — it starts anyway,
  because the match is nearly over.
- game 900571120, turn 254 and game 900571121, turn 257: 1 and 2 trees left, late.

8 matches contain no PICK at all — all of them short matches that ended before either trigger.

---

## 7. What it does *not* do

Each of these is an absence measured over 160 matches, not a guess:

- **It never trains a second extra worker** (160 TRAINs in 160 matches; game 900571119 buys at
  turn 16 and never again through turn 300).
- **It never plants out on the map** — 1,621 of 1,622 plants are on its own doorstep
  (game 900571119, turns 260-275, every plant at (11,3) or (10,2) beside its shack at (11,2)).
- **It barely harvests fruit** — 130 harvests, essentially all in the opening
  (game 900571119: one HARVEST, at turn 14, in a 300-turn match).
- **It never MOVEs to a cell it cannot reach this turn** — 0 of 40,143 (game 900571119,
  turns 1-2, and every other MOVE in the corpus).
- **It shows no behaviour that depends on the opponent's position.** Nothing measured here
  changed with where the opponent's trolls were; it does not race them to trees, block them, or
  chop trees near their shack in preference to trees near its own.

That last one is worth a sentence of its own. This bot plays a solitaire game of maximising its
own wood, and it plays it against everything on the ladder.

---

## 8. Sources of uncertainty in this document

Stated plainly so you can weigh each rule:

1. **Tree clocks are reconstructed, not read.** The recordings show the board visually; the tool
   used to decode them recovers each tree's size, health and cooldown by simulating the rules
   forward. Sizes and healths quoted here (§5.1, §6) are therefore reconstructions. Positions,
   carries, inventories and the commands themselves are read directly and are exact.
2. **Target choice (§5.2) is not determined.** Stated as a measured agreement, not a rule.
3. **The training turn (§4) is not determined.** Stated with a substitute rule.
4. **160 matches, one day, one ladder.** All 160 come from a single batch against the opponents
   the ladder happened to offer that afternoon. Rules that hold 160/160 here are strong; rates
   quoted as percentages are rates on this population.
