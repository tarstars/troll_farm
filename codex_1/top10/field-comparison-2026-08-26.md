# What the strong two-troll bots do that we do not

Date: 2026-08-26. Task: `20260826-track-t-top10-field-comparison`.

## Data and reproducibility

- Game summary corpus: `data/processed/games.jsonl`, 23,613 games, SHA-256 `150a5507e90c2c00a5d22b34abf19b7a0ad933fc3b31e3abf3521d3bc4dc4d24`.
- Turn corpus: `data/processed/turns.jsonl.gz`, 13,313,072 seat-turn rows, SHA-256 `1e0ea236a3f0b813eae29d5ba4ec01564ab013984c0064be0ed8330fa5a66726`; 0 parse failures and 12 missing seat-turns, all turn-1 timeouts.
- Commands: `python3 codex_1/top10/field_comparison.py --output codex_1/top10/field-comparison-first-table-2026-08-26.md` and `python3 codex_1/top10/per_turn_field_comparison.py --out codex_1/top10/per-turn-field-comparison-2026-08-26.json`.
- The JSON contains the same per-turn columns for all 25 peers and our 10,274 `tass` game-seats. The compact tables below show the peers that define the main contrast.

The turn corpus records commands the bots issued, not whether the referee accepted them. “Own-planted” below therefore means that a command was issued at the unit's last-known coordinate after the same seat issued a PLANT there. It is strong behavioral evidence, but not a successful-harvest ownership ledger. Near-shack distance and the exact goal-based parked-troll detectors cannot be reconstructed from this export; those cells are named unavailable rather than guessed.

## 1. Who and score composition

All 25 historically identified agents are present. The complete identity table, game counts, score at collection, score composition, training, and successful plant totals is in `field-comparison-first-table-2026-08-26.md`. The leading contrast is:

| bot | historical rank | games | raw score/game | fruit points | wood points | successful banana plants/game |
|---|---:|---:|---:|---:|---:|---:|
| yaichi | 7 | 222 | 252.4 | 7.2 | 245.2 | 29.03 |
| Stounate | 8 | 303 | 198.7 | 17.3 | 181.4 | 27.26 |
| skotz | 10 | 184 | 269.7 | 8.1 | 261.6 | 36.20 |
| goq | 29 | 269 | 247.6 | 10.8 | 236.8 | 27.57 |
| **ours** | — | 10,274 | 187.4 | 5.4 | 182.0 | 5.95 |

Wood supplies more than 90% of score for these bots. The banana loop is therefore primarily a renewable **wood** loop, not banana points banked at the end.

The successful-plant totals above come from the game summaries. Section 3 instead counts issued PLANT commands from the independent turn corpus. The two measures agree to two decimals for all four heavy planters; ours differs slightly (5.95 successful plants versus 5.98 issued commands).

## 2. Training

| bot | second troll, mean turn | games training a third troll |
|---|---:|---:|
| yaichi | 18.1 | 0.0% |
| Stounate | 25.6 | 0.0% |
| skotz | 28.3 | 0.0% |
| goq | 25.5 | 0.0% |
| **ours** | 8.7 | 0.9% |

The leaders do not win by training the second troll earlier. They train it later and keep the two-worker roster productive, consistent with the existing constraint that worker-two timing is closed as a lever.

## 3. Planting and the “wood farm”

Banana PLANT commands per game by turn bucket:

| bot | turns 1–50 | 51–100 | 101–150 | 151+ | issued PLANT commands/game |
|---|---:|---:|---:|---:|---:|
| yaichi | 5.87 | 6.13 | 5.19 | 11.83 | 29.03 |
| Stounate | 4.54 | 5.27 | 4.08 | 13.38 | 27.26 |
| skotz | 4.82 | 6.39 | 6.73 | 18.26 | 36.20 |
| goq | 3.17 | 4.65 | 3.70 | 16.04 | 27.57 |
| **ours** | **0.05** | **0.32** | **0.88** | **4.74** | **5.98** |

The heavy planters start immediately; ours is almost entirely a late-game behavior. Their later command chain also looks like a crop-to-wood lifecycle:

| bot | HARVEST at own-planted coordinate/game | CHOP at own-planted coordinate/game | mean plant→chop turns |
|---|---:|---:|---:|
| yaichi | 21.12 | 59.53 | 25.8 |
| Stounate | 28.65 | 39.83 | 53.9 |
| skotz | 30.20 | 67.23 | 25.6 |
| goq | 22.87 | 67.34 | 40.2 |
| **ours** | **2.85** | **47.08** | **4.6** |

This answers the sharpened question: yes, the heavy banana planters repeatedly issue HARVEST and later CHOP on their own planted coordinates. Ours rarely reaches the harvest part and chops a recently planted coordinate about six to twelve times sooner. Example games for every provenance class are stored in the JSON; among the heavy-planter examples are `893407296` (yaichi), `891857137` (Stounate), `895862081` (skotz), and `893996642` (goq).

## 4. Suppression

| bot | CHOP commands at opponent-planted coordinate/game | near opponent shack |
|---|---:|---|
| yaichi | 2.46 | unavailable: shack/state coordinates absent |
| Stounate | 0.94 | unavailable |
| skotz | 0.53 | unavailable |
| goq | 1.59 | unavailable |
| **ours** | **8.73** | unavailable |

The command chain does not support “the leaders suppress more.” Ours issues substantially more chops at coordinates the opponent previously tried to plant. The leaders' difference is production persistence, not a missing suppression reflex.

## 5. Last 30 turns

Issued commands per game in the final 30 turns:

| bot | PLANT | HARVEST | CHOP | DROP | PICK | MOVE |
|---|---:|---:|---:|---:|---:|---:|
| yaichi | 1.87 | 1.87 | 14.16 | 3.64 | 0.00 | 38.19 |
| Stounate | 2.41 | 0.49 | 9.74 | 5.70 | 3.43 | 37.17 |
| skotz | 3.30 | 4.67 | 12.38 | 3.79 | 0.00 | 34.88 |
| goq | 1.93 | 0.50 | 21.50 | 3.93 | 0.99 | 32.18 |
| **ours** | **3.40** | **0.38** | **23.97** | **5.41** | **3.16** | **7.96** |

Ours does not lack terminal planting or banking commands. It lacks the earlier crop generations that make terminal HARVEST productive; skotz is the clearest late-harvest example.

Ours also issues far fewer MOVE commands in this window (7.96 per game versus 32.18–38.19 for the four leaders), even while issuing the most CHOP commands. This may be real endgame parking or an emission-level difference between WAIT and MOVE; the available command corpus does not distinguish them, so it remains unexplained.

## 6. Idle and contention

| bot | seat-turns with no work verb | same-target MOVE turns/game |
|---|---:|---:|
| yaichi | 35.3% | 2.70 |
| Stounate | 35.3% | 0.00 |
| skotz | 35.5% | 0.00 |
| goq | 31.8% | 1.64 |
| **ours** | **35.5%** | **0.33** |

These are deliberately labeled proxies: “no work verb” means no issued HARVEST/CHOP/DROP/MINE/PLANT/PICK/TRAIN in that seat-turn, and same-target means two own MOVE commands target the same coordinate. They are not the P3/P4 goal-based detectors. On the observable proxy, generic idle is not the differentiator.

## Ranked tricks and estimated value

1. **Start a renewable banana-to-wood loop in the first 50 turns.** The top three issue 4.5–5.9 early banana plants/game; ours 0.05. Association estimate, not causal: their raw own-score advantage over our pooled games is about +11 to +82 points/game. Games: `893407296`, `891857137`, `895862081`.
2. **Harvest the planted crop before clearing it for wood.** Heavy planters issue 21–30 own-coordinate HARVEST commands/game; ours 2.85. Estimated value is not separately identifiable from trick 1; the same +11 to +82 raw-score association is the honest bound. Games: the three above plus `893996642`.
3. **Let the crop mature before chopping.** Their mean command-chain plant→chop delay is 26–54 turns; ours 4.6. Estimated value is again bundled with the farm lifecycle, not an additive claim.
4. **Maintain production through the endgame.** skotz issues 4.67 HARVEST commands in the last 30 turns versus our 0.38. Its raw-score association is +82/game, heavily confounded by opponent and map mix.

## Banana-farm decision

Yes: a banana farm is a prominent behavior of three of the historical top ten and goq. More precisely, it is a persistent banana-to-wood production loop: early planting, repeated harvesting on own planted coordinates, then delayed chopping. It is not universal—Escdemon, therealbeef, and yamo sit near our six banana plants/game—and four historical b100 games remain far too few for a theft-versus-own-crop claim. The useful design target is therefore not “plant more bananas”; it is the complete lifecycle with maturation, self-harvest, delayed wood recovery, and opponent-safety gates. That matches the earlier D101 result and explains why isolated farm grafts failed.
