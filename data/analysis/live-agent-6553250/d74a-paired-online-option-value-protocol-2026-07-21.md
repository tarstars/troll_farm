# D74a paired online option-value audit — frozen protocol (2026-07-21)

## Question

D73 learns broad suppression but cannot price its displaced own production. At the exact same
observable boundary, do paired terminal continuations provide broad option advantage, and can a
fixed low-capacity ranker recover enough of it across disjoint maps to justify a prospective
closed-loop selector?

D74a is a causal local label/learnability audit. It does not reuse D73 weights, run PPO, select a
complete policy, open confirmation, construct a candidate, call TestSession, or touch Arena.

## Frozen outcome-blind state manifest

Run exact balanced ordinary behavior on official seeds 9,812,000--9,812,031, both seats, and all
eight unchanged D40 opponent modes: 512 tasks. At every D71 72-feature boundary, increment a
per-task decision ordinal. Eligible states have all four ordinary options legal.

Partition maps before outcomes:

- discovery: seeds 9,812,000--9,812,015;
- validation: seeds 9,812,016--9,812,031.

Stratify eligible states by partition, opponent, seat, and phase (`turn <100`, `100--199`,
`>=200`). Within each stratum retain up to six rows with the smallest SHA-256 of
`(map_seed, seat, opponent_index, decision_ordinal)`. Stable identity breaks ties. Preserve exact
task identity, ordinal, turn, phase, 72 float32 features, legal mask, and a feature-bit hash. This
yields at most 576 states. Selection must not inspect terminal scores, actions after the boundary,
or any deviated outcome.

Require at least 480 unique states, at least 240 in each partition, every opponent/seat/phase in
both partitions, finite features, exact ordinary-source zeros, and byte-stable manifest generation.

## Exact paired continuations

For each manifest state, reconstruct its map/seat/opponent from turn zero and replay exact balanced
batch options through the recorded ordinal. Require exact turn, legal mask, and feature-bit hash.
From that state run four independent continuations:

1. take one of `balanced`, `harvest`, `renew`, or `fell` exactly once; then
2. return to exact balanced at every later boundary through terminal.

Record terminal own/opponent score, margin, workers, trains, crops, own-crop harvests,
reinvestments, invalidations, integrity counters, action hash, and state hash. Run the complete
matrix twice with 20 threads and require byte identity. Any replay, legality, finite, command,
provenance, deposit, action-count, or reward-identity failure quarantines value.

For each state define the crop-safe oracle as maximum terminal margin, breaking ties by higher own
score, lower opponent score, then lower action index. Because every selected state already has an
own crop, all four continuations must retain positive cumulative crop creation.

## Frozen label headroom gates

All must pass:

- at least 480 valid paired states and four actions per state;
- oracle mean advantage over balanced at least +5;
- strict oracle improvement in at least 55% of states;
- every opponent-family mean oracle advantage at least +1;
- at least two non-balanced modes are oracle-best in at least 24 states each; and
- mean oracle own-score delta nonnegative or mean opponent-score delta nonpositive.

Report each action's advantage distribution, phase/opponent effects, workforce transitions, and
negative tail without converting a selected oracle row into a policy.

## Frozen grouped ranker

Fit only on discovery labels. Standardize the exact 72 features with discovery mean/std, replacing
zero standard deviations by one. Fit one multi-output ridge regression (`alpha=10`, unpenalized
intercept) to the three paired advantages `harvest-balanced`, `renew-balanced`, and
`fell-balanced`. No feature selection, interaction, threshold search, weighting, resampling, or
hyperparameter tuning is allowed.

At inference choose the largest predicted non-balanced advantage only when it is strictly positive;
otherwise choose balanced. Action-order breaks predicted ties. Evaluate discovery descriptively
and apply every decision gate only to the untouched validation half.

The validation ranker passes only if all hold:

- activation between 20% and 80% of states;
- mean realized selected advantage at least +2;
- at least 55% of activated choices have positive advantage;
- selected actions use at least two non-balanced modes;
- every opponent mean advantage at least -3 and at least six of eight are positive; and
- realized mean advantage captures at least 25% of validation oracle mean advantage.

## Decision rule

- **Headroom and grouped ranker pass:** freeze the ranker and open one disjoint prospective
  complete-policy D75 test against balanced. D74 labels remain consumed and cannot qualify it.
- **Headroom passes, ranker fails:** retain paired option value as the target but close this static
  ridge representation; next test a bounded recurrent value model or deployability of direct
  high-level lookahead on fresh states.
- **Headroom fails:** close one-deviation ordinary-option values and move to multi-batch option
  sequences; do not tune the manifest quota, continuation, actions, or gates.
- **Integrity failure:** quarantine outcomes and repair only the defect before repeating unchanged.

No branch authorizes a submission candidate or any platform action.
