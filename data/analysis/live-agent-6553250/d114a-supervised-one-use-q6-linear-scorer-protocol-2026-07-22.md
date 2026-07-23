# D114a supervised one-use q6 linear scorer — frozen protocol

Date: 2026-07-22  
Status: frozen before D114 train, validation, or held outcomes exist

## Hypothesis and deployable class

D113's exact one-use teacher gains `+36.766` across all tasks and yields 11,980 backward-DP
targets with both act-now and wait supervision. D110/D111 failed because they selected complete
linear policies from sparse terminal outcomes, not because the 379-feature linear class lacked
proposal support. D114 tests the same deployable one-use class with dense supervised credit.

The runtime score is one dot product between 379 control-relative q6 features and 379 frozen
weights. At each baseline root, select the highest positive proposal score; otherwise wait. After
the first selected proposal, authority is exhausted and D40 finishes the game. Opponent-family
identity, terminal information, runtime simulation, recurrence, and more than one intervention are
excluded.

## Fresh datasets

- train: untouched seeds `9,843,300--9,843,315`, 16 maps / 256 tasks;
- validation: untouched seeds `9,843,400--9,843,407`, 8 maps / 128 tasks;
- conditional held: untouched seeds `9,843,500--9,843,515`, 16 maps / 256 tasks.

All use both seats and all eight opponents. Search found no prior artifact using these ranges.
Collect complete train and validation continuation matrices once with the unchanged D112 snapshot
collector and 20 workers. D112 already establishes three-way full-panel byte equality; each new
collection must clear 12 arms/s and all exact mechanics checks.

## Frozen fit and validation selection

Generate backward act-now-versus-wait targets independently inside each task. Give every root
equal total regression weight (`1 / proposals_at_root`). Fit weighted ridge regressions on raw 379
action differences. Feature zero is the deployable intercept and is not regularized.

The fixed candidate grid is:

- target clipping at `[-50,+50]` or `[-100,+100]` score points;
- ridge alpha in `{1, 10, 100, 1000}`; and
- post-fit abstention offset in `{0, 2, 5, 10, 15, 20}`, subtracted from weight zero.

Round every candidate to eight decimals before validation. No architecture, feature, sample weight,
clip, alpha, offset, or candidate is changed after validation outcomes are known.

Evaluate each candidate exactly offline: follow baseline roots in order and take its first positive
argmax; the corresponding one-deviation row is its exact terminal outcome. A validation candidate
is admissible only if mean gain is at least `+2`, strict gain at least 30%, both interleaved-map
fold means nonnegative, worst family at least `-5`, at least five families positive, own-score gain
nonnegative or opponent-score delta nonpositive, activity 10%--85%, crop creation 100%, and
worker-three reach within five percentage points of D40.

If none qualify, stop without held execution. Otherwise select one lexicographically by highest
minimum fold mean, worst family, overall mean, strict rate, then lowest activity, then fixed grid
order. Refit only its clip/alpha on combined train+validation labels, apply the same absolute
offset, round to eight decimals, and emit it as D107-compatible `one_00`; all other controller
weights are zero. No post-refit calibration or selection is allowed.

## Repeated held qualification

Run exact zero plus frozen `one_00` on the 256 held tasks, then repeat from a new process and
require byte-identical controller and baseline matrices. Require complete grids, exact zero
reproduction, paired reward identity below `1e-4`, exact one-use accounting, finite values, and zero
mechanical failures.

Held value/safety requires mean gain at least `+2`, strict gain at least 40%, worst family at least
`-3`, at least six positive families, own score nonnegative or opponent score nonpositive,
activity 10%--85%, crop creation 100%, and worker-three reach within five percentage points of
D40.

## Decision

- **Collection/fit mechanics failure:** repair only; do not interpret value.
- **No validation admission:** close supervised linear q6 without opening held maps.
- **Held failure:** close this exact linear fit; do not tune on held outcomes.
- **Full held pass:** open deployable reconstruction in the agent and a final new-map confirmation;
  D114 itself is not automatic submission authority.

No branch authorizes TestSession, Arena, submission, or resident mutation.
