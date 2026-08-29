# Behaviour profile: norxondor_gorgonax (agent ids 6480540; 218 games)

## Summary (plain words)

norxondor_gorgonax (Legend #2; agent 6480540; 218 games, all from raw replays; win rate 0.665, mean score 345 against 272).

1. The heaviest trainer: 3.5 trolls at the end on average, four or more in 52 % of games, and a rigid four-stage ladder. Troll 2 at median turn 9 = 2 2 2 2 (41 %) or 2 2 1 2 (19 %); troll 3 (85 % of games, turn ~100) = 2 3 1 2 in 64 %; troll 4 (52 %, turn ~132) = 2 3 0 3 in 47 % (chop 3 in 100 %, harvest 0 in 63 %); troll 5 (11 %, turn ~153) = 2 4 0 3 in 58 %. Speed stays 2 in 86 % of all trained trolls.
2. A two-phase game. Turns 1-100 are almost pure fruit economy: only 7 chops per game in the first 100 turns (delineate 28, Bubaptik 20) and the first wood arrives at median turn 97 (delineate 26, Bubaptik 24).
3. From turn ~100 the chop rate climbs to 12-13 per 10 turns around turns 170-220, the highest late chop rate of the four: 189 CHOP commands per game (the most), 80 wood.
4. It fells plums and lemons, not bananas: chopped trees are plum 37 %, lemon 33 %, apple 16 %, banana 14 % (delineate and MSz fell far more bananas). 63 % of the trees it chops are size 1 (just planted), 34 % size 4.
5. Plants 29 per game: lemon 35 %, plum 32 %, banana 26 % (bananas only in mid-game, 42 % of mid-game plants). The plants are the closest to home of all: median 1 cell from the shack, 57 % at distance 1, never beyond 4 cells.
6. The most opponent-directed chopper: 30 % of its chops are on opponent-planted trees and 36 % are nearer the opponent's shack than its own; in turns 1-100, 58 % of its (few) chops hit opponent trees.
7. Harvests 78 times per game (90 fruits; lemon 45 %, plum 31 %), 69 % at its own trees; harvesting almost stops after turn 200 (0.5-0.8 per 10 turns) when every troll becomes a chopper (endgame verb mix: MOVE 59 %, CHOP 29 %).
8. Mines late (first MINE at median turn 72) in 91 % of games, 12 iron per game, for the chop-3 trolls of stages 3-4.
9. Sends a MSG every turn with per-troll letters and a timing ("DD 0.5 ms", "PP ...", "DP", "TP"): the letters look like a mode code per troll (D, P, T) — a clue for the reconstruction, not decoded here. MOVE is step-wise (targets 0-4 cells away; 3 % of MOVEs to the cell it already stands on).
10. It clears the map: 48 games end with no tree left and 34 of 218 games ended before turn 300. With only two trolls it loses (27 % wins in those 30 games); with five or more it wins 83 %.

## How to read this

Every table is measured over this player's games in the corpus (`n` = the number of games or events behind the row). Positions and effects come from the referee's own per-turn log inside each replay (exact troll positions after every move, which tree was planted/damaged/harvested), so 'own-planted / wild / opponent-planted' and 'tree type at the time of the chop' are exact for games read from a raw replay. For a game read from `turns.jsonl.gz` only (no raw replay), positions are simulated from MOVE targets and marked approximate. Position source for this profile: {"raw_replay_exact_positions": 218}.

## 9. Results and score composition

| measure | value |
|---|---|
| games | 218 |
| win rate | 0.665 |
| seat 0 games | 111 |
| final score | mean 345.49, median 343.0, p25-p75 281.5-412.75, min-max 87.0-688.0 (n=218) |
| opponent final score | mean 271.5, median 250.0, p25-p75 197.5-344.0, min-max 30.0-657.0 (n=218) |
| score margin | mean 73.99, median 52.5, p25-p75 -19.0-151.25, min-max -328.0-423.0 (n=218) |
| fruit points (banked fruit) | mean 33.1, median 21.5, p25-p75 6.75-38.0, min-max 0-180 (n=218) |
| wood points (4 x banked wood) | mean 312.39, median 310.0, p25-p75 243.0-388.0, min-max 56-688 (n=218) |
| wood share of all points | 0.904 |
| final inventory mean (plum, lemon, apple, banana, iron, wood) | [7.61, 10.93, 9.83, 4.73, 1.35, 78.1] |
| games ending before turn 300 | 34 |
| turns per game | mean 294.68, median 300.0, p25-p75 300.0-300.0, min-max 202-300 (n=218) |
| timeout strikes (total) | 0 |

By the opponent's troll count at the end:

| opponent trolls | n | win rate | mean score | mean opp score |
|---|---|---|---|---|
| 1 | 2 | 1.0 | 304.0 | 55.0 |
| 2 | 59 | 0.712 | 290.6 | 213.2 |
| 3 | 53 | 0.755 | 307.3 | 214.1 |
| 4 | 86 | 0.57 | 375.3 | 327.6 |
| 5+ | 18 | 0.667 | 500.0 | 387.5 |

By own troll count at the end:

| own trolls | n | win rate | mean score |
|---|---|---|---|
| 1 | 2 | 0.0 | 89.5 |
| 2 | 30 | 0.267 | 210.4 |
| 3 | 73 | 0.712 | 302.7 |
| 4 | 89 | 0.73 | 392.5 |
| 5+ | 24 | 0.833 | 491.6 |

By the opponent's arena score (their ladder rating in the corpus record):

| opponent arena score | n | win rate | mean score |
|---|---|---|---|
| 20-25 | 63 | 0.746 | 324.4 |
| 25-28 | 152 | 0.625 | 354.1 |
| <20 | 3 | 1.0 | 350.3 |

Most frequent opponents:

| opponent | n | share |
|---|---|---|
| Bubaptik | 149 | 0.683 |
| tass | 38 | 0.174 |
| wala | 8 | 0.037 |
| a76a44 | 6 | 0.028 |
| FreZzz | 2 | 0.009 |
| laconic_pixel | 1 | 0.005 |
| OldJohn | 1 | 0.005 |
| goq | 1 | 0.005 |
| therealbeef | 1 | 0.005 |
| Arnaud.Net | 1 | 0.005 |
| Alos | 1 | 0.005 |
| Shartiniquais | 1 | 0.005 |

## 1. Training ladder (TRAIN = buy a new troll; talents = speed carry harvest chop)

| measure | value |
|---|---|
| TRAIN commands total / failed | 545 / 5 |
| trolls at the end | mean 3.48, median 4.0, p25-p75 3.0-4.0, min-max 1-6 (n=218) |
| trolls trained per game | 0: 2 games (0.009), 1: 30 games (0.138), 2: 73 games (0.335), 3: 89 games (0.408), 4: 23 games (0.106), 5: 1 games (0.005) |

**troll_2** (the first troll bought): in 216 games (0.991 of games); turn mean 23.49, median 9.0, p25-p75 1.0-36.0, min-max 1-146 (n=216); turn histogram (25-turn bins, start turn: n) {'1': 138, '26': 43, '51': 18, '76': 9, '101': 1, '126': 7}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 2 2 2 | 89 | 0.412 |
| 2 2 1 2 | 40 | 0.185 |
| 2 2 2 1 | 34 | 0.157 |
| 2 2 1 1 | 19 | 0.088 |
| 3 2 2 2 | 9 | 0.042 |
| 2 3 2 2 | 5 | 0.023 |
| 3 2 2 1 | 4 | 0.019 |
| 2 3 1 2 | 4 | 0.019 |

marginals: speed: {'2': 199, '3': 17}; carry: {'2': 198, '3': 18}; harvest: {'1': 72, '2': 144}; chop: {'1': 64, '2': 149, '3': 3}


**troll_3** (the second troll bought): in 186 games (0.853 of games); turn mean 103.77, median 100.5, p25-p75 76.75-126.0, min-max 43-185 (n=186); turn histogram (25-turn bins, start turn: n) {'26': 3, '51': 39, '76': 51, '101': 44, '126': 30, '151': 11, '176': 8}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 3 1 2 | 119 | 0.64 |
| 2 3 2 2 | 19 | 0.102 |
| 3 3 1 2 | 17 | 0.091 |
| 4 3 1 2 | 10 | 0.054 |
| 2 5 1 2 | 8 | 0.043 |
| 2 4 1 2 | 6 | 0.032 |
| 3 3 2 2 | 3 | 0.016 |
| 4 3 2 2 | 3 | 0.016 |

marginals: speed: {'2': 153, '3': 20, '4': 13}; carry: {'3': 171, '4': 7, '5': 8}; harvest: {'1': 160, '2': 26}; chop: {'2': 186}


**troll_4** (the third troll bought): in 113 games (0.518 of games); turn mean 132.07, median 132, p25-p75 107.5-153.0, min-max 76-183 (n=113); turn histogram (25-turn bins, start turn: n) {'76': 19, '101': 24, '126': 37, '151': 29, '176': 4}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 3 0 3 | 53 | 0.469 |
| 2 3 1 3 | 21 | 0.186 |
| 2 4 0 3 | 7 | 0.062 |
| 3 3 0 3 | 6 | 0.053 |
| 2 3 2 3 | 5 | 0.044 |
| 3 3 2 3 | 4 | 0.035 |
| 3 3 1 3 | 4 | 0.035 |
| 4 3 0 3 | 3 | 0.027 |

marginals: speed: {'2': 93, '3': 15, '4': 5}; carry: {'3': 98, '4': 12, '5': 3}; harvest: {'0': 71, '1': 31, '2': 11}; chop: {'3': 113}


**troll_5** (the 5th-1 troll bought): in 24 games (0.11 of games); turn mean 152.38, median 153.0, p25-p75 134.25-173.0, min-max 106-179 (n=24); turn histogram (25-turn bins, start turn: n) {'101': 3, '126': 9, '151': 8, '176': 4}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 4 0 3 | 14 | 0.583 |
| 2 4 1 3 | 3 | 0.125 |
| 3 4 0 3 | 3 | 0.125 |
| 4 4 0 3 | 1 | 0.042 |
| 2 5 0 3 | 1 | 0.042 |
| 2 4 2 3 | 1 | 0.042 |
| 3 4 2 3 | 1 | 0.042 |

marginals: speed: {'2': 19, '3': 4, '4': 1}; carry: {'4': 23, '5': 1}; harvest: {'0': 19, '1': 3, '2': 2}; chop: {'3': 24}


**troll_6** (the 6th-1 troll bought): in 1 games (0.005 of games); turn mean 156.0, median 156, p25-p75 156-156, min-max 156-156 (n=1); turn histogram (25-turn bins, start turn: n) {'151': 1}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 3 4 2 3 | 1 | 1.0 |

marginals: speed: {'3': 1}; carry: {'4': 1}; harvest: {'2': 1}; chop: {'3': 1}

Opponents' trained talents (for contrast):

| talents | n | share |
|---|---|---|
| 4 3 1 3 | 64 | 0.129 |
| 4 3 0 3 | 47 | 0.095 |
| 4 3 0 2 | 38 | 0.077 |
| 4 3 1 2 | 36 | 0.073 |
| 2 2 2 2 | 18 | 0.036 |
| 2 2 2 1 | 16 | 0.032 |

## 2. Opening (turns 1-30)

Letters: M=MOVE, H=HARVEST, C=CHOP, P=PLANT, K=PICK, D=DROP, I=MINE, T=TRAIN, W=WAIT, -=no command for that troll.

Starting troll, one letter per turn, turns 1-10 (most common patterns):

| pattern | n | share |
|---|---|---|
| MKPKMPMMMM | 22 | 0.101 |
| MKPMMMMMMM | 15 | 0.069 |
| MKPMMKPMMM | 12 | 0.055 |
| MKPMMMMMHM | 10 | 0.046 |
| MKPMMMMHMM | 8 | 0.037 |
| MMMMMMHMMM | 8 | 0.037 |
| MKPKMPMMMH | 8 | 0.037 |
| MKPKMPMKPM | 8 | 0.037 |
| MMMMMMMHMM | 6 | 0.028 |
| MMMMMHMMMM | 6 | 0.028 |
| MKPKMPMKMP | 6 | 0.028 |
| MKPKMPMKMM | 6 | 0.028 |

Starting troll, turns 1-20:

| pattern | n | share |
|---|---|---|
| MMMMMMMMMHMMMMMMMMDM | 3 | 0.014 |
| MMMMMMHMMMMMDMMMMMHM | 3 | 0.014 |
| MKPMMKPMMMMMMMMHMMMM | 2 | 0.009 |
| MKPMMHMPMHMMPMMHMPMH | 2 | 0.009 |
| MKPMMMMMHMMMMMDMMMMM | 2 | 0.009 |
| MMMMMHMMMMPMMMMHMMMP | 2 | 0.009 |
| MMMMMHMMMMDMMMMHMMMM | 2 | 0.009 |
| MKPKMPMMMMMMMMMHMMMM | 2 | 0.009 |

All trolls together, turns 1-10 (letters of one turn joined, turns separated by spaces):

| pattern | n | share |
|---|---|---|
| M K P M M M M M M M | 8 | 0.037 |
| M M M M M M H M M M | 7 | 0.032 |
| M K P M M M M M H M | 7 | 0.032 |
| M K P M M K P M M M | 6 | 0.028 |
| M M M M M H M M M M | 6 | 0.028 |
| M K P K M P M M M M | 5 | 0.023 |
| M K P K M P M K P M | 5 | 0.023 |
| M M M M M M M H M M | 4 | 0.018 |

First occurrences (turn of the first command of that kind; games with it):

| verb | games with it | turn |
|---|---|---|
| HARVEST | 218 | mean 9.09, median 8.0, p25-p75 5.0-11.0, min-max 2-37 (n=218) |
| PLANT | 216 | mean 8.55, median 3.0, p25-p75 3.0-5.0, min-max 3-265 (n=216) |
| CHOP | 218 | mean 80.39, median 86.0, p25-p75 15.0-130.0, min-max 5-194 (n=218) |
| TRAIN | 216 | mean 23.47, median 9.0, p25-p75 1.0-36.0, min-max 1-146 (n=216) |
| DROP | 218 | mean 22.11, median 17.0, p25-p75 11.0-25.0, min-max 3-119 (n=218) |
| MINE | 199 | mean 77.56, median 72, p25-p75 54.0-95.0, min-max 11-165 (n=199) |

first action verb of start troll:

| value | n | share |
|---|---|---|
| K | 156 | 0.716 |
| H | 62 | 0.284 |

first harvest type:

| value | n | share |
|---|---|---|
| PLUM | 88 | 0.404 |
| LEMON | 88 | 0.404 |
| APPLE | 37 | 0.17 |
| BANANA | 5 | 0.023 |

first harvest origin:

| value | n | share |
|---|---|---|
| wild | 213 | 0.977 |
| own | 5 | 0.023 |

first plant type:

| value | n | share |
|---|---|---|
| LEMON | 134 | 0.62 |
| PLUM | 74 | 0.343 |
| APPLE | 6 | 0.028 |
| BANANA | 2 | 0.009 |

first chop type:

| value | n | share |
|---|---|---|
| LEMON | 147 | 0.674 |
| BANANA | 41 | 0.188 |
| PLUM | 30 | 0.138 |

first chop origin:

| value | n | share |
|---|---|---|
| own | 87 | 0.399 |
| wild | 78 | 0.358 |
| opp | 53 | 0.243 |

Verb share by turn, turns 1-30 (commands per game, by letter):

| turn | M | H | C | P | K | D | I | T | W |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0 |  |  |  |  |  |  | 0.46 |  |
| 2 | 0.71 | 0.04 |  |  | 0.72 |  |  |  |  |
| 3 | 0.52 | 0.07 |  | 0.71 | 0.16 | 0.01 |  |  |  |
| 4 | 0.91 | 0.09 |  | 0.18 | 0.28 | 0.0 |  |  |  |
| 5 | 1.24 | 0.12 | 0.01 | 0.03 | 0.01 | 0.04 |  |  |  |
| 6 | 0.82 | 0.14 | 0.06 | 0.31 | 0.13 |  |  | 0.02 |  |
| 7 | 1.0 | 0.13 | 0.09 | 0.18 |  | 0.08 |  | 0.0 |  |
| 8 | 0.99 | 0.18 | 0.08 | 0.08 | 0.13 | 0.02 |  | 0.01 |  |
| 9 | 1.07 | 0.16 | 0.09 | 0.1 |  | 0.08 |  |  |  |
| 10 | 1.03 | 0.23 | 0.1 | 0.1 | 0.04 | 0.01 |  | 0.01 |  |
| 11 | 1.0 | 0.15 | 0.11 | 0.11 |  | 0.12 | 0.0 |  |  |
| 12 | 1.11 | 0.12 | 0.09 | 0.13 | 0.05 | 0.0 |  | 0.02 |  |
| 13 | 0.98 | 0.15 | 0.11 | 0.1 |  | 0.18 |  |  |  |
| 14 | 1.01 | 0.19 | 0.13 | 0.11 | 0.05 | 0.03 |  | 0.02 |  |
| 15 | 0.96 | 0.21 | 0.13 | 0.1 |  | 0.14 |  | 0.01 |  |
| 16 | 1.03 | 0.22 | 0.12 | 0.09 | 0.04 | 0.04 | 0.0 | 0.01 |  |
| 17 | 0.92 | 0.2 | 0.11 | 0.13 | 0.0 | 0.19 | 0.0 |  |  |
| 18 | 1.03 | 0.26 | 0.09 | 0.1 | 0.02 | 0.06 |  | 0.01 |  |
| 19 | 1.02 | 0.21 | 0.06 | 0.09 | 0.0 | 0.19 |  | 0.0 |  |
| 20 | 1.06 | 0.23 | 0.06 | 0.14 | 0.04 | 0.05 |  | 0.02 |  |
| 21 | 1.0 | 0.17 | 0.08 | 0.16 |  | 0.19 |  |  |  |
| 22 | 1.08 | 0.29 | 0.09 | 0.07 | 0.03 | 0.04 | 0.0 | 0.01 |  |
| 23 | 0.92 | 0.24 | 0.06 | 0.14 |  | 0.25 | 0.0 |  |  |
| 24 | 1.09 | 0.27 | 0.08 | 0.09 | 0.02 | 0.06 | 0.0 | 0.02 |  |
| 25 | 0.95 | 0.22 | 0.06 | 0.12 |  | 0.28 |  |  |  |
| 26 | 1.03 | 0.36 | 0.06 | 0.08 | 0.01 | 0.08 |  | 0.03 |  |
| 27 | 1.05 | 0.2 | 0.05 | 0.12 | 0.0 | 0.24 |  |  |  |
| 28 | 1.1 | 0.3 | 0.04 | 0.11 | 0.03 | 0.09 | 0.0 | 0.02 |  |
| 29 | 0.99 | 0.26 | 0.06 | 0.12 | 0.01 | 0.25 | 0.0 |  |  |
| 30 | 1.07 | 0.32 | 0.07 | 0.09 | 0.02 | 0.11 | 0.0 | 0.02 |  |

Most common MSG texts (digits replaced by N):

| message | n | share |
|---|---|---|
| DD N.N ms | 30661 | 0.477 |
| PP N.N ms | 26598 | 0.414 |
| DP N.N ms | 2886 | 0.045 |
| PD N.N ms | 1577 | 0.025 |
| TP N.N ms | 858 | 0.013 |
| PT N.N ms | 713 | 0.011 |
| TT N.N ms | 443 | 0.007 |
| DT N.N ms | 418 | 0.007 |
| TD N.N ms | 87 | 0.001 |

## 3. Planting

| measure | value |
|---|---|
| PLANT commands per game | mean 29.08, median 30.0, p25-p75 17.0-38.0, min-max 0-81 (n=218) |
| successful plants per game | mean 29.08, median 30.0, p25-p75 17.0-38.0, min-max 0-81 (n=218) |
| success rate of PLANT commands | 1.0 |
| distance (BFS over grass) from own shack | mean 1.73, median 1, p25-p75 1.0-2.0, min-max 1-4 (n=6339) |
| distance hist (cells: n; 12 = 12 or more) | {'1': 3634, '2': 1312, '3': 883, '4': 510} |
| distance from opponent shack | mean 11.66, median 12, p25-p75 9.0-14.0, min-max 3-27 (n=6339) |
| planted next to water | 0.226 |
| next to water, by type | {'PLUM': 0.254, 'LEMON': 0.233, 'APPLE': 0.427, 'BANANA': 0.132} |
| planted on own half of the map | 0.95 |
| planted nearer own shack than opponent's | 0.999 |
| plants per game by 10-turn bucket | {'1-10': 1.68, '11-20': 1.11, '21-30': 1.1, '31-40': 1.01, '41-50': 0.72, '51-60': 0.75, '61-70': 0.82, '71-80': 0.71, '81-90': 0.77, '91-100': 0.97, '101-110': 1.07, '111-120': 1.1, '121-130': 1.0, '131-140': 1.05, '141-150': 1.06, '151-160': 1.01, '161-170': 1.2, '171-180': 1.25, '181-190': 1.15, '191-200': 1.19, '201-210': 0.98, '211-220': 0.91, '221-230': 0.87, '231-240': 0.82, '241-250': 0.79, '251-260': 0.83, '261-270': 0.78, '271-280': 0.82, '281-290': 0.74, '291-300': 0.82} |

By type (successful plants):

| type | n | share |
|---|---|---|
| LEMON | 2239 | 0.353 |
| PLUM | 2018 | 0.318 |
| BANANA | 1667 | 0.263 |
| APPLE | 415 | 0.065 |

Seeds picked at the shack (PICK commands) by type:

| type | n | share |
|---|---|---|
| BANANA | 1319 | 0.444 |
| PLUM | 833 | 0.281 |
| LEMON | 707 | 0.238 |
| APPLE | 109 | 0.037 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA |
|---|---|---|---|---|
| early(1-100) | 0.389 | 0.493 | 0.034 | 0.084 |
| mid(101-200) | 0.248 | 0.285 | 0.046 | 0.421 |
| late(201-300) | 0.33 | 0.282 | 0.127 | 0.26 |

Distance from own shack by type: PLUM: mean 1.8, median 1.0, p25-p75 1.0-2.0, min-max 1-4 (n=2018); LEMON: mean 1.88, median 2, p25-p75 1.0-3.0, min-max 1-4 (n=2239); APPLE: mean 2.01, median 2, p25-p75 1.0-3.0, min-max 1-4 (n=415); BANANA: mean 1.36, median 1, p25-p75 1.0-1.0, min-max 1-4 (n=1667)

## 4. Harvesting

| measure | value |
|---|---|
| HARVEST commands per game | mean 78.18, median 71.0, p25-p75 54.75-96.0, min-max 18-209 (n=218) |
| fruits harvested per game (referee count) | mean 89.65, median 83.0, p25-p75 60.0-111.0, min-max 19-265 (n=218) |
| fruits per HARVEST command | 1.147 |
| HARVEST commands that took nothing | 0.0 |
| distance from own shack of the harvested cell | mean 2.29, median 2.0, p25-p75 1.0-3.0, min-max 1-19 (n=17044) |
| harvests per game by 10-turn bucket | {'1-10': 1.17, '11-20': 1.94, '21-30': 2.64, '31-40': 3.17, '41-50': 3.3, '51-60': 3.45, '61-70': 3.71, '71-80': 4.07, '81-90': 4.33, '91-100': 4.65, '101-110': 4.94, '111-120': 5.11, '121-130': 4.91, '131-140': 4.88, '141-150': 4.51, '151-160': 4.08, '161-170': 3.29, '171-180': 2.81, '181-190': 2.18, '191-200': 1.58, '201-210': 1.3, '211-220': 1.0, '221-230': 0.84, '231-240': 0.77, '241-250': 0.72, '251-260': 0.59, '261-270': 0.56, '271-280': 0.56, '281-290': 0.51, '291-300': 0.61} |

By the tree's origin (own-planted / wild / planted by the opponent):

| origin | n | share |
|---|---|---|
| own | 11798 | 0.692 |
| wild | 5051 | 0.296 |
| opp | 195 | 0.011 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.547 | 0.435 | 0.018 | 0 |
| mid(101-200) | 0.799 | 0.193 | 0.008 | 0 |
| late(201-300) | 0.771 | 0.228 | 0.001 | 0 |

Fruits harvested by type:

| type | n | share |
|---|---|---|
| LEMON | 8759 | 0.448 |
| PLUM | 6034 | 0.309 |
| APPLE | 3319 | 0.17 |
| BANANA | 1431 | 0.073 |

## 5. Chopping

| measure | value |
|---|---|
| CHOP commands per game | mean 189.21, median 191.0, p25-p75 155.0-226.0, min-max 50-302 (n=218) |
| chops that landed per game | mean 147.52, median 150.0, p25-p75 119.0-178.0, min-max 29-248 (n=218) |
| trees felled per game (this player struck the killing turn) | mean 0.66, median 0.0, p25-p75 0.0-1.0, min-max 0-8 (n=218) |
| wood collected per game | mean 79.91, median 81.0, p25-p75 61.0-99.0, min-max 14-173 (n=218) |
| turn of the first wood | mean 90.7, median 96.5, p25-p75 31.25-137.25, min-max 6-196 (n=218) |
| wood by phase (total over games) | {'early(1-100)': 366, 'mid(101-200)': 7694, 'late(201-300)': 9360} |
| chops per game by 10-turn bucket | {'1-10': 0.43, '11-20': 1.0, '21-30': 0.64, '31-40': 0.65, '41-50': 0.57, '51-60': 0.48, '61-70': 0.61, '71-80': 0.77, '81-90': 0.78, '91-100': 1.37, '101-110': 2.13, '111-120': 2.94, '121-130': 3.89, '131-140': 5.38, '141-150': 6.95, '151-160': 8.05, '161-170': 9.77, '171-180': 11.89, '181-190': 12.78, '191-200': 12.67, '201-210': 12.7, '211-220': 12.56, '221-230': 11.55, '231-240': 11.39, '241-250': 10.33, '251-260': 9.93, '261-270': 9.72, '271-280': 9.06, '281-290': 9.27, '291-300': 8.99} |
| chopped on own half of the map | 0.607 |
| distance from own shack | mean 5.56, median 3, p25-p75 1.0-9.0, min-max 1-31 (n=41247) |
| distance from opponent shack | mean 8.62, median 9, p25-p75 4.0-13.0, min-max 1-31 (n=41247) |

By the tree's origin:

| origin | n | share |
|---|---|---|
| own | 21562 | 0.523 |
| opp | 12457 | 0.302 |
| wild | 7228 | 0.175 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.149 | 0.273 | 0.578 | 0 |
| mid(101-200) | 0.645 | 0.14 | 0.215 | 0 |
| late(201-300) | 0.46 | 0.194 | 0.346 | 0 |

Nearer to whose shack (BFS distance):

| nearer | n | share |
|---|---|---|
| own | 25591 | 0.62 |
| opp | 15046 | 0.365 |
| equal | 610 | 0.015 |

Tree type at the time of the chop:

| type | n | share |
|---|---|---|
| PLUM | 15194 | 0.368 |
| LEMON | 13596 | 0.33 |
| APPLE | 6695 | 0.162 |
| BANANA | 5762 | 0.14 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA | ? |
|---|---|---|---|---|---|
| early(1-100) | 0.035 | 0.876 | 0.004 | 0.084 | 0 |
| mid(101-200) | 0.358 | 0.371 | 0.079 | 0.192 | 0 |
| late(201-300) | 0.399 | 0.262 | 0.233 | 0.106 | 0 |

Tree size at the chop:

| size | n | share |
|---|---|---|
| 1 | 26050 | 0.632 |
| 4 | 14004 | 0.34 |
| 2 | 624 | 0.015 |
| 3 | 569 | 0.014 |

Fruits on the tree at the chop:

| fruits | n | share |
|---|---|---|
| 0 | 32764 | 0.794 |
| 2 | 4558 | 0.111 |
| 1 | 3630 | 0.088 |
| 3 | 295 | 0.007 |

Chop power of the chopping troll:

| chop power | n | share |
|---|---|---|
| 2 | 19846 | 0.481 |
| 1 | 13534 | 0.328 |
| 3 | 7867 | 0.191 |

## 6. Mining

| measure | value |
|---|---|
| MINE commands per game | mean 7.95, median 8.0, p25-p75 2.0-13.0, min-max 0-24 (n=218) |
| iron collected per game | mean 12.24, median 14.0, p25-p75 4.0-18.0, min-max 0-44 (n=218) |
| games with at least one MINE | 199 |
| iron per MINE command | 1.539 |
| turn of the first MINE | mean 77.56, median 72, p25-p75 54.0-95.0, min-max 11-165 (n=199) |
| mines per game by 10-turn bucket | {'11-20': 0.01, '21-30': 0.03, '31-40': 0.08, '41-50': 0.23, '51-60': 0.44, '61-70': 0.52, '71-80': 0.61, '81-90': 0.93, '91-100': 0.83, '101-110': 0.64, '111-120': 0.69, '121-130': 0.89, '131-140': 0.64, '141-150': 0.55, '151-160': 0.5, '161-170': 0.31, '171-180': 0.05} |

## 7. Unit roles (verb mix per troll, in creation order)

| troll | games | commands per game | verb mix | talents (n) |
|---|---|---|---|---|
| start_troll | 218 | mean 294.68, median 300.0, p25-p75 300.0-300.0, min-max 202-300 (n=218) | MOVE 0.509, CHOP 0.165, DROP 0.129, HARVEST 0.122, PLANT 0.046, PICK 0.026, MINE 0.003 | 1 1 1 1 (218) |
| trained_1 | 216 | mean 271.14, median 280.0, p25-p75 254.25-299.0, min-max 154-299 (n=216) | MOVE 0.516, CHOP 0.211, DROP 0.107, HARVEST 0.101, PLANT 0.037, MINE 0.014, PICK 0.013 | 2 2 2 2 (89); 2 2 1 2 (40); 2 2 2 1 (34); 2 2 1 1 (19) |
| trained_2 | 186 | mean 190.0, median 193.5, p25-p75 171.75-215.25, min-max 115-256 (n=186) | MOVE 0.477, CHOP 0.301, DROP 0.091, HARVEST 0.082, PLANT 0.024, MINE 0.019, PICK 0.007 | 2 3 1 2 (119); 2 3 2 2 (19); 3 3 1 2 (17); 4 3 1 2 (10) |
| trained_3 | 113 | mean 159.88, median 160, p25-p75 138.0-176.0, min-max 102-213 (n=113) | MOVE 0.491, CHOP 0.358, DROP 0.096, HARVEST 0.02, PLANT 0.018, PICK 0.014, MINE 0.004 | 2 3 0 3 (53); 2 3 1 3 (21); 2 4 0 3 (7); 3 3 0 3 (6) |
| trained_4 | 24 | mean 137.58, median 131.0, p25-p75 123.0-160.0, min-max 87-180 (n=24) | MOVE 0.557, CHOP 0.353, DROP 0.078, PLANT 0.004, PICK 0.004, HARVEST 0.003, MINE 0.001 | 2 4 0 3 (14); 2 4 1 3 (3); 3 4 0 3 (3); 4 4 0 3 (1) |
| trained_5 | 1 | mean 144.0, median 144, p25-p75 144-144, min-max 144-144 (n=1) | MOVE 0.542, CHOP 0.389, DROP 0.069 | 3 4 2 3 (1) |

## 8. Endgame (last 30 turns)

| measure | value |
|---|---|
| verb mix, last 30 turns | {'MOVE': 0.59, 'CHOP': 0.286, 'DROP': 0.065, 'PLANT': 0.024, 'PICK': 0.019, 'HARVEST': 0.016} |
| verb mix, whole game | {'MOVE': 0.503, 'CHOP': 0.229, 'DROP': 0.11, 'HARVEST': 0.095, 'PLANT': 0.035, 'PICK': 0.016, 'MINE': 0.01, 'TRAIN': 0.003} |
| commands per game in the last 30 turns | 104.3 |
| per game in the last 30 turns | {'plants': 2.51, 'chops': 29.86, 'harvests': 1.71, 'drops': 6.76, 'wood': 11.49} |
| turn of the last DROP | mean 291.11, median 297.0, p25-p75 293.0-299.0, min-max 194-300 (n=218) |
| turns from the last DROP to the end | mean 3.57, median 2.0, p25-p75 1.0-6.0, min-max 0-29 (n=218) |
| trees alive at the end per game (own / wild / opp) | {'own': 1.38, 'wild': 3.04, 'opp': 2.03} |
| games ending with no tree on the map | 48 |

Commands per game by verb: {"MOVE": 415.4, "CHOP": 189.2, "DROP": 90.7, "HARVEST": 78.2, "PLANT": 29.1, "PICK": 13.6, "MINE": 8.0, "TRAIN": 2.5}

Commands per game by 10-turn bucket:

| turns | MOVE | HARVEST | CHOP | PLANT | PICK | DROP | MINE | TRAIN | WAIT |
|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 9.29 | 1.17 | 0.43 | 1.68 | 1.47 | 0.24 |  | 0.51 |  |
| 11-20 | 10.12 | 1.94 | 1.0 | 1.11 | 0.2 | 1.0 | 0.01 | 0.11 |  |
| 21-30 | 10.27 | 2.64 | 0.64 | 1.1 | 0.13 | 1.58 | 0.03 | 0.11 |  |
| 31-40 | 10.39 | 3.17 | 0.65 | 1.01 | 0.1 | 2.04 | 0.08 | 0.07 |  |
| 41-50 | 10.58 | 3.3 | 0.57 | 0.72 | 0.1 | 2.57 | 0.23 | 0.06 |  |
| 51-60 | 10.79 | 3.45 | 0.48 | 0.75 | 0.12 | 2.8 | 0.44 | 0.11 |  |
| 61-70 | 11.26 | 3.71 | 0.61 | 0.82 | 0.06 | 2.98 | 0.52 | 0.1 |  |
| 71-80 | 11.56 | 4.07 | 0.77 | 0.71 | 0.07 | 3.24 | 0.61 | 0.14 |  |
| 81-90 | 11.77 | 4.33 | 0.78 | 0.77 | 0.17 | 3.62 | 0.93 | 0.15 |  |
| 91-100 | 11.97 | 4.65 | 1.37 | 0.97 | 0.27 | 3.85 | 0.83 | 0.13 |  |
| 101-110 | 12.28 | 4.94 | 2.13 | 1.07 | 0.29 | 4.11 | 0.64 | 0.17 |  |
| 111-120 | 12.42 | 5.11 | 2.94 | 1.1 | 0.28 | 4.34 | 0.69 | 0.11 |  |
| 121-130 | 12.61 | 4.91 | 3.89 | 1.0 | 0.34 | 4.47 | 0.89 | 0.17 |  |
| 131-140 | 12.66 | 4.88 | 5.38 | 1.05 | 0.42 | 4.79 | 0.64 | 0.16 |  |
| 141-150 | 13.16 | 4.51 | 6.95 | 1.06 | 0.38 | 4.5 | 0.55 | 0.1 |  |
| 151-160 | 13.59 | 4.08 | 8.05 | 1.01 | 0.42 | 4.51 | 0.5 | 0.08 |  |
| 161-170 | 13.64 | 3.29 | 9.77 | 1.2 | 0.54 | 4.25 | 0.31 | 0.08 |  |
| 171-180 | 13.36 | 2.81 | 11.89 | 1.25 | 0.61 | 4.0 | 0.05 | 0.11 |  |
| 181-190 | 13.76 | 2.18 | 12.78 | 1.15 | 0.75 | 4.08 |  | 0.03 |  |
| 191-200 | 15.17 | 1.58 | 12.67 | 1.19 | 0.71 | 3.45 |  |  |  |
| 201-210 | 15.73 | 1.3 | 12.7 | 0.98 | 0.64 | 3.18 |  |  |  |
| 211-220 | 16.22 | 1.0 | 12.56 | 0.91 | 0.68 | 2.99 |  |  |  |
| 221-230 | 17.84 | 0.84 | 11.55 | 0.87 | 0.64 | 2.62 |  |  |  |
| 231-240 | 18.06 | 0.77 | 11.39 | 0.82 | 0.63 | 2.57 |  |  |  |
| 241-250 | 18.87 | 0.72 | 10.33 | 0.79 | 0.61 | 2.41 |  |  |  |
| 251-260 | 18.97 | 0.59 | 9.93 | 0.83 | 0.58 | 2.22 |  |  |  |
| 261-270 | 18.17 | 0.56 | 9.72 | 0.78 | 0.62 | 2.11 |  |  |  |
| 271-280 | 17.73 | 0.56 | 9.06 | 0.82 | 0.6 | 2.22 |  |  |  |
| 281-290 | 17.05 | 0.51 | 9.27 | 0.74 | 0.63 | 1.89 |  |  |  |
| 291-300 | 16.16 | 0.61 | 8.99 | 0.82 | 0.56 | 2.0 |  |  |  |

DROP: mean 90.65, median 88.0, p25-p75 71.0-107.0, min-max 33-212 (n=218) commands per game; items per drop mean 1.81, median 2.0, p25-p75 1.0-2.0, min-max 1-5 (n=19762)

Referee-reported failures per game: {"move_blocked": 0.1, "pick_out_of_stock": 0.09, "train_unaffordable": 0.02}

## 10. Movement

| measure | value |
|---|---|
| MOVE commands per game | mean 415.44, median 414.0, p25-p75 321.5-507.5, min-max 102-735 (n=218) |
| BFS distance from the troll's cell to the MOVE target | mean 1.55, median 2, p25-p75 1.0-2.0, min-max 0-4 (n=90567) |
| distance histogram (15 = 15 or more) | {'0': 2920, '1': 41288, '2': 41262, '3': 4223, '4': 874} |
| turns needed to arrive (distance / speed, rounded up) | mean 0.97, median 1, p25-p75 1.0-1.0, min-max 0-1 (n=90567) |
| target unreachable (water, rock, a shack cell) | 0.0 |
| target = the troll's current cell | 0.032 |

What the MOVE target is:

| target | n | share |
|---|---|---|
| other_grass | 44808 | 0.495 |
| tree_own | 19020 | 0.21 |
| own_shack_adjacent | 8558 | 0.094 |
| tree_wild | 7808 | 0.086 |
| tree_opp | 5221 | 0.058 |
| iron_adjacent | 3800 | 0.042 |
| opp_shack_adjacent | 1352 | 0.015 |

## What the corpus cannot tell

- Why a decision was taken: no bot state, no evaluation, no stderr. Only commands and the referee's outcomes are recorded.
- A troll's carried inventory between DROPs (the viewer shows one item at a time); carry is inferred only through referee events.
- Whether a MOVE was re-targeted before arrival is visible, but the intended destination of a multi-turn walk is not.
- Tree fruit counts and cooldowns are followed through the viewer diff (stage = size + fruits); the stage shown at a chop is the state after that turn's tick.
- Games of this agent id only; earlier or later versions of the same player's bot may differ.
