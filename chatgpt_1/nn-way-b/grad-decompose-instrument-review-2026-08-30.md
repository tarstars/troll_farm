# `grad_decompose.py` delivery review

Date: 2026-08-30
Agent: `chatgpt_1`
Task: `20260829-nn-bot-way-b`
Reviewed artifact: `agent/claude_1@c34265f99cbd5a6f1215ba9aa7e0d8d641a8817b`
Verdict: **GOOD INSTRUMENT, TWO REPAIRS BEFORE THE THREE-RUN VERDICT**

## What is strong

The delivery correctly:

- imports the trainer's actual observation, mask, GAE, optimizer and anchor functions;
- reconstructs the four objective terms on one minibatch;
- checks gradient linearity;
- reports per-block norms, trunk cosines and the global clip scale;
- restores PPO Adam moments for a realistic next value-only step;
- keeps the source checkpoint immutable;
- records hashes and effective configuration;
- distinguishes resumed Adam, fresh Adam and SGD;
- has a useful PLAN/TROLL contribution split.

## Blocker 1 — the clone baseline's optimizer layout is incompatible

The runbook's clone command leaves the default variants:

```text
adam-resumed,adam-fresh,sgd
```

`read_optimizer_state()` sees that the clone checkpoint has an `optimizer` key, so the resumed variant is attempted.

But the clone trainer saves:

```python
optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
```

which has **one parameter group**.

The PPO trainer and the instrument's `build_optimizer()` create **two parameter groups**:

```text
actor:  stem/tower/actor/plan
critic: critic.*
```

`optimizer.load_state_dict(clone_optimizer_state)` therefore raises a parameter-group mismatch. The current `adam-resumed` path does not catch that exception, so the whole clone measurement can terminate before writing JSON.

### Required repair

Make resumed-state compatibility explicit:

1. compare saved and rebuilt parameter-group counts and parameter counts before loading;
2. if incompatible, return a structured unavailable result:

```json
{
  "available": false,
  "reason": "optimizer layout incompatible: checkpoint=1 group, PPO=2 groups"
}
```

3. continue with `adam-fresh` and `sgd`;
4. add a test using a one-group clone checkpoint against the two-group PPO builder;
5. update the runbook: clone has no meaningful PPO-resumed counterfactual; quote resumed Adam only for g/h.

Do not remap the behaviour-cloning Adam moments heuristically. They came from a different loss and grouping, so even a technically possible remap would not be “the PPO step the clone would have taken.”

## Blocker 2 — own-policy rollouts cannot answer “is gamma 1 worse?”

The instrument collects a fresh rollout from each checkpoint. Same RNG seed aligns only the initial map/inventory/opponent schedule. The policies differ, so actions and subsequent states diverge.

The runbook acknowledges this, but its intended verdict still asks whether the value-gradient mechanism is worse under gamma 1 by comparing g and h side by side. Differences can come from:

- the checkpoint parameters;
- the checkpoint's state distribution;
- the gamma/lambda target;
- the optimizer moments;
- the actual objective gradients.

That is useful **on-policy context**, not a controlled gamma comparison.

### Required repair

Keep the existing on-policy reports, and add one shared fixed-state mode:

```text
--census-in <path>
--census-out <path>
```

A census contains at least:

```text
obs, legal, phase, actions, old_logprobs or explicit action source,
returns/advantages or the raw rollout fields needed to recompute them,
row provenance and SHA-256
```

Simplest bounded route:

1. collect one deterministic stratified 512-row census from the clone or a fixed union of clone/g/h rows;
2. save it once with PLAN/TROLL and fruit-chain coverage;
3. evaluate the three models and their value-only counterfactual steps on those **identical observations and masks**;
4. report on-policy and common-state results separately.

For the counterfactual, the common census only needs observations, masks and phases to compare before/after logits and choices. For per-objective gradients under a common batch, action/logprob/return semantics must be fixed and documented; do not silently reuse one model's behaviour log-probabilities as another model's on-policy PPO batch.

A minimal first repair can therefore provide:

```text
on-policy gradients per checkpoint
common-state before/after value-only logit and argmax changes
```

and reserve common-batch objective gradients for a separately defined off-policy diagnostic.

## Additional corrections

### Clone coefficients

The clone has no Phase-3 config. The current runbook says to add ppo-g flags manually but does not provide the exact command. Freeze a literal baseline command with the g recipe's maps, opponent, gamma/lambda, shaping, reward scale, rollout size and learning rates. Otherwise the clone row is measured under parser defaults and is not comparable.

### Report the actual resumed learning rates

After `optimizer.load_state_dict`, the saved parameter-group `lr` values may be annealed. The current report prints:

```text
args.learning_rate * args.actor_lr_scale
args.learning_rate
```

rather than `optimizer.param_groups[*]["lr"]` actually used by the resumed step. Report both base/configured and effective resumed rates.

### Name the counterfactual precisely

For g/h, resumed Adam at an update-500 checkpoint plus a newly collected minibatch is:

> the next hypothetical value-only step from the update-500 state

It is not the historical update-500 step. The current “the step the run would actually have taken” wording should be narrowed accordingly.

## Recommended execution order

```text
1. Repair incompatible optimizer handling and add the test.
2. Freeze the literal clone baseline command.
3. Run clone/g/h on-policy reports.
4. Save one common fixed observation census.
5. Run all before/after value-only models on that census.
6. Only then write the cross-checkpoint causal interpretation.
```

No training process, checkpoint, environment, YT operation, platform or Arena state was changed by this review.
