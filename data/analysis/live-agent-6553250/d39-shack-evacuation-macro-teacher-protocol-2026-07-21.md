# D39 shack-evacuation TRAIN-deficit macro teacher — frozen protocol (2026-07-21)

## Question

D38's worker-two rate is exactly split by a physical prerequisite that its resource deficit omits:
the initial/new worker occupies the shack, and the referee rejects TRAIN until that worker moves.
D39 asks whether a coefficient-free evacuation rule can turn the validated complete macro action
interface into a viable closed-loop behavior initializer.

D39 is a fresh preflight. It cannot train a model, construct a submission candidate, invoke
TestSession, submit, or act in Arena.

## Frozen environment corrections

Retain the corrected transactional D38 scheduler, exact official referee, both seats, all eight
opponents, persistent jobs, provenance, reservations, three-worker cap, reward decomposition, and
the existing nine action planes. Do not add an evacuation action or a fallback controller.

The D38 full-vector deposit-equality gate is replaced by a TRAIN-relevant equality gate over only
PLUM, LEMON, APPLE, and IRON. These are the only nonzero `training_cost` slots. BANANA and WOOD may
remain useful observation features but are neither reserved against TRAIN nor asserted exact:
persistent felling proved that future wood is changed by plant growth and competing chops.

## Frozen evacuation teacher

Use D38's producer-then-chopper global TRAIN goals and exact outstanding-resource deficit. At each
free-worker decision:

1. if the current free worker occupies our shack and a TRAIN goal is active, first use D38's exact
   positive deficit-reduction ordering when such a candidate exists;
2. otherwise, while that worker still blocks the shack, choose the shortest legal non-idle job,
   then stable role/target/plant-cell order; every acquisition target is off-shack, so its first
   executor command must evacuate the spawn cell;
3. for a worker not occupying the shack, use D38's unchanged deficit/reservation ordering; and
4. after worker three exists or no TRAIN goal is active, use D37's unchanged rate/provenance
   ordering.

No score coefficient, opponent-family branch, outcome label, map identity, or turn threshold is
introduced. The evacuation rule changes only the distinction between resource coverage and
physical TRAIN legality.

## Fresh experiment

Use official seeds **9,650,000--9,650,015**, both seats, all eight opponents. Generate:

- evacuation teacher A and independent byte-identical repeat B;
- a same-seed D38 deficit-only ablation; and
- a same-seed random-legal control.

All arms use the same corrected executor and TRAIN-relevant prediction telemetry. Run locally with
the available 20 CPUs. Preserve the four TSVs, analyzer JSON, focused tests, hashes, and verdict.

The evacuation teacher passes only if all hold:

1. all four 256-cell grids are complete and clean, including zero TRAIN-relevant deposit
   prediction failures and zero decision loops;
2. teacher A/B are byte-identical;
3. mean paired margin advantage is at least +50 versus random and at least +50 versus the D38
   deficit-only ablation;
4. worker two is trained in at least 90%, at least 40 percentage points above the ablation;
5. worker three is trained in at least 15%;
6. an own renewable crop appears in at least 60%;
7. median selected non-idle jobs is at least four; and
8. at least six opponent-family mean margin advantages versus random are nonnegative, with no
   family below -10.

A pass freezes the observation/action schema and opens a separate behavior-learning protocol. A
failure closes the evacuation-plus-deficit teacher and must distinguish remaining resource/supply
stalling from post-training production weakness. No gate may be tuned on these seeds.
