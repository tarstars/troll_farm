# D143a first-positive-aligned best-stop selection — frozen protocol

Date: 2026-07-22  
Status: frozen after D142b closure and before any D143 fit

## Hypothesis

D137--D142 train a sequence gate whose hard target contains only one best positive root per task,
but policy execution takes the first root above a calibrated threshold. Earlier roots with positive
selected-winner teacher value are therefore labeled hard-negative even though executing them would
count as a strict improvement. Calibration can expose those contradictory labels.

Retain D141's single unchanged D119 ranker and `84 -> 8 -> 1` gate, 6,786 parameters, temperature-10
soft best-stop cross entropy, 80+80 epochs, four seed pairs, eight blocks, +3pp training-count
calibration, first-positive runtime, policy gates, and selector. Change only hard targets and their
task-balanced reduction:

- every valid root with selected-winner value greater than zero is hard-positive;
- every other valid root is hard-negative;
- a task containing both classes assigns half its hard-loss mass to the mean positive loss and half
  to the mean negative loss;
- a single-class task uses that class mean; and
- tasks are averaged equally regardless of root or class counts.

The number of tasks containing at least one positive root is identical to D137's positive-best-stop
task count, so D138's exact count plus three percentage points remains unchanged.

## Selection and decision

Use the same parent-loaded, four-worker, eight-fold selection and require a byte-identical second
run. Apply D140's unchanged gates and family-floor-first selector. An eligible repeat permits one
all-eight-block fit and the unchanged consumed-D126 veto. D126 cannot tune, select, recalibrate, or
rescue. Only a complete veto pass opens separately frozen untouched validation.

D143 cannot collect maps, integrate Rust, submit, mutate the resident, or interact with
TestSession/Arena.
