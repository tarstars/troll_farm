# Shared critic-to-actor trunk audit

Date: 2026-08-30
Agent: `chatgpt_1`
Programme: `20260829-nn-bot-way-b`
Reviewed code: `main@e02e88c8afadc31dc16109ed85eb3c547913943e`

## Verdict

Every current Phase-3 run shares one unisolated destructive path: **after the critic warm-up, the value loss updates the same convolutional trunk that produces both spatial-action and plan logits**.

Therefore a poorly fitted or collapsing value estimator can change the policy even when:

- the policy loss is small;
- the actor learning rate is reduced;
- the clone anchor is present;
- the action and plan heads themselves would otherwise stay near the clone.

This is a code-path fact, not yet a causal verdict. It should be measured before attributing the common erosion shape only to opponent mix, gamma, or curriculum.

## Load-bearing code path

`SpatialActorCritic` has one shared `stem` + residual `tower`. The spatial actor consumes `hidden`, while the plan head and critic consume `pooled` from the same trunk:

```text
hidden, pooled = shared trunk(observation)
spatial logits = actor(hidden)
plan logits    = plan(pooled, ...)
value          = critic(pooled)
```

In `train_ppo_full.py`:

1. `is_critic_parameter()` returns true only for names beginning `critic.`.
2. The shared `stem.*` and `tower.*` parameters are classified in the **policy** optimizer group.
3. During warm-up those policy parameters are frozen, so only the small critic head learns.
4. Immediately after warm-up the trunk is re-enabled.
5. The ordinary loss contains `value_coef * value_loss` together with policy, entropy and anchor terms.
6. `loss.backward()` therefore sends the value-loss gradient through `critic -> pooled -> shared trunk`.
7. One global gradient clip is applied before the optimizer step.

`--actor-lr-scale 0.3` reduces the learning rate of the trunk, but it does not remove this value-gradient path.

## Why it matches the live evidence

Across runs the multi-step fruit executor decays while immediate chopping survives. In `ppo-h` the value estimate's explained variance fell to about `0.25`, while the action distribution shifted toward more MOVE and fewer PICK/PLANT operations.

A failing value target flowing through shared features is consistent with that pattern. It is not proved to be the cause because PPO, entropy and anchor gradients act at the same time. The present logs do not separate them.

The issue also explains why the critic warm-up can delay rather than eliminate erosion: the warm-up protects the trunk only for its first `N` updates. Once joint training starts, the value loss can move it again.

## Cheapest decisive diagnostic

On one captured post-warm-up minibatch, compute gradients separately for:

- clipped PPO policy loss;
- entropy bonus;
- clone-anchor KL;
- value loss.

Report, for `stem`, `tower`, spatial actor, plan head and critic head:

1. gradient norm per objective term;
2. cosine similarity between value and policy gradients;
3. global-clip scale when all terms are combined;
4. PLAN versus TROLL rows;
5. fruit-chain rows versus all other troll rows.

Then run one **value-only counterfactual optimizer step** from the same model and minibatch, with the trunk trainable exactly as in current PPO. Compare before/after:

- spatial and plan logit deltas;
- masked top-1 agreement;
- fruit-chain action probabilities.

If a value-only step materially changes action decisions, the shared critic path is directly demonstrated.

## Training implication if demonstrated

The closest bounded fix is the same staged structure supported by the delineate source audit:

- freeze `stem`, `tower` and spatial actor while fitting the critic and plan selector;
- or stop value gradients at pooled trunk features while fitting the critic head;
- train the plan selector/value head first;
- unfreeze the executor only in a separately gated fine-tune, with a fixed-reference troll-row loss.

A separate critic trunk is another option, but it changes the architecture and export budget more substantially.

## Recommendation

```text
DO NOT infer the common erosion mechanism from gamma alone.
ADD value loss to the offline gradient decomposition.
MEASURE one value-only counterfactual step before another all-parameter long run.
PREFER plan/value training with the executor trunk frozen if the path is confirmed.
```

No trainer, checkpoint, environment, dataset, YT operation, platform, or Arena state was changed by this audit.
