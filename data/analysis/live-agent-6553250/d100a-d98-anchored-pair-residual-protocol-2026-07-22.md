# D100a D98-anchored pair residual — frozen protocol

Date: 2026-07-22  
Status: frozen before population generation, implementation, reference execution, or outcomes

## Question

D99 proves that explicit pair actions fix joint/job/provenance activity, but replacing D98's
independent score surface loses `17.133` same-task oracle margin and reduces repeated-use increment
to `+2.672`. Does one bounded pair-interaction residual add at least five points to an exact frozen
D98 parent bank when the parent behavior remains an explicit member of the function class?

D100 is a deterministic function-class upper bound. No parent, residual, oracle winner, fixed rank,
or favorable subset is selectable. It cannot fit a model, tune scale or budget, construct a
candidate, call TestSession, inspect Arena, submit, or change the resident.

## Exact D98 parent

Use the 64 frozen D98 weight vectors from `four_00--four_63`, each with D98's exact 153 features,
catalog, positive-score rule, first-two-Rate-worker positions, and four intervention-batch budget.
Retain `CompleteMacroEnv` and D40 unchanged for all other behavior.

For each parent create three rows:

- `parent_XX`: exact D98 independent behavior;
- `zero_XX`: the same parent plus 342 exact-zero pair-residual weights; and
- `random_XX`: the same parent plus one frozen random 342-weight pair residual.

Add `d40_control`. There are exactly 193 policies. Every `parent_XX` must reproduce the frozen
pre-change D98 binary on every terminal, action-plane, action-hash, and state-hash field. Every
`zero_XX` must reproduce its `parent_XX` on those fields.

## Residual pair override

Each zero/random residual may use at most one pair override per episode. At the first ordinary Rate
worker of an otherwise D98-eligible batch, reconstruct the exact D98 parent first choice. Apply it
to a same-turn branch and reconstruct the exact D98 parent second choice with updated reservations,
budget, state, and second-position features. This ordered choice is the parent pair.

Enumerate D99's complete collision-safe pair catalog from the same root: D40 keep plus the first
renewable-safe exact-prior candidate in every available `fell` / `harvest` / `renew` x provenance
class and `mine`, with each first option applied before rebuilding its second catalog. If the exact
parent first action does not expose a second same-turn Rate worker, skip residual scoring and
continue exact sequential D98. No nonteacher action may fell the final live own crop.

Embed every pair—including the parent and `keep/keep`—with D99's exact 342 features. Control has
zeros only in the three-value pair-kind block; its real teacher candidate/context fields remain.
For each alternative, subtract the parent-pair embedding. The parent residual score is fixed zero;
an alternative score is one dot product between the 342 residual weights and that difference.
Choose the highest strictly positive alternative, with nested exact-prior order for ties. If no
alternative is positive, execute the exact parent pair. Applying an alternative consumes the sole
residual override, even if it contains only keep actions; actual nonkeep work continues to consume
the shared four-batch D98 intervention budget.

After a committed pair, validate the real second state, worker, observation, catalog, and action
against its preview. All later decisions use the same D98 parent on the realized state. The
controller cannot cancel or replace persistent jobs.

The 342 pair embedding is exactly:

1. 56 D61 Train-boundary features with balanced-control slots 44--51;
2. first 46 shared + 44 candidate features;
3. second 46 shared + 44 candidate features;
4. two stable three-value ordinal one-hots;
5. three `single_first/single_second/joint` values, all zero for control;
6. ordered 25-value job-pair and 25-value provenance-pair one-hots;
7. remaining actual intervention budget / four and two normalized exact-prior ranks; and
8. 44 elementwise first/second candidate products.

No opponent identity, seed, nickname, terminal value, D97--D99 winner, rollout, recurrent state, or
fitted threshold is available.

## Frozen population

Read the 64 exact D98 parent vectors without modification. Use NumPy PCG64 seed 10001 to draw 64
residual vectors of 342 values from `Normal(0, 0.25)` in C order and round to eight decimals. Pair
residual vector `XX` only with D98 parent `XX`. Do not center, normalize, reject, reorder, or inspect
a vector. `zero_XX` uses exact zeros.

## Frozen execution

Use new local official-map seeds `9,823,000--9,823,007`, both seats, and all eight unchanged D40
opponents: 128 tasks per policy and 24,704 rows. These maps become consumed development data.

Run D100 twice with 20 workers, sort by `(policy, map_seed, seat, opponent)`, and require byte
identity. Record D40 terminal/mechanics/action-plane fields, D98 scoring/budget fields, pair catalog
support, residual evaluations/overrides/joint overrides, preview validations, override-only job and
provenance counts, and deterministic parent/residual/pair hashes.

Run the already-frozen pre-change D98 release binary exactly once on the same 128 tasks. It is a
parity reference only and cannot alter any D100 artifact or gate.

## Frozen integrity gates

All must hold:

1. two complete 193 x 128 D100 matrices are byte-identical;
2. `d40_control` reproduces independent D40 exactly;
3. all 64 parents reproduce their same-index D98 reference rows exactly;
4. all 64 zero residuals reproduce their same-index parents exactly;
5. the population reconstructs exactly from D98 plus PCG64 seed 10001;
6. no policy exceeds four actual intervention batches, one residual override, or two committed pair
   actions, and all batch/pair/job/provenance accounting balances;
7. every committed second action matches its preview state, worker, observation, catalog, and legal
   action; and
8. zero illegal commands, reservation/target collisions, final-own-crop fells, provenance,
   deposit-prediction, worker-cap, reward, nonfinite-feature, catalog, hash, or action-plane failures
   occur.

Any integrity failure quarantines value and permits only defect repair under unchanged artifacts.

## Frozen safety and activity gates

Require:

1. every policy creates at least one own crop in every task;
2. at least 56/64 random residual policies retain worker-three reach no more than ten percentage
   points below their exact parent;
3. at least 56/64 random residuals change action hash from their parent in at least 25% of tasks;
4. at least 48/64 random residuals execute an override in at least 25% of tasks;
5. at least 32/64 random residuals execute a joint override in at least 10% of tasks;
6. at least 48/64 random residuals use at least three override job kinds and two override provenance
   classes globally; and
7. random fixed paired mean-margin deltas versus their parents span at least 20 points.

## Frozen incremental headroom gates

For each task construct:

- the **parent oracle** from D40 plus all 64 `parent_XX` rows; and
- the **strict-superset oracle** from D40, all parents, and all 64 `random_XX` rows.

Tie order is higher margin, higher own score, lower opponent score, fewer actual intervention
batches, fewer residual overrides, then lexical policy. The representation passes only if all hold:

1. strict-superset mean margin is at least `+5` above the parent oracle;
2. a random residual strictly beats the parent-oracle margin in at least 24/128 tasks;
3. at least twelve random residual policies are strict superset winners in at least two tasks;
4. strict-superset mean margin gain over D40 is at least `+55`;
5. every opponent-family strict-superset mean gain over D40 is at least `+15`;
6. strict-superset mean own-score delta versus D40 is nonnegative and opponent-score delta is
   nonpositive;
7. strict-superset worker-three reach is at least 85% and crop creation is exactly 100%; and
8. selected random-residual rows contain an executed override in at least 24 tasks, a joint override
   in at least 16 tasks, and span all four override jobs, two provenances, both seats, and all eight
   opponent families.

## Decision rule

- **Full pass:** freeze the anchored residual environment and open one short residual-selector
  mechanics/learning-signal preflight initialized at exact parent behavior. No checkpoint is a
  candidate.
- **Integrity failure:** repair only the defect and repeat unchanged rows.
- **Safety/activity failure:** close this residual initialization without tuning scale, budget,
  catalog, features, or thresholds on consumed maps.
- **Incremental failure:** close pair residuals on the D98 surface and switch representation; do not
  train PPO, CEM, imitation, or a larger pair residual.

No branch authorizes confirmation, candidate construction, TestSession, Arena, submission, or
resident replacement.
