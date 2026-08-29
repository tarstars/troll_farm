# Orchard 6 vs orchard 7 — the collected games read like for like (2026-08-29 12:0xZ)

The ladder readings differ (orchard 6: 18.8 at rank 70; orchard 7: 16.7 and 16.6), but each
reading is one batch of 160 games against whatever opponents the site drew, and the apple farm's
rounds showed the draw alone moves a reading by more than a point. So here the same games are
read again, split by the opponent's rating (the number the site shows for that opponent) and by
how many trolls each side ended with. The champion's batch of 08-28 15:22Z is the baseline; the
two orchard 5 batches are shown for context. Source: `local_claude_1/ladder-queue/games-<id>/ladder-read.json`
(one row a game: own score, opponent score, win, the second troll's talents and training turn,
own and opponent troll counts, the opponent's rating).

## The batches

| batch | games | wins–losses | win % | opponents' mean rating | own score | opp score | margin | ended with 3 trolls | ended with 1 troll | vs opponents with 4+ trolls | opponents with 3+ trolls | second troll (median turn) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| champion (08-28 15:22Z, `41208579`) | 160 | 86–74 | 54 | 17.3 | 186 | 196 | −9 | 0 | 0 | 2/22 | 56 % | 8 |
| orchard 5 round 1 (`41207673`) | 160 | 88–72 | 55 | 13.2 | 217 | 209 | +7 | 143 | 10 | 30/54 | 82 % | 23.5 |
| orchard 5 round 2 (`41207963`) | 160 | 80–80 | 50 | 13.5 | 225 | 221 | +4 | 148 | 10 | 23/48 | 91 % | 24 |
| **orchard 6 round 1 (`41209711`)** | 160 | **95–65** | **59** | 16.5 | 209 | 205 | +4 | 134 | 10 | 33/54 | 68 % | 25 |
| **orchard 7 round 1 (`41209967`)** | 160 | 88–72 | 55 | 15.6 | 230 | 217 | +13 | 147 | 1 | 32/51 | 81 % | 24 |
| **orchard 7 round 2 (`41210228`)** | 162 | 83–79 | 51 | 16.7 | 223 | 234 | −10 | 145 | 1 | 18/47 | 77 % | 20 |

## Win rate by the opponent's rating (wins/games)

| batch | opponent below 14 | 14 to 18 | 18 to 22 | 22 and above |
|---|---|---|---|---|
| champion (08-28) | 1/1 | 71/124 = 57 % | 14/33 = 42 % | 0/2 |
| orchard 5 round 1 | 49/75 = 65 % | 33/74 = 45 % | 0/3 | 0/2 |
| orchard 5 round 2 | 59/96 = 61 % | 18/57 = 32 % | 1/3 | 0/2 |
| **orchard 6 round 1** | 16/18 = 89 % | **49/78 = 63 %** | **27/59 = 46 %** | 0/2 |
| **orchard 7 round 1** | 13/16 = 81 % | **73/138 = 53 %** | 1/3 | 0/2 |
| **orchard 7 round 2** | 0/1 | **80/154 = 52 %** | 1/3 | 1/3 |

## Own score by how many trolls we ended with

| batch | ended with 1 troll | ended with 2 trolls | ended with 3 trolls |
|---|---|---|---|
| orchard 5 round 1 | 10 games, own 70 / opp 147, 30 % wins | 7 games, 95 / 116, 43 % | 143 games, 233 / 218, 57 % |
| orchard 5 round 2 | 10 games, 75 / 248, 10 % | 2 games, 86 / 214, 0 % | 148 games, 237 / 219, 53 % |
| **orchard 6 round 1** | 10 games, 70 / 302, 30 % | 16 games, 108 / 136, 38 % | **134 games, 231 / 206, 64 %** |
| **orchard 7 round 1** | 1 game (the opponent crashed) | 12 games, 139 / 212, 8 % | **147 games, 239 / 218, 59 %** |
| **orchard 7 round 2** | 1 game (the opponent crashed) | 16 games, 125 / 217, 12 % | **145 games, 236 / 237, 55 %** |

## What it says

1. **Orchard 6's edge over orchard 7 is not the draw.** In the one rating band with many games on
   both sides (opponents rated 14 to 18), orchard 6 won 63 % and orchard 7 won 53 % and 52 %. The
   gap is ten points on 78 against 292 games — about one and a half standard errors, so
   suggestive rather than settled, but it points the same way as the readings.
2. **Orchard 7's fix of the lone-troll games worked** (10 games a batch became 1), and those ten
   games were heavy losses in orchard 6 (own 70 against 302). That fix is worth keeping.
3. **But orchard 7's main line got worse**: with the third troll in hand it won 59 % and 55 %
   where orchard 6 won 64 %, and it let the opponents score more (217–234 against 206). One of
   the other two changes in orchard 7 — the 2 + 2 fruit reserve before planting, or the orchard
   cells within two steps of the tent instead of on the doors — costs more than the fix gains.
4. **All the orchard bots score more than the champion (209–230 against 186) and let the opponent
   score more too (205–234 against 196).** The champion's batch had −9 of margin at 54 % wins; the
   orchards run at +4 to +13 at 55–59 %. The orchard line wins by out-producing, not by denial.

## The recommendation (for the owner, for when the platform is ours again)

"Orchard 8" = orchard 6 plus the never-abandon rule only — one variable, one hour, one reading.
If it holds orchard 6's 64 % with the third troll and removes the ten lone-troll losses, the
reading should sit above 18.8. The reserve and the cell rule can be tested one at a time after
it, if at all. The alternative is a second reading of orchard 6 as it is, to shrink the ±1.5.
