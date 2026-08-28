# delineate — eulerscheZahl's Legend-league statistics (contest final, #1 with 33.77)

- URL: https://eulerschezahl.github.io/TrollFarm/troll_stats.html (linked from post #1 of the Feedback & Strategies thread: "We generated some statistics for legend league players")
- Fetched: 2026-08-28 (page says "Generated from 30123 matches"; the ranks and scores are the FINAL CONTEST standings, e.g. delineate #1 33.77)
- Author: eulerscheZahl (game author), computed over the Legend-league games at the end of the contest (2026-05-25)
- Language: English (numbers)
- Source type: SECONDARY — measured behaviour of the bot, not the player's description. Averages are per game unless stated. "Train N" = the N-th TRAINED troll (the starting troll is not counted), average of the four talents over the games in which that troll was trained. "Trolls" = number of trolls the bot ended the game with (game counts). Time series are averages at 5-turn intervals; we print every 25 turns (full series in the JSON next to this file).

Nothing below this line is our interpretation; it is the page's numbers re-typed.

---

## Record
Wins: 525  ·  Losses: 146  ·  Draws: 2  ·  Timeouts: 0  ·  Game turns: 297.0  ·  Score: 418.48 - 297.77

## Number of trolls at game end (games)
| 1 troll | 2 trolls | 3 trolls | 4 trolls | 5 trolls | 6 trolls |
|---|---|---|---|---|---|
| 4 (1%) | 254 (38%) | 179 (27%) | 179 (27%) | 53 (8%) | 4 (1%) |

## Average talents of the trained trolls (SPEED = movementSpeed, CARRY = carryCapacity, HARVEST = harvestPower, CHOP = chopPower)
| trained troll | SPEED | CARRY | HARVEST | CHOP |
|---|---|---|---|---|
| train-1 | 1.96 | 2.22 | 1.52 | 2.00 |
| train-2 | 2.47 | 3.35 | 0.98 | 2.50 |
| train-3 | 2.67 | 3.70 | 1.04 | 2.90 |
| train-4 | 2.72 | 3.89 | 1.02 | 2.89 |

## Score over time (average points; turn → own score / opponent score)
| turn | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| own | 23 | 17 | 24 | 35 | 47 | 63 | 85 | 119 | 168 | 227 | 296 | 366 | 421 |
| opp | 18 | 15 | 21 | 28 | 36 | 47 | 66 | 94 | 132 | 172 | 214 | 259 | 296 |

## Shack inventory over time (average items in the shack)
| item | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLUM | 5.5 | 2.5 | 3.3 | 4.7 | 6.0 | 6.7 | 7.0 | 6.8 | 6.8 | 6.9 | 6.9 | 6.8 | 6.6 |
| LEMON | 5.7 | 2.6 | 4.2 | 6.4 | 8.0 | 8.9 | 8.8 | 7.9 | 7.3 | 7.2 | 7.2 | 7.2 | 7.2 |
| APPLE | 5.9 | 3.5 | 3.2 | 3.4 | 3.6 | 3.8 | 4.1 | 4.2 | 4.4 | 4.6 | 5.0 | 5.5 | 5.9 |
| BANANA | 5.9 | 6.0 | 6.3 | 6.8 | 7.4 | 8.2 | 8.7 | 9.0 | 9.1 | 8.5 | 7.8 | 6.7 | 5.9 |
| IRON | 5.5 | 3.2 | 3.7 | 4.7 | 5.1 | 5.3 | 5.2 | 4.6 | 4.0 | 3.6 | 3.4 | 3.4 | 3.4 |
| WOOD | 0.0 | 0.6 | 1.8 | 3.4 | 5.5 | 8.8 | 14.1 | 22.8 | 35.1 | 50.0 | 67.2 | 85.0 | 98.7 |

## Trees planted (cumulative average per game, by type)
| type | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLUM | 0.0 | 0.7 | 1.2 | 1.6 | 1.9 | 2.4 | 3.0 | 3.9 | 4.9 | 5.8 | 6.7 | 7.5 | 8.3 |
| LEMON | 0.0 | 1.1 | 1.8 | 2.3 | 2.6 | 3.0 | 3.5 | 4.4 | 5.4 | 6.4 | 7.3 | 8.1 | 8.8 |
| APPLE | 0.0 | 0.1 | 0.2 | 0.2 | 0.3 | 0.3 | 0.4 | 0.6 | 0.7 | 1.0 | 1.2 | 1.3 | 1.5 |
| BANANA | 0.0 | 0.3 | 0.6 | 1.1 | 1.8 | 2.8 | 4.5 | 6.7 | 9.4 | 12.8 | 16.1 | 19.3 | 21.4 |
