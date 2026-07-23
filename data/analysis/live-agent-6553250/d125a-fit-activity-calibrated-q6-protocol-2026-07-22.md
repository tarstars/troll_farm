# D125a fit-activity-calibrated q6 — frozen protocol

Date: 2026-07-22  
Status: frozen before training-only calibration or fresh validation collection

## Prospective calibration rule

D124 finds a stable D119 gate band whose descriptively feasible policies have 82.03%--84.38% fit
activity. D125 converts that observation into one model-independent rule. Reproduce the unchanged
D119 models for seeds `11901--11904`. For each model, take the maximum gate logit over each fit
task's roots, include unsupported tasks as forced control, and choose the midpoint between the
215th and 216th descending task scores. This activates exactly 215 of 256 fit tasks, the nearest
integer to 84%. Fail on a boundary tie; do not round, scan, or adjust the threshold.

Require unchanged D119 structural gates and D118 fit-policy gates. Among eligible seeds, use the
existing robust fit order: minimum fold, worst family, mean, strict rate, lower activity, then
fixed seed order. Require two complete fit-selection JSON artifacts to be byte-identical before
freezing the selected model hash and calibrated offset.

## Conditional fresh validation

Only exact repeated fit selection opens untouched seeds `9,843,780--9,843,795`: 16 maps, both
seats, all eight opponents, and 256 tasks. Use the unchanged exact D112 collector, fixed expert
bank, and 20 workers. Score exactly the one selected model/offset without refitting or selection.

Because this is policy evaluation rather than teacher fitting, zero-boundary tasks are complete
forced-control outcomes. Require the prescribed 256-task grid, exact arm/root consistency, exact
paired gains and reward identities, finite features, single-intervention accounting, zero
mechanical failures, and at least 12 arms/s. Report support, roots, and arms, but do not gate on
their volume or percentage.

The one fresh policy passes only if it has mean margin at least `+2`, strict gains at least 40%,
both fold means nonnegative, worst family at least `-3`, at least six positive families,
nonnegative own-score change or nonpositive opponent-score change, activity 10%--85%, crop rate no
worse than exact control, and worker-three reach within five percentage points of control.

Mechanical corruption permits collector repair only. A policy-gate failure closes D125 without
tuning on these maps. A full pass may create a checkpoint and opens quantized Rust parity plus a
separate untouched confirmation; it does not authorize Arena, submission, or resident mutation.
