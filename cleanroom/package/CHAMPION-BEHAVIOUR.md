# CHAMPION BEHAVIOUR — what the reference bot does, and why

This document has two parts for two uses.

**Part I** is one page: the bot's play as ten principles, each with the reason behind it and a
label saying what kind of evidence stands behind it. **Build from Part I.** You are not asked to
copy habits; you are asked to build a bot at least as strong, and a leaner one if you can. Where a
principle says OPEN, your own judgement has to do the work and a different answer is not
automatically wrong.

**Part II** is the evidence: every count, table and match citation behind Part I. It exists so
that nothing here has to be taken on trust, and for the refinement loop — when your bot
diverges from the reference, Part II is where you check whether the divergence is one that
matters. You do not need to read it to build.

Everything here was written by watching recorded matches and counting. It was not written by
reading the bot's program and it does not describe the bot's program.

**The evidence.** 160 ranked matches played by the reference bot on 2026-08-27 (agent 6667789,
submission 41202036). Seat 0 in 77 of them, seat 1 in 83. Map heights 8 (33 matches), 9 (43),
10 (45), 11 (39). 73 matches ran the full 300 turns; the shortest ended at turn 81. A citation
`game 900571119, turn 16` means: in the recording of match 900571119, on turn 16, you can see
this happen. Nothing in this document comes from the bot's own `MSG` output — that channel was
stripped from the evidence before anything was written.

---

# Part I — The bot in ten principles

**The labels say what the evidence is, not what we think of it:**

- **SCORE MECHANISM** — arithmetic or a referee rule establishes the value.
- **OBSERVED INVARIANT** — held on the 160 recorded matches, with the count.
- **LADDER-TESTED** — a change was made and measured on the real ladder (`DOMAIN.md` §2).
- **HABIT** — observed; no claim that it carries strength.
- **OPEN** — the recordings do not determine it; the choice is yours.

**In one sentence:** it is a logging bot. It buys one extra worker, walks the two of them around
the map felling the big trees, banks the wood, and at the end converts the fruit in its shack
into wood by planting seeds at its own door and cutting them down.

1. **Wood is the score; fruit is currency.** — SCORE MECHANISM (wood 4 points, fruit 1; RULES §1);
   OBSERVED INVARIANT (98.2 % of its final score is wood; mean final shack 45 wood, about 3
   fruit); and every strong player on the ladder scores over 90 % in wood (`DOMAIN.md` §1.1).
   Fruit is spent on the worker and on seeds; 129 of its 130 harvests are in the opening.
   *(evidence: A1, A2)*

2. **One extra worker, bought once, that cannot harvest.** — OBSERVED INVARIANT for the bundle
   (160 of 160: `TRAIN ms cc 0 chop`, **each talent at the largest value its own resource affords**
   — the price of each talent is paid from its own fruit, RULES §8, so this is simply the largest
   affordable worker, unique at all 160 purchases; harvest power always 0). LADDER-TESTED in one
   direction only: making it *wait* for a `2/2/0/2` worker read two points below it (`DOMAIN.md`
   §2), so the value of the exact talent rule is not itself proven. **When it buys is OPEN**:
   median turn 9, range 1..35; in 159 of 160 it bought on the first turn its bundle became
   affordable, but what it was waiting for is invisible; the simplest rule tested agrees in only
   63 of 160 and otherwise buys ten turns early with a weaker worker. `champion-purchases.json`
   holds the data to fit your own. *(evidence: A3)*

3. **Earn the worker's price in the opening if turn 1 cannot pay it.** — OBSERVED INVARIANT
   (mining iron if the map has it, harvesting fruit otherwise, only in the first ~14 turns, only
   until the worker is affordable); LADDER-TESTED that the worker must come early (every attempt to
   spend the opening on something else read far below the reference, `DOMAIN.md` §2). The form is a
   HABIT. *(evidence: A2)*

4. **Prefer mature trees.** — OBSERVED INVARIANT (94 % of its chops on the map's own trees are on
   size-4 trees, 4 wood = 16 points); SCORE MECHANISM (a tree's wood is paid only when it dies, and
   a worker's carry caps what it can take from a dying tree, `DOMAIN.md` §3). *(evidence: A4.1)*

5. **A tree once started is finished.** — OBSERVED INVARIANT. Of 1,796 map trees the reference
   was first to chop, the same worker chopped every turn until the tree fell in 1,515 (84 %); in
   207 (12 %) its teammate finished it; in 18 the worker left and came back; only 53 (3 %) were
   lost to the opponent after the first chop, and 3 were still standing at the end.
   *(evidence: A4.5)*

6. **The two workers never share a tree and never get in each other's way.** — OBSERVED
   INVARIANT. In 39,023 turns with two workers alive, the two never chopped the same tree in the
   same turn, a worker never set out to a tree its teammate was already standing on, and a move
   within a worker's speed was never left undone because the teammate stood on the target cell.
   How they divide the trees between them is part of the OPEN choice below. *(evidence: A4.6)*

7. **Which tree next is OPEN.** It goes to the nearest available tree 44 % of the time and no more
   than one walking turn further 65 % of the time. The best simple rule found — *fewest turns to
   wood*, walking turns plus chopping turns — picks its tree 39.7 % of the time and is within its
   top three 82 % of the time. No rule tested does better. This, with principle 2's timing, is the
   largest open choice in the document. *(evidence: A4.2)*

8. **Bank full loads.** — HABIT, with a reason: 84.5 % of its `DROP`s are at exactly full
   capacity; the walk home is the cost of a trip. *(evidence: A4.3)*

9. **The endgame conversion: turn the shack's fruit into wood at the door.** — SCORE MECHANISM:
   a fruit in the shack is 1 point; taken back out (`PICK`), planted on a cell next to the shack
   (`PLANT`), felled (a new tree ticks to size 1 on the turn it is created, RULES §7) and banked
   (`DROP`), it is 4 points — **+3 per seed**. One chop of power 3 fells a banana sapling (3
   health), so the cycle is four commands for a strong chopper on a banana; plum and lemon (6) and
   apple (11) saplings, or a weaker chopper, need more chop turns. OBSERVED INVARIANT on the
   window: before turn 251 it converts **only when at most four trees are alive** (102 of 102
   early starts), and from turn 251 it converts regardless (the other 50). It takes the seed whose
   sapling is cheapest to fell — banana first, then plum and lemon (equal health; plum before lemon
   is a HABIT), then apple. It plants next to its shack in 1,621 of 1,622 plants. **The exact turn
   it starts inside that window is OPEN**: it is *not* a matter of score (58 of the 102 early starts
   came while behind, 44 while ahead), and on 1,298 qualifying turns a worker was free with a tree
   still available and it kept logging instead. `endgame-truth-table.json` holds every qualifying
   turn. *(evidence: A5)*

10. **Nothing but wood pays.** — HABIT, with a reason. After the opening it never harvests; when
    nothing pays it `WAIT`s (4,513 times, two thirds after turn 200). A fruit is 1 point; a trip for
    fruit is not worth its turns against wood at 4. *(evidence: A4.4)*

**Two notes that are not principles.** It never asks the referee to route: every one of its
40,143 `MOVE`s names a cell reachable this turn, so the random tie-break (RULES §4) never touches
it — a HABIT you may keep for determinism. And **no response to the opponent's position was
detected**: nothing measured here changed with where the opponent's trolls were (it does not race
them, block them, or prefer trees near their shack), and its conversion start does not depend on
the score either; whether anything else depends on the opponent was not measured. The strongest
players do not win by destroying the opponent's plantings (`DOMAIN.md` §1.4).

**The largest known gap** between this bot and the strongest players is not in this list: they
run a renewable wood farm from turn 1 and this bot does not (`DOMAIN.md` §1.3). Two attempts to
close it are recorded there; both failed for stated reasons. You are not required to close it,
and not forbidden to try.

---

# Part II — The evidence

Every principle in Part I, with the counts and the matches that support it. Rates are rates on
this population of 160 matches (§A8 on what that means).

## A1. What it scores with

Across the 160 matches its shack ended with, on average, 45.07 wood, 2.36 apples, 0.55 bananas,
0.19 plums, 0.16 lemons, 0.74 iron — a mean final score of 183.5, median 181; **98.2 % of the
score is wood.**

The whole command budget over 160 matches:

| command | count | |
|---------|-------|--|
| MOVE    | 40,143 | |
| CHOP    | 26,149 | |
| DROP    |  5,171 | |
| WAIT    |  4,513 | |
| PICK    |  1,623 | the seed loop (A5) |
| PLANT   |  1,622 | the seed loop (A5) |
| TRAIN   |    160 | **exactly one per match** |
| MINE    |    130 | opening only (A2) |
| HARVEST |    130 | opening only, all but one (A2) |

## A2. The opening, and how it moves — 40,143 / 40,143

**Turn 1 is always a MOVE**, in all 160 matches: the starting troll leaves the shack cell
immediately. In 59 of the 160 it also prints a `TRAIN` on turn 1.

Earning the difference when it cannot afford the worker on turn 1 takes one of two forms:

- **MINE** — 52 matches contain at least one, all inside the first 14 turns.
- **HARVEST** — 63 matches contain at least one, nearly all inside the first 10 turns.
- 12 matches contain both; **57 matches contain neither** — it could already afford its worker.

- game 900571119, turn 1: `MOVE 1 11 3` — the troll steps off the shack and nothing else.
- game 900571122, turn 1: `MOVE 0 3 3` — the same, from the other seat.
- game 900571119, turns 3 and 7: `MINE 1`, twice, before it can afford its worker at turn 16.
- game 900571120, turn 7 and game 900571121, turn 8: `HARVEST 1` in the opening.

The 130 HARVEST commands and 130 MINE commands in the whole corpus are, with one HARVEST late
in one match, this opening behaviour.

**It never asks the referee to find a path.** Over all 40,143 MOVE commands, the walking distance
from the troll to the cell it names was never greater than the troll's own movement speed; in
38,149 of them (95.0 %) it was **exactly** the speed, and in the other 1,994 it was less (the
troll is arriving).

- game 900571119, turns 1 and 2: troll 1 is at (11,2) with speed 1 and prints `MOVE 1 11 3`;
  next turn it is at (11,3) and prints `MOVE 1 12 3`. Each target is one step away.

## A3. The worker — 160 / 160

**One `TRAIN` per match. Never a second.** In all 160, the command is issued while it still has
exactly one troll. It finishes every match with two trolls.

**What it buys (160/160):** among every troll it could afford at that moment, the one with
**harvestPower 0** — always — and **the largest possible `movementSpeed + carryCapacity +
chopPower`**. In no match was a troll that is at least as good in all three of those and better
in one affordable and passed over. Because each talent's price is paid from its own resource
(RULES §8), this is the same as "each talent at the largest value its own resource affords", and
the best affordable bundle was unique at all 160 purchases. The commonest buys are `2/2/0/3`
(24 matches), `2/2/0/2` (21), `1/2/0/2` (13), `2/3/0/2` (12); the full spread runs from `1/1/0/2`
to `3/3/0/3`. Written as a command (RULES §8 argument order): `TRAIN ms cc 0 chop`.

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
earlier, is not recoverable from what a spectator can see.

The simplest rule tested — *wait until the best affordable worker has `ms + cc + chop >= 5`, then
buy it; buy unconditionally by turn 35* — buys on the same turn as this bot in only **63 of 160**
matches; in the other 97 it buys **earlier**, by a median of 10 turns and up to 27, and usually a
weaker worker (game 900571120: this bot buys `2/2/0/2` at turn 14; the rule buys `2/1/0/2` at
turn 1). Thresholds 4 and 6 do no better (60 and 59 of 160). So the bot waits for something a
threshold does not capture. The material to fit your own rule is in **`champion-purchases.json`**:
for each of the 160 matches, the shack's contents on every turn up to the purchase, whether the
map has iron, and what was bought on which turn.

## A4. Felling trees — the main loop

Between the opening and the endgame, both trolls do the same thing: walk to a tree, chop it
until it dies, carry the wood home, drop it, walk to the next tree.

### A4.1 It prefers grown trees

Of 12,971 chop commands aimed at trees that were on the map when the match began,
**12,217 (94.2 %) were on size-4 trees** — the biggest, worth 4 wood = 16 points. Sizes 1, 2 and
3 account for 142, 285 and 327. (The self-planted trees of A5 are a different pattern, counted
there.) This counts the size of the tree under each chop; what happens after the first chop is
A4.5.

### A4.2 Which tree it walks to — APPROXIMATE, best rule 39.7 %

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

No rule tested reproduces this bot's target choice. If you implement "go to the tree that puts
wood in your hands soonest, counting walking and chopping", you have a bot that agrees with the
reference on about two journeys in five and is within its top three choices on four in five. That
is the observable ceiling from replays alone; the remaining difference is either information a
spectator cannot see, or a tie-break, or a factor not measured here.

### A4.3 It banks a full load — 4,371 / 5,171 (84.5 %)

`DROP` happens next to its own shack (the rules force that) and, in 84.5 % of drops, the troll is
carrying **exactly its full capacity**. The 800 short drops are almost all one item in a capacity
of 2 or 3 (622 + 149) — a troll going home part-loaded, which happens but is not the habit.

- game 900571119, troll 1 (capacity 1): drops at turns 5, 9, 15, 31 — every one at full load.
- game 900571119, troll 3 (capacity 2): drops 2 items at turns 24 and 35.

### A4.4 It stands still rather than make work

4,513 WAIT commands. They are not evenly spread: the median WAIT is at turn 235, and 68 % of
them come after turn 200. In 860 of them a troll is standing **on** a living tree (waiting, not
walking away); in 1,436 there is not a single tree left alive anywhere on the map.

- game 900571120, turns 291-293: troll 2 stands on the tree at (8,1) and WAITs three turns
  running instead of leaving it.
- game 900571120, turns 296-297: no tree is alive anywhere and it WAITs out the clock.

### A4.5 A tree once started is finished — 1,515 / 1,796 by the same worker

For every tree that was on the map at the start and that one of the reference's workers was the
first to chop (1,796 trees), what happened between that first chop and the tree's death:

| outcome | trees |
|---------|------:|
| the first worker chopped it every turn until it fell | **1,515 (84.4 %)** |
| the teammate felled it (a hand-over) | 207 (11.5 %) |
| the first worker left and came back to finish it | 18 (1.0 %) |
| lost: felled by the opponent after our first chop | 53 (3.0 %) |
| still standing at the end of the match | 3 |

So 96 % of the trees it starts are felled by its own team, five in six of them without the
worker ever leaving the cell.

### A4.6 The two workers never share a tree and never block each other — 0 / 39,023

Over the 39,023 turns on which the reference had two workers alive: **0** turns on which both
chopped the same tree; **0** of its 4,079 chop journeys ended on a tree its teammate was already
standing on; and **0** of its 40,143 within-reach moves were left undone with the teammate on the
target cell. The division of labour is silent in the recordings — no rule for *which* worker
takes *which* tree was recovered — but its outcome is an invariant.

## A5. The endgame conversion

1. a troll stands on a GRASS cell **orthogonally adjacent to its own shack**;
2. `PICK` — it takes one fruit out of the shack;
3. `PLANT` — next turn it plants that fruit on the cell it is standing on;
4. `CHOP` — the sapling ticks to size 1 the turn it is created (RULES §7), so it can be felled
   at once — in one turn if the chopper's power covers the sapling's health (banana 3, plum and
   lemon 6, apple 11), otherwise in several;
5. `DROP` — the wood goes into the shack. Net: **+3 points per seed, per troll.**

The counts that fix each step:

- **1,623 PICKs and 1,622 PLANTs** — they come in pairs.
- **Almost every plant is at Manhattan distance 1 from its own shack**: 1,621 of 1,622. (The
  single exception is at distance 2.) It does not plant out on the map.
- **Self-planted trees are chopped as saplings**: of 6,664 chops on cells it planted itself,
  5,536 (83 %) were on a size-1 tree. Compare A4.1, where 94 % of chops on the map's own trees
  were on size-4.

- game 900571119: troll 3 plants a banana at (11,3) — its shack is at (11,2) — on turns 260,
  265, 270, 275, and troll 1 plants at (10,2), the shack's other neighbour, on turns 266 and 272.
  The matching PICKs are at turns 259, 264, 265, 269, 271, 274.

### A5.1 Which seed it takes — 1,609 / 1,623 (99.1 %)

Given what is in the shack, it takes the first available in this order:
**BANANA, then PLUM, then LEMON, then APPLE** — the order of how cheap the sapling is to fell
(size-1 health 3, 6, 6, 11; RULES §6), with plum before lemon at equal health as a tie-break
the economics do not explain. Measured, by what the shack held at that moment:

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

The 14 exceptions are all turns where **both** trolls picked at once and the second took the next
species down.

- game 900571119, turns 259, 264, 265, 269, 271, 274: shack holds plums and apples and bananas
  each time, and it takes BANANA every time.

### A5.2 When the loop starts — the window is determined, the turn inside it is not

The first `PICK` of each match (152 matches have one; the other 8 ended before either bound):

- **Before turn 251 it starts only when at most four trees are alive** — in all 102 early starts
  (median 2 trees alive; the earliest start was turn 41). There is no match in which it started
  before turn 251 with five or more trees standing.
- **From turn 251 it starts regardless** — the other 50 first PICKs fall between turns 251 and
  267, with a median of 8 trees still alive and up to 24.

What the recordings do **not** support is the converse, "at most four trees ⇒ it starts". The
truth table in `endgame-truth-table.json` lists every turn before 251 on which at most four trees
were alive, up to the first PICK — 2,634 turns:

| turns before 251 with ≤ 4 trees alive | it started | it did not |
|---|---:|---:|
| a worker was free (carrying nothing, not on a tree) and a tree was still available to it | 91 | 1,298 |
| a worker was free and no tree was left for it | 11 | 139 |
| no worker was free (all on trees or carrying) | 0 | 1,095 |

And the score has nothing to do with it: at the 102 early starts the reference was **behind in
58 and ahead in 44**; the 1,298 "free worker, free tree, kept logging" turns split 1,169 ahead,
106 behind, 23 tied. So the start is not "when the map is nearly bare" and not "when behind": on
most qualifying turns it prefers one more tree to the first seed, and what tips it — most likely
a comparison of the turns the next tree would cost against the turns a conversion cycle costs —
is not visible to a spectator. **The exact start inside the window is OPEN.**

- game 900571125, turn 176: only 2 trees left of the 16 the map started with — it starts.
- game 900571119, turn 259: 24 trees alive (both sides have been planting) — it starts anyway,
  because the match is nearly over.
- game 900571120, turn 254 and game 900571121, turn 257: 1 and 2 trees left, late.

## A6. What it does *not* do

Each of these is an absence measured over 160 matches, not a guess:

- **It never trains a second extra worker** (160 TRAINs in 160 matches; game 900571119 buys at
  turn 16 and never again through turn 300).
- **It does not plant out on the map** — 1,621 of 1,622 plants are on its own doorstep
  (game 900571119, turns 260-275, every plant at (11,3) or (10,2) beside its shack at (11,2)).
- **It barely harvests fruit** — 130 harvests, all but one in the opening
  (game 900571119: one HARVEST, at turn 14, in a 300-turn match).
- **It never MOVEs to a cell it cannot reach this turn** — 0 of 40,143 (game 900571119,
  turns 1-2, and every other MOVE in the corpus).
- **No response to the opponent's position was detected.** Nothing measured here changed with
  where the opponent's trolls were; it does not race them to trees, block them, or chop trees near
  their shack in preference to trees near its own. Its conversion start was tested against the
  score and found independent of it (A5.2). Other forms of dependence were not measured.

## A7. How the numbers were made

The recordings show the board visually; the tool used to decode them recovers each tree's size,
health and cooldown by simulating the rules forward. Sizes and healths quoted here (A4.1, A5)
are therefore reconstructions — checked against the platform's next state on 40,458 recorded
turns with two disagreements. Positions, carries, inventories and the commands themselves are
read directly and are exact. The counts of A1–A5.1 are produced by `measure.py`, those of A4.5,
A4.6 and A5.2's table by `measure_extra.py`; both are kept with the package's working files.

## A8. Sources of uncertainty

1. **Target choice (A4.2) is not determined.** Stated as a measured agreement, not a rule.
2. **The training turn (A3) is not determined.** Stated with the measured agreement of the
   simplest substitute and the data to fit your own.
3. **The conversion start inside its window (A5.2) is not determined.** Stated with the truth
   table.
4. **160 matches, one day, one ladder.** All 160 come from a single batch against the opponents
   the ladder happened to offer that afternoon. Rules that hold 160/160 here are strong; rates
   quoted as percentages are rates on this population.
