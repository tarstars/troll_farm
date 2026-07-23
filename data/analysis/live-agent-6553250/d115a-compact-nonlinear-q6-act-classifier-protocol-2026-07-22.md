# D115a compact nonlinear q6 act classifier — frozen protocol

Date: 2026-07-22  
Status: frozen before D115 training or validation collection

## Hypothesis and capacity bound

D114's train/validation teachers remain `+35.977`/`+39.055`, yet every direct 379-weight ridge
scorer fails; the best validation mean is only `+0.336`. Dense credit is sufficient, but one
hyperplane cannot represent the sparse act-now region.

D115 replaces only scorer capacity/objective: 379 raw control-relative action inputs, one 16-unit
ReLU hidden layer, and one logit (`6,097` parameters). Train the binary label
`act_advantage > 0` with root-balanced and globally class-balanced BCE. Runtime semantics remain
first positive argmax, at most one paired intervention, then D40. Opponent identity, recurrence,
runtime simulation, and terminal inputs remain excluded. A future int8 representation would be
about 6.1 kB before encoding, compatible with the 100k submission limit; D115 does not yet modify
the agent.

## Data isolation

Reuse only D114's fit-only training matrix on seeds `9,843,300--9,843,315` (21,374 arms). Do not
use its consumed validation matrix for training, model selection, thresholds, or diagnosis.

Collect new validation continuations on untouched seeds `9,843,600--9,843,607`, both seats and all
eight opponents: 128 tasks. Conditional held uses untouched seeds `9,843,700--9,843,715`, 256
tasks. The unchanged snapshot collector must pass exact mechanics, at least 90% task support, and
12 arms/s. Full-run reproducibility is inherited from D112.

## Frozen training and selection

Train four models with seeds `11501--11504`. For each:

- default deterministic PyTorch linear initialization after its fixed seed;
- 40 epochs, deterministic PCG64 epoch shuffles, minibatches of 1,024;
- Adam learning rate `1e-3`, weight decay `1e-4`, no schedule or early stop;
- each arm receives root weight `1 / proposals_at_root`;
- positive and nonpositive labels each receive half of total class mass; and
- weighted BCE is normalized by batch weight. Use 20 CPU threads and deterministic algorithms.

Round inference parameters to float32. Evaluate each fixed model at logit offsets
`{-1.0, 0.0, 0.5, 1.0, 1.5, 2.0}`: act when the highest `(logit - offset)` is positive. This is
the complete 24-candidate grid.

Validation admission is unchanged from D114: mean gain at least `+2`, strict gain at least 30%,
both interleaved folds nonnegative, worst family at least `-5`, at least five positive families,
own score nonnegative or opponent score nonpositive, activity 10%--85%, crops 100%, and
worker-three reach within five percentage points of D40. Select by highest minimum fold, worst
family, mean, strict rate, lowest activity, then fixed seed/offset order. Keep the selected trained
model unchanged; do not refit on validation.

## Conditional exact held qualification

If none qualify, do not collect held continuations. If one qualifies, collect the complete dense
held matrix once with the already byte-validated collector and evaluate the frozen model by exact
first-intervention lookup. Require collection mechanics again.

Held gates remain: mean gain at least `+2`, strict at least 40%, worst family at least `-3`, at
least six positive families, own score nonnegative or opponent score nonpositive, activity
10%--85%, crops 100%, and worker-three reach within five percentage points of D40.

## Decision

- **Mechanics failure:** repair only, without changing architecture/training/grid.
- **No validation admission:** close this small MLP without held collection.
- **Held failure:** close D115 and do not tune on held outcomes.
- **Full held pass:** open quantized Rust reconstruction, byte/decision parity, agent integration,
  and a final untouched confirmation panel before any submission decision.

No branch authorizes TestSession, Arena, submission, or resident mutation.
