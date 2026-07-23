# D98a bounded whole-game joint-assignment population — frozen protocol

Date: 2026-07-21  
Status: frozen before population generation, implementation, or outcome execution

## Question

D97 proves that one collision-safe concrete two-worker assignment gains `+36.852` margin over D40
and adds `+9.208` beyond the best single-worker intervention. Can the same target-aware interface
operate repeatedly as a bounded complete policy, preserving exact D40 outside a few natural
assignment batches and adding headroom beyond one intervention?

D98 is a deterministic random-function-class upper bound. It cannot select a random policy, fit a
model, tune a scale, construct a candidate, call TestSession, submit, inspect Arena, or change the
resident.

## Exact substrate and authority boundary

Retain `CompleteMacroEnv` and exact D40 unchanged for TRAIN, positive-deficit funding, shack
evacuation, persistent execution, provenance, reservations, shared PICK accounting, transaction
revalidation, and every noneligible worker decision.

At each Train boundary start a new assignment batch. A policy may score only the first two ordinary
Rate worker decisions in that batch, and only when:

- a live own-provenance crop exists;
- at least 30 turns remain; and
- the policy has remaining intervention-batch budget.

At each scored worker, reconstruct D97's exact catalog: D40 `keep` plus the first renewable-safe
exact-prior candidate in each available `fell` / `harvest` / `renew` x provenance class and
`mine`. Applying the first action updates active jobs and reservations before the second catalog is
built. No nonteacher action may fell the final live own crop. Later workers and every other branch
take exact D40.

A batch consumes one unit of budget if either scored worker chooses nonkeep. A batch with two
nonkeep choices is a joint intervention. The controller cannot cancel or replace persistent jobs.

## Frozen scorer and features

For each nonkeep catalog option concatenate exactly 153 finite features:

1. D61's 56 batch features captured at the current Train boundary;
2. D42's 46 shared worker/context features at the live worker decision;
3. the option's 44 exact candidate features;
4. a three-value stable worker-ordinal one-hot;
5. a two-value first/second scored-position one-hot;
6. remaining intervention budget divided by four; and
7. exact-prior rank divided by the current candidate count.

For D61 feature slots 44--51, which encode the previous global semantic mode and cumulative
semantic-mode batch counts, use D61's exact balanced-control convention for every D98 policy:
`balanced` is the previous mode after the first batch and every completed Train boundary increments
only the balanced count. These values are policy-independent bookkeeping, not inferred concrete-job
labels. This makes the phrase “D61's 56 batch features” bit-exact and keeps zero-control parity
well-defined.

The alternative score is one linear dot product. `keep` has fixed score zero. Choose the highest
strictly positive alternative; ties use catalog order. If no alternative is positive, choose
`keep`. Zero weights therefore reproduce D40 exactly. No opponent identity, seed, nickname,
future action, terminal value, D97 arm/winner/target, outcome label, rollout, recurrent state, or
fitted threshold is available.

## Frozen matched population

Use NumPy PCG64 seed 9801. Draw 64 vectors of 153 weights from `Normal(0, 0.25)` in C order and
round to eight decimals. Do not center, normalize, reject, or inspect a vector.

For each vector create two policies with identical weights:

- `one_XX`: at most one intervention batch per episode; and
- `four_XX`: at most four intervention batches per episode.

Add `zero_control` with 153 exact zero weights and budget four. There are exactly 129 policies.
Random fixed policies are descriptive and permanently unselectable.

## Frozen execution

Use new local official-map seeds `9,821,000--9,821,007`, both seats, and all eight unchanged D40
opponents: 128 tasks per policy and 16,512 rows. These maps become consumed development data.

Run the matrix twice with 20 workers, sort by `(policy, map_seed, seat, opponent)`, and require byte
identity. Record all D40 terminal/mechanics/action-plane fields plus eligible/scored/intervention
batches, nonkeep assignments, joint batches, budget use, option-class/owner/job counts, catalog
sizes, safety rejections, and deterministic policy/option hashes.

## Frozen integrity gates

All must hold:

1. two complete 129 x 128 matrices are byte-identical;
2. `zero_control` reproduces an independently run D40 baseline on every terminal, action-plane,
   action-hash, and state-hash field;
3. the population reconstructs exactly from PCG64 seed 9801;
4. one/four pairs have identical weights and exact budgets one/four;
5. no policy exceeds its batch budget or scores more than two workers in one batch; and
6. zero illegal commands, reservation/target collisions, final-own-crop fells, provenance,
   deposit-prediction, worker-cap, reward, nonfinite-feature, catalog, option-hash, or action-plane
   failures occur.

Any integrity failure quarantines value and permits only a defect repair under the unchanged
population and maps.

## Frozen safety and activity gates

Require:

1. every policy creates at least one own crop in every task;
2. at least 56/64 four-budget policies retain worker-three reach no more than ten percentage
   points below D40;
3. at least 56/64 random pairs change action hash from D40 in at least 50% of tasks;
4. at least 48/64 four-budget policies use at least three concrete job kinds and two provenance
   classes globally;
5. at least 48/64 four-budget policies execute at least two intervention batches in at least 25%
   of tasks;
6. at least 32/64 four-budget policies create a joint two-nonkeep batch in at least 10% of tasks;
   and
7. four-budget fixed-policy mean margins span at least 25 points.

Task action hashes are activity evidence only; authority is measured by the explicit batch and
assignment counters, avoiding D80's hash-saturation error.

## Frozen whole-game headroom gates

For each task construct two hindsight oracles with tie order higher margin, higher own score, lower
opponent score, fewer intervention batches, then lexical policy:

- **one oracle:** D40 plus all 64 `one_XX` policies;
- **four oracle:** D40 plus all 64 `four_XX` policies.

The representation passes only if all hold:

1. four-oracle mean margin gain over D40 is at least `+50`;
2. four oracle strictly improves D40 in at least 85% of tasks;
3. every opponent-family four-oracle mean gain is at least `+15`;
4. four-oracle mean own-score delta is nonnegative and opponent-score delta is nonpositive;
5. four-oracle worker-three reach is at least 85% and crop creation is exactly 100%;
6. four-oracle mean margin is at least `+10` above the one oracle;
7. four policies strictly beat the one-oracle row in at least 32/128 tasks;
8. at least twelve `four_XX` policies are strict four-oracle winners in at least two tasks; and
9. selected four-oracle rows use at least two intervention batches in at least 24 tasks, contain a
   joint batch in at least 16 tasks, and span all four jobs, two provenances, both seats, and all
   eight opponent families.

No fixed random rank, arm, class, target, favorable subset, or hindsight choice is selectable.

## Decision rule

- **Full pass:** freeze the bounded joint-assignment environment and open a separate short
  mechanics/learning-signal preflight initialized at exact D40. No value checkpoint is yet a
  candidate.
- **Integrity failure:** repair only the defect and repeat the unchanged matrix.
- **Safety/activity failure:** close this bounded random initialization without changing scale,
  budget, catalog, or gate on consumed maps.
- **Headroom or repeated-increment failure:** close repeated whole-game use of this interface; do
  not train PPO, CEM, imitation, or a larger scorer on it.

No branch authorizes fresh confirmation, candidate construction, TestSession, Arena, submission,
or resident replacement.
