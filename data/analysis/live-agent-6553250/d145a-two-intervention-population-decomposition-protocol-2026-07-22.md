# D145a two-intervention population decomposition — frozen protocol

Date: 2026-07-22  
Status: frozen after the D144b full pass and before computing prefix, partition, or selected-move
decompositions

## Purpose

D144b proves `+4.148` sampled two-use headroom beyond exact one use, but a maximum over 111
double-mode replicas per task can hide two different regimes:

- broad, repeatable sequence value that should be scaled across more maps; or
- value concentrated in rare extreme samples that requires deeper search before distillation.

It also does not say whether a winning sequence usually starts with the exact greedy one-use
oracle action. That determines whether the next deployable architecture should add a second-stage
residual to the existing one-use teacher or jointly learn both trajectory decisions.

D145 uses only the frozen D144 artifacts. It runs no simulation and cannot qualify a candidate.

## Frozen decomposition

Recompute the combined exact-one/two-use oracle using deterministic prefixes of the double-mode
replicas: the first 8, 16, 32, 64, and all 111 replicas (`17...127`). Report each prefix's mean and
strict increment, family breadth/floor, safety, executed-two count, and fraction of the all-111
mean. The full view must reproduce every shared D144b oracle field exactly.

Independently score two disjoint sequence populations by the zero-based parity of double-replica
ordinal. These contain 56 and 55 replicas. Both partitions must independently achieve:

- at least `+2.0` mean margin beyond exact one use;
- strict incremental improvement on at least 25% of all tasks; and
- positive mean increment in at least six opponent families.

Require the 64-replica prefix to retain at least 80% of the all-111 mean. Passing means a broader
map corpus can cap search at 64 double replicas per task; failing only this gate means retain the
sampler but deepen per-task search before creating a teacher.

## Winning-sequence attribution

For every task where the full sampled double oracle strictly beats the exact one-use oracle, write
one deterministic manifest row. Join its first `(task, boundary, slot)` to the exact D112 arm and
record:

- exact one-use gain;
- the selected first action's gain when executed alone;
- final two-use gain;
- lift of the second move over the same first move;
- both boundaries, gap, representative slots, first action kind, and selected replica; and
- whether the first action is exactly the task's one-use oracle arm.

Require mean second-move lift over the same first move of at least `+5` and a strictly positive
lift for every selected sequence. The latter is also a cross-artifact identity check: the complete
one-use oracle must dominate every first action executed alone.

Classify the next architecture at a frozen 50% exact-arm threshold. If at least half of winning
sequences begin with the exact one-use oracle arm, scale a second-stage residual teacher. Otherwise
scale a joint two-stage trajectory teacher. This classifier does not affect whether the population
value is considered robust.

## Decision

- All partition, saturation, and second-lift gates pass: scale map breadth with at most 64 double
  replicas per task, then use the 50% classifier to choose residual versus joint training.
- Every gate except 64-replica saturation passes: increase per-task search before teacher
  collection.
- Any partition or second-lift failure: do not scale the current sampler.

D145 consumes no new map, D126/final validation, YT operation, resident change, submission,
TestSession, or Arena action.
