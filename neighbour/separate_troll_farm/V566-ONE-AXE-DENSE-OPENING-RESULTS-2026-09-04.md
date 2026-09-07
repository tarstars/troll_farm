# V566 one-axe dense opening

## Verdict

V566 confirms that preserving an axe during the dense two-worker bill phase repairs much of the
opening, but it also proves that a carry-one sole producer cannot fund V564's late economy fast
enough. Relative to V564, it recovered 44.14 own points at turn 100. Worker three then arrived
about 69 command turns later, worker-four completions fell from 175 to 134, and final own score
fell 156.16. Against exact V468, V566 was -24.61 at turn 100, -59.94 at turn 200, and only +15.31
at the finish. It failed every promotion requirement and was not published.

The surviving insight is narrower and useful: one early axe is necessary but not sufficient. The
remaining opening cost is visible as fewer productive actions and far more movement than V468,
principally because the carry-one producer establishes the bill orchard. The next experiment will
put the faster carry-two worker on production and test natural-fruit-first collection before
planting shortage sources, while retaining an axe.

`bot.rs`, `submission.rs`, and the live V543 platform agent remain unchanged.

## Isolated change

V566 regenerates exact V564 and changes two expressions inside R1FA:

1. With exactly two workers, only ordinal zero is a producer; ordinal one is a dedicated axe.
2. That axe may enter V564's unchanged chop selector immediately rather than waiting for turn 55.

At three workers the role predicate becomes byte-equivalent in behavior to V564: ordinals zero
and one are producers and ordinal two is the hybrid. The `2/3/1/2` third worker, `2/4/0/3` fourth
worker, training costs, source-shortage calculation, ten-tree late cap, pathing, target scoring,
adaptive guard, and all outer wrappers are unchanged. Focused normalization tests prove that
reversing the two expressions reconstructs exact V564.

The readable and compact programs compiled independently. The compact program is 99,910 UTF-16
units, 90 below the platform limit. All 106 repository tests pass.

## Frozen V468 gate

The development panel used the frozen eight seeds, both seats, and 12 opponent families: 192
paired games.

| checkpoint | V468 | V566 | delta |
|---|---:|---:|---:|
| turn 100 | 93.01 | 68.40 | -24.61 |
| turn 200 | 176.18 | 116.24 | -59.94 |
| final | 247.25 | 262.56 | +15.31 |

V468 went 177/3/12; V566 went 158/2/32. Opponents scored 32.48 more points against V566. The
candidate missed both nonnegative checkpoint requirements, missed the +40 final requirement by
24.69 points, and added 20 losses. A favorable one-seed smoke (-9.0/-23.0/+171.8) did not
generalize, which is why the full frozen panel remains mandatory.

V566 improved final score over V468 in ten of the 12 families, but lost 14.06 against gold
adaptive and 26.62 against resident. The positive family deltas did not translate into safe
outcomes because the candidate also gave opponents more time and resources.

## Causal comparison with the dense parents

All three panels share the same rows and exact V468 baseline.

| measure | V546 | V564 | V566 | V566 vs V564 |
|---|---:|---:|---:|---:|
| turn-100 own score | 20.11 | 24.26 | 68.40 | +44.14 |
| turn-200 own score | 142.91 | 148.39 | 116.24 | -32.15 |
| final own score | 378.48 | 418.72 | 262.56 | -156.16 |
| final opponent score | 160.46 | 168.39 | 140.70 | -27.69 |
| wood | 84.89 | 95.10 | 60.45 | -34.65 |
| final workers | 3.78 | 3.83 | 3.56 | -0.27 |

V566 also finished 115.92 behind V546. Its gain over V468 is therefore not a stronger dense
economy; it is the residue of a late phase that starts too late to repay the opening.

The command stream makes the capacity bottleneck explicit:

| event | V564 | V566 |
|---|---:|---:|
| games buying `2/3/1/2` worker three | 176 | 165 |
| mean command turn for worker three | 96.59 | 165.53 |
| median command turn for worker three | 90 | 174 |
| games buying `2/4/0/3` worker four | 175 | 134 |
| mean command turn for worker four | 169.75 | 239.60 |
| final four/three/two-worker games | 175/1/16 | 134/31/27 |

Through turn 100, V566 issued 37.84 chops per game, 32.59 more than V564, while harvesting 13.54
times, 13.38 fewer. That is the intended axe-for-producer exchange and explains the 44-point
recovery over V564. It still remained less productive than V468 in the same interval: 13.34 fewer
chops, 8.08 fewer harvests, 37.75 more moves, and 4.93 more plants per game. Keeping the axe did
not remove the source-establishment and carry-one travel tax.

The parent delta was consistent across families: V566 finished below V564 in 11 of 12, by 101.88
to 209.50 points; resident alone gained 11.00. V566 recorded seven noncritical `move_blocked`
events in five rows and no critical or unclassified issues. Its failure is economic, not a runner
or legality artifact. Planning latency was 0.84 ms at p95 and 3.81 ms maximum.

## Consequence

V564 and V566 now bound the allocation problem. Two producers buy worker three near turn 97 but
score only 24 at turn 100; a dedicated capacity-two axe raises that checkpoint to 68 but leaves a
carry-one producer buying worker three near turn 166. A simple later release of the same axe
cannot address the 25-point gap to V468 while also recovering roughly 60 points by turn 200.

The next candidate should reverse the two-worker specialization: use the movement-two,
carry-two, harvest-one trained worker as the sole producer and leave the original worker as the
axe. A bounded comparison should also harvest reachable ripe deficit fruit before committing seed
trips. This follows the V563 elite evidence—BoatBuilder planted only two lemon sources and one plum
before its turn-48 third worker—and directly attacks V566's measured movement and orchard-build
overhead without returning to two full-time producers.

## Reproduction and integrity

- builder/test: `build_v566_one_axe_dense_opening.py` /
  `test_build_v566_one_axe_dense_opening.py`
- archived runner, build log, smoke, full panel, gate, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v566-one-axe/`
- panel/gate/diagnostics SHA-256: `6e5d1d17954ca7c9d06df6d712c74437cda22422d3773cb0c1071bcf37d062a0` /
  `aa2d588edf43c76fd035cdb58b20d06925760f8cdb583e70ec47bcf0b8512e93` /
  `b2cbedcf55f571ee9cf9533e6f3da33462e39aff1c1c2a9ea9220137e4e9246e`
- module/compact SHA-256: `1582d63be89a0d4ff7047cf5d211da915a8a42f19de224e3cef76486fff2fd58` /
  `9a4aaa2d392fe511f3f3297e86c3d33e976b5afd10c9928ca141ea294215fa13`
- builder/test SHA-256: `91af70de98d8e31ef406ff1bfbcd9cac0fdf750880b486a92afa38fbcb742747` /
  `b8fa478a21ac08cb4b719e117de22704993efea83e06b6235c9d887332374c38`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
