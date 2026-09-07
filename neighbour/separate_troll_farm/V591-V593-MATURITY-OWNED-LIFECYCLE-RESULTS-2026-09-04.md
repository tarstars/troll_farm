# V591--V593 maturity-owned two-worker lifecycle

## Verdict

Typed ownership, mature felling, and same-kind refill repair V588 on the behavior smoke but do not
transfer across the frozen map set. V591, whose size-two target matches the inherited axe's carry
two, scores +0.00/+15.83/+33.54 at turn 100/200/final on seed 9,941,000 and improves own score
against all 12 opponent families. It therefore entered the full 192-game panel. There it reverses
to +0.00/-15.66/-22.20, adds 15 losses, and fails the gate.

The lifecycle itself works: relative to V468, V591 adds 8.68 plants, 20.37 chops, and 4.42 final
wood per full-panel game. The failure is assigning V468's harvest-positive starter to that
lifecycle. On the six maps where V468 has a large renewable harvest economy, V591 removes about
31 harvests and 39 deposits overall. The 4.42 extra wood is worth 17.68 score, while final nonwood
inventory falls about 39.88 points, leaving the observed 22.20-point loss.

This closes full two-worker handoff, not owned-crop maturation. The next experiment must retain
V468's producer commands and apply ownership/maturity policy only to its harvest-zero axe.

No candidate entered fresh maps, duels, packaging, or platform publication. `bot.rs`,
`submission.rs`, and the live V543 platform agent remain unchanged.

## Isolated candidates

Every arm derives from V588 cap six and therefore from exact V468. V468 remains authoritative
through turn 100; the lazy controller then keeps exactly the observed two workers and has no
later-worker specification or bill.

At first call the controller adopts live crops within bank distance one as prefix-owned crops. It
records later plants in a `cell -> PlantKind` map. A disappeared owned crop creates a durable typed
refill count, which is reduced only by planting the same kind. The producer chooses banked refill
or balancing seed work before harvesting, reserves ripe owned trees before axe assignment, and
uses nonowned ripe fruit only to bootstrap an empty cap slot. The producer may chop only external
trees.

The axe rejects an owned tree below the target while growth, felling, and banking still fit. Once
the target is reached, an owned tree ranks before external wood. Arms differ only in that target:

| arm | target size | rationale | compact UTF-16 units |
|---|---:|---|---:|
| V591 | 2 | matches axe carry two | 99,609 |
| V592 | 3 | intermediate maturation | 99,609 |
| V593 | 4 | public-leader maturity pattern | 99,609 |

All readable and compact programs compile independently, all paired runners compile, the three
arms normalize to exact equality after replacing the maturity constant, and all 197 repository
tests pass.

## Behavior smoke

Each arm ran seed 9,941,000 in both seats against the 12 frozen opponent families: 24 games per
arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | candidate W/T/L | decision |
|---|---:|---:|---:|---:|---|
| V591 target 2 | +0.00 | +15.83 | +33.54 | 21/0/3 | admit |
| V592 target 3 | +0.00 | +5.96 | +33.21 | 20/0/4 | smoke only |
| V593 target 4 | +0.00 | +3.38 | +31.17 | 18/0/6 | smoke only |

V468 scores 94.67/160.67/215.46 and goes 19/1/4. V591 scores 94.67/176.50/249.00,
banks 61.50 versus 53.21 wood, and gains against every family from +8.5 against
`legend_balanced` to +63.5 against `silver_boss`. It retains V468's 38.71 deposits almost exactly
at 38.08 while adding 7.83 plants and 8.38 chops. This was a credible 84% of the required final
gain with both checkpoint inequalities intact, so V591 alone advanced.

The sweep favors size two. Waiting for size three gives up 9.87 points at turn 200 without a final
gain; size four gives up another 2.58 at turn 200 and 2.04 final while worsening outcomes. With a
carry-two axe, later maturity does not bank the third or fourth wood from a fell.

## Frozen V468 gate

V591 ran seeds 9,941,000--9,941,007 in both seats against all 12 opponent families: 192 paired
games.

| checkpoint | V468 | V591 | delta |
|---|---:|---:|---:|
| turn 100 | 93.01 | 93.01 | +0.00 |
| turn 200 | 176.18 | 160.52 | -15.66 |
| final | 247.25 | 225.05 | -22.20 |

V591 goes 165/0/27 versus V468's 177/3/12. Opponent mean score increases 30.71. First command
divergence is turn 101--114 with median 101, and the candidate differs on 175.69 command turns per
game. This proves the exact turn-100 boundary. Both arms retain exactly two workers and the same
first training specifications and turns; V591 has zero legality, critical, or unclassified
issues.

Own-score delta by family is negative against ten of 12, from -0.6 against `mybot` to -61.0
against `norx_native_three`. Only `resident` (+17.9) and `silver_boss` (+26.5) are positive. The
failure is broad rather than one opponent interaction.

## Map mechanism

The smoke seed is an atypical low-harvest V468 economy. Separating the full panel by map makes the
transfer boundary explicit:

| seed | V468 harvests | V591 harvests | final delta | wood delta |
|---:|---:|---:|---:|---:|
| 9,941,000 | 2.0 | 10.5 | +33.54 | +8.29 |
| 9,941,001 | 84.7 | 40.5 | -10.75 | +11.42 |
| 9,941,002 | 104.6 | 45.4 | -49.00 | +4.33 |
| 9,941,003 | 3.8 | 15.2 | +8.25 | +1.42 |
| 9,941,004 | 1.6 | 8.5 | +21.17 | +5.17 |
| 9,941,005 | 118.4 | 62.8 | -62.21 | +0.50 |
| 9,941,006 | 115.5 | 70.7 | -68.54 | -4.00 |
| 9,941,007 | 118.8 | 48.0 | -50.42 | +8.17 |

V591 is positive on the three maps where V468 averages fewer than four harvests and negative on
all five maps where V468 averages at least 84.7. Maturation is productive on both regimes, but
the opportunity cost of replacing the producer dominates whenever V468 already has renewable
fruit sources.

The full-panel means show both sides directly:

| per-game mean | V468 | V591 | change |
|---|---:|---:|---:|
| `PLANT` | 11.05 | 19.73 | +8.68 |
| `CHOP` | 155.08 | 175.45 | +20.37 |
| final wood | 45.02 | 49.44 | +4.42 |
| `HARVEST` | 68.67 | 37.70 | -30.97 |
| `DROP` | 97.52 | 58.34 | -39.18 |
| `MOVE` | 193.29 | 262.79 | +69.50 |
| final score | 247.25 | 225.05 | -22.20 |

Thus the new lifecycle fixes V588's missing crop and lumber throughput, but another whole-policy
handoff necessarily trades away the wrong asset. Further maturity constants, caps, or handoff
turns do not address that observed producer loss.

## Consequence

The next architecture should run the real V468 controller continuously, record its actual plant
commands for exact ownership, and never replace the harvest-positive worker's action. Only the
harvest-zero axe should be redirected: protect recorded owned saplings, prioritize owned trees at
size two, and otherwise preserve a collision-safe V468 axe action. This reverses the unsuccessful
V575 composition, which preserved the axe and borrowed the producer, and directly tests whether
the measured +4.42 wood can be retained without the -39.18 deposits.

## Reproduction and integrity

- builder/test: `build_v591_maturity_owned_lifecycle.py` /
  `test_build_v591_maturity_owned_lifecycle.py`
- canonical runners, smokes, full panel, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v591-v593-maturity-lifecycle/`
- V591 smoke/full panel SHA-256: `e5c94797746072e37a0bc0788e49fd77a6c815cb639e94eab45f44dfd7afb434` /
  `1af8eb1ef240702191fc55e2598e8da210d7c890d6d5bcd1ba0ff0ae307ace1a`
- V592/V593 smoke panel SHA-256: `27a34e0a6577129d3d63e62c3b2c84f653ae400418b94bd4510677f92035486d` /
  `d45ad4a4199a24a51f320134809bd01505cbed45a587d519f4b0533faab53628`
- V591 smoke/full gate SHA-256: `ddc92fa04e8937b9c90fead83d077a336d1405438b1362b6dadcb5970a44fd78` /
  `4a9b0a30f844e4993d0a6b0fbba3080f7f45a09e11768e2440a729b63e09d32b`
- V591 full diagnostics SHA-256:
  `d85557629fe68ab61081eea240194080d077941051318381b73930837a23180a`
- V591/V592/V593 module SHA-256: `1b4cd4b93614d6ae1ea7ab36862cac8d621f7a29a613af4e2c3e33d9c105d221` /
  `d4669917075d39f94a4ca74d73f26fb9c6e13ff282d50397c430200a9271da1a` /
  `07b7ecc0b7d009dde989cd2c34a12bd02f58fdf97ff337a12447fd3c01efad7f`
- V591/V592/V593 compact SHA-256: `4231071cd3874e6a9105a31c0e5d9fd72ec13a8c8273ca9a7d4f290c15974c09` /
  `80bbe8c38ed226ede19f10e026d75d4fd9506cf33c20bcf0e83da8b0cf5f1e00` /
  `1c01fbfbc91cb2acb12140fc38f4c5bd95a4e384829530f088953e2b818c7a53`
- V591/V592/V593 runner SHA-256: `4f10fa4afae323bc6d4c38c46d3a373459f3c1544a3f22823908ec264c1fdf2e` /
  `14f23b91b7e25bc078b9ccd42f4a0010a36c99254ce21c99b7cf6b2d1e25d0d6` /
  `14a5c0b4d1ee1c156fca32ebecc3e1ba46487240820b8560de2fcd3aa3d5211e`
- builder/test SHA-256: `b884d6f89504296a19741d3da58bbcf7a2bde5a0642c2df624b90ed8f5c142dd` /
  `2bdfd7db51149c6f249f58e9a43ce7c5d7a42c7a146a7e140b5493fe17ceffde`
- production hashes retained: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
