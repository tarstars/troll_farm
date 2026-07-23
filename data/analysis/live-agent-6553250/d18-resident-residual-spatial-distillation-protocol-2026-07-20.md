# D18 resident residual spatial distillation — development protocol (2026-07-20)

## Hypothesis

D17's compact scalar scorer retained a weak positive ranking signal but confused beneficial actions
with harmful lookalikes: the best 2% slice had +1.98 mean advantage and a positive map-clustered
CI, but only 48.28% precision.  Resource layout, route distance, and nearby competition are the
most plausible missing variables.  Adding exact spatial state should improve precision without
abandoning the small residual-policy budget.

## Frozen data boundaries

- Training labels: D17 train plus D17 validation, 28,800 rows on 200 already-open maps
  (31,000--31,159 and 32,000--32,039).
- Fresh validation labels: scenario IDs 408,000--408,479, maps 34,000--34,039, both seats and all
  six opponents, with 12 D16-style reservoir samples per scenario (5,760 rows).
- Prospective locked test: scenario IDs 420,000--420,479, maps 35,000--35,039.  Do not generate,
  read, or analyze this block unless the fresh-validation gate passes.
- D17's unopened maps 33,000--33,039 remain sealed and excluded from D18.

Replay every labeled scenario under all-`KEEP` and reconstruct the exact `137×11×22` uint8
observation at each row's recorded global alternative-candidate index.  Require candidate-count,
action, active-cell, action-plane, legal-count, and terminal-scenario agreement, with every row
captured exactly once.

## Frozen representations and models

Train each family with seeds 1801 and 1802:

1. **geometry binary/value MLP:** D17's 116 deployable features plus fixed path-distance and
   resource-count summaries computed from the observation.  Targets include own/enemy shack
   access, iron access, empty wet cells, other own workers, opponent workers, each plant kind, and
   each ripe plant kind.  For every target report reachable count, minimum walkable distance, and
   counts within distance 3 and 6.
2. **tiny spatial binary/value scorer:** a width-4 convolutional stem followed by width-4
   dilation-2 and dilation-4 residual layers.  Concatenate active-cell, valid-map mean, and
   valid-map maximum embeddings, then emit 13 action-plane scores.  Score only the row's proposed
   plane.

Binary and clipped-value losses, class/cost weighting, and fixed semantic scalar scaling remain
as in D17.  Geometry MLPs train for 64 epochs; spatial scorers train for 20 epochs.  Use no
opponent identity, scenario/map identity, terminal outcome, absolute coordinate, or label-derived
normalization.  Every individual model must have at most 10,000 parameters/int8 bytes; no ensemble
is eligible for deployment.

## Frozen validation selection

For each of the eight individual scorers, evaluate score quantiles corresponding to 0.5%, 1%, 2%,
4%, and 8% selection.  A recipe passes fresh validation only if it:

- selects at least 72/5,760 labels and at most 8%;
- has at least 70% positive precision and at least +2.0 conditional mean margin advantage;
- has a positive lower bound in a deterministic 10,000-resample map-clustered 95% bootstrap CI
  for mean contribution, with unselected labels contributing zero;
- creates no new catastrophe;
- has positive selections on at least 12/40 maps, against at least 4/6 opponents, and in both
  worker roles;
- uses at most 10,000 parameters and estimated int8 bytes.

Choose one passing recipe by maximum map-CI lower bound, then conditional mean, selected count,
smaller parameter count, and lexical name.  Passing authorizes generation and one-time evaluation
of the prospective locked block under the unchanged D17 locked-test gate (at least 72 selections,
at most 8%, precision at least 65%, conditional mean at least +1, positive map-CI lower bound,
no catastrophe, 12 maps, 4 opponents, both roles, and the same size limit).

Failure closes both spatial formulations at this observation horizon; do not repair a threshold
on validation.  Passing either validation or locked test still does not authorize source
integration, a candidate, submission, or Arena activity.

## Planned outputs

- exact observation `.npy` files and integrity metadata for each opened label block;
- `d18-resident-residual-mc-validation-scenarios408000-408479.tsv`;
- `d18-resident-residual-spatial-distillation-validation-2026-07-20.json`;
- `d18-resident-residual-spatial-distillation-result-2026-07-20.md`;
- prospective locked-test artifacts only after a validation pass.
