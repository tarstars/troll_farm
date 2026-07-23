# D83a threatened-response value predictability — frozen protocol (2026-07-21)

## Question

D82 proves +11.240 safe one-decision oracle headroom but shows that no fixed response is reliable.
Can a compact deployable snapshot value model recover enough held-map value to justify prospective
closed-loop evaluation?

D83a uses only consumed D82 roots/outcomes for grouped discovery. It cannot itself create a
candidate, open confirmation, or touch the platform.

## Frozen feature export

Replay exact D40 on D82 maps 9,914,000--9,914,031 to the unchanged first threatened-own-crop root.
Export one control row per task plus one row for every available fell/harvest/renew arm. Run the
export twice with 20 threads and require byte identity. Root identity and arm availability must
match the exact D82 matrix.

The 169 deployable float features are, in fixed order:

1. D42 shared context (46);
2. D40 control candidate features (44) and job context (16);
3. response candidate features (44) and job context (16); and
4. fell/harvest/renew one-hot (3).

For rooted control rows, response features equal control and the semantic one-hot is zero. For
unrooted controls all 169 values are zero. No map seed, seat, opponent identity/mode, terminal
field, future command, rollout result, rank, root turn, or state hash is a model feature.

## Frozen labels and model

Join each available semantic row to its exact D82 arm-minus-control terminal margin, own-score, and
opponent-score deltas. Control is an implicit action with predicted and realized delta zero.

Use eight held-map folds, `fold = map_seed mod 8`. In each fold:

1. fit only the other seven folds;
2. standardize each of 169 coordinates from training mean and population standard deviation,
   replacing zero scale with one;
3. fit one pooled ridge regression to raw terminal margin delta with fixed `lambda = 10`, centered
   features, an unpenalized intercept, and no clipping/weighting;
4. predict every available response in the held fold; and
5. per task choose the highest prediction only when it is strictly positive, otherwise control.
   Ties prefer control, then harvest, renew, fell.

No lambda, feature, target, fold, threshold, or arm-specific model may change after OOF results.

## Frozen integrity gates

Require exact byte-repeat export, all 512 task roots/656 available arms matched to D82, exact
provenance/proximity/semantic one-hots, finite features/fits/predictions, one OOF prediction per
available arm, disjoint fold training, and deterministic repeated analysis.

## Frozen OOF gates

The selected OOF policy must satisfy all:

1. mean margin gain at least +2;
2. strict improvement in at least 30% of rooted tasks and regression in at most 30%;
3. mean own-score delta nonnegative or mean opponent-score delta nonpositive;
4. at least six opponent-family mean gains nonnegative and the worst at least -3;
5. intervention rate among rooted tasks between 10% and 70%;
6. at least two semantic response types selected in at least eight tasks each; and
7. at least six of eight held-map-fold means nonnegative and the worst at least -5.

Report oracle capture, prediction Pearson/Spearman, sign precision, arm mix, fold/family effects,
and fixed-arm baselines descriptively; none can replace the conjunction.

## Decision rule

- **All gates pass:** fit the identical ridge recipe on all D82 rows, serialize its means/scales /
  weights/intercept, and open D83b prospective closed-loop evaluation on sealed maps
  9,915,000--9,915,031.
- **OOF failure:** close this pooled snapshot value model. Do not tune lambda, threshold, features,
  folds, arm weighting, or reuse D82 for another fit.
- **Integrity failure:** quarantine OOF value and repair only the defect before unchanged repeat.

Even on pass, the full-fit model is an experiment input, not a submission candidate. Active
TestSession, submission, resident replacement, and Arena remain unauthorized.
