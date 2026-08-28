# MSz — the algorithm, reconstructed (writer W5-MSz, 2026-08-28 ~04:30Z)

MSz is #4 on the multiplayer ladder (27.72) and was #10 in the contest (27.25) with an earlier version.
He wrote nothing about Troll Farm. This reconstruction stands on four legs, named at every rule:

- **CORPUS** — our 216 ladder games of agent `6479460` with every command, exact positions and tree
  origins from the referee's own per-turn log (`profiles/MSz.md`, read 2026-08-28 06:2xZ), plus the exact
  per-turn decision tables that worker W4 rebuilt from the same replays (`fits/tables/MSz_trips.jsonl.gz`,
  66,753 unit trips; `MSz_turns.jsonl.gz`, 60,900 player-turns over the 203 games that ran 300 turns) and
  W4's first-pass report `fits/MSz.md` (04:15Z). The rule accuracies below are W4's (`fit_rules.py`); the
  train-trigger, orchard-by-kind, seed-source and early-chop numbers come from a small extra script over
  the same tables (scratchpad `w5msz/custom.py`, read-only).
- **CONTEST** — the game author's statistics over MSz's 634 contest games: only averages at 5-turn
  intervals (`sources/MSz-eulerschezahl.github.io-stats-2026-05-25.md` and the series in
  `all-legend-players-eulerschezahl-stats-2026-05-25.json`). Where the two disagree the corpus wins (it is
  exact and it is the ladder version); the contest numbers are kept where they add a time series.
- **FAMILY** — the first-hand write-ups of the other build-up bots (wala #6, laconic_pixel #8, xSkyline
  #14, aangairbender #16, FinkPloyd #21, eulerscheZahl #23, Astrobytes; `sources/SUMMARY.md` §5), used to
  say what kind of machinery a bot with these numbers usually has.
- **TOOLKIT** — MSz's own post-mortems of OTHER contests (`sources/MSz-github.com-marekesz-earlier-postmortems-2024.md`):
  an exact simulation engine, nested beam search (look ahead while keeping only the few most promising plans)
  / hill climbing (keep changing the plan while the score improves) over action sets, Hungarian assignment
  (an exact one-troll-per-task matching), hand-weighted evaluation. Nothing in them is about Troll Farm;
  everything drawn from them is a GUESS.

Words used below. *Talents* = the four troll attributes speed / carry / harvest / chop (movementSpeed,
carryCapacity, harvestPower, chopPower), written `2/4/1/3`. *Bill* = the price of one TRAIN: with `n` trolls
already owned, `n + speed²` plums, `n + carry²` lemons, `n + harvest²` apples, `n + chop²` iron. *Roster* =
trolls owned. *Troll 2, 3, 4* = the first, second, third troll bought (the start troll is troll 1). *Trip* =
a run of step-wise MOVEs ending in the first non-move action. *Median* = the middle value; *p10/p90* = the
10th/90th percentile.

---

## 1. What kind of program this is

**Measured.** A build-up economy bot of the "farm-first staged scale" family (`prior-art.md` §1.4): it buys a
cheap second troll on turn 1 in 196 of the 203 full-length games of the fit tables (reviewer's count; the
profile's "214 of 215" is its 25-turn bin — median turn 1, mean 1.56; six of the exceptions trained in turns
2–25 and one at turn 95, all with a troll affordable on turn 1, reason unknown), seeds an orchard of training fruit 1–2 cells from
its shack in the first ten turns, harvests that orchard and the wild trees to pay for a carry-4 lumberjack
(troll 3, bought in 84 % of games, median turn 95–97), then for a second carry-4, chop-3 lumberjack (troll 4,
38 % of games, median turn 128–129), never a fifth (0 of 216), and from turn ~110 converts the map into wood
while the two cheap trolls keep harvesting fruit to the last turn. It is the fruit specialist of the top
four: 112 HARVEST commands and 129 fruits per game (the others 78–90), 78 fruit points per game (the others
27–34), wood only 80 % of its points (profile, 216 games: 320 wood + 78 fruit = 399; fits, 203 full-length
games: 321 + 81; wood per game 51.4 from its own trees,
16.7 from the map's initial trees, 12.8 from the opponent's — `fits/MSz.md` §5). It does not deny: 78 % of
its chops are nearer its own shack, 16 % hit opponent-planted trees, 3.6 % of its early chop targets are
the trees closest to the enemy shack (delineate: 40 %), and in the contest it scored 480 against the
opponent's 481 (CONTEST) — it out-produces and gets out-produced. Corpus record: 57 % wins, mean score
399 vs 333; 12 % wins in the 34 games where it never bought troll 3, 56 % with three trolls, 77 % with four
(CORPUS §9).

**Inferred** (rules that reproduce the measured numbers, accuracy given): the turn-1 purchase rule (exact,
196/196), the train trigger and ladder (delay 0 in 441 of 444 TRAIN commands), the orchard size and place,
the harvest and chop target habits (only partly explained: no single formula beats ~60 % for harvest and
~35 % for chop).

**Guessed**: everything about *how* the decisions are computed — the search, the evaluation weights, the
opponent model. MSz's usual toolkit is a simulation search; the 8 timeout strikes in 216 games (the only
top-four bot with any) are consistent with a time-boxed search that sometimes overruns (CORPUS §9), and the
contest version had 0 timeouts in 634 games (CONTEST), so the ladder version is heavier or the servers slower.

**Ladder version vs contest version.** The same bot within measurement: trained talents average
1.62/1.73/1.48/1.00 → 2.02/4.00/1.00/2.60 → 2.01/4.00/0.00/2.90 on the ladder (CORPUS) vs
1.67/1.70/1.47/1.00 → 2.04/4.00/1.00/2.71 → 2.05/4.00/0.00/2.87 in the contest; three trolls at the end
45 % / four 38 % (ladder) vs 42 % / 47 % (contest); 29.5 vs 29.9 trees planted per game, with more bananas
on the ladder (39 % vs 30 %) and fewer plums (17 % vs 29 %). The lower ladder score (399 vs 480) is the
opponents (Bubaptik in 69 % of the corpus games).

---

## 2. The game plan by phases

### Phase 0 — turn 1: buy the second troll from the starting stock (CORPUS, exact)

The starting shack holds 2–10 of each fruit and of iron (`docs/mechanics.md`). Turn 1 output: the start
troll MOVEs off the shack and the shack TRAINs (verb share at turn 1: MOVE 0.99, TRAIN 0.97 — CORPUS §2).
The talents are read off the stock with the bill itself as the threshold (196 of 196 turn-1 trains in the
tables, no exception):

| talent | rule | evidence (n) |
|---|---|---|
| speed | 2 if plums ≥ 5, else 1 | stock 2–4 → speed 1 in 76/76; stock 5–10 → speed 2 in 120/120 |
| carry | 2 if lemons ≥ 5, else 1 | stock 2–4 → carry 1 in 54/54; stock 5–10 → carry 2 in 142/142 |
| harvest | 2 if apples ≥ 5 **and carry = 2**, else 1 | (lemons ≥ 5, apples ≥ 5) → 2/2 in 92/92; (lemons < 5, apples ≥ 5) → carry 1, harvest 1 in 29/29 |
| chop | always 1 | 215/215 in the profile; never 2 even with 10 iron |

Five plums is exactly the bill of speed 2 with one troll owned (1 + 2²); the harvest ≤ carry clause is the
same masking delineate describes ("masked troll targets where harvest > carry"). The contest averages
(1.67/1.70/1.47/1.00) are what this rule gives on uniform 2–10 draws. The one game with troll 2 at turn 95
is unexplained (possibly a bot failure on that map), as are the six full-length games that trained in turns
2–25 instead of turn 1 (§1).

### Phase 1 — turns 2–~25: seed the orchard from the shack, start harvesting and mining (CORPUS)

The opening line of the start troll is `M K M P M K P K M P` (move, pick, move, plant, …): both trolls
PICK seeds from the shack and PLANT them 1–2 cells away. Plants per game: 3.9 in turns 1–10, 2.4 in 11–20,
1.1 in 21–30 (CORPUS §3); first PLANT at median turn 4, its kind lemon 60 %, plum 25 %, banana 10 %,
apple 5 %. Own trees alive at turn 10: 3.7 per game (banana 1.40, lemon 1.30, plum 0.72, apple 0.26); at
turn 25: 6.2 (banana 2.5, lemon 1.9, plum 1.2, apple 0.5) (tables, n = 203). Kinds planted in turns 1–50:
banana 778, lemon 496, plum 325, apple 111 (fits). Seeds in the first 100 turns come from the shack (PICK
then PLANT: banana 654, lemon 255, plum 154, apple 46 trips) and almost as often from the harvested fruit
itself (HARVEST then PLANT on the way: banana 444, lemon 316, plum 185, apple 68) — the "field-fruit seed"
D167 noticed (`prior-art.md` §1.4). Harvesting starts at median turn 9 (first target wild in 89 %; lemon
43 %, plum 35 %), the first DROP at median turn 15, the first MINE at median turn 20 (CORPUS §2). Contest
series: the score falls from 12.6 right after the train to 8.2 at turn 15 (the seeds picked out), then
climbs 1.3–1.9 points per 5 turns from turn 25 to 50.

### Phase 2 — turns ~25–97: fund troll 3, the carry-4 lumberjack (CORPUS + CONTEST)

Troll 3 is `2/4/1/c` — carry 4 in 181/181, harvest 1 in 181/181, speed 2 in 177/181 (3 in 4), chop c = 2 in
87, 3 in 75, 4 in 19 (of which the speed-2 ones: 84 / 74 / 19) (CORPUS §1). The bills with two trolls owned: **6 plums, 18 lemons, 3 apples, and
6 / 11 / 18 iron** for chop 2 / 3 / 4.

*The trigger.* The TRAIN fires on the first turn its spec is affordable: delay 0 in 441 of 444 TRAIN
commands of any ordinal (1 turn in the other 3); the surplus over the bill at the train turn has median 0
in every resource (p90: plums 2, lemons 1, apples 2, iron 1). The chop level is the largest affordable on
that turn in 169/169 troll-3 trains (2→2: 86, 3→3: 67, 4→4: 16). The resource that reached its bill last
(the binding one): lemons in 61, iron 54, plums 38, apples 16 of 169. From the turn the lemons reach 18 to
the TRAIN: median 15 turns, p90 46. In 43 of the 54 iron-bound cases the bot trained the very turn 6 iron
(chop 2) was in the shack; in the other 11 it waited 1–20 more turns and bought chop 3 — unexplained
(GUESS: a "buy now or buy better soon" comparison inside the search, or iron already carried by a troll).

*The funding sequence, as concretely as the data allows.* (a) Seeds planted turns 2–10 (above). (b) The
two cheap trolls harvest lemons first: of 2,724 harvest trips in turns 1–50, lemon 1,635, plum 665, banana
222, apple 202; own trees 1,416, wild 1,269; 1,503 of the trips by the start troll. (c) The chop-1 trolls
mine one iron per trip (784 of 1,237 mine trips yield 1; 602 trips by the `1/1/1/1` start troll): 385
trips in turns 1–25, 297 in 26–50, 185 in 51–75, 222 in 76–100, then almost none after 150. (d) The
shack stock in the contest series: lemons 0.8 (turn 10) → 2.9 (30) → 8.1 (50) → 10.8 (70), then a plateau
(the games that have paid pull the mean down); iron 4.0 → 8.0 by turn 50 and flat to turn 70; plums
1.5 → 4.6 (50) → **5.0 flat from turn 65 to 130**; apples **≈3.0 flat from turn 50 to 125**. The plum and
apple stocks sit at their bills (6 and 3): the bot harvests each resource up to what the next train needs
and no further, and lets the rest hang on the trees (a deficit-driven resource weight — the same mechanism
Astrobytes describes: "If I don't have enough of a fruit/iron I increase the weight … based on the actual
deficit"). (e) Median turn of the purchase 97 (fits; 95 in the profile; p25–p75 78–121).

*When it fails.* 34 games never bought troll 3 (16 %; 12 % wins). In 19 of them the lemon stock never
reached 18 (max 2–14 — the lemon orchard was raided or never grew); in 15 the lemons were there (18–140!)
but plums stayed below 6 or apples below 3 for the whole game (e.g. lemons 115, 124, 140 with plums ≤ 5).
The bot keeps stockpiling lemons instead of lowering its target: **the ladder is fixed and it waits for
it** — speed 2 and carry 4 are hard floors (no `1/4/…` and no `2/3/…` troll 3 in 181 games), harvest is
pinned (1 for troll 3, 0 for troll 4, even when 2 was affordable in 10 + 25 cases), and a strictly bigger
spec was affordable and not taken in 200 of 444 TRAIN commands (`fits/MSz.md` §0); only the chop level
floats with the iron.

### Phase 3 — turns ~97–128: troll 3 chops, troll 4 is funded (CORPUS + CONTEST)

Troll 3 spends 68 % of its action turns chopping, 22 % dropping, 7 % harvesting (roles fit). Chops per
game per 10 turns: 1.45 (91–100) → 2.2 → 3.0 → 3.7 → 5.1 (131–140) (CORPUS §5). Troll 4 = `2/4/0/3` in
89 % (`2/4/0/2` 10 %): bills with three trolls **7 plums, 19 lemons, 3 apples (harvest 0 still costs n = 3),
12 iron (chop 3) or 7 (chop 2)**. It is bought in 83 of 216 games (38 %), median turn 129 (p25–p75 115–144);
binding resource plums 25, iron 21, lemons 17, apples 10 of 73 (fits). Here the bot prefers chop 3: in 18 of
the 21 iron-bound cases it waited 1–19 turns past the chop-2 bill for the 12th iron; the 8 chop-2 purchases
were earlier (median turn 115) than the 65 chop-3 ones (131). Contest series: the lemon stock falls from
10.5 (turn 100) to 7.6 (turn 140) and iron from 7.2 to 2.8 (turn 150) — the second bill being paid from
the same orchard while troll 3 already chops. No fifth troll ever (0/216; contest 0/634).

### Phase 4 — turns ~110–290: the wood phase with the fruit farm still running (CORPUS + CONTEST)

First wood in the shack at median turn 116 (p25–p75 97–136). Chops per 10 turns 5.4–6.5 from turn 140 to
290; wood per chop turn 0.83 in turns 101–200 and 0.67 in 201–300 (tables). Contest wood in the shack: 1.1
(turn 100), 6.6 (120), 22.6 (150), 52 (200), 78 (250), 98 (295); own score ≈13 points per 5 turns from
turn 145 to 220 and ≈11.5 after (≈0.52 wood + 0.37 fruit per turn over turns 150–295). The two cheap trolls
keep harvesting ≈4 times per 10 turns to the end; the harvested kind shifts to apples (turns 101–200: lemon
33 %, apple 30 %; 201–300: apple 56 %, lemon 22 %); own apple trees alive grow from 0.67 (turn 100) to 1.49
(turn 290), 56 % of them next to water, where the apple cooldown is 2 ticks instead of 9 (CORPUS §3;
tables); the contest apple stock rises from 3 (turn 125) to 31 (turn 295). Planting continues at 0.8–1.2 per
10 turns, shifting from bananas to lemon/plum/apple (turns 201–300: lemon 38 %, banana 23 %, apple 20 %,
plum 19 %). Own trees alive per game: 6.3 (turn 50), 7.1 (100), 6.5 (150), 5.4 (200), 4.9 (250), 4.5 (290).

### Phase 5 — the last ~20 turns (CORPUS)

Last PLANT at median turn 280 (p10 244, p90 287); last HARVEST 298; last DROP 300 (median; 1.1 turns
before the end on average). In the last 30 turns per game: 14.7 chops, 11.6 harvests, 14.6 drops, 1.3
plants, 9.9 wood; chops drop to 3.35 per 10 turns in 291–300 (from 5.5) as trips no longer pay back;
13 games ended before turn 300. No "everybody chops" cash-out: the harvesters harvest to the end.

---

## 3. The per-turn decision procedure (pseudo-code, each rule with its leg)

```
STATE kept between turns: ladder_index (which troll is next: 3 or 4, or done);
                          plan of the previous turn (GUESS — the family keeps it, MSz's toolkit does)

each turn:
  # --- A. TRAIN (leg: CORPUS, 444 TRAIN commands, delay 0 in 441) ---
  if turn == 1:
      TRAIN (2 if plum>=5 else 1, 2 if lemon>=5 else 1,
             2 if (apple>=5 and lemon>=5) else 1, 1)                        # exact, 196/196
  elif roster == 2 and turn <= ~195:                                         # latest troll 3 seen: 194
      target = (2, 4, 1, c);  n = 2
      if plum>=6 and lemon>=18 and apple>=3 and iron>=6:
          c = max c in {2,3,4} with iron >= 2 + c*c;  TRAIN(2,4,1,c)        # 169/169 take max c
          # exception: 11 of 54 iron-bound cases waited 1-20 turns for c=3 (GUESS: search)
  elif roster == 3 and turn <= ~185:                                         # latest troll 4 seen: 184
      if plum>=7 and lemon>=19 and apple>=3 and iron>=12:
          TRAIN(2,4,0,3)                                                     # 65 of 73; it waits for the 12th iron
      # exception: 8 of 73 bought (2,4,0,2) with 7-11 iron (median turn 115); the condition that
      # lets it settle for chop 2 is not recovered (GUESS: a search outcome)
  # roster 4: never trains again (0/216)

  # --- B. resource wants (leg: CONTEST stocks flat at the bill; Astrobytes' deficit weights) ---
  deficit[k] = max(0, bill_next[k] - shack[k])    for k in plum, lemon, apple, iron
  # GUESS: the value of harvesting/mining k is high while deficit[k] > 0 and low after;
  # fruit beyond the bill still counts 1 point, so late-game harvesting continues (78 fruit pts/game)

  # --- C. orchard wants (leg: tables, own trees alive by kind) ---
  want_trees = {banana 3, lemon 2, plum 1, apple 1} within 2 cells of the shack until ~turn 150,
               then {lemon 2, apple 1.5, plum 1, banana 1}          # GUESS as a rule: these are the measured
               # means of own trees alive by kind (Phase 1 and 4), not a fitted target
  plant only if turn <= ~285 (last plant median 280, p90 287)

  # --- D. per troll, candidate jobs (leg: FAMILY — every write-up of this family has this list) ---
  for each own troll:
      jobs = HARVEST(tree with fruit), CHOP(tree), PLANT(kind, cell), PICK(kind), MINE(iron cell), DROP
      role bias by talents (leg: roles fit, action turns):
        harvest>=1 & chop==1 (trolls 1-2): HARVEST 36-46 %, DROP 27-38 %, CHOP 10-17 %, PLANT 7-12 %, MINE 1-3 %
        2/4/1/c (troll 3):                 CHOP 67-68 %, DROP 22-25 %, HARVEST 5-7 %, MINE 1-2 %
        2/4/0/3 (troll 4):                 CHOP 77 %, DROP 23 %, nothing else
      HARVEST target (leg: harvest fit, 12,433 trips):
        prefer own trees within 2 cells of the shack (8,367 of 12,433 at distance 2, 1,115 at 1);
        "nearest tree with fruit" explains 60 % (44.5 % after random tie-break),
        "min(fruits, free carry) / (travel + harvest turns + return + 1)" 61.8 % (42.1 %);
        kind follows the deficit (lemon 60 % of harvest trips in turns 1-50, apple 56 % in 201-300);
        will walk to a tree with 0 fruit that is about to ripen (1,192 of 12,433)
      CHOP target (leg: chop fit, 6,918 trips with movement):
        size 4 in 71 %, own-planted 61 %, initial 20 %, opponent-planted 20 %, own half 75 %;
        the chosen tree is the 1st or 2nd nearest in 54 %;
        best single formulas (in brackets: the honest figure, after the rule's ties are broken at random):
        size/(travel+1) 36 % (20 %), wood/(travel+chops) 33 % (25 %),
        our champion's wood/(travel+chops+return+1) 30 % (24 %)  -> no formula explains it; a plan search does
      PLANT cell (leg: plant fit, 6,069 plants):
        empty grass cell minimising (distance to shack + distance to the troll): 77.6 % (2,119 ties);
        never farther than 6 from the shack; 1-2 cells in 91 %; on own half 91 % (100 % nearer its own shack);
        apples go to water-adjacent cells in 46 % (284 of 628), other kinds 10-21 %
      PLANT kind: the shack seed when the shack has it (PICK->PLANT), else the fruit just harvested
        (HARVEST->PLANT, one cycle); early banana-heavy, late lemon/apple (Phase 4 shares)
      MINE: only chop-1 trolls in the funding phases, 1 iron per trip, stop when deficit[iron] == 0
      DROP: when full or passing the shack; 73 % of drops are fruit only, 22 % wood only, 5 % iron only

  # --- E. joint choice (leg: TOOLKIT — GUESS) ---
  simulate the joint action set of all trolls a few turns ahead with an exact engine,
  hill-climb / small beam over the sets (MSz: "action sets for a turn are computed in independent beam
  searches with a very small width (2 or 3)"), evaluate with hand weights: shack points, deficits toward
  the next bill, orchard near the shack, trip time; resolve own-troll cell conflicts (the referee lets
  two own trolls never share a cell); emit step-wise MOVEs (targets 1-3 cells away, 100 % of 86,249 MOVEs)
```

**The own-tree lifecycle and the early hits (CORPUS, tables; `fits/MSz.md` §5).** Own trees are grown to
full size before they are cut: of 7,656 chop runs on own trees, 4,917 were at size 4 (lemon 1,842, banana
1,489, plum 857, apple 729); median age at the cut 26 turns for bananas, 29 for lemons and plums, 37 for
apples; only 792 cuts within 4 turns of planting — no plant-and-cut conversion. But the chopping starts
early: the first chop of an own tree is at median turn 18, and turns 1–100 hold 1,624 chop trips (2,353
chop turns) that produced only 236 wood, 0.10 per chop turn — single hits by chop-1 trolls on own trees
next to the shack (the most common early case: one hit on an own size-1 banana of health 3, n = 82; then
one hit on an own size-4 lemon of health 12, n = 38), with no opponent on the tree in 1,503 of 1,624.
Where they come from: 4,055 of all chops happen without moving, and 2,534 of those come right after a
DROP on the same cell — the troll unloads at the shack and hits the tree standing on its cell with the
turn it has left. GUESS on the purpose: a chopped tree keeps its damage when it grows ("a damaged tree
gains the health difference between sizes"), so these spare hits make the later felling cheaper; or they
are a plan-search artefact. A program that copies the numbers should test these hits before copying them.

---

## 4. Numbers and parameters

| parameter | value | n / source |
|---|---|---|
| troll 2 turn | 1 (196 of 203 full-length games in the tables; profile: median 1, mean 1.56, its "214/215" is a 25-turn bin) | tables; CORPUS §1 |
| troll 2 talents | speed 2 iff plums ≥ 5; carry 2 iff lemons ≥ 5; harvest 2 iff apples ≥ 5 and carry 2; chop 1 | 196/196 (tables) |
| troll 3 talents | 2/4/1/c, c = max affordable chop ≥ 2 | 181 games; 169/169 max-c (tables) |
| troll 3 bill (roster 2) | 6 plums, 18 lemons, 3 apples, 6/11/18 iron for c = 2/3/4 | rules (`docs/mechanics.md`) |
| troll 3 turn | median 95–97, p25–p75 78–121, min 42, max 194 | n = 181 (CORPUS §1) |
| troll 3 trigger delay | 0 turns after affordability | 441/444 TRAIN commands (tables) |
| binding resource, troll 3 | lemons 61, iron 54, plums 38, apples 16 | n = 169 (tables) |
| troll 4 talents | 2/4/0/3 (89 %), 2/4/0/2 (10 %) | n = 83 (CORPUS §1) |
| troll 4 bill (roster 3) | 7 plums, 19 lemons, 3 apples, 12 (c=3) / 7 (c=2) iron | rules |
| troll 4 turn | median 128–129, p25–p75 115–144 | n = 83 |
| trolls at the end | 2: 16 %, 3: 45 %, 4: 38 %, never 5 | n = 216 |
| plants per game | 29.5; 3.9 in turns 1–10, 2.4 in 11–20, then 0.5–1.2 per 10 turns | n = 216 (CORPUS §3) |
| plant kinds | banana 39 %, lemon 33 %, plum 17 %, apple 11 % (early 51/27/17/6; late 23/38/19/21) | 6,370 plants |
| plant distance from shack | median 2, 1–2 cells in 91 %, max 6 | 6,370 plants |
| plant cell rule | min(d_shack + d_troll) 77.6 % | 6,069 (fit) |
| water-adjacent plants | 19.5 % overall; apples 46 %, plum/lemon 21 %, banana 10 % | 6,370 |
| own trees alive | 3.7 (t10), 6.2 (t25), 6.3 (t50), 7.1 (t100), 6.5 (t150), 5.4 (t200), 4.9 (t250), 4.5 (t290), 3.5 (t300) | 196–203 games per point (tables) |
| harvests per game | 112 commands, 129 fruits; ≈4 per 10 turns from turn 40 to 300 | n = 216 |
| harvest origin | own 75 %, wild 22 %, opponent 3 % | 24,268 |
| fruit harvested | lemon 37 %, apple 32 %, plum 17 %, banana 14 % | 27,814 fruits |
| first MINE | median turn 20; 8.3 MINEs and 10.7 iron per game; none after turn 180 | n = 197 games with a MINE |
| first wood | median turn 116 | n = 215 |
| chops per game | 118 commands; 5.4–6.5 per 10 turns in turns 131–290 | n = 216 |
| chop targets | size 4 in 71 %; own 61 %, initial 20 %, opponent 20 %; own half 75 %; 1st–2nd nearest 54 % | 6,918 trips with movement (fit) |
| wood per chop turn | 0.10 (turns 1–100), 0.83 (101–200), 0.67 (201–300) | tables |
| wood per game | 80 (ladder): 51.4 own trees + 16.7 initial + 12.8 opponent's; 98 at turn 295 (contest) | n = 216 / 634 |
| own trees: size and age at the cut | size 4 in 4,917 of 7,656 own-tree chop runs; median age 26 (banana), 29 (lemon, plum), 37 (apple) turns | `fits/MSz.md` §5 |
| harvest runs / drops | 22,080 harvest runs, 95 % single-turn; 24,521 drops, 61 % one item | `fits/MSz.md` §5 |
| last PLANT / HARVEST / DROP | median turn 280 / 298 / 300 | n = 203 / 203 / 216 |
| score composition | 320 wood points + 78 fruit points = 399 (ladder); 480 (contest) | n = 216 / 634 |
| MOVE style | step-wise, target 1–3 cells away (mean 1.36) | 86,249 MOVEs |
| timeouts | 8 strikes in 216 games (ladder); 0 in 634 (contest) | CORPUS §9 / CONTEST |

---

## 5. What a program built from this would still miss

1. **The search.** The numbers above are outputs; the joint per-turn choice that produces them is not
   visible. No single formula explains more than a third of the chop choices or 60 % of the harvest
   choices — what one expects from a plan search over several turns, not from a greedy rule. GUESS from
   MSz's toolkit: an exact engine plus nested beam search / hill climbing over action sets with a
   hand-weighted evaluation. A greedy re-implementation will get the phases and the ladder right and lose
   tempo in the trip choices.
2. **The evaluation weights**: the worth of a tree near the shack, how the deficit toward the next bill
   scales resource values, the fruit-trip vs chop-trip trade-off. Only the outcomes are known (stocks held
   flat at the bill; fruit farming continued to the end).
3. **The 11 + 18 "wait for chop 3" cases** — a search outcome or an explicit rule.
4. **Opponent handling.** Nothing measured shows a reaction to raids: no lemon-deny, no co-chop rule beyond
   what the search sees (an opponent troll stood on the tree in 15 % of mid-game and 22 % of late chop
   trips), no re-targeting when the lemon orchard is destroyed — the 34 two-troll games are the price. A
   program should add the family's guards (aangairbender: no planting with an opponent troll nearby; wala:
   stop planting when plants get destroyed; laconic_pixel: abandon a hopeless train).
5. **Denial.** None (§1). 6. **Map reading before turn 1.** Not visible; the turn-1 rule uses only the
   stock; MSz's Winter-2024 post-mortem admits he "did not use map analysis". 7. **The early spare hits**
   (§3) — copy only after testing.

---

## 6. Sources and confidence

- `profiles/MSz.md` (+ `.json`, `COMPARISON.md`) — 216 ladder games, exact. **HIGH** for every count quoted.
- `fits/MSz.md` (W4's first pass) and `fits/tables/MSz_{trips,turns}.jsonl.gz` (203 games, exact); the
  extra numbers from `w5msz/custom.py`. **HIGH** for the turn-1 rule and the train trigger (deterministic
  in the data); **MEDIUM** for the harvest/chop/plant accuracies (the best of a fixed candidate list).
- `sources/MSz-eulerschezahl.github.io-stats-2026-05-25.md` + the JSON series — 634 contest games, means
  at 5-turn steps only, contest version. **MEDIUM.**
- `sources/SUMMARY.md` §4–6 and the family write-ups (wala, laconic_pixel, xSkyline, aangairbender,
  FinkPloyd, eulerscheZahl, Astrobytes) — first-hand, about OTHER bots. **LOW** as evidence about MSz.
- `sources/MSz-github.com-marekesz-earlier-postmortems-2024.md` — first-hand, other games. **GUESS only.**
- `prior-art.md` §1.4 and §2 — the censuses (turn-1 training, the "farm-first staged scale" family, D167's
  field-fruit seed) and the closures that matter for anyone copying this bot: the top five reach worker 3
  in 75.6 % of games (median turn 106) and worker 4 in 41.6 % (median 137); a purchase ladder without its
  funding mechanism is inert (Norxondor's ladder with a chop-first continuation: −170 margin) while a
  temporary two-worker funding coalition made worker 3 affordable (+105.68). MSz's funding mechanism is
  Phase 2 above: two cheap harvesters, a 6-tree orchard at 1–2 cells, deficit-capped stocks, iron mined
  one at a time by chop-1 trolls.
- `docs/mechanics.md`, `sources/contest-rules-statement-…` — bills, cooldowns, health. **HIGH.**

Guesses in this document, all marked: the search and evaluation (TOOLKIT), the deficit-weight mechanism
behind the flat stocks, the reason for the early idle hits, the "wait for chop 3" cases, the orchard
composition as a target rather than an outcome, the plan kept between turns.
