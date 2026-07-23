# D150a joint-population value-support audit — frozen protocol

Date: 2026-07-23  
Status: frozen after D149b closure, before joining population returns to candidate actions

## Question

D149a/b show that a single hard argmax label from each 64-schedule population is not learnable.
Determine whether D148 already contains enough repeated action support to replace one-hot imitation
with return/near-tie supervision, without collecting maps or touching the reserved panel.

For every replayed candidate group, join deterministic proposal slots to D148 population terminals:

- before/at the first selected action, the replay is still on the control path; join population
  rows with exactly two executed interventions whose first boundary equals this group boundary and
  aggregate terminal margin by first slot;
- after the selected first action, join only rows with that exact first boundary and slot, then
  whose executed second boundary equals this group boundary, and aggregate terminal margin by
  second slot; and
- never treat a different first action's second state as interchangeable.

Audit distinct observed legal actions, episodes per action, max/mean return, exact selected-action
support, ties, and actions within five margin points of the observed group maximum. Unknown,
control, nonexecuted, one-intervention-only, or state-mismatched slots are not joined support;
unknown joined slots are mechanics errors.

## Frozen sufficiency gates

Mechanics require exact D148b hashes, all 66,560 population rows, all 2,508 candidate groups, all
909 selected manifests, legal-slot subset joins, and zero unknown/state-path matches.

Existing evidence is sufficient for a value-target follow-up only if:

- every one of the 776 selected first/second action labels is observed in its corresponding return
  join;
- at least 75% of the 388 selected-first groups observe four or more distinct first actions;
- at least 50% of the 388 selected-second groups observe two or more distinct conditional second
  actions;
- median legal-action coverage is at least 25% at selected-first groups and 10% at selected-second
  groups;
- there are at least 4,000 joined first-action episodes and 800 exactly conditioned second-action
  episodes across selected action groups; and
- at least 20% of selected action groups contain a nonselected action within five margin points of
  the observed maximum, demonstrating that a near-tie target actually differs from one-hot labels.

If all pass, freeze a value/near-tie learner on this corpus. If first support passes but conditional
second support fails, collect broader second-state counterfactual replays while reusing the existing
population outcomes where exact paths match. If both fail, redesign the population allocation
before further fitting.

D150a is read-only analysis. It cannot fit a model, read/generate reserved maps, integrate Rust,
qualify or submit a candidate, change the resident, or interact with Arena.
