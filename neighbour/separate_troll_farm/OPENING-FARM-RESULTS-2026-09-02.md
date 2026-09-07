# V476 to V481, an opening farm feeding a third troll: measured and rejected — 2026-09-02 (owner-approved multi-mechanism experiment)

The owner approved this multi-mechanism experiment on 2026-09-02 after the loop stopped at the
end of iteration 5, recorded in `THIRD-TROLL-RESULTS-2026-09-02.md`. The design combined an
opening farm with a third troll into one experiment because each mechanism fixes the other's
measured failure: mother bananas alone had no harvester with a reason to visit them in V464 to
V467, and the third troll alone had no supply to fund its bill in V472 to V475. The candidates
were built on the V468 base, `candidate_v468_no_denial_bonus_module.rs`, by
`build_v476_opening_farm.py`, with tests in `test_build_v476_opening_farm.py`. Each was measured
on the development panel of 8 maps, 9941000 to 9941007, both seats, 12 opponent families, 192
paired games, against the V468 baseline bridge, whose own score was 93.0, 176.2 and 247.2 at
turns 100, 200 and 300. The gate required the candidate's own score to be at or above the
baseline at turns 100, 200 and 300, and at least 40 points above it at turn 300.

| candidate | what it adds | own score at 100 / 200 / 300 | wood delta | harvests on the ring, delta | third troll trained (median train turn) | own delta when trained / when not | W/T/L (baseline 177/3/12) | gate |
|---|---|---|---|---|---|---|---|---|
| V476 | plum and lemon mothers on the shack's door cells, planted turns 12 to 60, protected until 270, harvested by the starter on arrival; 2/2/0/2 third troll trained turns 20 to 200 when its bill of 6 plum, 6 lemon, 2 apple, 6 iron is affordable; starter gathers via `early_candidates`, second troll mines iron only once the fruit is complete | 87.7 / 171.9 / 258.0 (-5.3 / -4.2 / +10.8) | +2.6 | +2.6 | 56 of 192 (122) | +26.1 / +4.5 | 176/0/16 | FAIL |
| V478 | as V476, but the starter gathers only from fruit-bearing trees; V476 had camped on fruitless trees | 87.9 / 173.1 / 259.4 (-5.1 / -3.0 / +12.2) | +2.9 | +3.1 | 54 of 192 (120) | +34.4 / +3.5 | 179/0/13 | FAIL |
| V479 | mothers may take the ring's diagonal cells when doors are short, since three-door maps had no cell for a second mother; the seed is carried by a troll from the shack with a 4-turn window | 85.0 / 171.1 / 256.9 (-8.0 / -5.1 / +9.6) | +2.5 | +2.8 | 48 of 192 (114) | +32.0 / +2.1 | 174/2/16 | FAIL |
| V480 | 12-turn seed window; target is the nearest free cell | 86.4 / 174.0 / 259.7 (-6.6 / -2.1 / +12.5) | +3.3 | +3.1 | 51 of 192 (113) | +39.1 / +2.9 | 176/1/15 | FAIL |
| V481 | bill run: while the bill lacks a mother's kind and that mother bears fruit, the starter leaves the apple engine, harvests it, and banks the fruit | 82.8 / 168.0 / 260.2 (-10.2 / -8.2 / +13.0) | +5.5 | -2.3 | 77 of 192 (140) | +24.0 / +5.6 | 177/1/14 | FAIL |

V477, a third troll of talents 2/2/0/3, was built but not measured. The plan ran it only if V476
passed the checkpoints, and V476 did not.

V479's numbers measured the build before commit 9e3feef, which made a carrier that harvests on
arrival keep its pending seed instead of forgetting it; the committed V479 files carry that fix,
and V480 and V481 were built and measured with it.

## What the panels showed

On the two four-door maps, 9941003 and 9941004, the third troll trained in 16 to 18 of 24 games
around turns 91 to 121, with own deltas of +29 to +50 in every variant. On the six three-door
maps it trained in 0 to 3 of 24 games until V481, except on 9941000, the map without water, where
it trained in 9 to 16 of 24 games. Under V481 map 9941005 trained in 21 of 24 games but its own
delta stayed negative at turns 100 and 200. Waits per game rose from 15.7 in the baseline to 26.7
under V481, and MOVE commands per game rose from 193 to 258. Third troll trained, of 24 games,
and own delta at turn 300, per map:

| map | doors | V476 | V478 | V479 | V480 | V481 |
|---|---|---|---|---|---|---|
| 9941000 | 3 | 16, +21.1 | 16, +26.9 | 9, +31.4 | 9, +31.4 | 9, +34.5 |
| 9941001 | 3 | 3, +6.1 | 2, -5.1 | 1, +1.8 | 2, -3.1 | 8, -15.8 |
| 9941002 | 3 | 0, -2.4 | 0, -1.5 | 0, -1.0 | 0, -0.8 | 0, +0.1 |
| 9941003 | 4 | 18, +29.0 | 18, +34.0 | 18, +35.6 | 18, +42.1 | 18, +36.5 |
| 9941004 | 4 | 18, +32.3 | 17, +41.2 | 18, +38.3 | 18, +44.0 | 16, +49.8 |
| 9941005 | 3 | 0, -0.2 | 0, -0.3 | 1, -28.7 | 3, -11.7 | 21, -1.9 |
| 9941006 | 3 | 1, +1.6 | 1, +2.5 | 1, -0.6 | 1, -0.6 | 5, +3.0 |
| 9941007 | 3 | 0, -1.5 | 0, -0.1 | 0, +0.0 | 0, -1.5 | 0, -2.3 |

Four mechanisms explain the pattern. Each was read from the command stream of map 9941005, seat
0, against the resident opponent, the same game in every panel.

- V479's seed-carry window lasted four turns. The second troll picked the plum at turn 13 and
  moved toward its cell, but at speed 1 it needed six moves to circle the shack. The window
  forgot the seed at turn 18, the planner banked the plum at turn 20, and the pick repeated at
  turns 27 and 41, diverting both trolls for about ten turns in every fourteen. This produced the
  -8.0 own delta at turn 100.
- V480's apple engine took priority over the bill gathering. The plum was planted at turn 19 and
  the lemon at turn 30, then the starter made no move at all between turns 41 and 150: 55 HARVEST
  and 55 DROP, alternating, on the watered apple mother, whose fruit regrows every two turns. Its
  own new mothers were never harvested and the bill never filled. On the map without water,
  9941000, the starter moved 33 times in the same span and the third troll trained in 9 of 24
  games.
- V481's bill run pulled the starter off the apple engine on purpose. It harvested the plum
  mother once at turn 32 and five times in a thirty-turn trip, turns 41 to 71, 22 moves, but
  never the lemon, and the bill still did not complete in that game. Harvests on the ring fell
  below the baseline for the first time, -2.3, and the candidate scored 198 in that game
  against the baseline's 214, where V480 had scored 216. Across the panel the third troll
  trained in 77 games but later, median turn 140, and paid +24 instead of +39.
- The economics stayed unfavorable at turn 100 in every variant. Every fruit of the bill cost the
  only harvester three to five turns against an apple engine that paid one point per two turns,
  so twelve fruits cost about 20 to 30 apples before turn 100. A third troll that arrived at turn
  113 to 140 repaid +24 to +39 in the games where it arrived. The end gains of +10 to +13 were the
  largest measured today, ahead of V468's +3 on fresh maps and V472's +4.6, but the dip of -5 to
  -10 at turn 100 appeared in every variant.

## Consequences

1. The item is closed. An opening farm whose bill is fetched by the starter cannot pass the
   checkpoints, because the starter is the apple income.
2. What would be new is the owner's decision, not autonomous work. A second harvester for the
   mothers is one option: the second troll with harvest power 1, which V470 and V471 found unused
   when there was nothing to harvest, now has two mothers to harvest, and the combination was not
   measured. A cheaper bill is another: a 2/1/0/2 troll costs 6 plums and 3 lemons instead of the
   current bill. A third option is parking the starter on a mother whose fruit is due, which
   needs the referee's fruit rule per size from the Java source. Before the farm layer is reused,
   one defect found by the final review must be fixed: `free_doors` counts the apple mother's
   door as free until the apple engine plants it, usually after turn 12, so on a three-door map
   both mothers can take doors and no door stays free once the apple mother arrives;
   `farm_slot_cap` is also dead state in every variant, written each turn and never read.
3. The day's count stands at V455 to V481, 26 candidates, all of which failed the +40 bar. V468's
   +3 remains the only gain.
4. Nothing was submitted.
