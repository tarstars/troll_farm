# D29 canonical spatial option critic — frozen protocol (2026-07-20)

## Question

Can a small player-relative spatial value model distinguish the turn-75 states where permanent
`ownership2` is preferable to the warmed resident, without D25's map-compatibility overfit?

D25's tabular forest retained +28.888 margin under simultaneous unseen-map/unseen-family folds but
missed its precision floor at 73.23%.  D26--D28 then falsified fixed pulses and state-preserving
returns.  D29 changes representation and data scale, not the D25 threshold or forest: it trains a
single canonical convolutional critic from scratch on five times as many newly designated maps.

This is an offline option-value experiment.  It does not run Monte Carlo in the submission, alter
either complete policy, submit, or act in Arena.

## Exact option and data

Every cell follows the exact resident through turn 74.  From the common turn-75 root:

- fallback: exact warmed resident through terminal;
- option: cold `ownership2` through terminal; and
- target: option terminal margin minus fallback terminal margin.

Partitions are fixed before generation:

- outcome-blind exporter smoke: consumed seeds 0--4, both seats, eight structural opponents;
- development: **600 new maps, seeds 53,000--53,599**, both seats and all eight opponents;
- prospective confirmation, only after a complete development pass: **120 untouched maps,
  seeds 53,600--53,719**.

The independent statistical unit is map seed after averaging seats/opponents.  Compact Gold and
fixed Gold are one structural family in validation, yielding seven families.

## Observable representation

At turn 75, rotate the board 180 degrees when necessary so the controlled shack is
lexicographically before the opponent shack, then pad to 22 x 11.  Export 36 raw integer planes:

1. in-map, walkable, water, and iron masks;
2. own and opponent shack masks;
3. four plant-kind masks plus size, health, fruit, and cooldown;
4. own unit count, movement, carry capacity, harvest, chop, and six carried-item planes; and
5. the same eleven unit planes for the opponent.

Combine these planes with D25's already-defined referee-visible scalar trajectory summary from
turns 1/25/50/75.  Relative orientation is applied before padding; seed, seat, opponent identity,
future commands/states, and terminal outcomes are forbidden inputs.  Fixed plane scales are 1 for
masks/count, 4 for plant size, 20 for health, 3 for fruit, 9 for cooldown, and 3 for unit stats and
carried items.  Scalars are standardized on each training fold only.

## Frozen model

One deterministic PyTorch model, no architecture or threshold grid:

- `Conv2d(36, 8, 3, padding=1)`, ReLU;
- `Conv2d(8, 8, 3, padding=1)`, ReLU;
- masked global mean and maximum pooling;
- scalar `Linear(n_features, 8)`, ReLU;
- concatenated `Linear(24, 16)`, ReLU, then `Linear(16, 1)`;
- at most 8,000 trainable parameters;
- 25th-percentile pinball loss, fixed threshold zero;
- AdamW, learning rate 0.001, weight decay 0.0001, batch 256, exactly 30 epochs;
- target mean/standard deviation estimated on the training fold, with predictions transformed
  back to raw margin before applying the zero threshold;
- seed 2901, sorted batches, 14 CPU intra-op threads, one inter-op thread, deterministic
  algorithms, no early stopping, checkpoint choice,
  augmentation, class weighting, or hyperparameter tuning.

The lower-quantile target and zero threshold replace D25's fitted mean-plus-buffer mechanism.  A
positive prediction means the conservative conditional value estimate favors the farm.

## Integrity and crossed evaluation

Smoke must be byte-identical on repeat, emit the exact 36 x 11 x 22 plane count for every row,
canonicalize both seats, and match D24/D25 turn-75 root fields.  Development must contain all
9,600 unique cells and exact resident/option labels from the existing D24 evaluator.

The sole selectable evidence is 42 crossed folds: six contiguous 100-map blocks x seven
structural opponent families.  For each fold, exclude both the held map block and every row of the
held family, train from initialization, and predict only their intersection.  Every row receives
exactly one prediction.  A byte-identical rerun of the complete prediction artifact is required.
Marginal blocked-map or held-family results may be reported descriptively but cannot select.

## Development gates

The crossed out-of-fold policy switches to `ownership2` only where predicted value is positive.
It passes only if all conditions hold:

1. switch rate is 5--55%;
2. positive-cell precision is at least **78%**;
3. seed-clustered mean margin is at least +8, 5%-trimmed mean at least +5, and 95% lower bound >0;
4. at least 6/8 opponent means are nonnegative and the worst is >=-5;
5. every one of the six held map blocks has nonnegative policy mean;
6. catastrophic frequency and negative-margin mass do not exceed resident;
7. at least 25% of the positive-cell hindsight-oracle mean is captured; and
8. two complete executions produce identical decisions/predictions within exact float32
   serialization, with no NaN, leakage, or fold overlap.

Failure closes D29 without changing quantile, threshold, epochs, channels, padding, or model size.

## Prospective and deployment disposition

Only after a development pass, train the exact model once on all 600 development maps, hash it,
and evaluate once on seeds 53,600--53,719.  Confirmation repeats every aggregate gate, uses no
refit, applies its preregistered cell-precision floor of >=75%, and requires every 20-map block
mean to be nonnegative.  (The 78% cell-precision floor selects the development model; it is not
re-applied to the smaller confirmation set.)

A two-stage pass authorizes deterministic Rust inference parity, int8 quantization, combined
resident/farm source-size measurement, latency measurement, and a separate field-transfer plan.
It does not authorize submission or Arena.  Quantization may not change more than 1% of decisions
or reduce paired mean by more than one point.

## Outputs

- spatial exporter: `rust/src/bin/d29_spatial_features.rs`;
- trainer/evaluator: `cgauto/d29_spatial_option_critic.py`;
- smoke/development/optional confirmation feature, label, prediction, and result artifacts;
- result: `d29-canonical-spatial-option-critic-result-2026-07-20.md`.
