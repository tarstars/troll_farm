# norxondor_gorgonax — eulerscheZahl's Legend-league statistics (contest final, #2 with 30.36)

- URL: https://eulerschezahl.github.io/TrollFarm/troll_stats.html (linked from post #1 of the Feedback & Strategies thread: "We generated some statistics for legend league players")
- Fetched: 2026-08-28 (page says "Generated from 30123 matches"; the ranks and scores are the FINAL CONTEST standings, e.g. delineate #1 33.77)
- Author: eulerscheZahl (game author), computed over the Legend-league games at the end of the contest (2026-05-25)
- Language: English (numbers)
- Source type: SECONDARY — measured behaviour of the bot, not the player's description. Averages are per game unless stated. "Train N" = the N-th TRAINED troll (the starting troll is not counted), average of the four talents over the games in which that troll was trained. "Trolls" = number of trolls the bot ended the game with (game counts). Time series are averages at 5-turn intervals; we print every 25 turns (full series in the JSON next to this file).

Nothing below this line is our interpretation; it is the page's numbers re-typed.

---

## Record
Wins: 345  ·  Losses: 267  ·  Draws: 4  ·  Timeouts: 0  ·  Game turns: 293.85  ·  Score: 370.43 - 355.84

## Number of trolls at game end (games)
| 1 troll | 2 trolls | 3 trolls | 4 trolls | 5 trolls | 6 trolls |
|---|---|---|---|---|---|
| 9 (1%) | 115 (19%) | 171 (28%) | 251 (41%) | 66 (11%) | 4 (1%) |

## Average talents of the trained trolls (SPEED = movementSpeed, CARRY = carryCapacity, HARVEST = harvestPower, CHOP = chopPower)
| trained troll | SPEED | CARRY | HARVEST | CHOP |
|---|---|---|---|---|
| train-1 | 2.09 | 2.08 | 1.66 | 1.65 |
| train-2 | 2.29 | 3.08 | 1.15 | 2.00 |
| train-3 | 2.36 | 3.10 | 0.45 | 3.00 |
| train-4 | 2.36 | 4.07 | 0.43 | 3.00 |

## Score over time (average points; turn → own score / opponent score)
| turn | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| own | 17 | 16 | 21 | 26 | 32 | 46 | 79 | 126 | 185 | 240 | 290 | 333 | 366 |
| opp | 19 | 15 | 22 | 29 | 37 | 52 | 79 | 120 | 170 | 222 | 273 | 323 | 369 |

## Shack inventory over time (average items in the shack)
| item | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLUM | 3.0 | 2.3 | 4.1 | 5.8 | 7.3 | 8.5 | 10.0 | 10.6 | 11.2 | 11.3 | 11.0 | 10.8 | 10.7 |
| LEMON | 3.6 | 2.6 | 4.5 | 5.9 | 6.8 | 6.6 | 7.5 | 7.5 | 7.8 | 8.0 | 8.0 | 7.8 | 7.7 |
| APPLE | 4.2 | 3.8 | 3.7 | 3.7 | 3.9 | 3.9 | 4.5 | 5.0 | 5.8 | 6.7 | 7.7 | 8.6 | 9.3 |
| BANANA | 6.0 | 6.2 | 6.5 | 6.9 | 7.2 | 7.5 | 7.4 | 6.9 | 6.0 | 5.4 | 5.0 | 4.5 | 4.2 |
| IRON | 4.0 | 3.3 | 2.9 | 2.9 | 3.5 | 3.4 | 3.2 | 2.4 | 2.2 | 2.2 | 2.2 | 2.3 | 2.4 |
| WOOD | 0.0 | 0.3 | 0.6 | 0.8 | 1.6 | 4.8 | 12.3 | 24.0 | 38.7 | 52.3 | 64.6 | 75.4 | 83.5 |

## Trees planted (cumulative average per game, by type)
| type | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLUM | 0.0 | 1.5 | 2.4 | 3.0 | 3.4 | 3.9 | 4.5 | 5.3 | 6.2 | 7.3 | 8.3 | 9.2 | 10.0 |
| LEMON | 0.0 | 1.8 | 2.9 | 4.0 | 5.0 | 6.1 | 7.2 | 8.1 | 8.7 | 9.2 | 9.7 | 10.4 | 11.1 |
| APPLE | 0.0 | 0.2 | 0.2 | 0.3 | 0.3 | 0.5 | 0.6 | 0.8 | 1.0 | 1.1 | 1.4 | 1.8 | 2.1 |
| BANANA | 0.0 | 0.0 | 0.1 | 0.2 | 0.8 | 1.6 | 2.8 | 4.1 | 5.7 | 6.7 | 7.5 | 8.2 | 8.7 |


> W1 note: this statistics page is the ONLY source found about norxondor_gorgonax's bot. The player never posted on the CodinGame forum (no forum account), has no findable GitHub/blog/other write-up (queries listed in SUMMARY.md). The TrollerPact podium page (https://www.trollerpact.com/, 'Contest Hall of Champions') lists norxondor_gorgonax, delineate, yamo; Astrobytes' post-mortem thanks 'norxondor_gorgonax, fink_ployd and yaichi for giving my bot all kinds of trouble throughout the contest'. That is all.
