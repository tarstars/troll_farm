# Behaviour profile: yamo (agent ids 6479814; 541 games)

## Summary (plain words)

yamo (agent 6479814, 541 games; the design our bot reproduces; win rate 0.495, mean score 153 against 153; opponents rated 20-25 in 78 % of games).

1. Two trolls, always: the second at median turn 4 (97 % by turn 25), always HARVEST 0 (2 2 0 2 in 17 %, 2 2 0 3 in 10 %; chop 2-3 in 83 %). Never a third troll.
2. Never harvests (0.5 HARVEST commands per game, all in the first 30 turns; 2 fruit points per game); 99 % of its points are wood.
3. A wild-tree chopper from turn ~12 (first wood at median turn 17): 157 CHOP commands per game, 38 wood; chop power 1 does 64 % of the chopping. Chop targets: wild 50 %, own 32 %, opponent-planted 18 %; apples are 40 % of chopped trees (54 % after turn 100) — big apples give 4 wood each.
4. Plants 11 per game, bananas 50 % and apples 33 %, every one exactly adjacent to its shack (100 % at distance 1), from turn ~60 on with a hump at turns 100-150 and again after 250; it then fells them: 62 % of its late chops are its own trees.
5. Destination-style MOVE commands (mean 5.5 cells away, up to 45): 39 % of targets are a cell next to its own shack (going home to drop), 32 % wild trees, 19 % opponent trees. This is the bot whose intentions the corpus shows best.
6. Mines only in the first 10 turns of 35 % of games (0.6 iron per game).
7. Deforests the map: 381 of 541 games ended before turn 300 and 388 end with no tree left; its last DROP is at median turn 221.
8. 27 timeout strikes over 541 games; 5.3 blocked-move failures per game (its trolls walk into each other).
9. Loses to trained-up opponents: 52 % wins against 2-troll opponents, 26 % against 3, 0 % against 4 (15 games).
10. MSG texts like "0>T(12,4)" and "0>T(12,4)|1>T(3,7)": each troll's current target cell (T = tree, M = move) — a readable trace of its targeting.

## How to read this

Every table is measured over this player's games in the corpus (`n` = the number of games or events behind the row). Positions and effects come from the referee's own per-turn log inside each replay (exact troll positions after every move, which tree was planted/damaged/harvested), so 'own-planted / wild / opponent-planted' and 'tree type at the time of the chop' are exact for games read from a raw replay. For a game read from `turns.jsonl.gz` only (no raw replay), positions are simulated from MOVE targets and marked approximate. Position source for this profile: {"raw_replay_exact_positions": 541}.

## 9. Results and score composition

| measure | value |
|---|---|
| games | 541 |
| win rate | 0.495 |
| seat 0 games | 283 |
| final score | mean 153.25, median 144.0, p25-p75 120.0-180.0, min-max 32.0-361.0 (n=541) |
| opponent final score | mean 152.6, median 142.0, p25-p75 112.0-180.0, min-max 19.0-497.0 (n=541) |
| score margin | mean 0.65, median 0.0, p25-p75 -9.0-8.0, min-max -338.0-229.0 (n=541) |
| fruit points (banked fruit) | mean 2.01, median 0, p25-p75 0.0-2.0, min-max 0-23 (n=541) |
| wood points (4 x banked wood) | mean 151.24, median 144, p25-p75 116.0-180.0, min-max 24-348 (n=541) |
| wood share of all points | 0.987 |
| final inventory mean (plum, lemon, apple, banana, iron, wood) | [0.12, 0.15, 1.27, 0.47, 0.65, 37.81] |
| games ending before turn 300 | 381 |
| turns per game | mean 226.43, median 222, p25-p75 171.5-300.0, min-max 66-300 (n=541) |
| timeout strikes (total) | 27 |

By the opponent's troll count at the end:

| opponent trolls | n | win rate | mean score | mean opp score |
|---|---|---|---|---|
| 1 | 16 | 1.0 | 160.0 | 64.4 |
| 2 | 466 | 0.517 | 147.2 | 143.6 |
| 3 | 43 | 0.256 | 194.8 | 230.3 |
| 4 | 15 | 0.0 | 210.7 | 296.1 |
| 5+ | 1 | 0.0 | 216.0 | 246.0 |

By own troll count at the end:

| own trolls | n | win rate | mean score |
|---|---|---|---|
| 2 | 541 | 0.495 | 153.2 |

By the opponent's arena score (their ladder rating in the corpus record):

| opponent arena score | n | win rate | mean score |
|---|---|---|---|
| 20-25 | 424 | 0.483 | 141.4 |
| 25-28 | 114 | 0.526 | 196.5 |
| <20 | 3 | 1.0 | 175.3 |

Most frequent opponents:

| opponent | n | share |
|---|---|---|
| tass | 327 | 0.604 |
| Bubaptik | 96 | 0.177 |
| FreZzz | 80 | 0.148 |
| Stounate | 18 | 0.033 |
| a76a44 | 4 | 0.007 |
| wala | 4 | 0.007 |
| celeria | 2 | 0.004 |
| ATsibin | 2 | 0.004 |
| goq | 1 | 0.002 |
| IlyaPol | 1 | 0.002 |
| _NikJ | 1 | 0.002 |
| TheMagicShop | 1 | 0.002 |

## 1. Training ladder (TRAIN = buy a new troll; talents = speed carry harvest chop)

| measure | value |
|---|---|
| TRAIN commands total / failed | 541 / 0 |
| trolls at the end | mean 2.0, median 2, p25-p75 2.0-2.0, min-max 2-2 (n=541) |
| trolls trained per game | 1: 541 games (1.0) |

**troll_2** (the first troll bought): in 541 games (1.0 of games); turn mean 7.25, median 4, p25-p75 1.0-14.0, min-max 1-57 (n=541); turn histogram (25-turn bins, start turn: n) {'1': 526, '26': 14, '51': 1}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 2 0 2 | 93 | 0.172 |
| 2 2 0 3 | 55 | 0.102 |
| 2 3 0 2 | 37 | 0.068 |
| 2 1 0 2 | 34 | 0.063 |
| 3 2 0 2 | 30 | 0.055 |
| 1 2 0 2 | 30 | 0.055 |
| 2 1 0 3 | 29 | 0.054 |
| 2 2 0 1 | 27 | 0.05 |

marginals: speed: {'1': 132, '2': 306, '3': 103}; carry: {'1': 134, '2': 293, '3': 114}; harvest: {'0': 541}; chop: {'1': 92, '2': 284, '3': 165}

Opponents' trained talents (for contrast):

| talents | n | share |
|---|---|---|
| 2 2 0 2 | 82 | 0.136 |
| 2 2 2 2 | 42 | 0.07 |
| 2 2 0 3 | 36 | 0.06 |
| 3 2 0 2 | 27 | 0.045 |
| 2 2 1 2 | 26 | 0.043 |
| 2 2 1 1 | 25 | 0.042 |

## 2. Opening (turns 1-30)

Letters: M=MOVE, H=HARVEST, C=CHOP, P=PLANT, K=PICK, D=DROP, I=MINE, T=TRAIN, W=WAIT, -=no command for that troll.

Starting troll, one letter per turn, turns 1-10 (most common patterns):

| pattern | n | share |
|---|---|---|
| MMMMMMMMMM | 121 | 0.224 |
| MMIMDMIMDM | 41 | 0.076 |
| MMMMMCCCCC | 27 | 0.05 |
| MMMMMMCCCC | 23 | 0.043 |
| MMMIMMDMMI | 21 | 0.039 |
| MMMMMMMMMC | 20 | 0.037 |
| MMMMMMMMCC | 20 | 0.037 |
| MMMMMMMCCC | 20 | 0.037 |
| MMMMIMMMDM | 18 | 0.033 |
| MMMIMMDMMM | 16 | 0.03 |
| MIDIDIDMMM | 14 | 0.026 |
| MMMMMMHMMM | 13 | 0.024 |

Starting troll, turns 1-20:

| pattern | n | share |
|---|---|---|
| MMMMMMMMMMMMMCCCCCCC | 16 | 0.03 |
| MMMMMMMMMCCCCCCCCCCC | 14 | 0.026 |
| MMIMDMIMDMIMDMMMMMMM | 13 | 0.024 |
| MMMMMMMMMMMMCCCCCCCC | 12 | 0.022 |
| MMMIMMDMMIMMDMMMMMMM | 10 | 0.018 |
| MMMMMMMMMMCCCCCCCCCC | 9 | 0.017 |
| MMMMMMMMMMMMMMCCCCCC | 9 | 0.017 |
| MMMMMMMMCCCCCCCCCCCC | 9 | 0.017 |

All trolls together, turns 1-10 (letters of one turn joined, turns separated by spaces):

| pattern | n | share |
|---|---|---|
| MT MM MM MM MM MM MM MM MM MM | 49 | 0.091 |
| M M I M D M I M D M | 30 | 0.055 |
| MT MM MM MM MM MM MM MM MM CM | 24 | 0.044 |
| M M M I M M D M M I | 21 | 0.039 |
| MT MM MM MM MM MM CM CM CM CM | 17 | 0.031 |
| M M M M I M M M D MT | 14 | 0.026 |
| M M M M M M H M M M | 13 | 0.024 |
| M M M I M M D MT MM MM | 13 | 0.024 |

First occurrences (turn of the first command of that kind; games with it):

| verb | games with it | turn |
|---|---|---|
| CHOP | 541 | mean 13.5, median 12, p25-p75 7.0-19.0, min-max 2-42 (n=541) |
| MINE | 190 | mean 3.52, median 3.0, p25-p75 2.0-4.0, min-max 2-7 (n=190) |
| TRAIN | 541 | mean 7.25, median 4, p25-p75 1.0-14.0, min-max 1-57 (n=541) |
| DROP | 541 | mean 13.31, median 11, p25-p75 5.0-19.0, min-max 3-50 (n=541) |
| HARVEST | 157 | mean 8.12, median 7, p25-p75 3.0-12.0, min-max 2-23 (n=157) |
| PLANT | 505 | mean 160.4, median 135, p25-p75 97.5-253.0, min-max 47-287 (n=505) |

first action verb of start troll:

| value | n | share |
|---|---|---|
| C | 262 | 0.484 |
| I | 190 | 0.351 |
| H | 89 | 0.165 |

first harvest type:

| value | n | share |
|---|---|---|
| LEMON | 85 | 0.541 |
| PLUM | 72 | 0.459 |

first harvest origin:

| value | n | share |
|---|---|---|
| wild | 157 | 1.0 |

first plant type:

| value | n | share |
|---|---|---|
| BANANA | 505 | 1.0 |

first chop type:

| value | n | share |
|---|---|---|
| LEMON | 284 | 0.525 |
| PLUM | 253 | 0.468 |
| BANANA | 3 | 0.006 |
| APPLE | 1 | 0.002 |

first chop origin:

| value | n | share |
|---|---|---|
| wild | 479 | 0.885 |
| opp | 62 | 0.115 |

Verb share by turn, turns 1-30 (commands per game, by letter):

| turn | M | H | C | P | K | D | I | T | W |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0 |  |  |  |  |  |  | 0.48 |  |
| 2 | 1.34 | 0.04 | 0.0 |  |  |  | 0.1 |  |  |
| 3 | 1.18 | 0.03 | 0.03 |  |  | 0.14 | 0.11 |  |  |
| 4 | 1.22 | 0.05 | 0.07 |  |  |  | 0.14 | 0.04 |  |
| 5 | 1.11 | 0.02 | 0.14 |  |  | 0.22 | 0.03 |  |  |
| 6 | 1.19 | 0.03 | 0.24 |  |  |  | 0.06 | 0.05 |  |
| 7 | 0.92 | 0.04 | 0.34 |  |  | 0.17 | 0.1 |  |  |
| 8 | 1.13 | 0.01 | 0.41 |  |  | 0.0 | 0.01 | 0.05 |  |
| 9 | 0.94 | 0.02 | 0.49 |  |  | 0.18 |  |  |  |
| 10 | 0.96 | 0.03 | 0.58 |  |  | 0.01 | 0.04 | 0.08 |  |
| 11 | 0.93 | 0.03 | 0.61 |  |  | 0.09 | 0.05 |  |  |
| 12 | 1.03 | 0.03 | 0.63 |  |  | 0.02 |  | 0.04 |  |
| 13 | 0.85 | 0.03 | 0.64 |  |  | 0.21 |  |  |  |
| 14 | 0.99 | 0.02 | 0.68 |  |  | 0.05 |  | 0.13 |  |
| 15 | 1.08 | 0.02 | 0.69 |  |  | 0.08 |  |  |  |
| 16 | 1.1 | 0.02 | 0.7 |  |  | 0.05 |  | 0.03 |  |
| 17 | 1.05 | 0.02 | 0.72 |  |  | 0.11 |  |  |  |
| 18 | 1.09 | 0.01 | 0.73 |  |  | 0.06 |  | 0.02 |  |
| 19 | 1.07 | 0.02 | 0.74 |  |  | 0.09 |  |  |  |
| 20 | 1.07 | 0.01 | 0.75 |  |  | 0.09 |  | 0.02 |  |
| 21 | 1.03 | 0.01 | 0.79 |  |  | 0.11 |  |  |  |
| 22 | 1.07 | 0.01 | 0.77 |  |  | 0.09 |  | 0.02 |  |
| 23 | 1.08 | 0.0 | 0.78 |  |  | 0.1 |  |  |  |
| 24 | 1.13 | 0.01 | 0.77 |  |  | 0.06 |  | 0.01 |  |
| 25 | 1.05 | 0.0 | 0.81 |  |  | 0.11 |  |  |  |
| 26 | 1.09 |  | 0.78 |  |  | 0.1 |  | 0.01 |  |
| 27 | 1.11 | 0.0 | 0.77 |  |  | 0.1 |  |  |  |
| 28 | 1.15 |  | 0.73 |  |  | 0.11 |  | 0.01 |  |
| 29 | 1.14 |  | 0.75 |  |  | 0.1 |  |  |  |
| 30 | 1.12 |  | 0.74 |  |  | 0.13 |  | 0.01 |  |

Most common MSG texts (digits replaced by N):

| message | n | share |
|---|---|---|
|  | 69516 | 0.567 |
| N>T(N,N) | 41857 | 0.342 |
| N>T(N,N)|N>T(N,N) | 10539 | 0.086 |
| N>M(N,N) | 586 | 0.005 |

## 3. Planting

| measure | value |
|---|---|
| PLANT commands per game | mean 11.12, median 11, p25-p75 9.0-14.0, min-max 0-49 (n=541) |
| successful plants per game | mean 11.04, median 11, p25-p75 9.0-14.0, min-max 0-24 (n=541) |
| success rate of PLANT commands | 0.993 |
| distance (BFS over grass) from own shack | mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-1 (n=5973) |
| distance hist (cells: n; 12 = 12 or more) | {'1': 5973} |
| distance from opponent shack | mean 9.8, median 10, p25-p75 7.0-13.0, min-max 1-26 (n=5973) |
| planted next to water | 0.144 |
| next to water, by type | {'PLUM': 0.171, 'LEMON': 0.141, 'APPLE': 0.135, 'BANANA': 0.146} |
| planted on own half of the map | 0.968 |
| planted nearer own shack than opponent's | 0.994 |
| plants per game by 10-turn bucket | {'41-50': 0.0, '51-60': 0.03, '61-70': 0.1, '71-80': 0.24, '81-90': 0.41, '91-100': 0.58, '101-110': 0.7, '111-120': 0.76, '121-130': 0.75, '131-140': 0.74, '141-150': 0.67, '151-160': 0.59, '161-170': 0.51, '171-180': 0.41, '181-190': 0.35, '191-200': 0.28, '201-210': 0.22, '211-220': 0.2, '221-230': 0.14, '231-240': 0.15, '241-250': 0.18, '251-260': 0.5, '261-270': 0.74, '271-280': 0.72, '281-290': 0.64, '291-300': 0.41} |

By type (successful plants):

| type | n | share |
|---|---|---|
| BANANA | 3001 | 0.502 |
| APPLE | 1966 | 0.329 |
| PLUM | 515 | 0.086 |
| LEMON | 491 | 0.082 |

Seeds picked at the shack (PICK commands) by type:

| type | n | share |
|---|---|---|
| BANANA | 3035 | 0.5 |
| APPLE | 1987 | 0.328 |
| PLUM | 539 | 0.089 |
| LEMON | 503 | 0.083 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA |
|---|---|---|---|---|
| early(1-100) | 0.069 | 0.047 | 0.135 | 0.749 |
| mid(101-200) | 0.091 | 0.086 | 0.382 | 0.441 |
| late(201-300) | 0.085 | 0.089 | 0.32 | 0.507 |

Distance from own shack by type: PLUM: mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-1 (n=515); LEMON: mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-1 (n=491); APPLE: mean 1.0, median 1.0, p25-p75 1.0-1.0, min-max 1-1 (n=1966); BANANA: mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-1 (n=3001)

## 4. Harvesting

| measure | value |
|---|---|
| HARVEST commands per game | mean 0.52, median 0, p25-p75 0.0-1.0, min-max 0-5 (n=541) |
| fruits harvested per game (referee count) | mean 0.52, median 0, p25-p75 0.0-1.0, min-max 0-5 (n=541) |
| fruits per HARVEST command | 1.0 |
| HARVEST commands that took nothing | 0.0 |
| distance from own shack of the harvested cell | mean 2.52, median 2.0, p25-p75 1.0-3.0, min-max 1-13 (n=280) |
| harvests per game by 10-turn bucket | {'1-10': 0.29, '11-20': 0.2, '21-30': 0.03, '41-50': 0.0} |

By the tree's origin (own-planted / wild / planted by the opponent):

| origin | n | share |
|---|---|---|
| wild | 280 | 1.0 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0 | 1.0 | 0 | 0 |
| mid(101-200) | 0 | 0 | 0 | 0 |
| late(201-300) | 0 | 0 | 0 | 0 |

Fruits harvested by type:

| type | n | share |
|---|---|---|
| LEMON | 142 | 0.507 |
| PLUM | 138 | 0.493 |

## 5. Chopping

| measure | value |
|---|---|
| CHOP commands per game | mean 157.19, median 155, p25-p75 119.5-190.0, min-max 35-325 (n=541) |
| chops that landed per game | mean 128.0, median 125, p25-p75 93.0-156.0, min-max 28-294 (n=541) |
| trees felled per game (this player struck the killing turn) | mean 0.0, median 0, p25-p75 0.0-0.0, min-max 0-1 (n=541) |
| wood collected per game | mean 38.07, median 36, p25-p75 29.5-45.0, min-max 7-90 (n=541) |
| turn of the first wood | mean 18.77, median 17, p25-p75 13.0-23.0, min-max 5-69 (n=541) |
| wood by phase (total over games) | {'early(1-100)': 8584, 'mid(101-200)': 7955, 'late(201-300)': 4059} |
| chops per game by 10-turn bucket | {'1-10': 2.29, '11-20': 6.91, '21-30': 7.69, '31-40': 7.01, '41-50': 7.17, '51-60': 7.52, '61-70': 7.27, '71-80': 7.38, '81-90': 7.2, '91-100': 6.8, '101-110': 6.92, '111-120': 7.15, '121-130': 7.07, '131-140': 6.82, '141-150': 6.29, '151-160': 6.21, '161-170': 5.67, '171-180': 5.17, '181-190': 4.64, '191-200': 4.35, '201-210': 3.67, '211-220': 3.28, '221-230': 2.9, '231-240': 2.66, '241-250': 2.51, '251-260': 2.52, '261-270': 2.57, '271-280': 2.96, '281-290': 3.15, '291-300': 3.43} |
| chopped on own half of the map | 0.648 |
| distance from own shack | mean 5.83, median 5.0, p25-p75 1.0-9.0, min-max 1-30 (n=85040) |
| distance from opponent shack | mean 8.84, median 9.0, p25-p75 4.0-13.0, min-max 1-34 (n=85040) |

By the tree's origin:

| origin | n | share |
|---|---|---|
| wild | 42332 | 0.498 |
| own | 27378 | 0.322 |
| opp | 15330 | 0.18 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.049 | 0.819 | 0.133 | 0 |
| mid(101-200) | 0.478 | 0.321 | 0.201 | 0 |
| late(201-300) | 0.624 | 0.129 | 0.246 | 0 |

Nearer to whose shack (BFS distance):

| nearer | n | share |
|---|---|---|
| own | 55682 | 0.655 |
| opp | 26728 | 0.314 |
| equal | 2630 | 0.031 |

Tree type at the time of the chop:

| type | n | share |
|---|---|---|
| APPLE | 34033 | 0.4 |
| PLUM | 17678 | 0.208 |
| LEMON | 17475 | 0.205 |
| BANANA | 15854 | 0.186 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA | ? |
|---|---|---|---|---|---|
| early(1-100) | 0.293 | 0.325 | 0.22 | 0.162 | 0 |
| mid(101-200) | 0.148 | 0.122 | 0.532 | 0.199 | 0 |
| late(201-300) | 0.138 | 0.106 | 0.54 | 0.216 | 0 |

Tree size at the chop:

| size | n | share |
|---|---|---|
| 1 | 45952 | 0.54 |
| 4 | 28178 | 0.331 |
| 2 | 5596 | 0.066 |
| 3 | 5314 | 0.062 |

Fruits on the tree at the chop:

| fruits | n | share |
|---|---|---|
| 0 | 65300 | 0.768 |
| 2 | 7874 | 0.093 |
| 1 | 7276 | 0.086 |
| 3 | 4590 | 0.054 |

Chop power of the chopping troll:

| chop power | n | share |
|---|---|---|
| 1 | 54150 | 0.637 |
| 2 | 21731 | 0.256 |
| 3 | 9159 | 0.108 |

## 6. Mining

| measure | value |
|---|---|
| MINE commands per game | mean 0.63, median 0, p25-p75 0.0-1.0, min-max 0-4 (n=541) |
| iron collected per game | mean 0.63, median 0, p25-p75 0.0-1.0, min-max 0-4 (n=541) |
| games with at least one MINE | 190 |
| iron per MINE command | 1.0 |
| turn of the first MINE | mean 3.52, median 3.0, p25-p75 2.0-4.0, min-max 2-7 (n=190) |
| mines per game by 10-turn bucket | {'1-10': 0.58, '11-20': 0.05} |

## 7. Unit roles (verb mix per troll, in creation order)

| troll | games | commands per game | verb mix | talents (n) |
|---|---|---|---|---|
| start_troll | 541 | mean 226.03, median 222, p25-p75 171.0-300.0, min-max 66-300 (n=541) | MOVE 0.543, CHOP 0.361, DROP 0.053, PLANT 0.019, PICK 0.019, MINE 0.003, HARVEST 0.002 | 1 1 1 1 (541) |
| trained_1 | 541 | mean 218.99, median 215, p25-p75 164.0-286.0, min-max 65-299 (n=541) | MOVE 0.513, CHOP 0.346, DROP 0.079, PICK 0.032, PLANT 0.031 | 2 2 0 2 (93); 2 2 0 3 (55); 2 3 0 2 (37); 2 1 0 2 (34) |

## 8. Endgame (last 30 turns)

| measure | value |
|---|---|
| verb mix, last 30 turns | {'CHOP': 0.414, 'MOVE': 0.388, 'DROP': 0.087, 'PLANT': 0.053, 'PICK': 0.051, 'WAIT': 0.008} |
| verb mix, whole game | {'MOVE': 0.526, 'CHOP': 0.352, 'DROP': 0.066, 'PICK': 0.025, 'PLANT': 0.025, 'TRAIN': 0.002, 'MINE': 0.001, 'WAIT': 0.001, 'HARVEST': 0.001} |
| commands per game in the last 30 turns | 60.0 |
| per game in the last 30 turns | {'plants': 3.19, 'chops': 24.82, 'harvests': 0.0, 'drops': 5.21, 'wood': 5.57} |
| turn of the last DROP | mean 223.35, median 221, p25-p75 170.0-293.0, min-max 56-300 (n=541) |
| turns from the last DROP to the end | mean 3.07, median 1, p25-p75 0.0-5.0, min-max 0-46 (n=541) |
| trees alive at the end per game (own / wild / opp) | {'own': 0.34, 'wild': 0.81, 'opp': 0.78} |
| games ending with no tree on the map | 388 |

Commands per game by verb: {"MOVE": 235.1, "CHOP": 157.2, "DROP": 29.3, "PICK": 11.2, "PLANT": 11.1, "TRAIN": 1.0, "MINE": 0.6, "WAIT": 0.6, "HARVEST": 0.5}

Commands per game by 10-turn bucket:

| turns | MOVE | HARVEST | CHOP | PLANT | PICK | DROP | MINE | TRAIN | WAIT |
|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 11.0 | 0.29 | 2.29 |  |  | 0.72 | 0.58 | 0.7 |  |
| 11-20 | 10.24 | 0.2 | 6.91 |  |  | 0.83 | 0.05 | 0.24 |  |
| 21-30 | 10.96 | 0.03 | 7.69 |  |  | 1.01 |  | 0.06 |  |
| 31-40 | 11.85 |  | 7.01 |  |  | 1.13 |  |  |  |
| 41-50 | 11.62 | 0.0 | 7.17 | 0.0 | 0.0 | 1.18 |  |  |  |
| 51-60 | 11.2 |  | 7.52 | 0.03 | 0.04 | 1.2 |  | 0.0 |  |
| 61-70 | 11.32 |  | 7.27 | 0.1 | 0.11 | 1.19 |  |  |  |
| 71-80 | 10.9 |  | 7.38 | 0.24 | 0.26 | 1.16 |  |  | 0.0 |
| 81-90 | 10.58 |  | 7.2 | 0.41 | 0.44 | 1.26 |  |  | 0.0 |
| 91-100 | 10.5 |  | 6.8 | 0.58 | 0.6 | 1.35 |  |  |  |
| 101-110 | 9.91 |  | 6.92 | 0.7 | 0.74 | 1.42 |  |  | 0.02 |
| 111-120 | 9.41 |  | 7.15 | 0.76 | 0.77 | 1.41 |  |  | 0.04 |
| 121-130 | 8.87 |  | 7.07 | 0.75 | 0.74 | 1.41 |  |  | 0.04 |
| 131-140 | 8.52 |  | 6.82 | 0.75 | 0.76 | 1.35 |  |  | 0.03 |
| 141-150 | 8.55 |  | 6.29 | 0.69 | 0.68 | 1.32 |  |  | 0.04 |
| 151-160 | 8.12 |  | 6.21 | 0.61 | 0.6 | 1.18 |  |  | 0.03 |
| 161-170 | 7.81 |  | 5.67 | 0.53 | 0.5 | 1.12 |  |  | 0.06 |
| 171-180 | 7.75 |  | 5.17 | 0.42 | 0.41 | 0.94 |  |  | 0.07 |
| 181-190 | 7.39 |  | 4.64 | 0.35 | 0.36 | 0.9 |  |  | 0.03 |
| 191-200 | 7.13 |  | 4.35 | 0.28 | 0.27 | 0.75 |  |  | 0.06 |
| 201-210 | 6.92 |  | 3.67 | 0.22 | 0.21 | 0.75 |  |  | 0.03 |
| 211-220 | 6.35 |  | 3.28 | 0.2 | 0.21 | 0.61 |  |  | 0.04 |
| 221-230 | 6.13 |  | 2.9 | 0.14 | 0.14 | 0.53 |  |  | 0.01 |
| 231-240 | 5.77 |  | 2.66 | 0.15 | 0.15 | 0.52 |  |  | 0.02 |
| 241-250 | 5.21 |  | 2.51 | 0.18 | 0.17 | 0.5 |  |  | 0.02 |
| 251-260 | 3.63 |  | 2.52 | 0.5 | 0.56 | 0.67 |  |  | 0.01 |
| 261-270 | 2.45 |  | 2.57 | 0.74 | 0.76 | 0.87 |  |  | 0.02 |
| 271-280 | 1.8 |  | 2.96 | 0.72 | 0.72 | 0.82 |  |  | 0.01 |
| 281-290 | 1.62 |  | 3.15 | 0.64 | 0.63 | 0.71 |  |  |  |
| 291-300 | 1.52 |  | 3.43 | 0.41 | 0.39 | 0.5 |  |  |  |

DROP: mean 29.31, median 29, p25-p75 24.0-34.0, min-max 6-59 (n=541) commands per game; items per drop mean 1.33, median 1, p25-p75 1.0-2.0, min-max 1-3 (n=15855)

Referee-reported failures per game: {"move_blocked": 5.25, "pick_out_of_stock": 0.13, "failed_other": 0.0}

## 10. Movement

| measure | value |
|---|---|
| MOVE commands per game | mean 235.05, median 220, p25-p75 149.0-324.0, min-max 50-455 (n=541) |
| BFS distance from the troll's cell to the MOVE target | mean 5.53, median 5.0, p25-p75 2.0-8.0, min-max 0-45 (n=126578) |
| distance histogram (15 = 15 or more) | {'0': 4288, '1': 14872, '2': 15619, '3': 13672, '4': 13298, '5': 11161, '6': 10717, '7': 8249, '8': 7756, '9': 6036, '10': 5257, '11': 3937, '12': 3387, '13': 2308, '14': 1857, '15': 4164} |
| turns needed to arrive (distance / speed, rounded up) | mean 4.55, median 4.0, p25-p75 2.0-6.0, min-max 0-45 (n=126578) |
| target unreachable (water, rock, a shack cell) | 0.005 |
| target = the troll's current cell | 0.034 |

What the MOVE target is:

| target | n | share |
|---|---|---|
| own_shack_adjacent | 49708 | 0.391 |
| tree_wild | 40645 | 0.32 |
| tree_opp | 23783 | 0.187 |
| opp_shack_adjacent | 9963 | 0.078 |
| tree_own | 2479 | 0.019 |
| unwalkable_other | 576 | 0.005 |
| iron_adjacent | 10 | 0.0 |

## What the corpus cannot tell

- Why a decision was taken: no bot state, no evaluation, no stderr. Only commands and the referee's outcomes are recorded.
- A troll's carried inventory between DROPs (the viewer shows one item at a time); carry is inferred only through referee events.
- Whether a MOVE was re-targeted before arrival is visible, but the intended destination of a multi-turn walk is not.
- Tree fruit counts and cooldowns are followed through the viewer diff (stage = size + fruits); the stage shown at a chop is the state after that turn's tick.
- Games of this agent id only; earlier or later versions of the same player's bot may differ.
