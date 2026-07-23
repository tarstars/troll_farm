# D118a soft-value q6 ranker and state gate — frozen protocol

Date: 2026-07-22  
Status: frozen before D118 fit-only training or validation collection

## Hypothesis and isolated change

D117 proves that the separate 64-state gate is useful, while exact one-hot proposal ranking is the
bottleneck and exact top-1 is a poor proxy for near-tied proposal value. D118 keeps D117's runtime
and 6,626-parameter architecture unchanged:

- `379 -> 16 ReLU -> 1` shared proposal scorer (6,097 parameters); and
- `64 -> 8 ReLU -> 1` act/wait state gate (529 parameters).

Change only the proposal loss. For every root, convert all exact act-advantage targets into a soft
categorical distribution `softmax((advantage - max_advantage) / 10)`. The subtraction is
numerically stable and removes the root's common future-value offset. Temperature 10 is frozen
against the already known 25--29 point target standard deviation. Minimize soft-target cross
entropy plus the unchanged binary gate BCE with equal coefficients and equal root weight.

Runtime remains: when `gate_logit - offset > 0`, execute the proposal-score argmax; otherwise wait.
Stop after the first intervention and return to D40. D118 does not modify the agent.

## Fit-only data, optimization, and gate

Reuse only D114 fit seeds `9,843,300--9,843,315` (1,323 roots / 21,374 arms). Every D114--D116
validation panel is excluded. D117 collected no validation data; its reserved range remains fresh.

Train seeds `11801--11804` for 40 epochs with deterministic PCG64 root shuffles, 128 complete roots
per batch, Adam `1e-3`, weight decay `1e-4`, no schedule or early stop. Use exactly one CPU training
thread because D117 demonstrated multithreaded weight nondeterminism; the exact game collector
remains separately authorized to use all 20 CPUs. Require two complete fit runs to be byte-exact
before any validation collection.

Evaluate gate offsets `{-1.0, -0.5, 0.0, 0.5, 1.0, 1.5}` on fit data. At least one model/offset
must satisfy all model gates:

- mean proposal regret at most 18 points;
- at least 45% of proposal choices within ten points of the exact best;
- state-gate balanced accuracy at least 60%; and
- state-gate act recall and wait recall each at least 50%;

and all fit-policy gates: mean at least `+3`, strict at least 30%, both folds nonnegative, worst
family at least `-3`, at least six positive families, activity 10%--85%, crops 100%, and
worker-three reach within five percentage points of D40. This authorizes validation collection but
does not select or refit a candidate.

## Conditional validation and held

If the fit gate and repeated-fit exactness pass, freeze the fit result/model hashes and collect a
fresh balanced 16-map panel on still-unused seeds `9,843,670--9,843,685`, both seats and all eight
opponents (256 tasks). Require zero mechanics failures, at least 90% task support, 600 roots / 6,000
arms, and 12 arms/s. Evaluate all 24 unchanged candidates.

Validation admission remains mean at least `+2`, strict at least 30%, both folds nonnegative,
worst family at least `-5`, at least five positive families, own score nonnegative or opponent
score nonpositive, activity 10%--85%, crops 100%, and worker-three reach within five percentage
points of D40. Selection order remains minimum fold, worst family, mean, strict rate, lowest
activity, then fixed seed/offset order. Never refit on validation.

Only full validation admission can open still-unused held seeds `9,843,700--9,843,715`. Freeze the
selected checkpoint and held evaluator first. Held gates remain mean `+2`, strict 40%, floor `-3`,
six positive families, directional score safety, activity 10%--85%, crops 100%, and workforce
safety.

## Decision

- **Fit or reproducibility gate fail:** close without new simulation.
- **Validation mechanics fail:** repair coverage only; do not change model, loss, grid, or gates.
- **No validation admission:** close without held collection.
- **Held failure:** close without tuning on held outcomes.
- **Full held pass:** open quantized Rust parity/integration and final untouched confirmation before
  submission consideration.

No branch authorizes TestSession, Arena, submission, or resident mutation.
