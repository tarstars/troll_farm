# `--train-scope plan-critic` fresh code review

Date: 2026-08-30
Agent: `chatgpt_1`
Task: `20260829-nn-bot-way-b`
Reviewed implementation: `main@213ee7f586a6a0fc6fda22bee9571159a3efdf0f`
Revision: r2 — adds phase-correct PPO diagnostics and target-KL semantics
Verdict: **BLOCKED AS A CLEAN LEVEL-4 / PLAN-ONLY EXPERIMENT**

## What the patch gets right

The new scope correctly keeps these parameter tensors byte-identical:

```text
stem.*
tower.*
actor.*
```

and leaves these trainable:

```text
plan.*
critic.*
```

The test proves the frozen tensors remain equal after warm-up plus PPO updates. This closes the direct value-gradient route into the executor parameters.

## Why the current run would still answer the wrong question

The patch changes only `requires_grad`. It does not change rollout action selection or the loss population.

### 1. TROLL actions are still sampled from the weak behaviour policy

The rollout loop remains unconditional for every phase:

```python
distribution = Categorical(logits=masked_logits(logits, legal_t))
actions = distribution.sample()
```

The accepted decoding factorial already says:

```text
argmax plan + argmax commands:   9/48, 133.8
sampled plan + argmax commands:  8/48, 133.2
argmax plan + sampled commands:  3/48, about 109
```

So `ppo-i` as implemented does not train a plan selector on top of the 9/48 deployed clone executor. It trains a plan selector on top of the 3/48 temperature-1 command-sampling executor, then evaluates the result with argmax commands.

The coordinator's statement that “the bench floor is the clone's own play” is therefore false under the current code. The executor weights are the clone's, but the behaviour policy is not the clone used by the gate.

### 2. TROLL rows still dilute PLAN advantage normalization

The update loop normalizes advantages over the complete mixed minibatch:

```python
mb_advantages = (mb_advantages - mb_advantages.mean()) / (
    mb_advantages.std() + 1e-8
)
```

Then it averages policy loss over every row.

Frozen TROLL rows have no policy gradient path to `plan.*`, but their advantages still determine the PLAN rows' centering and scale. The effective PLAN gradient therefore changes when the same PLAN data is accompanied by a different number or distribution of TROLL rows.

Since one turn contributes one PLAN row and one TROLL row per own troll, the plan optimiser's effective objective becomes roster-dependent.

### 3. TROLL rows dilute entropy, anchor and PPO diagnostics

The code computes:

```python
entropy_loss = entropy.mean()
approx_kl = (((ratio - 1) - log_ratio).mean())
clip_fraction = (...).mean()
```

over all phases.

With a plan-bearing anchor, `keep` is all rows and `anchor_kl` also returns a mean over all kept rows.

Frozen TROLL rows do not update the frozen executor, but they remain in all these denominators. Consequences:

- plan entropy and anchor gradients are scaled by the stochastic PLAN/TROLL mixture;
- `approx_kl` is diluted by frozen TROLL rows whose ratio remains one;
- `clip_fraction` is diluted the same way;
- the `target_kl` early-stop decision can fail to fire even when PLAN KL alone exceeds the threshold;
- the logged diagnostics do not describe the only policy that is actually trainable.

### 4. The critic still competes with the plan head through global clipping

The trunk is now frozen, so value loss cannot move it. But the trainer still performs:

```python
loss.backward()
clip_grad_norm_(model.parameters(), 0.5)
```

as one combined operation.

A large `critic.*` gradient can consume the global norm budget and scale down `plan.*` gradients. Thus plan and value remain coupled even though they share no trainable parameter. This may be measured first rather than changed immediately, but it must be named in the run interpretation.

## Minimum repair before `ppo-i`

### Rollout semantics

Under `train_scope == "plan-critic"`:

```text
PLAN phase:  sample from the trainable plan distribution
TROLL phase: masked argmax from the frozen executor
```

TROLL actions still enter the environment and staged prefix, but they are not PPO policy samples.

This is a project-specific Level-4 definition: the source says the movement network was frozen but does not state its action-selection temperature. Argmax is justified here because it is the measured stronger clone and the submitted policy.

### Loss population

Define `policy_rows = (mb_phase == PHASE_PLAN)`.

On `policy_rows` only:

- normalize policy advantages;
- compute old/new log-probabilities and ratios used by the policy objective;
- compute PPO policy loss;
- compute entropy;
- compute anchor KL and top-1 agreement;
- compute `approx_kl` and `clip_fraction`;
- apply `target_kl` early stopping.

Let value loss use all rows. If a minibatch has zero PLAN rows, run value loss only and do not update the PLAN policy diagnostics from that minibatch.

This makes the plan objective and its stopping rule invariant to how many frozen TROLL rows happen to accompany it.

### Value branch and clipping

The frozen trunk already prevents value gradients from changing executor weights. For a clean instrumented run, at minimum log:

- pre-clip `plan.*` norm;
- pre-clip `critic.*` norm;
- joint clip multiplier;
- whether clipping fired.

Prefer separate plan/critic clipping if the gradient falsifier shows critic domination. Do not silently bundle that change before the measurement.

## Required tests

1. Existing frozen-parameter byte-identity test.
2. **TROLL determinism:** changing the Torch RNG seed cannot change any TROLL action in plan-critic mode; PLAN draws remain seeded and stochastic.
3. **Executor parity:** plan-critic TROLL actions equal `bench.py` argmax commands on the same observation/mask/staged prefix.
4. **Population invariance:** duplicate arbitrary frozen TROLL rows around the same PLAN rows; normalized PLAN advantages, `plan.*` policy gradient, `approx_kl`, `clip_fraction`, entropy and target-KL decision remain equal.
5. **Anchor invariance:** duplicating TROLL rows cannot change plan-anchor KL or its gradient.
6. **No-PLAN minibatch:** value parameters may move; plan parameters and policy diagnostics remain unchanged/empty.
7. Checkpoint config records `train_scope`, `troll_decoding = argmax`, and the PLAN-row fraction.

## Interpretation after repair

The repaired experiment asks:

> Can a stochastic plan selector, trained on end score, improve the fixed deployed clone executor?

The current patch asks instead:

> Can a plan selector improve a weak sampled executor, while its gradient scaling and stopping diagnostics depend on how many frozen troll rows are mixed into each minibatch?

Those are not equivalent.

## Recommendation

```text
DO NOT START ppo-i from main@213ee7f5.
KEEP the parameter-freeze implementation.
ADD phase-specific rollout semantics and PLAN-only policy/entropy/anchor/KL calculations.
RUN the focused invariance tests.
THEN start ppo-i with the exact config pinned.
```

No training process, checkpoint, environment, YT operation, platform or Arena state was changed by this review.
