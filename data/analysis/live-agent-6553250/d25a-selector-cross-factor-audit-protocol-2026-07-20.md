# D25a selector cross-factor audit — frozen protocol (2026-07-20)

## Reason for the audit

D25's predeclared gate passes 37 configurations and selects
`random_forest_d4_l40_b30`.  Before opening any prospective map, two structural optimism channels
must be removed:

1. `compact_gold` and fixed `gold_elite` produce behavior-identical D24 outcomes, so treating them
   as two independently held opponent families leaves an alias in training; and
2. blocked-map CV sees every opponent on other maps, while held-opponent CV sees the held maps
   under other opponents.  Passing both marginal schemes does not prove transfer when map and
   opponent are simultaneously unseen.

This is a read-only audit on the already-consumed D25 development corpus.  It cannot select a new
model, buffer, feature set, or threshold.

## Frozen model

- family: random-forest value regressor;
- trees: 256;
- maximum depth: 4;
- minimum leaf: 40;
- switch buffer: 30 margin points;
- features, bootstrap, split criterion, seeds, and target exactly as D25.

## Frozen audits

1. **Structural-family holdout:** seven folds, with `compact_gold` and `gold_elite` excluded
   together; the other six opponents each form one fold.
2. **Crossed map × structural-family holdout:** 6 contiguous 20-seed blocks × 7 structural
   families.  For each of 42 cells, train on neither the held map block nor the held family and
   predict only their intersection.  Every labeled row receives exactly one such prediction.

Both audits must independently repeat every D25 research gate: 5--60% selection, >=75% positive
precision, >=+5 seed-clustered mean, >=+3 trimmed mean, 95% lower bound above zero, >=6/8
nonnegative reported opponents, worst opponent >=-5, no catastrophe-frequency or negative-mass
increase, and >=20% oracle capture.

The output must also reproduce byte-identical prediction hashes when the input rows are reversed.

## Decision

- If both audits pass, preserve the original D25 selection and open the already reserved
  prospective seeds 50,120--50,179 once.
- If either fails, close D25 without prospective data.  Do not choose another one of the 36
  development passers or retune the selected forest.

No candidate, submission, Arena game, or field action is authorized.
