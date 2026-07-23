# Complete-economy supply ownership diagnostic — result, 2026-07-19

## Verdict

**Close private placement as the primary complete-economy fix.**  The adaptive-Gold counter is not
stealing the top farm controller's trees.  It builds and converts its own renewable loop after the
farm policy stops contesting that loop.

The diagnostic used the frozen 30 discovery seeds, both seats, adaptive Gold only: 60 resident and
60 `lean_m2c2h0k2` games.  It exactly reproduces the earlier aggregate counterexample: farm versus
resident is +187.68 own score, +235.62 opponent score, -47.93 margin, +46.45 own inventory wood,
and +59.97 opponent inventory wood per game.

## Provenance decomposition

| Opponent chop wood over 60 games | Resident | Farm | Change | Share of added wood |
|---|---:|---:|---:|---:|
| Natural trees | 666 | 767 | +101 | 2.81% |
| Trees we planted | 113 | 153 | +40 | **1.11%** |
| Trees opponent planted | 1,254 | 4,703 | **+3,449** | **95.83%** |
| Unknown provenance | 0 | 9 | +9 | 0.25% |
| **Total** | **2,033** | **5,632** | **+3,599** | **100%** |

In the farm games, our planted trees yielded 5,208 wood to us and only 153 to adaptive Gold.  Its
capture share of our farm supply is therefore **2.85%**, far below the frozen 20% direct-capture
threshold.  The farm-induced opponent-wood share from our crops is 1.11%, far below the frozen 50%
threshold.

## Integrity and conservative bound

- the common grid is exact and all 120 games finish normally;
- 16,285/16,299 positive CHOP wood units have known provenance (99.91% overall; 99.88% farm,
  100% resident), clearing the 95% requirement;
- seven plant births were multiply claimed in simultaneous actions, so the deliberately strict
  zero-ambiguity integrity check fails; those births produce only 14 unknown wood units.

Even assigning every unknown opponent wood unit to our farm increases the direct component only
from 40 to 49 of 3,599 added units (1.36%), and the rival capture share remains around 3%.  The
ambiguity cannot approach either causal threshold, so it does not change the branch decision.

## Mechanism

The farm controller plants 50.78 trees/game and keeps nearly all their wood.  Adaptive Gold rises
from 17.00 to 46.45 successful plants/game and converts its own crops.  Simultaneously, our capture
of opponent-created wood falls from 498 to 131 total while opponent self-capture rises from 1,254
to 4,703.  The resident's low-output policy was winning partly by contesting opponent renewable
supply; the farm policy replaces that denial with an efficient private loop but leaves the rival
loop intact.

## Next hypothesis

The next complete-controller representation should combine:

1. the top farm's private near-shack production loop;
2. explicit provenance for opponent-created crops; and
3. opponent-relative liquidation that diverts a chopper only when denied rival conversion exceeds
   the opportunity cost of the next private-farm target.

This is not a farm-radius sweep and not a worker-count retune.  The first discriminator must be a
closed-loop ownership-aware controller against adaptive Gold and the other seven families on new
seeds, with separate accounting for private production preserved and opponent self-crop wood
suppressed.
