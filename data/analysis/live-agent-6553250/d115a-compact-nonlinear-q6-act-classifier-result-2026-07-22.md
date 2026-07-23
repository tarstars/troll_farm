# D115a compact nonlinear q6 act classifier — result

Date: 2026-07-22  
Decision: **mechanics and teacher pass; no classifier admission; held remains sealed**

## Coverage repair and mechanics

The first independent eight-map validation panel produced 582 roots, below the frozen 600-root
floor, although every other mechanic passed. No D115 model was trained or scored. Repair 1 did not
waive the floor: it quarantined that panel and prospectively collected a wholly fresh balanced
ten-map panel on seeds `9,843,610--9,843,619`.

The repaired panel contains 160 baselines, 909 roots, and 14,602 exact arms at 30.467 arms/s. It
supports 150/160 tasks (93.75%). All frozen hashes, grids, features, paired gains, reward
identities, one-use accounting, crop/workforce safety, and mechanics pass with zero failures. The
selection result is byte-identical across two full deterministic fits.

## Teacher and classifier frontier

The validation teacher remains very strong: `+40.169` mean margin, 93.125% strict improvement,
all eight positive families, and a `+26.800` family floor. Backward DP marks 441/909 roots as
act-now and 1,755/14,602 arms positive. Signal remains abundant and transfers beyond D114.

Four 6,097-parameter ReLU classifiers converge to weighted BCE `0.567--0.576`, with roughly
70% positive and nonpositive training recall. None of the 24 frozen seed/offset combinations
passes validation.

The highest-mean candidate (seed 11502, offset 0) reaches `+1.081` and 42.5% strict improvements,
but intervenes on 89.375% of tasks, has fold means `-1.350` / `+3.513`, and misses the `+2` mean
gate. Its family floor is `-2.200`, with five positive families. The most robust sparse point
(seed 11501, offset 2) has nonnegative folds, a `-0.600` floor, five positive families, and 14.375%
activity, but only `+0.669` mean and 8.75% strict improvements.

No checkpoint is retained and conditional held seeds `9,843,700--9,843,715` remain unopened.

## Conclusion

Close independent per-arm binary classification. It improves materially over D114's linear
regression, but class balancing teaches whether an arm is plausibly positive, not whether it is
the best proposal at a root or better than waiting. That mismatch produces either excessive early
intervention or a weak sparse tail.

The next bounded learner should optimize the deployed decision directly: one root-wise categorical
loss over every proposal plus an explicit WAIT alternative, using the exact backward-DP
`teacher_take_arm` label. Keep the compact shared proposal scorer and first-positive runtime, but
train ranking and abstention jointly with equal root weight. Use only D114 fit data, collect a new
validation panel, and keep the existing global held range sealed.

Result SHA-256: `453988476ccd7a890500b6a04dd132b54f1ea6002b5e4e60184eb97c522be5f6`  
Selection lock SHA-256: `70c5e0b84501f72f63b81f72ddd3e6d3ff00f34a657e6cb32acde246eb52231c`
