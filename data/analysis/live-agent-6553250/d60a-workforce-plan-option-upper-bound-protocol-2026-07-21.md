# D60a workforce-plan option upper bound — frozen protocol (2026-07-21)

## Question

D56--D59 show that a fixed two-worker rule cannot choose the right sequence between renewable
source investment and immediate TRAIN-bill materialization. D40 already supplies a complete,
mechanically validated persistent-job controller and reaches worker three broadly. Does a small
semantic plan interface over D40 contain enough whole-game value and task heterogeneity to justify
learning a high-level option selector instead of adding another hand-written job rule?

This is a representation upper-bound study. It does not train or select a policy, construct a
submission candidate, change the stable resident, call TestSession, submit, or inspect Arena.

## Frozen controller anchor

Use the unchanged `CompleteMacroEnv` and exact D40 prior. Global TRAIN decisions, the one-worker
opening, positive-deficit choices, spawn evacuation, persistent job execution, target provenance,
transaction accounting, and all opponent behavior remain exact D40.

Only D40's `Rate` branch may be redirected, and only after worker two exists. Within a semantic
mode, retain D40's exact ordering and select the first legal candidate of the requested job kind;
if no such candidate exists, fall back exactly to D40 for that decision. The four modes are:

1. `balanced`: exact D40;
2. `harvest`: prefer `HARVEST_BANK`, materializing existing ripe fruit without planting;
3. `renew`: prefer `RENEW`, investing one harvested fruit into a new source before banking; and
4. `fell`: prefer `FELL_BANK`, converting living stock to wood and removing its future lineage.

These are option semantics, not fitted scores. There are no bonuses, thresholds, turn cuts,
resource weights, target-count changes, opponent identities, outcome features, or post-result
parameters.

## Frozen plan interface

Enumerate the Cartesian product of the four modes at two observable workforce phases:

- `pre3`: exactly two own workers; and
- `post3`: at least three own workers.

The one-worker phase always uses D40. A plan is therefore a persistent pair
`pre3_<mode>__post3_<mode>`, producing exactly 16 plans. Include a seventeenth `d40_control` arm
whose action is read directly from `teacher_index`; `pre3_balanced__post3_balanced` must match it in
every action and terminal field.

This phase pair is deliberately smaller than an online controller. Its hindsight per-task oracle
is an upper bound on what a deployable selector might recover, not a deployable policy and not a
label source yet.

## Frozen execution bank and telemetry

Run official seeds 9,800,000--9,800,015, both seats, and the unchanged eight D40 opponent modes:
256 tasks per arm and 4,352 rows total. Run the complete matrix twice with 20 host threads and
require byte identity. Record terminal score/return/workforce/crop/mechanical fields, action and
state hashes, all nine action-plane counts, and for each workforce phase:

- number of D40 `Rate` decisions;
- number of decisions where the requested semantic kind exists; and
- number of actual D40 overrides.

No result from seeds used before D60 is a comparator except immutable environment integrity
knowledge. The within-run direct D40 arm is the sole outcome control.

## Frozen gates

### Integrity and interface

1. Both 17 x 256 matrices are complete and byte-identical.
2. The balanced/balanced anchor matches direct D40 in every terminal, action-plane, action-hash,
   and state-hash field.
3. Every row has zero illegal command, provenance, deposit-prediction, worker-cap, reward-identity,
   action-count, eligibility, and override-accounting failure.
4. At least 12 of 15 non-anchor plans change the action hash in at least 10% of tasks.
5. `harvest`, `renew`, and `fell` each produce at least one actual override in both `pre3` and
   `post3` across the complete catalog.
6. Non-anchor plan mean margins span at least 25 points, establishing outcome sensitivity.

### Representation headroom

For each task, choose the maximum terminal margin among the 16 plans, breaking ties by higher own
score, lower opponent score, then lexical plan label. Compare this hindsight oracle to direct D40.
All must hold:

1. paired mean oracle margin gain is at least +20;
2. a non-anchor plan strictly improves at least 30% of tasks;
3. all eight opponent-family oracle mean gains are at least +8;
4. at least four different non-anchor plans are strict winners in at least four tasks each;
5. oracle mean own-score delta is nonnegative and mean opponent-score delta is nonpositive; and
6. the oracle-selected episodes retain at least 85% worker-three reach and 95% crop creation.

Best fixed-plan outcome, per-mode/phase attribution, tails, and plan frequencies are descriptive.
They may explain the result but cannot select a plan from this consumed bank.

## Decision rule

- **Full pass:** freeze the four-mode interface and open D61, a prospective opponent-blind
  state/history selector study with disjoint development and validation maps. PPO remains sealed
  until the selector representation first beats constant/fixed-plan controls.
- **Integrity or anchor failure:** quarantine outcomes and repair only the exact implementation
  defect before repeating this unchanged matrix.
- **Active but headroom failure:** close this four-mode workforce-phase interface. Do not tune
  modes, add phase cuts, weaken gates, or select a descriptively good plan; move to a richer
  job-boundary option representation.
- **Inactive:** close the mode vocabulary before reading value and inspect candidate-kind coverage
  only.

No branch authorizes candidate generation, TestSession, submission, or Arena activity.
