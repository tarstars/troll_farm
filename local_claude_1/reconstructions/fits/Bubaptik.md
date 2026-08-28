# Bubaptik (latest agent 6568138) -- decision-rule fits from 182 full-length replays (first pass)

Bubaptik resubmitted 36 times (36 agent ids in the corpus, 3,917 games). This pass uses only the
most recent agent, 6568138 (191 games, 182 of them 300 turns long), reconstructed exactly
(see `README.md`); 45,515 unit trips. Written in the last minutes before the 04:15Z report.

## 0. In one paragraph

A wood economy built on **fast (speed-4) choppers**: the second troll comes at median turn 2
((2,2,2,2) 17, (2,2,1,2) 14, (2,2,2,1) 13, (1,2,2,2) 13 -- whatever the start affords, harvest
power 2 in 123 of 188), the third at median turn 116 is **(4,3,x,2/3)** ((4,3,1,2) 46, (4,3,0,2)
45, (4,3,1,3) 13, (4,3,0,3) 9: ms 3+ in 121 of 147 -- it pays 2 + 16 = 18 plums for speed 4;
never carry 4), the fourth at median 151 ((4,3,1,3) 29, (4,3,0,3) 17), a fifth at 178 in 12
games. Training fires when the spec is affordable (delay 0 in 254 of 425, 1 turn in 150; the
spec is maximal in ms+cc+chop among affordable ones in 83 %). Roles: troll 1 (1,1,1,1) HARVEST
38 % / DROP 31 % / PLANT 15 % / CHOP 10 % (farmer); the (4,3,*,*) trolls CHOP 69-77 %, DROP
19-22 %, HARVEST <= 6 %. Plants: PLUM 2,464 (the speed-4 bill), LEMON 1,564, BANANA 1,122
(mostly after turn 150), APPLE 129. Harvest fades late (1,651 runs in 100-124 -> 471 in
250-274) while chopping of own trees climbs (8 in 0-24 -> 682 in 250-274); own trees alive
peak at 7.3 (turn 200) and end at 3.9; trees on the map 24.2 (turn 100) -> 13.2 (300).

## 1. Chop target (5,019 chop trips with movement; 2,062 in place)

Chosen tree: size 4 in 70 %; kinds P 1,670 / B 1,634 / L 1,494 / A 221; planted by Bubaptik
2,040, by the opponent 1,781 (35 %), initial 1,198; opponent's half 46 %; nearest tree 22 %;
long trips are common (>= 5 cells: 34 %; speed 4 makes distance cheap).
Rules (in-argmax; expected with random tie-break): wood/(travel+chops+1) 38.4 % (17.0);
size/(travel+1) 36.2 % (17.1); champion value 35.9 % (15.8); biggest tree 23.0 % (18.1); nearest
opponent-planted 22.7 % (17.9); nearest 21.5 % (15.5); closest to the opponent's shack 19.9 %.
Turns 1-100 (805 trips): the value rules hit 70 % in-set but only 10 % expected (all ties: a
carry-2 troll makes every size >= 2 tree "worth" 2), nearest tree 47.2 % (35.1 expected),
closest to the enemy shack 38.8 %, fruitless-first 34.9 % (28.4). So the early chopper mostly
cuts the nearest fruitless tree, with some pull toward the enemy shack; nothing simple explains
the mid/late choices (best expected ~18 %).

## 2. Planting (5,279 PLANT actions)

Cell: 2,272 shack-adjacent, 1,300 at distance 2, 692 at 3, then a tail to 12 (Bubaptik plants
farther out than the other three; 40 plants on the opponent's half). Rules: min d(shack) +
d(troll) 84.2 %; nearest to the troll 81.5 % (1,689 plants without moving, 2,267 after one step);
nearest to the shack 49.7 %; nearest-to-troll cell with <= 1 adjacent tree 53.3 %; water-adjacent
first 16-21 % (rejected). Kind by phase: turns 0-99 PLUM 781 / LEMON 695 / BANANA 46; 150-299
PLUM 1,430 / BANANA 967 / LEMON 690.

## 3. Harvest target (7,646 trips with movement)

Plums 3,592, lemons 3,135, apples 511, bananas 408; own-planted 64 %; 44 % of targets at
distance 2 from the shack. Rules: nearest tree with fruit (no other own troll on it) 54.3 %
(44.0 expected); nearest with fruit 54.3 % (42.8); ties -> more fruit 47.9 % (42.7); the
throughput value min(fruits,free)/(travel+harvest+return+1) 51.0 % (32.7); closest-to-shack
27.6 %.

## 3b. Score composition and own-tree lifecycle

Final score: mean 266 wood points + 28 fruit points (wood share 91 %). Wood per game: 39.9
from own-planted trees, 14.0 from opponent-planted, 14.5 from initial trees (the lowest
own-orchard yield of the four, the highest reliance on the map's trees). Own trees: 3,979 chop
runs, mostly at full size (P4 1,228, L4 749, B4 249) after a long wait (median age at chop 36
turns for plums, 46 for lemons), plus a plant-and-cut banana stream (B1 439 cuts, median banana
age 7 turns; 888 cuts within 4 turns of planting). No TRAIN on turn 1 in any of the 182 games
(the first troll mines or plants first; 1,073 MINE actions). Games end with 2 trolls in 35,
3 in 65, 4 in 74, 5 in 8.

## 4. Endgame

Last PLANT median turn 293, last HARVEST median 280, first own-tree chop median 128; own-tree
chops per 25 turns: 118 (100-124), 353 (150-174), 585 (200-224), 682 (250-274), 670 (275-299);
harvest runs 1,616 (125-149) -> 807 (200-224) -> 364 (275-299). A gradual shift from harvesting
to cutting the orchard from turn ~150, without a hard switch.
