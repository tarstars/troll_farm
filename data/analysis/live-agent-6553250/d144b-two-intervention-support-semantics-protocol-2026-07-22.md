# D144b two-intervention support-semantics repair — frozen protocol

Date: 2026-07-22  
Status: frozen after D144a's mechanics-only stop and before computing any target incremental-oracle
value

## Diagnosis available at the stop boundary

D144a passes every YT, reproducibility, exact-one-use, schema, mapping, hash, cap, accounting,
failure, control-parity, single-arm-parity, and two-use episode-rate gate. It stops only because
118/128 tasks execute a sampled two-intervention sequence (`92.1875%`) rather than the prescribed
95%.

The independently collected exact D112 baselines show that exactly the same 118/128 tasks have at
least one q6 boundary; ten tasks have zero boundaries and are structurally forced to D40 control.
No schedule, proposal sampler, or number of replicas can execute two interventions in those ten
tasks. Therefore the raw all-task denominator asks for at least 122 eligible tasks on a panel that
contains only 118. This is the same availability distinction established by D113/D133b: a valid
zero-boundary task is control evidence, not a malformed or under-sampled trajectory.

D144a did not compute or expose the target incremental oracle after this stop. Only mechanics and
the already-independent exact one-use teacher are known.

## Isolated repair

Remove only `at_least_95pct_tasks_have_sampled_two_interventions`. Retain every other frozen D144a
infrastructure and mechanics gate unchanged. Replace it with stronger feasibility-conditioned
requirements:

1. the complete 128-task baseline grid is unique;
2. the set of tasks with at least one executed two-intervention episode is exactly the set whose
   exact baseline has at least one q6 boundary—no missing eligible task and no impossible extra;
3. every episode of every zero-boundary task executes zero interventions and exactly reproduces
   its D112 baseline terminal; and
4. descriptive raw two-use task coverage equals exact q6 support availability.

This requires 100% coverage of eligible tasks rather than 95% coverage of all tasks. It changes no
corpus byte, seed, schedule, action, replica count, outcome, target definition, or model.

## Value interpretation and decision

Only if all repaired mechanics pass may D144b compute the previously hidden oracle. Apply the
original D144a value and relative-safety gates without alteration over all 128 tasks, including
forced-control tasks:

- at least `+3.0` mean margin beyond complete exact one use;
- strict incremental improvement on at least 20% of tasks;
- at least six positive opponent-family increments and a nonnegative worst family;
- zero new crop failures versus exact one use; and
- worker-three reach within five percentage points of exact one use.

A full pass opens a separately frozen trajectory-teacher and deployable two-intervention policy
fit. A mechanics-clean value or safety failure closes this sampled two-intervention population.
D144b runs no simulation, launches no YT job, consumes no D126/final seed, changes no resident,
submits nothing, and does not touch TestSession or Arena.
