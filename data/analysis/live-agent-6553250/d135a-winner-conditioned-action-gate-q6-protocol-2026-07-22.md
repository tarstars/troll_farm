# D135a winner-conditioned action gate q6 — frozen protocol

Date: 2026-07-22  
Status: frozen after D134's consumed-panel veto failure and before any D135 fit

## Isolated hypothesis

D134 validates independent-block selection but the unchanged D119 controller fails D126 at
`+1.020`, four positive families, and 89.06% activity. Its gate sees only 64 root-state features
and is trained on whether the *oracle-best* proposal is positive. At runtime, however, the ranker
may choose a different proposal. The gate cannot see that winner or its ranking confidence.

Retain D119's proposal ranker exactly: `379 -> 16 -> 1`, temperature-10 soft targets, Adam
`1e-3`, weight decay `1e-4`, batches of 128, 80 epochs, deterministic shuffles, and one PyTorch
thread. For direct comparison use the same ranker seeds `13401--13404` as D134. Freeze each fitted
ranker before training the new gate.

Replace only the state gate with an `84 -> 8 -> 1` ReLU gate. Its inputs are:

- the unchanged 64 state features;
- the 16-dimensional ReLU hidden representation of the proposal currently ranked first; and
- winner logit, winner-minus-runner-up margin, winner-minus-logsumexp confidence, and valid
  proposal count divided by 26.

Train the gate for 80 epochs with the unchanged unweighted root BCE, Adam, weight decay, and batch
size. Its target is whether the *ranker's selected winner* has strictly positive exact advantage,
not whether some oracle proposal is positive. Gate seeds are `13501--13504`, paired in order with
ranker seeds. Assert the frozen ranker hash is unchanged by gate training. The complete controller
has 6,786 parameters.

## Calibration and transfer selection

Calibrate the gate only on each three-block training fold by descending per-task maximum logits.
Use fixed target activity 80%, not a searched grid. This is a prospective 5-point guard band:
D134's D133 held blocks reached as high as 89.45% from an 84% fit target, so fitting at the
admission ceiling left no out-of-block sampling margin. This choice uses D133 transfer evidence;
D126 cannot choose or tune it.

Repeat D134's four leave-one-block-out folds and policy gates. Additionally require every held
block, not merely the pooled result, to remain between 10% and 85% activity. Select eligible pairs
lexicographically by worst block mean, pooled family floor, pooled mean, strict rate, lower pooled
activity, then lower ranker seed. Execute four seed pairs concurrently in isolated processes within
each fold; every process uses one PyTorch thread. Process order and timing are absent from results.

Require a second complete selection run to reproduce the full JSON byte-for-byte.

## Full fit and decision

Only an exact repeat with an eligible pair permits one all-four-block fit. Recalibrate to 80% on
D133 and score the frozen controller on consumed D126 seeds `9,843,780--9,843,795` as veto only.
Use D134's unchanged veto gates: mean at least `+2`, strict at least 40%, both folds nonnegative,
family floor at least `-3`, at least six positive families, directional score safety, 10%--85%
activity, crop no lower than control, and worker-three reach within five points.

- No held-block candidate or failed repeat: close this action-aware gate.
- D126 veto failure: close without tuning on D126.
- Full pass: save an internal checkpoint and open one separately frozen final validation on
  untouched seeds `9,843,800--9,843,815`.

D135 collects no maps and cannot integrate Rust, submit, mutate the stable resident, touch
TestSession/Arena, or reinterpret D126 as selection evidence.
