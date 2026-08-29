# norxondor_gorgonax — the algorithm, reconstructed (W5, 2026-08-28)

**Who:** Legend #2 on the ladder (29.66) and #2 in the contest (30.36); agent id `6480540`.
**What this is:** a description of actions, sufficient to write a program, of a bot whose author
never wrote anything down (the name is a CodinGame auto-generated pseudonym; W1 found nothing
on the web — `sources/SUMMARY.md` §2). It stands on three legs, and every number says which leg:

- **[stats]** — the game author's statistics of its 616 contest games
  (`sources/norxondor_gorgonax-eulerschezahl-stats-2026-05-25.md`, series in `sources/all-legend-players-…json`).
- **[family]** — first-hand write-ups of bots of the same family (3–4 trolls with hard-coded
  train targets, an orchard by the shack, then mass wood): wala, laconic_pixel, xSkyline,
  aangairbender, FinkPloyd, eulerscheZahl, Astrobytes (`sources/<name>-….md`, `sources/SUMMARY.md` §5).
- **[corpus]** — our own 218 ladder games with every command: the behaviour profile
  (`profiles/norxondor_gorgonax.md`, 218 games, exact positions from the referee's log), the
  decision-rule fits (`fits/norxondor.md`, 184 full-length games, 48,104 unit "trips"), the
  July prior art (`prior-art.md` §1.2: Phase 10/14, 30 games), and my own runs over the fit
  tables `fits/tables/norxondor_*.jsonl.gz` and the corpus messages, marked **[W5]** (ad-hoc
  scripts, not checked in; every number is reproducible from those tables). Where the corpus
  legs and the contest statistics differ, the corpus describes the ladder version we face and
  takes precedence.

Vocabulary, once. **Talents** = a troll's four numbers in the game's order
speed / carry / harvest / chop, written `2/3/1/2`. **Roster** = how many trolls you have.
**Floor** = the smallest talents the bot accepts for its next troll; **cap** = the largest it
will pay for; a spec is the **componentwise maximum** when each talent separately is the largest
level the shack can pay under its cap. **Free carry** = carry capacity minus the load already
carried; **ceil** = rounded up. **BFS distance** = walking distance over grass. A **trip** = one troll's walk
(zero or more MOVEs) ending in one action (harvest, chop, plant, pick, drop, mine).
**Teacher-forced accuracy** = how often a rule picks the same target as the real bot did *from
the real bot's own situations*; **closed-loop** = the rule playing the game by itself.
**PCD** = plant-chop-drop: turn a fruit (1 point) into wood (4 points).
**Seat** = which of the two players you are. "GUESS" marks anything not measured.

---

## 1. What kind of program it is

**Known (measured).**

- **A fast rule-based program, not a search.** It prints a message every turn of the form
  `"XY t ms"` — two capital letters and its own running time. Over 63,945 turns of 217 corpus
  games the time is **0.13 ms mean, 0.125 ms median, 0.20 ms at the 95th percentile, 0.25 ms
  at the 99th, 5.2 ms maximum** [W5]. A bot that finishes in a quarter of a millisecond of a
  50 ms budget is not simulating or searching; it is evaluating hand-written rules.
  (`prior-art.md` §1.2 guessed "probably time-budgeted and randomized (search or rollouts)"
  from the telemetry and from the fact that it does not replay identically on a fixed map,
  diverging at turn 22; the timing contradicts a search. GUESS: the non-determinism is a random
  tie-break inside the bot or on the platform, not a rollout.)
- **A two-flag global state machine.** The two letters are *not* per-troll (always exactly
  two letters whether it has 1 or 6 trolls; 63,945 turns [W5]). Each letter is one of
  **P, D, T**. The first letter is the economy mode: **P** ("produce": harvest, plant, train)
  for the first half of the game, **D** ("deforest": chop, no more training) for the second;
  **T** is a transitional value (see §2.4). The second letter uses the same alphabet, switches
  at about the same time (median turn 158 vs 153) but usually not on the same turn (same turn
  in only 12 of 184 games) — its meaning is not decoded (§2.4). Corpus shares by turn bucket
  [W5]: turns 1–75 `PP` 97 %; 101–125 `PP` 62 %, `DD` 10 %, `DP` 10 %; 151–175 `DD` 48 %,
  `PP` 13 %; from turn 200 `DD` 99.5 %.
- **The build-up family.** Ends the game with 4 trolls in 41 % of games, 3 in 28 %, 5+ in 12 %,
  2 in 19 % [stats, n = 616]; in our corpus 3.5 trolls on average, four or more in 52 %
  [profile, n = 218]. Plants 32 trees per game [stats] / 29 [profile], the closest to home of all
  top bots (median 1 cell from the shack, never beyond 4). 90 % of its points are wood [profile].
- **Movement is step-wise**: 99.856 % of MOVE targets are the cell it stands on next turn, and
  93.4 % of walk endpoints lie on a shortest path to the next action (Phase 10, 10,406 MOVEs,
  `prior-art.md` §1.2). So: intent → target cell → one BFS step per turn.

**Inferred.** The structure below (ladder, orchard, cash-out) is the same skeleton every
first-hand write-up of this family describes — wala: "2 phases HARVEST/TRAIN then PLANT/CHOP
… Training is hardcoded for 4 trolls (with round limits). As well as the number of trees needed
close to the shack for each type"; eulerscheZahl: "TRAIN is hardcoded regarding the amount of
trolls I want to train as well as their skills (having a lower bar, but allowing for stronger
trolls if the starting resources are high enough)" — which is exactly the floor/cap rule
measured below [family].

---

## 2. The game plan by phases

Turn numbers are medians unless stated.

### 2.1 Opening (turns 1–10): the first worker and the first two seeds

- **Turn 1:** if the drawn starting shack can pay for a `2/2/1/1` troll (5 plums, 5 lemons,
  2 apples, 2 iron with one existing troll), it TRAINs immediately: 76 of 184 games trained on
  turn 1 and every one of them satisfied that test; the other 108 did not and none trained
  [W5]. (Reviewer's check on the fit tables, 184 games: 76/76 and 0/108 — exact. The `2/2/2/2`
  bill that `fits/norxondor.md` §3 names as the test was affordable in only 35 of the 76, so
  the floor is `2/2/1/1` with harvest and chop raised to what the stock affords.) The average
  score therefore *falls* from 17 at turn 0 to 16 at turn 25 [stats].
- **Turns 1–6, the start troll:** move off the shack, PICK a seed from the shack, PLANT it on
  the neighbouring cell, often PICK and PLANT again: the commonest first-ten-turn letter
  patterns are `MKPKMPMMMM` (22 games), `MKPMMMMMMM` (15), `MKPMMKPMMM` (12) [profile]. First
  plant on turn 3 (median); the first seed is a LEMON in 62 % of games, a PLUM in 34 %. First
  harvest at turn 8, of a wild tree in 98 % of games (plum 40 %, lemon 40 %, apple 17 %).
- **Second troll** (the first trained): median turn 9 in the profile (turn 14 in the 300-turn
  games), 25th–75th percentile 1–36. Talents `2/2/2/2` in 41 %, `2/2/1/2` 19 %, `2/2/2/1` 16 %,
  `2/2/1/1` 9 % [profile, n = 216] — a hybrid that can both harvest and chop.

### 2.2 Build-up (turns ~10–100): the lemon-and-plum orchard, then iron

- Almost pure fruit economy: only 7 CHOP commands per game in turns 1–100 (delineate 28); the
  first wood arrives at median turn 97 [profile].
- Planting rate ~1 tree per 10 turns; kinds in turns 0–49: LEMON 544, PLUM 444, APPLE 36,
  BANANA 26 (of 1,050 plants) [fits]. By turn 50 it has planted 2.9 lemons and 2.4 plums,
  twice delineate's early planting [stats]. Why lemons and plums: the next two trolls cost
  lemons for carry (`2/3/1/2` at roster 2 = 11 lemons, 6 plums, 3 apples, 6 iron) and the
  fourth costs iron for chop 3 (`2/3/0/3` at roster 3 = 12 iron, 12 lemons, 7 plums, 3 apples).
- Shack stocks climb steadily: plums 3.0 → 7.3, lemons 3.6 → 6.8 by turn 100 [stats].
- **Mining starts late**: first MINE at median turn 72 (25th–75th 54–95), 12 iron per game,
  in 91 % of games [profile]; every one of 1,043 mining trips (roster ≤ 4) happened while the
  shack lacked the iron for the next stage's floor (1,036 of 1,036) [W5] — iron is mined only
  when the next troll needs it (Astrobytes' rule: "I only allow mining if iron is required for
  the next train" [family]).
- **Third troll:** median turn 100 (profile) / 106 (fits); `2/3/1/2` in 64 % [profile, n = 186].

### 2.3 The wood phase (turns ~100–175): lumberjacks, the switch to D

- **Fourth troll:** median turn 132 (profile) / 138 (fits); `2/3/0/3` in 47 %, `2/3/1/3` 19 %;
  chop 3 in 100 %, harvest 0 in 63 % [profile, n = 113]. **Fifth:** median 153 / 165;
  `2/4/0/3` 58 % [profile, n = 24]. Contest averages: train-3 = 2.4/3.1/0.4/3.0,
  train-4 = 2.4/4.1/0.4/3.0 [stats].
- Chop commands per 10 turns rise from ~1 (turns 81–90) to 2.9 (111–120), 6.9 (141–150),
  12.8 (181–190) [profile]. Wood in the shack: 1.6 at turn 100, 4.8 at 125, 12.3 at 150,
  24 at 175, 38.7 at 200 [stats]. Score 32 at turn 100, 79 at 150, 185 at 200 [stats].
- Bananas appear as the mid-game crop: 42 % of turn-101–200 plants [profile]; bananas planted
  0.8 by turn 100, 2.8 by 150, 5.7 by 200 [stats].
- **The switch of the first letter to D** (persistent to the end of the game): median turn
  **153**, 25th–75th percentile 124–173, earliest 18, latest 186 [W5, n = 184]. It comes
  **one turn after the last TRAIN** in most games (median gap 1 turn; 114 of 184 within 5
  turns; 38 games more than 30 turns later). By roster at the switch: 2 trolls → turn 129,
  3 → 144, 4 → 154, 5 → 173. Map height makes no clear difference (141/144/163/151 for
  heights 8/9/10/11). Own planted trees alive at the switch: median 7; trees on the map 26.
- **No TRAIN ever happens in D mode**: of the turns on which the next floor was affordable,
  443 were in P/T mode and all trained; 193 were in `DD` mode and none trained (all after
  turn 184) [W5]. The last TRAIN of the corpus is turn 185.

### 2.4 The transitional letter T

`T` appears in either position in runs of median 15 turns (58 runs in the first letter, 81 in
the second), at rosters 2–4, around turns 75–150; the runs are *not* followed by a TRAIN (in
41 of 58 first-letter runs no TRAIN ever follows, in 15 more it is 4+ turns away) [W5]. While
the first letter is T the trolls chop their **own** mature trees near home (46 % own big,
24 % own small; only 19 % of targets nearer the opponent's shack) [W5]. GUESS: T is a short
"thin the orchard" or "cash-out check" state. Its trigger is unknown.

### 2.5 The endgame (turns ~175–300): the clear-cut

- Harvesting collapses: harvest runs per 25 turns 1,908 (turns 100–124) → 872 (175–199) →
  493 (200–224) → 267 (275–299); last HARVEST at median turn 222 [fits]. Chop runs peak at
  1,563 in 175–199 and stay at 1,200–1,500 per 25 turns to the end [fits].
- Own planted trees alive: 7.7 at turn 150, 4.8 at 200, 2.3 at 250, 1.6 at 300; all trees on
  the map 24.8 → 7.7 [fits]. 48 of 218 games end with no tree on the map; 34 of 218 end before
  turn 300 (the referee ends a game early when the last tree is felled or a player cannot lose)
  [profile]. Games last 293.85 turns on average, the shortest of the top three [stats].
- Verb mix of the last 30 turns: MOVE 59 %, CHOP 29 %, DROP 6.5 %, PLANT 2.4 %, PICK 1.9 %,
  HARVEST 1.6 % [profile]. Last DROP at median turn 297; 2 turns before the end [profile].
- Planting does *not* stop (0.8 plants per 10 turns to the end; last plant median turn 279
  [fits]): these are the plant-and-cut bananas of §3.5. Bananas in the shack fall from 7.5
  (turn 130) to 4.2 (turn 295) [stats].
- Wood 64.6 at turn 250, 83.5 at 295; score 366 vs 369 for the opponent at turn 295 of the
  contest series [stats] (the same page's record line says 370 − 356 over all games, which
  is why `sources/SUMMARY.md` prints "366 vs 356"; the contest opponents were stronger than
  our corpus's: 345 vs 272 here [profile]).

---

## 3. The per-turn decision procedure (pseudo-code)

Each rule names the leg it stands on. Accuracies are teacher-forced (see vocabulary); the
closed-loop warning of §5 applies to all of them.

### 3.1 The train ladder

```
FLOOR = {roster 1: 2/2/1/1,  roster 2: 2/3/1/2,  roster 3: 2/3/0/3,  roster 4: 2/4/0/3}
CAP   = speed 4, carry 5, harvest 2, chop 2 at rosters 1-2, chop 3 at rosters 3-4
cost(n, v) per talent = n + v²  (plums for speed, lemons for carry, apples for harvest, iron for chop)

each turn, if mode1 != 'D' and roster n <= 4:
    if every talent of FLOOR[n] is affordable from the shack (pre-turn inventory):
        for each talent independently: buy the largest value <= CAP that is affordable
        (harvest 0 and chop 0 still cost n apples / n iron)
        TRAIN speed carry harvest chop     # fires the same turn, no waiting
```

- Trigger: delay between "floor affordable" and TRAIN is **0 turns in 439 of 444 TRAINs, 1 in
  5** [fits]; with the mode condition the rule reproduces every one of the 443 trains and every
  one of the 193 non-trains on affordable turns [W5]. The July study found the same
  zero-delay floors on 30 games (8,738 decisions, 62/62) [prior art].
- Spec: **441 of 443** TRAINs are the componentwise maximum under these caps [W5]. (Counting
  note: the fit tables hold 444 TRAIN commands from the 184 full-length games; 443 of them are
  at rosters 1–4, the 444th is the single sixth troll. The profile counts 545 commands with 5
  failures over all 218 games; GUESS: the 5 "delay 1" cases below are re-issues after a
  failed attempt. Reviewer's recount on the tables: 441/443 under these caps, 411/443 under the
  July caps `3/3/2/2, 4/5/2/2, 3/3/1/3, 3/4/1/3`; the two misses bought chop 3 with 10 iron
  on turn 1. Speed 4, carry 4–5 and harvest 2 do occur at every stage when affordable — carry
  4 or 5 in 13 third trolls and 14 fourth trolls, so carry 4 is *not* reserved for the fifth
  troll as `fits/norxondor.md` §3 reads; chop is fixed by
  stage: 2 in all 152 third trolls, 3 in all 87 fourth and 17 fifth [fits].) Harvest of the
  fourth/fifth troll is 0 when apples < n+1, 1 when ≥ n+1, 2 when ≥ n+4 (55/23/9 and 13/2/2
  cases) [W5] — it is not "harvest 0 by design", it is "harvest is whatever is affordable
  after the 0-cost is paid".
- Resource collection order for the next stage: the harvested kind is a kind in deficit for
  the next floor in 6,736 of 12,676 harvest trips with or without movement (53 %), a
  non-deficit kind in 4,840 (38 %), bananas 982 (8 %) [W5] — preference, not exclusivity
  (§3.4). Iron: mined only in deficit (§2.2).
- Roster limit: the ladder stops at roster 5 (a sixth troll in 1 game of 218 [profile]);
  wala's "round limits" [family] correspond to the D mode: no TRAIN after the switch.
- **Funding warning [prior art, Phase 10]:** the purchase rule alone is inert. Transplanted onto
  a bot that keeps its trolls chopping, it produced −170 margin; worker 3 became affordable
  only when two trolls were *jointly* assigned to the next stage's deficits ("temporary two-
  worker funding coalition", +105.68). In the corpus, all trolls harvest in P mode (start troll
  HARVEST 18 %, hybrids — trolls with both harvest and chop power such as `2/2/2/2` — 16 %,
  CHOP 1 % and 7 %) [W5] — the coalition is the P mode itself.

### 3.2 The mode machine

```
mode1 = 'P' at start.
mode1 -> 'D' when the ladder is finished (one turn after the last TRAIN in 62 % of games)
         or, later, on an unknown test (median turn 165 in the other 38 %)   # GUESS: a payback
         test — "can the next troll still repay before turn 300?" (laconic_pixel: "once training
         became hopeless … immediately switch into building/scoring mode" [family])
mode1 = 'T' for ~15 turns, sometimes, at rosters 2-4 (unknown trigger; see §2.4)
mode2: same alphabet, switches at about the same time; meaning unknown.
in 'D': no TRAIN; all trolls chop (start troll CHOP 31 % of commands vs 1 % in P; hybrids 34 % vs 7 %)
        and harvesting fades (start troll HARVEST 6 % vs 18 %) [W5]
```

### 3.3 Chopping — which tree

```
candidates = every living tree (own, wild and the opponent's; "all trees equally owned",
             Astrobytes [family])
value(tree) ≈ min(size, free carry) / (travel turns + ceil(health / chop) + 1)
               + a bonus for the opponent's freshly planted trees (denial)
               + a bonus for a tree the opponent is chopping (co-chop / steal)
prefer trees no other own troll is already assigned to
go: one BFS step per turn toward the tree; CHOP until it falls (or until it is gone)
```

- The wood-per-turn value picks the observed tree in **40.7 %** of the 5,596 chop trips with
  movement (29.4 % expected once ties are broken at random); our champion's value with the
  return trip 38.8 %; "nearest tree" 24.7 %; "closest to the opponent's shack" 25.4 %;
  "biggest tree" 21.7 % [fits]. Excluding trees with another own troll on them raises the
  value rule to 42.4 % [fits] — evidence of target reservation among own trolls. The July
  ranker with 128 weights reached 41.8 % [prior art]. So the ordering is *approximately* wood
  per turn, and the rest is not recovered.
- **Denial is real and phase-dependent.** Early chops (215 trips before turn 100) are raids:
  the chosen tree is the opponent's in 59 % (opp size 1: 47, opp size 4: 46, opp size 2: 23
  of 215) and lies nearer the opponent's shack in 69 % [W5]; "closest to the opponent's shack"
  fits 35 % of them. In the endgame the single largest target class is the opponent's
  **size-1** trees (629 of 3,294 trips: killing seedlings), then wild size 4 (625), opponent
  size 4 (542), own size 4 (520), opponent size 2 (434) [W5]. Over the whole game 30 % of chop
  commands hit opponent-planted trees and 36 % are nearer the opponent's shack than its own —
  the most opponent-directed of the four bots studied [profile]. The profile also prints "63 %
  of chop commands on size-1 trees, 34 % on size 4", but that field reads the viewer's stage
  *after* the turn's tick and contradicts the exact fits for delineate (see
  `delineate/ALGORITHM.md` §5b); the exact trip data say size 4 in 56 %, size 1 in 19 %, size 2
  in 17 % of the trees walked to [fits] — the in-place banana cuts of §3.5 are the extra size-1
  chops.
- **Co-chop.** An opponent troll was standing on the chosen tree when the trip started in
  25 % of early trips (54/215), 15 % of mid (312/2,087), 19 % of late (641/3,294) [W5] — a
  bias, not a rule (wala's `STEAL_OPPONENT_CHOP` [family]). GUESS on its weight.
- Kinds felled: plum 37 %, lemon 33 %, apple 16 %, banana 14 % of chop commands [profile]; own
  lemons and plums are left to mature (median age at chop 18 and 11 turns; 839 lemon and 688
  plum chops at size 4) while own bananas are cut at age 1 (§3.5) [fits].

### 3.4 Harvesting — which tree

```
candidates = trees with fruit (64 % own-planted, 34 % wild, 2 % the opponent's)
value(tree) = min(fruits, free carry) / (travel + harvest turns + return + 1)    # 59.2 %
prefer kinds in deficit for the next train floor (53 % vs 38 %)
stay 2-3 turns for a full load (carry-2/3 trolls)
```

The throughput value fits 59.2 % of 7,528 harvest trips with movement (40.0 % expected);
"nearest own-planted tree with fruit" 53.6 %; "nearest tree with fruit" 52.1 % [fits]. Fruits
harvested per game: 90 (lemon 45 %, plum 31 %, apple 17 %, banana 7 %) [profile]. Harvesting
of wild trees dominates only early (44 % in turns 1–100, 19 % in 101–200) [profile].

### 3.5 Planting — kind, cell, how many, when to stop

```
seed: PICK from the shack (13.6 picks per game: banana 44 %, plum 28 %, lemon 24 %, apple 4 %)
      or keep a harvested fruit; a seed is in hand at the start of every planting trip (5,656/5,656)
cell: the free grass cell minimising  d(shack) + d(troll)          # 86.7 % (1,782 ties)
      => the ring next to the shack first (58 % at distance 1, 21 % at 2, 14 % at 3, 8 % at 4,
         never farther, never on the opponent's half), water-adjacency ignored (22 %, base rate)
kind: lemons and plums while trolls 2-4 are unpaid; bananas from turn ~100; apples late     # not exact
stop: never a hard cap — planting continues to turn 279 (median last plant)
```

- Cell rule [fits]: `min d(shack)+d(troll)` 86.7 %; "nearest free cell to the troll" 69.3 %;
  "shack-adjacent first" 67.6 %; "next to water first" 17.7 % (rejected). Cells with 0/1/2/3
  neighbouring trees: 34/34/23/8 % [W5]. July: all 561 plant cells inside the "bank-door
  footprint", 82 % next to an existing tree [prior art]. The family plants "close to shack/water"
  (eulerscheZahl), "near shack or near water" (aangairbender) [family]; norxondor uses only the
  shack.
- Kind by 50-turn bucket [fits]: 0–49 L 544 / P 444 / B 26 / A 36; 50–99 L 336 / P 285 / B 127;
  100–149 B 323 / L 316 / P 229; 150–199 B 578 / L 287 / P 273; 200–249 B 320 / P 271 / L 226;
  250–299 P 309 / L 266 / A 152 / B 128. No kind rule reaches 40 %: "fewest own trees of that
  kind" 32 %, "largest shack stock" 32 % [fits]; "largest deficit for the next floor" 36 %,
  "lemon deficit first, then plum, else banana" 37 % [W5]. GUESS: the kind is decided by a
  wala-style table of "trees needed close to the shack for each type" [family] whose numbers we
  cannot see; what is measured is that lemon/plum plantings keep growing with the count already
  alive (lemons planted with 0/1/2/3/4/5/6+ own lemon trees alive: 353/412/394/301/216/126/173)
  while bananas are mostly planted when none is alive (699 of 1,502) — they are cut at once.
- **The plant-and-cut banana loop (the signature) [fits]:** own bananas are chopped at median
  age 1 turn at size 1 (1,116 chop runs; 2,407 of 5,161 own-tree chop runs within 0–4 turns of
  planting): PICK a banana at the shack → PLANT it on the shack-adjacent cell → CHOP it (a
  size-1 banana has 3 health: one blow for a chop-3 troll) → DROP 1 wood. One fruit point
  becomes four wood points every ~4 turns per troll. This is why bananas are 44 % of picks but
  only 7 % of harvested fruit, why 3,254 chops happen without moving [fits], and why the
  shack's bananas drain from turn 150 [stats]. Per game the bot banks 42 wood from its own
  trees, 23 from the opponent's, 14 from wild ones [fits].

### 3.6 Drop / bank

```
when the load is full -> walk to a cell next to the shack (nearest one), DROP
```
15,309 of 16,793 drop trips start with a full load (91 %); loads were fruit 9,279, wood 6,314,
iron 895, mixed 305 [W5]; 1.8 items per drop, 90.7 drops per game [profile]. Drop endpoints:
95 % in the nearest-path tie set [prior art].

### 3.7 Mining

```
if iron in the shack < iron cost of the next floor and mode1 != 'D':
    a troll with chop >= 1 walks to a cell next to iron and MINEs (gets min(chop, free carry))
```
1,036 of 1,036 mining trips at roster ≤ 4 were in deficit [W5]; done mostly by the hybrids
(`2/2/2/2` 252 trips, `2/3/1/2` 216, the start troll 118) [W5]; 1.54 iron per MINE [profile].

### 3.8 Unit roles and coordination

Roles follow talents, as in FinkPloyd's "roles are determined mostly by stats" [family]:

| troll (talents) | units | CHOP | HARVEST | DROP | PLANT | PICK | MINE |
|---|---:|---:|---:|---:|---:|---:|---:|
| start `1/1/1/1` | 184 | 34 % | 25 % | 26 % | 10 % | 5 % | 0 % |
| `2/2/2/2` | 78 | 48 % | 16 % | 23 % | 8 % | 4 % | 2 % |
| `2/3/1/2` | 97 | 56 % | 18 % | 17 % | 5 % | 1 % | 2 % |
| `2/3/0/3` | 40 | 75 % | 0 % | 19 % | 3 % | 3 % | 1 % |
| `2/4/0/3` | 16 | 81 % | 0 % | 17 % | 1 % | 1 % | 0 % |

(action turns per unit, [fits]). The start troll is the planter and picker; the chop-3 trolls
never harvest. Assignment: GUESS — greedy per troll with reservation of chosen trees (the
"no other own troll on the tree" restriction improves the chop fit; two own trolls rarely share
a target), no Hungarian/Munkres step (an optimal one-troll-per-task assignment algorithm) is
visible. Conflicts: 0.1 MOVE_BLOCKED per game
[profile] — collisions are handled (the referee blocks a move onto an own troll's cell).

### 3.9 One turn, assembled

```
read state; n = roster; mode1, mode2 from the state machine (§3.2)
if TRAIN condition (§3.1): emit TRAIN
for each own troll (GUESS: in id order):
    if load full: goal = DROP (§3.6)
    elif mode1 == 'D' or troll.harvest == 0: goal = best CHOP target (§3.3)
    elif holding a seed: goal = PLANT at the best cell (§3.5)
    elif next to the shack, no seed in hand and a planting is wanted (§3.5): PICK the kind   # GUESS on the condition
    elif iron deficit and troll.chop >= 1 and no miner yet: goal = MINE (§3.7)
    elif a fruit deficit exists: goal = best HARVEST target (§3.4), else CHOP (§3.3)
    endgame banana loop (§3.5) interleaves with chopping from turn ~150
    act if on the goal cell, else MOVE one BFS step toward it (§1)
emit "<mode1><mode2> <elapsed> ms"
```

The branch order above is a GUESS; the measured facts it must reproduce are the verb mixes
of §3.8 and the phase curves of §2.

---

## 4. Numbers and parameters

| parameter | value | n / source |
|---|---|---|
| running time per turn | 0.13 ms mean, 0.25 ms p99, 5.2 ms max | 63,945 turns [W5] |
| train floors by roster 1/2/3/4 | `2/2/1/1`, `2/3/1/2`, `2/3/0/3`, `2/4/0/3` | 443 TRAINs [W5]; 62 [prior art] |
| train caps | speed 4, carry 5, harvest 2; chop 2 (rosters 1–2), 3 (3–4) | 441/443 [W5] |
| train delay after affordability | 0 turns (439/444), 1 turn (5) | [fits] |
| TRAIN on turn 1 | 76/184 games, exactly when `2/2/1/1` is affordable | [W5] |
| troll 2 / 3 / 4 / 5 median turn | 9 / 100 / 132 / 153 (profile); 14 / 106 / 138 / 165 (fits) | 216 / 186 / 113 / 24 games |
| contest talents train-1..4 | 2.1/2.1/1.7/1.7, 2.3/3.1/1.1/2.0, 2.4/3.1/0.4/3.0, 2.4/4.1/0.4/3.0 | 616 games [stats] |
| trolls at game end 1/2/3/4/5/6 | 1 / 19 / 28 / 41 / 11 / 1 % | [stats] |
| last TRAIN of the corpus | turn 185; none in D mode | [W5] |
| mode1 → D switch | median 153 (124–173), one turn after the last TRAIN in 62 % | 184 games [W5] |
| plants per game | 29 (lemon 35 %, plum 32 %, banana 26 %, apple 7 %) | 6,339 [profile] |
| plant cell | min d(shack)+d(troll), 86.7 %; distance 1/2/3/4 = 58/21/14/8 %, never > 4 | 5,656 [fits] |
| first plant turn / kind | 3; lemon 62 %, plum 34 % | 216 [profile] |
| own bananas: age at chop | median 1 turn, size 1 | 1,116 runs [fits] |
| own lemons / plums: age at chop | 18 / 11 turns, size 4 | 839 / 688 [fits] |
| chop target rule | wood/(travel+chops+1): 40.7 % (29.4 % expected) | 5,596 trips [fits] |
| harvest target rule | min(fruits,free)/(travel+harvest+return+1): 59.2 % (40 % expected) | 7,528 [fits] |
| chops on opponent-planted / nearer opp shack | 30 % / 36 % of chop commands | 41,247 [profile] |
| chop destinations of size 4 / 1 / 2 (trips with movement) | 56 % / 19 % / 17 % (the profile's "63 % size 1" is the doubtful viewer field, §3.3) | 5,596 [fits] |
| CHOP / HARVEST / PLANT / DROP / MINE / PICK per game | 189 / 78 / 29 / 91 / 8 / 14 | [profile] |
| first wood turn | median 97 | [profile] |
| wood in shack at 100 / 150 / 200 / 250 / 295 | 1.6 / 12.3 / 38.7 / 64.6 / 83.5 | [stats] |
| score at 100 / 150 / 200 / 250 / 295 | 32 / 79 / 185 / 290 / 366 (opp 369) | [stats] |
| drop when full | 91 % of drop trips | 16,793 [W5] |
| first MINE | median 72; only in iron deficit (1,036/1,036) | [profile], [W5] |
| last HARVEST / last PLANT / last DROP | 222 / 279 / 297 | [fits], [profile] |
| games with no tree left / ended early | 48 / 34 of 218 | [profile] |
| win rate by own roster 2 / 3 / 4 / 5+ | 27 / 71 / 73 / 83 % | 30 / 73 / 89 / 24 games [profile] |

---

## 5. What a program built from this would still miss

1. **The chop ordering.** 40 % teacher-forced is a description, not the rule; the roaming
   long trips (42 % of chop trips ≥ 5 cells [fits]) and the exact weights of denial and
   co-chop are unknown. Every positional rule tried is ≤ 35 %.
2. **The plant-kind rule** (best 37 %) and the size of the orchard it aims for.
3. **The D-switch trigger** in the 38 % of games where it is not "one turn after the last
   TRAIN", the trigger of T, and the meaning of the second letter.
4. **Coordination.** Whether trolls are assigned greedily, by permutation search (wala), by
   Munkres — an optimal one-troll-per-task assignment algorithm — (aangairbender, Astrobytes)
   or by trying all combinations of each troll's top actions (xSkyline) is invisible; only the
   outcome (roles by talents, target reservation) is measured.
5. **Opponent modelling.** The raids and seedling-killing are measured, the decision behind
   them is not; nor any reaction rule such as "stop planting if the opponent destroys our
   plants" (wala) or "no planting with an opponent troll nearby" (aangairbender) [family].
6. **The two-troll fallback.** When the ladder stalls at two trolls it wins only 27 % (30
   games) [profile]; what it does differently there is not described here.
7. **Search:** none to add — but the referee's random movement tie-breaks and the bot's own
   non-determinism (`prior-art.md` §1.2) mean an exact replay is impossible anyway.
8. **The closed-loop warning [prior art, Phase 14]:** a native controller assembled from
   fits of this very bot (intent tree 76.9 % teacher-forced, ladder, goal rankers,
   deterministic planting; `rust/src/strategies/norxondor_native.rs`) lost **−172.7 paired
   margin** against our resident and produced ~38 CHOP / 68 PICK per game instead of the
   bot's ~159 / 17. Small target errors change the inventory and the geometry, and the
   states drift away from the ones the rules were fitted on. A program written from this
   document must be validated on real maps, not on its per-decision accuracy.

---

## 6. Sources and confidence

| claim | leg | confidence |
|---|---|---|
| fast rule-based bot, two-letter state machine, P→D at ~153 | corpus [W5] | high (63,945 turns) |
| train ladder floors/caps, zero delay, no TRAIN in D | corpus [W5], [fits], [prior art] | high (443 trains; 8,738 decisions in July) |
| orchard by the shack, lemon/plum first, banana mid-game, apple late | [stats], [profile], [fits] | high |
| plant cell = nearest ring around the shack | [fits] 86.7 % | high |
| plant-and-cut banana loop | [fits] | high (1,116 runs) |
| chop = wood per turn + denial + co-chop | [fits], [W5], [family] | medium (40 %; components measured, weights GUESSed) |
| harvest = throughput value, deficit kinds preferred | [fits], [W5] | medium-high (59 %) |
| mine only in deficit; drop when full | [W5] | high |
| roles by talents, greedy assignment with reservation | [fits]; GUESS | roles high; assignment GUESS |
| meaning of T and of the second letter; D-switch test | — | GUESS |
| the branch order of §3.9 | — | GUESS |

Files: `sources/norxondor_gorgonax-eulerschezahl.github.io-stats-2026-05-25.md`,
`sources/all-legend-players-eulerschezahl-stats-2026-05-25.{md,json}`, `sources/SUMMARY.md`,
`sources/{wala,laconic_pixel,xSkyline,aangairbender,FinkPloyd,eulerscheZahl}-forum.codingame.com-….md`,
`sources/astrobytes-github.com-2026-05-27.md`, `profiles/norxondor_gorgonax.{md,json}`,
`fits/norxondor.md`, `fits/norxondor_fit_results.json`, `fits/tables/norxondor_{trips,turns}.jsonl.gz`,
`prior-art.md` §1.2 and §2, and the July records
`data/analysis/live-agent-6553250/norxondor-controller-iteration-2026-07-18.md`,
`…/norxondor-offline-distillation-and-native-controller-2026-07-18.md`,
`…/norxondor-workforce-ladder-study-2026-07-18.json`. Mechanics: `docs/mechanics.md`.
Corpus messages: `/home/tarstars/prj/troll_farm/data/processed/turns.jsonl.gz` (agent `6480540`).
