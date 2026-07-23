# D134a block-transfer-selected soft-value q6 — frozen protocol

Date: 2026-07-22  
Status: frozen before D133 outcome interpretation or any D134 model fit

## Isolated hypothesis

D131 cannot distinguish useful random initializations on one 16-map fit panel: in-sample proposal
regret is inversely associated with consumed-panel policy value. D133 changes the evidence scale
to four independent 16-map blocks. D134 tests only whether held-block selection fixes that defect.

Retain D119 exactly:

- the 6,626-parameter `379 -> 16 -> 1` ReLU proposal ranker and `64 -> 8 -> 1` ReLU state gate;
- temperature-10 soft proposal targets plus equal soft-rank-cross-entropy and gate-BCE losses;
- Adam `1e-3`, weight decay `1e-4`, root batches of 128, 80 epochs, deterministic shuffles, and
  one PyTorch training thread; and
- first-positive, highest-ranked, at-most-one-intervention runtime semantics.

Do not add the D128 absolute anchor, D129 safety head, or D130 cross-sign term. Use fixed model
seeds `13401--13404`. Calibrate each gate only on its training blocks to exactly 84% active tasks,
using the midpoint between adjacent per-task maximum gate logits as in D125.

## Four-fold selection

D133 full pass is a hard prerequisite. For every fixed seed, run four fits. Each fit trains on
three D133 blocks and evaluates the excluded fourth block without updating weights or threshold.
Thus every one of the 1,024 corpus tasks is an out-of-fit policy outcome exactly once.

Pool held outcomes by their task counts and preserve each block and opponent family separately.
Proposal regret, within-ten coverage, gate recall, and gate balanced accuracy are descriptive: D131
shows that using in-sample proposal regret as a selector is specifically unsafe. A seed is eligible
only if its held policy has:

- pooled mean margin delta at least `+2`, strict gains at least 40%, and every held-block mean
  nonnegative;
- pooled worst opponent-family mean at least `-3` and at least six positive families;
- pooled mean own-score delta nonnegative or opponent-score delta nonpositive;
- intervention rate from 10% through 85%, crop rate no lower than exact control, and worker-three
  reach within five percentage points of control.

Select eligible seeds lexicographically by highest worst-block mean, pooled family floor, pooled
mean, strict rate, lower activity, then lower fixed seed. Require a second complete D134 selection
run to reproduce every model hash, metric, eligibility decision, and selected seed exactly.

## Full fit and retrospective veto

Only reproducible held-block eligibility permits fitting the selected seed once on all four D133
blocks. Recalibrate its gate to 84% activity using only D133. Then score that frozen full model on
the already-consumed D126 panel (`9,843,780--9,843,795`) without refitting or selecting another
seed. This panel has veto authority only; it cannot rescue or choose a model.

Require D126 mean at least `+2`, strict gains at least 40%, both parity folds nonnegative, family
floor at least `-3`, at least six positive families, directional score safety, 10%--85% activity,
crop performance no lower than control, and worker-three reach within five percentage points.

## Decision

- **D133 prerequisite/mechanics failure:** do not train.
- **No held-block-eligible seed or failed exact repeat:** close the unchanged D119 abstraction and
  next test a winner-conditioned action-aware gate on these same consumed blocks.
- **Consumed D126 veto failure:** record the failure and close without tuning on D126.
- **Full pass:** save an internal checkpoint and open one separately frozen final validation on
  untouched seeds `9,843,800--9,843,815`.

D134 cannot itself integrate Rust, create a submission, mutate the resident, or touch
TestSession/Arena.
