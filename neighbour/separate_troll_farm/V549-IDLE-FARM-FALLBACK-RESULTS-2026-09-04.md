# V549 idle farm fallback result

## Design and build

V549 rebuilt exact V481 from V468, added V471's harvest-power-one opening with its one-apple
reserve, and kept V481's plum/lemon mothers as the job source. After normal planning, a
non-starter harvest-capable worker with empty hands could replace only an exact `WAIT` with a move
to the nearest fruiting mother or a harvest underfoot. The choice was stateless: any normal action
on the next turn cancelled the trip. V548's natural-fruit and bill-run reroutes were deliberately
absent, and the apple mother was never a fallback target.

The compact source was 94,865 UTF-16 units, SHA-256
`8425400f88b849d9ae8c361016356d3a083d77d5090f389db2e2a86df0afa205`. The module and readable
SHA-256 values were `b935fcc1174fd1df7e9744558f72501b1dfccbff932279d5cc6a769226b3d91a` and
`0aea4f2da298ff284f07538a54b44b04f933fdf994c0138a21738e045d13d1ee`. Readable and compact
forms compiled and emitted identical sample commands. Twenty-one focused builder, dependency,
gate and diagnostic tests passed. Candidate planning latency was 1.583 ms p95 and 4.86 ms maximum.

## Matched V481 comparison

The V481 and V549 panels contain the same 192 map/seat/opponent keys: seeds 9,941,000 through
9,941,007, both seats and the frozen 12 opponent families. The V468 arm's full command streams
matched in all 192 games.

| measure | V481 | V549 | delta |
|---|---:|---:|---:|
| own score at turn 100 | 82.80 | 80.52 | -2.29 |
| own score at turn 200 | 167.99 | 165.15 | -2.84 |
| final own score | 260.24 | 254.64 | -5.60 |
| final opponent score | 119.08 | 124.54 | +5.46 |
| final margin | 141.16 | 130.10 | -11.06 |
| wood | 50.52 | 45.32 | -5.19 |
| ring harvests | 66.01 | 81.45 | +15.44 |
| ring chops | 66.18 | 62.73 | -3.45 |
| final workers | 2.401 | 2.318 | -0.083 |
| third troll trained | 77/192 | 61/192 | -16 |
| median third-train turn when trained | 140 | 118 | -22 |
| W/T/L | 177/1/14 | 174/0/18 | -3/-1/+4 |

The intended mechanism engaged. Candidate `WAIT` commands fell from 26.65 to 21.60 per game and
total harvests rose from 68.71 to 84.31. The work was not free, however. Each harvested fruit
created later return and bank actions: drops rose 8.87 per game while chops fell 18.01. The
harvest talent also made the initial worker bill consume apples that the later bill needed;
third-worker completion fell from 77 to 61 games. The net result was 5.19 less wood and 11.06 less
margin. Margin improved in 49 games, tied in seven and regressed in 136, with standard error 2.18;
both seats lost about 11 margin.

A command trace makes the follow-on cost explicit. On map 9,941,005, seat 1 against
`compact_gold`, V549 used worker 2's otherwise idle turn 271 to `HARVEST 2`; on turn 272 its normal
planner necessarily issued `DROP 2`, while V481's worker 2 issued `CHOP 2`. V481 also completed a
third worker in that game; V549 did not. V549 finished with 6 wood and -137 margin against V481's
36 wood and -51 margin. This is the aggregate failure in miniature: guarding only the first farm
action does not guard the mandatory carrying and banking actions that follow it.

V549 recorded zero command issues, down from V481's mean 1.28, because its final conflict pass
also cleaned the farm wrapper's moves. That legality improvement did not offset the economic loss.

## Gate verdict

Against required V468, V549 scored 80.52 versus 93.01 at turn 100 (-12.49), 165.15 versus 176.18
at turn 200 (-11.04), and 254.64 versus 247.25 at turn 300 (+7.39). W/T/L was 174/0/18 versus
177/3/12, opponents' mean score rose 16.32, and the required +40 final gain was absent. V549
failed both the checkpoint and final-gain gates. No fresh-map holdout, duel, packaging audit or
platform submission was opened; V543 remains the published artifact.

Evidence:

- panel SHA-256: `ad6df97edc4ae6b1b501fa4643de639b99f39642d3aafa2036a31e56f220f5f5`
- gate report SHA-256: `935e52f2c211be3ce470af2645039b83e938cf1f07fd907ca623b8c8722a738b`
- diagnostic report SHA-256: `eea0a27058c169cb020682838c7894db61069275e91f1b18da1c2b875de8da08`
- runner SHA-256: `a8f29a05f22d54e7377238ceed170e606a87cedc5769767ae40cdfa3bf008f78`

