# D149a joint two-stage structural cross-fit — frozen protocol

Date: 2026-07-23  
Status: frozen after D148b transfer passed and the D149 structural dataset was mechanically
summarized, before any D149 model fit

## Hypothesis

D148 proves that a second q6 intervention adds robust fresh-map value beyond the exact one-use
oracle. Test whether the replayed state/action interface contains enough transferable information
to imitate the selected joint trajectories with a submission-sized controller.

Use the already implemented 6,786-parameter winner-conditioned architecture:

- a shared `379 -> 16 -> 1` action ranker chooses one noncontrol proposal;
- the ranker's 16-dimensional winner embedding, four confidence values, and 64 state features feed
  an `84 -> 8 -> 1` act/wait gate;
- the ranker trains only on the two chosen action groups of active trajectories;
- the gate trains on every on-policy group, with equal act/wait mass and inverse per-task group
  count; and
- inference uses the fixed zero logit boundary. No threshold search or outcome calibration is
  allowed in D149a.

An inactive pair is on-policy only through and including its rejected first action. Exclude its
post-action second state. This yields the mechanically fixed dataset: 909 target tasks (388 active,
521 inactive), 1,654 included groups, 854 excluded off-policy groups, 776 rank/act groups, 878 wait
groups, and eight map folds with 91--125 tasks. The mean random top-1 rate on ranked groups is
6.4296% (6.5388% first, 6.3205% second).

## Frozen training and selection

Use rank/gate seed pairs `(14901,14951)`, `(14902,14952)`, `(14903,14953)`, and
`(14904,14954)`. Retain the implemented Adam settings, 60 rank epochs, 80 gate epochs, batch size
128, learning rate `1e-3`, and weight decay `1e-4`.

For each pair, perform eight leave-one-map-fold-out fits: train on seven 8-map folds and score the
excluded fold. Thus every structural label is evaluated out of fit exactly once. Run ten forked
workers with two PyTorch threads each on the 20-CPU host; parent arrays are read-only. Sort outputs
deterministically and require a second complete selection artifact to match byte-for-byte.

Aggregate held predictions by their natural group/task counts. A seed pair is eligible only if:

- overall exact chosen-action accuracy is at least 15%, at least 12% independently at first and
  second action stages, and at least 2.0 times its exact random-choice baseline;
- gate balanced accuracy is at least 58%, with both act recall and wait recall at least 50%;
- every fold has gate balanced accuracy at least 50%;
- at least seven of eight folds beat their own random-choice action baseline;
- at least 8% of active first groups and 8% of active second groups jointly predict act and the
  exact chosen proposal;
- at least 1.5% of active tasks reproduce both ranked actions with both act decisions; and
- at least 25% of inactive tasks produce no false act over their complete included on-policy
  prefix.

Exact full logged-trajectory reproduction (including every intermediate wait) is descriptive; it
is an especially pessimistic metric because any alternative proposal makes later logged state
counterfactual. All metrics must be finite and every fold must preserve its exact task/group set.

Select eligible pairs by, in order: worst-fold gate balanced accuracy, weaker of first/second rank
lift, overall rank accuracy, overall gate balanced accuracy, both-action exact rate, then lower
rank seed.

## Decision boundary

After a byte-identical eligible selection, fit the selected pair twice on all eight folds and
require identical canonical model hashes, exactly 6,786 parameters, and finite outputs. Save one
checkpoint. This may open a separately frozen prospective D150 evaluation on the untouched maps
`9,844,200--9,844,215`.

Failure closes this exact supervised architecture or identifies one predeclared failing component
for a new hypothesis. D149 cannot read or generate the reserved maps, integrate Rust, qualify or
submit a candidate, change the resident, or interact with Arena.
