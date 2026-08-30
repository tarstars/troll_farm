# Shared-trunk value-gradient and global-clipping audit

Date: 2026-08-30
Agent: `chatgpt_1`
Programme: `20260829-nn-bot-way-b`
Reviewed main: `8300905cb65e5f5974c5277189f389ce97ed93f8`
Revision: r3 — pins optimizer-state and cross-checkpoint comparison semantics

## Verdict

After critic warm-up, the value objective is not isolated from the policy in **two** ways:

1. `value_loss` directly updates the shared convolution trunk that produces both spatial and plan logits;
2. the trainer clips one combined gradient vector over the entire model, so a large value gradient can scale down policy, entropy and anchor gradients even on parameters the value head does not touch.

These are code-level mechanisms shared by every eroding Phase-3 run. They are not yet a causal verdict, but they are stronger next falsifiers than another opponent, gamma or episode-length sweep because `ppo-h` made the value target harder and immediately produced the worst update-500 result.

## Exact shared-trunk gradient path

`cgauto/train_level1_ppo.py::SpatialActorCritic.forward_with_plan` computes:

```python
hidden, pooled, scaled, valid = self._trunk(observations)
spatial = self.actor(hidden)
plan = self.plan(pooled, scaled, valid)
value = self.critic(pooled)
```

The same `stem.*` and `tower.*` tensors therefore feed all three outputs.

`local_claude_1/nn-bot/train_ppo_full.py` forms:

```python
loss = (
    policy_loss
    - entropy_coef * entropy_loss
    + value_coef * value_loss
)
loss += anchor_coef * anchor_kl
loss.backward()
nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
optimizer.step()
```

No detach separates the value branch from `pooled`.

The optimizer's two groups do not change this fact:

```text
critic group: critic.* only
actor group:  stem.*, tower.*, actor.*, plan.*
```

A value-loss gradient through the trunk is applied using the actor group's learning rate. `actor_lr_scale` reduces it, but does not remove it.

## The second coupling: one global clip coefficient

`clip_grad_norm_(model.parameters(), 0.5)` computes one norm over every gradient and applies one scaling factor to all of them when the threshold is exceeded.

Consequences:

- a large `critic.*` or value-to-trunk gradient can force clipping;
- the same factor then attenuates `actor.*` and `plan.*` gradients, even though the value branch has no direct path into those head parameters;
- anchor and policy gradients can be suppressed while the combined update direction is dominated by value fitting;
- making the value target harder can change the effective policy update even if the policy loss, entropy coefficient and anchor coefficient are unchanged.

The logs do not report pre-clip total norm, per-term norms, the clip scale, or how often clipping fires. `clip_fraction` is PPO ratio clipping, not gradient clipping.

Therefore a future `pooled.detach()` control is necessary but not sufficient for clean isolation unless clipping is also separated or measured: the critic-head gradient can still consume the global norm budget.

## Why warm-up does not close either coupling

During `critic_warmup_updates`, all non-`critic.*` parameters have `requires_grad=False`, so the trunk is protected and only the small value MLP learns.

At the first normal PPO update the loop re-enables every non-critic parameter. From that point:

- value loss changes `stem.*` and `tower.*`;
- those changes move spatial and plan logits even if policy loss were zero;
- critic/value gradients participate in the one global clipping norm;
- the anchor can respond only after logits have moved;
- the value target is a short-rollout bootstrapped target, not certified full-episode return-to-go.

The warm-up therefore delays shared-representation damage; it does not prevent it.

## Why the current evidence makes this worth testing

The following are consistent with, but do not prove, value-gradient/clipping damage:

- lower actor learning rate delayed erosion in `ppo-f2`;
- that multiplier applies to the trunk, including value gradients;
- `ppo-h` made value fitting harder, logged explained variance around `0.25`, and had the worst update-500 scout (`3/48`, `112.8` points);
- fruit-chain commands decay while other behaviours remain, which is compatible with a shared feature representation moving;
- no run reports whether the combined gradient was clipped or which term dominated it.

## Instrument identity requirements

The committed checkpoints carry all four keys:

```text
model
optimizer
config
evaluation
```

Therefore the instrument must not approximate the live update.

For each checkpoint:

1. load `model` exactly;
2. rebuild the two optimizer groups from the checkpoint config;
3. load the checkpoint's `optimizer` state dict, including Adam moments and per-group learning rates;
4. load the original clone anchor named by the config and use the coefficient at the checkpoint's recorded `turn_steps`;
5. use the checkpoint's exact gamma, lambda, value coefficient, entropy coefficient, clip coefficient, max-grad norm, actor LR scale, plan-target-memory mode, opponent and seed configuration;
6. record all input SHA-256 hashes and the complete effective config in the output.

A fresh Adam optimizer is a different experiment: its first step lacks the live run's moments and bias-correction state. Such a result must be labelled `fresh_optimizer_control`, never the run's counterfactual.

The current training log stores policy/value/entropy/anchor scalars from the **last minibatch**, not an update average. The instrument's per-term measurements are therefore the source of truth for its chosen minibatch; do not try to match the printed scalar as if it represented the full update.

## Decisive offline gradient decomposition

Use one exact post-warm-up minibatch and identical copies of the same checkpoint. For each loss term separately, compute gradients without stepping:

```text
P: clipped PPO policy loss
E: -entropy_coef * entropy
V: value_coef * value loss
A: anchor_coef * KL(anchor || policy)
```

For each term report gradient norm on:

```text
stem.*
tower.*
actor.*
plan.*
critic.*
```

Also report:

- pairwise cosine similarity on the shared trunk: `P·V`, `E·V`, `A·V`, `P·E`, `P·A`;
- each term's full-model norm;
- the norm of `P+E+V+A` before clipping;
- the exact global clip multiplier at threshold `0.5`;
- the policy-head update with and without V included in the norm calculation.

Split P and V by PLAN versus TROLL rows and by fruit-chain versus other TROLL actions where applicable.

## Same-state and on-policy views

The clone, `ppo-g` update 500 and `ppo-h` update 500 naturally induce different trajectories. Both views are needed:

### On-policy view

Collect one rollout under each checkpoint's own temperature-1 behaviour with the same map/inventory seed schedule. This measures the gradient context that checkpoint actually creates, while explicitly labelling the state-distribution difference.

### Fixed-state view

Build one common 512-observation census, preferably a deterministic stratified union of clone/g/h rollout rows, with PLAN/TROLL and fruit-chain coverage. Evaluate all three checkpoints and all value-only counterfactual steps on exactly this same census.

Without the fixed-state view, a larger g-versus-h logit shift can be caused by different states rather than a different gradient mechanism.

## Value-only counterfactual step

On a copy of each checkpoint:

1. restore the live Adam optimizer state;
2. zero gradients;
3. backward `value_coef * value_loss` only on the selected minibatch;
4. record pre-clip norms and the global clip multiplier;
5. apply exactly one optimizer step using the live learning rates and moments;
6. run the common fixed observation census before and after;
7. report:
   - parameter deltas by block;
   - spatial and plan logit KL;
   - argmax agreement;
   - agreement on fruit-chain rows;
   - change in clone-anchor KL.

This directly answers whether the value objective alone can move deployed actions at the actual update-500 optimizer state.

Negative controls:

- repeat with `pooled.detach()` for the value branch; only `critic.*` may receive V gradients and policy logits must remain byte-identical under a V-only step;
- repeat the original path with a fresh optimizer, labelled separately, to show how much Adam state matters.

## Narrow matched-seed training controls

If the offline result is material, add two separately recorded switches:

```text
--critic-trunk-grad on|off
--gradient-clipping joint|per-group
```

For `critic-trunk-grad=off`, compute the value head from `pooled.detach()` during update-time loss construction. The forward value is numerically unchanged; only the gradient path into `stem.*` and `tower.*` is cut.

For `gradient-clipping=per-group`, clip the policy-side and critic-side parameter groups separately and log both pre-clip norms and multipliers. Do not silently change this together with the detach control in the first causal run:

1. first compare current joint behavior to `critic-trunk-grad=off` while recording the joint clip scale;
2. only if critic-head gradients still dominate clipping, run the per-group clipping arm as a second one-variable test.

Required tests:

- value-only backward gives nonzero `critic.*` gradients and zero trunk/head gradients when detach is on;
- policy and anchor gradients still reach their intended parameters;
- each checkpoint records both flags;
- old behavior is byte-identical under `on/joint`;
- synthetic oversized critic gradients demonstrate that joint clipping scales policy gradients while per-group clipping does not.

Use the same seed and otherwise frozen best recipe. Do not combine either switch with temperature, entropy, lambda or curriculum changes.

## Relation to the source-backed curriculum

The winner's Level 4 froze the movement executor while training the plan selector and a separate end-score value head. A plan-only mode with the trunk and spatial actor frozen automatically blocks the direct value-gradient route into the executor. Separately clipping the trainable plan and critic groups would also make their competition observable. This makes plan-only PPO both a source-backed stage and a strong safety control.

## Recommendation

```text
MEASURE per-term and pre-clip gradient norms before another explanatory long run.
RESTORE the live Adam state for the value-only step.
USE both on-policy and fixed-state comparisons.
IF material, run a matched-seed critic-trunk-gradient OFF control.
MEASURE joint clipping; test per-group clipping only as a separate follow-up.
DO NOT assume the critic affects the actor only through advantages; the current code couples them directly and through clipping.
```

No trainer, checkpoint, environment, dataset, YT operation, platform or Arena state was changed by this audit.
