# D94a factory existing-stock materialization audit — result

Date: 2026-07-21  
Verdict: pass; authorize one consumed-map D94b causal bridge

## Integrity

The one-thread and 20-thread outputs are byte-identical, SHA-256
`daf44fb1998bf6909e85b17a6e1f5fcded7b4c4f3b849f15151ed05de04bf94a`.
All 212 fields shared with D93a match in every one of 512 rows, including commands, terminal
states, scores, margins, provenance, workforce, and prior stock-flow telemetry. The audit changes
no behavior.

## Result

| Measure | Resident | D89 factory |
|---|---:|---:|
| Fruit bill materializable | 254 / 256 | 254 / 256 |
| Full bill already materializable | 0 / 256 | 0 / 256 |
| Best vector is IRON-only | 254 / 256 | 254 / 256 |
| Median first fruit window | turn 17 | turn 17 |
| Reached tasks with run >=2 | 251 / 254 | 254 / 254 |
| Median longest window | 42 turns | 256 turns |
| Mean minimum post-stock deficit | 5.578 | 5.578 |

Every opponent family has at least 31/32 reached D89 tasks. The two misses are the same map/seat
geometry represented by `compact_gold` and its behavior-identical `gold_elite` twin. All five
prewritten warrant gates pass.

At the best observed D89 state, PLUM and APPLE are sufficient in 256/256 tasks, LEMON in 254/256,
and IRON in 0/256. Mean maximum observable stock is 15.629 PLUM, 12.312 LEMON, 20.965 APPLE, and
0.438 IRON against costs 6/6/2/6. Thus existing ripe fruit is broadly sufficient in principle;
unmined IRON is the only universal missing coordinate.

## Interpretation

This result sharply narrows the old D55--D68 closure. A new deposited-seed source portfolio is not
needed on these maps. The board already exposes the required fruit early, and D89's long-lived
banana economy keeps the acquisition horizon open. The missing action grammar is concurrent
materialization: the harvest-capable starter must win and bank existing fruit while the trained
chopper mines IRON.

The audit is intentionally optimistic because it counts all ripe board fruit, including contested
fruit. It proves availability, not collectability or value. D94b must test both causally.

## Next experiment

Authorize one disabled-by-default consumed-map bridge:

1. preserve the exact resident opening and complete D89 bank-BANANA bootstrap;
2. while exactly two workers remain, the starter banks existing ripe PLUM/LEMON/APPLE against the
   exact `(2,2,0,2)` bill and the trained worker mines/banks IRON;
3. issue TRAIN only from deposited affordability and a clear shack;
4. return immediately to unchanged banana-factory roles after worker three appears; and
5. never create a non-BANANA source or tune species counts, turn thresholds, or the worker spec.

Fresh maps remain sealed until this bridge passes separate mechanism and value gates.

