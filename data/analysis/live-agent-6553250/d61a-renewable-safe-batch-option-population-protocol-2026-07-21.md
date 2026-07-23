# D61a renewable-safe batch-option population — frozen protocol (2026-07-21)

## Question

D60 proves that harvest/materialize, renew/invest, and fell/liquidate choices contain +47.398
whole-game oracle margin over exact D40, but one fixed choice for each workforce phase admits 30
profitable no-crop trajectories and fails safety. Can the same coefficient-free semantics become a
useful controller representation when one option is chosen from observable state at every natural
free-worker assignment batch and renewable establishment/preservation is part of option legality?

D61 is a random-function-class/upper-bound preflight. It does not fit a selector, train PPO, choose
a deployable policy, construct a candidate, change the stable resident, call TestSession, submit,
or inspect Arena.

## Frozen semi-Markov option boundary

Use the unchanged `CompleteMacroEnv` and exact D40 prior. A new option decision occurs only at the
environment's `Train` stage, before D40's TRAIN choice for a newly free worker batch. The chosen
mode persists across every worker assignment in that batch and is discarded when exact execution
advances to the next Train-stage boundary.

TRAIN, positive-deficit, and evacuation branches always execute exact D40. On a `Rate` worker
decision, the active mode selects the first legal candidate of its requested job kind under D40's
unchanged exact prior, falling back to the first renewable-safe D40 candidate when absent:

1. `balanced`: exact D40 priority;
2. `harvest`: `HARVEST_BANK`;
3. `renew`: `RENEW`; and
4. `fell`: `FELL_BANK`.

There is no option duration, turn cut, resource weight, target count, fitted bonus, rollout,
opponent identity, seed, or terminal feature.

## Frozen renewable legality

Candidate policies cannot act until exact D40 has established at least one currently live
own-provenance crop. While no such crop exists, force `balanced` for the whole batch. If all own
crops later disappear, return to the same D40 establishment lock until an own crop is live again.

Once unlocked, reject any `FELL_BANK` candidate whose target is own-provenance when only one live
own crop remains. Scan the same D40 order for the next safe requested candidate, or the first safe
D40 fallback. Other provenance classes and job kinds are unchanged. The direct D40 control bypasses
this filter; the `safe_balanced` anchor must nevertheless reproduce it exactly on the frozen bank.

This uses only current plant provenance already maintained by the deployable controller. It does
not use the terminal crop counter or future survival.

## Frozen deployable state vector

At each option boundary expose exactly 56 finite normalized features:

- bias, turn, own/opponent worker counts, own/opponent score, and score margin (7);
- six own and six opponent deposited inventory coordinates (12);
- six own and six opponent carried-inventory coordinates (12);
- live plant counts and live fruit totals for natural/own/opponent/ambiguous provenance (8);
- current own/opponent live-source indicators (2);
- persistent TRAIN goal one-hot: none/producer/chopper (3);
- previous executed option one-hot (4);
- cumulative executed batch counts for the four modes (4);
- water and walkable fractions (2); and
- total own harvest and chop capability (2).

No opponent mode label, nickname, seed, future command, rollout value, terminal result, or D60
hindsight selection enters the vector.

## Frozen policy population

Generate one immutable TSV before outcomes with:

- `d40_control`, which directly reads `teacher_index` and ignores the option layer;
- `safe_balanced`, `safe_harvest`, `safe_renew`, and `safe_fell`; and
- 64 deterministic linear policies `linear_00`--`linear_63`.

Each linear policy contains 4 x 56 weights generated once by NumPy `PCG64` seed 6101. Non-bias
weights are independent Normal(0, 0.5), bias weights Normal(0, 0.15), and for each feature the mean
across four modes is subtracted because common-mode weights cannot affect argmax. Values are frozen
to eight decimal places. At a boundary choose the maximum dot product, breaking exact ties in mode
order `balanced`, `harvest`, `renew`, `fell`.

The random policies are probes of a compact deployable function class. None can be selected from
this consumed population even if its fixed mean is positive.

## Frozen execution and telemetry

Run official seeds 9,801,000--9,801,007, both seats, and all eight unchanged D40 opponent modes:
128 tasks per policy, 69 policies, and 8,832 rows. Repeat the full matrix with 20 host threads and
require byte identity.

Record all D60 terminal/mechanical/action-plane fields plus option batches, establishment-locked
batches, counts for each executed mode, mode switches, safe-fell rejections, semantic eligibility,
semantic overrides, and an option-sequence hash.

## Frozen gates

### Integrity, safety, and activity

1. Both 69 x 128 matrices are complete and byte-identical.
2. `safe_balanced` matches direct D40 in every terminal, action-plane, action-hash, and state-hash
   field.
3. Every row has zero illegal command, provenance, deposit-prediction, worker-cap,
   reward-identity, action-count, finite-feature, mode-count, switch-count, option-hash, or
   eligibility/override failure.
4. Direct D40 and every one of the 68 option policies create at least one crop in every task.
5. At least 56/68 option policies change action hash in at least 10% of tasks.
6. `harvest`, `renew`, and `fell` each issue at least 1,000 semantic overrides across the full
   population.
7. At least 48/64 linear policies execute at least three different modes globally.
8. At least 48/64 linear policies switch modes in at least 25% of their tasks.
9. Candidate-policy mean margins span at least 25 points.

### Crop-safe representation headroom

For each task choose maximum terminal margin among the 68 option policies, breaking ties by higher
own score, lower opponent score, then lexical policy label. Compare this hindsight population
oracle to direct D40. All must hold:

1. mean oracle margin gain is at least +30;
2. strict improvement occurs in at least 60% of tasks;
3. every opponent-family mean gain is at least +10;
4. at least twelve distinct linear policies are strict winners in at least two tasks each;
5. linear policies account for at least half of all strict oracle selections;
6. mean own-score delta is nonnegative and mean opponent-score delta is nonpositive;
7. worker-three reach is at least 85%; and
8. crop creation is exactly 100%.

Best fixed-policy means, tails, selected labels, mode frequencies, and lock frequency are
descriptive only. They cannot nominate a checkpoint or policy.

## Decision rule

- **Full pass:** freeze the batch-option environment and open a separate short PPO/behavioral
  preflight. It must learn state-dependent mode probabilities and beat constant/frozen controls on
  disjoint maps before a long run.
- **Safety, anchor, or integrity failure:** quarantine outcomes and repair only the exact invariant
  before repeating this unchanged matrix.
- **Active but headroom/function-class failure:** close linear state-conditioned batch options and
  move to recurrent or paired-rollout option values; do not tune weights, random seed, modes,
  features, gates, or consumed maps.
- **Inactive:** close the batch boundary before reading value and inspect option coverage only.

No branch authorizes candidate construction, TestSession, submission, or Arena activity.
