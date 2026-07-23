# D135a winner-conditioned action gate q6 — result

Date: 2026-07-22  
Decision: **close D135 on consumed-panel veto**

## Execution and transfer selection

The 6,786-parameter controller retains D119's ranker and adds only a small winner-conditioned
gate. Four isolated one-thread workers raised aggregate CPU use to 408%--411%. Complete selection
runs took 99.55 and 101.30 seconds; their 110 KB JSON artifacts are byte-identical (SHA
`55d9f81d...`). The paired ranker/gate seeds 13404/13504 are the sole eligible candidate:

- pooled mean `+3.596`, strict gains 44.14%, and all eight families positive;
- block means `+3.906`, `+2.715`, `+3.082`, and `+4.680`;
- family floor `+0.141`; and
- block activities 84.77%, 79.69%, 72.27%, and 78.91%, all inside the new guardrail.

Thus winner conditioning improves D133 held-block robustness and fixes the D134 activity-boundary
problem. The selected proposal is truly positive on only 15.88%--19.97% of held roots; the raw
gate's zero-threshold balanced accuracy is just 53.10%--53.69%, so much of the policy result still
comes from per-task calibration and first-positive temporal composition.

## Full fit and D126 veto

The full fit calibrates exactly 819/1,024 D133 tasks (79.98%) and has model hash `a76c4e6d...`.
On consumed D126 it obtains:

- mean `+0.355` and strict gains 39.45% (both fail);
- parity folds `+1.352` and `-0.641` (fail);
- two positive families and family floor `-2.031` (breadth fails, floor passes);
- own delta `+0.113`, opponent delta `-0.242`, 100% crop, and workforce parity (pass); and
- activity 84.77% (passes, unlike D134).

The selected winner is positive on 14.39% of D126 roots. At zero threshold the gate recalls 97.19%
of nonpositive winners but only 12.09% of positive winners; balanced accuracy is 54.64%. Proposal
regret is 22.52, within the broad held-block range 19.73--23.56 rather than a singular mechanics
failure.

Five veto gates fail. No checkpoint or final-validation authorization is emitted, and there is no
platform mutation. Result SHA is `b15ce182...`; lock SHA is `6647730a...`.

## Next diagnostic

D135 changes both seed selection (13403 to 13404) and gate semantics, so its final failure does not
yet distinguish an action-gate abstraction failure from another selector miss. Refit all four
frozen D135 pairs on all D133 blocks and score them on consumed D126 in a retrospective-only audit.
That audit cannot qualify a controller. Compare held selection order with D126 value, activity,
family breadth, winner-positive prevalence, and gate discrimination before choosing D136's model
change. Final seeds remain closed.
