# V560--V562 harvest-free banana battery result

## Verdict

FAIL. Removing the starter's reserve-harvest job did not turn mature bananas into profitable wood
batteries. All variants were exact V468 through turn 100, but cap one was down 0.58 points at turn
200 and finished only +0.03; caps two and three were down 0.63 and finished +0.05. The required
final gain is +40. Caps two and three produced identical game rows. No candidate advanced to
fresh maps, duels, packaging audit, or the platform; `bot.rs`, `submission.rs`, and published V543
remain unchanged.

## Design and repair path

V557--V559 showed that harvesting mature reserve bananas with the starter displaced 35 apple
cycles. V560--V562 isolated that cost while retaining the repaired reserve boundaries:

- an outer overlay evaluated exact V468 on every turn and returned its commands untouched through
  turn 100;
- the roster stayed at V468's two workers, with every battery action assigned to the higher-id
  chopper;
- only V468's own late banana conversion opportunity could start a reachable, non-door plot, with
  hard live caps of one, two, or three;
- the chopper fetched and planted the seed, protected the tree while it grew, felled it only at
  size four, and banked the wood;
- the starter was never routed to or asked to harvest a battery tree;
- battery fruit was masked from V468's cloned planning view, while the rest of each tree remained
  visible, so V468 could not independently harvest the protected fruit; and
- an apple commitment guard yielded to the chopper's selected apple pick, plant, approach, chop,
  carried apple, or ordinary wood-banking action.

The initial harvest-free cap-three form still lost about 40 apple cycles. Hiding entire battery
trees from V468 was rejected at smoke because it caused movement jams. Fruit-only masking removed
those jams, but a trace showed that the higher-id chopper itself performs late apple conversions.
The apple commitment guard was added before the final panels. Its 24-game smoke was exact through
turn 100, issue-free, and +3.0 final, so the frozen cap sweep proceeded.

## Frozen 192-game development panels

Each candidate ran on seeds 9,941,000--9,941,007, both seats, and the unchanged 12 opponent
families. Baseline commands and fields were identical across all panels.

| candidate | live-plot cap | own score at 100 / 200 / 300 | final own delta | opponent delta | margin delta | W/T/L | gate |
|---|---:|---:|---:|---:|---:|---:|---|
| V468 baseline | -- | 93.01 / 176.18 / 247.25 | -- | -- | -- | 177/3/12 | -- |
| V560 | 1 | 93.01 / 175.60 / 247.28 | +0.03 | +1.05 | -1.02 | 178/2/12 | FAIL |
| V561 | 2 | 93.01 / 175.55 / 247.30 | +0.05 | +1.22 | -1.18 | 178/1/13 | FAIL |
| V562 | 3 | 93.01 / 175.55 / 247.30 | +0.05 | +1.22 | -1.18 | 178/1/13 | FAIL |

No candidate command diverged on or before turn 100. Each panel had 52 command-divergent games,
with first differences on turns 101--229; final own score changed in 48 cap-one rows and 49
cap-two/cap-three rows. All rows ended with two own workers. V560 had no recorded command issue;
V561/V562 each had three supported noncritical `move_blocked` events and zero critical or
unclassified issues.

V561 and V562 had identical game rows, including full command streams: the conversion-only entry
condition never exposed a useful third simultaneous slot. Their TSV files differ only in runner
latency metadata. Candidate p95/max planning time was 1.11/5.49 ms for V560, 1.18/7.01 ms for
V561, and 1.11/5.11 ms for V562. Each compact source is 97,603 UTF-16 units.

## Mechanism

The overlay contains no reserve harvest action, yet it still consumed more of the chopper's base
work than its mature-tree yield repaid. Across the whole panel, V560 lost 319 chop commands, added
606 moves and 431 waits, and banked 20 less wood. V561/V562 lost 381 chops, added 762 moves and
456 waits, and banked 24 less wood. Per game, the cap-two form was therefore -2.26 chops, +3.97
moves, +2.38 waits, and -0.13 wood.

The apple guard preserved immediate commitments, not the future cadence that a multi-turn battery
trip displaces. V560 still lost 35 apple pick/plant cycles across the panel; V561/V562 lost 38.
They added only one or two banana picks and no net banana plant commands. The small increases in
aggregate harvests and drops are indirect trajectory changes, not battery harvesting.

The effect also gives opponents room: own score was essentially flat, while opponent score rose
1.05--1.22 per game and margin fell. Cap two's largest own losses were against `compact_gold`
(-4.62), `mybot` (-1.44), and `boss_real` (-0.88); gains against `script_boss` (+4.00) and
`silver_boss` (+2.50) did not generalize. One additional loss at cap two/three confirms that the
nominal score gain is not strategically useful.

This closes the two-worker mature-battery idea. Harvesting the fruit diverted the starter in
V557--V559; not harvesting it still diverts the only axe, suppresses normal mature chops, and
perturbs later apple work. Raising the cap cannot add capacity. The unresolved upstream question
is how the strongest public opponents fund parallel workers without paying the opening penalty
seen throughout V472--V554; the next queue item audits that funding provenance before another
architecture is built.

## Reproduction and integrity

- builder: `build_v560_harvest_free_batteries.py`
- focused tests: `test_build_v560_harvest_free_batteries.py` (7 focused; 90 repository tests pass)
- panels: `/data/separate_troll_farm-working/panels/2026-09-04-v560-v562/v560-dev8.tsv`,
  `v561-dev8.tsv`, and `v562-dev8.tsv`
- panel SHA-256: V560 `14d36588b898e73825add9cd38f1a08fec2c5cec89d4ed8721ab27587324591b`,
  V561 `d367472d54e222514a4694a0bdd5bbe68eef5cf72cbcde702af0610ee76e9f4e`,
  V562 `07aa792f485cc8ffcb28796c10b271ea3b8ddbf22344084d759cfac3155dd885`
- gate JSON SHA-256: V560 `323a35d88c4a68c38dace5f9df03086207f577bf740042a93466a92d341048ae`,
  V561 `4505655b5f96dd0891d5956f384de72240c40a0753f631e14be85e50fa821cca`,
  V562 `0aca1c68dbfce34e21ca4d9a057c8cc006e3b82dbfc9174f9137d5853e3c4379`
- compact SHA-256: V560 `eb22cf164fc48856f5d8ef6cf88f9cb8922a595c54a1926af5c1baf9d17814a2`,
  V561 `a975f8c02f0696565307825f18ba1a808c110c66626b0fc1552c79ceb45d01d0`,
  V562 `4b59ab82417bf636d8fa1f66350e5b9beb12346d325c61c616f17ae717a868d5`
- builder/test SHA-256: `b759d5ae65a51f7a9141f3b6e07a9613238174d8bd3945a67f1705e0f54f3858` /
  `2c3785ebff8ae258a21826605ccb755ccf90a70989c13569c8217366c5be3abb`
- exact V468 base/bridge SHA-256: `f3e6442270fa289247167e017be89b31563a7543312216e04a508b3d7f989b59` /
  `0178423a17af97c73ed2b1f7f8530bb0bb028bef16974d2f0aaaf078ce1bfc1e`
