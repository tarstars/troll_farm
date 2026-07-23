# D153b out-of-fold confidence/abstention diagnostic — frozen protocol

Date: 2026-07-23  
Status: frozen after D153a closed, before generating or reading any per-action D153b score export

## Question

D153a transfers only `+0.858--+1.820` margin and chooses control in 2.2%--2.9% of states, despite
selecting roughly `+14--+17` value in fit. Determine whether its out-of-fold score magnitude has a
small high-precision region that can justify control abstention. Do not alter features, targets,
architecture, loss, epochs, seeds, or folds.

Recreate all 32 D153a outer-fold fits for seeds `15301--15304` and export predicted relative value
for every held legal action. Run the export twice. Require exact action keys and targets, maximum
A/B score drift at most `1e-4` margin points, and exact A/B selected slots for every diagnostic
policy. Tiny threaded model-hash differences already observed in D153a are recorded, not hidden.

## Frozen readout

Evaluate each seed separately and the mean four-seed ensemble. In each state, find the stable
highest-scored noncontrol slot. Execute it only when its predicted value is at least one of:

`0, 2, 5, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60` margin points.

Otherwise choose slot zero. Threshold zero must reproduce the corresponding D153a held behavior
for each individual seed. Also report rank-decile calibration of the ensemble's best noncontrol
score against its exact value.

A source/threshold pair has enough diagnostic support only if it selects noncontrol in at least
10% of the 909 states and has:

- mean exact conditional value at least `+5.0`;
- harmful negative selection rate at most 15%;
- oracle-value capture at least 15%;
- nonnegative mean selected value in every fold;
- at least six positive opponent families and a family floor at least `-2`;
- zero new crop failures; and
- worker-three reach within five percentage points of control.

Passing opens a separately frozen nested calibration cross-fit; the threshold observed here is not
a selected deployable threshold. Failure closes scalar confidence abstention for this compact
snapshot scorer and favors a representation/action-abstraction pivot.

## Boundary

D153b cannot save a deployable checkpoint, build first-stage values, read/generate reserved maps
`9,844,200--9,844,215`, integrate Rust, qualify or submit a candidate, change the resident, use YT,
or interact with Arena.
