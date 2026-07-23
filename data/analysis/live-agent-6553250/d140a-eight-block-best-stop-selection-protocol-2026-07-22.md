# D140a eight-block best-stop selection — conditional frozen protocol

Date: 2026-07-22  
Status: frozen while D139 is running, before any D139 outcome or D140 fit is observed

## Hypothesis

D138 proves activity calibration transfers but four-block selection does not predict D126 value.
Test evidence scale only. Conditional on a complete D139 pass, retain D138 exactly:

- D119 `379 -> 16 -> 1` ranker, seeds `13401--13404`, temperature-10 soft proposal loss, 80 epochs;
- D137 `84 -> 8 -> 1` task-sequence gate, seeds `13701--13704`, equal soft-stop and one-best-stop
  losses, 80 epochs;
- D138 calibration at exact positive-stop tasks plus three percentage points; and
- 6,786 total parameters and first-positive runtime.

Use D133 blocks 0--3 and D139 blocks 4--7 as eight independent 16-map blocks (2,048 tasks). For
each pair, train eight times on seven blocks and evaluate the excluded block. Every task is scored
out of fit once.

## Selection and execution

Use D138's unchanged eligibility gates: pooled mean at least `+2`, strict at least 40%, every block
nonnegative, pooled family floor at least `-3`, at least six positive families, directional safety,
pooled and per-block activity 10%--85%, crop no lower than control, and worker-three within five
points. Select by family floor, worst block, mean, strict, lower activity, then lower seed.

To keep eight-block memory bounded, the parent loads each seven-block training tensor and held panel
once. Four forked workers inherit this read-only evidence copy-on-write and train one seed pair each,
with one PyTorch thread. Workers may not mutate corpus/dataset tensors; results are sorted by seed and
contain no process timing. Abort on excessive memory rather than swap-thrashing. Require a second
complete selection run to match byte-for-byte.

## Decision

D139 failure means no D140 fit. An eligible exact selection permits one all-eight-block fit and the
unchanged consumed-D126 veto. D126 cannot tune or rescue. Only a veto pass opens a separately frozen
untouched validation on seeds `9,843,800--9,843,815`.

D140 cannot collect maps, integrate Rust, submit, mutate the resident, or interact with
TestSession/Arena.
