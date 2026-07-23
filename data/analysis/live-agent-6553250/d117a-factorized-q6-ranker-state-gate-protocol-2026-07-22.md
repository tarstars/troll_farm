# D117a factorized q6 ranker and state gate — frozen protocol

Date: 2026-07-22  
Status: frozen before D117 fit-only training or validation collection

## Hypothesis and compact architecture

D116's root-softmax frontier is robust but small (`+1.078`, both folds positive, `-0.813` floor)
because fixed WAIT dominates a many-way proposal choice. D117 factorizes the deployed decision:

- a shared `379 -> 16 ReLU -> 1` proposal ranker (`6,097` parameters); and
- an independent `64 root state -> 8 ReLU -> 1` act/wait gate (`529` parameters).

The total is 6,626 float32 parameters, about 26.5 kB unencoded or 6.6 kB at one byte per
parameter. Train proposal-only categorical cross entropy on every root, targeting the exact best
proposal under the existing teacher tie-break even when every proposal is worse than waiting.
Train binary gate cross entropy on backward-DP `act_now_optimal`. Give both losses equal coefficient
and every root equal weight. There is no opponent identity, recurrence, terminal input, online
rollout, or interaction between roots.

At runtime, compute the gate once per q6 boundary. If `gate_logit - offset > 0`, execute the
ranker's highest-scoring proposal; otherwise wait. Stop after the first paired intervention and
return to D40. D117 does not yet modify the agent.

## Fit data and prospective structural gate

Reuse only D114's fit-only seeds `9,843,300--9,843,315`: 1,323 roots and 21,374 arms. D114,
D115, and D116 validation panels are excluded from fitting, threshold selection, and diagnosis.

Train four models with seeds `11701--11704`:

- default deterministic PyTorch initialization after the fixed seed;
- 40 epochs, deterministic PCG64 root shuffles, batches of 128 complete roots;
- Adam learning rate `1e-3`, weight decay `1e-4`, no schedule or early stop;
- summed mean proposal-rank CE and mean gate BCE;
- float32 inference, 20 CPU threads, deterministic algorithms.

Evaluate the complete fixed gate-offset grid `{-1.0, -0.5, 0.0, 0.5, 1.0, 1.5}` on fit data.
Before any new validation collection, require at least one model/offset pair whose model has:

- proposal top-1 accuracy at least 20% on all roots and on act roots;
- gate balanced accuracy at least 60%; and
- both gate act recall and wait recall at least 50%;

and whose fit-only policy has mean gain at least `+2`, strict gain at least 20%, both interleaved
folds nonnegative, worst family at least `-3`, at least six positive families, activity 10%--85%,
crops 100%, and worker-three reach within five percentage points of D40. This gate only authorizes
buying fresh validation data; it does not select or refit a candidate.

## Conditional fresh validation

If the fit gate fails, close D117 without validation collection. If it passes, freeze the complete
fit result and model hashes, then collect a fresh balanced 16-map panel on unused seeds
`9,843,670--9,843,685`, both seats and all eight opponents: 256 tasks. Require the unchanged exact
collector, zero failures, at least 90% task support, 600 roots / 6,000 arms, and 12 arms/s.

Evaluate all 24 unchanged seed/offset candidates. Validation admission remains: mean at least
`+2`, strict at least 30%, both folds nonnegative, worst family at least `-5`, at least five
positive families, own score nonnegative or opponent score nonpositive, activity 10%--85%, crops
100%, and worker-three reach within five percentage points of D40. Select by highest minimum fold,
worst family, mean, strict rate, lowest activity, then fixed seed/offset order. Keep the selected
training-only model unchanged.

## Conditional held qualification

Only a full validation admission can open still-unused held seeds `9,843,700--9,843,715`. Freeze
the selected checkpoint and exact held evaluator first. Held requires complete mechanics, mean at
least `+2`, strict at least 40%, worst family at least `-3`, at least six positive families, own
score nonnegative or opponent score nonpositive, activity 10%--85%, crops 100%, and worker-three
reach within five percentage points of D40.

## Decision

- **Fit gate fail:** close D117 without new simulation.
- **Validation mechanics fail:** repair coverage only; do not change model, losses, grid, or gates.
- **No validation admission:** close without held collection.
- **Held failure:** close without tuning on held outcomes.
- **Full held pass:** open quantized Rust parity/integration and a final untouched confirmation
  panel before submission consideration.

No branch authorizes TestSession, Arena, submission, or resident mutation.
