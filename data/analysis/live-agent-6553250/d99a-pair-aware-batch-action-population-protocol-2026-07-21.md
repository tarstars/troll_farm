# D99a pair-aware batch-action population — frozen protocol

Date: 2026-07-21  
Status: frozen before population generation, implementation, reference execution, or outcome execution

## Question

D97 proves terminal interaction between two concrete assignments. D98 preserves safety and repeated
headroom, but its independent worker scorer collapses onto stable single-class preferences: only
23/64 policies create joint batches broadly, its four-use oracle selects joint work in only 12/128
tasks, and it misses the whole-game gain floor. Does scoring one collision-safe ordered pair as a
single batch action expose broader joint activity and at least five points of fresh-map oracle value
beyond the frozen D98 interface?

D99 is a deterministic random-function-class upper bound. It cannot select a random policy, fit a
model, tune a scale, construct a candidate, call TestSession, submit, inspect Arena, or change the
resident.

## Exact substrate and pair action

Retain `CompleteMacroEnv` and exact D40 unchanged for TRAIN, positive-deficit funding, shack
evacuation, persistent jobs, provenance, reservations, shared PICK accounting, transaction
revalidation, and every uncommitted decision.

At each Train boundary begin a new assignment batch. At the first ordinary Rate worker, a policy
may enumerate a pair only when:

- a live own-provenance crop exists;
- at least 30 turns remain;
- its intervention-batch budget remains; and
- applying D40's first worker action exposes a second same-turn ordinary Rate worker.

Build D98's exact first-worker catalog: D40 `keep` plus the first renewable-safe exact-prior
candidate in every available `fell` / `harvest` / `renew` x provenance class and `mine`. For each
first option, create a same-turn branch, apply that option, and rebuild the second-worker catalog
from the resulting state and active-job reservations. Enumerate every resulting ordered pair.
There must be exactly one `keep/keep` control. Pairs classify as `single_first`, `single_second`, or
`joint`; no nonteacher action may fell the final live own crop.

Score the full pair before changing the real environment. Apply the committed first action, require
the real second state, worker, observation, catalog, and action to match the preview, then apply the
committed second action. Later workers and every other branch take exact D40. A selected noncontrol
pair consumes one batch budget; a joint pair contains two nonkeep assignments. The controller
cannot cancel or replace persistent jobs.

## Frozen pair features and scorer

For each noncontrol ordered pair concatenate exactly 342 finite features:

1. D61's 56 Train-boundary features, using its exact balanced-control convention for slots 44--51;
2. the first worker's 46 D42 shared features and 44 exact candidate features;
3. the post-first branch's second worker 46 shared features and 44 exact candidate features;
4. two stable three-value worker-ordinal one-hots;
5. a three-value `single_first` / `single_second` / `joint` one-hot;
6. a 25-value ordered job-pair one-hot over `keep/fell/harvest/renew/mine`;
7. a 25-value ordered provenance-pair one-hot over
   `none/natural/own/opponent/ambiguous`, where keep and mine use `none`;
8. remaining intervention budget divided by four;
9. the first and second exact-prior ranks, each divided by that observation's full candidate count;
10. 44 elementwise products of the first and second exact candidate feature vectors.

The pair score is one linear dot product. `keep/keep` has fixed score zero. Choose the highest
strictly positive noncontrol pair; ties use nested exact-prior catalog order. If no pair is positive,
choose `keep/keep`. Zero weights therefore reproduce D40 exactly. No opponent identity, seed,
nickname, future action beyond the same-turn committed second assignment, terminal value, D97/D98
winner, rollout, recurrent state, or fitted threshold is available.

## Frozen matched population

Use NumPy PCG64 seed 9901. Draw 64 vectors of 342 weights from `Normal(0, 0.25)` in C order and
round to eight decimals. Do not center, normalize, reject, or inspect a vector.

For each vector create two policies with identical weights:

- `one_XX`: at most one noncontrol pair batch per episode; and
- `four_XX`: at most four noncontrol pair batches per episode.

Add `zero_control` with 342 exact zero weights and budget four. There are exactly 129 policies.
Random fixed policies are descriptive and permanently unselectable.

## Frozen execution and D98 reference

Use new local official-map seeds `9,822,000--9,822,007`, both seats, and all eight unchanged D40
opponents: 128 tasks per policy and 16,512 pair-policy rows. These maps become consumed development
data.

Run the D99 matrix twice with 20 workers, sort by `(policy, map_seed, seat, opponent)`, and require
byte identity. Record all D40 terminal/mechanics/action-plane fields plus eligible pair batches,
pair-option counts, selected pair types, intervention/nonkeep/joint counts, job/provenance counts,
safety rejections, preview validations, and deterministic catalog/policy hashes.

Also run the already-frozen D98 population and pre-change release binary exactly once on the same
tasks with 20 workers. This is a nonselectable architectural reference only. Its zero row must match
the independent D99 D40 baseline exactly. D98 policy outcomes may not alter the D99 population,
features, implementation, thresholds, or gates.

## Frozen integrity gates

All must hold:

1. two complete 129 x 128 D99 matrices are byte-identical;
2. D99 `zero_control` reproduces independent D40 on every terminal, action-plane, action-hash, and
   state-hash field;
3. the population reconstructs exactly from PCG64 seed 9901;
4. one/four pairs have identical weights and exact budgets one/four;
5. no policy exceeds its batch budget, commits more than two actions in a pair, or has pair/job/
   provenance accounting disagreement;
6. every committed second action exactly matches its preview state, worker, observation, catalog,
   and legal action; and
7. zero illegal commands, reservation/target collisions, final-own-crop fells, provenance,
   deposit-prediction, worker-cap, reward, nonfinite-feature, catalog, hash, or action-plane failures
   occur.

Any integrity failure quarantines value and permits only a defect repair under the unchanged
population and maps.

## Frozen safety and activity gates

Require:

1. every policy creates at least one own crop in every task;
2. at least 56/64 four-budget policies retain worker-three reach no more than ten percentage points
   below D40;
3. at least 56/64 matched pairs have both budget variants change action hash from D40 in at least
   50% of tasks;
4. at least 48/64 four-budget policies use at least three concrete job kinds and two provenance
   classes globally;
5. at least 48/64 four-budget policies execute at least two intervention batches in at least 25%
   of tasks;
6. at least 48/64 four-budget policies create a joint pair in at least 25% of tasks; and
7. four-budget fixed-policy mean margins span at least 25 points.

## Frozen whole-game headroom gates

For each task construct D99 one- and four-use hindsight oracles from D40 plus the corresponding 64
random policies. Construct the D98 four-use reference oracle from D40 plus its frozen 64 four-use
policies. All tie orders are higher margin, higher own score, lower opponent score, fewer
intervention batches, then lexical policy.

The representation passes only if all hold:

1. D99 four-oracle mean margin gain over D40 is at least `+50`;
2. D99 four oracle strictly improves D40 in at least 85% of tasks;
3. every opponent-family D99 four-oracle mean gain is at least `+15`;
4. D99 four-oracle mean own-score delta is nonnegative and opponent-score delta is nonpositive;
5. D99 four-oracle worker-three reach is at least 85% and crop creation is exactly 100%;
6. D99 four-oracle mean margin is at least `+10` above the D99 one oracle;
7. D99 four policies strictly beat the D99 one-oracle row in at least 32/128 tasks;
8. at least twelve D99 `four_XX` policies are strict four-oracle winners in at least two tasks;
9. selected D99 four-oracle rows use at least two intervention batches in at least 24 tasks, contain
   a joint pair in at least 32 tasks, and span all four jobs, two provenances, both seats, and all
   eight opponent families; and
10. the D99 four oracle exceeds the same-task frozen D98 four oracle by at least `+5` mean margin.

No fixed random rank, pair, class, target, favorable subset, or hindsight choice is selectable.

## Decision rule

- **Full pass:** freeze the pair-action environment and open one short mechanics/learning-signal
  preflight initialized at exact D40. No value checkpoint is yet a candidate.
- **Integrity failure:** repair only the defect and repeat the unchanged matrix.
- **Safety/activity failure:** close this random pair initialization without changing scale, budget,
  catalog, or gate on consumed maps.
- **Headroom or D98-increment failure:** close pair-aware whole-game use; do not train PPO, CEM,
  imitation, or a larger scorer on it.

No branch authorizes fresh confirmation, candidate construction, TestSession, Arena, submission,
or resident replacement.
