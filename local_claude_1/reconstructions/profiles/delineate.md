# Behaviour profile: delineate (agent ids 6479768; 223 games)

## Summary (plain words)

delineate (Legend #1; agent 6479768; 223 games, all read from raw replays; win rate 0.785, mean score 415 against 253).

1. The strongest of the four and the one that scores most from wood: 93 % of its points are wood (388 wood points and 27 fruit points per game); it collects 98 wood per game, the most of any profiled bot.
2. It wins with FEWER trolls: 2.9 trolls at the end on average (norxondor 3.5, Bubaptik 3.3, MSz 3.2). A third troll appears in only 56 % of games (median turn 111) and a fourth in 27 % (turn 144); its win rate is 69 % with two trolls and 91 % with four.
3. Second troll early (median turn 6, 74 % by turn 25) with balanced talents: speed 2 / carry 2 / harvest 1-2 / chop 2 (2 2 2 2 in 20 % of games, chop 2 in 66 %). Later trolls are haulers-choppers: carry 4 in 70 %, chop 3 in 61 % (troll 3) and 97 % (troll 4); 3 4 1 3 is the standard fourth troll.
4. It plants the most (40 successful plants per game; the others 29): lemons first (67 % of first plants), bananas later (48 % of all plants, 53 % in the last 100 turns). The planting rate rises from 0.7 per 10 turns early to 1.9 per 10 turns after turn 150: the banana farm grows all game.
5. Plants close to home: median 2 cells from its shack (43 % at distance 1, 5 % beyond 4), 94 % on its own half, 23 % next to water.
6. Chops 172 times per game (129 land). 64 % of chops hit its own planted trees, 24 % opponent-planted, 13 % wild. In turns 1-100 it is a raider: 56 % of its early chops are on the opponent's freshly planted trees; in turns 201-300 it fells its own farm (80 %). 64 % of all trees it chops are size 1 with no fruit: plant, let it tick once, fell it for one wood (4 points).
7. Harvests 79 times per game (85 fruits, lemons 42 %), 72 % at its own trees; harvesting peaks around turns 100-150 and fades in the endgame while chopping climbs to 10 per 10 turns.
8. Mines in 77 % of games (7.8 MINE commands, 11.5 iron), mostly turns 50-150, to pay the chop-3 trolls.
9. MOVE commands are one step at a time: the target is always within 1-3 cells (its speed), so the corpus never shows its true destinations (the same is true of norxondor and MSz; Bubaptik and yamo send destinations).
10. Clean play: no MSG, no timeouts, no failed commands in 223 games; 8 games ended early. It beats 4-troll opponents 72 % of the time and 2-troll opponents 82 %.

## How to read this

Every table is measured over this player's games in the corpus (`n` = the number of games or events behind the row). Positions and effects come from the referee's own per-turn log inside each replay (exact troll positions after every move, which tree was planted/damaged/harvested), so 'own-planted / wild / opponent-planted' and 'tree type at the time of the chop' are exact for games read from a raw replay. For a game read from `turns.jsonl.gz` only (no raw replay), positions are simulated from MOVE targets and marked approximate. Position source for this profile: {"raw_replay_exact_positions": 223}.

## 9. Results and score composition

| measure | value |
|---|---|
| games | 223 |
| win rate | 0.785 |
| seat 0 games | 109 |
| final score | mean 415.22, median 380.0, p25-p75 267.0-541.0, min-max 61.0-984.0 (n=223) |
| opponent final score | mean 252.5, median 236.0, p25-p75 170.0-312.0, min-max 20.0-590.0 (n=223) |
| score margin | mean 162.71, median 129.0, p25-p75 21.0-268.0, min-max -91.0-809.0 (n=223) |
| fruit points (banked fruit) | mean 27.48, median 21, p25-p75 10.0-39.0, min-max 0-149 (n=223) |
| wood points (4 x banked wood) | mean 387.73, median 356, p25-p75 232.0-520.0, min-max 44-976 (n=223) |
| wood share of all points | 0.934 |
| final inventory mean (plum, lemon, apple, banana, iron, wood) | [4.49, 9.58, 9.29, 4.12, 2.93, 96.93] |
| games ending before turn 300 | 8 |
| turns per game | mean 298.41, median 300, p25-p75 300.0-300.0, min-max 158-300 (n=223) |
| timeout strikes (total) | 0 |

By the opponent's troll count at the end:

| opponent trolls | n | win rate | mean score | mean opp score |
|---|---|---|---|---|
| 1 | 2 | 1.0 | 356.0 | 24.5 |
| 2 | 84 | 0.821 | 324.6 | 198.8 |
| 3 | 59 | 0.78 | 408.3 | 222.9 |
| 4 | 67 | 0.716 | 504.2 | 333.4 |
| 5+ | 11 | 0.909 | 613.1 | 369.6 |

By own troll count at the end:

| own trolls | n | win rate | mean score |
|---|---|---|---|
| 2 | 98 | 0.694 | 284.2 |
| 3 | 64 | 0.781 | 415.1 |
| 4 | 45 | 0.911 | 599.4 |
| 5+ | 16 | 1.0 | 700.4 |

By the opponent's arena score (their ladder rating in the corpus record):

| opponent arena score | n | win rate | mean score |
|---|---|---|---|
| 20-25 | 54 | 0.852 | 385.2 |
| 25-28 | 158 | 0.747 | 417.2 |
| <20 | 10 | 1.0 | 565.3 |
| unknown | 1 | 1.0 | 220.0 |

Most frequent opponents:

| opponent | n | share |
|---|---|---|
| Bubaptik | 148 | 0.664 |
| tass | 30 | 0.135 |
| celeria | 6 | 0.027 |
| FreZzz | 5 | 0.022 |
| wala | 5 | 0.022 |
| LeRenard | 4 | 0.018 |
| laconic_pixel | 3 | 0.013 |
| Stounate | 3 | 0.013 |
| goq | 3 | 0.013 |
| oidrissi | 2 | 0.009 |
| therealbeef | 2 | 0.009 |
| viewlagoon | 1 | 0.004 |

## 1. Training ladder (TRAIN = buy a new troll; talents = speed carry harvest chop)

| measure | value |
|---|---|
| TRAIN commands total / failed | 425 / 0 |
| trolls at the end | mean 2.91, median 3, p25-p75 2.0-4.0, min-max 2-5 (n=223) |
| trolls trained per game | 1: 98 games (0.439), 2: 64 games (0.287), 3: 45 games (0.202), 4: 16 games (0.072) |

**troll_2** (the first troll bought): in 223 games (1.0 of games); turn mean 19.9, median 6, p25-p75 2.0-26.0, min-max 1-237 (n=223); turn histogram (25-turn bins, start turn: n) {'1': 165, '26': 35, '51': 15, '76': 1, '101': 5, '226': 2}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 2 2 2 | 45 | 0.202 |
| 2 2 1 2 | 23 | 0.103 |
| 2 3 1 2 | 17 | 0.076 |
| 1 2 2 2 | 11 | 0.049 |
| 2 2 2 1 | 11 | 0.049 |
| 3 2 2 2 | 9 | 0.04 |
| 3 3 1 2 | 7 | 0.031 |
| 2 3 2 2 | 7 | 0.031 |

marginals: speed: {'1': 39, '2': 142, '3': 42}; carry: {'1': 18, '2': 133, '3': 68, '4': 4}; harvest: {'0': 1, '1': 108, '2': 114}; chop: {'1': 32, '2': 147, '3': 44}


**troll_3** (the second troll bought): in 125 games (0.561 of games); turn mean 114.29, median 111, p25-p75 89.5-131.0, min-max 50-227 (n=125); turn histogram (25-turn bins, start turn: n) {'26': 1, '51': 16, '76': 27, '101': 40, '126': 25, '151': 10, '176': 2, '201': 2, '226': 2}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 4 1 3 | 14 | 0.112 |
| 3 4 1 2 | 13 | 0.104 |
| 3 4 1 3 | 11 | 0.088 |
| 2 4 1 2 | 11 | 0.088 |
| 1 4 1 3 | 10 | 0.08 |
| 3 3 1 3 | 7 | 0.056 |
| 3 2 1 3 | 6 | 0.048 |
| 3 4 0 3 | 5 | 0.04 |

marginals: speed: {'1': 17, '2': 51, '3': 57}; carry: {'1': 1, '2': 16, '3': 20, '4': 88}; harvest: {'0': 16, '1': 93, '2': 16}; chop: {'1': 4, '2': 45, '3': 76}


**troll_4** (the third troll bought): in 61 games (0.274 of games); turn mean 149.3, median 144, p25-p75 131.5-158.5, min-max 96-276 (n=61); turn histogram (25-turn bins, start turn: n) {'76': 1, '101': 11, '126': 23, '151': 19, '176': 3, '201': 2, '251': 1, '276': 1}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 3 4 1 3 | 25 | 0.41 |
| 2 4 1 3 | 15 | 0.246 |
| 3 4 2 3 | 7 | 0.115 |
| 2 3 1 3 | 3 | 0.049 |
| 2 4 2 3 | 3 | 0.049 |
| 3 2 1 3 | 2 | 0.033 |
| 3 3 0 3 | 1 | 0.016 |
| 3 4 2 2 | 1 | 0.016 |

marginals: speed: {'1': 1, '2': 23, '3': 37}; carry: {'2': 2, '3': 5, '4': 54}; harvest: {'0': 4, '1': 46, '2': 11}; chop: {'2': 2, '3': 59}


**troll_5** (the 5th-1 troll bought): in 16 games (0.072 of games); turn mean 170.94, median 166.0, p25-p75 157.75-182.25, min-max 149-207 (n=16); turn histogram (25-turn bins, start turn: n) {'126': 1, '151': 11, '176': 2, '201': 2}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 4 1 3 | 7 | 0.438 |
| 3 4 1 3 | 5 | 0.312 |
| 3 4 2 3 | 2 | 0.125 |
| 2 4 1 2 | 1 | 0.062 |
| 2 3 0 2 | 1 | 0.062 |

marginals: speed: {'2': 9, '3': 7}; carry: {'3': 1, '4': 15}; harvest: {'0': 1, '1': 13, '2': 2}; chop: {'2': 2, '3': 14}

Opponents' trained talents (for contrast):

| talents | n | share |
|---|---|---|
| 4 3 1 3 | 50 | 0.112 |
| 4 3 1 2 | 41 | 0.092 |
| 2 2 2 2 | 28 | 0.063 |
| 4 3 0 2 | 28 | 0.063 |
| 4 3 0 3 | 23 | 0.051 |
| 2 2 1 1 | 19 | 0.043 |

## 2. Opening (turns 1-30)

Letters: M=MOVE, H=HARVEST, C=CHOP, P=PLANT, K=PICK, D=DROP, I=MINE, T=TRAIN, W=WAIT, -=no command for that troll.

Starting troll, one letter per turn, turns 1-10 (most common patterns):

| pattern | n | share |
|---|---|---|
| MKPKMPMMMM | 17 | 0.076 |
| MMMHMMDMMH | 12 | 0.054 |
| MKPKMPMKPM | 10 | 0.045 |
| MMMMMMMMMM | 8 | 0.036 |
| MKPKMPMKMP | 5 | 0.022 |
| MMHMDMHMDM | 5 | 0.022 |
| MKPKMPMKMM | 4 | 0.018 |
| MKPKMPMMHM | 4 | 0.018 |
| MMMIMMDMMI | 4 | 0.018 |
| MMMMMMMHMM | 4 | 0.018 |
| MKPKMPIMDM | 3 | 0.013 |
| MMMHMMDMMM | 3 | 0.013 |

Starting troll, turns 1-20:

| pattern | n | share |
|---|---|---|
| MMMHMMDMMHMMDMMHMMDM | 8 | 0.036 |
| MKPKMPMMMMHMDMHMDMHM | 2 | 0.009 |
| MMHMPMHMMPMMHMDMHMDM | 2 | 0.009 |
| MMMIMMDMMIMMDMMIMMDM | 2 | 0.009 |
| MMMMMMHMMMMMDMMMMMHM | 2 | 0.009 |
| MKPMMHMPMHMMPMMHMMDH | 2 | 0.009 |
| MIDKPKMPMKMMPMMIDHDM | 1 | 0.004 |
| MKPKMPMKPMM-MM-MMHDH | 1 | 0.004 |

All trolls together, turns 1-10 (letters of one turn joined, turns separated by spaces):

| pattern | n | share |
|---|---|---|
| M K P K M P M M M M | 12 | 0.054 |
| M M M H M M D M M H | 9 | 0.04 |
| M M M M M M M M M M | 7 | 0.031 |
| M K P K M P M K M P | 5 | 0.022 |
| M M M I M M D M M I | 3 | 0.013 |
| M M M M M M H M M M | 3 | 0.013 |
| M K P K M P M M H M | 3 | 0.013 |
| M M H M D M H M D M | 3 | 0.013 |

First occurrences (turn of the first command of that kind; games with it):

| verb | games with it | turn |
|---|---|---|
| HARVEST | 223 | mean 13.61, median 9, p25-p75 4.0-18.0, min-max 2-93 (n=223) |
| PLANT | 223 | mean 13.84, median 5, p25-p75 3.0-19.0, min-max 3-111 (n=223) |
| CHOP | 223 | mean 39.17, median 22, p25-p75 10.0-53.0, min-max 4-231 (n=223) |
| MINE | 171 | mean 43.81, median 34, p25-p75 8.0-70.0, min-max 2-208 (n=171) |
| TRAIN | 223 | mean 19.9, median 6, p25-p75 2.0-26.0, min-max 1-237 (n=223) |
| DROP | 223 | mean 13.18, median 11, p25-p75 7.0-17.0, min-max 3-92 (n=223) |

first action verb of start troll:

| value | n | share |
|---|---|---|
| K | 103 | 0.462 |
| H | 83 | 0.372 |
| I | 31 | 0.139 |
| C | 6 | 0.027 |

first harvest type:

| value | n | share |
|---|---|---|
| LEMON | 127 | 0.57 |
| PLUM | 64 | 0.287 |
| BANANA | 23 | 0.103 |
| APPLE | 9 | 0.04 |

first harvest origin:

| value | n | share |
|---|---|---|
| wild | 196 | 0.879 |
| own | 27 | 0.121 |

first plant type:

| value | n | share |
|---|---|---|
| LEMON | 149 | 0.668 |
| PLUM | 40 | 0.179 |
| BANANA | 19 | 0.085 |
| APPLE | 15 | 0.067 |

first chop type:

| value | n | share |
|---|---|---|
| LEMON | 114 | 0.511 |
| PLUM | 55 | 0.247 |
| BANANA | 48 | 0.215 |
| APPLE | 6 | 0.027 |

first chop origin:

| value | n | share |
|---|---|---|
| wild | 113 | 0.507 |
| opp | 80 | 0.359 |
| own | 30 | 0.135 |

Verb share by turn, turns 1-30 (commands per game, by letter):

| turn | M | H | C | P | K | D | I | T | W |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0 |  |  |  |  |  |  | 0.08 |  |
| 2 | 0.52 | 0.07 |  |  | 0.43 |  | 0.05 | 0.24 |  |
| 3 | 0.7 | 0.08 |  | 0.39 | 0.0 | 0.1 | 0.03 | 0.07 |  |
| 4 | 0.8 | 0.14 | 0.01 | 0.04 | 0.33 |  | 0.05 | 0.06 |  |
| 5 | 1.08 | 0.08 | 0.05 | 0.09 | 0.01 | 0.12 | 0.02 | 0.02 |  |
| 6 | 0.8 | 0.12 | 0.08 | 0.31 | 0.09 | 0.0 | 0.04 | 0.04 |  |
| 7 | 0.88 | 0.13 | 0.13 | 0.09 | 0.01 | 0.19 | 0.06 | 0.01 |  |
| 8 | 0.87 | 0.1 | 0.2 | 0.09 | 0.16 | 0.01 | 0.05 | 0.02 | 0.0 |
| 9 | 0.9 | 0.05 | 0.23 | 0.13 | 0.0 | 0.2 | 0.02 | 0.0 |  |
| 10 | 0.87 | 0.16 | 0.26 | 0.1 | 0.06 | 0.02 | 0.05 | 0.01 | 0.01 |
| 11 | 0.96 | 0.09 | 0.2 | 0.07 | 0.0 | 0.16 | 0.04 | 0.0 |  |
| 12 | 0.99 | 0.1 | 0.26 | 0.06 | 0.05 | 0.03 | 0.03 | 0.0 |  |
| 13 | 0.76 | 0.13 | 0.28 | 0.07 | 0.0 | 0.28 | 0.04 | 0.01 |  |
| 14 | 0.96 | 0.12 | 0.28 | 0.07 | 0.02 | 0.05 | 0.05 | 0.02 | 0.01 |
| 15 | 0.86 | 0.13 | 0.29 | 0.09 | 0.0 | 0.18 | 0.03 | 0.01 |  |
| 16 | 0.95 | 0.2 | 0.25 | 0.07 | 0.04 | 0.05 | 0.04 | 0.01 |  |
| 17 | 0.82 | 0.1 | 0.28 | 0.1 | 0.01 | 0.27 | 0.03 | 0.0 |  |
| 18 | 0.85 | 0.21 | 0.35 | 0.07 | 0.05 | 0.05 | 0.04 | 0.01 | 0.0 |
| 19 | 0.75 | 0.19 | 0.3 | 0.05 | 0.01 | 0.3 | 0.02 |  | 0.0 |
| 20 | 0.89 | 0.23 | 0.32 | 0.06 | 0.01 | 0.09 | 0.02 | 0.03 |  |
| 21 | 0.77 | 0.13 | 0.27 | 0.08 | 0.01 | 0.33 | 0.05 | 0.01 |  |
| 22 | 0.98 | 0.23 | 0.29 | 0.06 | 0.02 | 0.07 | 0.02 | 0.03 |  |
| 23 | 0.79 | 0.18 | 0.31 | 0.09 | 0.02 | 0.25 | 0.05 | 0.01 |  |
| 24 | 1.02 | 0.18 | 0.29 | 0.06 | 0.0 | 0.1 | 0.05 | 0.01 |  |
| 25 | 0.7 | 0.2 | 0.32 | 0.11 | 0.02 | 0.33 | 0.04 | 0.01 | 0.0 |
| 26 | 0.94 | 0.25 | 0.3 | 0.06 | 0.02 | 0.13 | 0.03 | 0.01 |  |
| 27 | 0.78 | 0.18 | 0.32 | 0.09 | 0.03 | 0.33 | 0.04 |  |  |
| 28 | 0.96 | 0.26 | 0.28 | 0.09 | 0.01 | 0.11 | 0.04 |  |  |
| 29 | 0.73 | 0.22 | 0.31 | 0.06 | 0.01 | 0.35 | 0.05 | 0.01 |  |
| 30 | 0.93 | 0.26 | 0.3 | 0.07 | 0.03 | 0.13 | 0.03 | 0.02 |  |

Most common MSG texts (digits replaced by N):

| message | n | share |
|---|---|---|

## 3. Planting

| measure | value |
|---|---|
| PLANT commands per game | mean 39.65, median 41, p25-p75 29.0-50.0, min-max 4-90 (n=223) |
| successful plants per game | mean 39.65, median 41, p25-p75 29.0-50.0, min-max 4-90 (n=223) |
| success rate of PLANT commands | 1.0 |
| distance (BFS over grass) from own shack | mean 2.05, median 2, p25-p75 1.0-3.0, min-max 1-18 (n=8843) |
| distance hist (cells: n; 12 = 12 or more) | {'1': 3791, '2': 2484, '3': 1549, '4': 625, '5': 250, '6': 91, '7': 32, '8': 9, '9': 5, '10': 1, '12': 6} |
| distance from opponent shack | mean 11.03, median 11, p25-p75 8.0-14.0, min-max 1-25 (n=8843) |
| planted next to water | 0.228 |
| next to water, by type | {'PLUM': 0.243, 'LEMON': 0.277, 'APPLE': 0.211, 'BANANA': 0.196} |
| planted on own half of the map | 0.941 |
| planted nearer own shack than opponent's | 0.992 |
| plants per game by 10-turn bucket | {'1-10': 1.25, '11-20': 0.7, '21-30': 0.77, '31-40': 0.83, '41-50': 0.69, '51-60': 0.77, '61-70': 0.73, '71-80': 0.65, '81-90': 0.62, '91-100': 0.75, '101-110': 0.73, '111-120': 0.84, '121-130': 1.01, '131-140': 1.08, '141-150': 1.33, '151-160': 1.65, '161-170': 1.73, '171-180': 1.85, '181-190': 1.92, '191-200': 1.82, '201-210': 1.89, '211-220': 1.89, '221-230': 1.96, '231-240': 1.94, '241-250': 1.9, '251-260': 1.88, '261-270': 1.72, '271-280': 1.74, '281-290': 1.55, '291-300': 1.48} |

By type (successful plants):

| type | n | share |
|---|---|---|
| BANANA | 4243 | 0.48 |
| LEMON | 2456 | 0.278 |
| PLUM | 1722 | 0.195 |
| APPLE | 422 | 0.048 |

Seeds picked at the shack (PICK commands) by type:

| type | n | share |
|---|---|---|
| BANANA | 1948 | 0.57 |
| LEMON | 715 | 0.209 |
| PLUM | 573 | 0.168 |
| APPLE | 179 | 0.052 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA |
|---|---|---|---|---|
| early(1-100) | 0.235 | 0.395 | 0.061 | 0.309 |
| mid(101-200) | 0.201 | 0.254 | 0.03 | 0.515 |
| late(201-300) | 0.172 | 0.245 | 0.056 | 0.526 |

Distance from own shack by type: PLUM: mean 2.13, median 2.0, p25-p75 1.0-3.0, min-max 1-13 (n=1722); LEMON: mean 2.08, median 2.0, p25-p75 1.0-3.0, min-max 1-8 (n=2456); APPLE: mean 1.78, median 1.0, p25-p75 1.0-2.0, min-max 1-18 (n=422); BANANA: mean 2.03, median 2, p25-p75 1.0-3.0, min-max 1-9 (n=4243)

## 4. Harvesting

| measure | value |
|---|---|
| HARVEST commands per game | mean 78.78, median 75, p25-p75 56.0-103.0, min-max 2-178 (n=223) |
| fruits harvested per game (referee count) | mean 85.08, median 79, p25-p75 59.0-112.0, min-max 2-200 (n=223) |
| fruits per HARVEST command | 1.08 |
| HARVEST commands that took nothing | 0.0 |
| distance from own shack of the harvested cell | mean 2.24, median 2, p25-p75 1.0-3.0, min-max 1-20 (n=17569) |
| harvests per game by 10-turn bucket | {'1-10': 0.93, '11-20': 1.49, '21-30': 2.09, '31-40': 2.29, '41-50': 2.49, '51-60': 2.92, '61-70': 3.08, '71-80': 3.35, '81-90': 3.54, '91-100': 3.7, '101-110': 3.9, '111-120': 4.01, '121-130': 3.98, '131-140': 3.96, '141-150': 3.72, '151-160': 3.51, '161-170': 3.04, '171-180': 3.05, '181-190': 2.67, '191-200': 2.52, '201-210': 2.47, '211-220': 2.31, '221-230': 2.25, '231-240': 2.02, '241-250': 1.96, '251-260': 1.74, '261-270': 1.65, '271-280': 1.41, '281-290': 1.52, '291-300': 1.22} |

By the tree's origin (own-planted / wild / planted by the opponent):

| origin | n | share |
|---|---|---|
| own | 12593 | 0.717 |
| wild | 4721 | 0.269 |
| opp | 255 | 0.015 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.584 | 0.404 | 0.012 | 0 |
| mid(101-200) | 0.742 | 0.243 | 0.015 | 0 |
| late(201-300) | 0.857 | 0.127 | 0.016 | 0 |

Fruits harvested by type:

| type | n | share |
|---|---|---|
| LEMON | 7984 | 0.421 |
| PLUM | 4331 | 0.228 |
| BANANA | 3887 | 0.205 |
| APPLE | 2770 | 0.146 |

## 5. Chopping

| measure | value |
|---|---|
| CHOP commands per game | mean 172.35, median 174, p25-p75 137.0-208.0, min-max 32-302 (n=223) |
| chops that landed per game | mean 128.65, median 133, p25-p75 98.0-160.0, min-max 17-232 (n=223) |
| trees felled per game (this player struck the killing turn) | mean 4.48, median 2, p25-p75 0.0-6.0, min-max 0-33 (n=223) |
| wood collected per game | mean 98.17, median 90, p25-p75 59.0-131.0, min-max 11-253 (n=223) |
| turn of the first wood | mean 43.98, median 26, p25-p75 14.0-62.0, min-max 5-238 (n=223) |
| wood by phase (total over games) | {'early(1-100)': 1653, 'mid(101-200)': 7276, 'late(201-300)': 12964} |
| chops per game by 10-turn bucket | {'1-10': 0.97, '11-20': 2.82, '21-30': 3.0, '31-40': 3.42, '41-50': 3.32, '51-60': 3.12, '61-70': 2.95, '71-80': 2.83, '81-90': 2.98, '91-100': 2.83, '101-110': 2.83, '111-120': 3.15, '121-130': 3.47, '131-140': 4.01, '141-150': 4.58, '151-160': 5.51, '161-170': 6.43, '171-180': 6.83, '181-190': 7.08, '191-200': 7.62, '201-210': 7.78, '211-220': 8.04, '221-230': 8.16, '231-240': 9.05, '241-250': 9.0, '251-260': 9.56, '261-270': 10.03, '271-280': 10.42, '281-290': 10.1, '291-300': 10.46} |
| chopped on own half of the map | 0.67 |
| distance from own shack | mean 4.44, median 3, p25-p75 1.0-6.0, min-max 1-20 (n=38433) |
| distance from opponent shack | mean 8.38, median 9, p25-p75 4.0-12.0, min-max 1-25 (n=38433) |

By the tree's origin:

| origin | n | share |
|---|---|---|
| own | 24545 | 0.639 |
| opp | 9060 | 0.236 |
| wild | 4828 | 0.126 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.173 | 0.266 | 0.561 | 0 |
| mid(101-200) | 0.605 | 0.137 | 0.258 | 0 |
| late(201-300) | 0.799 | 0.076 | 0.124 | 0 |

Nearer to whose shack (BFS distance):

| nearer | n | share |
|---|---|---|
| own | 26733 | 0.696 |
| opp | 11251 | 0.293 |
| equal | 449 | 0.012 |

Tree type at the time of the chop:

| type | n | share |
|---|---|---|
| LEMON | 12953 | 0.337 |
| PLUM | 11082 | 0.288 |
| BANANA | 10278 | 0.267 |
| APPLE | 4120 | 0.107 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA | ? |
|---|---|---|---|---|---|
| early(1-100) | 0.292 | 0.486 | 0.039 | 0.183 | 0 |
| mid(101-200) | 0.329 | 0.325 | 0.079 | 0.268 | 0 |
| late(201-300) | 0.265 | 0.299 | 0.144 | 0.293 | 0 |

Tree size at the chop:

| size | n | share |
|---|---|---|
| 1 | 24747 | 0.644 |
| 4 | 12954 | 0.337 |
| 3 | 413 | 0.011 |
| 2 | 319 | 0.008 |

Fruits on the tree at the chop:

| fruits | n | share |
|---|---|---|
| 0 | 31640 | 0.823 |
| 2 | 3628 | 0.094 |
| 1 | 2919 | 0.076 |
| 3 | 246 | 0.006 |

Chop power of the chopping troll:

| chop power | n | share |
|---|---|---|
| 2 | 16848 | 0.438 |
| 3 | 13972 | 0.364 |
| 1 | 7613 | 0.198 |

## 6. Mining

| measure | value |
|---|---|
| MINE commands per game | mean 7.83, median 5, p25-p75 1.0-12.0, min-max 0-57 (n=223) |
| iron collected per game | mean 11.51, median 7, p25-p75 1.0-20.0, min-max 0-66 (n=223) |
| games with at least one MINE | 171 |
| iron per MINE command | 1.47 |
| turn of the first MINE | mean 43.81, median 34, p25-p75 8.0-70.0, min-max 2-208 (n=171) |
| mines per game by 10-turn bucket | {'1-10': 0.38, '11-20': 0.34, '21-30': 0.4, '31-40': 0.37, '41-50': 0.38, '51-60': 0.43, '61-70': 0.47, '71-80': 0.45, '81-90': 0.49, '91-100': 0.53, '101-110': 0.57, '111-120': 0.55, '121-130': 0.54, '131-140': 0.61, '141-150': 0.41, '151-160': 0.27, '161-170': 0.18, '171-180': 0.12, '181-190': 0.08, '191-200': 0.1, '201-210': 0.04, '211-220': 0.03, '221-230': 0.01, '231-240': 0.02, '241-250': 0.04, '251-260': 0.01, '261-270': 0.01, '271-280': 0.01, '291-300': 0.0} |

## 7. Unit roles (verb mix per troll, in creation order)

| troll | games | commands per game | verb mix | talents (n) |
|---|---|---|---|---|
| start_troll | 223 | mean 292.59, median 297, p25-p75 292.0-299.0, min-max 157-300 (n=223) | MOVE 0.451, HARVEST 0.185, DROP 0.156, PLANT 0.087, CHOP 0.084, PICK 0.031, MINE 0.007 | 1 1 1 1 (223) |
| trained_1 | 223 | mean 277.91, median 290, p25-p75 271.0-297.0, min-max 63-299 (n=223) | MOVE 0.44, CHOP 0.303, DROP 0.114, HARVEST 0.071, PLANT 0.04, PICK 0.016, MINE 0.016 | 2 2 2 2 (45); 2 2 1 2 (23); 2 3 1 2 (17); 1 2 2 2 (11) |
| trained_2 | 125 | mean 184.61, median 188, p25-p75 169.0-209.5, min-max 73-248 (n=125) | CHOP 0.408, MOVE 0.389, DROP 0.121, HARVEST 0.039, PLANT 0.019, MINE 0.013, PICK 0.012 | 2 4 1 3 (14); 3 4 1 2 (13); 3 4 1 3 (11); 2 4 1 2 (11) |
| trained_3 | 61 | mean 150.43, median 154, p25-p75 141.5-168.5, min-max 24-204 (n=61) | CHOP 0.416, MOVE 0.412, DROP 0.122, HARVEST 0.02, PLANT 0.017, PICK 0.01, MINE 0.003 | 3 4 1 3 (25); 2 4 1 3 (15); 3 4 2 3 (7); 2 3 1 3 (3) |
| trained_4 | 16 | mean 128.88, median 133.5, p25-p75 117.75-141.5, min-max 93-151 (n=16) | CHOP 0.45, MOVE 0.36, DROP 0.12, HARVEST 0.029, PLANT 0.027, PICK 0.014 | 2 4 1 3 (7); 3 4 1 3 (5); 3 4 2 3 (2); 2 4 1 2 (1) |

## 8. Endgame (last 30 turns)

| measure | value |
|---|---|
| verb mix, last 30 turns | {'MOVE': 0.379, 'CHOP': 0.366, 'DROP': 0.117, 'PLANT': 0.056, 'HARVEST': 0.048, 'PICK': 0.034, 'MINE': 0.0, 'WAIT': 0.0, 'TRAIN': 0.0} |
| verb mix, whole game | {'MOVE': 0.433, 'CHOP': 0.237, 'DROP': 0.132, 'HARVEST': 0.108, 'PLANT': 0.055, 'PICK': 0.021, 'MINE': 0.011, 'TRAIN': 0.003, 'WAIT': 0.0} |
| commands per game in the last 30 turns | 85.8 |
| per game in the last 30 turns | {'plants': 4.82, 'chops': 31.37, 'harvests': 4.15, 'drops': 10.0, 'wood': 17.75} |
| turn of the last DROP | mean 296.21, median 299, p25-p75 297.0-300.0, min-max 156-300 (n=223) |
| turns from the last DROP to the end | mean 2.2, median 1, p25-p75 0.0-3.0, min-max 0-29 (n=223) |
| trees alive at the end per game (own / wild / opp) | {'own': 3.31, 'wild': 5.88, 'opp': 4.25} |
| games ending with no tree on the map | 8 |

Commands per game by verb: {"MOVE": 314.6, "CHOP": 172.3, "DROP": 95.9, "HARVEST": 78.8, "PLANT": 39.7, "PICK": 15.3, "MINE": 7.8, "TRAIN": 1.9, "WAIT": 0.3}

Commands per game by 10-turn bucket:

| turns | MOVE | HARVEST | CHOP | PLANT | PICK | DROP | MINE | TRAIN | WAIT |
|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 8.42 | 0.93 | 0.97 | 1.25 | 1.11 | 0.65 | 0.38 | 0.55 | 0.01 |
| 11-20 | 8.8 | 1.49 | 2.82 | 0.7 | 0.21 | 1.46 | 0.34 | 0.11 | 0.02 |
| 21-30 | 8.61 | 2.09 | 3.0 | 0.77 | 0.19 | 2.13 | 0.4 | 0.12 | 0.0 |
| 31-40 | 8.57 | 2.29 | 3.42 | 0.83 | 0.25 | 2.34 | 0.37 | 0.05 | 0.0 |
| 41-50 | 8.84 | 2.49 | 3.32 | 0.69 | 0.24 | 2.63 | 0.38 | 0.06 | 0.0 |
| 51-60 | 8.78 | 2.92 | 3.12 | 0.77 | 0.26 | 2.93 | 0.43 | 0.05 |  |
| 61-70 | 9.18 | 3.08 | 2.95 | 0.73 | 0.2 | 3.23 | 0.47 | 0.07 |  |
| 71-80 | 9.51 | 3.35 | 2.83 | 0.65 | 0.17 | 3.37 | 0.45 | 0.03 |  |
| 81-90 | 9.35 | 3.54 | 2.98 | 0.62 | 0.14 | 3.59 | 0.49 | 0.05 |  |
| 91-100 | 9.61 | 3.7 | 2.83 | 0.75 | 0.17 | 3.7 | 0.53 | 0.06 |  |
| 101-110 | 9.74 | 3.9 | 2.83 | 0.73 | 0.2 | 4.01 | 0.57 | 0.11 | 0.01 |
| 111-120 | 10.24 | 4.01 | 3.15 | 0.84 | 0.2 | 4.0 | 0.55 | 0.09 | 0.01 |
| 121-130 | 10.71 | 3.98 | 3.47 | 1.01 | 0.26 | 4.03 | 0.54 | 0.1 | 0.01 |
| 131-140 | 11.05 | 3.96 | 4.01 | 1.08 | 0.27 | 3.97 | 0.61 | 0.09 | 0.02 |
| 141-150 | 11.52 | 3.72 | 4.58 | 1.33 | 0.36 | 3.87 | 0.41 | 0.09 | 0.01 |
| 151-160 | 11.63 | 3.51 | 5.51 | 1.65 | 0.46 | 3.65 | 0.27 | 0.1 | 0.01 |
| 161-170 | 11.88 | 3.04 | 6.43 | 1.73 | 0.57 | 3.48 | 0.18 | 0.06 | 0.03 |
| 171-180 | 11.88 | 3.05 | 6.83 | 1.85 | 0.66 | 3.41 | 0.12 | 0.02 | 0.02 |
| 181-190 | 12.16 | 2.67 | 7.08 | 1.92 | 0.61 | 3.37 | 0.08 | 0.01 | 0.01 |
| 191-200 | 11.94 | 2.52 | 7.62 | 1.82 | 0.7 | 3.39 | 0.1 | 0.02 | 0.03 |
| 201-210 | 11.94 | 2.47 | 7.78 | 1.89 | 0.74 | 3.32 | 0.04 | 0.02 | 0.02 |
| 211-220 | 12.21 | 2.31 | 8.04 | 1.89 | 0.69 | 3.19 | 0.03 | 0.0 | 0.01 |
| 221-230 | 12.09 | 2.25 | 8.16 | 1.96 | 0.67 | 3.16 | 0.01 | 0.02 | 0.01 |
| 231-240 | 11.52 | 2.02 | 9.05 | 1.94 | 0.74 | 3.15 | 0.02 | 0.0 |  |
| 241-250 | 11.32 | 1.96 | 9.0 | 1.9 | 0.79 | 3.37 | 0.04 |  | 0.0 |
| 251-260 | 10.95 | 1.74 | 9.56 | 1.88 | 0.86 | 3.27 | 0.01 |  |  |
| 261-270 | 10.82 | 1.65 | 10.03 | 1.72 | 0.77 | 3.32 | 0.01 | 0.0 |  |
| 271-280 | 10.54 | 1.41 | 10.42 | 1.74 | 0.95 | 3.21 | 0.01 | 0.0 | 0.0 |
| 281-290 | 10.53 | 1.52 | 10.1 | 1.55 | 0.9 | 3.39 |  |  | 0.0 |
| 291-300 | 10.22 | 1.22 | 10.46 | 1.48 | 1.0 | 3.3 | 0.0 |  | 0.0 |

DROP: mean 95.89, median 90, p25-p75 72.0-120.0, min-max 17-206 (n=223) commands per game; items per drop mean 1.76, median 1, p25-p75 1.0-2.0, min-max 1-4 (n=21383)

Referee-reported failures per game: {}

## 10. Movement

| measure | value |
|---|---|
| MOVE commands per game | mean 314.57, median 308, p25-p75 241.0-376.0, min-max 109-602 (n=223) |
| BFS distance from the troll's cell to the MOVE target | mean 1.46, median 1.0, p25-p75 1.0-2.0, min-max 1-3 (n=70148) |
| distance histogram (15 = 15 or more) | {'1': 44296, '2': 19711, '3': 6141} |
| turns needed to arrive (distance / speed, rounded up) | mean 1.0, median 1.0, p25-p75 1.0-1.0, min-max 1-1 (n=70148) |
| target unreachable (water, rock, a shack cell) | 0.0 |
| target = the troll's current cell | 0.0 |

What the MOVE target is:

| target | n | share |
|---|---|---|
| tree_own | 26842 | 0.383 |
| other_grass | 23421 | 0.334 |
| own_shack_adjacent | 6746 | 0.096 |
| tree_wild | 6477 | 0.092 |
| tree_opp | 3284 | 0.047 |
| iron_adjacent | 2615 | 0.037 |
| opp_shack_adjacent | 763 | 0.011 |

## What the corpus cannot tell

- Why a decision was taken: no bot state, no evaluation, no stderr. Only commands and the referee's outcomes are recorded.
- A troll's carried inventory between DROPs (the viewer shows one item at a time); carry is inferred only through referee events.
- Whether a MOVE was re-targeted before arrival is visible, but the intended destination of a multi-turn walk is not.
- Tree fruit counts and cooldowns are followed through the viewer diff (stage = size + fruits); the stage shown at a chop is the state after that turn's tick.
- Games of this agent id only; earlier or later versions of the same player's bot may differ.
