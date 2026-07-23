# D17 resident residual precision distillation — development protocol (2026-07-20)

## Hypothesis

D16 found a distributed but asymmetric one-intervention signal: 17.88% of sampled alternatives
improved terminal margin, while an unfiltered alternative remained harmful on average.  A compact
supervised residual scorer can learn a conservative subset of these exceptions from deployable
decision features.  `KEEP` remains the default; the scorer is an abstaining guard, not a resident
replacement.

## Frozen corpus

Generate exact one-intervention labels with the D16 runner and sampling procedure, using 12
uniform reservoir samples per scenario and map-disjoint blocks:

| Split | Scenario IDs | Map seeds | Scenarios | Labels |
|---|---|---|---:|---:|
| train | 372,000--373,919 | 31,000--31,159 | 1,920 | 23,040 |
| validation | 384,000--384,479 | 32,000--32,039 | 480 | 5,760 |
| locked test | 396,000--396,479 | 33,000--33,039 | 480 | 5,760 |

Every split contains both seats and all six development opponents for every map.  Clone fidelity
must pass in every scenario.  D16 maps are used only to design this protocol and are not included
in any D17 split.

## Deployable features

Use only information available at the live resident decision: turn and unit ordinal/count; active
worker stats, capacity and inventory; own/opponent public inventories and scores; wood edge and
plant count; local plant type/health/fruits; home/iron adjacency; intent age; legal-action count;
resident, previous, and other-worker action intents; and the proposed alternative plane.

Exclude scenario/map identity, opponent-policy identity, absolute terminal outcomes, continuation
latency, candidate/reservoir index, and all post-decision fields.  Exclude absolute `(x,y)` so the
first model cannot memorize map geometry.  Continuous features use fixed game-semantic scales,
not test-derived normalization.  Categorical verbs, intent planes, local plant type, and proposed
plane are one-hot encoded.

## Frozen model search

Train the following compact scorers with seeds 1701, 1702, and 1703:

1. a linear binary scorer for `margin_advantage > 0`;
2. a two-hidden-layer binary MLP with widths 24 and 12;
3. a two-hidden-layer value MLP with widths 24 and 12 and a clipped Smooth-L1 target.

Binary loss balances the positive class and weights harmful negatives by capped loss magnitude.
The value target clips margin advantage to `[-32,+32]` before scaling.  Also evaluate the
three-seed mean score for each model family.  Architecture, optimizer schedule, feature schema,
seeds, and epochs are fixed before reading validation results.

For each scorer, validation thresholds are its score quantiles corresponding to selection rates
of 0.5%, 1%, 2%, 4%, 8%, and 12%.  A threshold is validation-eligible only when it:

- selects at least 72/5,760 labels and at most 12%;
- has at least 70% positive-label precision and at least +2.0 conditional mean margin advantage;
- creates no new catastrophe;
- has positive selections on at least 12/40 maps, against at least 4/6 opponents, and in both
  active-worker roles;
- has a positive lower bound of the deterministic 10,000-resample map-clustered 95% bootstrap CI
  for mean contribution (unselected rows contribute zero).

Choose exactly one model/threshold by maximum validation CI lower bound, then conditional mean,
then number selected, then smaller parameter count and lexical model name.  Do not adapt after
opening the test split.

## Locked-test gate

The selected recipe authorizes an exact full-trajectory policy prototype only if the locked test:

1. selects at least 72 labels and no more than 12%;
2. reaches at least 65% positive precision and +1.0 conditional mean advantage;
3. has a strictly positive lower bound for the same map-clustered contribution CI;
4. creates no new catastrophe;
5. has positive selections on at least 12 maps, against at least 4 opponents, and in both roles;
6. has at most 10,000 parameters and an estimated int8 payload of at most 10,000 bytes.

Passing authorizes a separate exact policy-trajectory experiment only.  It does not authorize
source integration, candidate promotion, submission, or Arena activity.  Failure closes this
feature/model formulation without threshold repair on the locked block.

## Planned outputs

- `d17-resident-residual-mc-train-scenarios372000-373919.tsv`;
- `d17-resident-residual-mc-validation-scenarios384000-384479.tsv`;
- `d17-resident-residual-mc-test-scenarios396000-396479.tsv`;
- `d17-resident-residual-precision-distillation-2026-07-20.json`;
- `d17-resident-residual-precision-distillation-result-2026-07-20.md`.
