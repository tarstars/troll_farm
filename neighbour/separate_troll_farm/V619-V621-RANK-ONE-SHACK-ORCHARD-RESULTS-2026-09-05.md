# V619--V621 rank-one shack orchard: lifecycle without conversion -- 2026-09-05

## Verdict

V619--V621 reproduced the recovered rank-one control structure after an exact V468 opening, but
did not reproduce its compounding wood economy. The raid-end arms at turns 100, 150 and 200 scored
respectively `+0.00/-21.75/+1.42`, `+0.00/-22.00/+1.79`, and
`+0.00/-26.21/+3.04` at turn 100/200/final on the 24-game behavior smoke. Every arm failed the
turn-200 checkpoint and the required +40 final gain.

The lifecycle itself was active. Final V619 added 9.37 plants and 17.46 harvests per game and made
0.54 more chops than V468, but banked 1.50 less wood. Its score outside wood rose from 2.62 to
10.04, so fruit inventory concealed the missing wood at the endpoint. The farmer replanted
disappeared types before the banana quota, producing 11.46 apples and only 4.62 bananas per game;
an apple at size four needs ten power-two chops, versus three for a banana. Meanwhile the intended
carry-four/chop-three third worker trained in zero of 72 rows across the sweep, even though the axe
spent six commands per game mining toward its bill. The recovered rank-one economy's cheap banana
turnover and capable later worker therefore never materialized.

Moving the opponent-shack raid boundary changed the final delta by only 1.63 points from V619 to
V621 and made the turn-200 deficit worse. The common conversion and roster bottleneck, rather than
raid timing, explains the family. No frozen 192-game panel, fresh-map panel, duel, packaging audit,
production change, or platform publication ran.

## Source reconstruction and candidate family

The read-only neighboring checkout supplied two derived reconstruction documents, not code:
`local_claude_1/reconstructions/fits/delineate.md` and
`local_claude_1/reconstructions/delineate/ALGORITHM.md`. Their 215 exact full-length rank-one
replays reported 93% wood score, 75 own-crop wood per game, a planter-cell fit of 89.9%, a
nearest-ripe fit of 70.5%, a median turn-seven second worker, and a late shack-local banana phase.
The neighboring checkout remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`; its pre-existing
modified `data/processed/stats.json` and untracked
`data/panels/top5-ab-20260902T115338Z.json` were unchanged by this iteration.

`build_v619_rank_one_shack_orchard.py` derives each arm by marker substitution from the exact
`candidate_v468_no_denial_bonus_module.rs` base. It retains the live V468 controller through turn
100 while recording typed plant provenance, then transfers both existing workers to one allocator:

- the lowest-id starter banks each load, harvests the nearest ripe unreserved tree, and maintains
  at most eight typed crops on own-half cells minimizing `d(shack)+d(farmer)`;
- the axe reserves unique persistent targets, protects owned trees below size four, prefers mature
  own bananas, mines the later-worker iron deficit, and otherwise chooses efficient wild or raid
  trees;
- projected landing reservations keep same-player paths apart, and one shack door remains clear;
- the sole arm parameter ends the opponent-plant raid at turn 100, 150, or 200.

| arm | raid through | compact UTF-16 units | module SHA-256 |
|---|---:|---:|---|
| V619 | 100 | 98,909 | `5dfdf3d5c75aac22ff57eb150ecddf06af0f5d0ce9b07ab17c4864dde560e491` |
| V620 | 150 | 98,909 | `7c9a5642c6ed40e31063d6bca4b161c6ba882050a33d18f3b4c9397a2983bae5` |
| V621 | 200 | 98,909 | `894313cb8e9ac9aad6f64887fa663d906b7d76e06af1373b76d3544a4e2d9496` |

All readable and compact programs were regenerated from the builder. Each readable program
compiled independently with Rust 2021 and optimization. The compact artifacts remain 1,091 UTF-16
units below the platform limit.

## Test-first repairs

`test_build_v619_rank_one_shack_orchard.py` first failed collection because the builder did not
exist, then covered exact-prefix delegation, typed provenance and refills, seed-job durability,
fitted plot and harvest rules, maturity protection, the later-worker bill, raid isolation,
collision reservations, standalone compilation, emitted arms, and compact size.

Two smoke failures exposed controller defects before the final comparison:

1. The initial V619 picked 44.62 seeds but planted only 10.54 per game, because a picked seed lost
   its intent after leaving the bank and was deposited. A persistent unit-to-seed job repaired the
   transaction; this broken run scored -53.96 final and is retained as
   `v619-smoke-initial-seed-loop.tsv`.
2. The seed-fixed build retained a collision fallback whose target was the worker's current cell,
   producing 63.54 waits per game. Fallback moves are now one-turn waits and are never persisted;
   this intermediate -31.67 run is retained as
   `v619-smoke-seed-fixed-sticky-move.tsv`.

The repaired focused suite passed 11 tests, and the complete repository suite passed 306 tests in
92.46 seconds. Repaired V619 averaged 21.79 waits rather than 63.54; its remaining 1.62 issues per
game were all noncritical `move_blocked` events.

## Smoke gate

All arms ran map 9941000 in both seats against the registered 12-family opponent set, producing
24 paired rows per arm. Every first command divergence was exactly turn 101.

| arm | delta t100 | delta t200 | delta final | candidate score | candidate wood | opponent score delta | candidate W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|
| V619 | +0.00 | -21.75 | +1.42 | 216.88 | 51.71 | +46.75 | 16/0/8 |
| V620 | +0.00 | -22.00 | +1.79 | 217.25 | 51.58 | +49.71 | 16/0/8 |
| V621 | +0.00 | -26.21 | +3.04 | 218.50 | 51.17 | +42.12 | 15/1/8 |

The baseline scored 94.67/160.67/215.46 at turn 100/200/final, banked 53.21 wood, and went
19/1/4. V619's detailed action means show what replaced the missing middle-game score:

| measure per game | V468 | V619 | delta |
|---|---:|---:|---:|
| plants | 13.38 | 22.75 | +9.37 |
| harvests | 2.00 | 19.46 | +17.46 |
| chops | 182.79 | 183.33 | +0.54 |
| moves | 275.67 | 284.50 | +8.83 |
| deposits | 38.71 | 42.96 | +4.25 |
| mines | 0.00 | 6.00 | +6.00 |
| waits | 11.00 | 21.79 | +10.79 |

V619 planted 0.46/11.42/10.88 crops in turns 1--100/101--200/201--300, versus
0.46/4.12/8.79 for V468. It harvested 6.88 times in the middle phase, but its chops fell from
56.67 to 46.17 there; its turn-200 score consequently fell by 21.75. The final catch-up came from
fruit rather than wood. Candidate games all ran through turn 301, 28.54 turns longer than the
baseline mean, while opponents gained 5.75 wood and 46.75 score. Longer survival did not create a
winning economy.

The complete TSVs, gate JSON, diagnostics JSON, independent binaries, and build logs are archived
under
`/data/separate_troll_farm-working/archive/2026-09-05-v619-v621-rank-one-shack-orchard/`.

## Decision

The phase sweep rules out raid duration as the missing rank-one mechanism. The integrated orchard
can perform durable planting and harvesting without corrupting V468's opening, but its type-refill
policy spends most new seeds on slow-to-fell apples and its first post-prefix worker bill is not
reachable. Queue item 34 therefore keeps the integrated lifecycle but tests an affordable staged
third worker that can increase banana planting and mature-tree conversion before capacity is
escalated. V619--V621 are retained as research artifacts only.

Production remained byte-identical: `bot.rs` SHA-256
`b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372` and `submission.rs`
SHA-256 `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
