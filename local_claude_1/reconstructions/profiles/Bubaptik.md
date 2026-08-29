# Behaviour profile: Bubaptik (agent ids 6568138; 191 games)

## Summary (plain words)

Bubaptik (Legend #3 at 19:50Z; this profile = agent 6568138, its most-played and most recent id, 191 games; Bubaptik resubmits constantly — 34 agent ids and 3,917 game lines in the corpus, listed in the Notes below; win rate 0.654, mean score 295 against 310: it out-scores weaker opponents and loses on score to the strongest — 32 % wins against opponents rated 28 or more).

1. Second troll on turn 2 in 89 % of games (median turn 2), with mixed talents (harvest 2-3 in 66 %, chop 2 in 54 %, 2 2 2 2 the single most common at 9 %) — whatever the starting stock affords.
2. The only top bot that buys SPEED 4: troll 3 (81 % of games, median turn 118) is a speed-4 carry-3 runner (4 3 0 2 in 34 %, 4 3 1 2 in 31 %); troll 4 (45 %, turn 153) is 4 3 1 3 in 38 %. Carry 3 in 100 % of its later trolls.
3. Destination-style MOVE commands: the target is the real destination (mean 2.9 cells away, up to 29), so its intentions are readable in the corpus; 23 % of MOVE targets are its own shack cell (the referee parks the troll next to it), which produces 26.6 "can't move, target blocked" referee failures per game — harmless.
4. A plum farmer: plants plum 47 %, lemon 30 %, banana 21 % (first plant is a plum in 64 % of games); plums are 52 % of the fruit it harvests and 42 % of the trees it chops.
5. Plants farther out than the others (mean 2.4 cells from the shack, 12 % beyond 4 cells, up to 15) but 99 % on its own half; 23 % next to water.
6. Chops the least of the four (136 CHOP commands, 69 wood per game) and with chop-power 2 for 53 % of chops; 57 % of chopped trees are size 1, 40 % size 4.
7. Early chopping is denial: in turns 1-100, 50 % of its chops hit opponent-planted trees and 41 % wild ones; in turns 201-300, 70 % are its own trees. First wood at median turn 24.
8. Mines in 92 % of games (8.3 MINE commands, 12 iron), mostly turns 60-130.
9. Opening: the start troll does move, move, pick, plant, pick, move, plant (a plum or lemon 1-2 cells from the shack) while the second troll is bought on turn 2 and walks to a wild tree; 3.9 WAIT commands per game (the only top bot that waits).
10. Wins 74 % against 2-troll opponents, 57 % against 4, 33 % against 5+; with its own fourth troll 70 %.

## How to read this

Every table is measured over this player's games in the corpus (`n` = the number of games or events behind the row). Positions and effects come from the referee's own per-turn log inside each replay (exact troll positions after every move, which tree was planted/damaged/harvested), so 'own-planted / wild / opponent-planted' and 'tree type at the time of the chop' are exact for games read from a raw replay. For a game read from `turns.jsonl.gz` only (no raw replay), positions are simulated from MOVE targets and marked approximate. Position source for this profile: {"raw_replay_exact_positions": 191}.

Notes: Pseudo Bubaptik appears under 34 agent ids in games.jsonl (id: games) {6568138: 191, 6567616: 155, 6568015: 155, 6567772: 154, 6565556: 152, 6567813: 152, 6567856: 152, 6568033: 150, 6567909: 146, 6568097: 145, 6567667: 139, 6542619: 136, 6567585: 129, 6563637: 123, 6566707: 122, 6555848: 120, 6565849: 118, 6565634: 117, 6565903: 116, 6563190: 109, 6566509: 106, 6557104: 104, 6565503: 102, 6563484: 100, 6555862: 99, 6563744: 96, 6565764: 93, 6565654: 90, 6542586: 85, 6565274: 85, 6542512: 64, 6542560: 63, 6542200: 48, 6529176: 1}; this profile uses [6568138].

## 9. Results and score composition

| measure | value |
|---|---|
| games | 191 |
| win rate | 0.654 |
| seat 0 games | 97 |
| final score | mean 295.44, median 290.0, p25-p75 201.0-376.0, min-max 41.0-670.0 (n=191) |
| opponent final score | mean 309.65, median 276.0, p25-p75 201.0-400.0, min-max 10.0-874.0 (n=191) |
| score margin | mean -14.21, median 29.0, p25-p75 -50.0-54.0, min-max -712.0-126.0 (n=191) |
| fruit points (banked fruit) | mean 27.1, median 24, p25-p75 15.0-34.0, min-max 0-93 (n=191) |
| wood points (4 x banked wood) | mean 268.34, median 260, p25-p75 180.0-356.0, min-max 16-624 (n=191) |
| wood share of all points | 0.908 |
| final inventory mean (plum, lemon, apple, banana, iron, wood) | [12.71, 7.3, 3.12, 3.97, 1.92, 67.08] |
| games ending before turn 300 | 9 |
| turns per game | mean 298.3, median 300, p25-p75 300.0-300.0, min-max 189-300 (n=191) |
| timeout strikes (total) | 0 |

By the opponent's troll count at the end:

| opponent trolls | n | win rate | mean score | mean opp score |
|---|---|---|---|---|
| 2 | 90 | 0.744 | 227.0 | 219.7 |
| 3 | 49 | 0.612 | 306.1 | 315.2 |
| 4 | 46 | 0.565 | 396.3 | 446.6 |
| 5+ | 6 | 0.333 | 461.0 | 563.7 |

By own troll count at the end:

| own trolls | n | win rate | mean score |
|---|---|---|---|
| 2 | 37 | 0.432 | 175.8 |
| 3 | 68 | 0.75 | 261.3 |
| 4 | 76 | 0.697 | 359.9 |
| 5+ | 10 | 0.5 | 480.4 |

By the opponent's arena score (their ladder rating in the corpus record):

| opponent arena score | n | win rate | mean score |
|---|---|---|---|
| 20-25 | 65 | 0.862 | 311.4 |
| 25-28 | 74 | 0.635 | 273.4 |
| <20 | 15 | 0.667 | 313.0 |
| >=28 | 37 | 0.324 | 304.3 |

Most frequent opponents:

| opponent | n | share |
|---|---|---|
| Stounate | 18 | 0.094 |
| gaha | 16 | 0.084 |
| tass | 15 | 0.079 |
| MSz | 13 | 0.068 |
| norxondor_gorgonax | 12 | 0.063 |
| delineate | 12 | 0.063 |
| yaichi | 11 | 0.058 |
| skotz | 8 | 0.042 |
| viewlagoon | 7 | 0.037 |
| laconic_pixel | 7 | 0.037 |
| wala | 6 | 0.031 |
| Escdemon | 4 | 0.021 |

## 1. Training ladder (TRAIN = buy a new troll; talents = speed carry harvest chop)

| measure | value |
|---|---|
| TRAIN commands total / failed | 447 / 6 |
| trolls at the end | mean 3.31, median 3, p25-p75 3.0-4.0, min-max 2-5 (n=191) |
| trolls trained per game | 1: 37 games (0.194), 2: 68 games (0.356), 3: 76 games (0.398), 4: 10 games (0.052) |

**troll_2** (the first troll bought): in 191 games (1.0 of games); turn mean 7.97, median 2, p25-p75 2.0-2.0, min-max 2-72 (n=191); turn histogram (25-turn bins, start turn: n) {'1': 170, '26': 11, '51': 10}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 2 2 2 | 18 | 0.094 |
| 2 2 1 2 | 16 | 0.084 |
| 2 2 2 1 | 14 | 0.073 |
| 1 2 2 2 | 14 | 0.073 |
| 2 1 2 2 | 9 | 0.047 |
| 2 2 1 1 | 8 | 0.042 |
| 2 3 1 1 | 7 | 0.037 |
| 1 2 1 2 | 7 | 0.037 |

marginals: speed: {'1': 46, '2': 123, '3': 22}; carry: {'1': 37, '2': 126, '3': 28}; harvest: {'0': 1, '1': 63, '2': 98, '3': 29}; chop: {'1': 62, '2': 104, '3': 25}


**troll_3** (the second troll bought): in 154 games (0.806 of games); turn mean 121.65, median 118.0, p25-p75 90.0-148.0, min-max 42-290 (n=154); turn histogram (25-turn bins, start turn: n) {'26': 3, '51': 12, '76': 37, '101': 36, '126': 31, '151': 25, '176': 5, '201': 2, '226': 2, '276': 1}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 4 3 0 2 | 52 | 0.338 |
| 4 3 1 2 | 48 | 0.312 |
| 4 3 1 3 | 13 | 0.084 |
| 4 3 0 3 | 11 | 0.071 |
| 1 3 1 3 | 9 | 0.058 |
| 1 3 1 2 | 4 | 0.026 |
| 1 3 0 2 | 4 | 0.026 |
| 1 3 0 3 | 3 | 0.019 |

marginals: speed: {'1': 26, '4': 128}; carry: {'3': 154}; harvest: {'0': 70, '1': 74, '2': 5, '3': 5}; chop: {'2': 114, '3': 40}


**troll_4** (the third troll bought): in 86 games (0.45 of games); turn mean 158.65, median 153.0, p25-p75 136.0-184.25, min-max 95-242 (n=86); turn histogram (25-turn bins, start turn: n) {'76': 3, '101': 9, '126': 27, '151': 22, '176': 15, '201': 8, '226': 2}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 4 3 1 3 | 33 | 0.384 |
| 4 3 0 3 | 17 | 0.198 |
| 4 3 1 2 | 9 | 0.105 |
| 1 3 0 3 | 8 | 0.093 |
| 1 3 1 3 | 7 | 0.081 |
| 4 3 0 2 | 5 | 0.058 |
| 1 3 1 2 | 2 | 0.023 |
| 1 3 2 2 | 2 | 0.023 |

marginals: speed: {'1': 20, '4': 66}; carry: {'3': 86}; harvest: {'0': 30, '1': 51, '2': 5}; chop: {'2': 19, '3': 67}


**troll_5** (the 5th-1 troll bought): in 10 games (0.052 of games); turn mean 169.5, median 164.0, p25-p75 145.25-195.5, min-max 130-223 (n=10); turn histogram (25-turn bins, start turn: n) {'126': 3, '151': 4, '176': 1, '201': 2}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 4 3 0 3 | 5 | 0.5 |
| 4 3 1 3 | 4 | 0.4 |
| 1 3 1 3 | 1 | 0.1 |

marginals: speed: {'1': 1, '4': 9}; carry: {'3': 10}; harvest: {'0': 5, '1': 5}; chop: {'3': 10}

Opponents' trained talents (for contrast):

| talents | n | share |
|---|---|---|
| 2 2 0 2 | 43 | 0.123 |
| 2 2 2 1 | 36 | 0.103 |
| 3 4 1 3 | 28 | 0.08 |
| 2 3 1 2 | 19 | 0.054 |
| 2 4 0 3 | 15 | 0.043 |
| 2 2 2 2 | 15 | 0.043 |

## 2. Opening (turns 1-30)

Letters: M=MOVE, H=HARVEST, C=CHOP, P=PLANT, K=PICK, D=DROP, I=MINE, T=TRAIN, W=WAIT, -=no command for that troll.

Starting troll, one letter per turn, turns 1-10 (most common patterns):

| pattern | n | share |
|---|---|---|
| MMKPKMPMMM | 19 | 0.099 |
| MMKPKMPMKP | 16 | 0.084 |
| MMKPKMPMKM | 12 | 0.063 |
| MMKPMMMMMM | 9 | 0.047 |
| MMKPKMPMMH | 8 | 0.042 |
| MKPKMPMKPM | 5 | 0.026 |
| MMKPMMHMPM | 5 | 0.026 |
| MMKPMMMHMP | 5 | 0.026 |
| MMKPKMPMHM | 4 | 0.021 |
| MKPMMMMMMM | 4 | 0.021 |
| MMKPKMMPKM | 3 | 0.016 |
| MKPKMMPKMP | 3 | 0.016 |

Starting troll, turns 1-20:

| pattern | n | share |
|---|---|---|
| MMKPKMPMMMMMMMMMMMMM | 3 | 0.016 |
| MMKPKMPMMMMMHMPMHMPM | 2 | 0.01 |
| MMKPKMPMKPMMMMMMMMMM | 2 | 0.01 |
| MMKPKMPMMHMPMHMPMHMM | 2 | 0.01 |
| MKPKMPMKPMMKMMDHDKDH | 1 | 0.005 |
| MHDHDHDHDKMPMHDHDHDH | 1 | 0.005 |
| MKPMMMMHMMPMMHMMPMMH | 1 | 0.005 |
| MMKPMMMMMMMMMMHMPMHM | 1 | 0.005 |

All trolls together, turns 1-10 (letters of one turn joined, turns separated by spaces):

| pattern | n | share |
|---|---|---|
| M MT KM MP KM MM MP MM MM MM | 6 | 0.031 |
| M MT KM MP KM MM MP MM CM CM | 6 | 0.031 |
| M MT KM MP MM MM MM MM MM MM | 4 | 0.021 |
| M K P K M P M K P M | 3 | 0.016 |
| M MT KM MP KM MM MP MM CK CP | 3 | 0.016 |
| M MT KM KP KP MM MP MM KM MP | 3 | 0.016 |
| M MT KM MP KM MM MP MM KM MM | 3 | 0.016 |
| M MT KM MP KM MM MP MM KM MP | 3 | 0.016 |

First occurrences (turn of the first command of that kind; games with it):

| verb | games with it | turn |
|---|---|---|
| HARVEST | 191 | mean 11.03, median 9, p25-p75 6.0-15.0, min-max 2-71 (n=191) |
| PLANT | 191 | mean 5.1, median 4, p25-p75 4.0-5.0, min-max 3-27 (n=191) |
| CHOP | 191 | mean 41.47, median 14, p25-p75 9.0-66.0, min-max 5-186 (n=191) |
| MINE | 176 | mean 56.87, median 55.5, p25-p75 26.0-79.75, min-max 2-207 (n=176) |
| TRAIN | 191 | mean 6.52, median 2, p25-p75 2.0-2.0, min-max 2-72 (n=191) |
| DROP | 191 | mean 19.42, median 17, p25-p75 10.0-27.0, min-max 3-67 (n=191) |

first action verb of start troll:

| value | n | share |
|---|---|---|
| K | 142 | 0.743 |
| H | 46 | 0.241 |
| I | 3 | 0.016 |

first harvest type:

| value | n | share |
|---|---|---|
| LEMON | 88 | 0.461 |
| PLUM | 84 | 0.44 |
| BANANA | 12 | 0.063 |
| APPLE | 7 | 0.037 |

first harvest origin:

| value | n | share |
|---|---|---|
| wild | 174 | 0.911 |
| own | 17 | 0.089 |

first plant type:

| value | n | share |
|---|---|---|
| PLUM | 123 | 0.644 |
| LEMON | 65 | 0.34 |
| BANANA | 3 | 0.016 |

first chop type:

| value | n | share |
|---|---|---|
| LEMON | 81 | 0.424 |
| PLUM | 72 | 0.377 |
| BANANA | 37 | 0.194 |
| APPLE | 1 | 0.005 |

first chop origin:

| value | n | share |
|---|---|---|
| wild | 120 | 0.628 |
| opp | 38 | 0.199 |
| own | 33 | 0.173 |

Verb share by turn, turns 1-30 (commands per game, by letter):

| turn | M | H | C | P | K | D | I | T | W |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0 |  |  |  |  |  |  |  |  |
| 2 | 0.69 | 0.1 |  |  | 0.19 |  | 0.02 | 0.83 |  |
| 3 | 0.9 | 0.08 |  | 0.19 | 0.55 | 0.08 |  |  |  |
| 4 | 0.83 | 0.11 |  | 0.55 | 0.3 | 0.01 | 0.01 | 0.02 |  |
| 5 | 1.07 | 0.03 | 0.02 | 0.22 | 0.38 | 0.08 | 0.01 |  |  |
| 6 | 1.36 | 0.15 | 0.08 | 0.16 | 0.04 | 0.02 | 0.02 | 0.01 |  |
| 7 | 0.99 | 0.15 | 0.16 | 0.38 | 0.02 | 0.1 | 0.03 |  |  |
| 8 | 1.2 | 0.15 | 0.23 | 0.11 | 0.09 | 0.03 | 0.02 | 0.01 |  |
| 9 | 0.94 | 0.14 | 0.29 | 0.17 | 0.19 | 0.09 | 0.03 |  |  |
| 10 | 1.03 | 0.16 | 0.28 | 0.21 | 0.07 | 0.07 | 0.02 | 0.01 |  |
| 11 | 1.05 | 0.14 | 0.31 | 0.18 | 0.05 | 0.09 | 0.03 |  |  |
| 12 | 1.07 | 0.19 | 0.31 | 0.14 | 0.05 | 0.05 | 0.04 | 0.01 |  |
| 13 | 1.07 | 0.16 | 0.35 | 0.07 | 0.04 | 0.15 | 0.02 |  |  |
| 14 | 1.05 | 0.2 | 0.37 | 0.16 | 0.03 | 0.06 | 0.01 | 0.01 |  |
| 15 | 1.02 | 0.18 | 0.35 | 0.11 | 0.06 | 0.12 | 0.04 |  |  |
| 16 | 1.06 | 0.18 | 0.37 | 0.12 | 0.02 | 0.1 | 0.04 |  |  |
| 17 | 0.93 | 0.26 | 0.34 | 0.14 | 0.03 | 0.16 | 0.02 |  |  |
| 18 | 1.02 | 0.21 | 0.35 | 0.12 | 0.02 | 0.13 | 0.02 |  |  |
| 19 | 1.03 | 0.22 | 0.32 | 0.14 | 0.02 | 0.1 | 0.03 |  |  |
| 20 | 1.03 | 0.21 | 0.35 | 0.11 | 0.01 | 0.13 | 0.04 | 0.01 |  |
| 21 | 1.0 | 0.2 | 0.35 | 0.13 | 0.03 | 0.16 | 0.01 |  |  |
| 22 | 0.9 | 0.28 | 0.38 | 0.13 | 0.01 | 0.17 | 0.02 | 0.01 |  |
| 23 | 0.91 | 0.22 | 0.35 | 0.12 | 0.04 | 0.21 | 0.04 |  |  |
| 24 | 1.04 | 0.21 | 0.36 | 0.09 | 0.02 | 0.13 | 0.03 | 0.01 |  |
| 25 | 0.98 | 0.21 | 0.35 | 0.1 | 0.03 | 0.19 | 0.03 |  |  |
| 26 | 1.04 | 0.21 | 0.29 | 0.1 | 0.01 | 0.18 | 0.06 | 0.01 |  |
| 27 | 0.89 | 0.34 | 0.3 | 0.1 | 0.03 | 0.2 | 0.03 |  |  |
| 28 | 1.02 | 0.27 | 0.31 | 0.09 | 0.01 | 0.18 | 0.02 | 0.01 |  |
| 29 | 0.92 | 0.27 | 0.29 | 0.12 | 0.03 | 0.26 | 0.03 |  |  |
| 30 | 1.0 | 0.23 | 0.32 | 0.08 | 0.01 | 0.2 | 0.05 | 0.01 |  |

Most common MSG texts (digits replaced by N):

| message | n | share |
|---|---|---|

## 3. Planting

| measure | value |
|---|---|
| PLANT commands per game | mean 28.76, median 28, p25-p75 21.0-36.0, min-max 5-65 (n=191) |
| successful plants per game | mean 28.76, median 28, p25-p75 21.0-36.0, min-max 5-65 (n=191) |
| success rate of PLANT commands | 1.0 |
| distance (BFS over grass) from own shack | mean 2.41, median 2, p25-p75 1.0-3.0, min-max 1-15 (n=5493) |
| distance hist (cells: n; 12 = 12 or more) | {'1': 2349, '2': 1346, '3': 713, '4': 407, '5': 266, '6': 152, '7': 90, '8': 78, '9': 34, '10': 22, '11': 17, '12': 19} |
| distance from opponent shack | mean 11.09, median 11, p25-p75 8.0-14.0, min-max 1-24 (n=5493) |
| planted next to water | 0.232 |
| next to water, by type | {'PLUM': 0.212, 'LEMON': 0.265, 'APPLE': 0.237, 'BANANA': 0.232} |
| planted on own half of the map | 0.988 |
| planted nearer own shack than opponent's | 0.985 |
| plants per game by 10-turn bucket | {'1-10': 1.99, '11-20': 1.27, '21-30': 1.04, '31-40': 0.7, '41-50': 0.78, '51-60': 0.64, '61-70': 0.63, '71-80': 0.49, '81-90': 0.45, '91-100': 0.52, '101-110': 0.49, '111-120': 0.52, '121-130': 0.55, '131-140': 0.73, '141-150': 0.88, '151-160': 0.95, '161-170': 1.21, '171-180': 1.36, '181-190': 1.29, '191-200': 1.3, '201-210': 1.37, '211-220': 1.26, '221-230': 1.17, '231-240': 1.03, '241-250': 0.98, '251-260': 1.16, '261-270': 1.03, '271-280': 0.98, '281-290': 1.01, '291-300': 0.97} |

By type (successful plants):

| type | n | share |
|---|---|---|
| PLUM | 2582 | 0.47 |
| LEMON | 1618 | 0.295 |
| BANANA | 1162 | 0.212 |
| APPLE | 131 | 0.024 |

Seeds picked at the shack (PICK commands) by type:

| type | n | share |
|---|---|---|
| PLUM | 911 | 0.394 |
| BANANA | 906 | 0.392 |
| LEMON | 417 | 0.18 |
| APPLE | 79 | 0.034 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA |
|---|---|---|---|---|
| early(1-100) | 0.511 | 0.445 | 0.012 | 0.031 |
| mid(101-200) | 0.461 | 0.297 | 0.028 | 0.213 |
| late(201-300) | 0.446 | 0.175 | 0.029 | 0.35 |

Distance from own shack by type: PLUM: mean 2.41, median 2.0, p25-p75 1.0-3.0, min-max 1-15 (n=2582); LEMON: mean 2.93, median 2.0, p25-p75 1.0-4.0, min-max 1-13 (n=1618); APPLE: mean 1.91, median 1, p25-p75 1.0-1.0, min-max 1-14 (n=131); BANANA: mean 1.75, median 1.0, p25-p75 1.0-2.0, min-max 1-12 (n=1162)

## 4. Harvesting

| measure | value |
|---|---|
| HARVEST commands per game | mean 78.07, median 74, p25-p75 59.0-92.0, min-max 13-176 (n=191) |
| fruits harvested per game (referee count) | mean 86.41, median 82, p25-p75 65.0-104.0, min-max 13-176 (n=191) |
| fruits per HARVEST command | 1.107 |
| HARVEST commands that took nothing | 0.0 |
| distance from own shack of the harvested cell | mean 2.32, median 2, p25-p75 1.0-3.0, min-max 1-23 (n=14911) |
| harvests per game by 10-turn bucket | {'1-10': 1.06, '11-20': 1.94, '21-30': 2.45, '31-40': 2.79, '41-50': 3.32, '51-60': 3.47, '61-70': 3.98, '71-80': 3.73, '81-90': 3.97, '91-100': 3.93, '101-110': 4.09, '111-120': 4.08, '121-130': 3.99, '131-140': 4.05, '141-150': 3.94, '151-160': 3.69, '161-170': 3.22, '171-180': 2.87, '181-190': 2.53, '191-200': 2.3, '201-210': 2.12, '211-220': 1.64, '221-230': 1.67, '231-240': 1.29, '241-250': 1.17, '251-260': 1.08, '261-270': 1.08, '271-280': 0.96, '281-290': 0.84, '291-300': 0.79} |

By the tree's origin (own-planted / wild / planted by the opponent):

| origin | n | share |
|---|---|---|
| own | 10689 | 0.717 |
| wild | 4069 | 0.273 |
| opp | 153 | 0.01 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.613 | 0.379 | 0.008 | 0 |
| mid(101-200) | 0.766 | 0.22 | 0.014 | 0 |
| late(201-300) | 0.832 | 0.162 | 0.006 | 0 |

Fruits harvested by type:

| type | n | share |
|---|---|---|
| PLUM | 8652 | 0.524 |
| LEMON | 5737 | 0.348 |
| APPLE | 1289 | 0.078 |
| BANANA | 827 | 0.05 |

## 5. Chopping

| measure | value |
|---|---|
| CHOP commands per game | mean 136.38, median 134, p25-p75 110.0-170.0, min-max 6-255 (n=191) |
| chops that landed per game | mean 103.16, median 102, p25-p75 82.0-130.0, min-max 3-195 (n=191) |
| trees felled per game (this player struck the killing turn) | mean 3.68, median 1, p25-p75 0.0-6.0, min-max 0-28 (n=191) |
| wood collected per game | mean 68.85, median 67, p25-p75 48.0-91.0, min-max 4-160 (n=191) |
| turn of the first wood | mean 53.64, median 24, p25-p75 13.0-95.0, min-max 6-187 (n=191) |
| wood by phase (total over games) | {'early(1-100)': 673, 'mid(101-200)': 4861, 'late(201-300)': 7616} |
| chops per game by 10-turn bucket | {'1-10': 1.06, '11-20': 3.41, '21-30': 3.29, '31-40': 2.65, '41-50': 2.1, '51-60': 1.69, '61-70': 1.53, '71-80': 1.48, '81-90': 1.43, '91-100': 1.51, '101-110': 1.51, '111-120': 1.79, '121-130': 2.35, '131-140': 3.09, '141-150': 3.72, '151-160': 4.96, '161-170': 5.98, '171-180': 6.36, '181-190': 7.03, '191-200': 7.07, '201-210': 7.31, '211-220': 7.99, '221-230': 7.32, '231-240': 7.66, '241-250': 7.53, '251-260': 7.19, '261-270': 7.22, '271-280': 6.77, '281-290': 6.71, '291-300': 6.64} |
| chopped on own half of the map | 0.668 |
| distance from own shack | mean 5.28, median 4.0, p25-p75 2.0-8.0, min-max 1-28 (n=26048) |
| distance from opponent shack | mean 8.42, median 9.0, p25-p75 3.0-13.0, min-max 1-25 (n=26048) |

By the tree's origin:

| origin | n | share |
|---|---|---|
| own | 14083 | 0.541 |
| opp | 6254 | 0.24 |
| wild | 5711 | 0.219 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.094 | 0.407 | 0.499 | 0 |
| mid(101-200) | 0.487 | 0.262 | 0.251 | 0 |
| late(201-300) | 0.698 | 0.141 | 0.162 | 0 |

Nearer to whose shack (BFS distance):

| nearer | n | share |
|---|---|---|
| own | 16798 | 0.645 |
| opp | 8846 | 0.34 |
| equal | 404 | 0.016 |

Tree type at the time of the chop:

| type | n | share |
|---|---|---|
| PLUM | 11020 | 0.423 |
| LEMON | 7596 | 0.292 |
| BANANA | 5878 | 0.226 |
| APPLE | 1554 | 0.06 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA | ? |
|---|---|---|---|---|---|
| early(1-100) | 0.425 | 0.404 | 0.02 | 0.15 | 0 |
| mid(101-200) | 0.374 | 0.297 | 0.052 | 0.276 | 0 |
| late(201-300) | 0.452 | 0.257 | 0.075 | 0.216 | 0 |

Tree size at the chop:

| size | n | share |
|---|---|---|
| 1 | 14711 | 0.565 |
| 4 | 10303 | 0.396 |
| 2 | 530 | 0.02 |
| 3 | 504 | 0.019 |

Fruits on the tree at the chop:

| fruits | n | share |
|---|---|---|
| 0 | 19930 | 0.765 |
| 2 | 3251 | 0.125 |
| 1 | 2486 | 0.095 |
| 3 | 381 | 0.015 |

Chop power of the chopping troll:

| chop power | n | share |
|---|---|---|
| 2 | 13896 | 0.533 |
| 3 | 7595 | 0.292 |
| 1 | 4557 | 0.175 |

## 6. Mining

| measure | value |
|---|---|
| MINE commands per game | mean 8.29, median 8, p25-p75 4.0-12.0, min-max 0-25 (n=191) |
| iron collected per game | mean 11.91, median 11, p25-p75 6.0-18.0, min-max 0-37 (n=191) |
| games with at least one MINE | 176 |
| iron per MINE command | 1.436 |
| turn of the first MINE | mean 56.87, median 55.5, p25-p75 26.0-79.75, min-max 2-207 (n=176) |
| mines per game by 10-turn bucket | {'1-10': 0.16, '11-20': 0.28, '21-30': 0.3, '31-40': 0.37, '41-50': 0.41, '51-60': 0.4, '61-70': 0.54, '71-80': 0.57, '81-90': 0.66, '91-100': 0.67, '101-110': 0.65, '111-120': 0.71, '121-130': 0.66, '131-140': 0.52, '141-150': 0.39, '151-160': 0.31, '161-170': 0.14, '171-180': 0.2, '181-190': 0.08, '191-200': 0.08, '201-210': 0.06, '211-220': 0.03, '221-230': 0.03, '231-240': 0.02, '241-250': 0.01, '281-290': 0.01, '291-300': 0.02} |

## 7. Unit roles (verb mix per troll, in creation order)

| troll | games | commands per game | verb mix | talents (n) |
|---|---|---|---|---|
| start_troll | 191 | mean 296.5, median 300, p25-p75 298.0-300.0, min-max 189-300 (n=191) | MOVE 0.566, HARVEST 0.165, DROP 0.135, PLANT 0.065, CHOP 0.045, PICK 0.021, MINE 0.003 | 1 1 1 1 (191) |
| trained_1 | 191 | mean 289.09, median 298, p25-p75 292.0-298.0, min-max 187-298 (n=191) | MOVE 0.583, CHOP 0.175, DROP 0.102, HARVEST 0.088, PLANT 0.024, MINE 0.015, PICK 0.012 | 2 2 2 2 (18); 2 2 1 2 (16); 2 2 2 1 (14); 1 2 2 2 (14) |
| trained_2 | 154 | mean 177.05, median 178.5, p25-p75 151.5-209.25, min-max 10-255 (n=154) | MOVE 0.51, CHOP 0.336, DROP 0.097, MINE 0.02, HARVEST 0.019, PLANT 0.01, PICK 0.009 | 4 3 0 2 (52); 4 3 1 2 (48); 4 3 1 3 (13); 4 3 0 3 (11) |
| trained_3 | 86 | mean 139.95, median 145.5, p25-p75 115.75-162.0, min-max 58-205 (n=86) | MOVE 0.5, CHOP 0.348, DROP 0.102, HARVEST 0.016, PICK 0.016, PLANT 0.015, MINE 0.003 | 4 3 1 3 (33); 4 3 0 3 (17); 4 3 1 2 (9); 1 3 0 3 (8) |
| trained_4 | 10 | mean 128.1, median 129.5, p25-p75 104.5-151.75, min-max 77-170 (n=10) | MOVE 0.509, CHOP 0.347, DROP 0.101, PICK 0.016, PLANT 0.015, HARVEST 0.012 | 4 3 0 3 (5); 4 3 1 3 (4); 1 3 1 3 (1) |

## 8. Endgame (last 30 turns)

| measure | value |
|---|---|
| verb mix, last 30 turns | {'MOVE': 0.631, 'CHOP': 0.207, 'DROP': 0.066, 'PLANT': 0.03, 'HARVEST': 0.026, 'WAIT': 0.021, 'PICK': 0.019, 'MINE': 0.0, 'TRAIN': 0.0} |
| verb mix, whole game | {'MOVE': 0.552, 'CHOP': 0.17, 'DROP': 0.112, 'HARVEST': 0.097, 'PLANT': 0.036, 'PICK': 0.015, 'MINE': 0.01, 'WAIT': 0.005, 'TRAIN': 0.003} |
| commands per game in the last 30 turns | 99.2 |
| per game in the last 30 turns | {'plants': 3.02, 'chops': 20.49, 'harvests': 2.59, 'drops': 6.51, 'wood': 10.99} |
| turn of the last DROP | mean 291.78, median 297, p25-p75 292.0-299.0, min-max 175-300 (n=191) |
| turns from the last DROP to the end | mean 6.52, median 3, p25-p75 1.0-7.0, min-max 0-125 (n=191) |
| trees alive at the end per game (own / wild / opp) | {'own': 3.7, 'wild': 5.69, 'opp': 3.19} |
| games ending with no tree on the map | 10 |

Commands per game by verb: {"MOVE": 444.1, "CHOP": 136.4, "DROP": 90.3, "HARVEST": 78.1, "PLANT": 28.8, "PICK": 12.1, "MINE": 8.3, "WAIT": 3.9, "TRAIN": 2.3}

Commands per game by 10-turn bucket:

| turns | MOVE | HARVEST | CHOP | PLANT | PICK | DROP | MINE | TRAIN | WAIT |
|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 10.0 | 1.06 | 1.06 | 1.99 | 1.83 | 0.48 | 0.16 | 0.88 |  |
| 11-20 | 10.31 | 1.94 | 3.41 | 1.27 | 0.31 | 1.1 | 0.28 | 0.03 |  |
| 21-30 | 9.7 | 2.45 | 3.29 | 1.04 | 0.2 | 1.89 | 0.3 | 0.04 |  |
| 31-40 | 9.86 | 2.79 | 2.65 | 0.7 | 0.2 | 2.6 | 0.37 | 0.02 |  |
| 41-50 | 9.57 | 3.32 | 2.1 | 0.78 | 0.22 | 3.03 | 0.41 | 0.03 |  |
| 51-60 | 9.9 | 3.47 | 1.69 | 0.64 | 0.24 | 3.42 | 0.4 | 0.03 |  |
| 61-70 | 9.65 | 3.98 | 1.53 | 0.63 | 0.14 | 3.7 | 0.54 | 0.07 |  |
| 71-80 | 10.55 | 3.73 | 1.48 | 0.49 | 0.14 | 3.8 | 0.57 | 0.05 |  |
| 81-90 | 10.81 | 3.97 | 1.43 | 0.45 | 0.13 | 3.9 | 0.66 | 0.11 |  |
| 91-100 | 11.52 | 3.93 | 1.51 | 0.52 | 0.19 | 4.02 | 0.67 | 0.07 |  |
| 101-110 | 12.21 | 4.09 | 1.51 | 0.49 | 0.16 | 4.05 | 0.65 | 0.08 |  |
| 111-120 | 12.76 | 4.08 | 1.79 | 0.52 | 0.15 | 4.13 | 0.71 | 0.09 |  |
| 121-130 | 13.31 | 3.99 | 2.35 | 0.55 | 0.12 | 4.17 | 0.66 | 0.13 |  |
| 131-140 | 13.81 | 4.05 | 3.09 | 0.73 | 0.2 | 4.1 | 0.52 | 0.13 | 0.01 |
| 141-150 | 14.43 | 3.94 | 3.72 | 0.88 | 0.24 | 4.05 | 0.39 | 0.13 | 0.02 |
| 151-160 | 14.8 | 3.69 | 4.96 | 0.95 | 0.26 | 3.94 | 0.31 | 0.13 | 0.01 |
| 161-170 | 15.57 | 3.22 | 5.98 | 1.21 | 0.37 | 3.69 | 0.14 | 0.1 | 0.02 |
| 171-180 | 16.43 | 2.87 | 6.36 | 1.36 | 0.47 | 3.42 | 0.2 | 0.06 | 0.01 |
| 181-190 | 16.85 | 2.53 | 7.03 | 1.29 | 0.39 | 3.24 | 0.08 | 0.03 | 0.05 |
| 191-200 | 17.34 | 2.3 | 7.07 | 1.3 | 0.44 | 3.2 | 0.08 | 0.06 | 0.08 |
| 201-210 | 17.84 | 2.12 | 7.31 | 1.37 | 0.53 | 2.84 | 0.06 | 0.03 | 0.07 |
| 211-220 | 18.16 | 1.64 | 7.99 | 1.26 | 0.49 | 2.72 | 0.03 | 0.03 | 0.14 |
| 221-230 | 18.99 | 1.67 | 7.32 | 1.17 | 0.51 | 2.68 | 0.03 | 0.01 | 0.23 |
| 231-240 | 19.49 | 1.29 | 7.66 | 1.03 | 0.49 | 2.48 | 0.02 | 0.01 | 0.25 |
| 241-250 | 19.54 | 1.17 | 7.53 | 0.98 | 0.59 | 2.63 | 0.01 | 0.01 | 0.36 |
| 251-260 | 19.95 | 1.08 | 7.19 | 1.16 | 0.69 | 2.29 |  |  | 0.46 |
| 261-270 | 19.98 | 1.08 | 7.22 | 1.03 | 0.58 | 2.45 |  |  | 0.38 |
| 271-280 | 20.4 | 0.96 | 6.77 | 0.98 | 0.58 | 2.15 |  |  | 0.54 |
| 281-290 | 20.3 | 0.84 | 6.71 | 1.01 | 0.59 | 2.16 | 0.01 | 0.01 | 0.65 |
| 291-300 | 20.07 | 0.79 | 6.64 | 0.97 | 0.65 | 2.03 | 0.02 |  | 0.66 |

DROP: mean 90.33, median 87, p25-p75 70.0-107.0, min-max 23-165 (n=191) commands per game; items per drop mean 1.64, median 1, p25-p75 1.0-2.0, min-max 1-3 (n=17253)

Referee-reported failures per game: {"move_blocked": 26.57, "train_unaffordable": 0.03, "pick_out_of_stock": 0.03, "failed_other": 0.01}

## 10. Movement

| measure | value |
|---|---|
| MOVE commands per game | mean 444.13, median 440, p25-p75 382.0-515.0, min-max 127-759 (n=191) |
| BFS distance from the troll's cell to the MOVE target | mean 2.85, median 2, p25-p75 1.0-3.0, min-max 0-29 (n=62439) |
| distance histogram (15 = 15 or more) | {'0': 576, '1': 25416, '2': 17108, '3': 4268, '4': 3948, '5': 2425, '6': 2280, '7': 1476, '8': 1274, '9': 951, '10': 835, '11': 473, '12': 382, '13': 273, '14': 204, '15': 550} |
| turns needed to arrive (distance / speed, rounded up) | mean 1.99, median 1, p25-p75 1.0-2.0, min-max 0-27 (n=62439) |
| target unreachable (water, rock, a shack cell) | 0.264 |
| target = the troll's current cell | 0.007 |

What the MOVE target is:

| target | n | share |
|---|---|---|
| tree_own | 21539 | 0.254 |
| own_shack_cell | 19597 | 0.231 |
| tree_wild | 17144 | 0.202 |
| other_grass | 13198 | 0.156 |
| tree_opp | 7444 | 0.088 |
| unwalkable_other | 2677 | 0.032 |
| own_shack_adjacent | 1728 | 0.02 |
| iron_adjacent | 1094 | 0.013 |
| opp_shack_adjacent | 408 | 0.005 |

## What the corpus cannot tell

- Why a decision was taken: no bot state, no evaluation, no stderr. Only commands and the referee's outcomes are recorded.
- A troll's carried inventory between DROPs (the viewer shows one item at a time); carry is inferred only through referee events.
- Whether a MOVE was re-targeted before arrival is visible, but the intended destination of a multi-turn walk is not.
- Tree fruit counts and cooldowns are followed through the viewer diff (stage = size + fruits); the stage shown at a chop is the state after that turn's tick.
- Games of this agent id only; earlier or later versions of the same player's bot may differ.
