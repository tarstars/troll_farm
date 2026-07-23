# D138a best-stop +3pp calibration q6 — frozen protocol

Date: 2026-07-22  
Status: frozen after D137 held closure and before any D138 fit

## Isolated hypothesis

D137's task-sequence model makes every block positive and seven/eight families positive for all
four pairs, but its best pair misses 40% strict gains by four of 1,024 tasks at only 68.75% pooled
activity. Keep every D137 model, target, loss, seed, epoch, process, gate, and selector unchanged.

Change only calibration. Instead of activating exactly the training count of tasks with a positive
selected-winner maximum, activate that count plus `round(0.03 * training_tasks)`: 23 extra tasks in
each 768-task fold and 31 in the 1,024-task full fit. This fixed three-point guardband is frozen as
a single test, not selected from a threshold grid. It remains far below the 85% activity ceiling.

Repeat the four D133 leave-one-block-out folds and require all unchanged gates, including every
block's 10%--85% activity range. Retain family-floor-first selection and two byte-identical complete
runs. Only an eligible reproducible pair may be fit on all D133 and scored on consumed D126 with
the unchanged veto. D126 cannot tune or select; untouched final seeds remain closed unless the
veto passes.

D138 collects no maps and cannot integrate Rust, submit, mutate the resident, or interact with
TestSession/Arena.
