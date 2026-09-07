# V557--V559 champion-prefix banana reserve result

## Verdict

FAIL. All three candidates preserved exact V468 through turn 100 and kept its two-worker roster,
but no reserve cap passed the frozen development gate. V557 was down 0.65 points at turn 200 and
finished only +0.02; V558 and V559 were down 0.63 at turn 200 and finished -0.01. The required
final gain is +40. No candidate advanced to fresh maps, duels, packaging audit, or the platform;
`bot.rs`, `submission.rs`, and published V543 remain unchanged.

## Design and implementation

V556 found continuous banana supply and usable planting geometry in the strongest mature V543
losses, but zero banana planting after the fourth worker. V557--V559 tested whether that crop
advantage could instead be attached to V468's strong opening without a third-worker bill:

- an outer overlay always evaluated exact V468 first and returned its commands untouched through
  turn 100;
- turn-one live trees were retained as wild provenance, and the reserve could start only after no
  surviving wild tree was within four path cells of an own-shack door;
- one, two, or three reachable non-door plots within two path cells of an own door formed the hard
  live-tree cap;
- only V468's own `PICK BANANA` or `PLANT BANANA` conversion opportunity could start a plot, so a
  new farm cycle could not cancel a suppressive far-tree trip;
- the higher-id chopper planted the banana, surviving initial wild trees were the only substitute
  chop targets while it grew, the lower-id harvest-capable starter took the mature fruit, and the
  chopper felled only at size four;
- reserve fruit and wood cargo had explicit provenance, plot theft/obstruction timed out cleanly,
  and the dead legacy farm was removed to keep the compact source under the platform limit.

The first cap-one smoke exposed three overlay defects: it started mid-trip, treated every banana
carried by the starter as reserve cargo (creating a `PICK`/`DROP` loop), and changed substitute
tree targets every turn. That form lost 45.7 own points. Focused regression tests were added before
repairing it with home/conversion-only starts, reserve-cargo provenance, and persistent natural-tree
fallback targets. The repaired cap-three smoke was exact at turn 100, had zero issues, and gained
3.0 own points on 24 games, allowing the frozen panels to proceed.

## Frozen 192-game development panels

Each candidate ran on seeds 9,941,000--9,941,007, both seats, and the unchanged 12 opponent
families. Every V468 baseline field and full command stream was identical across the three panels.

| candidate | live-plot cap | own score at 100 / 200 / 300 | final own delta | opponent delta | margin delta | W/T/L | gate |
|---|---:|---:|---:|---:|---:|---:|---|
| V468 baseline | -- | 93.01 / 176.18 / 247.25 | -- | -- | -- | 177/3/12 | -- |
| V557 | 1 | 93.01 / 175.53 / 247.27 | +0.02 | +1.07 | -1.06 | 179/2/11 | FAIL |
| V558 | 2 | 93.01 / 175.56 / 247.24 | -0.01 | +1.21 | -1.22 | 180/1/11 | FAIL |
| V559 | 3 | 93.01 / 175.56 / 247.24 | -0.01 | +1.21 | -1.22 | 180/1/11 | FAIL |

No candidate command diverged on or before turn 100. There were 52 changed games in each panel,
with first differences on turns 101--229. V558 and V559 were behaviorally identical on every row:
the conversion-only start gate never exposed enough independent opportunities to use the third
slot. All rows ended with exactly two own workers. V557 had one supported noncritical
`move_blocked`; V558/V559 had three each, with zero critical or unclassified issues.

The candidates stayed within the latency and size envelopes. V557's candidate p95/max planning
times were 1.18/6.93 ms; V558/V559 were about 1.11/5.31 ms. Each compact source was 98,791 UTF-16
units.

## Mechanism

The reserve did create and harvest mature bananas, but it consumed the two existing income roles.
Relative to V468, V557 added three banana plant commands over the whole panel but lost 32 apple
pick/plant cycles. V558/V559 added ten banana plants and two banana picks but lost 35 apple
pick/plant cycles. Per game, the cap-two/cap-three form added 0.40 harvest commands and 3.79 moves,
but lost 1.63 chops and added 2.23 waits. Its total ring-plant count therefore fell 0.21 even while
banana planting rose.

Across V558/V559's 52 changed games, mean own-score delta was -0.04 while opponents gained 4.46,
for -4.50 margin. The mature fruit merely replaced the starter's valuable apple cadence; protected
growth and routing removed chopper pressure and gave opponents more uncontested income. Increasing
the cap cannot repair those role costs, and a safe gate makes the nominal third slot dormant.

This is a narrower result than the old single-slot grow-before-fell failure: the new implementation
proved exact champion-prefix composition, non-door parallel geometry, provenance-safe cargo, and
conversion-only starts. The remaining testable part is the one role cost isolated here: grow
several fast bananas as wood batteries and fell at size four without sending the starter to
harvest. That follow-up has a new reason because these panels directly measured 35 lost apple
cycles from the harvest detour.

## Reproduction and integrity

- builder: `build_v557_champion_prefix_banana_reserve.py`
- focused tests: `test_build_v557_champion_prefix_banana_reserve.py` (8 passed)
- panels: `/data/separate_troll_farm-working/panels/2026-09-04-v557-v559/v557-dev8.tsv`,
  `v558-dev8.tsv`, and `v559-dev8.tsv`
- panel SHA-256: V557 `839993f12eb3857e2b04dd31c7403d33ef7e9bb121b0838eab5218a31c50d0ec`,
  V558 `57cf230c84e777ab9536c1c61d1ecf7b9ba2cfd4675b05dcb8684dff796dc1fe`,
  V559 `c6d05b04b74fd637550c2c913c27a103d794b3394ad39953460d31e2272684e0`
- gate JSON SHA-256: V557 `b030643eb1a9367f50be3144baf5c7748646ddb675080df640a1970075b20b17`,
  V558 `c8009ce28e6102dcc7c532171ab7c5c6c72472b61b2e7e40c6a7965b3209049a`,
  V559 `5b962bd9b18b36ecaf3a614c63528f3d44d66ff95ca87f4f3d259293a4e611eb`
- compact SHA-256: V557 `281b99cb9bf7e99930a3a40f6fdee98e4427e9a6ef6b7314138ec22d777c4c3e`,
  V558 `d0735dc751e5818d62bea847a17db63b4de5b9d464afc41071e8af6cd671a350`,
  V559 `c9ae3d196fc5d2fe96ec15d8ce5e76a31e1893eea752539dd4f5c0c9edd7d2d6`
- builder/test SHA-256: `029dcf3dd8c36724bde00aced624e91f3639d97f7ec81735b081482f2b5194b1` /
  `54698f54c546b0f4cd3f180dc952c2e9cc7558d8f9d2e883fc789f74f6cbead8`
- exact V468 base/bridge SHA-256: `f3e6442270fa289247167e017be89b31563a7543312216e04a508b3d7f989b59` /
  `0178423a17af97c73ed2b1f7f8530bb0bb028bef16974d2f0aaaf078ce1bfc1e`
