# D137a task-sequence best-stop gate q6 — frozen protocol

Date: 2026-07-22  
Status: frozen after D136 interpretation and before any D137 fit

## Isolated model hypothesis

D135 predicts the sign of every selected winner independently, while runtime scans all boundaries
and executes the first positive gate. D136 shows weak root classification and unstable task value.
Keep D135's 6,786-parameter architecture and D119 ranker exactly. Change only the gate target and
loss from independent winner-sign BCE to task-sequence stopping value.

For each supported training task, compute the frozen ranker's selected winner and exact advantage
at every boundary, then add an explicit wait candidate with value zero. Build a temperature-10 soft
target over all boundary values plus wait. Also mark exactly one hard stop target: the earliest
maximum-value boundary when that maximum is strictly positive; otherwise mark no root and wait.

Train the same `84 -> 8 -> 1` gate for 80 epochs in task batches of 128 with the same Adam
`1e-3`, weight decay `1e-4`, deterministic shuffles, and one PyTorch thread. Minimize equal-weight:

1. soft cross-entropy over boundary logits plus a fixed zero wait logit; and
2. root BCE for the one-best-stop labels (all other roots are negative).

The fixed wait logit anchors absolute act/wait scale; the soft term preserves advantage magnitude;
the hard term suppresses earlier and lower positive roots. Ranker seeds remain `13401--13404` for
direct comparison, paired with new gate seeds `13701--13704`. Assert ranker hashes do not change.

## Calibration and block transfer

Do not impose an arbitrary activity target. On each three-block fit, count tasks whose selected
winner sequence has a strictly positive maximum. Calibrate the gate's per-task maximum to activate
exactly that many of all training tasks. This count is derived only from training teacher evidence;
unsupported tasks remain wait.

Repeat D135's four leave-one-block-out folds, exact policy gates, and per-block 10%--85% activity
guardrail. D136 found held mean uninformative (`r=0.004`) and held family floor more aligned with
transfer (`r=0.684`), so eligible pairs are selected prospectively by highest family floor first,
then worst block, pooled mean, strict rate, lower activity, and lower ranker seed. This diagnostic
motivates the rule but D126 values cannot enter D137 fitting or eligibility.

Run the four pairs concurrently in isolated one-thread processes within each fold. Require a second
complete selection run to reproduce every byte.

## Full fit and authority

Only a reproducible eligible pair permits an all-D133 fit and count-calibrated gate. Score consumed
D126 with the unchanged veto gates. D126 can reject only; it cannot select another pair or tune the
objective. A pass opens one separately frozen validation on untouched seeds
`9,843,800--9,843,815`; a failure closes D137.

D137 collects no maps and cannot integrate Rust, submit, mutate the stable resident, or interact
with TestSession/Arena.
