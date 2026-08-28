# delineate (agent 6479768) -- decision-rule fits from 215 full-length replays

Data: every corpus game of delineate that ran 300 turns (215 of 223), reconstructed exactly
(see `README.md`); 60,968 unit trips, 64,500 player-turns. Numbers are counts over those games
unless said otherwise. "Trip" = a troll's run of moves ending in its next action.

## 0. What the bot is, in one paragraph

A **wood economy with a shack-hugging orchard**. Of the final score, 93 % is wood
(mean 390 wood points + 28 fruit points per game). Per game its trolls carry home 75 wood from
trees **it planted itself**, 12.5 from trees the opponent planted and 11 from the map's initial
trees. The first troll (1,1,1,1) is a farmer: it lives on the cells next to the shack
(34 % of its actions are HARVEST, 29 % DROP, 16 % PLANT, 15 % CHOP), plants lemon/plum trees on
the cells adjacent to the shack (water-adjacent when possible), and feeds fruit into the shack
one at a time (HARVEST, DROP, HARVEST, DROP -- 14,744 of 15,816 harvest runs are a single turn,
57 % of drops carry exactly one item). The fruit pays for choppers: troll 2 at median turn 7
(usually (2,2,2,2) / (2,2,1,2) / (2,3,1,2)), troll 3 at median turn 111 (a big carrier-chopper,
cc 4 and chop 3 in most cases), troll 4 at median 146, troll 5 at 166. The choppers spend
68-77 % of their action turns chopping and ~20 % dropping. From mid-game on the orchard is a
**banana wood farm**: bananas are planted on shack-adjacent cells (4,176 of 8,636 plants are
bananas, 3,657 of them after turn 100), grown and chopped at size 4 (1,861 chop runs on own
bananas at size 4; median age at chop 17 turns), and the wood is dropped next door. Chopping
of own-planted trees rises from 37 runs in turns 0-24 to 1,367 in turns 275-299.

## 1. Chop target (7,651 chop trips with movement; 3,155 more chops without moving)

Descriptive facts (chosen tree, trips with movement): 66 % are size 4; 47 % carry fruit at the
moment of choice (2,260 carry 3 fruits -- the bot chops fruit-bearing trees); kinds B 2,789 /
L 2,394 / P 2,075 / A 393; planted by delineate 4,424, by the opponent 2,186, initial 1,041;
the chosen tree is the nearest living tree in only 28 % of trips (rank 2: 24 %, rank 3: 13 %);
BFS distance travelled: 1-2 cells 62 %, 3-4 20 %, >= 5 18 %.
**Phase structure** (share of chosen trees on the opponent's half / within 2 cells of the
opponent's shack): turns 0-49 84 % / 56 %, 50-99 74 % / 50 %, 100-149 46 % / 33 %, 150-199
29 % / 21 %, 200-249 22 % / 15 %, 250-299 14 % / 9 %. Early choppers camp at the opponent's
shack and cut the young trees the opponent plants there (e.g. game 891153730: troll 3 kills the
opponent's size-1/2 lemons at (10,3), (8,2), (9,3) -- all within 2 of the enemy shack (9,2) --
again and again as they are replanted). Late choppers cut the home orchard.

Rules scored (in-argmax-set accuracy; expected accuracy with random tie-break in brackets):

| rule (candidates = every living tree) | all 7,651 | turns 1-100 (1,426) | 201-300 (3,761) |
|---|---|---|---|
| size / (travel turns + 1) | 48.0 % (24.7) | 33.5 % (20.9) | **53.7 % (28.1)** |
| wood / (travel + chop turns + 1), wood = min(size, free carry) | 45.8 % (22.0) | **62.6 % (13.2)** | 39.7 % (24.8) |
| our champion's value: wood x 1000 / (travel + chops + return + 1) | 41.8 % (20.5) | 60.4 % (11.6) | 36.3 % (24.0) |
| same, opponent-half trees weighted x2 | 39.4 % | 66.2 % | 29.8 % |
| nearest tree (BFS) | 27.9 % (19.4) | 41.6 % (30.4) | 25.8 % (18.0) |
| biggest tree, ties nearest | 31.8 % | 24.4 % | 35.1 % |
| nearest opponent-planted tree, else nearest | 20.8 % | 44.0 % | 13.0 % |
| closest to the opponent's shack | 18.7 % | 39.6 % | 10.8 % |
| min (travel + chop turns) | 27.6 % | 41.8 % | 22.5 % |
| fewest chop turns / closest to own shack / fruitless-first | 13.6 / 12.8 / 20.3 % | | |

Restricting candidates to trees with no other own troll on them lifts the champion value to
47.7 % (wood/(travel+chops) 49.7 %). Excluding own-planted trees from the candidates makes every
rule worse (<= 23 %) -- **delineate does chop its own trees, deliberately**.

Verdict: **no single-formula rule reproduces the chop choice**; the best expected accuracy is
~28 % (late game, "biggest tree per travel turn") and the early-game value rules only reach
13 % once their massive ties are broken at random (free carry 2 caps `wood` at 2 for every
tree of size >= 2). What the data supports: (i) early game = denial at the enemy shack (the
target is one of the opponent's young trees near their shack, chosen among several -- the exact
ordering is not recovered); (ii) from turn ~150 = harvest of the home orchard, preferring big
(size-4) trees near the current position, own bananas at size 4 first; (iii) fruit on the tree
is no deterrent (47 % of targets carry fruit) -- often the troll harvests first and chops in
place (3,155 chops without moving: 1,355 right after planting on that cell, 1,300 right after a
DROP on that cell, i.e. the shack-adjacent farm cell).
Counter-examples to the nearest-tree rule (game 891153730): at turn 7 troll 3 (2,2,1,3) walks
4 cells to a size-1 lemon 2 cells from the enemy shack instead of the size-2 banana 3 cells away
or its own size-1 lemon 1 cell away; at turn 13 it walks 3 cells to another enemy size-1 lemon
instead of the size-3 banana next to it.

## 2. Planting (8,636 PLANT actions)

Cell: 3,677 plants (43 %) on a cell adjacent to the shack, 2,420 at BFS distance 2, 1,534 at
3, 619 at 4; 99.6 % on the own half; 23 % water-adjacent; 2,287 without moving, 3,730 after one
step. Candidate cells = every empty walkable cell:

| rule | accuracy (ties) |
|---|---|
| **cell minimising d(shack) + d(troll)** -- i.e. on a shortest path between the troll and the shack, nearest available | **89.9 %** (3,782 ties) |
| empty cell nearest to the troll | 78.7 % (2,846 ties); ties -> nearer the shack 76.7 % |
| 2 x d(shack) + d(troll) | 57.5 % |
| empty cell nearest to the shack | 50.3 % (3,099 ties) = shack-adjacent cell first |
| nearest-to-shack cell with an adjacent tree | 45.7 % |
| water-adjacent cell nearest to shack / to troll | 17.2 % / 20.4 % |
| nearest cell not adjacent to any tree | 14.7 % |

So: the planter picks up a seed at the shack and drops it on the first empty cell it stands on
while heading out, or on the free shack-adjacent cell -- a compact orchard around the shack;
water adjacency is **not** sought (rejected), rings and "next to other trees" are not sought.
Kind: early game LEMON 440 / PLUM 246 / BANANA 164 / APPLE 53 (turns 0-49); from turn 50 on
bananas dominate (BANANA 3,657 vs LEMON 1,750, PLUM 1,285, APPLE 282 after turn 100). Kind rules:
"the fruit with the largest shack stock" 44.6 %, "BANANA always" 48.4 %, "BANANA after turn 100,
else the scarcer of PLUM/LEMON" 50.0 %, "the kind with fewest own living trees" 19 %. Not
recovered exactly; what holds is: lemons/plums first (they buy the second troll), bananas as
the wood crop later, apples rare (385).

## 3. Training (412 TRAIN commands, all succeeded)

Trigger: the spec that was trained was affordable for the first time (at the same roster size)
0 turns earlier in 251 cases, 1 turn earlier in 110, 2-5 turns in 34, 6+ in 17 -- i.e.
**train as soon as the target spec is affordable** (88 % within one turn). Turn-1 TRAIN in only
13 games; the second troll comes at median turn 7 (min 1, max 237) after the first troll has
mined iron (M-D-M opening in games where iron was short: 1,294 MINE actions, 166 games with
mining, mostly before turn 150) and planted a seed or two.
Spec: among all affordable specs the chosen one maximises ms+cc+chop (94 %), cc x chop (97 %),
i.e. it is (near-)maximal in the three useful talents while harvest power is kept at 1 except
for the second troll (hp >= 2 in 109 of 215 second trolls, in 16 of 121 third, 11 of 60 fourth).
In 83 of 412 cases a strictly bigger spec was affordable -- the bot keeps stock for seeds.
Ladder: troll 2 = (2,2,2,2) 43, (2,2,1,2) 23, (2,3,1,2) 17, (1,2,2,2) 11, (2,2,2,1) 11, (3,2,2,2) 9;
troll 3 = (2,4,1,3) 14, (3,4,1,2) 12, (1,4,1,3) 10, (3,4,1,3) 10, (2,4,1,2) 10 (cc >= 4 in
85 of 121, chop >= 3 in 74 of 121, ms >= 3 in 54 of 121), median turn 111; troll 4 = (3,4,1,3)
25, (2,4,1,3) 15 (cc 4 in 54 of 60, chop 3 in 58 of 60), median turn 146; troll 5 = (2,4,1,3) 7,
(3,4,1,3) 5, median 166. Games end with 2 trolls in 94 games, 3 in 61, 4 in 44, 5 in 16. Wood stock at training is irrelevant (median 0-15): the bottleneck is fruit
(a cc-4 troll costs 2 + 16 = 18 lemons at roster 2, chop 3 costs 11 iron), which is why the
farmer harvests lemons all game (3,543 of 9,741 harvest trips are lemons).

## 4. Harvest target (9,741 harvest trips with movement)

Chosen tree: 66 % own-planted, 32 % initial, 1 % opponent's; at BFS distance 1-2 from the shack
in 58 % of trips (5,694 of 9,741); 51 % had 3 fruits, 21 % two, 22 % one, 6 % none yet.
Rules: **nearest tree with fruit that no other own troll stands on: 70.5 %** (2,479 ties);
nearest tree with fruit 69.1 %; nearest own-planted tree with fruit 64.7 %; min(fruits, free) per
(travel + harvest + return + 1) 66.0 %; max fruits/(travel+1) 56.2 %; closest-to-shack tree with
fruit 36.5 %. Harvest runs are one turn long (93 %) because the farmer has carry 1 and drops
after every fruit; a harvest is nearly always followed by DROP (20,939 drops, 18,599 with a full
load).

## 5. Endgame

There is **no visible switch**: planting continues to the last turns (last PLANT per game:
median turn 296, 10th percentile 282), harvesting to median turn 292, own-planted trees are
chopped throughout (first own-tree chop median turn 96) and the chopping rate simply climbs with
the roster (all CHOP runs per 25 turns: 288 at 0-24, 493 at 100-124, 1,353 at 200-224, 1,598
at 275-299). Own-planted trees alive: 3.1 at turn 50, 7.8 at 200, 7.0 at 250, 3.5 at 300; the
orchard is drawn down over the last 50 turns but never to zero, and the bot still plants
bananas in turns 275-299 (877 plants). Trees alive on the map: 15.8 at start, 22.3 at turn 200,
14.1 at the end.

## 6. Unit roles

Troll 1 (1,1,1,1): HARVEST 34 %, DROP 29 %, PLANT 16 %, CHOP 15 %, PICK 6 %, MINE 1 % -- farmer
at the shack. (2,2,2,2) (43 units): CHOP 49 %, DROP 22 %, HARVEST 14 %, PLANT 10 %. Big
choppers (3,4,1,3) / (2,4,1,3) / (2,4,1,2) / (3,4,1,2): CHOP 68-77 %, DROP 16-21 %, HARVEST <= 6 %.

## 7. What is not recovered (gaps)

* the chop target's exact ordering (best expected accuracy 28 %); the early-game denial
  phase's exact choice among the enemy's trees; whether denial is a rule ("cut the opponent's
  young trees near their shack") or falls out of a value function that rewards small quick
  kills near the troll's position -- the descriptive data favours a deliberate rule
  (84 % opp-half targets in turns 0-49 even though most trees are on the own half);
* the plant-kind choice (best 50 %);
* the second troll's exact spec as a function of the starting inventory.
