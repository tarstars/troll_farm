# D142a shared-ranker dual-gate selection — frozen protocol

Date: 2026-07-22  
Status: frozen after D141 closure and before any D142 fit

## Hypothesis

D140's root-weighted hard-stop gate and D141's equal-task/class-balanced gate are complementary.
The former has high raw wait recall and favors the D133 half; the latter restores positive-task
recall, makes all pooled families and blocks positive, and favors D139 for the closest seed. They
use an identical ranker for each seed.

Retain one unchanged D119 ranker and train both frozen gates over its winner contexts:

- gate R uses D137's temperature-10 soft task-choice loss plus flattened root-weighted hard BCE;
- gate T uses the same soft loss plus D141's equal-task, within-positive-task class-balanced hard
  BCE; and
- runtime gate evidence is the exact arithmetic mean `(R + T) / 2` before calibration.

Reset each gate to the same frozen gate seed before training and give it the same epoch/batch order
as its source experiment. For every held block and seed pair, gate R plus the shared ranker must
reproduce the corresponding D140 model hash exactly, and gate T plus the shared ranker must
reproduce the corresponding D141 model hash exactly. A mismatch aborts before policy scoring.

The shared ranker plus two 689-parameter gates has 7,475 parameters. Keep ranker/gate epochs,
temperature, seeds, +3pp training-count calibration, first-positive runtime, and every data or
policy gate unchanged.

## Selection and execution

Use the same eight D133/D139 blocks and leave-one-block-out selection. The parent loads each
seven-block fold once; four one-thread fork workers train the four seed pairs. Use D140's unchanged
eligibility gates and family-floor-first selector. Require two complete selection artifacts to
match byte-for-byte and abort rather than swap-thrash.

An eligible exact repeat permits one all-eight-block dual-gate fit and the unchanged consumed-D126
veto. D126 cannot tune, select, change the 50/50 mixture, recalibrate, or rescue. Only a complete
veto pass opens a separately frozen validation on untouched seeds `9,843,800--9,843,815`.

D142 cannot collect maps, integrate Rust, submit, mutate the resident, or interact with
TestSession/Arena.
