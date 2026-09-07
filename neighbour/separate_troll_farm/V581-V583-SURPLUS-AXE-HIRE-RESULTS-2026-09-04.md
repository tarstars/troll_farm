# V581--V583 surplus-funded third worker with axe-only iron

## Verdict

V468 does not retain a complete diversified third-worker fruit bill early enough to fund a hire
without intervention. V581, V582, and V583 were byte-identical to exact V468 across both the
standard seed-9,941,000 smoke and a targeted seed-9,941,006 reachability panel: 48 games per arm,
144 candidate games total. They issued no mining override and no extra `TRAIN`, so every score,
outcome, action, and opponent response was identical.

The second panel is decisive for the premise rather than merely another inactive map. On seed
9,941,006 V468 averages 115.5 harvests and 140.2 deposits per game, yet even the cheapest tested
`1/1/1/1` bill is never simultaneously banked after reserving V468's same-turn seed picks while at
least 96 turns remain. Existing harvest volume is not the same as available diversified surplus.
No arm was behaviorally credible for the frozen 192-game panel, and none entered fresh maps,
duels, packaging, or platform publication.

`bot.rs`, `submission.rs`, and the live V543 platform agent remain unchanged.

## Isolated candidates

The candidates derive directly from V468 and embed no dense controller. V468 generates the full
command vector first on every turn and remains the controller before and after any prospective
hire. Once the second worker is observed, the wrapper records only the harvest-zero worker as the
axe. It never replaces a harvest-positive worker.

Activation is one-shot and requires all of the following:

- at least 96 turns remain;
- the axe carries nothing;
- the current bank covers the complete plum, lemon, and apple bill after subtracting every
  same-turn V468 `PICK`;
- two own workers are still observed.

After activation, only the axe may travel to the nearest reachable iron cell, mine while capacity
is available, and bank its cargo. V468's other projected action has collision priority. A hire is
emitted only when the entire banked bill is available and V468's projected moves leave the shack
clear; same-turn deposits are deliberately excluded because `TRAIN` resolves before `DROP`.
Failure to observe worker three leaves the hire eligible for a safe retry. Observing worker three
permanently disables the overlay and leaves all workers under V468.

The arms differ only in their third-worker tuple and its rule-derived bill:

| arm | worker | plum | lemon | apple | iron |
|---|---|---:|---:|---:|---:|
| V581 | `1/1/1/1` | 3 | 3 | 3 | 3 |
| V582 | `2/2/1/1` | 6 | 6 | 3 | 3 |
| V583 | `2/3/1/2` | 6 | 11 | 3 | 6 |

The builder removes the unreferenced `LegacyCompactLeanBananaFarmBot` definition before adding
the wrapper. That type has no constructor or policy references in V468's selected controller;
its removal is command-neutral and leaves ample source headroom. The final compact programs are
90,154 UTF-16 units each. All readable and compact forms compile independently, all paired
runners compile, the wrapper's private-identifier transform round trips exactly, and all 162
repository tests pass.

## Standard behavior smoke

Each arm ran seed 9,941,000, both seats, against all 12 frozen opponent families: 24 games.

| arm | turn 100 | turn 200 | final | W/T/L | command divergences | issues |
|---|---:|---:|---:|---:|---:|---:|
| V581 `1/1/1/1` | +0.00 | +0.00 | +0.00 | 19/1/4 | 0 | 0 |
| V582 `2/2/1/1` | +0.00 | +0.00 | +0.00 | 19/1/4 | 0 | 0 |
| V583 `2/3/1/2` | +0.00 | +0.00 | +0.00 | 19/1/4 | 0 | 0 |

V468 scores 94.67/160.67/215.46 at turns 100/200/final and also goes 19/1/4. Its final
inventory contains 53.2 wood per game but the map produces only two harvest commands per game;
the absent complete fruit bill is unsurprising. All three inactive wrappers return V468's command
vector byte-for-byte.

## Fruit-heavy reachability panel

Seed 9,941,006 was selected before inspection of these candidates because V579's only three full-
panel third hires occurred there. Each arm again ran both seats and all 12 families: 24 games.

| arm | turn 100 | turn 200 | final | W/T/L | harvests | deposits | divergences |
|---|---:|---:|---:|---:|---:|---:|---:|
| V468 | 88.50 | 189.50 | 280.83 | 22/1/1 | 115.50 | 140.21 | -- |
| V581 | 88.50 | 189.50 | 280.83 | 22/1/1 | 115.50 | 140.21 | 0 |
| V582 | 88.50 | 189.50 | 280.83 | 22/1/1 | 115.50 | 140.21 | 0 |
| V583 | 88.50 | 189.50 | 280.83 | 22/1/1 | 115.50 | 140.21 | 0 |

Every arm retains two workers and emits only V468's turn-14 `TRAIN 3 2 0 1`. There are no issues
or opponent differences. Since V581 needs only three of each fruit, failure to activate on this
high-throughput map shows that V468's harvested stock remains committed to its live seed and score
cycles rather than accumulating as an early three-crop reserve. The more expensive V582 and V583
bills cannot repair that reachability failure.

## Consequence

The no-intervention surplus premise is closed. V579 proved that taking over the producer destroys
the renewable income loop; V581--V583 now prove that leaving the producer completely untouched
never exposes the diversified bill inside the payback window. A successful graft needs a narrow
middle ground: preserve harvesting and routing, but escrow the minimum bill by declining only
seed picks that would consume reserved plum, lemon, or apple stock. The axe can then provide iron
without taking the producer offline.

The next experiment should use the cheapest balanced bill, reserve its fruit after V468 has
established live sources, and retain the tested explicit-ID, post-pick affordability, post-move
shack-clearance, and producer-priority collision rules. This is distinct from another controller
handoff or another passive wait for surplus.

## Reproduction and integrity

- builder/test: `build_v581_surplus_axe_hire.py` / `test_build_v581_surplus_axe_hire.py`
- canonical runners, both reachability panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v581-v583-surplus-axe-hire/`
- V581 seed-0 panel/gate/diagnostics SHA-256: `cdbe1c88425ae2abc6a7a85a73570b3f31fbbcd1499a3ac35fc7d7473789baad` /
  `b3a1b79e215b5a6bded36583ee1336978786b9158a168f733e2670e4917c7066` /
  `531e2b0a6b3bb7caf95a26fea36fba7e5ce2bcddfb6b14d9c9a9c846d2b20f51`
- V582 seed-0 panel/gate/diagnostics SHA-256: `47dd175f18e287cdeeee83b52e387eb1591a48d55cd37e542d06267254bc340a` /
  `1726b12678a8be2b778ab4f7856a031bf5c643c85fea5f71b565afdf7ae5160f` /
  `0a195b1e13980cc1d28c4c2af02697d4b3ee5d0f03ce1ea56e89aebe9df785da`
- V583 seed-0 panel/gate/diagnostics SHA-256: `7b5fff0c314a2a66e6e0d205763e78bf8afff178046e73b94088e6790f15066b` /
  `9b143dac59d8186aad132b056e4ff2ab86b7e89c487226b7bfba76bf708ea60e` /
  `ceaf30abb4b1e703ae68be6f9a612863f09f78a5a112d1f8981f79097a262084`
- V581 seed-6 panel/gate/diagnostics SHA-256: `c3ced8cf8432b6d8f81a6ef2db84ccb904c89ffad535bb56e8941b48157a58ae` /
  `4977b12d3fd30dd983903b982e838c9fbf1caee8c9c40c588aa73ca91a3b0bae` /
  `22ab4276ec2ff8c717869f6364ef828d5ee0cf442850ac7404455f4cb05357db`
- V582 seed-6 panel/gate/diagnostics SHA-256: `6ef9a208d65930930b13ecce10078bebb006fde4ff317f423dd40c11c6c1f388` /
  `5bf8b6a43909da29c6ae68e8ada4e450971984c13bb484215fdd55c908ed21c4` /
  `3f9da5c4166522e1c8a67ae11e4db369112f8409bf4a0928f8d0132d71ab56d4`
- V583 seed-6 panel/gate/diagnostics SHA-256: `699e7e5c8bde9b3f1dda65cca23cdf83405524bb3308e0df35d46734f8cc2b9a` /
  `a451e7882d52bb77ff58976c4822f0e798f4ccd6f3dca81aa29501d041c5e7f0` /
  `b00639319d1f5007904ba8e36c77772fc885f0d1f37488fe437392d24241e6ae`
- V581/V582/V583 module SHA-256: `a576ea9f76cdfc62ddb0182c5f0f0b4ceb4138ca5cb5f4af0fb85af683547b2b` /
  `f9001c37f05f9ac8000f0c1ed075fb362c5a3cde2f52cf3bae6ac42bccbef512` /
  `4e6a4d287c366f5d91ca900d4098960c42d2f30ce69f27734ca32118dcf7b872`
- V581/V582/V583 compact SHA-256: `e2ba385568eece9f0c37cb73a92ea7a79510b13a6bfe2d70e71884e5750da60b` /
  `ae0af46d9b1e3369e4859de1efdd7171f5ace78fbb3c9762c21955614c52144f` /
  `cc56d36de12421419764103ee2a82627440163ef9bf03c0d31f3cb6aab25e935`
- V581/V582/V583 runner SHA-256: `45a1b5e6bdbca9776aa4bc647713670474bb5e25086b3c1677842c3aa010ad1c` /
  `a5433940da1080d33201548ee09fc006fa64a8c6b71b5bd3ddd4054e648cc543` /
  `a5895ae1fa63303a550d53a0b9fae42c5209b17cc3f47a27e02a8bdb7183b676`
- builder/test SHA-256: `5aba6c9cc9d694a2304b4179ccfb17dfdac60ddd083032b43f75295dc11534ca` /
  `3a458adcf3e6b104baa9bd35aea0b81d0f9e7b55458ce14e7e43fd2c9bd671af`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
