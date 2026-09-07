# V572--V574 observed-second-train dense handoff

## Verdict

The missing early handoff interval does not rescue a wholesale dense-controller switch. V573, the
best complete arm, scored -24.20/-49.43/-25.69 against exact V468 at turns 100, 200, and final on
the frozen 192-game panel. V574's live-source credit scored -22.04/-50.25/-41.78. They went
154/0/38 and 150/0/42 versus V468's 177/3/12. Both fail every score gate, so neither entered fresh
maps, duels, packaging, or platform publication.

The state boundary itself is clean and materially earlier than V552--V554. All 192 first V468
training command/turn pairs are exact, and the first changed command occurs only after the
observed second worker exists. The failure is the continuation: even capability-aware R1FA
replaces both established workers' command policies while assembling its bill. V573 added 202.46
moves per game, removed 39.59 chops and 12.75 harvests, and allowed opponents 18.57 more points.
Its 159 third-worker and 93 fourth-worker completions still did not repay that displacement.

`bot.rs`, `submission.rs`, and the live V543 agent remain unchanged.

## Isolated candidates

All arms regenerate the exact V564 economy: V543's fast R1FA controller, a ten-tree verified
source cap, and the locally successful `2/3/1/2` third worker. They add the V552 late-call repairs
so plant provenance initializes on R1FA's first call and harvest work is never assigned without
harvest power. An observed-state wrapper returns V468's commands byte-for-byte while fewer than
two own workers exist, latches only after a later state contains the second worker, and calls only
R1FA thereafter. Because R1FA first sees two workers, it does not train its native second worker.

The three arms then isolate two repairs:

1. V572 is the direct state-handoff control and retains V564's ordinal roles.
2. V573 makes every harvest-positive worker a producer, makes the inherited harvest-zero worker
   an immediate axe, and makes the capacity-three third worker both producer and mining hybrid.
3. V574 retains V573's roles but credits actual ripe fruit on reachable, own-half, not-known-
   opponent trees toward source capacity. Owned dense sources remain counted separately, so the
   arm changes only whether currently collectible neutral fruit defers replacement planting.

The source-credit transformation normalizes exactly back to V573, and the two role blocks
normalize V573 back to V572. The third/fourth specifications, training costs, ten-tree cap, crop
order, chop scoring, and conflict resolution are identical. The final compact sizes are 99,596,
99,689, and 99,982 UTF-16 units. All readable and compact forms compile independently, all three
paired runners compile, and all 127 repository tests pass. To recover platform headroom without
changing commands, the builder removes one unused R1FA pathfinder and an unnecessary `mut`.

## Behavior smoke

Each arm first ran seed 9941000, both seats, against all 12 frozen opponent families: 24 games.

| arm | turn 100 | turn 200 | final | candidate W/T/L | opponent delta | decision |
|---|---:|---:|---:|---:|---:|---|
| V572 direct | -41.63 | -28.38 | +117.29 | 20/0/4 | +21.00 | no full panel |
| V573 capability roles | -14.83 | -19.13 | +99.04 | 20/0/4 | +28.08 | admit |
| V574 live-source credit | -11.54 | -20.88 | +84.00 | 20/0/4 | +31.38 | admit |

V468 went 19/1/4. V572 proved that the early state handoff can unlock the dense late phase on this
geometry, but its idle-before-turn-55 harvest-zero role caused a 41.63-point turn-100 loss. V573's
capability map recovered 26.79 points at turn 100 and 9.25 at turn 200 relative to V572. V574
recovered another 3.29 points at turn 100. Both repaired arms were therefore credible enough to
test across maps despite their negative smoke checkpoints and were admitted to the full frozen
panel; the unadapted control was not.

All 24 first V468 train commands were exact. The handoff first diverged at turn seven, the first
state after this smoke's turn-six `3/2/0/2` worker appeared. V572/V573 had no runner issues. V574
had one noncritical `move_blocked` event and no critical or unclassified issue.

## Frozen V468 gate

V573 and V574 ran seeds 9,941,000--9,941,007, both seats, and all 12 frozen opponent families:
192 paired games each.

| checkpoint | V468 | V573 | delta | V574 | delta |
|---|---:|---:|---:|---:|---:|
| turn 100 | 93.01 | 68.81 | -24.20 | 70.97 | -22.04 |
| turn 200 | 176.18 | 126.76 | -49.43 | 125.93 | -50.25 |
| final | 247.25 | 221.56 | -25.69 | 205.47 | -41.78 |

V573 lost the own-score comparison against every opponent family, from -6.62 against
`silver_boss` to -66.44 against `compact_gold`. V574 also lost every family, from -2.06 against
`mybot` to -67.00 against `compact_gold`. Opponent final score rose 18.57 for V573 and 14.82 for
V574. The smoke's +84--99 late gains were therefore specific to one map, not a portable scaling
edge.

The prefix invariant held across the variable V468 opening. Its first worker-two train mix was 96
rows of `3/2/0/2` and 24 each of `1/2/0/3`, `2/2/0/2`, `1/2/0/1`, and `3/2/0/1`; every one has
harvest power zero. Candidate and baseline first-train command/turn pairs matched in all 192 rows.
First divergence ranged from turn 2 to 21, median 13, only when the state-based worker-count gate
observed the result of V468's own opening. The role repair therefore covered the actual roster
variation rather than overfitting the smoke's one specification.

## Why the extra workers did not pay

| measure per game | V468 | V573 | delta | V574 | delta |
|---|---:|---:|---:|---:|---:|
| final score | 247.25 | 221.56 | -25.69 | 205.47 | -41.78 |
| wood | 45.02 | 50.17 | +5.15 | 46.78 | +1.76 |
| workers | 2.00 | 3.31 | +1.31 | 3.17 | +1.17 |
| moves | 193.29 | 395.75 | +202.46 | 410.52 | +217.23 |
| chops | 155.08 | 115.49 | -39.59 | 108.78 | -46.30 |
| harvests | 68.67 | 55.92 | -12.75 | 45.76 | -22.91 |
| drops | 97.52 | 78.22 | -19.30 | 69.71 | -27.81 |
| plants | 11.05 | 13.50 | +2.45 | 9.64 | -1.41 |

V573 trained the `2/3/1/2` worker in 159 games at mean/median turn 182.47/180, then reached the
`2/4/0/3` fourth worker in 93 games at 255.39/261. It banked 5.15 more wood, worth about 20.6
score, but lost roughly 46 points of nonwood inventory and raised opponent score. The established
V468 route is productive work, not a neutral prefix state: replacing its targets with bill-source
and mine routes more than doubled movement while reducing both immediate income actions.

V574 improves V573 by only 2.16 at turn 100, then loses 0.82 at turn 200 and 16.08 final. It makes
3.86 fewer plants and 10.16 fewer harvests, adds 14.77 moves, banks 3.39 less wood, and completes
only 151 third and 74 fourth workers. Current ripe fruit is not durable source capacity: crediting
it postpones the orchard that must fund later bill cycles, so the shortcut becomes a late deficit.

Each full candidate panel contains one noncritical `move_blocked` and no critical or unclassified
issue. Candidate p95/max planning latency is 0.784/2.661 ms for V573 and 1.060/3.463 ms for V574.
The score losses persist across clean rows and every family; legality and latency are not causal.

## Consequence

V552--V554 showed that switching at turns 80--120 is too late; V572--V574 now show that switching
immediately after the second hire is still a teardown. The missing variable is not another handoff
turn. It is command ownership during the bill phase. R1FA must not replace the champion axe and
producer wholesale merely because the roster boundary was correct.

The next experiment will keep V468 as the continuation for inherited workers and splice only
bounded, currently useful bill actions into the starter while preserving the harvest-zero worker's
exact V468 axe command. Full V564 control should begin only after the capacity-three third worker
is actually observed. That isolates whether the bill can be accumulated as an overlay on champion
production, rather than by dismantling it. The full-panel movement and action deficits make this
a distinct mechanism; another fixed turn, source credit, or dense role predicate is closed.

## Reproduction and integrity

- builder/test: `build_v572_observed_second_dense_handoff.py` /
  `test_build_v572_observed_second_dense_handoff.py`
- canonical/archived runners, smokes, full panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v572-v574-observed-handoff/`
- V573 panel/gate/diagnostics SHA-256: `c8daeb8c1dfe3693d21bd9f1e71931afe00f99d9bc837d26d27b1ffa98b2ddda` /
  `f21bbb06c8d05108696d8aac68578a69ebf7a3bd7fab1aac3782fe94a79893b8` /
  `a8800a2183d23e19c548371d51b96dd3f88ac29e757763fd1afa605f95ccf528`
- V574 panel/gate/diagnostics SHA-256: `1fc55ae022278b70c3ffef909c75883b1146dc3f61d49062a030a6b4b56ab8ca` /
  `8218edf5df2d3661f979f807de6b36c0f87758216561a7944c7088b1ea9e408e` /
  `db3e9214a58d8a2f83c3cd02208d7f6d81ae4e559db1f5994f94f0f6aa977e32`
- V572 smoke/gate/diagnostics SHA-256: `6cf343331542695e2be7cc358781d612cb89efa22afb76f9d12b7ab4ffa4bbd3` /
  `41de9b5626fa855181e4fecec75c8cd587fc7bba863f4adb90455e3a14f8ff8b` /
  `09964d39950d22376190b0c2f0a59f30e99030c6d3dd7be5402e44507eb78fad`
- V572/V573/V574 module SHA-256: `37f8aa485550060803477a927028c88239e8a9627560e58fc182dcf4a0aac130` /
  `f5065e7436002fd076ee9cc4ca2d6747a3cf5a6adc391ebb9c6fe9c9195b82a0` /
  `ea0c232d7bbc3829ccd89a34f42482e9a4b085b78e99f9ef4ae2a76ccd2f3426`
- V572/V573/V574 compact SHA-256: `f546e9b6f90031b0a25286e4321c41666117eac8480f299ae1491e87c366f917` /
  `d4dce878c28368abbf0593e8209644199b521344908eecd5771eefd84edab321` /
  `f45b047435eb3bbabfbeecb064f2fc0be1680875c76d54018c9e593d56b7635c`
- V572/V573/V574 runner SHA-256: `aeab7a5ad2737c7848c101a14f304c04be483a223bb5f976f9d3be8cb4b66b83` /
  `5b63e595d9766e6fe77928e7e0105d6ed7c33fb41dfc9bed4c9419e10607956b` /
  `2126421c5c3e223227fd3f1f31c0f7196ad6c953d8a2a1a069fa637ca3ac2dad`
- builder/test SHA-256: `9406f4c8fa4d50732c5352c1f7e1bea05780e605391b84c2049a64fa7c672897` /
  `a3ad2356fd8607b25160036fabed3711fa52f255dad9c21bac75a423152be5a0`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
