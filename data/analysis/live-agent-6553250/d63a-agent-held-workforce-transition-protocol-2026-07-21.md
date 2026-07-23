# D63a agent-held workforce-transition protocol (2026-07-21)

## Question

Does current top-policy third-worker creation transfer across agents as:

1. an opening/map-conditioned strategy choice; or
2. a mature-economy state-conditioned capitalization choice after turn 100?

D61p finds that the resident always stops at two workers, while 11/20 current top agents reach at
least three workers in 94/200 selected appearances. Scale is selective and usually not early:
adopters create worker three at median turn 101. This audit distinguishes a first-move selector
from a closed-loop state trigger before changing the local controller representation.

## Frozen data and sealing

- Consume only the 200 selected top-20 appearances named by the passed open D61p snapshot
  `20260721T105508Z-d61p`.
- Select appearances from acquisition provenance (`legend_top20` source), not outcome, rank, name,
  final score, or whether the policy scaled.
- Never enumerate or read `processed/sealed_confirmation`.
- Reverify D61p QA, open tables, trajectories, and named raw bodies through the existing open loader.
- Reconstruct exact official states and successful training events with zero unknown updates and
  exact final inventory/turn agreement.

## Agent-held partition

Partition by policy identity before feature extraction:

```text
bucket = SHA256("d63-agent:" + agentId) mod 10
discovery = buckets 0..5
validation = buckets 6..9
```

All ten appearances of one top agent stay in one partition. Agent ID, rank, name, and partition
bucket are metadata only and are forbidden model features.

## Fixed targets and feature times

### Model A: opening selector

- One row per selected top appearance (expected 200).
- Label: a third worker is successfully created at any turn (`TRAIN` ordinal 2 exists).
- Features: every numeric/bool value returned by the frozen official opening feature extractor.
  Exclude string/list fields, player identity, rank, commands, and every post-opening state.
- A key numeric/bool in any row is retained. A missing/`None` value is encoded as -1 and receives a
  companion `<feature>__missing` indicator; no outcome-dependent imputation is allowed.

This tests whether map geometry and starting stock alone support first-move/recipe selection.

### Model B: turn-100 capitalization selector

- Snapshot official state after resolved turn 100.
- Include only games lasting at least 150 turns with exactly two own workers after turn 100 and no
  third-worker event through turn 100.
- Label: a third worker is successfully created after turn 100.
- Features comprise Model A plus this fixed deployable turn-100 vector:
  - own and opponent bank inventory by all six materials, current bank score, and score/wood gaps;
  - own and opponent carried inventory totals and carrying-worker counts;
  - own two-worker aggregate and per-ordinal movement/carry/harvest/chop specifications;
  - opponent current worker count;
  - total current board plants, fruit, health, size, and per-species plant/fruit counts;
  - successful own/opponent TRAIN, PLANT, HARVEST amount, CHOP, and DROP amount through turn 100;
  - first successful own TRAIN turn and specification;
  - own planting counts by species through turn 100.

Do not use final score, final margin, later commands/events, policy identity, or leaderboard rank.

## Fixed model

Fit one logistic regression per model on discovery only:

- discovery mean/standard-deviation normalization; zero-variance scale becomes one;
- intercept unpenalized, all feature coefficients L2-penalized with lambda 1.0;
- Newton updates for at most 100 iterations, stopping at maximum step <=1e-9;
- no feature selection, hyperparameter search, threshold search, class weighting, or refit on
  validation;
- fixed probability threshold 0.5 for balanced accuracy;
- report ROC AUC, balanced accuracy, sensitivity, specificity, Brier score, prevalence, confusion
  matrix, and the 20 largest absolute standardized coefficients.

## Gates

### Model A gate

- at least 30 rows in each partition;
- at least ten positives and ten negatives in each partition;
- validation positive and negative labels each span at least three agents;
- validation ROC AUC >=0.65; and
- validation balanced accuracy >=0.60.

### Model B gate

- at least 30 eligible rows in each partition;
- at least eight positives and 15 negatives in each partition;
- validation positive and negative labels each span at least three agents;
- validation ROC AUC >=0.70; and
- validation balanced accuracy >=0.60.

Missing support produces `insufficient`, never a relaxed gate. AUC is the primary ranking measure;
balanced accuracy prevents a prevalence-only pass.

## Decision

- Model B pass: open a new offline protocol adding an explicit natural-boundary capitalization
  action to a closed-loop controller. If Model A also passes, use it only as an opening prior.
- Model A pass and Model B fail: open an offline first-move/recipe portfolio selector; do not add a
  universal turn-100 trigger.
- Neither pass: current scale is not captured by these deployable snapshots; move to a recurrent
  sequence or policy-portfolio representation rather than threshold tuning.

No outcome in this audit establishes value. Any selected representation must later pass exact
local prospective value, renewable safety, fresh field confirmation, and separately authorized
Arena transfer. D63a cannot create a candidate, open D61p confirmation, start games, or submit.
