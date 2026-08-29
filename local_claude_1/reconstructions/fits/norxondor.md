# norxondor_gorgonax (agent 6480540) -- decision-rule fits from 184 full-length replays

Data: every corpus game of norxondor_gorgonax that ran 300 turns (184 of 218), reconstructed
exactly (see `README.md`); 48,104 unit trips, 55,200 player-turns.

## 0. What the bot is, in one paragraph

Also a **wood economy** (90 % of the final score: mean 307 wood points + 34 fruit points), but
with a different engine: a **plant-and-cut banana conversion** and a **clear-cut endgame**.
Per game its trolls bring home 42 wood from trees it planted itself, 23 from trees the
opponent planted (twice delineate's) and 14 from initial trees. Its own bananas are chopped at
**median age 1 turn, at size 1** (1,116 chop runs on own bananas at size 1; 2,407 of the 5,161
own-tree chop runs happen 0-4 turns after planting): a banana fruit (1 point) is picked from
the shack, planted on the adjacent cell, cut the next turn for 1 wood (4 points) and dropped.
Lemons and plums it plants are left to grow (median age at chop 18 and 11 turns; 839 lemon and
688 plum chops at size 4). It trains earlier and more than delineate: TRAIN on turn 1 in 76 of
184 games, troll 2 at median turn 14 ((2,2,2,2) 74, (2,2,1,2) 37, (2,2,2,1) 27), troll 3 at
median 106 ((2,3,1,2) in 91 of 152; the rest are small variations: (3,3,1,2) 14, (2,3,2,2) 14,
(4,3,1,2) 10), troll 4 at median 138 ((2,3,0,3) 39 of 87 -- harvest power 0, a pure chopper;
chop 3 in all 87), troll 5 at 165 ((2,4,0,3) 9 of 17); games end with 3 trolls in 65 games, 4 in
70, 2 in 30, 5 in 16. From turn ~150 it stops growing the orchard and cuts everything: trees
alive on the map fall from 24.8 (turn 150) to 7.7 (turn 300), own-planted trees from 7.7 to 1.6;
harvesting collapses after turn 175 (872 harvest runs in 175-199, 267 in 275-299) while chopping
peaks at 1,563 runs in 175-199.

## 1. Chop target (5,596 chop trips with movement; 3,254 chops without moving)

Descriptive: chosen tree size 4 in 56 %, size 1 in 19 %, size 2 in 17 %; 50 % carry fruit;
kinds P 2,256 / L 1,828 / B 812 / A 700; planted by the opponent 2,547 (46 %), own 1,973,
initial 1,076; on the opponent's half 52 %; nearest living tree in only 25 % of trips; travel
distance >= 5 cells in 42 % (norxondor's choppers roam: 290 trips of 15+ cells).
Rules (in-argmax-set accuracy; expected with random tie-break in brackets):

| rule (candidates = every living tree) | all 5,596 | turns 101-200 (2,087) | 201-300 (3,294) |
|---|---|---|---|
| wood / (travel + chop turns + 1) | **40.7 % (29.4)** | 43.6 % | 38.6 % (29.9) |
| our champion's value wood/(travel+chops+return+1) | 38.8 % (30.1) | 42.5 % | 36.2 % (30.0) |
| wood/(travel+chops), no other own troll on the tree | 42.4 % | | |
| min (travel + chop turns) | 29.6 % | 29.9 % | 30.0 % |
| nearest fruitless tree | 28.5 % | 24.9 % | 31.2 % |
| size / (travel + 1) | 30.4 % (16.9) | 37.4 % | 27.2 % |
| closest to the opponent's shack | 25.4 % | 17.3 % | 29.8 % |
| nearest tree (BFS) | 24.7 % (18.8) | 24.2 % | 25.2 % |
| nearest opponent-planted tree, else nearest | 21.7 % | 16.2 % | 24.8 % |
| biggest tree, ties nearest | 21.7 % | 24.1 % | 21.0 % |
| closest to own shack / fewest chop turns | 21.8 % / 16.9 % | | |

Only 215 chop trips with movement happen before turn 100 (the early game is planting and
harvesting; in-place plant-and-cut bananas do not count as trips with movement).
Verdict: a **wood-per-turn value** (wood = min(size, free carry), time = travel + chop turns,
with or without the return) is the best description at ~30 % expected accuracy -- better than
for delineate and better than every positional/denial rule, but far from exact; the roaming
long trips (42 % >= 5 cells) show the bot values big far trees more than the formula does, and
the in-place chops are a separate mechanism (see planting). Counter-examples of the nearest
rule abound: 75 % of targets are not the nearest tree. For comparison, the repo's earlier
norxondor CHOP-target ranker reached 41.83 % exact against a 23.27 % baseline
(`prior-art.md` §3); on this table the plain wood-per-turn formula is at the same level
(40.7 % in-argmax, 29.4 % once ties are broken at random), so neither has found the real
ordering.

## 2. Planting (5,656 PLANT actions)

Cell: 3,269 (58 %) on a shack-adjacent cell, 1,169 at distance 2, 777 at 3, 441 at 4, none
farther than 4 and none on the opponent's half; 2,434 without moving. Candidate cells = every
empty walkable cell: **min d(shack) + d(troll) 86.7 %** (1,782 ties); 2 x d(shack) + d(troll)
70.3 %; nearest to the troll 69.3 %; nearest to the shack = shack-adjacent first 67.6 %
(2,674 ties); with an adjacent tree 47.2 %; water-adjacent first 17.7 % (rejected -- 22 % of
plants are water-adjacent, about the base rate). So: seeds go on the free cell next to the
shack, else the nearest free cell on the way; a ring at distance <= 4.
Kind: turns 0-49 LEMON 544 / PLUM 444 / BANANA 26 / APPLE 36; 50-99 LEMON 336 / PLUM 285 /
BANANA 127; 100-149 BANANA 323 / LEMON 316 / PLUM 229; 150-199 BANANA 578 / LEMON 287 / PLUM
273; 200-249 BANANA 320 / PLUM 271 / LEMON 226; 250-299 PLUM 309 / LEMON 266 / APPLE 152 /
BANANA 128. Kind rules: "kind with fewest own living trees among PLUM/LEMON/BANANA" 32.4 %,
"largest shack stock" 32.3 %, "fewest own living trees, all four" 28.5 %, "BANANA always" 27 %.
Not recovered; what holds: lemons and plums first (they pay for trolls 2-3: (2,3,1,2) costs
2 + 9 = 11 lemons at roster 2), bananas from turn 100 as the conversion crop, apples only late
(when the fourth troll (2,3,0,3) no longer needs apples at all -- apple cost n + hp^2 = n + 0).

## 3. Training (444 TRAIN commands, 5 failed)

Trigger: **the moment the spec becomes affordable** -- delay 0 turns in 439 of 444, 1 turn in
5. Turn-1 TRAIN in 76 of 184 games (when the drawn start inventory affords (2,2,2,2): 5 plum,
5 lemon, 5 apple, 5 iron). Spec: maximal in ms+cc+chop among affordable specs in 93 % of cases
(a strictly bigger spec was affordable in 60 of 444). Harvest power: >= 2 in 127 of 187 second
trolls, 21 of 152 third, 9 of 87 fourth; chop 3 in 0 of the first two trained trolls and 87 of
87 fourth trolls; cc 4 only in the fifth troll (17 of 17). Movement speed is 2 in almost every
trained troll (ms >= 3 in 16 + 31 + 16 + 4 cases). Wood stock at training: median 0 for trolls
2-4 (the wood is never spent -- it is the score), 10 for the fifth.
Ladder (most common full sequences): (2,2,2,2),(2,3,1,2) 16 games; (2,2,2,2) alone 12;
(2,2,2,2),(2,3,1,2),(2,3,0,3) 10; (2,2,1,2) 10; (2,2,1,2),(2,3,1,2) 7.

## 4. Harvest target (7,528 harvest trips with movement)

Chosen tree: 64 % own-planted, 34 % initial, 2 % opponent's; lemons 3,446, plums 2,466, apples
906, bananas 710 (bananas are for cutting, not eating); 51 % had 3 fruits.
Rules: **min(fruits, free carry) / (travel + harvest turns + return + 1) 59.2 %** (2,462 ties);
nearest own-planted tree with fruit 53.6 %; nearest tree with fruit 52.1 %; ... no other own
troll on it 51.1 %; max fruits/(travel+1) 48.1 %; closest-to-shack 34.9 %. Harvest runs of
2-3 turns are common (1,614 of 12,676: the carry-2/3 trolls stay for a full load).

## 5. Endgame -- the clear-cut

Per game: last HARVEST at median turn 222 (10th percentile 150, 90th 298); last PLANT median
279; first chop of an own-planted tree median 137 (10th pct 93). By 25-turn bucket, HARVEST runs
1,908 (100-124) -> 1,489 (150-174) -> 872 (175-199) -> 493 (200-224) -> 282 (250-274); CHOP
runs 293 (100-124) -> 1,108 (150-174) -> 1,563 (175-199) -> ~1,300-1,500 to the end; own-tree
chops peak at 1,048 in 175-199. Own-planted trees alive: 6.6 at turn 100, 7.7 at 150, 4.8 at
200, 2.3 at 250, 1.6 at 300; all trees on the map 24.8 -> 7.7. The switch is gradual and tied
to the fourth troll (a (2,3,0,3) that cannot harvest) arriving at median turn 138, not to a
fixed turn; a turn-250 rule like our champion's does not describe it.

## 6. Unit roles

Troll 1 (1,1,1,1): CHOP 34 %, DROP 26 %, HARVEST 25 %, PLANT 10 %, PICK 5 % (a mixed worker,
not a pure farmer). (2,3,1,2) (97 units): CHOP 56 %, HARVEST 18 %, DROP 17 %. (2,2,2,2)
(78 units): CHOP 48 %, DROP 23 %, HARVEST 16 %. (2,3,0,3) (40 units): CHOP 75 %, DROP 19 %,
no harvesting. (2,4,0,3) (16): CHOP 81 %.

## 7. Gaps

* the chop-target ordering beyond "wood per turn" (~30 % expected), in particular why the bot
  makes long trips to far trees;
* the plant-kind rule (best 32 %);
* the exact condition for the harvest-to-chop transition (co-occurs with the fourth troll).
