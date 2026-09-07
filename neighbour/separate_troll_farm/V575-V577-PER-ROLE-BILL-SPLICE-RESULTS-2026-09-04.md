# V575--V577 per-role third-worker bill splice

## Verdict

Bounded dense macros on only the starter preserve V468's score curve, but they do not fund the
third worker. After repairing action ownership and cross-controller movement conflicts, V575,
V576, and V577 scored +0.67/+2.21/+0.17, +0.79/+3.75/-2.04, and
+1.00/+2.54/+1.38 against exact V468 at turns 100, 200, and final on the 24-game behavior
smoke. All three issued zero third-worker trains. The largest final gain is 1.38, far below the
required +40, so none was credible enough for the frozen 192-game panel. Fresh maps, duels,
packaging, and platform publication remained closed.

`bot.rs`, `submission.rs`, and the live V543 platform agent remain unchanged.

## Isolated candidates

All three arms derive from V573's capability-aware, ten-source R1FA controller behind an exact
V468 observed-second-worker prefix. On every two-worker state both controllers continue to
receive the real state, but only the recorded harvest-positive starter may take a dense action.
The inherited harvest-zero worker retains V468's explicit command unchanged. Dense control may
start only when the starter is empty beside the own shack, ends on `PLANT`, `DROP`, or a 24-turn
deadline, and then waits 48, 32, or 16 turns in V575, V576, or V577. A dense
`TRAIN 2 3 1 2` would be merged, and observing that third worker would permanently latch the full
V573/V564 continuation.

The cooldown constant is the only policy difference among the arms. Normalizing that constant
makes their generated modules identical. The source retains V573's durable source accounting,
capability roles, bill calculation, target persistence, fourth-worker specification, and
conflict resolver. V574's live-fruit credit is absent.

The final compact programs are 99,607 UTF-16 units each. All readable and compact forms compile
independently, their paired runners compile, the private-identifier headroom transform round
trips exactly, and all 139 repository tests pass.

## Action-routing repairs

The first smoke exposed two composition defects rather than policy evidence. The initial wrapper
mapped actions by vector position. R1FA is allowed to omit a worker command, so that assumption
occasionally selected the inherited worker's action and produced duplicate ownership. The
wrapper now parses the explicit worker ID from unit commands; a regression test covers omitted
actions.

The next smoke still produced same-destination moves because the two controllers had each
resolved movement before their commands were spliced together. The final wrapper projects both
workers' explicit destinations, keeps the V468 command as priority, and declines a starter
replacement when the combined vector would collide. The final 72-game smoke has zero movement
issues. V576 has one noncritical `pick_stock_lost` event caused by simultaneous opponent stock
contention; V575 and V577 have no issues. Both pre-repair smoke generations and runners are
retained under the archive's `pre-action-routing-fix/` and `pre-collision-guard/` directories and
are excluded from the verdict.

## Behavior smoke

Each final arm ran seed 9,941,000, both seats, against all 12 frozen opponent families: 24 games.

| arm | turn 100 | turn 200 | final | candidate W/T/L | opponent delta | third trains | decision |
|---|---:|---:|---:|---:|---:|---:|---|
| V575 cooldown 48 | +0.67 | +2.21 | +0.17 | 20/0/4 | +8.50 | 0 | reject |
| V576 cooldown 32 | +0.79 | +3.75 | -2.04 | 19/0/5 | +14.08 | 0 | reject |
| V577 cooldown 16 | +1.00 | +2.54 | +1.38 | 19/0/5 | +13.29 | 0 | reject |

V468 went 19/1/4. V575 and V577 satisfy the two checkpoint inequalities on this smoke, but no
arm is remotely close to the +40 final requirement. The best arm changes sign by opponent:
V577 ranges from +18 against `script_boss` to -9.5 against `legend_balanced`, and it loses the
baseline draw despite gaining 1.38 mean own score. This is not a plausible candidate for a
larger promotion panel.

All 72 V468 first-worker training commands remain `TRAIN 3 2 0 2` on turn six. With the final
collision guard, first command divergence occurs on turn eight or nine, after the second worker
has been observed. Mean command-difference turns are 246.25, 248.46, and 250.83 for V575--V577;
the long downstream divergence is therefore measured rather than mistaken for a small byte-level
change.

## Why the bill did not complete

| measure per game | V468 | V575 | delta | V576 | delta | V577 | delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| final score | 215.46 | 215.63 | +0.17 | 213.42 | -2.04 | 216.83 | +1.38 |
| wood | 53.2 | 53.5 | +0.3 | 52.9 | -0.3 | 53.6 | +0.4 |
| moves | 275.67 | 270.67 | -5.00 | 276.92 | +1.25 | 285.46 | +9.79 |
| chops | 182.79 | 186.04 | +3.25 | 181.71 | -1.08 | 179.92 | -2.87 |
| harvests | 2.00 | 2.42 | +0.42 | 2.67 | +0.67 | 3.25 | +1.25 |
| plants | 13.38 | 14.79 | +1.41 | 14.88 | +1.50 | 14.83 | +1.45 |
| workers | 2.00 | 2.00 | +0.00 | 2.00 | +0.00 | 2.00 | +0.00 |

The command streams contain no `MINE` and no `TRAIN 2 3 1 2`. R1FA's ordinal-zero producer
prioritizes outstanding fruit sources and deficits; its mining fallback starts only after those
jobs clear. Ending each borrowed interval on one planting or deposit and imposing another
cooldown fragments that dependency chain. Shortening the cooldown adds harvest and planting work,
but V577 still does only 1.25 extra harvests per game, never reaches iron collection, removes
2.87 chops, and lets opponents score 13.29 more. The splice preserved the champion axe policy,
but it did not give one worker continuous ownership long enough to assemble a multi-resource
training bill.

## Consequence

Per-role command ownership solves V573's wholesale-controller teardown: early checkpoints move
from V573's -24.20/-49.43 on the full panel to nonnegative smoke deltas in V575 and V577, and the
large movement explosion disappears at the longest cooldown. The bounded unit of work is wrong,
however. A plant or deposit is only one dependency inside a training bill, not a completed bill
macro.

The next experiment should retain explicit-ID routing, the V468-priority collision guard, and the
exact inherited-worker continuation, but give the starter continuous dense ownership from a safe
bank boundary until either the third-worker train is emitted or an evidence-derived whole-bill
deadline expires. That directly tests the missing continuity. Another shorter cooldown or another
one-trip source macro is closed.

## Reproduction and integrity

- builder/test: `build_v575_per_role_bill_splice.py` /
  `test_build_v575_per_role_bill_splice.py`
- canonical runners, smokes, gates, diagnostics, and pre-repair evidence:
  `/data/separate_troll_farm-working/archive/2026-09-04-v575-v577-per-role-splice/`
- V575 panel/gate/diagnostics SHA-256: `403a256a1b20c46b080d2fdb060967d932ac506554348c2dc27630279e40b31f` /
  `206c808603d807fe37dd6bfd3289b6f616f4792a9e4d3ba2fcb8c29fbaa4eae1` /
  `261e8056a88dcab00cb20af0632a3a69ba401f1eedf5c61dcafc9c8fa07b3994`
- V576 panel/gate/diagnostics SHA-256: `a4540a311460db6dbc0db8950392969e8acf44047b10400404d3621662a88ce1` /
  `52f07ca1c58c0b733edbc852134285cd84476121b02827f27a4480f26d14ef8e` /
  `15995c547b8e31c906681267c7dc674116b5f2d180a2abe61df7a764dd821478`
- V577 panel/gate/diagnostics SHA-256: `36cb4aa1c92644e01e0b1ca4049ecad2194e475dfee589d80bf50b47ae3dea37` /
  `7ec14ca88b09c0dd466d4ab619bf6531056ed56e625406347b581ab0e5019071` /
  `3b1a5bf667ea75203bbe3eb7348233bdad4a3266f42f33bd73788aef8d5fbfe7`
- V575/V576/V577 module SHA-256: `d9c75c84d0719a367e2e695ec8e0d5b692d378a5bf4cb6f0b450861c7cbc63fc` /
  `17c0772fc41fc885f8cb846ece2c0921b055a0324126d5384d250e789037b3d0` /
  `2fd4bddff6aef2658f44bb51e4304559bf220e649007ec0c215b43d67c96086d`
- V575/V576/V577 compact SHA-256: `d9f4e13349e0cc4b3ef79ff063971f4e96e004231b672305cdf9b0abf8f62e25` /
  `20ac9e105333d9a2a01d3d40063c422d117bef5e638964e42532b88c83592f29` /
  `1c3c304825a0c1b503117a782dddf31d10b84539f23b14b0058c36f26d8f70f6`
- V575/V576/V577 runner SHA-256: `569589d5b5b4d5c3fe5aa296c91a9a3075e2f1710116d7fc39e3e2e10bc1dd8d` /
  `ef7484cf73fee5711bbeda6ac92fb6553e2f3f5717c05b800269e3cb99e295c4` /
  `93c174e832ccf1e6b59d0d42159b71de94350914344fc0f071824687165b80e3`
- builder/test SHA-256: `0c76a4108706a2fd224d772fa2a920f7748964a4d86cdff39dd3fac79fff7282` /
  `bc3af14ced06c0a488da479631531d8c2ec78572f94d35ce9f2b41491cba8d3b`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
