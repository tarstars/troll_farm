# D116a root-wise q6 proposal/WAIT choice — frozen protocol

Date: 2026-07-22  
Status: frozen before D116 training or validation collection

## Hypothesis and controlled change

D115's best binary classifier improves 42.5% of validation tasks but intervenes on 89.375% and
reaches only `+1.081`. Independent arm classification rewards every positive arm and does not
directly teach either within-root ranking or abstention. D116 changes only that objective.

Keep D115's 379 raw control-relative inputs and `379 -> 16 ReLU -> 1` shared proposal scorer
(`6,097` float32 parameters). At each root, form one categorical choice with logits
`[0 for WAIT, score(proposal_1), ..., score(proposal_n)]`. If the backward-DP best act advantage is
nonpositive, target WAIT. Otherwise target the exact best proposal under the existing deterministic
teacher tie-break. Minimize equal-root-weight categorical cross entropy. Padding logits are masked
to negative infinity. There is no opponent identity, recurrence, terminal input, online rollout,
or extra WAIT network. D116 does not yet alter the agent.

## Data isolation and mechanics

Reuse only D114's fit-only seeds `9,843,300--9,843,315`: 1,323 roots and 21,374 arms. D114 and
D115 validation panels are excluded from fitting, calibration, selection, and diagnosis.

Collect one fresh balanced validation panel on unused seeds `9,843,630--9,843,639`, both seats and
all eight opponents: 160 tasks. Require the unchanged snapshot collector, exact mechanics, zero
failures, at least 90% task support, at least 600 roots / 6,000 arms, and 12 arms/s. Conditional
held remains the still-unopened seeds `9,843,700--9,843,715`, 256 tasks.

## Frozen training and selection

Train four models with seeds `11601--11604`. For each:

- default deterministic PyTorch linear initialization after its fixed seed;
- 40 epochs and deterministic PCG64 root shuffles;
- minibatches of 128 complete roots, so proposals never cross or split a root;
- Adam learning rate `1e-3`, weight decay `1e-4`, no schedule or early stop;
- mean categorical cross entropy over roots; and
- float32 inference, 20 CPU threads, and deterministic algorithms.

Evaluate each unchanged trained model with D115's same logit offsets
`{-1.0, 0.0, 0.5, 1.0, 1.5, 2.0}`. Runtime semantics are unchanged: at each boundary select the
highest-scoring proposal only when `max_score - offset > 0`; otherwise wait. Execute at most the
first selected paired intervention, then return to D40. This is the complete 24-candidate grid.

Validation admission is unchanged: mean gain at least `+2`, strict gain at least 30%, both
interleaved folds nonnegative, worst family at least `-5`, at least five positive families, own
score nonnegative or opponent score nonpositive, activity 10%--85%, crops 100%, and worker-three
reach within five percentage points of D40. Select by highest minimum fold, worst family, mean,
strict rate, lowest activity, then fixed seed/offset order. Keep the selected training-only model
unchanged; never refit on validation.

## Conditional held qualification

If no validation candidate qualifies, do not collect or open held data. If one qualifies, freeze
its checkpoint hash and a separate exact held evaluator before collection. Evaluate the model by
first-intervention lookup over the complete dense held matrix. Require mechanics again and held
mean at least `+2`, strict at least 40%, worst family at least `-3`, at least six positive families,
own score nonnegative or opponent score nonpositive, activity 10%--85%, crops 100%, and
worker-three reach within five percentage points of D40.

## Decision

- **Mechanics failure:** repair coverage only; do not change model, loss, grid, or gates.
- **No validation admission:** close the fixed-wait listwise scorer without held collection.
- **Held failure:** close D116 without tuning on held outcomes.
- **Full held pass:** open quantized Rust reconstruction, byte/decision parity, agent integration,
  and one final untouched confirmation panel before submission consideration.

No branch authorizes TestSession, Arena, submission, or resident mutation.
