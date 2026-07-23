# D111a diverse one-use q6 linear lineage — frozen protocol

Date: 2026-07-22  
Status: frozen before any D111 outcome exists

## Hypothesis

D110a closes random one-use selection but leaves a narrow, prospective optimization target. Three
of 64 random 379-weight policies pass its core mean, strict-win, two-fold, and family screens; all
three act on more than 85% of tasks. `one_41` reaches `+2.020`, six positive families, and a
`-2.844` floor, missing admission only by nine active tasks. This suggests that exact q6 proposal
support and one-use authority are sufficient, while the global control threshold is not calibrated.

Test targeted direct policy optimization from scratch. Retain actual parameter vectors, mutate the
shared noncontrol threshold more strongly than proposal-ranking weights, penalize activity outside
the allowed band inside whole-game fitness, and preserve founder diversity. No D110 vector or
four-use outcome is an initializer, parent, label, or target.

## Immutable inputs and implementation

- D110 result: `64333cf8d29743281c25be481b1470c4d817a24dd3d90dd6a7021c51d7f6321b`;
- q6 expert bank: `87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8`;
- frozen D107 runner source:
  `2bd7e3c5628cf048af61082aba848bb6ea6f66d3967e4ee056823679693d0514`;
- release runner: `96030ca2ab75e7b98b74942863b9b4c53124790bf62bf7c6946ab546e3a78547`;
- D110 metric/integrity implementation:
  `52e05c8cc1e1feeace487b6cbeaa321eb79458b3e96425ab41e4bb2f9b7ba513`; and
- D110 population serializer:
  `13cbe478d2d725a25608d1a2e5dd6089a89ca0d1dc9ed4927857228af62d41f5`.

The controller is the exact D107 379-feature linear score with action zero at score zero and at
most one noncontrol batch. Four-use partner rows exist only for runner compatibility and remain
excluded from search, selection, and diagnosis.

## Frozen lineage search

Use NumPy PCG64 seed `11101`, five generations, population 64, `mu=8`, and seven children per
survivor. Generation one has 64 independent Normal(`0`, `0.25`) vectors rounded to eight decimals;
feature zero is overwritten by the 16-level `-0.15` through `-2.40` abstention ladder.

Children are exact parent copies plus independent Gaussian mutation: sigma `0.10` for feature zero
and `0.025` for the other 378 weights. Clip feature zero to `[-3,0]`, other weights to
`[-1.5,1.5]`, and round to eight decimals. There is no crossover, averaging, adaptive sigma,
restart, D110 seeding, opponent identity, terminal input, checkpoint selection, or manual pruning.

Each generation uses four new maps, both seats, and all eight opponents: 64 paired tasks per
policy. Generation `g=0..4` starts at `9,841,000 + 4*g`; parents are reevaluated on every new block.

For each one-use policy calculate:

`fitness = mean_margin + 0.5 * worst_family + 0.25 * p10_margin`

`          + 0.5 * min(0, mean_own_score) - activity_penalty`,

where `activity_penalty = 20 * (max(0, activity-0.85) + max(0, 0.10-activity))` and NumPy's
default linear p10 is used. A policy is eligible only with 100% crops and worker-three reach within
five percentage points of paired D40. Rank eligible policies by fitness, worst family, mean,
distance of activity from 50%, then label. Ineligible policies follow eligible ones.

Retain eight actual policies, but at most two descendants of any founder. Traverse the frozen
ranking and skip a policy when its founder already has two survivors. This must leave at least four
founders; failure to fill eight safe diverse survivors is a mechanics/search failure. Record every
vector hash, lineage edge, population, row matrix, baseline matrix, metric, ranking, and survivor.

## Separate selection

Reevaluate the eight generation-five survivors on untouched seeds `9,841,100--9,841,115`, both
seats and all opponents: 256 tasks each. Analyze two interleaved map folds. A policy is admitted
only under D110's unchanged discovery rule: mean at least `+1.5`, strict improvement at least 30%,
both fold means nonnegative, worst family at least `-5`, five positive families, nonnegative own
score or nonpositive opponent score, 10%--85% activity, 100% crops, and worker-three reach within
five points of D40.

If no survivor is admitted, stop. Otherwise choose the admitted survivor highest in the unchanged
lineage fitness ranking. No earlier generation member or alternate final survivor may be selected.

## Repeated held qualification

Only after selection admission, evaluate exact zero, the frozen one-use champion, and its ignored
four-use compatibility partner on untouched seeds `9,842,000--9,842,031`, both seats and all eight
opponents. Repeat the complete 1,536-row matrix and 512-row baselines from a new process and require
byte identity.

The one-use champion passes only with mean gain at least `+2`, strict improvement at least 40%,
every family at least `-3`, at least six positive families, nonnegative own score or nonpositive
opponent score, 10%--85% activity, 100% crop creation, and worker-three reach within five points of
D40. All source, grid, zero, reward, counter, and failure integrity gates must pass throughout.

## Decision

- **Mechanics/reconstruction failure:** quarantine value and repair only.
- **No selection admission:** close the diverse one-use linear lineage before held evaluation.
- **Held failure:** close this controller and exact optimizer; do not choose another survivor,
  extend generations, change mutation/fitness/diversity, or reuse maps.
- **Full held pass:** open deployable q6-plus-379-weight reconstruction and one entirely new final
  confirmation panel. D111a does not itself authorize submission.

No branch authorizes TestSession, Arena, submission, or resident change.
