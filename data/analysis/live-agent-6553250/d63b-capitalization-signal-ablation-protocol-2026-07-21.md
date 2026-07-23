# D63b capitalization-signal ablation protocol (2026-07-21)

## Question

Does D63a's held-agent turn-100 result remain transferable after removing worker-recipe and opening
fingerprints, or does the full model merely recognize which policy recipe produced the state?

D63b is a fixed, no-new-data ablation. It cannot establish action value. Its purpose is to select
the state representation for the next prospective experiment without tuning on held agents.

## Frozen input and rows

- Input is exactly `d63a-agent-held-workforce-transition-2026-07-21.json`, SHA-256
  `58be23c7a7e6b5995bcaa5b7a209a412f7a06a0231b66a8c9eb83013b5a98ef2`.
- Retain exactly its 150 `turn100_eligible` rows, labels, and frozen identity-held partition.
- Do not reconstruct or fetch games, alter row eligibility, repartition agents, or inspect any
  sealed confirmation product.
- Label remains successful creation of worker three after turn 100.
- Agent ID, name, leaderboard rank, outcome, final score, and later commands remain forbidden.

## Frozen feature families

Every model uses only keys already present in the D63a turn-100 feature dictionary. Feature groups
are selected by the following semantic prefixes; there is no coefficient- or outcome-based feature
selection.

### R: worker recipe only

Include `first_train_*`, `worker0_*`, `worker1_*`, `workers_sum_*`, and `workers_max_*`.
This deliberately includes duplicated representations of the first trained worker because they
were present in the full frozen model. It tests whether static role recipe alone transfers.

### S: instantaneous economy without recipe or history

Include `bank_score_gap`, `bank_wood_gap`, `board_*`, `own_bank_*`, `opponent_bank_*`,
`own_carry_*`, `opponent_carry_*`, `own_carrying_workers`, `opponent_carrying_workers`, and
`opponent_worker_count`. Exclude every `open_*`, worker talent, first-TRAIN, and cumulative event
feature.

### F: cumulative economy flow without recipe or opening

Include all S features plus `own_successful_*`, `opponent_successful_*`, `own_harvested_amount`,
`opponent_harvested_amount`, `own_chops_landed`, `opponent_chops_landed`, `own_dropped_amount`,
`opponent_dropped_amount`, `own_planted_*`, and `opponent_planted_*`.

F is the primary deployable representation. A controller can maintain every included cumulative
count online; none requires future information or policy identity.

### C: combined reference

Reuse the exact 139-feature D63a turn-100 model as an immutable reference. D63b must verify its
stored metrics and must not refit or reinterpret C as a new test.

## Frozen fit and metrics

Fit R, S, and F independently on discovery only using the exact D63a procedure:

- discovery mean/standard-deviation normalization;
- L2 logistic regression, lambda 1.0, unpenalized intercept;
- Newton updates, at most 100 iterations, maximum-step tolerance `1e-9`;
- fixed 0.5 classification threshold;
- no weighting, feature selection, threshold selection, hyperparameter search, or validation refit.

Report discovery/validation ROC AUC, balanced accuracy, sensitivity, specificity, Brier score,
confusion matrix, label/agent support, feature names, and 20 largest absolute standardized
coefficients.

## Gates and decision

All models require the unchanged D63a support gate: discovery at least 30 rows with at least eight
positives and 15 negatives; validation likewise; and validation positive/negative labels each span
at least three agents.

The primary F gate passes at validation ROC AUC >= 0.70 and balanced accuracy >= 0.60. R and S use
the same thresholds as diagnostic gates, not alternate candidates.

Decision is frozen:

1. F pass: dynamic economy flow is sufficient; open a prospective state-conditioned
   capitalization-value protocol. R/S results may simplify that representation but cannot veto it.
2. F fail and R pass: classify D63a as recipe recognition; open a whole-recipe/recurrent policy
   representation, not a state trigger.
3. F fail, R fail, C pass: the signal depends on recipe-state interaction; prospective actions must
   be conditioned on existing worker roles.
4. If the stored C reference or any integrity assertion differs, mark invalid and stop.

No D63b outcome authorizes a candidate, confirmation access, TestSession, Arena, or submission.

