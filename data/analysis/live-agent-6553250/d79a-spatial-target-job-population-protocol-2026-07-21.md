# D79a spatial target/job scorer population preflight — frozen protocol (2026-07-21)

## Question

D78 shows that current target condition and worker-to-crop geometry add transferable opponent-
commitment signal, while six-turn history adds almost no ranking value. Can a D40-anchored,
memoryless scorer over concrete legal jobs express broad, safe, outcome-sensitive whole policies?

D79a is a consumed-map representation preflight. It cannot select a random policy, fit on outcomes,
construct a candidate, open confirmation, call TestSession, submit, or touch Arena.

## Frozen policy interface

Keep exact D40 behavior for TRAIN, deficit funding, and shack evacuation. Keep its persistent job
executor, provenance, reservations, shared PICK ledger, and transaction revalidation unchanged.

Only at D40's ordinary `rate` branch, enumerate the same legal candidate jobs and exact-prior order.
For candidate `i`, form:

- D40's 44 candidate features;
- D42's 46 current shared-context features; and
- D42's 16 target/job spatial features, including target condition, worker/target distance,
  opponent distance/occupancy, water, and plant-cell geometry.

Use an eight-unit two-tower scorer:

`s = tanh(W_s shared + b_s)`

`j_i = tanh(W_j [candidate_i, job_context_i] + b_j)`

`residual_i = v dot (s * j_i) + q dot job_context_i + b`

`score_i = - exact_prior_rank_i / max(1, candidate_count - 1) + residual_i`.

Choose maximum score, breaking ties by exact-prior rank then action ID. The controller has 889
parameters: `8*46 + 8 + 8*60 + 8 + 8 + 16 + 1`. It has no recurrent state, opponent identity,
map seed, terminal feature, rollout, future command, handcrafted threat threshold, or D78 fitted
coefficient.

## Frozen population

Use NumPy PCG64 seed 7901. Write one all-zero anchor followed by 32 independent random policies.
For each random policy, draw and round to eight decimals:

- `W_s ~ Normal(0, 1/sqrt(46))`;
- `b_s ~ Normal(0, 0.10)`;
- `W_j ~ Normal(0, 1/sqrt(60))`;
- `b_j ~ Normal(0, 0.10)`;
- `v ~ Normal(0, 1/sqrt(8))`;
- `q ~ Normal(0, 0.25)`; and
- `b ~ Normal(0, 0.10)`.

No parameter, scale, policy, or seed may be changed after activity/outcome inspection.

## Frozen execution

Use consumed D40/D45 official maps 9,670,000--9,670,003, both seats, and the unchanged eight D40
opponents: 64 tasks per policy, 2,112 rows total. Run the complete matrix twice with 20 threads,
sort by `(policy, map_seed, seat, opponent)`, and require byte identity.

Record all D40 terminal/mechanics/action hashes and action planes plus rate decisions, overrides,
selected exact-prior rank sum/maximum, and selected targets with opponent distance at most two.
Reconstruct the population from seed and verify every serialized parameter exactly. The zero policy
must match the corresponding D40 reference rows on every common terminal/action/state field.

## Frozen gates

### Integrity and activity

All must hold:

1. complete byte-identical 33 x 64 matrices and exact population reconstruction;
2. zero invalid command, provenance, deposit-prediction, worker-cap, reward, nonfinite-feature, or
   illegal-selection failure;
3. zero-policy exact D40 parity on every task;
4. at least 24/32 random policies change action hash in 10%--90% of tasks;
5. at least 24/32 override the exact prior at least 128 times and use at least three distinct
   non-idle action planes; and
6. at least 24/32 make at least one selected target choice with current opponent distance <=2.

### Safety and outcome sensitivity

Require:

1. at least 24/32 random policies create a crop in at least 95% of tasks;
2. at least 24/32 retain worker three no more than ten percentage points below the zero anchor;
3. random-policy mean margins span at least 30 points; and
4. fixed-policy means occur both above and below the zero anchor.

### Representation headroom

For each task, select the highest-margin arm among zero and random policies that creates a crop and
has at least as many workers as `max(2, zero_workers - 1)`. This hindsight oracle is descriptive
representation headroom only. It passes when:

1. mean margin gain over zero is at least +20;
2. at least 50% of tasks improve strictly;
3. mean own-score delta is nonnegative or mean opponent-score delta is nonpositive; and
4. all eight opponent-family mean gains are positive.

## Decision rule

- **All gates pass:** freeze this interface and open D80, a preregistered actual-policy whole-game
  search on fresh maps. D79 random policies remain consumed and unselectable.
- **Integrity failure:** quarantine outcomes and repair only the defect before an unchanged repeat.
- **Activity failure:** close this scorer/initialization without changing scale or population.
- **Safety failure:** close unconstrained all-rate scoring; the only future variant may restrict
  choices structurally before seeing new outcomes.
- **Headroom failure:** close the spatial scorer representation; do not optimize it.

No D79 branch authorizes candidate construction or platform activity.
