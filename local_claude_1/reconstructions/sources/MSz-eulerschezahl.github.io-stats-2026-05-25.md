# MSz — eulerscheZahl's Legend-league statistics (contest final, #10 with 27.25)

- URL: https://eulerschezahl.github.io/TrollFarm/troll_stats.html (linked from post #1 of the Feedback & Strategies thread: "We generated some statistics for legend league players")
- Fetched: 2026-08-28 (page says "Generated from 30123 matches"; the ranks and scores are the FINAL CONTEST standings, e.g. delineate #1 33.77)
- Author: eulerscheZahl (game author), computed over the Legend-league games at the end of the contest (2026-05-25)
- Language: English (numbers)
- Source type: SECONDARY — measured behaviour of the bot, not the player's description. Averages are per game unless stated. "Train N" = the N-th TRAINED troll (the starting troll is not counted), average of the four talents over the games in which that troll was trained. "Trolls" = number of trolls the bot ended the game with (game counts). Time series are averages at 5-turn intervals; we print every 25 turns (full series in the JSON next to this file).

Nothing below this line is our interpretation; it is the page's numbers re-typed.

---

## Record
Wins: 314  ·  Losses: 319  ·  Draws: 1  ·  Timeouts: 0  ·  Game turns: 297.28  ·  Score: 480.26 - 480.77

## Number of trolls at game end (games)
| 1 troll | 2 trolls | 3 trolls | 4 trolls |
|---|---|---|---|
| 1 (0%) | 70 (11%) | 266 (42%) | 297 (47%) |

## Average talents of the trained trolls (SPEED = movementSpeed, CARRY = carryCapacity, HARVEST = harvestPower, CHOP = chopPower)
| trained troll | SPEED | CARRY | HARVEST | CHOP |
|---|---|---|---|---|
| train-1 | 1.67 | 1.70 | 1.47 | 1.00 |
| train-2 | 2.04 | 4.00 | 1.00 | 2.71 |
| train-3 | 2.05 | 4.00 | 0.00 | 2.87 |
| train-4 | (never trained) | | | |

## Score over time (average points; turn → own score / opponent score)
| turn | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| own | 13 | 10 | 19 | 23 | 28 | 58 | 117 | 183 | 250 | 313 | 373 | 430 | 474 |
| opp | 19 | 16 | 21 | 29 | 40 | 59 | 92 | 146 | 212 | 282 | 352 | 421 | 479 |

## Shack inventory over time (average items in the shack)
| item | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLUM | 2.1 | 2.5 | 4.6 | 4.9 | 5.1 | 5.0 | 6.4 | 8.7 | 11.2 | 13.8 | 16.3 | 18.7 | 21.1 |
| LEMON | 2.1 | 1.9 | 8.1 | 10.5 | 10.5 | 8.4 | 7.8 | 8.7 | 10.2 | 11.9 | 13.7 | 15.3 | 16.8 |
| APPLE | 2.7 | 2.7 | 3.1 | 3.0 | 2.9 | 3.1 | 4.8 | 7.7 | 11.6 | 16.0 | 21.0 | 26.3 | 30.7 |
| BANANA | 5.8 | 3.2 | 3.4 | 4.0 | 4.9 | 6.6 | 8.0 | 8.7 | 9.3 | 10.0 | 10.7 | 11.2 | 11.9 |
| IRON | 4.0 | 5.9 | 8.0 | 7.4 | 7.2 | 4.8 | 2.8 | 2.0 | 1.6 | 1.6 | 1.6 | 1.6 | 1.7 |
| WOOD | 0.0 | 0.0 | 0.1 | 0.1 | 1.1 | 8.8 | 22.6 | 37.4 | 51.9 | 65.4 | 77.8 | 89.7 | 98.4 |

## Trees planted (cumulative average per game, by type)
| type | 0 | 25 | 50 | 75 | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | 295 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLUM | 0.0 | 1.6 | 1.8 | 1.9 | 2.1 | 2.6 | 3.4 | 4.4 | 5.4 | 6.5 | 7.3 | 8.2 | 8.6 |
| LEMON | 0.0 | 2.3 | 2.7 | 3.0 | 3.3 | 4.0 | 5.0 | 6.1 | 6.9 | 7.7 | 8.4 | 9.1 | 9.3 |
| APPLE | 0.0 | 0.6 | 0.6 | 0.7 | 0.8 | 0.9 | 1.1 | 1.4 | 1.7 | 2.1 | 2.5 | 2.9 | 3.1 |
| BANANA | 0.0 | 2.7 | 3.3 | 3.8 | 4.2 | 4.9 | 5.6 | 6.4 | 7.1 | 7.7 | 8.2 | 8.6 | 8.9 |


> W1 note: this statistics page is the ONLY Troll-Farm-specific source found about MSz's bot. MSz's forum account (created 2020) has NO post about Spring Challenge 2026; his post-mortem repository https://github.com/marekesz/contests (one branch 'main', last commit 2025-01-29) holds post-mortems for 2022–2024 contests only (archived as MSz-github.com-marekesz-earlier-postmortems-2024.md for his usual toolkit). Note also the contest rank: MSz was #10 in the contest (27.25); the #4 (27.72) of the current multiplayer ladder is a later submission.
