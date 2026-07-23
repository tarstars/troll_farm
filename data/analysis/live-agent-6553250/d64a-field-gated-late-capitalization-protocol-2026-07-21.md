# D64a field-gated late-capitalization protocol (2026-07-21)

## Question

Does the instantaneous economy state that predicts later third-worker creation in held current top
agents also select a *valuable* late-capitalization decision prospectively in the exact complete
macro environment?

D64a is the causal bridge between D63 behavior prediction and controller construction. It tests
one fixed selector and one fixed two-arm decision. It does not tune a threshold, choose a worker
genome, alter D40's job scheduler, construct a submission, or perform a platform action.

## Frozen sources and classifier

- D63a source report SHA-256:
  `58be23c7a7e6b5995bcaa5b7a209a412f7a06a0231b66a8c9eb83013b5a98ef2`.
- D63b result SHA-256:
  `6970d5ae2949c71f32bcade6f992d39b2f1f984c15d73b1f4593cbceaf5db059`.
- Refit the exact D63b 44-feature `snapshot` logistic model from discovery rows only using D63a's
  frozen normalization, L2 lambda 1.0, and optimizer. Export feature order, means, scales,
  standardized coefficients, intercept, and fixed probability threshold 0.5 before any D64 game.
- The exporter must reproduce D63b snapshot discovery/validation AUC and balanced accuracy within
  `1e-15`, and its artifact must be immutable during D64 execution.
- Also export an outcome-blind support reference: for each D63 validation row, compute RMS
  standardized distance from the discovery mean over the 44 features. The support radius is the
  nearest-rank 95th percentile (`sorted_values[ceil(0.95*n)-1]`). This diagnostic cannot change
  the action; it only gates transfer language.

The exact instantaneous vector is the sorted D63b snapshot feature set: current own/opponent bank
and carried inventories, inventory score/wood gaps, carrying-worker counts, opponent worker count,
and current board plant/fruit/health/size aggregates. It contains no opening, worker talent,
action-history, outcome, opponent identity, or future feature.

## Frozen intervention boundary

Use unchanged `CompleteMacroEnv`, exact D40 `teacher_index`, maximum three workers, and all eight
unchanged opponent modes.

All policies execute D40 exactly before turn 100. At the first `Train`-stage boundary satisfying:

- current turn >=100; and
- own worker count is exactly two,

record the exact state hash and classifier probability, then latch one of two actions for the
remainder of the game:

1. **scale:** preserve exact D40, including its chopper third-worker goal; or
2. **suppress:** whenever still at two workers at a later `Train` stage, select `None` instead of
   D40's chopper goal. Every worker-stage action remains exact D40.

The latch never removes an existing third worker, changes pre-turn-100 behavior, interrupts an
active worker job, changes TRAIN cost/specification, or alters any opponent. Tasks that create
worker three before the boundary are ineligible and remain identical across policies.

## Frozen policies

Run exactly four policies:

- `d40_control`: always latch scale;
- `never_late_scale`: always latch suppress;
- `field_snapshot_gate`: scale iff frozen probability >=0.5;
- `inverse_snapshot_gate`: scale iff frozen probability <0.5.

The inverse is a directional negative control, not a candidate. No threshold, tie rule, feature,
or policy may be selected from D64 outcomes.

## Fresh task bank and repetition

Use official seeds 9,830,000--9,830,015, both seats, and all eight D40 opponent modes:
256 tasks per policy and 1,024 rows per matrix. Seeds 9,830,000--9,830,007 are the development
block; 9,830,008--9,830,015 are the validation block. Run the full matrix twice with 20 host
threads and require byte identity.

Record all D61 terminal/mechanical/action-plane fields plus eligibility, decision turn/state hash,
classifier logit/probability, latched action, RMS standardized distance, support-radius membership,
override count, and first observed third-worker turn.

## Frozen analysis

Compare policies only within exact task keys. Report full, eligible-only, block, and opponent-family
paired changes in own score, opponent score, margin, catastrophic losses (`margin <= -100`), worker
three, crops, and action hashes.

For each eligible task, define a two-arm hindsight upper bound as the better terminal margin of
`d40_control` and `never_late_scale`, breaking ties by higher own score, lower opponent score, then
`d40_control`. This oracle measures action headroom only; it cannot select a deployable policy.
Report selector agreement with the oracle and captured oracle margin gain.

## Frozen gates

### Integrity and safety

1. Both 4 x 256 matrices are complete and byte-identical.
2. Every task has identical eligibility, decision turn, decision-state hash, logit, probability,
   and support diagnostics across all four policies; all ineligible tasks are terminally identical.
3. Every row has zero illegal command, provenance, deposit-prediction, worker-cap, reward-identity,
   finite-feature, model-parity, or action-accounting failure.
4. `field_snapshot_gate` creates a crop in every task, retains at least two workers in every task,
   and never exceeds three workers.

### Support and activity

5. At least 32 tasks are eligible overall and at least 12 in each block.
6. `field_snapshot_gate` selects scale and suppress on at least eight eligible tasks each overall
   and at least three each in both blocks.
7. It changes terminal action hash versus each pure arm on at least eight tasks.
8. At least half of eligible decision states fall within the frozen field support radius.

### Action headroom

9. On eligible tasks, the two-arm oracle gains at least +5.0 mean margin over D40 and strictly
   improves at least 20% of tasks.

### Selector value

10. On eligible tasks, `field_snapshot_gate` gains at least +2.0 mean margin over D40, captures at
    least 25% of oracle gain, and beats `inverse_snapshot_gate` by at least +2.0 mean margin.
11. Its eligible validation-block mean margin delta versus D40 is nonnegative.
12. Across all tasks, its mean margin delta is nonnegative, mean own-score delta is at least -2.0,
    mean opponent-score delta is at most +2.0, and no opponent-family mean margin delta is below
    -5.0.
13. It does not increase catastrophic-loss count overall or in the validation block.

Missing support is `insufficient`; integrity/safety failure is `invalid`; adequate support with a
failed value conjunction is `fail`. Gates are not relaxed for small effects.

## Decision rule

- **Full pass:** validate state-conditioned late capitalization on the complete controller. Open a
  separate integration protocol using this fixed action inside a submission-capable complete
  controller, then require fresh field confirmation before candidacy.
- **Oracle/headroom pass but selector-value fail:** the action is useful but the observational
  classifier is not a value selector. Open a narrow Monte-Carlo/value-target experiment at this
  boundary; do not tune the D63 threshold or restart broad PPO.
- **Support/activity failure:** classify D63-to-D40 transfer as distribution mismatch. Do not infer
  value or tune the classifier; move to role-conditioned/recurrent representation on a field-like
  controller substrate.
- **Oracle/headroom failure:** close late scale-vs-suppress as a useful local action on D40.
- **Safety/integrity failure:** quarantine value and repair only the violated invariant.

No branch authorizes confirmation access, TestSession, Arena, submission, or resident replacement.

