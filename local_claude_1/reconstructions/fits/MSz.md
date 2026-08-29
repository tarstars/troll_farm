# MSz (agent 6479460) -- decision-rule fits from 203 full-length replays (first pass)

Data: every corpus game of MSz that ran 300 turns (203 of 216), reconstructed exactly (see
`README.md`, validator "exact" on all 203); 66,753 unit trips. Written in the last minutes
before the 04:15Z report; shallower than the delineate/norxondor fits.

## 0. In one paragraph

A **fixed three-troll plan with a harvest-heavy orchard**. TRAIN on turn 1 in nearly every game
(second troll at median turn 1: (2,2,2,1) 59, (1,2,2,1) 37, (2,2,1,1) 35, (2,1,1,1) 28, (1,1,1,1)
27 -- whatever the start inventory affords, with harvest power 2 when possible and chop kept at
1), third troll at median turn 97 = a carry-4 chopper ((2,4,1,2) 83, (2,4,1,3) 66, (2,4,1,4) 16;
cc 4 in 169 of 169), fourth troll at median 128 = (2,4,0,3) (64 of 73; harvest power 0). Games
end with 3 trolls in 96 cases, 4 in 73, 2 in 33. Training fires the very turn the spec is
affordable (delay 0 in 441 of 444), but the spec is NOT the largest affordable one: in 200 of
444 cases a strictly bigger spec was affordable (the objective "max ms+cc+chop" fits only 66 %)
-- MSz follows a fixed ladder (cc 4 for troll 3, (2,4,0,3) for troll 4) and waits for it.
Roles: troll 1 (1,1,1,1) HARVEST 36 % / DROP 32 % / CHOP 17 % / PLANT 10 %; the small second
trolls ((2,2,2,1), (1,2,2,1), (2,2,1,1)) are harvesters too (HARVEST 38-45 %, DROP 27-38 %,
CHOP 10-13 %); the cc-4 trolls are choppers (CHOP 61-77 %, DROP 22-28 %). Harvesting does not
collapse late (2,000+ harvest runs per 25-turn bucket from turn 125 to 299; last HARVEST at
median turn 298) -- unlike norxondor's clear-cut.

## 1. Chop target (6,918 chop trips with movement; 4,055 in place)

Chosen tree: size 4 in 71 %; kinds L 2,237 / B 1,894 / P 1,689 / A 1,098 (MSz chops apples,
the others avoid them); planted by MSz 4,196 (61 %), initial 1,372, opponent 1,350; on the own
half 75 %; nearest tree only 21 %; distance 1-2 cells 62 %.
Rules (in-argmax; expected with random tie-break): size/(travel+1) 36.1 % (20.4); wood/(travel +
chop turns) 33.0 % (**25.1**); champion value 29.9 % (23.8); biggest tree 28.4 % (20.3);
nearest 20.8 % (12.9); closest to the opponent's shack 11.5 %; opponent-planted first 11.4 %;
denial rules < 12 %. Early game (turns 1-100, 695 trips): biggest tree / size per travel 27-29 %,
everything else below 20 %. No denial phase at all (3.6 % of early targets closest to the enemy
shack, versus 40 % for delineate). Verdict as for the others: wood-per-turn is the best simple
description at ~25 % expected; the ordering is not recovered.

## 2. Planting (6,069 PLANT actions)

Cell: 2,583 shack-adjacent, 2,949 at distance 2, 360 at 3 -- a tight two-ring orchard, never
beyond distance 6, never on the opponent's half. Rules: min d(shack) + d(troll) 77.6 %; nearest to
the troll 58.4 %; nearest to the shack 57.4 % (= shack-adjacent first); nearest-to-shack cell
with an adjacent tree 57.3 %; water-adjacent first 15 % (rejected). Kind: turns 0-49 BANANA 778 /
LEMON 496 / PLUM 325 / APPLE 111 (1,393 plants in the first 25 turns -- the opening is a
planting burst); later LEMON leads (435 / 398 / 251 in the 150-299 buckets) with apples rising
to 199 in 200-249 (apples feed harvest power? no -- the trained trolls have hp <= 2; apples are
simply points and big wood: an apple tree at size 4 is 4 wood behind 20 health).

## 3. Harvest target (12,433 harvest trips with movement)

Lemons 5,304, apples 3,463, plums 2,209, bananas 1,457; own-planted 68 %; 67 % of targets are
exactly 2 cells from the shack (8,367 of 12,433). Rules: min(fruits,free)/(travel+harvest+
return+1) 61.8 % (42.1 expected); nearest tree with fruit 60.1 % (44.5); nearest with fruit,
ties -> more fruit 54.0 % (**45.5**); ripening-within-2 59.3 %; closest-to-shack 43.1 %.

## 4. Endgame

None visible: last PLANT median 280, last HARVEST median 298, own-tree chops flat at 700-900 per
25 turns from turn 125, all trees alive 25.4 (turn 100) -> 12.4 (300), own-planted 7.1 -> 3.5.
First chop of an own tree at median turn 18: MSz cuts its own trees from the start.

## 5. Score composition and the own-tree lifecycle

Final score: mean 321 wood points + 81 fruit points (wood share 80 %, the lowest of the three;
MSz banks far more fruit: 22,080 harvest runs, 95 % single-turn, 24,521 drops of which 61 %
carry one item). Wood per game: 51.4 from own-planted trees, 16.7 from initial trees, 12.8
from opponent-planted ones. Own trees are grown to full size before cutting: of 7,656 own-tree
chop runs, 4,917 were at size 4 (L 1,842, B 1,489, P 857, A 729); median age at chop 26 turns
for bananas, 29 for lemons and plums, 37 for apples; only 792 cuts within 4 turns of planting
(no plant-and-cut conversion like norxondor's). 4,055 chops happen without moving: 2,534 right
after a DROP on the same cell (the tree next to the shack is cut after unloading), 655 after
planting there, 635 after an interrupted chop, 234 after harvesting the tree first. MINE:
1,237 actions (iron for the chop-3 troll). TRAIN on turn 1 in 196 of 203 games.
