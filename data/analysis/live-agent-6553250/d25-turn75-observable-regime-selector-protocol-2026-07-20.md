# D25 observable turn-75 regime selector — frozen protocol (2026-07-20)

## Question

Can visible state history through turn 75 conservatively identify when the frozen `ownership2`
complete continuation is safer and more valuable than the warmed resident continuation?

D24 established the option's mechanism twice: it adds +67.80 own score in discovery and +59.77
in confirmation.  Its unconditional confirmation failed because the opponent also gained +44.87
score, with negative mean against three productive Gold-family regimes.  D25 therefore predicts
complete terminal option value, not single actions, worker count, opponent nickname, or a generic
catastrophe label.

## Frozen development corpus

D25 treats all already-read D24 maps as **development data**:

- seeds 50,000--50,119;
- both seats and all eight fixed opponents;
- exact resident prefix through turn 74;
- exact resident and `ownership2` terminal continuations from turn 75;
- 1,920 labeled opponent cells / 120 independent map seeds.

The earlier D24 confirmation block is not validation for D25 because this hypothesis was formed
after its outcomes were read.  It may be used for development and cross-validation but never
cited as prospective evidence again.

No additional generated seed may be opened unless the complete cross-validation gate below
passes.  If it passes, seeds **50,120--50,179** are reserved for one prospective test; otherwise
they remain unopened.

## Frozen observable representation

The feature exporter recreates the exact resident/opponent prefix and records referee-visible
state at turns 1, 25, 50, and 75:

- map dimensions, walkable/water/iron counts, shack separation, and relative resource geometry;
- both scores and all inventory items;
- worker counts, visible stats, carried items, and distances to both shacks;
- total and per-species plant count, size, health, fruit, cooldown, own-side/opponent-side split,
  near-shack supply, and ripe supply; and
- derived score, wood, worker, plant, and supply velocities between checkpoints.

Forbidden features are seed number, opponent name or index, agent identity, hidden command text,
future state, option state, terminal outcome, model-compatibility score, and any field unavailable
to a live bot.  Seat is a grouping key, not a model feature.  All geometry is expressed relative
to the controlled player.

## Integrity gates

Before fitting:

1. a consumed five-seed export must be byte-identical on repeat;
2. all 1,920 development keys must appear exactly once;
3. turn-75 root score, wood, worker, plant, and reached-cut fields must exactly match the frozen
   D24 rows;
4. no forbidden key may enter the model matrix;
5. every feature must be finite and have identical meaning in both seats; and
6. a row-order shuffle must leave every out-of-fold prediction and decision unchanged.

An integrity failure permits infrastructure repair only; no model result is interpretable until
the gate passes.

## Frozen model family

Fit value regressors to exact terminal margin delta (`ownership2 - resident`).  The deliberately
small fixed grid is:

- ridge regression with standardized features and alpha in `{1, 10, 100}`;
- random forest with 256 trees, maximum depth in `{2, 3, 4}`, minimum leaf in `{20, 40, 80}`, and
  fixed random seed 2501; and
- extremely randomized forest with the same depth/leaf grid and fixed seed 2501.

Each regressor is paired with a switch buffer in `{0, 10, 20, 30, 40}` margin points.  No model,
feature, hyperparameter, buffer, or preprocessing change may be added after results are inspected.

Ridge standardizes each feature on the training fold and leaves the intercept unpenalized.  Both
forest families use seed-cluster bootstraps, squared-error regression leaves, and
`ceil(sqrt(feature_count))` randomly sampled features per node.  Random forest evaluates at most
16 evenly spaced admissible value gaps per sampled feature; extremely randomized forest evaluates
one randomly selected admissible gap.  The leaf prediction is mean training-fold terminal delta.
All trees and folds derive deterministic sub-seeds from 2501.  Complexity order is ridge, then
depth 2/3/4; within equal depth, a larger minimum leaf is simpler, with family name as the final
tie break.

## Frozen cross-validation

Every configuration receives two independent out-of-fold evaluations:

1. **blocked map:** six contiguous 20-seed folds; train on five folds and predict the sixth;
2. **held opponent family:** eight folds; train on seven full opponent families and predict the
   unseen eighth.

For a predicted value above the fixed buffer, take the exact `ownership2` outcome; otherwise take
resident delta zero.  Statistics cluster by seed.  Opponent names may define the second split and
reporting groups but are never inputs.

## Research gate and selection

A configuration passes only if **both** out-of-fold schemes satisfy all of these:

1. switch rate is between 5% and 60%;
2. selected-action precision (`true delta > 0`) is at least 75%;
3. seed-clustered mean selected-policy margin delta is at least +5;
4. its 5%-trimmed mean is at least +3 and normal 95% lower bound is above zero;
5. at least 6/8 opponent-family means are nonnegative and the worst is at least -5;
6. selected-policy catastrophic frequency and negative-margin mass do not exceed resident; and
7. the selected policy captures at least 20% of the positive-cell hindsight oracle mean.

If multiple configurations pass, select by highest minimum worst-opponent mean across the two
schemes, then highest minimum mean value, then lowest switch rate, then lower model complexity,
then larger buffer, then lexical label.  Freeze exactly one model trained on all 120 development
seeds before opening prospective data.

If no configuration passes, close observable farm/resident regime selection at this
representation.  Do not add opponent identity, nickname tables, more capacity, new thresholds,
or another development block.

## Prospective disposition

If and only if development passes, run the frozen exporter, exact two-branch D24 evaluator, and
frozen model once on seeds 50,120--50,179.  The prospective gate repeats every condition above
using the single trained model, and requires at least 90% model-decision reproducibility between
Python and a compact deterministic reference implementation before candidate work.

A pass authorizes only integration, exact parity, latency, size, and a later independent local
regression block.  It does not authorize submission or Arena activity.

## Outputs

- exporter: `rust/src/bin/d25_turn75_features.rs`;
- selector analysis: `cgauto/d25_turn75_regime_selector.py`;
- consumed feature TSV/analysis JSON and optional prospective artifacts;
- result: `d25-turn75-observable-regime-selector-result-2026-07-20.md`.
