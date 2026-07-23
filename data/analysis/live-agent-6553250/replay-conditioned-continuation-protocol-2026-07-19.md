# Replay-conditioned continuation retrieval — frozen protocol, 2026-07-19

## Question

After seeing an opponent through turn 50 or 100, does its recent state/action history predict the
next 50-turn production vector materially better than a population mean or current state alone?

This is a feasibility audit for opponent continuations on the 21 consumed rich-immediate Phase 21
games.  It is not candidate evidence and cannot authorize an arena transfer.

## Frozen examples and targets

Create two examples per exact replay, at cutoffs 50 and 100 (42 total).  The target is the next
50-turn increment in score, fruit, wood, workers, successful plants, harvested fruit, successful
chops, and dropped items.  Use only information observable through the cutoff.

Compare three representations:

1. **map** — symmetric turn-one bank/tree/type/fruit/health/size totals, water adjacency, shack
   distance, and iron presence from the existing exact-map census;
2. **state** — the eight opponent production/state counters at the cutoff;
3. **history** — state plus the immediately preceding 50-turn production increments, issued
   CHOP/DROP/HARVEST/MINE/MOVE/PICK/PLANT rates, and the immediate trained worker's four stats.

No opponent name/agent ID, future TRAIN, future action, final outcome, candidate margin, rank, or
post-cutoff map state may enter a feature.

## Frozen retrieval and validation

- Standardize each feature from the eligible training fold only; zero-variance features contribute
  zero distance.
- Predict with the unweighted mean of the nearest `k` complete trajectories in Euclidean feature
  distance.  Choose `k` from `{1,3}` independently for each representation using only the 12-game
  discovery partition, leave-one-opponent-out within each cutoff.  Break ties toward smaller `k`.
- The baseline is the eligible training-fold mean target.
- Freeze each selected `k`, train on discovery, and predict the nine confirmation games while
  excluding any training occurrence with the same opponent name.
- Also report all-21 leave-one-game-out and leave-one-opponent-out diagnostics with the frozen `k`.

Primary error is mean absolute target error normalized by fixed 50-turn scales inherited from the
continuation audit: score 20, fruit 6, wood 5, workers 1, plants 4, harvest 8, chops 15, and drops
12.  Report per-field MAE, per-cutoff error, and paired example wins as well.

## Frozen gates

All gates must pass:

1. exactly 21 unique games, 42 unique examples, 24 discovery examples, and 18 confirmation
   examples with complete targets/features;
2. confirmation history error is at least 10% below the split-mean baseline;
3. confirmation history error is at least 5% below state retrieval;
4. turn-100 confirmation history error is at least 10% below the split-mean baseline;
5. all-game leave-one-opponent-out history error is at least 5% below its mean baseline; and
6. history beats state on at least 55% of confirmation examples (ties do not win).

## Stop rule

- **Pass:** build a bounded replay-resampling ambiguity set, then test whether counterfactual
  command traces remain usable under small resident-policy perturbations.
- **Fail:** trajectory history does not transfer across named agents at this sample size.  Do not
  tune distances/features on these 21 games; collect completed histories for repeated rich agents
  and move to per-opponent distillation.

No fresh seed, arena game, submission, source candidate, or resident change is allowed.

