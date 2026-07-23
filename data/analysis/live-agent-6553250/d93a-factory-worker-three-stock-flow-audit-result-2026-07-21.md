# D93a factory worker-three stock-flow audit — result

Date: 2026-07-21  
Verdict: direct worker-three intervention not authorized

## Integrity

The one-thread and 20-thread 512-row outputs are byte-identical, SHA-256
`76dc5f68f495ec091c3651d8ecdce0c24e3f4e42d1e65d28291dde8765508c93`.
All 140 fields shared with the original D89 discovery panel match in every row, including command
hash, terminal-state hash, scores, margins, plants, workforce, provenance, and factory telemetry.
The audit changed no game behavior.

## Availability result

| Profile | Balanced bill reached | Cheap bill reached | Balanced with carried stock | Balanced legal turns |
|---|---:|---:|---:|---:|
| Resident | 0 / 256 | 0 / 256 | 0 / 256 | 0 |
| D89 banana factory | 0 / 256 | 0 / 256 | 0 / 256 | 0 |

D89 fails every prewritten warrant for D93b. There is no first legal turn, no family coverage, and
no legal run. The result is stronger than “the chosen worker is expensive”: no trajectory can pay
even the diagnostic `(1,1,0,1)` bill, including currently carried resources.

Spawn occupancy is not the blocker. D89 records only 256 occupied-shack states across 74,138
two-worker turns—one transient turn per task, or 0.345%. The balanced bill's best simultaneous
deficit remains a mean 15.688 units and is reached at median turn 13, before the factory changes the
economy. Its best-state mean deficit vector is:

| Currency | Required | Mean best deficit | Tasks ever zero at their best state | Share of D89 two-worker turns deficient |
|---|---:|---:|---:|---:|
| PLUM | 6 | 4.625 | 0 / 256 | 100.0% |
| LEMON | 6 | 5.375 | 0 / 256 | 100.0% |
| APPLE | 2 | 0.125 | 224 / 256 | 13.0% |
| IRON | 6 | 5.562 | 0 / 256 | 100.0% |

Terminal D89 bank means are 1.375 PLUM, 0.621 LEMON, 5.441 APPLE, 0 BANANA, 0.438 IRON, and 92.777
WOOD. Forty-eight tasks end with the cheap PLUM component, 16 with cheap LEMON, 224 with cheap
APPLE, and **zero with cheap IRON**. These components are not simultaneously available.

## Interpretation

The apparent contradiction with strong multi-worker bots is resolved mechanistically. D89's
renewable economy is complete only for BANANA-to-WOOD score production. Training is a different
multi-currency production problem. The factory starter repeatedly harvests/replants BANANA, while
the trained role explicitly excludes `MINE`, `HARVEST`, `PICK`, and `PLANT`; neither role creates
the PLUM/LEMON/IRON stock needed for labor expansion. Strong bots support more workers because
their renewable policy jointly services the next TRAIN bill, not because additional workers are
intrinsically cheap.

## Verdict and next discriminator

Close direct third-worker addition on D89. Do not issue TRAIN, reduce the worker spec, or weaken the
availability gates.

The next eligible hypothesis is a bounded **bill-capitalization bridge** before worker three:
preserve the proven banana factory and wood role, but use otherwise productive decisions to acquire
the three permanently missing currencies. Before implementing it, compare the old D40--D68 bill
funding failures with D89's new stock flow and identify the smallest genuinely new action grammar;
the bridge must include IRON and cannot be another static species or threshold sweep.

## Artifacts

- `d93a-factory-worker-three-stock-flow-audit-protocol-2026-07-21.md`
- `d93a-factory-worker-three-audit-rows-a.tsv`
- `d93a-factory-worker-three-audit-rows-b.tsv`
- `rust/src/bin/ownership_aware_complete_economy.rs`

