# Second-troll census — what the strong bots train, and what we train (2026-08-27)

Owner's question (2026-08-27 ~17:15Z): *"What is the next nearest idea to test? more powerful second
troll?"* This page is the read behind the answer. Facts first, the reading after.

## Data and method

- Corpus: `data/processed/turns.jsonl.gz` (main checkout only, gitignored) — 13,313,072 seat-turns of
  23,613 real Legend games (the T-2 per-turn export). Every `TRAIN` command is recorded with its four
  numbers: **speed, carry, harvest, chop** (the referee's order).
- `extract.py` (10 s over the whole corpus) keeps, per game-seat, the first `TRAIN` (= the second
  troll) and writes `train-census.json`: per bot, games, seats that trained, median and mean first-training
  turn, the harvest-capable share, the top-8 talent vectors. 47,214 game-seats; 46,320 trained.
- Round 2's games of the apple farm (`local_claude_1/apple-farm/games-41203992/`) supply the within-batch
  split (our own `TRAIN` lines and the opponents').

## The rules that make talents worth points (`docs/mechanics.md`, `sim/engine.py:apply_chop`)

- Training with `n` trolls costs **plums n+speed², lemons n+carry², apples n+harvest², iron n+chop²**.
  With one troll a `2/2/0/2` troll costs 5 plums, 5 lemons, 1 apple, 5 iron; `3/3/0/3` costs
  10/10/1/10; adding harvest power 1 costs one apple more.
- A `CHOP` takes the chopper's chop power off the tree's health (plum/lemon 4+2×size, apple 8+3×size,
  banana 2+size; size up to 4).
- **When the tree dies its wood (= size, up to 4) is dealt one piece per round to every chopper on the
  cell that still has free carrying space** — a troll's haul is capped by its free carry. A carry-1
  troll takes 1 wood (4 points) of a size-4 tree's 4; the rest vanishes. The champion's chop
  valuation knows this (`wood = final_size.min(free_capacity)`, `score = 1000·wood/turns`).

## Table 1 — the strong two-troll peers (T-1's cohort): their second troll

Talent vectors are written speed/carry/harvest/chop. "Below the floor" = weaker than `2/2/0/2` in
speed, carry or chop.

| rank | bot | trained | median turn | harvest-capable | top vectors | below `2/2/0/2` |
|---:|---|---:|---:|---:|---|---:|
| 7 | yaichi | 220 | 14 | 0 % | 2/2/0/2 ×140, 2/2/0/3 ×30, 2/3/0/2 ×18, 3/2/0/2 ×15 | 5 % |
| 8 | Stounate | 293 | 20 | 0 % | 2/2/0/2 ×206, 2/2/0/3 ×31, 3/2/0/2 ×23, 2/3/0/2 ×23 | 0 % |
| 10 | skotz | 178 | 22 | 0 % | 2/2/0/2 ×91, 2/2/0/3 ×32, 2/3/0/2 ×26, 3/2/0/2 ×19 | 0 % |
| 11 | Escdemon | 293 | 14 | 0 % | 2/3/0/2 ×59, 2/2/0/2 ×59, 1/2/0/2 ×24, 3/2/0/2 ×17 | — |
| 12 | therealbeef | 457 | 4 | 0 % | 2/2/0/2 ×82, 2/2/0/3 ×33, 2/3/0/2 ×32, 2/2/0/1 ×32 | 23 % |
| 15 | yamo (our ancestor) | 524 | 4 | 0 % | 2/2/0/2 ×91, 2/2/0/3 ×53, 2/3/0/2 ×37, 2/1/0/2 ×32 | 22 % |
| 16 | putibuzu | 182 | 14 | **100 %** | 2/2/2/2 ×69, 2/2/1/2 ×30, 2/2/3/2 ×16 (a fruit economy: 57 fruit points a game) | — |
| 17 | Risen | 390 | 18 | 0 % | 2/2/0/2 ×178, 2/2/0/3 ×133, 3/2/0/2 ×23, 2/3/0/2 ×18 | 0 % |
| 24 | Konstant | 239 | 32 | 0 % | **2/3/0/3 ×43, 2/3/0/2 ×29, 3/3/0/3 ×25, 3/3/0/2 ×20** — the one buyer of big trolls; 214 wood points a game (yaichi 245 with 2/2/0/2) | — |
| 29 | goq | 268 | 24 | 0 % | 2/2/0/2 ×90, 2/3/0/2 ×40, 2/2/0/3 ×38, 3/2/0/2 ×35 | 0 % |
| 36 | Dridriun | 553 | 3 | 0 % | 2/2/0/2 ×136, 2/2/0/1 ×85, 1/2/0/2 ×78, 1/2/0/1 ×41 | — |
| 38 | mehdi_ayari | 271 | 24 | 0 % | 2/2/0/2 ×88, 2/3/0/2 ×64, 2/2/0/3 ×49, 2/3/0/3 ×35 | — |
| 46 | DaNinja | 589 | 16 | 0 % | **2/2/0/2 ×589** (one fixed troll, always) | 0 % |
| 50 | GoodDevel | 659 | 19 | 0 % | 2/2/0/2 ×475, 2/3/0/2 ×56, 2/2/0/3 ×56, 3/2/0/2 ×49 | 0 % |
| 54 | VINCE_MX | 283 | 20 | 0 % | 2/2/0/2 ×118, 2/3/0/2 ×47, 3/2/0/2 ×35, 2/2/0/3 ×32 | — |
| 57 | 0x6E0FF | 184 | 14 | 0 % | 2/2/0/2 ×133, 3/2/0/2 ×18, 2/2/0/3 ×13, 2/3/0/2 ×13 | — |
| 58 | Kheopsian | 155 | 1 | 0 % | 2/1/0/2 ×21, 2/2/0/2 ×21, 1/2/0/2 ×21, 2/1/0/1 ×15 (trains on turn 1 with whatever the draw allows) | — |
| 63–104 | Ticasali, tonigineer, LeRenard, FRHT | 49–200 | 10–28 | 0 % | 2/2/0/2 first, then 3/2/0/2 or 2/3/0/2 | — |
| 73–97 | abdelmathin, NOIIICE, Shun_PI, anuragm | 15–24 | 1–78 | 21–100 % | small samples, mixed | — |

The rest of the ladder (32,825 first trainings by every other bot, top-8 vectors per bot): speed 2 in
90 %; carry 2 in 86 %, 3 in 7 %; **harvest 0 in 29 %, 1 in 30 %, 2 in 40 %**; chop 2 in 54 %, 1 in 31 %,
0 in 9 %, 3 in 6 %. Round 2's 158 opponents: median training turn 18, harvest-capable 105 (66 %),
vectors 2/2/0/2 ×38, 2/2/1/1 ×24, 2/2/2/1 ×19, 2/2/1/2 ×18, 2/2/2/0 ×16, 2/2/2/2 ×11.

## Table 2 — ours

- All our lineages in the corpus (`tass`, 10,269 trained seats): 2/2/0/2 ×1,748 (17 %), 2/2/0/3 ×989,
  **1/2/0/2 ×758, 3/2/0/2 ×662, 2/2/0/1 ×561**, 2/3/0/2 ×560, 1/2/0/3 ×354, 2/1/0/2 ×319, and a long
  tail (26 vectors in H8's count). Harvest-capable 1 %. Mean training turn 8.7 (T-1). **Below the floor
  in 37 % of the covered vectors.**
- The champion on the ladder today (round 2 of the apple farm, 159 trained games, median turn 10):
  2/2/0/2 ×38, 2/2/0/3 ×19, 1/2/0/2 ×12, 2/1/0/2 ×10, 1/2/0/3 ×8, 3/2/0/3 ×7, 3/3/0/2 ×7, 3/2/0/2 ×7,
  2/3/0/2 ×6, 2/2/0/1 ×5, … — **below the floor in 71 of 159 games (45 %)**.
- Why: `choose_second_troll` (readable champion, `opening_options` / `opening_key`) takes the strongest
  vector whose estimated funding time is within 15 turns, and when the draw or the map makes `2/2/0/2`
  slower than that it settles for a weaker troll now rather than the standard one later. The same
  logic sits in yamo and therealbeef (22–23 % below the floor); the leaders above them never do this.

## Table 3 — round 2 of the apple farm, within one batch (same bot, 160 real games)

| our second troll | games | wins | own score | median training turn |
|---|---:|---:|---:|---:|
| `2/2/0/2` or stronger in every talent | 88 | **58 (66 %)** | 234 | 10 |
| weaker in some talent | 71 | **24 (34 %)** | 196 | 10 |

By training turn alone: turns 1–5: 60 games, 55 % wins; 6–10: 26, 46 %; 11–20: 55, 53 %; 21+: 18, 44 %
— the turn does not separate the games; the troll does.

Caveat, stated plainly: a poor draw or far-away plums/lemons/iron produces both a weak troll *and* a
harder map for our economy, so part of the 32-point gap is the map class, not the troll. Two things
limit that confound: the draw and the map are the same for both players (point-symmetric map, one shared
inventory draw), and our opponents on those very maps train `2/2/0/2` — later.

## Reading

1. **The strong bots' second troll is not more powerful than ours — it is the same troll, `2/2/0/2`,
   bought later and never weaker.** Bigger trolls (`3/3/0/3`, 10 plums + 10 lemons + 10 iron) are bought
   by one strong bot, Konstant (#24, turn 32), who banks less wood than the `2/2/0/2` buyers above him.
   Harvest power on the second troll is the mid-ladder's habit (71 %), not the top wood bots' (0 %):
   a fruit is 1 point, a wood 4.
2. **What we do that they don't: field a weak second troll** (speed 1, carry 1 or chop 1) in roughly
   four games in ten, to save a few turns. Within one batch those games are lost twice as often.
3. The leaders train later mostly because they do something else first (T-1: bananas planted in turns
   1–50) — timing itself was priced at +1.31 ± 4 (H8, not significant), so waiting a few turns for the
   standard troll should cost little.

## The proposal — "the floor": the second troll is never weaker than `2/2/0/2`; wait for it

One variable on the champion, through the generator-and-compactor chain: in `opening_options` the grid
starts at 2 for speed, carry and chop (2..3 each); the turn-35 fallback trains the strongest *affordable
floored* troll and otherwise keeps waiting for `2/2/0/2` instead of abandoning; `fallback_second_troll`
becomes `2/2/0/2`. The funding behaviour of the starting troll (collect the bill's plums, lemons, iron)
is untouched. One hour on the ladder; the reading against the owner's stated prediction. Coordinator's
expectation: a rise of about a point — the 32-point within-batch gap is partly the map class.

Files: `extract.py`, `train-census.json` (232 KB, every bot in the corpus).
