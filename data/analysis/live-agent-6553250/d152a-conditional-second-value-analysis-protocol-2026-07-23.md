# D152a conditional-second value analysis — conditionally frozen protocol

Date: 2026-07-23  
Status: frozen while D151 A/B jobs are running, before downloading or observing any D151 branch
return; conditional on a complete D151 mechanics pass

## Interpretation

For each of the 909 selected-first conditional states, slot zero is the exact first-action-only
continuation. Rank all noncontrol second actions by terminal margin, own score, lower opponent score,
then lower stable slot. Select a noncontrol action only when its margin strictly exceeds slot zero;
otherwise retain slot zero. Define each action's exact value as its terminal margin minus slot-zero
margin and define near-optimal actions as within five margin points of the best combined value.

Report separately for all 909 states and the 388 D148-active targets:

- combined-oracle gain over first-only control, strict rate, own/opponent decomposition, crop and
  worker-three safety;
- four consecutive 16-map blocks and all eight opponent families;
- original D148 selected-second exact-best and within-five rates;
- positive/negative/zero action-value counts, value dispersion, number of positive and near-optimal
  actions per state, and nonselected near-tie prevalence; and
- increment of the new exact conditional oracle over D148's originally selected sequence and over
  its exact-one-use comparator.

No threshold, tie rule, subgroup, or safety rule may change after return exposure.

## Frozen signal and target gates

On the 388 active targets, the combined conditional-second oracle must:

- add at least `+5.0` mean margin over first-only continuation;
- strictly improve at least 50% of tasks;
- have positive mean gain in all four 16-map blocks;
- have at least six positive opponent families and a nonnegative family floor;
- introduce zero crop failures relative to first-only; and
- retain worker-three reach within five percentage points of first-only.

Across all 909 states it must add at least `+2.0` mean and strictly improve at least 25% of tasks.
For value-target richness, at least 20% of states must contain a nonselected action within five
points of the best, at least 20% must contain two or more positive noncontrol actions, and exact
noncontrol values must have population standard deviation at least five margin points.

## Decision

If mechanics, signal, safety, and target richness all pass, write exact second-action value labels
and open a separately frozen grouped cross-fit. Combine them later with D150's rich first-stage
population values; do not revert to one-hot selected-pair labels. Failure closes conditional-second
distillation and redirects effort to population allocation/representation.

D152 cannot fit a model, read/generate reserved maps `9,844,200--9,844,215`, integrate Rust,
qualify or submit a candidate, change the resident, or interact with Arena.
