# D146a two-intervention schedule-priority audit — frozen protocol

Date: 2026-07-22  
Status: frozen after D145's unsaturated-uniform decision and before scoring any schedule class or
priority subset

## Hypothesis

D145's 57 winning trajectories are concentrated at first boundary zero (46/57) and a one-boundary
gap (42/57). Test whether this observable, outcome-blind schedule structure allocates a fixed
episode budget more efficiently than uniform replica prefixes. Use only the frozen D144 matrix;
this audit runs no new simulation.

Class every double-mode episode using only its precomputed schedule:

1. `early_immediate`: first boundary 0, gap 1;
2. `early_delayed`: first boundary 0, gap greater than 1;
3. `later_immediate`: first boundary greater than 0, gap 1; and
4. `later_delayed`: all remaining schedules.

Within each task, sort by that class order, then first boundary, gap, and replica index. Take the
first 32 or 64 rows. No terminal outcome, action, opponent, or value may enter the priority.
Compare these fixed per-task subsets with D145's equal-budget uniform 32/64 prefixes. Also report
each schedule class's descriptive oracle.

## Frozen gates

The 32-row priority must:

- add at least `+0.5` mean increment over the uniform 32 prefix;
- have strict incremental rate no lower than uniform 32; and
- retain at least six positive opponent families.

The 64-row priority must:

- retain at least 80% of D145's full 111-replica incremental mean;
- have mean increment no lower than uniform 64; and
- have strict incremental rate no lower than uniform 64.

If all pass, scale map breadth at 64 prioritized schedules for a joint two-stage teacher. If only
the 32-row efficiency gates pass, the frozen population supports schedule concentration but not
the exact existing rows; launch one new boundary-concentrated per-task population before scaling.
Otherwise retain uniform deeper search.

D146 cannot qualify a model or consume a new seed, D126/final validation, YT operation, resident
change, submission, TestSession, or Arena action.
