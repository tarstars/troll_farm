# V548 second harvester result

## Design and build

V548 rebuilt exact V481, then added V471's harvest-power-one opening enumeration and one-apple
reserve. Both ordinary fruit gathering for the third-troll bill and the mother-farm bill run were
assigned to the second, highest-id worker so the starter could retain its apple harvest/drop loop.
`free_doors` was also corrected to reserve the planned apple-mother door before the apple tree
appeared, preserving a usable shack door on three-door maps.

The compact source was 93,625 UTF-16 units, SHA-256
`562f00193854b0cbbececc78db3586b74b9d709a7bcdcfd7d3def033855a086c`. Readable and compact
forms compiled and emitted identical sample commands. Ten focused builder and dependency tests
passed before the panel; the final builder, gate and diagnostic suite passed 18 tests. Candidate
planning latency was 1.616 ms p95 and 5.42 ms maximum.

## Matched V481 comparison

V481 and V548 were measured on the same 192 map/seat/opponent keys (seeds 9,941,000--9,941,007,
both seats and 12 opponent families). Their V468 scores and full baseline command streams matched;
only the candidate-dependent `baseline_divergent_command` field differed.

| measure | V481 | V548 | delta |
|---|---:|---:|---:|
| own score at turn 100 | 82.80 | 52.31 | -30.50 |
| own score at turn 200 | 167.99 | 149.55 | -18.44 |
| final own score | 260.24 | 255.36 | -4.88 |
| final opponent score | 119.08 | 137.59 | +18.51 |
| final margin | 141.16 | 117.77 | -23.39 |
| wood | 50.52 | 43.34 | -7.17 |
| ring harvests | 66.01 | 93.21 | +27.20 |
| final workers | 2.401 | 2.698 | +0.297 |
| third troll trained | 77/192 | 134/192 | +57 |
| median third-train turn | 140 | 105 | -35 |
| W/T/L | 177/1/14 | 165/0/27 | -12/-1/+13 |

Every first trained troll kept V481's movement/carry/chop tuple and changed harvest power from zero
to one: 3/2/1/2 in 96 games and each of 1/2/1/3, 2/2/1/2, 1/2/1/1 and 3/2/1/1 in 24. The
second harvester did its assigned work: total HARVEST commands rose from 68.71 to 99.78 per game,
ring harvests rose by 27.20, and the third troll arrived in 57 more games, 35 turns earlier. But
the worker stopped being the main axe: total CHOP commands fell from 152.82 to 136.55, wood fell
7.17, and the fruit plus earlier third troll did not repay that five-points-per-wood loss.

Margin improved in 67 games, tied in one and regressed in 124; paired mean margin fell 23.39 with
standard error 4.37. This was not caused only by legality noise: in the 91 V548 games with zero
issues, turn-100 score still fell 33.66 versus V481 and final score gained only 1.40 while opponents
gained 19.43.

## Collision defect and gate verdict

V548 did expose a second defect. It recorded 1,271 noncritical `move_blocked` issues in 101 games,
with 1,052 concentrated in eight games; critical and unclassified issues remained zero. In map
9,941,006, seat 0 versus `legend_balanced`, the starter planted and occupied the apple mother at
(7,9), then alternated HARVEST/DROP while the second troll issued `MOVE 2 7 9` 148 times and the
referee recorded 148 blocked moves. Moving ordinary third-bill fruit gathering from the starter to
the second made the static-distance planner target the occupied apple mother without a collision-
safe route. The fixed free-door accounting cannot prevent that separate natural-fruit path jam.

Against required V468, V548 scored 52.3 versus 93.0 at turn 100 (-40.7), 149.5 versus 176.2 at
turn 200 (-26.6), and 255.4 versus 247.2 at turn 300 (+8.1). W/T/L was 165/0/27 versus
177/3/12, opponents' mean score rose 29.4, and the required +40 final gain was absent. The second
harvester allocation therefore fails even outside its collision defect. No fresh-map holdout,
packaging audit, or platform submission was opened.

V548 panel SHA-256:
`f86fcb0aa43512382e20a61b8813b6ce3294d897cff08247b08fc2b50254cc67`.
Gate-report SHA-256:
`14fea6ee685384e95071ad55c52905bfff374195d858a522bd2a36bfcd8bd7ad`.
Diagnostic-report SHA-256:
`bb4d5c7ae0cbf6e94c6db3de1ebcb197f127b6118eadd1582863d2cb1005da6f`.
