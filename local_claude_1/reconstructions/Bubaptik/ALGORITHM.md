# Bubaptik — the algorithm, as far as our corpus shows it

Writer W5, 2026-08-28 ~04:10Z. Bubaptik is #3 on the Legend ladder (27.90 at 19:50Z on 08-27), was not in
the contest's Legend league and has left no trace on the internet (`../sources/Bubaptik-NOTHING-FOUND.md`).
Everything below therefore comes from our own corpus of its games; there is no write-up to check it against.

**How much is measured and how much is guessed.** The *habits* — when it trains, what it buys, what it plants,
where, what it harvests, how the game splits into phases, how it does against whom — are measured over 191
games of its newest version (numbers with `n`, sources in §6). The *training rule* is measured to the point
where a program can copy it (§3.1: 95 % of purchases explained). The *mode switch* from fruit-farming to
wood-cutting is measured as an event (§3.2). The *target-choice rules* (which tree to chop, which cell to plant,
which tree to harvest) are fitted descriptions that explain 44–84 % of decisions teacher-forced (teacher-forced
= the rule is asked what it would do in the bot's own recorded situations, one decision at a time), never the
whole choice; the chop-target ordering in mid/late game is essentially not recovered (best rule ≈ 18 %
expected accuracy — "expected" = after the ties among the rule's equally-best choices are broken at random;
"in-set" = the real choice was somewhere among those ties). Every mechanism sentence that is not backed by a number is marked **GUESS**. The record's
closure applies (`../prior-art.md` §2, item 16 and §4): a fitted description is not an algorithm until it
regenerates the bot's own play; this document is the description, with its gaps named in §5.

Vocabulary used throughout. *Talents* = a troll's four attributes in the game's order — movement speed /
carry capacity / harvest power / chop power — written `4 3 0 2`. *TRAIN* = buy a new troll; with `n` trolls
already owned it costs `n + speed²` plums, `n + carry²` lemons, `n + harvest²` apples, `n + chop²` iron
(`docs/mechanics.md`). *PICK* = take a seed of one fruit kind out of the shack to plant it. *Wood* is worth 4
points, fruit 1 point. *Own half* = the half of the point-symmetric map that holds the own shack.
*BFS distance* = number of steps over grass cells. *Denial* = chopping trees the opponent planted or wants.

## 1. Who and what it is

**Identity in the corpus.** The pseudo `Bubaptik` appears under 34 agent ids (one id per resubmission) in
`games.jsonl`, 3,917 seat-games in all. The newest and most-played id is **6568138** (191 games, 192 seats;
one game has it in both seats); the four workers' analyses and this document use that id. Whether it is the
exact submission playing as #3 today is not recorded anywhere in the repo (`../prior-art.md` §1.3) — it is the
best available proxy.

**Version history** (my `train_trigger.json` → `versions`, from `games.jsonl`, all 34 ids): the older ids
(6542200 … 6557104; 48–136 games each) bought the second troll late (median turn 4–28) and a third troll of
`2 3 1 3` / `3 3 1 2`, with a speed-4 troll in only 13–35 % of games. From id 6563190 on, all 25 later versions buy
the second troll on turn 2 (median) and a speed-4 third troll in 63–88 % of games — the design described here
has been stable over the last 25 resubmissions. Win rates by version range 0.50–0.71 with no trend (different opponent
pools; the arena rating stored per game is the collector's constant 26.91, so per-version ratings cannot be
recovered). The 07-16 census saw an older id at rank 8 with a losing margin (−63.7, n=80; `../prior-art.md`).

**Results of 6568138** (`../profiles/Bubaptik.md` §9, n=191): win rate **0.654**; mean score 295 against
310 (it wins more games than it out-scores: it wins the close ones and loses big to the strongest). By the
opponent's final troll count: 2 trolls 74 % wins (n=90), 3 trolls 61 % (49), 4 trolls 57 % (46), 5+ 33 % (6).
By opponent rating: 20–25 → 86 % (65), 25–28 → 64 % (74), ≥ 28 → 32 % (37). Most frequent opponents:
Stounate 18, gaha 16, tass 15, MSz 13, norxondor_gorgonax 12, delineate 12, yaichi 11. Score composition:
wood 268 points + fruit 27 (wood share 0.908); final shack mean plum 12.7 / lemon 7.3 / apple 3.1 /
banana 4.0 / iron 1.9 / wood 67.1. Games last 298 turns on average (9 of 191 ended early); zero timeouts.

**Family.** Bubaptik is a **three-to-four-troll build-up bot** (the family of norxondor_gorgonax, MSz, wala,
laconic_pixel, xSkyline, aangairbender, FinkPloyd — `../sources/SUMMARY.md` §5–6): hard-coded troll targets,
an orchard of the training fruits next to the shack, a mass-wood phase from mid-game, 3.31 trolls at the end
(2 trolls in 19 % of games, 3 in 36 %, 4 in 40 %, 5 in 5 %). It differs from every documented member of that
family in five ways: (a) it pays for **speed 4** (18 plums at roster 2) where the others pay for **carry 4**
(18 lemons) — it is the only top bot that ever buys speed 4, and it never buys carry 4 (0 of 425 trains); (b)
its orchard is therefore **plums** first (47 % of plants) rather than lemons/bananas; (c) the second troll is
bought on **turn 2** with "whatever the starting stock affords" (MSz buys a cheap worker on turn 1, delineate
on turn 7, norxondor on turn 9); (d) its wood phase is a **hard switch at the last TRAIN** (delineate has no
switch); (e) it banks the least wood of the four top bots (69 per game; MSz 80, norxondor 80, delineate 98),
although MSz issues fewer CHOP commands (118 against Bubaptik's 136).
From the two-troll chopper family (yamo, yaichi, skotz, Konstant, putibuzu, Escdemon) it shares only the
hybrid harvest-and-chop second troll and the early denial chopping (Konstant's "rush to train the cutter who
destroys the opponent's trees") — not the two-troll cap, not the pure banana plant-chop-drop loop. Its edge is
exactly against that two-troll family (74 % wins) and it is out-produced by the strong build-up bots.

## 2. The game plan, by phases

All per-turn rates are commands per game per 10 turns from `../profiles/Bubaptik.md` §8 unless noted.

**Phase A — the opening (turns 1–10).** Turn 1: the start troll (`1 1 1 1`) moves off the shack. Turn 2: TRAIN
the second troll (154 of 186 first purchases on exactly turn 2; the rule in §3.1). Turns 3–7: the start troll's
most common pattern is `M M K P K M P` — pick a seed, plant it on a shack-adjacent cell (turn 4), pick again,
step out, plant at distance 2 (turn 7); first plant is a PLUM in 64 % of games, a LEMON in 34 % (n=191); its
first non-move action is PICK in 74 % of games and HARVEST in 24 %. The new second troll walks to a wild tree
and harvests or, if it has chop power, chops (CHOP 0.3 per turn in the first 25 turns, my chop timeline).
First HARVEST median turn 9, first DROP 17, first CHOP 14, first MINE 55.

**Phase B — the training economy (turn ~10 to the last TRAIN, median turn 145).** Everybody feeds the next
troll's bill: harvest plums and lemons, drop them one or two at a time, mine iron (between turns 11–20 and
101–130, per 10 turns: HARVEST 1.9 → 4.1, DROP 1.1 → 4.1, MINE 0.3 → 0.7; 12 iron per game), and plant the
training fruits near the shack (before the last TRAIN: 773 plums, 687 lemons, 54 bananas, 6 apples —
`plan_end.json` → D). Chopping is low (1.5 per 10 turns at turns 50–120) and mostly denial: in turns 1–100,
50 % of chops hit trees the opponent planted and 41 % wild trees (profile §5). The stock climbs to the target:
plums 1.7 at turn 25 (spent on troll 2) → 9.4 at 100 → 11.3 at 125; lemons 1.4 → 6.8 → 7.8; iron 2.5 → 4.7 →
5.5 (`train_trigger.json` → curves, n=192). The third troll is bought at median turn 115 (p25–p75 = the middle
half of the games: 88–148), the fourth at 150 (132–174), a fifth at 164 (n=12; the profile says 164 on 10 games,
W4's `../fits/Bubaptik.md` prints 178 on 12 — not reconciled).

**Phase C — the wood phase (from the last TRAIN to ~turn 290).** The switch is immediate and global: in the
20 turns after the last TRAIN, CHOP goes from 0.03 to 0.69 commands per turn, PLANT from 0.03 to 0.15, MINE
from 0.04 to 0.00, while HARVEST stays 0.35 → 0.38 and then fades (0.20 by +60 turns) (`plan_end.json` → B,
1,380/1,371 turns for a rank-3 last train). Planting changes crop: after the last TRAIN, 1,835 plums, 1,110
bananas, 939 lemons, 134 apples; the bananas come out of the shack (890 banana PICKs after the last TRAIN
against 18 before) — the untouched starting bananas become the quick wood crop — while plums and lemons are
planted straight from the harvest carry. The choppers cut own trees at full size (W4: own-tree chops mostly at
size 4, median age 36 turns for plums, 46 for lemons) and run a quick banana stream (439 cuts of size-1
bananas, median age 7 turns; 888 cuts within 4 turns of planting — `../fits/Bubaptik.md` §3b). Wood in the
shack: 3.2 at turn 100 → 9.7 (150) → 27.4 (200) → 48.4 (250) → 66.7 (300); score 38 → 67 → 137 → 221 → 294,
the opponent 38 → 77 → 149 → 229 → 312 (curves, n=192…183).

**Phase D — the last 30 turns.** No separate endgame: last PLANT median turn 293, last DROP median 297 (p25–p75
292–299), last HARVEST median 280. Verb mix in the last 30 turns: MOVE 63 %, CHOP 21 %, DROP 7 %, PLANT 3 %,
HARVEST 3 %, WAIT 2 %; per game 20.5 chops, 6.5 drops, 3.0 plants, 11 wood in those 30 turns. WAIT appears only
from turn ~130 on and grows to 0.66 per game per 10 turns at the end — a troll with nothing worth doing stands
still (the only top bot that waits; profile §8).

**When the plan fails (2-troll games, 19 %).** If the third troll never becomes affordable, phase C never
comes: CHOP stays at 0.3–0.45 per turn and HARVEST at 0.12–0.26 per turn for the whole game (my chop timeline
by final roster, n=36); those games are won 43 % with a mean score of 176.

## 3. The per-turn decision procedure (pseudo-code with evidence)

```
each turn:
  update state: my trolls, stock (plum, lemon, apple, banana, iron, wood), trees, opponent trolls
  if mode == TRAINING and target affordable:            # §3.1
      TRAIN target; roster += 1
      if roster == planned_roster: mode = WOOD           # §3.2 (how the plan length is set: GUESS)
  for each troll (greedy = each troll takes its own best job in turn, no joint search — GUESS, see §3.7):
      job = choose_job(troll)                            # §3.3–3.6
      emit the command; a walk is one MOVE to the job's cell (destination-style)
```

### 3.1 Training (measured; `train_trigger.json`, 422 successful TRAINs of 192 seats)

**Second troll (turn 2).** Buy, on turn 2, the troll whose every talent is the highest level the starting
stock affords for that resource alone (level `k` costs `1 + k²` of the resource; harvest and chop may be 0,
speed and carry are at least 1). Evidence: of 154 purchases made on turn 2, **147 match all four talents**
(carry 154/154, harvest 154/154, chop 154/154, speed 147/154 — the 7 misses bought speed 2 with exactly 10
plums, where speed 3 was affordable). The resulting talents are `2 2 2 2` (18), `2 2 1 2` (16), `2 2 2 1`
(14), `1 2 2 2` (14) … because starting draws are 2..10 per resource: level 2 needs 5, level 3 needs 10. The
purchase spends 76 % of the starting bank on average (n=154).
*Delayed second troll* (32 of 186 first purchases, turns 4–72): in 31 of the 32 the start had fewer than 5
lemons (carry would have been 1); 26 of them bought carry 2–3 after harvesting lemons, 19 on the very turn the
stock reached 5 (e.g. start `8 2 5 9 9` → `2 2 2 2` on turn 8; start `4 2 4 9 10` → `1 2 1 3` on turn 20); the
one exception had 9 lemons and waited two turns for the 10th to buy carry 3. But 32 other games with lemons
< 5 bought carry 1 on turn 2 anyway — the criterion that separates "wait for lemons" from "buy now" (a lemon
tree within reach? — **GUESS**) is not recovered.

**Trolls 3, 4, 5.** Target = `4 3 h c`: speed 4 (18 plums at roster 2, 19 at 3), carry 3 (11 lemons at
roster 2) — so the bill that must be affordable is the floor `4 3 0 2` (at roster 2: 18 plums, 11 lemons,
2 apples, 6 iron), and `h` and `c` are then raised to what the stock affords: `h` = the highest harvest level the apples afford (0 if apples < roster+1, else 1; 2–3 only when
apples allow — 64 zeros, 72 ones, 11 higher at troll 3; the bot never farms apples), `c` = 3 if iron ≥ roster+9,
else 2 (troll 3: iron ≥ 11 → chop 3 in 37/37 cases, iron < 11 → chop 2 in 107/110; troll 4: iron ≥ 12 → chop 3
in 59/59). Caps: speed 4 even when 5 or 6 was affordable (16/16 cases), carry 3 even when 4–6 was affordable
(43 cases: 25 + 13 + 5 at trolls 3/4/5) — a carry-4 troll was never bought in 425 trains. **Trigger = the first turn the target is
affordable**: delay 0 turns in 139/147 (troll 3), 67/77 (troll 4), 11/12 (troll 5); W4 counts delay 0 in 254
and delay 1 in 150 of 425 with a slightly different affordability accounting (`../fits/Bubaptik.md` §0). Stock
at the moment of a speed-4 purchase: plums median 18 (min 18), lemons median 12 (min 11), iron median 8,
apples 3 — the bot buys the instant the last resource arrives.

**The speed-1 fallback** (27 of 147 third trolls, 19 of 77 fourth): `1 3 h c` (3 plums instead of 18), bought
at median turn 107 (p25–p75 70–133), when plums were scarce — the plum stock had never exceeded 17 (median
maximum 8) and only 9 plums had been harvested so far against 22 in the speed-4 games; the map had the same
number of plum trees (1.8 vs 2.1 on the own half). Mechanism **GUESS**: the bot degrades the speed target when
its estimate of the time to reach 18 plums is too long (Escdemon's and xSkyline's write-ups describe this kind
of "best affordable within a reasonable timeframe" rule); a simpler "plums < X when lemons and iron are ready"
does not fit (one purchase happened with 17 plums, 40 lemons).

**End of the plan.** No TRAIN is ever attempted after the last successful one (0 of 192 games). In games that
end with 2 trolls, a `4 3 0 2` third troll was never affordable (0/37) and a `1 3 0 2` only once; with 3 trolls,
a fourth was affordable in 2/69 (fast) and 12/69 (cheap); with 4 trolls, a fifth was affordable in 14/76
(fast, median turn 166) and 28/76 (cheap) and not bought (`plan_end.json` → C). So the plan is mostly ended
by the economy, but there is a cap the data cannot pin down: **GUESS** either a maximum roster tied to the
opponent's (own trolls at the end average 2.85 against 2-troll opponents, 3.4 against 3, 4.0 against 4, 4.5
against 5) or a turn limit (last TRAIN never after turn 242 for a fourth, 223 for a fifth; 290 once for a
third).

### 3.2 Mode switch (measured event, mechanism GUESS)

The change to wood-cutting happens at the **last** TRAIN and not at the others: around a third troll that is
*not* the last, CHOP goes 0.00 → 0.13 per turn and HARVEST 0.43 → 0.62 (the new troll harvests and MINEs
0.17 per turn — iron for the next troll's chop 3); around a third troll that *is* the last, CHOP 0.03 → 0.69,
MINE 0.04 → 0.00 (`plan_end.json` → B). Hence the bot knows at purchase time that the roster is complete —
**GUESS**: a planned roster size (per map or per opponent) set before the purchase; the alternative, "switch
when the next troll looks unreachable", would not produce a switch on the very turn of the purchase.

### 3.3 Roles (measured; W4 `../fits/Bubaptik.md` §0 and profile §7)

- Troll 1 `1 1 1 1` — the farmer: HARVEST 38 %, DROP 31 %, PLANT 15 %, CHOP 10 %, PICK 5 %, MINE 1 % of its
  action turns (182 units); it lives 1–2 cells from the shack, harvests one fruit (carry 1) and drops it.
- Troll 2 `2 2 x x` — the hybrid: CHOP 44–46 %, DROP 23–27 %, HARVEST 18–24 % (`2 2 2 2`, `2 2 1 2`, `1 2 2 2`);
  the `2 2 2 1` variant harvests more (32 %) and chops less (25 %). It is the early denial chopper and a second
  harvester.
- Trolls 3+ `4 3 h c` — choppers: CHOP 69–77 %, DROP 19–22 %, HARVEST ≤ 6 %, MINE 1–3 %. Speed 4 makes long
  trips cheap: 34 % of their chop trips are ≥ 5 cells (W4 §1).

### 3.4 Harvest (fitted; W4 §3, 7,646 harvest trips with movement)

Target = the **nearest tree with fruit that no other own troll stands on**: 54.3 % of trips in the rule's
choice set, **44.0 % expected** after random tie-breaks; the throughput value `min(fruits, free capacity) /
(travel + harvest turns + return + 1)` explains 51.0 % (32.7 % expected); "closest to the shack" only 27.6 %.
Harvested kinds: plums 3,592, lemons 3,135, apples 511, bananas 408 — 64 % from own-planted trees (profile:
72 % own, 27 % wild over all 14,911 harvests); 44 % of targets stand 2 cells from the shack. Kind preference —
**GUESS**: the fruit still missing for the current target (plums until 18, lemons until 11), because harvests
are 52 % plums although plums are 47 % of what it plants and the plum stock is held at 11–13 once the last
troll is bought. Not fitted.

### 3.5 Plant (fitted; W4 §2, 5,279 PLANT actions)

Cell = the empty cell that **minimises d(shack) + d(troll)** — i.e. the nearest free cell on the way between
the troll and the shack: 84.2 % (2,143 ties among hits); "nearest to the troll" 81.5 %; "nearest to the shack"
49.7 %; water-adjacent rules 16–21 % (rejected — water is not sought). 1,689 plants without moving, 2,267
after one step. Distance from the shack: 1 cell 2,272, 2 cells 1,300, 3 cells 692, then a tail to 12 (mean 2.4
— farther out than the other three, 12 % beyond 4 cells; profile §3); 99 % on the own half, 23 % next to water.
Kind: training phase plums and lemons (526 + 470 in turns 0–49, 30 bananas); wood phase plums, bananas,
lemons (turns 250–299: 424 / 396 / 140). Kind rule — **GUESS** by phase: before the last TRAIN, the fruit of the
next bill (plum or lemon) carried from a harvest or picked; after it, whatever the troll carries plus bananas
picked from the shack (890 PICKs). Not fitted.

### 3.6 Chop (fitted; W4 §1, 5,019 chop trips with movement + 2,062 in place)

- Early game (decision turns 1–100, 805 trips): the chopper goes to the **opponent's half and cuts the nearest
  tree there** — "nearest tree on the opponent half, else nearest" 55.5 % (42.5 % expected), "nearest
  opponent-planted tree" 46.0 % (37.5), "closest to the opponent's shack" 38.8 % (23.8), plain "nearest tree"
  47.2 % (35.1), "nearest fruitless tree" 34.9 % (28.4). Value rules score 70 % in-set but only 10 % expected
  (a carry-2 troll makes every tree of size ≥ 2 worth the same 2 wood). The profile's "57 % of all chop
  commands hit size-1 trees" is doubtful: that field reads the viewer's stage after the turn's tick and
  contradicts the exact fits for delineate (`../delineate/ALGORITHM.md` §5b); the exact trip data below say
  size 4 in 70 %.
- Mid and late game (1,828 + 2,386 trips): **no simple rule reproduces the choice** — best are `wood /
  (travel + chop turns + 1)` 33.6 % / 31.3 % (18 % expected) and `size / (travel + 1)` 41.2 % late (17.7 %
  expected); "nearest tree" 15–18 %. Descriptively the target is size 4 in 70 % of moved-to chops, 44 %
  carry 3 fruits (fruit is no deterrent), planted by itself 2,040 / by the opponent 1,781 / initial 1,198;
  restricting candidates to trees without another own troll on them lifts the value rules by ~3 points
  (40.6 %) — trolls do not double up on a tree.
- Wood per game 68.9 (profile), of which 39.9 from own trees, 14.0 from the opponent's, 14.5 from the map's —
  the lowest own-orchard yield of the four and the highest reliance on the map (W4 §3b). 53 % of chops are
  made with chop power 2 (profile §5).

### 3.7 Banking, mining, movement, coordination

- **Banking**: DROP 90 per game, 1.64 items per drop (the farmer drops single fruits, the choppers 3 wood);
  a "go home" is issued as `MOVE id <shack x> <shack y>` — the shack cell itself is the target in 23 % of all
  MOVEs, the referee parks the troll next to it, and reports 26.6 harmless "can't move" failures per game.
- **Mining**: by the farmer/hybrid in turns 60–130 before the next purchase and by a fresh `4 3 0 x` troll right
  after a non-last purchase (MINE 0.17 per turn); none after the last TRAIN. Iron is mined only up to the next
  troll's chop bill (iron stock 5.5 at turn 125 → 2.0 at the end).
- **Movement**: MOVE commands name the destination, not the next step (mean 2.85 cells away, up to 29; 26 % of
  targets are unwalkable cells such as the shack). The bot lets the referee's BFS do the pathing.
- **Coordination** — **GUESS**: a greedy per-troll job assignment without lookahead. Evidence for "no search":
  destination-style moves, WAIT for idle trolls, 0 timeouts in 191 games, trolls never sharing a target tree.
  Evidence against is absent, not present — a short search cannot be excluded.
- **Messages**: none (the profile's MSG table is empty).

## 4. Numbers and parameters

| parameter | value | n / source |
|---|---|---|
| second troll | turn 2; talents = max level per resource with `1+k² ≤ stock` | 147/154 exact; `train_trigger.json` |
| later trolls | `4 3 h c`; plums ≥ roster+16, lemons ≥ roster+9; h = max by apples; c = 3 if iron ≥ roster+9 else 2 | 422 trains |
| trigger | first affordable turn (delay 0) | 139/147, 67/77, 11/12 |
| caps | speed ≤ 4, carry ≤ 3 (carry 4 never) | 425 trains, W4 |
| fallback | `1 3 h c` when plums scarce (max stock ≤ 17, median 8) | 27/147 troll 3, 19/77 troll 4 |
| troll 3 / 4 / 5 turn | median 115 / 150 / 164 (p25–p75 88–148 / 132–174 / 147–188) | 147 / 77 / 12 |
| roster at the end | 2: 19 %, 3: 36 %, 4: 40 %, 5: 5 % (mean 3.31) | 191, profile |
| plants per game | 28.8; PLUM 47 %, LEMON 30 %, BANANA 21 %, APPLE 2 % | 5,493, profile |
| plant cell | min d(shack)+d(troll): 84.2 %; mean distance 2.4; 23 % water-adjacent | 5,279, W4 |
| harvest target | nearest fruit tree without own troll: 54.3 % (44.0 expected) | 7,646, W4 |
| harvests per game | 78 commands, 86 fruit; plums 52 %, lemons 35 % | 14,911, profile |
| early chop target | nearest tree on the opponent half: 55.5 % (42.5 expected) | 805, W4 |
| late chop target | not recovered (≤ 18 % expected); size 4 in 70 % | 4,214, W4 |
| chops per game | 136 commands, 103 landed, 69 wood; chop power 2 in 53 % | 26,048, profile |
| mining | 8.3 MINE, 12 iron, turns 60–130, 92 % of games | 191, profile |
| mode switch | CHOP 0.03 → 0.69 per turn at the last TRAIN; MINE → 0 | 2,751 turns, `plan_end.json` |
| wood / score curve | wood 3 (t100), 10 (150), 27 (200), 48 (250), 67 (300); score 38 / 67 / 137 / 221 / 294 | 192…183 seats |
| endgame | last PLANT 293, last DROP 297, last HARVEST 280 (medians); WAIT 0.66 per 10 turns at the end | 182–191 |
| move style | destination MOVEs, mean 2.85 cells; 23 % target the shack cell; 26.6 blocked per game | 62,439, profile |
| results | 0.654 wins; 74 % vs 2-troll, 57 % vs 4-troll, 32 % vs rating ≥ 28 | 191, profile |

## 5. What is missing

1. **The mid/late chop-target ordering** — the largest gap: the best single rule reaches ~18 % expected
   accuracy (W4). Whether it is a value with a denial term, a distance-limited "biggest tree", or an
   assignment over all trolls is unknown.
2. **How the planned roster size is set** (§3.1 end, §3.2): why 14 affordable fifth trolls were not bought,
   why the switch is known at the last purchase; the correlation with the opponent's roster is not a rule.
3. **The speed-1 fallback criterion** (§3.1): a time-to-afford estimate is a guess.
4. **The delayed second troll** (32 games): "wait for 5 lemons" fits 24 but not the 32 that bought carry 1.
5. **Plant kind and harvest kind** rules: only phase-level shares; no fitted rule (W4 fitted cells, not kinds).
6. **The WAIT condition** (which jobs are judged worthless) and the DROP timing of the choppers.
7. **Whether any lookahead exists** (§3.7): all evidence is circumstantial.
8. **The 7 turn-2 purchases** that bought speed 2 with 10 plums (speed 3 affordable).
9. **Older versions**: only id 6568138 is analysed at decision level; 33 other ids (3,726 seats) only for the
   ladder (§1). The ladder-#3 submission may be newer than 6568138.
10. **No closed-loop test**: nothing here has been played (`../prior-art.md` §2, items 2, 11, 16).

## 6. Sources and confidence

- `../profiles/Bubaptik.md` + `.json` (W3; agent 6568138, 191 games, exact positions and tree origins from the
  referee log in the raw replays) — every "profile" number above. **HIGH** as measurement.
- `../fits/Bubaptik.md` + `Bubaptik_fit_results.json` (W4; 182 full-length games reconstructed exactly, 45,515
  unit trips; a first pass) — the plant-cell, harvest, chop and role fits. **HIGH** as measured accuracies;
  the rules themselves are descriptions, **LOW–MEDIUM** as mechanism.
- `train_trigger.py` → `train_trigger.json`, `plan_end.py` → `plan_end.json` (this directory; `games.jsonl`
  plus the raw replays' inventory lines; the TRAIN cost was visible on the own inventory line in 422/422
  purchases, which validates the seat mapping) — the training rule, the version table, the curves, the switch,
  the plan's end. **HIGH** as measurement; the fallback and plan-length mechanisms **GUESS**.
- `../sources/SUMMARY.md` §5–6 and the per-player write-ups (W1) — the two families and the analogies.
  **MEDIUM** relevance: none of them is Bubaptik. `../sources/Bubaptik-NOTHING-FOUND.md` — no write-up exists.
- `../prior-art.md` §1.3, §2, §4 — the censuses, the closures, the "description, not algorithm" rule.

Overall: the training plan and the phase structure can be programmed from this document with confidence; the
target-choice layer (chop, plant kind, harvest kind) would have to be designed, not copied, and the whole
would then need the closed-loop gate the record demands.
