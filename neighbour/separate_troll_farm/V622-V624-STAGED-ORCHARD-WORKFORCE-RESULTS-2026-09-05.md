# V622--V624 staged orchard workforce: minimum useful worker still unfundable -- 2026-09-05

## Verdict

V622--V624 made the V619 orchard banana-first and reduced its proposed third worker to the cheapest
useful harvest-and-chop bills, but none of the three workers trained in any of 72 final smoke rows.
The speed/carry/harvest/chop arms `1/2/1/2`, `2/2/1/2`, and `2/3/1/2` scored respectively
`+0.00/-12.29/+1.46`, `+0.00/-11.38/+2.17`, and `+0.00/-11.38/+1.25` at turn
100/200/final. Every arm failed the middle checkpoint and the required +40 endpoint.

The crop correction worked: V623 planted 9.79 bananas and 0.96 apples per game, compared with
V619's 4.62 bananas and 11.46 apples. Wood per chop rose from V468's 0.291 to 0.355. The workforce
did not appear, however, and total chops fell from 182.79 to 147.58; V623 consequently banked 0.88
less wood than V468. A cheaper bill cannot create rank-one compounding after turn 100 when the
existing roster has only one harvest-power-one unit and no owned scarce-fruit supply.

No frozen 192-game panel, fresh-map panel, duel, packaging audit, production change, or platform
publication ran.

## Candidate family

`build_v622_staged_orchard_workforce.py` derives V619's raid-100 integrated controller from the
exact `candidate_v468_no_denial_bonus_module.rs` base. Every arm remains command-identical to V468
through turn 100. Common post-prefix changes are:

- live crop demand is quota-bound at four bananas, two lemons, one plum, and one apple, with
  bananas selected first and surplus carried fruit deposited instead of planted;
- fruit needed by an active worker bill outranks travel distance when selecting ripe plants, and
  non-banana bill stock is not picked back out of the bank;
- natural trees of a currently deficient fruit type are protected from both choppers;
- the inherited axe mines only the bill's iron deficit, and no fourth-worker bill is opened;
- after training, the new unit would harvest a missing crop type, plant it, prefer mature owned
  bananas, and bank its load while the inherited axe retained general wood duty.

Only the proposed third-worker spec varies:

| arm | speed/carry/harvest/chop | cost at roster two: plum/lemon/apple/iron | compact UTF-16 units | module SHA-256 |
|---|---|---|---:|---|
| V622 | `1/2/1/2` | `3/6/3/6` | 99,592 | `6349eb4cc4002a62afb9887beef1c5ca9209d60480329848aa46111132969ff9` |
| V623 | `2/2/1/2` | `6/6/3/6` | 99,592 | `7f5971e01f3c0ec195b2f0a79190c96b300a18e97ad0d9d7702ed283dfedee2a` |
| V624 | `2/3/1/2` | `6/11/3/6` | 99,592 | `3a6b37c3df2c38b81529741c454e22205fc2a6e73ed9618bd811c2cd75fbb6df` |

All readable programs compiled independently with Rust 2021 and optimization. The compact files
remain 408 UTF-16 units below the platform limit.

## Test-first implementation and diagnostic repairs

`test_build_v622_staged_orchard_workforce.py` first failed collection because the builder did not
exist. Its final 13 tests cover exact-prefix inheritance, banana-first bounded quotas, surplus
fruit banking, bill-stock reservation, natural source protection, registered costs, single-stage
training, bill-first harvesting, the later unit's full lifecycle, arm isolation, standalone
compilation, emitted artifacts, and compact size.

The first V622 smoke made the bill failure observable but also exposed stock churn. It scored
`+0.00/-10.17/+7.42`, mined the required iron, and still ended with two workers because harvested
lemon and plum were picked back out of the bank for crop refills. Reserving non-banana bill stock
changed V622 to `+0.00/-10.75/+2.96`, again without training. Protecting every natural tree whose
fruit remained deficient produced the final `+0.00/-12.29/+1.46`; it increased source survival but
still did not create enough harvestable fruit and ceded more wood to the opponent.

All three repair stages are retained under the archive as `unreserved-bill`,
`reserved-stock-unprotected-sources`, and the canonical final panels. The panel runner now writes
turn-220 state snapshots as ignored `#checkpoint_state` comment rows, preserving the gate TSV
schema while exposing exact bank and carried inventories. The change does not affect simulation,
maps, opponents, scoring, or gate parsing.

The focused suite passed 13 tests, the complete repository suite passed 319 tests in 100.85
seconds, and each final panel runner compiled through the release build.

## Final smoke gate

Each arm ran map 9941000 in both seats against the registered 12-family opponent set, producing 24
paired rows. All first command divergences were turn 101.

| arm | delta t100 | delta t200 | delta final | candidate score | candidate wood | opponent score delta | workers | candidate W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V622 | +0.00 | -12.29 | +1.46 | 216.92 | 52.25 | +41.96 | 2.00 | 15/0/9 |
| V623 | +0.00 | -11.38 | +2.17 | 217.62 | 52.33 | +43.25 | 2.00 | 15/0/9 |
| V624 | +0.00 | -11.38 | +1.25 | 216.71 | 52.04 | +42.67 | 2.00 | 15/0/9 |

V468 scored 94.67/160.67/215.46 at turn 100/200/final, banked 53.21 wood, and went 19/1/4.
V623's action mix explains its small final gain and middle regression:

| measure per game | V468 | V623 | delta |
|---|---:|---:|---:|
| plants | 13.38 | 14.38 | +1.00 |
| banana plants | 7.96 | 9.79 | +1.83 |
| harvests | 2.00 | 9.00 | +7.00 |
| chops | 182.79 | 147.58 | -35.21 |
| wood | 53.21 | 52.33 | -0.88 |
| moves | 275.67 | 312.33 | +36.66 |
| waits | 11.00 | 48.75 | +37.75 |

Its banana bias and maturity protection increased yield per chop by 22%, but fruit searches and
protected sources removed too many middle-game chops. The candidate trailed 11.38 at turn 200,
ran 23.96 turns longer than the baseline mean, and let opponents add 43.25 score. The endpoint gain
came from 5.68 additional non-wood points, not from the required wood step change.

## Turn-220 bill audit

The exact prefix left V622 at turn 101 with zero plum and iron and exactly four lemon and four
apple in all 24 rows. Its minimum third-worker bill needed three plum, six lemon, three apple, and
six iron. The final turn-220 snapshots existed for 23 rows because one game ended earlier:

| stock | mean banked | required | rows still short |
|---|---:|---:|---:|
| plum | 1.96 | 3 | 10/23 |
| lemon | 4.52 | 6 | 21/23 |
| apple | 4.00 | 3 | 0/23 |
| iron | 6.04 | 6 | 0/23 |

No unit carried any missing bill item at that checkpoint, and zero row was jointly affordable.
At turn 101 the board averaged 2.46 fruit-bearing plum trees and 1.71 fruit-bearing lemon trees,
but the only own harvester had power one. Reserving stock and preserving those trees still left it
competing with the opponent for a finite natural supply. V623 and V624 require more plum or lemon
and were strictly farther from affordability. The limiting resource is repeatable scarce-fruit
production, not iron, the training deadline, or the proposed worker's capability cost.

The complete panels, checkpoint states, gate and diagnostic JSON, intermediate repair evidence,
standalone programs, runners, and build logs are archived under
`/data/separate_troll_farm-working/archive/2026-09-05-v622-v624-staged-orchard-workforce/`.

## Decision

Queue item 34 closes the direct post-prefix third-worker path: even the minimum worker that can
harvest and fell mature wood cannot be financed reliably from natural fruit after V468's opening.
Queue item 35 tests a new causal mechanism rather than a smaller bill: invest the first scarce
fruit in a protected near-bank lemon/plum mother, harvest its repeated output, and only then reserve
the worker bill. That experiment must measure whether source capitalization repays its own
turn-200 opportunity cost before any workforce escalation.

Production remained byte-identical: `bot.rs` SHA-256
`b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372` and `submission.rs`
SHA-256 `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
