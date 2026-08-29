# Behaviour profile: MSz (agent ids 6479460; 216 games)

## Summary (plain words)

MSz (Legend #4; agent 6479460; 216 games, all from raw replays; win rate 0.569, mean score 399 against 333 — the second-highest score of the four but the lowest win rate; it is the only one of the four with timeout strikes, 8 in 216 games).

1. Buys the second troll on turn 1 in 214 of 215 games, always with chop 1 and as cheap as the random starting stock allows: 2 2 2 1 (31 %), 2 2 1 1 (18 %), 1 2 2 1 (17 %), 2 1 1 1 (14 %), 1 1 1 1 (13 %). No other top bot trains on turn 1.
2. Third troll (84 % of games, median turn 95) always carry 4: 2 4 1 2 (46 %) or 2 4 1 3 (41 %); fourth (38 %, turn 129) is 2 4 0 3 in 89 %. Speed 2 in 98 % of trolls 3-4.
3. The fruit specialist: 112 HARVEST commands and 129 fruits per game (the others 78-90), 78 fruit points (the others 27-33); wood is only 80 % of its score (93 % for delineate). It keeps harvesting to the last turn: 11.6 harvests in the last 30 turns (the others 2-4) and 14.6 DROPs.
4. Apples: 11 % of its plants (20 % in the last 100 turns), 46 % of them next to water (water cuts the apple cooldown from 9 to 2 ticks), and apples are 32 % of all fruit it harvests. No other top bot farms apples.
5. Front-loaded planting: 29 plants per game, 6.3 of them in the first 20 turns (3.9 in turns 1-10); banana 39 %, lemon 33 %, plum 17 %; median 2 cells from the shack, never beyond 6, 91 % on its own half.
6. Chops late and at home: first wood at median turn 116; 118 CHOP commands per game (the fewest), 78 % nearer its own shack, 64 % on its own trees and only 16 % on opponent trees (delineate 24 %, norxondor 30 %); chop power 1 for 36 % of chops (the start troll and the cheap second troll keep chopping).
7. Mines early: first MINE at median turn 20 and 1.2 MINEs per 10 turns in turns 11-30 — the chop-1 second troll mines the iron for the chop-3 trolls bought later.
8. Step-wise MOVE (targets 1-3 cells away), so destinations are not visible in the corpus.
9. Weak with two trolls (12 % wins in the 34 games where it never bought a third), 56 % with three, 77 % with four; 13 games ended early.
10. Opening line of the start troll: move, pick, (move,) plant, move, pick, plant, pick, ... — three or four seeds planted 1-2 cells from the shack in the first 10 turns, the fastest farm start of the four.

## How to read this

Every table is measured over this player's games in the corpus (`n` = the number of games or events behind the row). Positions and effects come from the referee's own per-turn log inside each replay (exact troll positions after every move, which tree was planted/damaged/harvested), so 'own-planted / wild / opponent-planted' and 'tree type at the time of the chop' are exact for games read from a raw replay. For a game read from `turns.jsonl.gz` only (no raw replay), positions are simulated from MOVE targets and marked approximate. Position source for this profile: {"raw_replay_exact_positions": 216}.

## 9. Results and score composition

| measure | value |
|---|---|
| games | 216 |
| win rate | 0.569 |
| seat 0 games | 96 |
| final score | mean 398.62, median 408.5, p25-p75 286.25-506.5, min-max 21.0-742.0 (n=216) |
| opponent final score | mean 333.38, median 331.5, p25-p75 249.25-414.75, min-max 35.0-886.0 (n=216) |
| score margin | mean 65.25, median 23.5, p25-p75 -39.75-141.75, min-max -253.0-603.0 (n=216) |
| fruit points (banked fruit) | mean 78.11, median 73.5, p25-p75 40.0-108.75, min-max 2-232 (n=216) |
| wood points (4 x banked wood) | mean 320.52, median 342.0, p25-p75 214.0-439.0, min-max 0-668 (n=216) |
| wood share of all points | 0.804 |
| final inventory mean (plum, lemon, apple, banana, iron, wood) | [10.86, 17.67, 37.38, 12.2, 2.52, 80.13] |
| games ending before turn 300 | 13 |
| turns per game | mean 297.96, median 300.0, p25-p75 300.0-300.0, min-max 184-300 (n=216) |
| timeout strikes (total) | 8 |

By the opponent's troll count at the end:

| opponent trolls | n | win rate | mean score | mean opp score |
|---|---|---|---|---|
| 1 | 1 | 1.0 | 366.0 | 35.0 |
| 2 | 63 | 0.524 | 292.1 | 230.9 |
| 3 | 41 | 0.537 | 350.1 | 310.0 |
| 4 | 87 | 0.563 | 454.1 | 400.7 |
| 5+ | 24 | 0.75 | 561.6 | 410.5 |

By own troll count at the end:

| own trolls | n | win rate | mean score |
|---|---|---|---|
| 1 | 1 | 0.0 | 64.0 |
| 2 | 34 | 0.118 | 147.4 |
| 3 | 98 | 0.561 | 400.1 |
| 4 | 83 | 0.771 | 503.8 |

By the opponent's arena score (their ladder rating in the corpus record):

| opponent arena score | n | win rate | mean score |
|---|---|---|---|
| 20-25 | 60 | 0.533 | 331.8 |
| 25-28 | 154 | 0.578 | 423.3 |
| <20 | 2 | 1.0 | 503.5 |

Most frequent opponents:

| opponent | n | share |
|---|---|---|
| Bubaptik | 149 | 0.69 |
| tass | 38 | 0.176 |
| FreZzz | 8 | 0.037 |
| wala | 6 | 0.028 |
| a76a44 | 3 | 0.014 |
| ATsibin | 3 | 0.014 |
| Stounate | 3 | 0.014 |
| Escdemon | 1 | 0.005 |
| goq | 1 | 0.005 |
| FRHT | 1 | 0.005 |
| OldJohn | 1 | 0.005 |
| therealbeef | 1 | 0.005 |

## 1. Training ladder (TRAIN = buy a new troll; talents = speed carry harvest chop)

| measure | value |
|---|---|
| TRAIN commands total / failed | 479 / 0 |
| trolls at the end | mean 3.22, median 3.0, p25-p75 3.0-4.0, min-max 1-4 (n=216) |
| trolls trained per game | 0: 1 games (0.005), 1: 34 games (0.157), 2: 98 games (0.454), 3: 83 games (0.384) |

**troll_2** (the first troll bought): in 215 games (0.995 of games); turn mean 1.56, median 1, p25-p75 1.0-1.0, min-max 1-95 (n=215); turn histogram (25-turn bins, start turn: n) {'1': 214, '76': 1}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 2 2 1 | 66 | 0.307 |
| 2 2 1 1 | 38 | 0.177 |
| 1 2 2 1 | 37 | 0.172 |
| 2 1 1 1 | 30 | 0.14 |
| 1 1 1 1 | 27 | 0.126 |
| 1 2 1 1 | 17 | 0.079 |

marginals: speed: {'1': 81, '2': 134}; carry: {'1': 57, '2': 158}; harvest: {'1': 112, '2': 103}; chop: {'1': 215}


**troll_3** (the second troll bought): in 181 games (0.838 of games); turn mean 101.93, median 95, p25-p75 78.5-121.0, min-max 42-194 (n=181); turn histogram (25-turn bins, start turn: n) {'26': 1, '51': 37, '76': 64, '101': 44, '126': 15, '151': 14, '176': 6}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 4 1 2 | 84 | 0.464 |
| 2 4 1 3 | 74 | 0.409 |
| 2 4 1 4 | 19 | 0.105 |
| 3 4 1 2 | 3 | 0.017 |
| 3 4 1 3 | 1 | 0.006 |

marginals: speed: {'2': 177, '3': 4}; carry: {'4': 181}; harvest: {'1': 181}; chop: {'2': 87, '3': 75, '4': 19}


**troll_4** (the third troll bought): in 83 games (0.384 of games); turn mean 128.23, median 129, p25-p75 115.0-144.0, min-max 90-184 (n=83); turn histogram (25-turn bins, start turn: n) {'76': 8, '101': 27, '126': 37, '151': 10, '176': 1}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 4 0 3 | 74 | 0.892 |
| 2 4 0 2 | 8 | 0.096 |
| 3 4 0 3 | 1 | 0.012 |

marginals: speed: {'2': 82, '3': 1}; carry: {'4': 83}; harvest: {'0': 83}; chop: {'2': 8, '3': 75}

Opponents' trained talents (for contrast):

| talents | n | share |
|---|---|---|
| 4 3 1 3 | 67 | 0.133 |
| 4 3 1 2 | 47 | 0.094 |
| 4 3 0 3 | 43 | 0.086 |
| 4 3 0 2 | 41 | 0.082 |
| 2 2 2 2 | 21 | 0.042 |
| 2 2 1 1 | 16 | 0.032 |

## 2. Opening (turns 1-30)

Letters: M=MOVE, H=HARVEST, C=CHOP, P=PLANT, K=PICK, D=DROP, I=MINE, T=TRAIN, W=WAIT, -=no command for that troll.

Starting troll, one letter per turn, turns 1-10 (most common patterns):

| pattern | n | share |
|---|---|---|
| MKMPMKPKMP | 15 | 0.069 |
| MKPKMPMKPK | 13 | 0.06 |
| MKPKMPMKMP | 9 | 0.042 |
| MKMPMKMPMK | 9 | 0.042 |
| MKPKMPCMKP | 6 | 0.028 |
| MKMPMKPMMM | 6 | 0.028 |
| MKPKMPMKPM | 6 | 0.028 |
| MKMPCMKPMM | 4 | 0.019 |
| MKMPMKPKMM | 4 | 0.019 |
| MKPMMKMPMK | 4 | 0.019 |
| MKMPMKPMHM | 3 | 0.014 |
| MKPKMPIMDK | 3 | 0.014 |

Starting troll, turns 1-20:

| pattern | n | share |
|---|---|---|
| MKMPMKPKMPMIDIDIDIDI | 3 | 0.014 |
| MKMPMKPMHMMPMMHMMMDK | 1 | 0.005 |
| MKMPMKPMHMPMMMMHMMMP | 1 | 0.005 |
| MKPKMPCMMHMMPMMHMMMM | 1 | 0.005 |
| MKPKMPCMKPMMMHMMMMMM | 1 | 0.005 |
| MKPKMPMKPKM-PMHMPMMM | 1 | 0.005 |
| MKPMMMMMHMMMMPMMMIMM | 1 | 0.005 |
| MKMPMKPMMMMIMMDKPMMI | 1 | 0.005 |

All trolls together, turns 1-10 (letters of one turn joined, turns separated by spaces):

| pattern | n | share |
|---|---|---|
| MT KM KM KP MP KM KP KP MM PP | 3 | 0.014 |
| MT KM KM KP MP KM PP MM IM IM | 2 | 0.009 |
| MT KM MP HK MM MP MP KM KP KP | 2 | 0.009 |
| MT KM KM K PP MM KP MP MM MM | 2 | 0.009 |
| MT KM KM KP MP KM PP CM HM KM | 1 | 0.005 |
| MT KM KM KP MP KM PP MM HH MM | 1 | 0.005 |
| MT KM KP KP MM MP CM HM MM HM | 1 | 0.005 |
| MT KM KP KP MM HP CM MM KP MP | 1 | 0.005 |

First occurrences (turn of the first command of that kind; games with it):

| verb | games with it | turn |
|---|---|---|
| HARVEST | 216 | mean 10.01, median 9.0, p25-p75 5.0-13.0, min-max 2-40 (n=216) |
| PLANT | 216 | mean 3.63, median 4.0, p25-p75 3.0-4.0, min-max 3-9 (n=216) |
| CHOP | 216 | mean 20.53, median 16.0, p25-p75 8.0-27.0, min-max 2-104 (n=216) |
| TRAIN | 215 | mean 1.56, median 1, p25-p75 1.0-1.0, min-max 1-95 (n=215) |
| DROP | 216 | mean 15.43, median 15.0, p25-p75 11.0-19.0, min-max 3-44 (n=216) |
| MINE | 197 | mean 37.4, median 20, p25-p75 10.5-60.0, min-max 2-155 (n=197) |

first action verb of start troll:

| value | n | share |
|---|---|---|
| K | 204 | 0.944 |
| H | 8 | 0.037 |
| I | 2 | 0.009 |
| C | 2 | 0.009 |

first harvest type:

| value | n | share |
|---|---|---|
| LEMON | 92 | 0.426 |
| PLUM | 76 | 0.352 |
| APPLE | 33 | 0.153 |
| BANANA | 15 | 0.069 |

first harvest origin:

| value | n | share |
|---|---|---|
| wild | 193 | 0.894 |
| own | 23 | 0.106 |

first plant type:

| value | n | share |
|---|---|---|
| LEMON | 130 | 0.602 |
| PLUM | 53 | 0.245 |
| BANANA | 22 | 0.102 |
| APPLE | 11 | 0.051 |

first chop type:

| value | n | share |
|---|---|---|
| BANANA | 90 | 0.417 |
| LEMON | 72 | 0.333 |
| PLUM | 45 | 0.208 |
| APPLE | 9 | 0.042 |

first chop origin:

| value | n | share |
|---|---|---|
| own | 159 | 0.736 |
| wild | 56 | 0.259 |
| opp | 1 | 0.005 |

Verb share by turn, turns 1-30 (commands per game, by letter):

| turn | M | H | C | P | K | D | I | T | W |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.99 |  |  |  |  |  |  | 0.97 |  |
| 2 | 0.97 | 0.03 | 0.0 |  | 0.93 |  | 0.01 | 0.01 |  |
| 3 | 0.65 | 0.12 | 0.02 | 0.46 | 0.68 | 0.01 | 0.0 |  |  |
| 4 | 0.45 | 0.12 | 0.02 | 0.72 | 0.6 |  | 0.02 |  |  |
| 5 | 1.19 | 0.06 | 0.07 | 0.47 | 0.12 | 0.02 | 0.02 |  |  |
| 6 | 0.8 | 0.1 | 0.06 | 0.45 | 0.47 | 0.02 | 0.06 |  |  |
| 7 | 0.84 | 0.12 | 0.07 | 0.57 | 0.25 | 0.05 | 0.04 | 0.0 |  |
| 8 | 0.86 | 0.09 | 0.07 | 0.5 | 0.33 | 0.03 | 0.07 |  |  |
| 9 | 1.06 | 0.11 | 0.06 | 0.38 | 0.17 | 0.08 | 0.07 |  |  |
| 10 | 0.89 | 0.2 | 0.11 | 0.33 | 0.27 | 0.06 | 0.09 |  |  |
| 11 | 1.0 | 0.22 | 0.07 | 0.3 | 0.14 | 0.12 | 0.1 |  |  |
| 12 | 0.92 | 0.24 | 0.05 | 0.35 | 0.17 | 0.12 | 0.1 |  |  |
| 13 | 1.02 | 0.14 | 0.09 | 0.29 | 0.11 | 0.19 | 0.1 |  |  |
| 14 | 1.0 | 0.18 | 0.11 | 0.28 | 0.14 | 0.12 | 0.13 |  |  |
| 15 | 0.86 | 0.2 | 0.11 | 0.3 | 0.08 | 0.27 | 0.13 |  |  |
| 16 | 1.01 | 0.22 | 0.13 | 0.18 | 0.13 | 0.13 | 0.15 |  |  |
| 17 | 0.89 | 0.3 | 0.11 | 0.19 | 0.09 | 0.3 | 0.11 |  |  |
| 18 | 0.95 | 0.23 | 0.11 | 0.22 | 0.09 | 0.21 | 0.16 | 0.0 |  |
| 19 | 0.99 | 0.21 | 0.07 | 0.19 | 0.07 | 0.34 | 0.1 |  |  |
| 20 | 0.89 | 0.31 | 0.12 | 0.15 | 0.07 | 0.26 | 0.17 |  |  |
| 21 | 0.9 | 0.33 | 0.12 | 0.18 | 0.05 | 0.29 | 0.12 |  |  |
| 22 | 0.94 | 0.32 | 0.07 | 0.12 | 0.04 | 0.35 | 0.13 |  |  |
| 23 | 0.87 | 0.31 | 0.09 | 0.13 | 0.06 | 0.37 | 0.13 |  |  |
| 24 | 0.97 | 0.26 | 0.11 | 0.12 | 0.05 | 0.33 | 0.13 |  |  |
| 25 | 0.88 | 0.34 | 0.1 | 0.1 | 0.04 | 0.38 | 0.14 |  |  |
| 26 | 0.92 | 0.32 | 0.09 | 0.07 | 0.08 | 0.36 | 0.12 |  |  |
| 27 | 0.94 | 0.27 | 0.14 | 0.12 | 0.04 | 0.37 | 0.1 |  |  |
| 28 | 0.96 | 0.32 | 0.14 | 0.08 | 0.05 | 0.35 | 0.09 |  |  |
| 29 | 0.9 | 0.33 | 0.17 | 0.08 | 0.04 | 0.37 | 0.07 |  |  |
| 30 | 0.98 | 0.35 | 0.13 | 0.08 | 0.03 | 0.31 | 0.1 |  |  |

Most common MSG texts (digits replaced by N):

| message | n | share |
|---|---|---|

## 3. Planting

| measure | value |
|---|---|
| PLANT commands per game | mean 29.51, median 29.0, p25-p75 23.0-36.0, min-max 9-55 (n=216) |
| successful plants per game | mean 29.49, median 29.0, p25-p75 23.0-36.0, min-max 9-55 (n=216) |
| success rate of PLANT commands | 0.999 |
| distance (BFS over grass) from own shack | mean 1.71, median 2.0, p25-p75 1.0-2.0, min-max 1-6 (n=6370) |
| distance hist (cells: n; 12 = 12 or more) | {'1': 2702, '2': 3118, '3': 368, '4': 91, '5': 54, '6': 37} |
| distance from opponent shack | mean 9.15, median 9.0, p25-p75 6.0-12.0, min-max 2-27 (n=6370) |
| planted next to water | 0.195 |
| next to water, by type | {'PLUM': 0.21, 'LEMON': 0.21, 'APPLE': 0.461, 'BANANA': 0.098} |
| planted on own half of the map | 0.914 |
| planted nearer own shack than opponent's | 1.0 |
| plants per game by 10-turn bucket | {'1-10': 3.89, '11-20': 2.44, '21-30': 1.08, '31-40': 0.61, '41-50': 0.5, '51-60': 0.6, '61-70': 0.54, '71-80': 0.61, '81-90': 0.5, '91-100': 0.51, '101-110': 0.76, '111-120': 0.85, '121-130': 0.9, '131-140': 1.12, '141-150': 1.22, '151-160': 1.21, '161-170': 1.08, '171-180': 1.08, '181-190': 1.11, '191-200': 1.06, '201-210': 1.07, '211-220': 1.12, '221-230': 0.93, '231-240': 0.95, '241-250': 0.85, '251-260': 0.75, '261-270': 0.81, '271-280': 0.72, '281-290': 0.6, '291-300': 0.02} |

By type (successful plants):

| type | n | share |
|---|---|---|
| BANANA | 2469 | 0.388 |
| LEMON | 2085 | 0.327 |
| PLUM | 1103 | 0.173 |
| APPLE | 713 | 0.112 |

Seeds picked at the shack (PICK commands) by type:

| type | n | share |
|---|---|---|
| BANANA | 1185 | 0.617 |
| LEMON | 373 | 0.194 |
| PLUM | 255 | 0.133 |
| APPLE | 109 | 0.057 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA |
|---|---|---|---|---|
| early(1-100) | 0.165 | 0.27 | 0.057 | 0.508 |
| mid(101-200) | 0.17 | 0.351 | 0.102 | 0.377 |
| late(201-300) | 0.189 | 0.378 | 0.205 | 0.227 |

Distance from own shack by type: PLUM: mean 1.72, median 2, p25-p75 1.0-2.0, min-max 1-6 (n=1103); LEMON: mean 1.68, median 2, p25-p75 1.0-2.0, min-max 1-6 (n=2085); APPLE: mean 2.12, median 2, p25-p75 2.0-2.0, min-max 1-6 (n=713); BANANA: mean 1.62, median 1, p25-p75 1.0-2.0, min-max 1-6 (n=2469)

## 4. Harvesting

| measure | value |
|---|---|
| HARVEST commands per game | mean 112.35, median 114.0, p25-p75 83.25-138.5, min-max 23-222 (n=216) |
| fruits harvested per game (referee count) | mean 128.77, median 127.0, p25-p75 93.0-161.0, min-max 23-257 (n=216) |
| fruits per HARVEST command | 1.146 |
| HARVEST commands that took nothing | 0.0 |
| distance from own shack of the harvested cell | mean 2.19, median 2.0, p25-p75 1.0-2.0, min-max 1-22 (n=24268) |
| harvests per game by 10-turn bucket | {'1-10': 0.94, '11-20': 2.25, '21-30': 3.17, '31-40': 3.61, '41-50': 3.74, '51-60': 3.4, '61-70': 3.44, '71-80': 3.58, '81-90': 3.82, '91-100': 4.38, '101-110': 4.3, '111-120': 4.22, '121-130': 4.27, '131-140': 4.19, '141-150': 4.16, '151-160': 3.93, '161-170': 3.69, '171-180': 3.93, '181-190': 3.85, '191-200': 4.03, '201-210': 3.97, '211-220': 3.92, '221-230': 4.02, '231-240': 3.94, '241-250': 3.98, '251-260': 4.08, '261-270': 4.06, '271-280': 3.89, '281-290': 4.12, '291-300': 3.5} |

By the tree's origin (own-planted / wild / planted by the opponent):

| origin | n | share |
|---|---|---|
| own | 18295 | 0.754 |
| wild | 5314 | 0.219 |
| opp | 659 | 0.027 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.591 | 0.376 | 0.034 | 0 |
| mid(101-200) | 0.748 | 0.219 | 0.033 | 0 |
| late(201-300) | 0.894 | 0.091 | 0.015 | 0 |

Fruits harvested by type:

| type | n | share |
|---|---|---|
| LEMON | 10298 | 0.37 |
| APPLE | 9050 | 0.325 |
| PLUM | 4679 | 0.168 |
| BANANA | 3787 | 0.136 |

## 5. Chopping

| measure | value |
|---|---|
| CHOP commands per game | mean 118.27, median 123.0, p25-p75 89.0-151.0, min-max 11-240 (n=216) |
| chops that landed per game | mean 91.15, median 92.0, p25-p75 64.25-117.75, min-max 6-191 (n=216) |
| trees felled per game (this player struck the killing turn) | mean 0.0, median 0.0, p25-p75 0.0-0.0, min-max 0-0 (n=216) |
| wood collected per game | mean 80.21, median 86.0, p25-p75 53.5-109.75, min-max 0-167 (n=216) |
| turn of the first wood | mean 113.46, median 116, p25-p75 97.0-136.0, min-max 9-245 (n=215) |
| wood by phase (total over games) | {'early(1-100)': 175, 'mid(101-200)': 8931, 'late(201-300)': 8220} |
| chops per game by 10-turn bucket | {'1-10': 0.49, '11-20': 0.98, '21-30': 1.16, '31-40': 1.21, '41-50': 1.3, '51-60': 1.32, '61-70': 1.28, '71-80': 1.08, '81-90': 1.03, '91-100': 1.45, '101-110': 2.21, '111-120': 2.99, '121-130': 3.7, '131-140': 5.13, '141-150': 5.36, '151-160': 5.92, '161-170': 6.5, '171-180': 6.52, '181-190': 6.15, '191-200': 6.33, '201-210': 6.32, '211-220': 6.49, '221-230': 6.16, '231-240': 5.84, '241-250': 5.83, '251-260': 5.9, '261-270': 5.34, '271-280': 5.38, '281-290': 5.54, '291-300': 3.35} |
| chopped on own half of the map | 0.734 |
| distance from own shack | mean 3.63, median 2, p25-p75 1.0-5.0, min-max 1-25 (n=25547) |
| distance from opponent shack | mean 8.77, median 9, p25-p75 5.0-13.0, min-max 1-27 (n=25547) |

By the tree's origin:

| origin | n | share |
|---|---|---|
| own | 16360 | 0.64 |
| wild | 5171 | 0.202 |
| opp | 4016 | 0.157 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.779 | 0.187 | 0.034 | 0 |
| mid(101-200) | 0.642 | 0.25 | 0.108 | 0 |
| late(201-300) | 0.611 | 0.162 | 0.227 | 0 |

Nearer to whose shack (BFS distance):

| nearer | n | share |
|---|---|---|
| own | 20047 | 0.785 |
| opp | 4875 | 0.191 |
| equal | 625 | 0.024 |

Tree type at the time of the chop:

| type | n | share |
|---|---|---|
| LEMON | 8774 | 0.343 |
| PLUM | 6082 | 0.238 |
| APPLE | 5348 | 0.209 |
| BANANA | 5343 | 0.209 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA | ? |
|---|---|---|---|---|---|
| early(1-100) | 0.168 | 0.367 | 0.035 | 0.429 | 0 |
| mid(101-200) | 0.227 | 0.342 | 0.162 | 0.269 | 0 |
| late(201-300) | 0.262 | 0.34 | 0.287 | 0.111 | 0 |

Tree size at the chop:

| size | n | share |
|---|---|---|
| 1 | 13406 | 0.525 |
| 4 | 11523 | 0.451 |
| 3 | 334 | 0.013 |
| 2 | 284 | 0.011 |

Fruits on the tree at the chop:

| fruits | n | share |
|---|---|---|
| 0 | 20335 | 0.796 |
| 2 | 2943 | 0.115 |
| 1 | 1943 | 0.076 |
| 3 | 326 | 0.013 |

Chop power of the chopping troll:

| chop power | n | share |
|---|---|---|
| 1 | 9280 | 0.363 |
| 3 | 8832 | 0.346 |
| 2 | 6364 | 0.249 |
| 4 | 1071 | 0.042 |

## 6. Mining

| measure | value |
|---|---|
| MINE commands per game | mean 8.29, median 8.0, p25-p75 5.0-12.0, min-max 0-21 (n=216) |
| iron collected per game | mean 10.74, median 10.0, p25-p75 5.0-17.0, min-max 0-30 (n=216) |
| games with at least one MINE | 197 |
| iron per MINE command | 1.296 |
| turn of the first MINE | mean 37.4, median 20, p25-p75 10.5-60.0, min-max 2-155 (n=197) |
| mines per game by 10-turn bucket | {'1-10': 0.39, '11-20': 1.24, '21-30': 1.14, '31-40': 0.83, '41-50': 0.54, '51-60': 0.44, '61-70': 0.48, '71-80': 0.52, '81-90': 0.77, '91-100': 0.68, '101-110': 0.44, '111-120': 0.34, '121-130': 0.22, '131-140': 0.13, '141-150': 0.04, '151-160': 0.04, '161-170': 0.02, '171-180': 0.0, '181-190': 0.0} |

## 7. Unit roles (verb mix per troll, in creation order)

| troll | games | commands per game | verb mix | talents (n) |
|---|---|---|---|---|
| start_troll | 216 | mean 287.52, median 292.0, p25-p75 287.0-295.0, min-max 180-300 (n=216) | MOVE 0.495, HARVEST 0.177, DROP 0.159, CHOP 0.092, PLANT 0.05, PICK 0.018, MINE 0.009 | 1 1 1 1 (216) |
| trained_1 | 215 | mean 290.17, median 295, p25-p75 290.0-297.0, min-max 177-299 (n=215) | MOVE 0.513, HARVEST 0.194, DROP 0.163, CHOP 0.057, PLANT 0.049, MINE 0.013, PICK 0.012 | 2 2 2 1 (66); 2 2 1 1 (38); 1 2 2 1 (37); 2 1 1 1 (30) |
| trained_2 | 181 | mean 188.04, median 192, p25-p75 171.0-211.0, min-max 105-246 (n=181) | MOVE 0.476, CHOP 0.344, DROP 0.124, HARVEST 0.034, MINE 0.013, PLANT 0.006, PICK 0.002 | 2 4 1 2 (84); 2 4 1 3 (74); 2 4 1 4 (19); 3 4 1 2 (3) |
| trained_3 | 83 | mean 159.23, median 159, p25-p75 145.0-177.0, min-max 102-207 (n=83) | MOVE 0.551, CHOP 0.345, DROP 0.102, PICK 0.001, PLANT 0.001 | 2 4 0 3 (74); 2 4 0 2 (8); 3 4 0 3 (1) |

## 8. Endgame (last 30 turns)

| measure | value |
|---|---|
| verb mix, last 30 turns | {'MOVE': 0.526, 'CHOP': 0.164, 'DROP': 0.163, 'HARVEST': 0.129, 'PLANT': 0.015, 'PICK': 0.003} |
| verb mix, whole game | {'MOVE': 0.501, 'DROP': 0.149, 'CHOP': 0.148, 'HARVEST': 0.141, 'PLANT': 0.037, 'PICK': 0.011, 'MINE': 0.01, 'TRAIN': 0.003} |
| commands per game in the last 30 turns | 89.8 |
| per game in the last 30 turns | {'plants': 1.34, 'chops': 14.74, 'harvests': 11.55, 'drops': 14.63, 'wood': 9.91} |
| turn of the last DROP | mean 296.84, median 300.0, p25-p75 299.0-300.0, min-max 161-300 (n=216) |
| turns from the last DROP to the end | mean 1.12, median 0.0, p25-p75 0.0-1.0, min-max 0-23 (n=216) |
| trees alive at the end per game (own / wild / opp) | {'own': 3.24, 'wild': 4.69, 'opp': 3.67} |
| games ending with no tree on the map | 18 |

Commands per game by verb: {"MOVE": 399.3, "DROP": 118.5, "CHOP": 118.3, "HARVEST": 112.4, "PLANT": 29.5, "PICK": 8.9, "MINE": 8.3, "TRAIN": 2.2}

Commands per game by 10-turn bucket:

| turns | MOVE | HARVEST | CHOP | PLANT | PICK | DROP | MINE | TRAIN | WAIT |
|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 8.71 | 0.94 | 0.49 | 3.89 | 3.83 | 0.28 | 0.39 | 0.99 |  |
| 11-20 | 9.53 | 2.25 | 0.98 | 2.44 | 1.1 | 2.06 | 1.24 | 0.0 |  |
| 21-30 | 9.24 | 3.17 | 1.16 | 1.08 | 0.49 | 3.47 | 1.14 |  |  |
| 31-40 | 9.81 | 3.61 | 1.21 | 0.61 | 0.18 | 3.56 | 0.83 |  |  |
| 41-50 | 10.18 | 3.74 | 1.3 | 0.5 | 0.09 | 3.45 | 0.54 | 0.0 |  |
| 51-60 | 10.93 | 3.4 | 1.32 | 0.6 | 0.07 | 3.05 | 0.44 | 0.05 |  |
| 61-70 | 11.71 | 3.44 | 1.28 | 0.54 | 0.11 | 2.91 | 0.48 | 0.06 |  |
| 71-80 | 12.31 | 3.58 | 1.08 | 0.61 | 0.07 | 3.0 | 0.52 | 0.13 |  |
| 81-90 | 12.97 | 3.82 | 1.03 | 0.5 | 0.02 | 3.26 | 0.77 | 0.11 |  |
| 91-100 | 12.86 | 4.38 | 1.45 | 0.51 | 0.06 | 3.79 | 0.68 | 0.15 |  |
| 101-110 | 13.45 | 4.3 | 2.21 | 0.76 | 0.07 | 3.87 | 0.44 | 0.13 |  |
| 111-120 | 13.75 | 4.22 | 2.99 | 0.85 | 0.08 | 3.94 | 0.34 | 0.11 |  |
| 121-130 | 13.88 | 4.27 | 3.7 | 0.9 | 0.13 | 4.31 | 0.22 | 0.15 |  |
| 131-140 | 13.65 | 4.19 | 5.13 | 1.12 | 0.12 | 4.37 | 0.13 | 0.1 |  |
| 141-150 | 13.87 | 4.16 | 5.36 | 1.22 | 0.14 | 4.44 | 0.04 | 0.07 |  |
| 151-160 | 14.09 | 3.93 | 5.92 | 1.21 | 0.15 | 4.51 | 0.04 | 0.06 |  |
| 161-170 | 14.34 | 3.69 | 6.5 | 1.1 | 0.15 | 4.38 | 0.02 | 0.03 |  |
| 171-180 | 14.53 | 3.93 | 6.52 | 1.08 | 0.12 | 4.21 | 0.0 | 0.02 |  |
| 181-190 | 14.72 | 3.85 | 6.15 | 1.11 | 0.14 | 4.5 | 0.0 | 0.03 |  |
| 191-200 | 14.7 | 4.03 | 6.33 | 1.06 | 0.16 | 4.65 |  | 0.0 |  |
| 201-210 | 15.07 | 3.97 | 6.32 | 1.07 | 0.24 | 4.56 |  |  |  |
| 211-220 | 15.08 | 3.92 | 6.49 | 1.12 | 0.17 | 4.41 |  |  |  |
| 221-230 | 15.2 | 4.02 | 6.16 | 0.93 | 0.17 | 4.52 |  |  |  |
| 231-240 | 15.42 | 3.94 | 5.84 | 0.95 | 0.21 | 4.6 |  |  |  |
| 241-250 | 15.31 | 3.98 | 5.83 | 0.85 | 0.22 | 4.61 |  |  |  |
| 251-260 | 14.78 | 4.08 | 5.9 | 0.75 | 0.13 | 4.64 |  |  |  |
| 261-270 | 15.12 | 4.06 | 5.34 | 0.81 | 0.21 | 4.71 |  |  |  |
| 271-280 | 15.09 | 3.89 | 5.38 | 0.72 | 0.15 | 4.54 |  |  |  |
| 281-290 | 14.56 | 4.12 | 5.54 | 0.6 | 0.1 | 4.52 |  |  |  |
| 291-300 | 14.47 | 3.5 | 3.35 | 0.02 | 0.0 | 5.38 |  |  |  |

DROP: mean 118.49, median 116.5, p25-p75 94.0-141.75, min-max 35-252 (n=216) commands per game; items per drop mean 1.68, median 1, p25-p75 1.0-2.0, min-max 1-4 (n=25593)

Referee-reported failures per game: {"failed_other": 0.02}

## 10. Movement

| measure | value |
|---|---|
| MOVE commands per game | mean 399.3, median 394.5, p25-p75 327.25-481.0, min-max 116-626 (n=216) |
| BFS distance from the troll's cell to the MOVE target | mean 1.36, median 1, p25-p75 1.0-2.0, min-max 1-3 (n=86249) |
| distance histogram (15 = 15 or more) | {'1': 55679, '2': 30386, '3': 184} |
| turns needed to arrive (distance / speed, rounded up) | mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-1 (n=86249) |
| target unreachable (water, rock, a shack cell) | 0.0 |
| target = the troll's current cell | 0.0 |

What the MOVE target is:

| target | n | share |
|---|---|---|
| other_grass | 32595 | 0.378 |
| tree_own | 29635 | 0.344 |
| own_shack_adjacent | 9143 | 0.106 |
| tree_wild | 8030 | 0.093 |
| tree_opp | 3199 | 0.037 |
| iron_adjacent | 2864 | 0.033 |
| opp_shack_adjacent | 783 | 0.009 |

## What the corpus cannot tell

- Why a decision was taken: no bot state, no evaluation, no stderr. Only commands and the referee's outcomes are recorded.
- A troll's carried inventory between DROPs (the viewer shows one item at a time); carry is inferred only through referee events.
- Whether a MOVE was re-targeted before arrival is visible, but the intended destination of a multi-turn walk is not.
- Tree fruit counts and cooldowns are followed through the viewer diff (stage = size + fruits); the stage shown at a chop is the state after that turn's tick.
- Games of this agent id only; earlier or later versions of the same player's bot may differ.
