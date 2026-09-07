# V628--V630 stock-light producer bridge: a working producer still arrives too late -- 2026-09-05

## Verdict

V628--V630 replaced V627's direct minimum useful-worker bill with a cheaper `1/1/1/0` producer,
costing `3/3/3/2` at roster two. V629 then reserved a `1/2/1/2` fourth worker and V630 a
`2/2/1/2` fourth worker. After two scheduler regressions were found and repaired, the producer
really did multiply sources: in its eight trained rows it averaged roughly ten harvests and seven
plants. It still trained too late and too rarely to bridge the economy. All three arms trained it
in the same 8 of 24 rows at turns 153, 158, 159, 160, 166, 170, 171, and 176 (median 163), and no
arm ever trained a fourth worker.

The final arms scored `+0.00/-9.83/+7.00`, `+0.00/-13.42/+7.38`, and
`+0.00/-13.42/+7.83` at turn 100/200/final. They preserved the required turn-100 prefix, but
failed the middle checkpoint and reached less than one fifth of the required +40 endpoint. The
producer-complete V629/V630 rows were all short in plum, lemon, and apple at turn 220 even though
their iron bill was complete. The fourth-worker escrow also imposed a -24.00 mean turn-200 delta
in those rows. The producer bridge therefore executes, but its late source investment consumes the
remaining match rather than creating timely mature-wood capacity.

No frozen 192-game panel, fresh-map panel, duel, packaging audit, production change, or platform
publication ran.

## Candidate family

`build_v628_stock_light_producer_bridge.py` starts from the final dual-source V627 builder and
applies the result to the exact `candidate_v468_no_denial_bonus_module.rs` base. All variants are
command-identical to V468 through turn 100. The common mechanism:

- preserves V627's typed source provenance, water-first plots, scarce-fruit protection, and
  independent starter and axe roles;
- substitutes a `1/1/1/0` producer with a turn-180 deadline for the direct `1/2/1/2` third hire;
- gives that producer its own carry-source, harvest, bank, and bounded plant lane;
- lets a live fourth-worker bill capitalize up to two plums, three lemons, and two apples, with a
  total live-crop cap of twelve;
- extends axe iron acquisition only while the staged bill is active;
- makes V628 producer-only, V629 reserve `4/7/4/7` for a `1/2/1/2` fourth hire, and V630 reserve
  `7/7/4/7` for a `2/2/1/2` fourth hire, both with turn-230 deadlines;
- removes the post-prefix unreachable raid and opponent-provenance branch to fund the controller;
- resolves an adjacent full-carrier/empty-producer corridor lock by emitting reciprocal moves for
  the pair when at least three own workers are alive.

The panel runner now emits ignored `#checkpoint_state` records at turns 180 and 220. This changes
neither the TSV game-row schema nor simulation and made the producer bill and subsequent fourth
bill independently auditable.

| arm | staged fourth worker | compact UTF-16 units | module SHA-256 | compact SHA-256 |
|---|---|---:|---|---|
| V628 | none | 99,910 | `c729a803ad206025bf252f8dc708c504c48ba14c5c2f28fa70a994167fc24b81` | `f34c66d6a370b985f8c58487678a11113d601b6fab3ed54f178afc2d9b516ace` |
| V629 | `1/2/1/2` | 99,921 | `8f998f3f6595c518dc19caaebe386e6c7867a87b14c00d0aad4607991799e55e` | `61b765d2d7dbee9af7df6cadfd8b11ffb7d0e2849d9144e70ab070c14c75f6c2` |
| V630 | `2/2/1/2` | 99,921 | `f13c326c3968eb57c1ba0d600d84a7da9974863549a66e854fac8124b3436f6d` | `27fc56d5e0b390483a698851c992ff5cdc07130ee92b0dd410e6575d40db0121` |

All readable programs compiled independently with Rust 2021 and optimization. Every compact file
is below the 100,000 UTF-16-unit platform limit.

## Test-first implementation and scheduler repairs

`test_build_v628_stock_light_producer_bridge.py` first failed collection because the builder did
not exist. The initial implementation passed its 13 focused tests, but its first smoke showed a
nominal producer averaging only 1.88 harvests and 1.62 plants when trained. A new bounded active-
bill source-multiplication test failed before the repair and passed after it.

The expanded source path exposed a second mechanism: five of the eight producer rows accumulated
93--120 consecutive waits because a full starter and an empty producer faced each other in a
one-cell corridor. An adjacent-detour regression test failed before its repair and passed after it,
but the detour could not solve a one-wide head-on swap. A final focused reciprocal-carrier-swap
test then failed before implementation and passed afterward. The swap reduced waits to about 41
per game, made all intended producer lanes execute, and improved the final deltas from
`+2.96/-3.33/-4.04` in the detour-only arms to `+7.00/+7.38/+7.83`.

The final focused suite passed 16 tests in 8.06 seconds. The complete repository suite passed 348
tests in 115.23 seconds. All three final readable candidates compiled independently. The repairs
are retained because they are supported by focused regressions and distinguish scheduler failure
from the economic result; the remaining failure is not an unexecuted controller branch.

## Final smoke gate

Each arm ran map 9941000 in both seats against the registered 12-family opponent set, producing 24
paired games. Every first command divergence was turn 101.

| arm | delta t100 | delta t200 | delta final | candidate final | wood | opponent final delta | workers | candidate W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V628 | +0.00 | -9.83 | +7.00 | 222.46 | 53.25 | +34.67 | 2.33 | 16/0/8 |
| V629 | +0.00 | -13.42 | +7.38 | 222.83 | 52.75 | +37.42 | 2.33 | 16/0/8 |
| V630 | +0.00 | -13.42 | +7.83 | 223.29 | 52.83 | +37.71 | 2.33 | 16/0/8 |

V468 scored 94.67/160.67/215.46 at turn 100/200/final, banked 53.21 wood, and went 19/1/4.
The bridge expanded activity but not wood conversion:

| action per game | V468 | V628 | V629 | V630 |
|---|---:|---:|---:|---:|
| moves | 275.67 | 360.38 | 353.46 | 353.17 |
| chops | 182.79 | 152.62 | 148.71 | 148.79 |
| drops | 38.71 | 36.17 | 41.58 | 41.67 |
| picks | 13.38 | 8.00 | 9.96 | 9.88 |
| plants | 13.38 | 13.29 | 14.08 | 14.04 |
| harvests | 2.00 | 12.38 | 15.67 | 15.75 |
| waits | 11.00 | 42.75 | 40.79 | 40.96 |
| mines | 0.00 | 1.04 | 2.38 | 2.38 |

V630 added only 0.66 plants and 13.75 harvests over V468 while removing 34.00 chops, adding 77.50
moves, and losing 0.38 wood. Its +7.83 final gain therefore came from non-wood activity and was
accompanied by +37.71 opponent score, four additional losses, and 22.21 longer games. This is not
the platform-scale parallel mature-tree conversion required by the goal.

## Producer deadline audit

The same eight rows completed the producer in every arm because all behavior is common until that
train. The sixteen misses at turn 180 averaged the following bank and carried resources, in
plum/lemon/apple/banana/iron/wood order:

| location | mean inventory | binding condition |
|---|---|---|
| bank | 0.75 / 4.06 / 4.00 / 3.75 / 2.06 / 31.75 | all 16 lacked the three banked plums |
| carried | 0.31 / 0.00 / 0.00 / 0.12 / 0.00 / 0.69 | 14 of 16 still lacked plum including carries |

No missed row lacked enough lemon, apple, or iron after including carried stock. The cheap bill
removed V627's lemon and iron bottlenecks but did not make serial plum capitalization reliable
before the deadline. The eight successes trained at turns 153--176, already too late to improve
the turn-200 checkpoint consistently.

V628's eight trained rows averaged -13.25 at turn 200 and +12.50 own score at the end, with +1.75
wood. Its sixteen missed rows averaged -8.12 at turn 200, +4.25 final, and -0.81 wood. Thus a live
producer adds real late value, but even successful rows remain far below +40 and lose too much
during its acquisition window.

## Producer output and failed fourth bill

In the eight rows where it existed, the V629 producer averaged 102.25 moves, 3.62 picks, 6.88
plants, 10.38 harvests, 6.38 drops, and 6.38 waits. Across those rows it planted 24 lemons, 16
bananas, 11 apples, and 4 plums. V630 was similar: 102.25 moves, 3.62 picks, 7.12 plants, 10.00
harvests, 5.75 drops, and 7.12 waits, with 24 lemons, 18 bananas, 11 apples, and 4 plums.

The active fourth-worker reservation made those trained rows average -24.00 at turn 200 in both
V629 and V630. At turn 220 their mean bank was
`1.38/0.62/0.12/2.00/8.00/36.25` and mean carried stock was
`0.12/0.38/0.25/0.50/0.00/0.75`. Every row was short in plum, lemon, and apple even after carried
stock, while every row had enough iron. No fourth worker trained by the turn-230 deadline or by
the end of any game.

V629's trained rows ended +13.62 own score and +0.25 wood but lost 42.12 margin on average;
V630's ended +15.00 own score and +0.50 wood but lost 41.62 margin. Their sixteen producer-miss
rows stayed on the common V628 path. The additional producer plants prove that the independent
source loop works, but one late power-one harvester cannot generate three separate fruit bills
before the match's useful wood-conversion window closes.

The final panels reported 27 candidate movement issues per arm, all classified `move_blocked`,
with zero critical or unclassified issues. Command-stream inspection showed no remaining persistent
head-on lock after the swap repair. These isolated blocks are not the cause of the universal
fourth-bill failure.

Canonical panels, gate and diagnostic JSON, turn-180/220 states, all three pre-repair smoke stages,
standalone binaries, panel runners, and build logs are archived under
`/data/separate_troll_farm-working/archive/2026-09-05-v628-v630-stock-light-producer-bridge/`.

## Decision

Queue item 36 closes a cheap third-worker producer as a bridge after V468's established two-worker
opening. It is cheaper and more reachable than V627's direct useful worker, and its independent
lane genuinely expands harvest and planting, but the median turn-163 arrival leaves neither a
turn-200 return nor enough time to fund a fourth worker. More post-turn-100 source quotas would
repeat the same chronology.

Queue item 37 reverses the workforce order. It will test a cheap producer as the early second hire,
then use conserved opening stock plus parallel fruit production to acquire the first capable axe
before turn 100. This is structurally different from V603's expensive harvest-capable second worker:
the first new unit is deliberately cheap and chop-free, and wood capacity is the second purchase.

A turn-number audit while writing this report also corrected V626/V627's previously documented
zero-based stream indexes to the platform-facing turns 213/219 and 210. Scores and conclusions are
unchanged.

Production remained byte-identical: `bot.rs` SHA-256
`b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372` and `submission.rs`
SHA-256 `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
The neighboring read-only repository remained at
`370fa63cae12eda129ff5553c33a7086dfcb87c2`; its pre-existing modified stats file and untracked
panel JSON were not touched.
