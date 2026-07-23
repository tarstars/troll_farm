# D38 TRAIN-deficit complete-macro teacher — frozen protocol (2026-07-21)

## Question

D37 validates a deterministic complete persistent-job environment but rejects its behavior teacher:
the starter repeatedly converts its one harvested seed into a new crop and therefore fails to bank
the exact currency requested by TRAIN. D38 asks whether the existing action interface can support
workforce growth when the teacher values jobs by **mechanical reduction of the pending TRAIN bill**
rather than a scalar production-rate bonus.

D38 is a fresh initializer preflight. It cannot train a network, build a candidate, open D37's
development/confirmation blocks, invoke TestSession, submit, or act in Arena.

## Pre-data scheduler integrity amendment

The first attempted random-control execution exposed a deterministic zero-time loop at seed
9,630,006, seat 1, opponent `gold_adaptive`, turn 300. When any active job completed, D37 discarded
the other jobs' commands for that boundary but accidentally retained command-side mutations such
as `idle_issued` or `plant_issued`. Two workers could therefore alternate phantom completion
without advancing the referee. The attempted control produced no artifact; the two concurrent
teacher files were invalidated before analysis.

Before generating accepted D38 rows, command construction was made transactional: if a completion
causes a zero-time boundary, every nonfinished job is restored to its pre-command state. The exact
failing random episode is now a regression test with the frozen 16-decision zero-time ceiling.
This correction changes historical D37 executor hashes, so D38 retains D37's intended game/action
interface rather than reproducing the discovered mutation defect. Every teacher and control row
below must be regenerated from the corrected executor.

## Frozen environment

Retain D37's exact official engine, both seats, eight opponents, asynchronous free-worker
assignment, three-worker cap, provenance, reservations, persistent executor, action planes, and
complete-policy boundary. No D37 value result changes any game rule, job target quota, or terminal
objective.

Extend each legal job record with a deterministic predicted deposit vector:

- `BANK`: the worker's complete current carry;
- `FELL_BANK`: current carry plus the wood that fits at selection time;
- `HARVEST_BANK`: current carry plus the fruit that fits and can be harvested now;
- `RENEW`: current carry plus harvested fruit minus exactly one seed spent on the planned crop;
- `MINE_BANK`: current carry plus the exact yield of one `MINE`,
  `min(chop_power, free_capacity)` iron; and
- `IDLE_ONE_TURN`: zero.

The vector is a mechanics feature, not a terminal-value estimate. Prediction/replay equality is
checked only when a job completes normally; opponent invalidation remains separately counted.

## Frozen deficit teacher

The global goal is producer `(2,2,1,1)` while fewer than two workers exist, then chopper
`(2,2,0,2)` while fewer than three exist, then `NO_TRAIN`. Use the exact referee
`training_cost(current_worker_count, goal)` and current inventory.

At each free-worker decision:

1. subtract current inventory and deposits already reserved by active jobs from the TRAIN cost,
   clipping every item at zero;
2. for every legal candidate, compute the integer sum across items of
   `min(outstanding_deficit[item], predicted_deposit[item])`;
3. if any candidate has positive reduction, choose maximum reduction, then smaller predicted ETA,
   then `BANK` before acquisition on an exact tie, then stable role/target/plant-cell key;
4. if active reserved deposits already cover the bill but it is not yet affordable, select
   `IDLE_ONE_TURN` so free workers do not spend the reserved currency;
5. if no legal job can reduce an uncovered bill because the required source is temporarily
   unavailable, select `IDLE_ONE_TURN`; and
6. once the bill is affordable or worker three exists, use the unchanged D37
   rate/provenance ordering.

No learned/outcome coefficient, crop bonus, opponent-family rule, turn threshold, or observed D37
score enters this ordering. In particular, a one-seed `RENEW` has zero funding value while the
paired `HARVEST_BANK` has one.

## Fresh preflight

Use official seeds **9,630,000--9,630,015**, both seats, all eight opponents. Run the deficit
teacher twice and random legal once. Require the same row/integrity checks as D37 plus exact action
and state hashes, predicted-deposit accounting, and zero decision loops.

The teacher passes only if all hold:

1. independent teacher rows are byte-identical and both controls have complete clean 256-cell
   grids;
2. mean paired margin advantage over random is at least +50;
3. worker two is trained in at least 80% and worker three in at least 15%;
4. an own renewable crop is created in at least 60%;
5. median selected non-idle jobs is at least four; and
6. at least six opponent-family mean margin advantages over random are nonnegative, with no family
   below -10.

A pass freezes the observation schema and opens a new behavior dataset/clone under a separate D38
learning protocol. A failure closes deficit-only teacher initialization. Diagnose whether the miss
is source availability, deposit prediction, asynchronous reservation, or post-training scheduling;
do not tune the ordering on these seeds.

## Compute and artifacts

Run locally with 24 Rust workers. Preserve two teacher TSVs, one random TSV, analyzer JSON, focused
Rust/Python tests, hashes, and a written verdict. YT remains irrelevant until a behavior initializer
passes and a neural workload is actually authorized.
