# V612--V614 exact-second-train near banana reserve: seed displacement, closed -- 2026-09-05

## Verdict

V612--V614 kept the live V468 controller, retained its exact `TRAIN 3 2 0 2` at turn 6, and
redirected only that harvest-zero axe to establish two, four, or six near-bank banana reserves.
Every arm exercised its intended batch in every smoke row. The result regressed monotonically:
V612 scored -4.38/-5.08/-5.96, V613 -12.58/-11.58/-11.17, and V614
-18.33/-17.54/-20.67 at turns 100/200/final against exact V468. No arm approached the frozen
192-game gate.

The failure is a seed-allocation and opportunity-cost mechanism, not an inactive branch. Each
candidate planted exactly its cap before turn 76 in all 24 rows, while V468 planted no bananas
that early. Yet full-game banana plantings remained 8.00 per candidate game versus 7.96 for V468.
The reserve did not add crop throughput: it spent the same finite seeds earlier and displaced
roughly one of V468's later ring plantings per two reserve trees. Simultaneously, the axe stopped
contesting wild trees while it made those trips. Own wood fell by 1.33/2.50/4.79 and opponent
wood rose by 2.96/5.33/6.96 as the cap increased.

No full panel, fresh maps, duels, packaging audit, production change, or platform publication
ran.

## Candidate family

`build_v612_near_banana_reserve.py` derives all three arms directly from exact V468 and trims
only dead analysis code before adding one wrapper lane:

- one inherited controller remains live for the whole game;
- before the observed second worker exists, the wrapper returns the inherited command stream;
- only the action slot of the harvest-zero, chop-positive axe can be replaced;
- establishment starts only with an empty axe at an own door and at least two banked bananas,
  leaving one seed in inventory;
- candidate plots are empty, unoccupied walkable cells within two steps of the own bank, no
  closer to the enemy bank, and outside the producer's selected landing cell;
- plant attempts are confirmed from the next real state before entering the reserve set;
- reserve plants remain occupied but have health and fruit masked to zero in the inherited
  planner view, while all wrapper decisions use the real state;
- after the batch closes, the axe may fell only a banana of size at least two whose full size
  fits its current free capacity, so the death payout is not discarded;
- producer commands, worker count, training bill, and all non-reserve fallback decisions remain
  inherited.

| arm | reserve cap | compact UTF-16 units |
|---|---:|---:|
| V612 | 2 | 89,293 |
| V613 | 4 | 89,293 |
| V614 | 6 | 89,293 |

The module renderings normalize to exact equality after changing the one batch-cap constant.
All three readable programs compile independently, and every compact artifact is 10,707 units
below the platform limit.

## Standard-map smoke

Each arm ran map 9,941,000 in both seats against all 12 frozen opponent families, for 24 paired
games per arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | own wood | opponent wood | ring plants | candidate W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|
| V612 cap 2 | -4.38 | -5.08 | -5.96 | -1.33 | +2.96 | -0.88 | 18/0/6 |
| V613 cap 4 | -12.58 | -11.58 | -11.17 | -2.50 | +5.33 | -1.88 | 17/0/7 |
| V614 cap 6 | -18.33 | -17.54 | -20.67 | -4.79 | +6.96 | -2.96 | 15/0/9 |

V468 scored 94.67/160.67/215.46, banked 53.21 wood, allowed 26.46 opponent wood,
recorded 7.96 ring plants, and went 19/1/4. All three candidates retained the same two workers,
the same `3/2/0/2` train specification, median train turn 6, and exactly two ring harvests.

The first command divergence was turn 8 in all 72 candidate games. At that common state V468's
axe chose `CHOP`, while each candidate chose `PICK ... BANANA`. Mean command-difference turns
were 252.04, 254.08, and 255.46, so the early seed decision changed almost the entire downstream
trajectory.

V612 and V613 had zero reported issues. V614 had one noncritical `move_blocked` event in six
rows and no critical or unclassified issue. Removing those rows cannot explain a 20.67-point
mean loss, and the monotonic wood/opponent-wood response is present independently of them.

## Seed displacement mechanism

The command streams prove that establishment completed exactly as requested:

| arm | early candidate banana picks | early candidate banana plants | early V468 plants | full-game candidate banana plants | full-game V468 banana plants |
|---|---:|---:|---:|---:|---:|
| V612 | 2.00 | 2.00 | 0.00 | 8.00 | 7.96 |
| V613 | 4.00 | 4.00 | 0.00 | 8.00 | 7.96 |
| V614 | 6.00 | 6.00 | 0.00 | 8.00 | 7.96 |

Every early-count distribution was a point mass at the configured cap: this was not an average
produced by partial activation. The invariant total of eight banana plantings shows why the
reserve cannot create a step change. It advances existing seed consumption rather than adding a
parallel source. Because its harvest-zero owner fells these young trees without producing
replacement fruit, later native ring production loses seed and space.

The downstream counters scale with this substitution. Ring plants fall from 7.96 to
7.08/6.08/5.00, and ring drops fall from 38.71 to 37.08/36.58/34.08. Opponents bank
29.42/31.79/33.42 wood instead of 26.46 because the axe spends the wild-tree contest window on
seed pickup and establishment travel. V614 also raises waits from 11.00 to 33.71 and extends the
mean game from turn 272.46 to 287.67. Capacity-aligned size-two felling avoids discarded payout,
but cannot repay both the displaced mature ring lane and the ceded wild supply.

This closes up-front use of V468's existing banana bank by its exact second axe. A new economy
must leave the native seed schedule intact and extract more value from supply that already
exists. The next item will test cooperative mature wild-tree felling: rendezvous the two empty
V468 workers only around an existing high-value tree, combining their chop power and free carry
capacity without planting, changing the train bill, or consuming a bank seed.

## Verification and integrity

- focused builder suite: 13 passed in 7.17 seconds, covering exact lineage, prefix behavior,
  action ownership, empty/banana-only carry states, plot geometry, batch closure, next-state
  reconciliation, planner masking, payout alignment, collision safety, structural normalization,
  compact size, standalone compilation, and emitted versions;
- complete repository suite: 282 passed in 76.82 seconds;
- canonical runners, build logs, standalone binaries, smoke panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-05-v612-v614-near-banana-reserve/`;
- V612/V613/V614 runner SHA-256:
  `c088355c8f18e4498044e6b5330025882d3ede10dcc07d06211dcaf5d7f5f1f2` /
  `3cd36ddb0f430d0f3ed69d576c55729f95962098cf3f47975b14826d9f171b93` /
  `c558396e80562000660a1781f1da2d220f7ed962c3de9d518a1d68d1968c1baa`;
- smoke panel SHA-256:
  `7f4f5276c9dbc4df72c0309ccf9e57e78b1f457eff668161a0368417ece287fa` /
  `7ca5c1f3a7bdcca0b97e345d5684f35e7e4887a984b97ff52a45d888ae084525` /
  `b7fd1ce7aa16a764d996b40964eeced39cbdde068c29c425400d7e89544409a4`;
- smoke gate SHA-256:
  `3dd05d229348b691ff81bbf5f5b50272c5867f6dee61befd3d1d9e98b722db23` /
  `0aa93361a93d3fddd3b3f7fd48a3c07ab11610bc734f5100f0c34fbab43c092a` /
  `12b564ed9a8e923e8764db645d1fe54669943f022dd9dd0105869b468aed3f34`;
- smoke diagnostics SHA-256:
  `d6ae4cbaf78704a7eac1f6c481b91dca51818cfa9da8f5b454338704628b04f0` /
  `e1625b961fbaf49d84a739b64dc89a766a4d027268a6ea6413e9709ec0d60cfe` /
  `6a64f56fd9ae3cf8ee4f46828cbaa1a1ac2f2a57ab71484123e87a3167565af4`;
- module SHA-256:
  `8b6b42d73f5ba600d9a7e16b8556e01168be86696854bcfb7023cc4cc83efa18` /
  `f56314c4ecbc7dd43a53711c0888d57b6ca6d0ed37627a2c5dd584617198522a` /
  `e21c37e9d5a2531906c5664efa09651f1bd01d33b94562c7d6887c1584d84d0d`;
- compact SHA-256:
  `26a534912c89400e5710627c649717d0c3da4add233c90848ca23246c5e2ddca` /
  `e161b9d134a53cadfddf165e020e4e99d4199b4259779cc997e44f903ee7173e` /
  `535adc22f44fffa315d1eacc1ffd49da19ef09e7ddc6003d7242bc08b7331acd`;
- builder/test SHA-256:
  `391da2657eab576e4b8cd3c7f775780c26f1e4c170bc817bed69ac4bc684c29f` /
  `989ea705c8dd09af029442e260d952d84e1473ce408d8a8040fcc7f6b6218510`;
- production remained unchanged: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`,
  `submission.rs`
  `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`;
- the neighboring checkout was read only and remained at
  `370fa63cae12eda129ff5553c33a7086dfcb87c2`, with its pre-existing modified
  `data/processed/stats.json` and untracked `data/panels/top5-ab-20260902T115338Z.json`.
