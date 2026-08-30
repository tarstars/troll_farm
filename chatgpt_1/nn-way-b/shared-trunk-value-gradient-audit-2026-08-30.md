# Shared-trunk value-gradient audit

Date: 2026-08-30
Agent: `chatgpt_1`
Programme: `20260829-nn-bot-way-b`
Reviewed main: `e02e88c8afadc31dc16109ed85eb3c547913943e`

## Verdict

After critic warm-up, the value objective is not isolated from the policy. `value_loss` directly updates the shared convolution trunk that produces both spatial and plan logits.

This is a code-level mechanism shared by every eroding Phase-3 run. It is not yet a causal verdict, but it is a stronger next falsifier than another opponent, gamma or episode-length sweep because `ppo-h` made the value target harder and immediately produced the worst update-500 result.

## Exact gradient path

`cgauto/train_level1_ppo.py::SpatialActorCritic.forward_with_plan` computes:

```python
hidden, pooled, scaled, valid = self._trunk(observations)
spatial = self.actor(hidden)
plan = self.plan(pooled, scaled, valid)
value = self.critic(pooled)
```

The same `stem.*` and `tower.*` tensors therefore feed all three outputs.

`local_claude_1/nn-bot/train_ppo_full.py` then forms:

```python
loss = (
    policy_loss
    - entropy_coef * entropy_loss
    + value_coef * value_loss
)
loss += anchor_coef * anchor_kl
loss.backward()
```

No detach separates the value branch from `pooled`.

The optimizer's two groups do not change this fact:

```text
critic group: critic.* only
actor group:  stem.*, tower.*, actor.*, plan.*
```

A value-loss gradient through the trunk is applied using the actor group's learning rate. `actor_lr_scale` reduces it, but does not remove it.

## Why warm-up does not close it

During `critic_warmup_updates`, all non-`critic.*` parameters have `requires_grad=False`, so the trunk is protected and only the small value MLP learns.

At the first normal PPO update the loop re-enables every non-critic parameter. From that point:

- value loss changes `stem.*` and `tower.*`;
- those changes move spatial and plan logits even if policy loss were zero;
- the anchor can respond only after logits have moved;
- the value target is a short-rollout bootstrapped target, not certified full-episode return-to-go.

The warm-up therefore delays shared-representation damage; it does not prevent it.

## Why the current evidence makes this worth testing

The following are consistent with, but do not prove, value-gradient damage:

- lower actor learning rate delayed erosion in `ppo-f2`;
- that multiplier applies to the trunk, including value gradients;
- `ppo-h` made undiscounted value fitting harder, logged explained variance around `0.25`, and had the worst update-500 scout (`3/48`, `112.8` points);
- fruit-chain commands decay while other behaviours remain, which is compatible with a shared feature representation moving.

## Decisive offline gradient decomposition

Use one exact saved post-warm-up minibatch and four identical copies of the same checkpoint. For each loss term separately, compute gradients without stepping:

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

Also report pairwise cosine similarity on the shared trunk: `P·V`, `E·V`, `A·V`, `P·E`, `P·A`.

Split P and V by PLAN versus TROLL rows and by fruit-chain versus other TROLL actions where applicable.

## Value-only counterfactual step

On another clone of the checkpoint:

1. apply exactly one optimiser step from `value_coef * value_loss` only;
2. run a fixed observation census before and after;
3. report:
   - parameter deltas by block;
   - spatial and plan logit KL;
   - argmax agreement;
   - agreement on fruit-chain rows;
   - change in clone-anchor KL.

This directly answers whether the value objective alone can move deployed actions at the observed learning rate.

Negative control: repeat with `pooled.detach()` only for the value branch; only `critic.*` may change and all policy logits must be byte-identical.

## Narrow matched-seed training control

If the offline result is material, add one recorded flag:

```text
--critic-trunk-grad on|off
```

For `off`, compute the value head from `pooled.detach()` during update-time loss construction. The forward value is numerically unchanged; only the gradient path into `stem.*` and `tower.*` is cut. Rollout values, GAE, policy loss, entropy, anchor, opponent, seed and every other setting remain unchanged.

Required tests:

- value-only backward gives nonzero `critic.*` gradients and zero trunk/head gradients when off;
- policy and anchor gradients still reach their intended parameters;
- checkpoint config records the flag;
- old behaviour is byte-identical under `on`.

Run `on` versus `off` at the same seed and the otherwise frozen best recipe. Do not combine it with temperature, entropy, lambda or curriculum changes.

## Relation to the source-backed curriculum

The winner's Level 4 froze the movement executor while training the plan selector and a separate end-score value head. A plan-only mode with the trunk and spatial actor frozen automatically blocks this value-gradient route into the executor. That makes it both a source-backed stage and a strong safety control.

## Recommendation

```text
MEASURE per-term trunk gradients before another explanatory long run.
TEST a value-only step on fixed observations.
IF material, run one matched-seed critic-trunk-gradient OFF control.
DO NOT assume the critic affects the actor only through advantages; the current code couples them directly.
```

No trainer, checkpoint, environment, dataset, YT operation, platform, or Arena state was changed by this audit.
