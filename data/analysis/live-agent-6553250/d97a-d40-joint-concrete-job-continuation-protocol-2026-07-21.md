# D97a D40 joint concrete-job continuation — frozen protocol

Date: 2026-07-21  
Status: frozen before manifest generation, implementation, or outcome execution

## Question

D96 proves that adding per-worker state to four coarse semantic modes yields only `+0.797`
incremental oracle margin over the existing global-mode class and does not create mixed worker
batches broadly enough. D35 nevertheless shows that persistent concrete jobs cover more than 98%
of strong-bot unit turns and that distinct roles coexist in roughly 63% of multi-worker turns. Is
there broad causal value in choosing two workers' **concrete target-aware jobs together** at one
natural D40 batch boundary, beyond the best intervention on either worker alone?

This is a bounded one-batch continuation upper bound. It cannot fit a selector, select an arm,
train a policy, create a candidate, use platform data, call TestSession, submit, or change the
resident.

## Why this is a new discriminator

The experiment retains exact D40 as the complete trajectory anchor and changes at most two job
assignments in one batch. It is distinct from:

- D35b--D35d, which intervene on a private-farm trajectory at fixed turn roots;
- D36, which bounds repeated bundles over the resident;
- D41/D42, which change one exact-prior rank for one worker and then fit snapshot classifiers;
- D79, whose random scorer replaces every Rate decision;
- D82, which acts only at a threatened-own-crop trigger; and
- D96, which chooses only `balanced` / `harvest` / `renew` / `fell` without a concrete target.

No D96 random weight, oracle winner, scale, or task outcome enters D97.

## Frozen tasks and root manifest

Use new local official-map seeds `9,820,000--9,820,015`, both seats, and all eight unchanged D40
opponent modes: 256 tasks. These maps are development-only after this protocol and can never become
confirmation or candidate evidence.

Run exact D40 outcome-blindly. For each task retain the first decision satisfying all conditions:

1. the environment is in the ordinary Rate branch at a Worker decision;
2. at least one live own-provenance crop exists;
3. applying D40's exact teacher action reaches another Worker decision in the same referee turn
   and the ordinary Rate branch; and
4. at least 30 turns remain.

The root is the first worker decision; the immediately following decision is the second worker.
Record map, seat, opponent, decision ordinal, turn, worker ids/ordinals, complete candidate/action
hashes, teacher actions, state hash, live own crops, and the deterministic concrete option catalog.
Generate and freeze this manifest before any arm reaches terminal state. Manifest generation may
inspect only current candidates and the state produced by a first action; it may not inspect a
terminal score or choose roots/options from outcomes.

## Frozen concrete option catalog

At each of the two worker decisions, order candidates by D40's exact prior. Always include the D40
teacher as `keep`. From the remaining renewable-safe candidates retain the first candidate in each
available concrete class:

- `fell:{natural,own,opponent,ambiguous}`;
- `harvest:{natural,own,opponent,ambiguous}`;
- `renew:{natural,own,opponent,ambiguous}`; and
- `mine`.

The class is determined only from the frozen 44 candidate features: job one-hot, provenance
one-hot, and exact action/cell. Exclude a candidate that fells the final live own-provenance crop.
Deduplicate by exact action. Ties retain exact-prior order. No rank cap, learned score, geometric
threshold, opponent identity feature, resource value, terminal statistic, or post-result pruning
is permitted.

Enumerate the collision-safe Cartesian product sequentially. For every first-worker option,
reconstruct the exact root, apply that action, and construct the second-worker catalog from the
resulting live candidate set. D40 reservations and candidate legality therefore remove acquisition
and planting-cell collisions naturally. Retain only pairs whose second decision is still a Worker
Rate decision in the same turn.

Classify arms before outcomes:

- `control`: teacher first, then the resulting teacher second;
- `single_first`: nonteacher first, teacher second;
- `single_second`: teacher first, nonteacher second; and
- `joint`: nonteacher at both decisions.

Concrete action ids and target cells are part of the arm identity. There is no arm-count truncation.

## Frozen continuation

For every arm, replay exact D40 from game start to the root and require exact root identity. Apply
the two preregistered actions, then return permanently to exact D40 while both selected persistent
jobs execute through the ordinary transaction-safe executor. Record terminal scores, workers,
crops, job/failure counters, action/state hashes, both actions/classes/targets, selected job kinds,
owners, predicted deposits, and elapsed time.

Run the complete matrix twice with 20 workers, sorted by
`(map_seed, seat, opponent, root_id, first_option, second_option)`, and require byte identity.

## Frozen integrity and support gates

All must hold before value is opened:

1. complete task coverage and at least 220/256 eligible roots;
2. exact manifest reconstruction and two byte-identical complete matrices;
3. exactly one control arm per root, reproducing uninterrupted D40 on every terminal/action/state
   field;
4. every arm reproduces the root, first catalog, first action, resulting second catalog, and second
   action exactly;
5. zero duplicate arm keys, illegal actions, target/reservation collisions, final-own-crop fells,
   provenance failures, deposit-prediction failures, worker-cap violations, reward-identity
   failures, nonfinite values, or action-plane/accounting failures;
6. at least 5,000 joint arms and at least 1,000 single arms;
7. both seats and all eight opponent families have at least 24 roots each; and
8. at least 90% of roots expose both a fell and renewable (`harvest` or `renew`) alternative, at
   least 50% expose mine, and every provenance class observed in the catalog appears in both seats.

Any integrity failure quarantines value and authorizes only a defect repair under the unchanged
manifest and protocol.

## Frozen causal-value gates

At each root form three hindsight choices with tie order higher terminal margin, higher own score,
lower opponent score, fewer nonteacher actions, then lexical arm id:

- exact D40 control;
- the best `control` / `single_first` / `single_second` arm; and
- the best `joint` arm.

The joint representation passes only if all conditions hold:

1. the best safe joint-or-control oracle gains at least `+15` mean margin over D40 across all 256
   tasks, counting tasks without a root as zero;
2. it strictly improves at least 55% of eligible roots;
3. every opponent-family mean gain across all tasks is at least `+3`;
4. mean own-score delta is nonnegative and mean opponent-score delta is nonpositive;
5. crop creation is exactly 100% and worker-three reach is no more than five percentage points
   below D40;
6. over eligible roots, the best joint-or-control oracle is at least `+5` mean margin above the
   best single-or-control oracle;
7. a joint arm strictly beats the best single-or-control margin in at least 25% of eligible roots;
8. at least two distinct nonteacher role tuples are joint-oracle winners in at least ten roots
   each; and
9. joint-oracle winners use at least three job kinds, two provenance classes, both worker orders,
   and all eight opponent families.

Hindsight arms and catalogs are permanently unselectable. Descriptive favorable subsets, ranks,
targets, maps, or role tuples cannot weaken any gate.

## Decision rule

- **Full pass:** freeze the concrete joint-assignment executor and open a separate bounded
  whole-game function-class preflight with exact D40 fallback. Do not train yet.
- **Integrity failure:** repair only the defect and rerun the unchanged manifest/matrix.
- **Support failure:** close this concrete catalog without adding ranks, targets, thresholds, or
  root windows on the consumed bank.
- **Causal or incremental failure:** close two-worker concrete assignment over D40; move away from
  local job intervention rather than fitting another selector or learner.

No branch authorizes a candidate, fresh confirmation, TestSession, Arena, submission, or resident
replacement.
