# Behaviour profile: tass (agent ids 6665150; 160 games)

## Summary (plain words)

tass = our own bot, for contrast (agent 6665150, the most recent full 160-game batch; the pseudo has 103 agent ids and 10,682 game lines in the corpus, listed in the Notes; win rate 0.600, mean score 190 against 179 — its opponents are weaker than the top four's: 77 % rated 20-25, none of the top four met).

1. Two trolls, always: the second at median turn 8 (96 % by turn 25) with HARVEST 0 in 100 % of games (2 2 0 2 in 20 %, chop 2-3 in 80 %); it never buys a third troll. The top four end with 2.9-3.5 trolls and their third troll arrives around turn 95-120.
2. It does not harvest: 0.8 HARVEST commands per game (the top four 78-112), all in the first 30 turns; 2.6 fruit points per game versus 27-78. Its economy is wood only (99 % of points).
3. Chops from the start: first CHOP at median turn 12, first wood at turn 16; 185 CHOP commands per game (more than any top bot) but only 47 wood (delineate 98), because chop power 1 does 63 % of the chopping and the targets are wild size-4 trees far from home (mean 6.6 cells from the shack; 43 % wild, 32 % opponent-planted, 25 % own).
4. Plants 10 per game, 82 % of them after turn 250 (first PLANT at median turn 252), bananas 57 % and apples 27 %, every one adjacent to the shack (100 % at distance 1); the top four plant 29-40 per game from turn 2 on.
5. Mines almost never (0.5 MINE per game, only in the first 10 turns of 28 % of games).
6. Idles: 25 WAIT commands per game and 28 % of its endgame commands are WAIT; 56 of 160 games ended before turn 300 with no tree left; 60 games end with no tree on the map.
7. Its MOVE targets are one step ahead (1-3 cells) like delineate's; 68 % of MOVE targets are plain grass cells (walking), only 16 % tree cells.
8. It loses to trained-up opponents: 68 % wins against 2-troll opponents, 37 % against 3, 12.5 % against 4 (the top four win 57-72 % against 4-troll opponents).
9. NARRATE debug messages every turn (the owner's instrument), the only bot here whose MSG text describes its own state.
10. Everything the top four do that tass does not: buy a third and fourth troll around turns 95-150 (carry 4, chop 3), harvest 80-130 fruits per game from own-planted lemon/plum/banana trees 1-2 cells from the shack, plant from turn 2 and keep planting (29-40 per game), fell the own farm's trees at size 1, and mine 8-12 iron in mid-game to pay for the chop-3 trolls.

## How to read this

Every table is measured over this player's games in the corpus (`n` = the number of games or events behind the row). Positions and effects come from the referee's own per-turn log inside each replay (exact troll positions after every move, which tree was planted/damaged/harvested), so 'own-planted / wild / opponent-planted' and 'tree type at the time of the chop' are exact for games read from a raw replay. For a game read from `turns.jsonl.gz` only (no raw replay), positions are simulated from MOVE targets and marked approximate. Position source for this profile: {"raw_replay_exact_positions": 160}.

Notes: Pseudo tass appears under 103 agent ids in games.jsonl (id: games) {6561795: 255, 6594200: 200, 6614096: 194, 6553250: 161, 6604529: 161, 6551322: 160, 6551808: 160, 6589709: 160, 6590141: 160, 6592612: 160, 6612307: 160, 6635217: 160, 6636007: 160, 6648254: 160, 6650438: 160, 6652642: 160, 6659743: 160, 6665150: 160, 6633433: 153, 6592495: 152, 6592330: 147, 6551038: 146, 6634986: 146, 6652602: 145, 6645883: 144, 6643835: 143, 6652424: 142, 6536563: 140, 6551304: 140, 6592362: 140, 6643465: 139, 6649868: 137, 6592529: 136, 6644257: 135, 6633209: 133, 6649241: 132, 6593838: 131, 6650168: 131, 6560289: 128, 6553231: 127, 6592131: 127, 6610636: 127, 6631618: 127, 6646733: 127, 6647954: 127, 6664057: 123, 6560269: 121, 6648976: 121, 6663676: 121, 6592097: 118, 6648091: 117, 6642046: 116, 6560240: 115, 6632611: 115, 6642773: 114, 6557204: 113, 6640462: 106, 6634457: 105, 6643172: 105, 6646271: 104, 6647102: 104, 6641617: 103, 6649705: 103, 6632048: 102, 6634792: 102, 6585578: 101, 6559490: 99, 6633935: 98, 6648682: 96, 6650034: 93, 6556873: 88, 6644785: 86, 6592447: 84, 6559513: 83, 6647689: 83, 6647370: 82, 6643278: 80, 6592744: 76, 6642442: 72, 6641056: 68, 6559583: 64, 6645217: 55, 6555355: 52, 6592383: 45, 6640802: 41, 6560353: 29, 6610399: 29, 6556775: 20, 6555394: 15, 6585755: 9, 6589510: 8, 6585739: 5, 6585765: 5, 6585846: 5, 6590136: 5, 6592326: 5, 6592329: 5, 6585801: 4, 6590083: 4, 6560350: 2, 6664418: 2, 6664787: 2, 6536359: 1}; this profile uses [6665150].

## 9. Results and score composition

| measure | value |
|---|---|
| games | 160 |
| win rate | 0.6 |
| seat 0 games | 83 |
| final score | mean 189.87, median 185.5, p25-p75 152.0-228.75, min-max 46.0-376.0 (n=160) |
| opponent final score | mean 178.94, median 147.0, p25-p75 90.0-230.75, min-max 6.0-761.0 (n=160) |
| score margin | mean 10.93, median 12.0, p25-p75 -41.0-89.0, min-max -548.0-343.0 (n=160) |
| fruit points (banked fruit) | mean 2.64, median 1.0, p25-p75 0.0-4.0, min-max 0-11 (n=160) |
| wood points (4 x banked wood) | mean 187.22, median 184.0, p25-p75 148.0-224.0, min-max 44-376 (n=160) |
| wood share of all points | 0.986 |
| final inventory mean (plum, lemon, apple, banana, iron, wood) | [0.07, 0.14, 2.27, 0.16, 0.82, 46.81] |
| games ending before turn 300 | 56 |
| turns per game | mean 276.55, median 300.0, p25-p75 276.75-300.0, min-max 80-300 (n=160) |
| timeout strikes (total) | 0 |

By the opponent's troll count at the end:

| opponent trolls | n | win rate | mean score | mean opp score |
|---|---|---|---|---|
| 1 | 17 | 1.0 | 170.5 | 35.9 |
| 2 | 97 | 0.68 | 185.3 | 144.2 |
| 3 | 30 | 0.367 | 197.5 | 252.6 |
| 4 | 16 | 0.125 | 223.8 | 403.1 |

By own troll count at the end:

| own trolls | n | win rate | mean score |
|---|---|---|---|
| 2 | 160 | 0.6 | 189.9 |

By the opponent's arena score (their ladder rating in the corpus record):

| opponent arena score | n | win rate | mean score |
|---|---|---|---|
| 20-25 | 123 | 0.577 | 192.5 |
| <20 | 35 | 0.686 | 177.1 |
| >=28 | 1 | 0.0 | 236.0 |
| unknown | 1 | 1.0 | 268.0 |

Most frequent opponents:

| opponent | n | share |
|---|---|---|
| 0x6E0FF | 9 | 0.056 |
| DaNinja | 8 | 0.05 |
| Ztrk | 8 | 0.05 |
| GoodDevel | 7 | 0.044 |
| daaskare | 6 | 0.037 |
| _H3R0_ | 6 | 0.037 |
| uta_ccc | 5 | 0.031 |
| Dridriun | 5 | 0.031 |
| mikmak | 5 | 0.031 |
| icecuber | 4 | 0.025 |
| Pduhard- | 4 | 0.025 |
| a76a44 | 4 | 0.025 |

## 1. Training ladder (TRAIN = buy a new troll; talents = speed carry harvest chop)

| measure | value |
|---|---|
| TRAIN commands total / failed | 160 / 0 |
| trolls at the end | mean 2.0, median 2.0, p25-p75 2.0-2.0, min-max 2-2 (n=160) |
| trolls trained per game | 1: 160 games (1.0) |

**troll_2** (the first troll bought): in 160 games (1.0 of games); turn mean 8.82, median 8.0, p25-p75 1.0-14.0, min-max 1-35 (n=160); turn histogram (25-turn bins, start turn: n) {'1': 154, '26': 6}

| talents (speed carry harvest chop) | n | share |
|---|---|---|
| 2 2 0 2 | 32 | 0.2 |
| 2 2 0 3 | 15 | 0.094 |
| 2 2 0 1 | 14 | 0.087 |
| 1 2 0 2 | 11 | 0.069 |
| 3 2 0 2 | 11 | 0.069 |
| 2 1 0 2 | 9 | 0.056 |
| 2 3 0 3 | 8 | 0.05 |
| 2 3 0 2 | 7 | 0.044 |

marginals: speed: {'1': 36, '2': 96, '3': 28}; carry: {'1': 30, '2': 96, '3': 34}; harvest: {'0': 160}; chop: {'1': 32, '2': 86, '3': 42}

Opponents' trained talents (for contrast):

| talents | n | share |
|---|---|---|
| 2 2 0 2 | 37 | 0.18 |
| 2 2 1 1 | 20 | 0.098 |
| 2 2 2 0 | 16 | 0.078 |
| 2 2 1 2 | 15 | 0.073 |
| 2 2 2 1 | 13 | 0.063 |
| 2 2 2 2 | 12 | 0.059 |

## 2. Opening (turns 1-30)

Letters: M=MOVE, H=HARVEST, C=CHOP, P=PLANT, K=PICK, D=DROP, I=MINE, T=TRAIN, W=WAIT, -=no command for that troll.

Starting troll, one letter per turn, turns 1-10 (most common patterns):

| pattern | n | share |
|---|---|---|
| MMMMMMMMMM | 42 | 0.263 |
| MMMMIMMMDM | 9 | 0.056 |
| MMMMHMMMDM | 8 | 0.05 |
| MMMHMMDMMH | 7 | 0.044 |
| MMHMDMHMDM | 7 | 0.044 |
| MMMMMHMMMM | 6 | 0.037 |
| MMMMMMMCCC | 6 | 0.037 |
| MMIMDMIMDM | 5 | 0.031 |
| MMMMMMCCCC | 5 | 0.031 |
| MIDIDIDMMM | 5 | 0.031 |
| MMMMMMMMCC | 5 | 0.031 |
| MMMMMMMMMC | 4 | 0.025 |

Starting troll, turns 1-20:

| pattern | n | share |
|---|---|---|
| MMMMIMMMDMMMMMMMMMMM | 6 | 0.037 |
| MMMMMMMCCCCCCCCCCCCM | 6 | 0.037 |
| MMMHMMDMMHMMDMMMMMMM | 5 | 0.031 |
| MMMMMHMMMMDMMMMMMMMM | 4 | 0.025 |
| MMMMHMMMDMMMHMMMDMMM | 4 | 0.025 |
| MMMMMMMMMMMCCCCCCCCC | 4 | 0.025 |
| MMMMMMMMMMMMMMMMMMMM | 4 | 0.025 |
| MMMMMMMMMMMMMMMCCCCC | 4 | 0.025 |

All trolls together, turns 1-10 (letters of one turn joined, turns separated by spaces):

| pattern | n | share |
|---|---|---|
| M M M M I M M M D MT | 9 | 0.056 |
| M M M H M M D M M H | 7 | 0.044 |
| M M M M M H M M M M | 6 | 0.037 |
| M M M M H M M M D M | 4 | 0.025 |
| M M M M H M M M D MT | 4 | 0.025 |
| MT MM MM MM MM MM MM MM MM MM | 4 | 0.025 |
| M M H M D M H M D M | 4 | 0.025 |
| M M M M M M M M M M | 4 | 0.025 |

First occurrences (turn of the first command of that kind; games with it):

| verb | games with it | turn |
|---|---|---|
| HARVEST | 67 | mean 18.88, median 5, p25-p75 4.0-8.0, min-max 2-291 (n=67) |
| PLANT | 158 | mean 213.0, median 252.0, p25-p75 178.0-255.0, min-max 62-265 (n=158) |
| CHOP | 160 | mean 12.88, median 12.0, p25-p75 5.0-18.0, min-max 3-40 (n=160) |
| TRAIN | 160 | mean 8.82, median 8.0, p25-p75 1.0-14.0, min-max 1-35 (n=160) |
| DROP | 160 | mean 10.52, median 9.0, p25-p75 5.0-13.0, min-max 3-37 (n=160) |
| MINE | 44 | mean 3.45, median 3.0, p25-p75 2.0-5.0, min-max 2-6 (n=44) |

first action verb of start troll:

| value | n | share |
|---|---|---|
| C | 64 | 0.4 |
| H | 52 | 0.325 |
| I | 43 | 0.269 |
| none | 1 | 0.006 |

first harvest type:

| value | n | share |
|---|---|---|
| LEMON | 42 | 0.627 |
| PLUM | 23 | 0.343 |
| APPLE | 2 | 0.03 |

first harvest origin:

| value | n | share |
|---|---|---|
| wild | 66 | 0.985 |
| opp | 1 | 0.015 |

first plant type:

| value | n | share |
|---|---|---|
| BANANA | 158 | 1.0 |

first chop type:

| value | n | share |
|---|---|---|
| PLUM | 65 | 0.406 |
| BANANA | 47 | 0.294 |
| LEMON | 46 | 0.287 |
| APPLE | 2 | 0.013 |

first chop origin:

| value | n | share |
|---|---|---|
| wild | 140 | 0.875 |
| opp | 20 | 0.125 |

Verb share by turn, turns 1-30 (commands per game, by letter):

| turn | M | H | C | P | K | D | I | T | W |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0 |  |  |  |  |  |  | 0.41 |  |
| 2 | 1.27 | 0.04 |  |  |  |  | 0.09 |  | 0.01 |
| 3 | 1.05 | 0.06 | 0.09 |  |  | 0.12 | 0.06 |  | 0.01 |
| 4 | 0.99 | 0.09 | 0.18 |  |  |  | 0.11 |  | 0.03 |
| 5 | 0.77 | 0.07 | 0.26 |  |  | 0.23 | 0.06 |  | 0.02 |
| 6 | 0.96 | 0.07 | 0.27 |  |  | 0.02 | 0.07 | 0.03 | 0.02 |
| 7 | 0.79 | 0.07 | 0.3 |  |  | 0.23 | 0.03 |  | 0.02 |
| 8 | 0.97 | 0.03 | 0.34 |  |  | 0.04 | 0.02 | 0.07 | 0.03 |
| 9 | 0.81 | 0.04 | 0.38 |  |  | 0.25 | 0.01 |  | 0.02 |
| 10 | 0.91 | 0.07 | 0.42 |  |  | 0.04 | 0.04 | 0.12 | 0.02 |
| 11 | 0.96 | 0.03 | 0.46 |  |  | 0.14 | 0.02 |  | 0.03 |
| 12 | 1.01 | 0.04 | 0.53 |  |  | 0.01 | 0.02 | 0.06 | 0.02 |
| 13 | 0.84 | 0.04 | 0.56 |  |  | 0.24 |  | 0.01 | 0.01 |
| 14 | 1.06 | 0.01 | 0.57 |  |  | 0.03 | 0.01 | 0.11 | 0.03 |
| 15 | 1.08 |  | 0.59 |  |  | 0.11 |  | 0.01 | 0.03 |
| 16 | 1.02 | 0.01 | 0.66 |  |  | 0.09 |  | 0.04 | 0.04 |
| 17 | 0.99 | 0.04 | 0.69 |  |  | 0.11 |  | 0.01 | 0.03 |
| 18 | 1.02 | 0.01 | 0.73 |  |  | 0.07 |  | 0.04 | 0.02 |
| 19 | 1.07 | 0.01 | 0.72 |  |  | 0.07 |  |  | 0.02 |
| 20 | 1.09 | 0.01 | 0.69 |  |  | 0.1 |  | 0.03 | 0.01 |
| 21 | 1.04 |  | 0.72 |  |  | 0.14 |  | 0.01 | 0.01 |
| 22 | 1.05 | 0.01 | 0.76 |  |  | 0.11 |  | 0.03 | 0.01 |
| 23 | 1.14 |  | 0.77 |  |  | 0.04 |  |  | 0.01 |
| 24 | 1.03 | 0.01 | 0.79 |  |  | 0.12 |  |  | 0.01 |
| 25 | 1.0 |  | 0.88 |  |  | 0.07 |  | 0.01 | 0.01 |
| 26 | 1.07 | 0.01 | 0.79 |  |  | 0.09 |  |  | 0.01 |
| 27 | 1.0 |  | 0.85 |  |  | 0.11 |  |  | 0.01 |
| 28 | 0.96 | 0.01 | 0.88 |  |  | 0.11 |  | 0.01 | 0.01 |
| 29 | 0.97 |  | 0.91 |  |  | 0.09 |  |  | 0.01 |
| 30 | 0.99 | 0.01 | 0.9 |  |  | 0.07 |  | 0.01 | 0.01 |

Most common MSG texts (digits replaced by N):

| message | n | share |
|---|---|---|
| NARRATE vN t=N uN=TREE(N,N)/TREE(N,N)/r=N/b=N/k=N uN=TREE(N, | 6622 | 0.15 |
| NARRATE vN t=N uN=NONE/TREE(N,N)/r=P/b=N/k=N uN=TREE(N,N)/TR | 4672 | 0.106 |
| NARRATE vN t=N uN=NONE/BANK(N,N)/r=P/b=N/k=N uN=TREE(N,N)/TR | 3062 | 0.069 |
| NARRATE vN t=N uN=TREE(N,N)/TREE(N,N)/r=N/b=N/k=N uN=NONE/BA | 2428 | 0.055 |
| NARRATE vN t=N uN=NONE/TREE(N,N)/r=P/b=N/k=N uN=NONE/TREE(N, | 2386 | 0.054 |
| NARRATE vN t=N uN=TREE(N,N)/TREE(N,N)/r=N/b=N/k=N uN=BANK(N, | 2347 | 0.053 |
| NARRATE vN t=N uN=TREE(N,N)/TREE(N,N)/r=N/b=N/k=N uN=NONE/TR | 2233 | 0.05 |
| NARRATE vN t=N uN=NONE/BANK(N,N)/r=P/b=N/k=N uN=NONE/TREE(N, | 2012 | 0.045 |
| NARRATE vN t=N uN=NONE/TREE(N,N)/r=P/b=N/k=N uN=NONE/BANK(N, | 1712 | 0.039 |
| NARRATE vN t=N uN=NONE/BANK(N,N)/r=P/b=N/k=N uN=NONE/BANK(N, | 1535 | 0.035 |

## 3. Planting

| measure | value |
|---|---|
| PLANT commands per game | mean 10.17, median 11.0, p25-p75 8.0-12.0, min-max 0-22 (n=160) |
| successful plants per game | mean 10.17, median 11.0, p25-p75 8.0-12.0, min-max 0-22 (n=160) |
| success rate of PLANT commands | 1.0 |
| distance (BFS over grass) from own shack | mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-2 (n=1627) |
| distance hist (cells: n; 12 = 12 or more) | {'1': 1623, '2': 4} |
| distance from opponent shack | mean 9.73, median 10, p25-p75 7.0-13.0, min-max 1-17 (n=1627) |
| planted next to water | 0.151 |
| next to water, by type | {'PLUM': 0.174, 'LEMON': 0.194, 'APPLE': 0.095, 'BANANA': 0.168} |
| planted on own half of the map | 0.951 |
| planted nearer own shack than opponent's | 0.99 |
| plants per game by 10-turn bucket | {'61-70': 0.02, '71-80': 0.03, '81-90': 0.08, '91-100': 0.09, '101-110': 0.15, '111-120': 0.18, '121-130': 0.17, '131-140': 0.21, '141-150': 0.17, '151-160': 0.18, '161-170': 0.22, '171-180': 0.21, '181-190': 0.3, '191-200': 0.28, '201-210': 0.28, '211-220': 0.45, '221-230': 0.38, '231-240': 0.34, '241-250': 0.35, '251-260': 1.42, '261-270': 1.94, '271-280': 1.66, '281-290': 0.87, '291-300': 0.2} |

By type (successful plants):

| type | n | share |
|---|---|---|
| BANANA | 926 | 0.569 |
| APPLE | 432 | 0.266 |
| PLUM | 161 | 0.099 |
| LEMON | 108 | 0.066 |

Seeds picked at the shack (PICK commands) by type:

| type | n | share |
|---|---|---|
| BANANA | 927 | 0.569 |
| APPLE | 432 | 0.265 |
| PLUM | 161 | 0.099 |
| LEMON | 108 | 0.066 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA |
|---|---|---|---|---|
| early(1-100) | 0.088 | 0.059 | 0.029 | 0.824 |
| mid(101-200) | 0.073 | 0.042 | 0.248 | 0.637 |
| late(201-300) | 0.106 | 0.073 | 0.277 | 0.544 |

Distance from own shack by type: PLUM: mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-1 (n=161); LEMON: mean 1.0, median 1.0, p25-p75 1.0-1.0, min-max 1-1 (n=108); APPLE: mean 1.0, median 1.0, p25-p75 1.0-1.0, min-max 1-1 (n=432); BANANA: mean 1.0, median 1.0, p25-p75 1.0-1.0, min-max 1-2 (n=926)

## 4. Harvesting

| measure | value |
|---|---|
| HARVEST commands per game | mean 0.82, median 0.0, p25-p75 0.0-1.0, min-max 0-7 (n=160) |
| fruits harvested per game (referee count) | mean 0.82, median 0.0, p25-p75 0.0-1.0, min-max 0-7 (n=160) |
| fruits per HARVEST command | 1.0 |
| HARVEST commands that took nothing | 0.0 |
| distance from own shack of the harvested cell | mean 3.23, median 3, p25-p75 2.0-4.0, min-max 1-15 (n=131) |
| harvests per game by 10-turn bucket | {'1-10': 0.54, '11-20': 0.2, '21-30': 0.04, '281-290': 0.01, '291-300': 0.03} |

By the tree's origin (own-planted / wild / planted by the opponent):

| origin | n | share |
|---|---|---|
| wild | 127 | 0.969 |
| opp | 4 | 0.031 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0 | 0.976 | 0.024 | 0 |
| mid(101-200) | 0 | 0 | 0 | 0 |
| late(201-300) | 0 | 0.857 | 0.143 | 0 |

Fruits harvested by type:

| type | n | share |
|---|---|---|
| LEMON | 81 | 0.618 |
| PLUM | 44 | 0.336 |
| APPLE | 6 | 0.046 |

## 5. Chopping

| measure | value |
|---|---|
| CHOP commands per game | mean 184.56, median 188.5, p25-p75 153.25-218.75, min-max 28-292 (n=160) |
| chops that landed per game | mean 151.83, median 153.0, p25-p75 118.25-184.75, min-max 22-242 (n=160) |
| trees felled per game (this player struck the killing turn) | mean 0.0, median 0.0, p25-p75 0.0-0.0, min-max 0-0 (n=160) |
| wood collected per game | mean 46.89, median 46.0, p25-p75 38.0-56.0, min-max 11-94 (n=160) |
| turn of the first wood | mean 17.38, median 16.0, p25-p75 11.0-22.0, min-max 4-45 (n=160) |
| wood by phase (total over games) | {'early(1-100)': 2625, 'mid(101-200)': 2521, 'late(201-300)': 2357} |
| chops per game by 10-turn bucket | {'1-10': 2.24, '11-20': 6.21, '21-30': 8.24, '31-40': 7.03, '41-50': 6.67, '51-60': 6.8, '61-70': 6.81, '71-80': 6.74, '81-90': 6.63, '91-100': 6.59, '101-110': 6.62, '111-120': 6.83, '121-130': 6.4, '131-140': 6.19, '141-150': 6.34, '151-160': 6.24, '161-170': 5.46, '171-180': 5.76, '181-190': 5.68, '191-200': 5.69, '201-210': 5.08, '211-220': 5.36, '221-230': 5.91, '231-240': 5.09, '241-250': 5.27, '251-260': 5.77, '261-270': 7.33, '271-280': 7.99, '281-290': 8.06, '291-300': 3.52} |
| chopped on own half of the map | 0.52 |
| distance from own shack | mean 6.63, median 6.0, p25-p75 1.0-10.0, min-max 1-25 (n=29530) |
| distance from opponent shack | mean 7.1, median 6.0, p25-p75 2.0-11.0, min-max 1-32 (n=29530) |

By the tree's origin:

| origin | n | share |
|---|---|---|
| wild | 12776 | 0.433 |
| opp | 9531 | 0.323 |
| own | 7223 | 0.245 |

Origin by phase:

| phase | own | wild | opp | none |
|---|---|---|---|---|
| early(1-100) | 0.006 | 0.696 | 0.298 | 0 |
| mid(101-200) | 0.122 | 0.455 | 0.423 | 0 |
| late(201-300) | 0.628 | 0.126 | 0.246 | 0 |

Nearer to whose shack (BFS distance):

| nearer | n | share |
|---|---|---|
| own | 14492 | 0.491 |
| opp | 14156 | 0.479 |
| equal | 882 | 0.03 |

Tree type at the time of the chop:

| type | n | share |
|---|---|---|
| APPLE | 9542 | 0.323 |
| PLUM | 7426 | 0.251 |
| LEMON | 6765 | 0.229 |
| BANANA | 5797 | 0.196 |

Type by phase:

| phase | PLUM | LEMON | APPLE | BANANA | ? |
|---|---|---|---|---|---|
| early(1-100) | 0.439 | 0.307 | 0.105 | 0.149 | 0 |
| mid(101-200) | 0.195 | 0.243 | 0.372 | 0.19 | 0 |
| late(201-300) | 0.107 | 0.131 | 0.508 | 0.253 | 0 |

Tree size at the chop:

| size | n | share |
|---|---|---|
| 1 | 16321 | 0.553 |
| 4 | 9983 | 0.338 |
| 3 | 1729 | 0.059 |
| 2 | 1497 | 0.051 |

Fruits on the tree at the chop:

| fruits | n | share |
|---|---|---|
| 0 | 23004 | 0.779 |
| 2 | 2784 | 0.094 |
| 1 | 2355 | 0.08 |
| 3 | 1387 | 0.047 |

Chop power of the chopping troll:

| chop power | n | share |
|---|---|---|
| 1 | 18508 | 0.627 |
| 2 | 8034 | 0.272 |
| 3 | 2988 | 0.101 |

## 6. Mining

| measure | value |
|---|---|
| MINE commands per game | mean 0.53, median 0.0, p25-p75 0.0-1.0, min-max 0-7 (n=160) |
| iron collected per game | mean 0.53, median 0.0, p25-p75 0.0-1.0, min-max 0-7 (n=160) |
| games with at least one MINE | 44 |
| iron per MINE command | 1.0 |
| turn of the first MINE | mean 3.45, median 3.0, p25-p75 2.0-5.0, min-max 2-6 (n=44) |
| mines per game by 10-turn bucket | {'1-10': 0.49, '11-20': 0.04} |

## 7. Unit roles (verb mix per troll, in creation order)

| troll | games | commands per game | verb mix | talents (n) |
|---|---|---|---|---|
| start_troll | 160 | mean 261.62, median 286.0, p25-p75 244.5-295.0, min-max 61-300 (n=160) | MOVE 0.57, CHOP 0.349, DROP 0.045, PICK 0.015, PLANT 0.015, HARVEST 0.003, MINE 0.002 | 1 1 1 1 (160) |
| trained_1 | 160 | mean 257.42, median 280.5, p25-p75 254.0-290.0, min-max 65-299 (n=160) | MOVE 0.508, CHOP 0.362, DROP 0.082, PICK 0.024, PLANT 0.024 | 2 2 0 2 (32); 2 2 0 3 (15); 2 2 0 1 (14); 1 2 0 2 (11) |

## 8. Endgame (last 30 turns)

| measure | value |
|---|---|
| verb mix, last 30 turns | {'CHOP': 0.412, 'WAIT': 0.281, 'MOVE': 0.111, 'DROP': 0.085, 'PLANT': 0.057, 'PICK': 0.053, 'HARVEST': 0.001} |
| verb mix, whole game | {'MOVE': 0.513, 'CHOP': 0.338, 'DROP': 0.061, 'WAIT': 0.046, 'PICK': 0.019, 'PLANT': 0.019, 'TRAIN': 0.002, 'HARVEST': 0.002, 'MINE': 0.001} |
| commands per game in the last 30 turns | 60.0 |
| per game in the last 30 turns | {'plants': 3.4, 'chops': 24.7, 'harvests': 0.04, 'drops': 5.12, 'wood': 5.25} |
| turn of the last DROP | mean 271.46, median 294.5, p25-p75 270.0-298.0, min-max 57-300 (n=160) |
| turns from the last DROP to the end | mean 5.09, median 4.0, p25-p75 1.0-7.0, min-max 0-45 (n=160) |
| trees alive at the end per game (own / wild / opp) | {'own': 0.01, 'wild': 2.35, 'opp': 3.19} |
| games ending with no tree on the map | 60 |

Commands per game by verb: {"MOVE": 279.7, "CHOP": 184.6, "DROP": 33.0, "WAIT": 25.2, "PICK": 10.2, "PLANT": 10.2, "TRAIN": 1.0, "HARVEST": 0.8, "MINE": 0.5}

Commands per game by 10-turn bucket:

| turns | MOVE | HARVEST | CHOP | PLANT | PICK | DROP | MINE | TRAIN | WAIT |
|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 9.53 | 0.54 | 2.24 |  |  | 0.94 | 0.49 | 0.63 | 0.17 |
| 11-20 | 10.14 | 0.2 | 6.21 |  |  | 0.96 | 0.04 | 0.29 | 0.22 |
| 21-30 | 10.25 | 0.04 | 8.24 |  |  | 0.96 |  | 0.06 | 0.07 |
| 31-40 | 11.79 |  | 7.03 |  |  | 1.04 |  | 0.02 | 0.07 |
| 41-50 | 12.13 |  | 6.67 |  |  | 1.17 |  |  | 0.03 |
| 51-60 | 12.18 |  | 6.8 |  |  | 0.96 |  |  | 0.07 |
| 61-70 | 11.83 |  | 6.81 | 0.02 | 0.02 | 1.12 |  |  | 0.19 |
| 71-80 | 12.04 |  | 6.74 | 0.03 | 0.04 | 0.96 |  |  | 0.2 |
| 81-90 | 11.77 |  | 6.63 | 0.08 | 0.07 | 1.11 |  |  | 0.21 |
| 91-100 | 11.66 |  | 6.59 | 0.09 | 0.09 | 1.04 |  |  | 0.4 |
| 101-110 | 11.56 |  | 6.62 | 0.15 | 0.14 | 1.07 |  |  | 0.34 |
| 111-120 | 11.28 |  | 6.83 | 0.18 | 0.17 | 0.99 |  |  | 0.42 |
| 121-130 | 11.24 |  | 6.4 | 0.17 | 0.18 | 1.11 |  |  | 0.69 |
| 131-140 | 11.2 |  | 6.19 | 0.21 | 0.21 | 1.08 |  |  | 0.66 |
| 141-150 | 11.01 |  | 6.34 | 0.17 | 0.16 | 1.01 |  |  | 0.64 |
| 151-160 | 10.95 |  | 6.24 | 0.18 | 0.19 | 0.97 |  |  | 0.44 |
| 161-170 | 11.19 |  | 5.46 | 0.22 | 0.23 | 1.07 |  |  | 0.57 |
| 171-180 | 10.68 |  | 5.76 | 0.21 | 0.21 | 0.91 |  |  | 0.69 |
| 181-190 | 10.17 |  | 5.68 | 0.3 | 0.31 | 1.06 |  |  | 0.84 |
| 191-200 | 10.1 |  | 5.69 | 0.28 | 0.24 | 0.93 |  |  | 0.89 |
| 201-210 | 10.27 |  | 5.08 | 0.28 | 0.34 | 1.04 |  |  | 0.94 |
| 211-220 | 9.61 |  | 5.36 | 0.45 | 0.43 | 1.03 |  |  | 0.75 |
| 221-230 | 8.81 |  | 5.91 | 0.38 | 0.37 | 1.03 |  |  | 0.95 |
| 231-240 | 9.26 |  | 5.09 | 0.34 | 0.38 | 1.02 |  |  | 0.98 |
| 241-250 | 8.8 |  | 5.27 | 0.35 | 0.31 | 0.93 |  |  | 1.12 |
| 251-260 | 5.19 |  | 5.77 | 1.42 | 1.6 | 1.5 |  |  | 0.75 |
| 261-270 | 1.62 |  | 7.33 | 1.94 | 1.88 | 2.01 |  |  | 0.85 |
| 271-280 | 1.29 |  | 7.99 | 1.66 | 1.61 | 1.71 |  |  | 0.84 |
| 281-290 | 1.32 | 0.01 | 8.06 | 0.87 | 0.84 | 1.26 |  |  | 2.24 |
| 291-300 | 0.88 | 0.03 | 3.52 | 0.2 | 0.13 | 1.04 |  |  | 8.0 |

DROP: mean 33.04, median 33.5, p25-p75 29.0-38.0, min-max 6-58 (n=160) commands per game; items per drop mean 1.46, median 1, p25-p75 1.0-2.0, min-max 1-3 (n=5287)

Referee-reported failures per game: {}

## 10. Movement

| measure | value |
|---|---|
| MOVE commands per game | mean 279.74, median 293.5, p25-p75 246.0-331.5, min-max 56-411 (n=160) |
| BFS distance from the troll's cell to the MOVE target | mean 1.36, median 1, p25-p75 1.0-2.0, min-max 1-3 (n=44759) |
| distance histogram (15 = 15 or more) | {'1': 31154, '2': 11112, '3': 2493} |
| turns needed to arrive (distance / speed, rounded up) | mean 1.0, median 1, p25-p75 1.0-1.0, min-max 1-1 (n=44759) |
| target unreachable (water, rock, a shack cell) | 0.0 |
| target = the troll's current cell | 0.0 |

What the MOVE target is:

| target | n | share |
|---|---|---|
| other_grass | 30369 | 0.679 |
| own_shack_adjacent | 4166 | 0.093 |
| tree_wild | 3759 | 0.084 |
| tree_opp | 3425 | 0.077 |
| iron_adjacent | 2140 | 0.048 |
| opp_shack_adjacent | 893 | 0.02 |
| tree_own | 7 | 0.0 |

## What the corpus cannot tell

- Why a decision was taken: no bot state, no evaluation, no stderr. Only commands and the referee's outcomes are recorded.
- A troll's carried inventory between DROPs (the viewer shows one item at a time); carry is inferred only through referee events.
- Whether a MOVE was re-targeted before arrival is visible, but the intended destination of a multi-turn walk is not.
- Tree fruit counts and cooldowns are followed through the viewer diff (stage = size + fruits); the stage shown at a chop is the state after that turn's tick.
- Games of this agent id only; earlier or later versions of the same player's bot may differ.
