# V578--V580 continuous single-owner third-worker bill

## Verdict

Continuous starter ownership turns the seed-9,941,000 smoke positive but does not transfer across
maps. V579, the credible 192-turn arm, gained +7.25/+21.04/+34.46 at turns 100, 200, and final in
the 24-game smoke, with positive own-score deltas against all 12 opponent families. On the frozen
192-game panel it instead scored -14.24/-26.83/-31.20 and went 158/2/32 versus V468's 177/3/12.
It failed both checkpoint inequalities and the +40 final requirement, so fresh maps, duels,
packaging, and platform publication remained closed.

The mechanism rarely completed its stated purpose. V579 trained a third worker in only three of
192 games, all on seed 9,941,006, and trained one fourth worker. Across the panel it reassigned
V468's primary producer, removed 55.53 harvest commands and 59.84 deposits per game, and added
113.70 moves. The inherited axe was preserved, but the lost producer income dominated.

`bot.rs`, `submission.rs`, and the live V543 platform agent remain unchanged.

## Isolated candidates

All three arms derive from the repaired V575--V577 composition. They return exact V468 commands
until its second worker is observed, parse explicit worker IDs instead of relying on vector
position, and retain V468's action and movement priority for the inherited harvest-zero worker.
Both V468 and V573's capability-safe R1FA controller remain warm on every two-worker state.

The original harvest-positive starter begins one dense attempt only when empty beside the own
shack and when its first R1FA action is useful and collision-free. It then retains R1FA ownership
across planting and deposit boundaries. A conflicting action falls back to V468 for that turn
without ending the attempt. The arms differ only in the one-shot horizon: 144 turns in V578, 192
in V579, and 320 in V580. Expiry permanently restores the starter to V468. A clear-state
`TRAIN 2 3 1 2` is merged, and an observed third worker latches the full V573/V564 continuation.

Normalizing the horizon constant makes the generated modules identical. Each compact source is
99,515 UTF-16 units. All readable and compact forms compile independently, all paired runners
compile, the private identifier transformation round trips exactly, and all 150 repository tests
pass.

## Behavior smoke

Each arm ran seed 9,941,000, both seats, against all 12 frozen opponent families: 24 games.

| arm | turn 100 | turn 200 | final | candidate W/T/L | opponent delta | third trains | decision |
|---|---:|---:|---:|---:|---:|---:|---|
| V578 horizon 144 | +7.25 | +19.58 | +27.79 | 18/0/6 | +40.29 | 0 | no full panel |
| V579 horizon 192 | +7.25 | +21.04 | +34.46 | 18/1/5 | +38.25 | 0 | admit |
| V580 horizon 320 | +7.25 | +21.04 | +29.50 | 17/2/5 | +40.50 | 0 | no full panel |

Every arm preserved both V468 checkpoint inequalities, and V579 improved own score against every
opponent family, from +5 against `mybot` to +59.5 against `compact_gold`. V579 was an interior
horizon optimum and reached 86% of the required final gain, so it was the only behaviorally
credible arm admitted to the full frozen panel. V578 gave up 6.67 final points by restoring V468
too early; V580 gave up 4.96 by continuing the dense attempt through the endgame. None emitted a
third-worker train on this map.

The outcome count did not follow own score because every arm also extended games and raised
opponent score by 38--41 points. This was an early warning of map-specific interaction, but not a
reason to discard V579 without the preregistered transfer test.

## Frozen V468 gate

V579 ran seeds 9,941,000--9,941,007, both seats, and all 12 frozen opponent families: 192 paired
games.

| checkpoint | V468 | V579 | delta |
|---|---:|---:|---:|
| turn 100 | 93.01 | 78.77 | -14.24 |
| turn 200 | 176.18 | 149.35 | -26.83 |
| final | 247.25 | 216.05 | -31.20 |

V579 lost own score against ten of 12 families, from -13.1 against `resident` to -57.6 against
`legend_balanced`. Its only nonnegative family results were +0.3 against `mybot` and +3.4 against
`silver_boss`. Opponent final score rose 23.23 per game. The candidate added 20 losses and removed
one tie, so the failure is visible in both score and outcomes.

All 192 V468 first-training command/turn pairs match exactly. First command divergence occurs
only after the trained second worker is observable, ranging from turns 2 to 79 with median 16 as
the V468 opening adapts across maps. The candidate has one `move_blocked` and 12 `no_capacity`
events, all noncritical and none unclassified. Its large score loss persists across clean rows;
legality is not causal.

## Rare bill completions

The continuous attempt emitted no extra train on the smoke. On the full panel it emitted only
three `TRAIN 2 3 1 2` commands:

| seed | seat | opponent | third-train turn | later result |
|---:|---:|---|---:|---|
| 9,941,006 | 0 | `legend_v3_hp2_four` | 184 | fourth worker at turn 292 |
| 9,941,006 | 1 | `legend_balanced` | 217 | three workers |
| 9,941,006 | 1 | `legend_v3_hp2_four` | 211 | three workers |

The other 189 games ended with two workers. A longer horizon is not the missing repair: V580's
320-turn arm was already effectively unbounded on the smoke and scored less than V579. R1FA's
ordinal-zero producer still has to build and harvest sources, clear three fruit deficits, mine six
iron, and return to a clear shack. One worker rarely finishes that dependency chain within a
match.

## Producer opportunity cost

| measure per game | V468 | V579 | delta |
|---|---:|---:|---:|
| final score | 247.25 | 216.05 | -31.20 |
| wood | 45.02 | 53.26 | +8.24 |
| moves | 193.29 | 306.99 | +113.70 |
| chops | 155.08 | 170.97 | +15.89 |
| harvests | 68.67 | 13.14 | -55.53 |
| drops | 97.52 | 37.68 | -59.84 |
| plants | 11.05 | 19.50 | +8.45 |
| workers | 2.00 | 2.02 | +0.02 |

The extra 8.24 wood is worth about 32.96 score, but nonwood final inventory falls about 64.16
points, yielding the observed -31.20 net. V468's starter is not spare labor: across diverse maps
it performs the renewable harvest/deposit loop that supplies most nonwood score. Preserving only
the axe therefore preserves the wrong half of the champion economy. Continuous ownership does
repair the fragmentation seen in V575--V577, but it turns the repair into a long producer outage.

## Consequence

The controller-handoff line is closed. Fixed late handoffs failed in V552--V554, immediate full
handoffs failed in V572--V574, bounded per-role work failed to assemble the bill in V575--V577,
and continuous per-role work now proves that assembling it by borrowing the producer is too
expensive. Another horizon, cooldown, or starter handoff does not address the observed loss.

The next experiment should preserve the V468 producer completely and capitalize inventory it
already banks. V468 averages 68.67 harvests but only 0.25 mines per game. A distinct test is to
wait until the bank already covers a cheap third worker's fruit bill, divert only the inherited
harvest-zero axe for the exact missing iron, issue the hire, and then leave all workers under
V468. This spends axe chops rather than erasing the renewable producer loop and tests whether a
surplus-funded worker can repay its small bill without violating the early checkpoints.

## Reproduction and integrity

- builder/test: `build_v578_continuous_starter_bill.py` /
  `test_build_v578_continuous_starter_bill.py`
- canonical runners, smokes, full panel, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v578-v580-continuous-bill/`
- V578 smoke/gate/diagnostics SHA-256: `fe813ab1ce016bf5fbc4a66aabd8528a113af84009531580f132014ae03c4c4d` /
  `140c513b2ee80d90392de231f1c34d3af5389a0c646eb6b0cab9818808037a60` /
  `b8b4d3fb2a2729b252f8e25457618bc39cc5a5ad35a1a6afed6b9db52fb527ff`
- V579 smoke/gate/diagnostics SHA-256: `57cc36488458cbc39893f808ea0af5d82bdc22b11215dedf1a32a13fb374c6e0` /
  `cded3c742ceffb4c428e25e74956442d93b57a159fa5103145a91ed15e8b4240` /
  `d1700951bcff5261330a1c1bdb7f8d5aa003953865913e073355bcde963ee489`
- V580 smoke/gate/diagnostics SHA-256: `4ef0f287c8d4e8d04cfa0eea738cf4cf969c7db0a28ebdf989486e8960a5b87d` /
  `8c8c208434c85b6199f55cb0f84a3f61cc3ed70213f447694dfe42b73a30734e` /
  `715b75ccba9808ecf0a0d2da1c7aa7e03c561a4e09f53408211ceaaef7b9674d`
- V579 full panel/gate/diagnostics SHA-256: `c1b63dc8cd34c76480bd17f72aca17555387c53ffc58d102364ff3e73b29b176` /
  `712a6a4899276dd006d29e537d53abda014a04f03b5b2baac4d3e74ed40dddc7` /
  `8889458031309ed1a777777da83fe670a54a0b0c829cc77dc4b69ea2ec3c3395`
- V578/V579/V580 module SHA-256: `f9cdbab353c906d28da42fbf185f125d541f41ffe798bf31358376fd9d364973` /
  `776714addceeb01b3bc156ec07fc947aaaa5a8b7da18a054350e031c62411424` /
  `7c71bcb96cc1eb530360f1bd9dfa4f49b905689e4d27e04d6f222c96dffd4050`
- V578/V579/V580 compact SHA-256: `e075987f792c7047cc220deb0b67f2577984bee0b1a25c803f152a850e0ec910` /
  `77e6d99188f42a5bc21d545168bd318d5496ea0869cf70c1871d00d8d38722d3` /
  `7d19c72d46f1961d63296878e5e65bbfd9e8ec64e590174ab437794a4989311c`
- V578/V579/V580 runner SHA-256: `023bc3f0c8484cfa4d3f01c880ba03d00a8456970f107dd93d9cd675904ccb23` /
  `bd275dca404426a8e2feb9cedf8a04a0b4dd934c0aec8894fd8b10315d4caf02` /
  `f3d5fa3c0717bc63177e789549c4c7d44b745b85fe7af71b72f332c2325a9ed5`
- builder/test SHA-256: `33dab0f9e8e884c29bbb0a976db5a78741bf053506fdaf579e573c2e54ee83e2` /
  `2aead92c159a4af64420c21a6bfa4c9c7e926ad425e5362858c66cc8b914689e`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
