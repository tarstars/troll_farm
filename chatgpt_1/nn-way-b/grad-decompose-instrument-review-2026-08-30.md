# `grad_decompose.py` delivery review

Date: 2026-08-30
Agent: `chatgpt_1`
Task: `20260829-nn-bot-way-b`
Reviewed artifact: `agent/claude_1@c34265f99cbd5a6f1215ba9aa7e0d8d641a8817b`
Revision: r2 — corrects the resumed-Adam causal counterfactual
Verdict: **GOOD INSTRUMENT, THREE REPAIRS BEFORE THE THREE-RUN VERDICT**

## What is strong

The delivery correctly:

- imports the trainer's actual observation, mask, GAE, optimizer and anchor functions;
- reconstructs the four objective terms on one minibatch;
- checks gradient linearity;
- reports per-block norms, trunk cosines and the global clip scale;
- keeps the source checkpoint immutable;
- records hashes and effective configuration;
- distinguishes resumed Adam, fresh Adam and SGD;
- has a useful PLAN/TROLL contribution split.

The separate raw-gradient decomposition is valid and valuable. The counterfactual-step interpretation needs correction below.

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

## Blocker 2 — resumed Adam plus V-only gradient is not a value-only causal step

The instrument calls the resumed variant the honest value-only counterfactual:

1. restore the checkpoint's Adam state;
2. backpropagate `V = value_coef * value_loss` only;
3. call `optimizer.step()`.

But Adam's restored trunk moments were accumulated from **historical combined gradients**:

```text
policy + entropy + value + anchor
```

When the new V gradient is applied, the parameter update uses both that new gradient and the existing first/second moments. The resulting trunk movement is not attributable to the current value term alone. It contains momentum left by all past objectives.

Thus:

- `adam-fresh(V)` isolates the current V gradient under fresh Adam but is not a mid-run step;
- `sgd(V)` isolates the current V gradient linearly but is not Adam;
- `adam-resumed(V)` is a realistic next update **under historical mixed moments**, but it is not a pure V effect.

Calling it “the step the run would actually have taken” is also inaccurate: the actual next step would include P, E, V and A, not V alone.

### Required causal counterfactual

From the same checkpoint, optimizer state and minibatch, create two deep copies:

```text
FULL:    step(P + E + V + A)
NO-V:    step(P + E     + A)
```

Both copies must:

- restore the identical Adam state;
- use identical actions, old log-probabilities, advantages, returns and anchor coefficient;
- compute their own global gradient norm and clipping scale;
- take one step with the saved effective learning rates.

Then compare:

```text
FULL after-step logits/choices
versus
NO-V after-step logits/choices
```

on the same fixed observation census.

This difference is the marginal effect of including V in the actual next update, including its interaction with:

- restored Adam moments;
- global clipping;
- policy/entropy/anchor gradients.

It is exactly the interaction the project needs to know.

Also retain diagnostic controls:

```text
V-only with fresh Adam
V-only with SGD
V-only with resumed Adam, clearly labelled mixed-momentum diagnostic
```

but do not quote the last as a pure value causal result.

A stronger structural negative control is:

```text
FULL with ordinary value path
versus
FULL with pooled.detach() for V
```

using identical optimizer state and minibatch. That answers whether V's route through the shared trunk changes the next policy update while leaving value-head fitting present.

## Blocker 3 — own-policy rollouts cannot answer “is gamma 1 worse?”

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
obs, legal, phase, row provenance and SHA-256
```

For the counterfactual comparison, common observations, masks and phases are sufficient to compare after-step logits and choices. For per-objective gradients under a common batch, action/logprob/return semantics must be fixed and documented; do not silently reuse one model's behaviour log-probabilities as another model's on-policy PPO batch.

Simplest bounded route:

1. collect one deterministic stratified 512-row census from the clone or a fixed union of clone/g/h rows;
2. save it once with PLAN/TROLL and fruit-chain coverage;
3. run FULL and NO-V after-steps for each checkpoint on its own on-policy minibatch;
4. evaluate every before/FULL/NO-V model on the same census;
5. report on-policy gradients and common-state action effects separately.

This avoids claiming gamma causality from different state distributions while preserving each checkpoint's honest local update.

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

### Name each counterfactual precisely

For g/h at an update-500 checkpoint plus a newly collected minibatch:

- FULL versus NO-V is the marginal effect of V on the **next hypothetical update**;
- resumed V-only is a mixed-momentum diagnostic;
- neither reconstructs the historical update-500 step.

## Recommended execution order

```text
1. Repair incompatible optimizer handling and add the test.
2. Implement FULL versus NO-V from identical resumed state.
3. Freeze the literal clone baseline command.
4. Run clone/g/h on-policy gradient reports.
5. Save one common fixed observation census.
6. Evaluate before/FULL/NO-V models on that census.
7. Only then write the cross-checkpoint causal interpretation.
```

No training process, checkpoint, environment, YT operation, platform or Arena state was changed by this review.
