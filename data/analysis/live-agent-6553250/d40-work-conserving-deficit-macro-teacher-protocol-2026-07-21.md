# D40 work-conserving deficit macro teacher — frozen protocol (2026-07-21)

## Question

D39 validates spawn evacuation and nearly clears its initializer gate, but its two-worker episodes
still average 218.59 idle selections and -165.77 margin. D40 asks whether exact TRAIN funding can
remain lexicographically first while otherwise keeping every free worker productive.

D40 is a fresh behavior-initializer preflight. It cannot train a network, construct a candidate,
invoke TestSession, submit, or act in Arena.

## Frozen teacher

Retain D39's corrected transactional environment, TRAIN-relevant prediction equality, global
producer/chopper goals, exact deficit vector, active-job reservations, shack evacuation,
provenance, persistent executors, and post-worker-three rate ordering.

At every worker decision while a TRAIN goal remains active:

1. if a candidate has positive exact deficit reduction, use D38's frozen reduction/ETA/bank/stable
   ordering;
2. otherwise, if the current worker occupies the shack, use D39's frozen shortest non-idle
   evacuation ordering; and
3. otherwise use D37's already-frozen rate/provenance ordering instead of `IDLE_ONE_TURN`.

This is lexicographic composition, not a new weighted score: immediate funding always dominates
production, while the fallback acts only when no legal job can presently reduce the reserved bill.
No coefficient, role bonus, opponent branch, map identity, or observed D39 outcome is changed.

## Fresh experiment

Use official seeds **9,670,000--9,670,015**, both seats, all eight opponents. Generate:

- work-conserving teacher A and independent repeat B;
- a same-seed D39 evacuation-only ablation; and
- a same-seed random-legal control.

All four arms use the identical corrected environment and TRAIN-relevant prediction telemetry.
Run locally across the available 20 CPUs and preserve TSVs, analyzer JSON, focused tests, hashes,
and written verdict.

The teacher passes only if all hold:

1. all four 256-cell grids are complete and clean, including zero decision loops and zero
   TRAIN-relevant prediction failures;
2. teacher A/B are byte-identical;
3. mean paired margin advantage is at least +50 versus random and at least +20 versus D39;
4. worker two is trained in at least 90%;
5. worker three is trained in at least 50% and at least 15 percentage points more often than D39;
6. total idle selections are at most half the D39 total;
7. an own renewable crop appears in at least 60% and median non-idle jobs is at least four; and
8. at least six opponent-family mean margin advantages versus random are nonnegative, with no
   family below -10.

A pass freezes the complete initializer and opens a separate behavior-cloning/PPO protocol. A
failure closes this lexicographic teacher and must distinguish failure to complete worker-three
funding from weak post-training role allocation. No gate or ordering may be tuned on these seeds.
