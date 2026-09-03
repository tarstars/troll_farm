# Adversarial second opinion on the self-play experiment

Date: 2026-08-31
Agent: `chatgpt_1`
Reviewed dossier: `main@f9595b53066903cce8f1104bc915420b3650b484`
Reviewed file: `local_claude_1/nn-bot/EXPERIMENT-2026-08-31.md`
Code read against the same commit:

- `local_claude_1/nn-bot/train_ppo_full.py`
- `rust/src/rl_full.rs`
- `cgauto/train_level1_ppo.py`

## Technical verdict

The dossier is unusually good: it is self-contained, distinguishes the clone from PPO, records the failed runs instead of hiding them, and correctly retracts several earlier causal stories.

The diagnosis is nevertheless **not complete**. Two of its central interpretations need correction before more compute is attributed causally:

1. **The gamma/lambda discussion omits rollout truncation.** GAE is recomputed inside a buffer of only 32 learner mini-steps per environment. A terminal reward cannot directly trace through 50 or 300 game turns in this implementation, even with `(gamma, lambda) = (1, 1)`. Beyond roughly 6-16 game turns, depending on the troll count, credit is carried only by the critic bootstrap.
2. **The anchor did not materially fade during run I.** With 4,096 decisions per update and a `0.1 -> 0.05` schedule over 100 million decisions, its coefficient was about `0.09898` at update 500 and `0.09488` at update 2,500. It never approached `0.05`. Run I therefore does not support the statement that it held while the leash was strong and drifted when the leash faded.

The two surviving explanations in section 11 should become at least four:

- short-rollout bootstrapping plus noisy critic targets;
- per-minibatch normalization amplifying those noisy advantages;
- entropy and stochastic plan exploration softening a distilled plan policy whose deployment is argmax;
- value gradients changing the shared trunk in full-parameter runs.

The anchor can still be intrinsically too weak, but **anchor decay is not yet the measured cause**.

---

## 1. Blocking correction: the real credit horizon is the rollout, not 300 turns

The dossier's local GAE arithmetic is correct. At a turn boundary:

```python
delta_discount = gamma
trace_factor = gamma * gae_lambda
```

and the trace is exactly 1 inside the artificial mini-steps of one turn.

The missing fact is where that recurrence stops. The trainer allocates:

```python
RolloutBuffer(rollout_steps=32, num_envs=128)
```

then calls `compute_gae(...)` once and supplies one `next_value` bootstrap at the end of those 32 mini-steps. `last` is initialized to zero for every update; no eligibility trace is carried into the next rollout.

One game turn costs:

```text
1 PLAN mini-step + one TROLL mini-step per own troll
```

Therefore 32 mini-steps cover at most:

| own trolls | game turns represented by 32 mini-steps |
|---:|---:|
| 1 | 16 |
| 2 | about 10.7 |
| 3 | 8 |
| 4 | about 6.4 |

The clone buys a second troll in 44 of 48 scout games, so the practical direct trace is usually around 8-11 turns and becomes shorter as the roster grows.

### Consequence

The dossier's example that a terminal reward reaches a move 50 turns earlier with weight about `0.077` describes an uninterrupted mathematical trace, not this training run. In the actual run, a move 50 turns earlier can learn only through a sequence of critic bootstraps across several rollout boundaries.

A `(gamma, lambda) = (1, 1)` run with the same 32-step buffer is therefore **not an undiscounted 300-turn policy-credit experiment**. It is an undiscounted, at-most-32-mini-step return with a learned value bootstrap at the cut.

### Required interpretation change

```text
KEEP: gamma=1, lambda=.95 was a gamma-only sensitivity.
ADD: lambda=1 with rollout_steps=32 is still a short-horizon bootstrapped test.
DO NOT call the long-horizon axis tested until the trace spans a material fraction of an episode.
```

### Cheapest useful work

Before another 60-million-decision job, log for each update:

- number of terminal transitions in the rollout;
- fraction of policy rows whose GAE trace contains an actual terminal reward before the buffer cut;
- distance in game turns to that terminal;
- raw advantage mean/std before normalization;
- bootstrap value share versus observed reward share in the return target.

Then do an offline comparison on saved rollouts for lambda `.95` and `1.0`. This is useful, but it still answers only the within-buffer question.

A true long-horizon experiment needs one of:

- much longer rollouts, with fewer parallel environments if memory is the constraint;
- complete-episode trajectories and Monte-Carlo/GAE returns;
- a trace explicitly carried across rollout chunks;
- an auxiliary terminal-return head trained from completed games.

Do **not** spend cluster time on `(1,1)` alone under the present 32-step buffer and call it the long-horizon answer.

---

## 2. Blocking correction: run I's anchor barely changed

The trainer computes:

```python
fraction = turn_steps / anchor_decay_steps
coef = initial + (final - initial) * fraction
```

Run I uses:

```text
batch size              = 128 * 32 = 4,096 decisions/update
anchor                   = 0.1 -> 0.05
anchor_decay_steps       = 100,000,000 decisions
```

The actual coefficient is therefore:

| update | decisions | anchor coefficient |
|---:|---:|---:|
| 500 | 2,048,000 | 0.098976 |
| 1,000 | 4,096,000 | 0.097952 |
| 1,500 | 6,144,000 | 0.096928 |
| 2,000 | 8,192,000 | 0.095904 |
| 2,500 | 10,240,000 | 0.094880 |
| 2,650 | 10,854,400 | 0.094573 |

Run I's 9 -> 10 -> 9 -> 6 -> 5 curve happened while the anchor remained between about `0.099` and `0.095`. That is a five-percent reduction in the coefficient, not an approach to `0.05`.

### Consequence

Section 11(b) is not supported as written. The evidence can support:

> The on-policy KL anchor at approximately 0.1 is insufficient to stop slow plan-mode drift.

It cannot yet support:

> The plan drifts because the anchor fades.

The fixed-0.1 cluster arm `i2` is still worth keeping, but its early treatment difference from run I is tiny. At update 2,500 it compares `0.1000` with `0.0949`. A positive result would say that even a small increase matters, or that a longer-run divergence eventually matters; a negative result would not acquit the anchor mechanism.

Also correct this sentence in the dossier:

> Wins are about 2% of champion games, so clone habits are never reinforced by return.

Run I's own champion-only telemetry was about 18-21% wins, and the reward is score margin, not a binary win. Losing games still carry graded relative returns. The signal may be noisy or badly credited, but it is not literally absent.

---

## 3. Missing leading cause: entropy plus plan sampling changes the policy being optimized

The repaired staged scope fixed the largest executor mismatch:

- PLAN rows sample;
- TROLL rows use masked argmax;
- only PLAN rows contribute to policy loss, entropy and anchor.

That is a sound Level-4-like experiment. One important train/deploy mismatch remains:

```text
training plan policy   = categorical sample
bench/deployment plan  = argmax
```

The clone factorial says plan sampling initially costs little. That does **not** prove the mismatch stays harmless after PPO. Run I's plan entropy rose from `0.90` to `1.35` while its argmax bench drifted.

At the exact clone:

- anchor KL has zero gradient;
- entropy has nonzero gradient toward a flatter distribution;
- PPO return gradients are weak and bootstrapped;
- the plan space has 400 legal candidates, while the teachers used only 106 distinct targets.

The entropy term is therefore a direct, persistent force that can move probability mass onto poorly supervised or unseen targets even when PPO has little reliable preference signal.

### The plan is also reselected without explicit memory

The environment retains `main_plan` between turns if it was not trained, but every new PLAN action overwrites it. At PLAN phase the sanitizer zeroes planes 59-71 and 98 before the model sees them. Thus the selector cannot observe the prior target and the scorer's "matches previous target" feature is effectively disabled.

The winner explicitly included previous-target matching in the candidate features. Our staged learner instead samples a fresh target every turn without seeing the previous one, then deploys the mode of that distribution.

That can create:

- sampled target thrashing during training;
- a policy optimized under trajectories different from argmax deployment;
- slow movement of the argmax between nearly tied plans;
- entropy-driven exploration of unsupported 400-way candidates.

### Decisive diagnostics

For clone and every run-I checkpoint, report:

- plan top-1 probability and top-2 logit/probability margin;
- entropy and effective number of plans `exp(entropy)`;
- sampled-versus-argmax disagreement;
- selected plans inside versus outside the 106 teacher-supported targets;
- target switches per game before a purchase;
- argmax-plan bench and sampled-plan bench on the same games.

### Cheapest causal arm

Run one same-seed staged arm with:

```text
entropy_coef = 0
all other run-I settings unchanged
```

Do not bundle it with a fixed anchor or lower learning rate. `i2` tests the anchor treatment; a separate entropy-zero arm tests the softening force.

A stronger later repair is to restore target commitment: expose a safe previous-target feature to the plan scorer, or keep a selected target until purchase/cancel rather than asking for an independent target every turn.

---

## 4. Missing leading cause: normalized bootstrap noise has full policy scale

After shaping is removed, observed reward is terminal. A 4,096-row update contains 128 trajectories of only 32 mini-steps each. With roughly 300 game turns and multiple mini-steps per turn, only a small number of episodes finish inside any one update.

Most policy rows therefore receive advantages dominated by:

```text
critic bootstrap differences + TD residuals
```

rather than by a terminal score observed in the same buffer.

The trainer then normalizes advantages separately in every minibatch:

```python
adv = (adv - adv.mean()) / (adv.std() + 1e-8)
```

This is usually a good PPO convention. Here it has a dangerous implication: even if the raw TD signal is tiny and mostly critic noise, it is rescaled to unit variance and receives a full-sized policy update. Critic warm-up can reduce the noise but cannot certify that the ordering of advantages is correct.

This mechanism is consistent with all observations:

- warm-up delays erosion but does not remove it;
- lower actor learning rate delays erosion;
- full-parameter runs destroy multi-step executor behavior;
- staged policy drifts more slowly because only one small head sees the normalized signal.

### Instrument it before changing it

Log per update and separately for PLAN/TROLL rows:

- raw advantage std and quantiles;
- fraction of signs changed by switching lambda `.95 -> 1`;
- correlation with complete-episode Monte-Carlo returns where available;
- terminal-bearing versus bootstrap-only rows;
- gradient norm before and after normalization.

Then compare, same seed:

1. current per-minibatch normalization;
2. one normalization over the full rollout;
3. no normalization, with an explicitly adjusted learning rate.

This is a better causal experiment than changing reward scale. Positive reward scaling is mostly removed from the actor by normalization; it mainly changes critic fitting and gradient clipping.

---

## 5. The critic evidence is not yet an independent validation of value quality

The logged `explained_variance` is computed between:

```text
stored rollout values
GAE returns = stored values + computed advantages
```

Those returns themselves use the same value predictions and the end-of-rollout bootstrap. High explained variance against this target does not prove that the critic predicts actual final margin or complete-episode return-to-go.

The needed critic gate is independent:

- freeze a checkpoint;
- play complete held-out episodes;
- record every visited state;
- compute realized Monte-Carlo return-to-go from the final score;
- evaluate value calibration, rank correlation and explained variance by game turn, map size, seat and score regime.

The shared-trunk gradient instrument is still valuable. Its conclusion should be based on:

- fixed common observations for clone/G/H;
- compatible optimizer handling;
- actual resumed learning rates;
- command/plan argmax flips after a value-only step.

If the value-only step materially changes action logits or top-1 commands, a separate value encoder or a detached value branch ranks above another ordinary full-parameter PPO run.

For staged `plan-critic`, the trunk is frozen, so the value term cannot change executor features. It can still suppress plan updates through the joint global clip. The new pre-clip plan/critic norms and clip multiplier should decide whether separate optimizers/clipping are needed.

---

## 6. Target-KL is not currently a reliable trust-region control

Inside the minibatch loop, `approx_kl` is overwritten on every minibatch. After an epoch, the early-stop test uses only the value left by the **last minibatch**:

```python
if target_kl > 0 and approx_kl > target_kl:
    break
```

The logged `approx_kl` is likewise the final minibatch's value, not an epoch mean or maximum.

In staged mode, a last minibatch with no or unusually easy PLAN rows can report zero/small KL even if earlier PLAN minibatches moved substantially. Conversely, one noisy final minibatch can stop the epoch.

This is probably not the primary erosion cause, but it means target-KL cannot presently be cited as a dependable safety mechanism.

Repair it by accumulating PLAN-row KL weighted by PLAN-row count over the epoch, logging mean/max, and applying the preregistered rule to that aggregate.

---

## 7. The 48-game bench is a scout, not a selector with +/-2-win precision

For the clone, `p = 9/48 = 0.1875`. Under an independent-binomial approximation:

```text
SD of the win count = sqrt(48 * p * (1-p)) = 2.70 wins
approximate 95% half-width = 1.96 * 2.70 = 5.3 wins
```

So the dossier's "+/-2 wins" wording is too optimistic, and `2.7` is wins, not "points of score". The Wilson 95% interval for the win rate is roughly 10%-32%.

The repeated panel is also not an independent binomial sample: checkpoints play the same map-seat cells and are highly correlated. That is useful because it permits **paired** analysis, but raw win totals discard the pairing.

### Recommended evaluation protocol

- Keep the present 48-game panel for cheap scouting and behavioral diagnostics.
- Compare candidate versus clone on the same map/seat/inventory cells using paired score-margin differences, paired win changes and a paired bootstrap/randomization interval.
- Do not select many checkpoints and then treat the best result on the same 24 maps as confirmation.
- Maintain a second locked panel for confirmation.
- When a scout passes a preregistered threshold, run 144-192 games for confirmation; reserve the 400-game champion/orchard gates for a candidate that has already passed.

Replace "two consecutive 48-game reads at least the clone" with a rule such as:

```text
scout: paired mean margin is positive versus clone and no behavioral guardrail fails
confirmation: lower paired confidence bound is non-negative on a locked >=144-game panel
```

The final 400-game gate remains the actual promotion gate.

---

## 8. Direct answers to the six questions

### 8.1 Is the diagnosis complete?

No. The dossier misses or underweights:

1. **rollout truncation**: direct policy credit stops after 32 mini-steps;
2. **normalized bootstrap noise**: weak TD ordering is rescaled to unit policy variance;
3. **entropy-driven plan softening** under sparse return;
4. **fresh target sampling without previous-target memory**;
5. **400-way exploration beyond teacher support**;
6. **critic validation against its own bootstrapped target rather than realized returns**;
7. **target-KL using only the last minibatch**;
8. **low effective independent sample size**: thousands of rows, but only a few completed games per update.

The shared-trunk value-gradient mechanism remains credible and should be measured.

The listed Adam-moment-staleness hypothesis is not credible for the actor: `load_policy` restores model weights only, then `build_optimizer` creates a fresh PPO Adam. Policy parameters are frozen during warm-up and have no accumulated PPO moments until they are enabled. Critic moments do accumulate during warm-up, which is intended.

### 8.2 Is the gamma/lambda accounting right, and is `(1,1)` worth cluster time?

The local recurrence is right. The operational conclusion is incomplete because the recurrence is truncated after 32 mini-steps.

`(1,1)` is worth a cheap offline or short pilot under the current buffer, but **not** a large cluster run advertised as the long-horizon answer. A real test must also lengthen or stitch the rollout so observed terminal reward can reach early decisions without crossing dozens of critic bootstraps.

### 8.3 Does staged scope still train a different problem?

The repaired TROLL/PLAN loss population is correct. Remaining differences are:

- plans sample in training but use argmax in deployment;
- the plan is reselected every turn while previous-target planes are sanitized away;
- entropy acts over a 400-way plan space with limited teacher support;
- critic and plan gradients still share one global clip;
- target-KL is based on the last minibatch only;
- the anchor is evaluated only on current on-policy states, not a fixed clone/teacher state census.

The first two are the most important semantic holes.

### 8.4 Should reads move to 96/144 games and should the run-of-record rule change?

Yes, but in two stages:

- 48 games remains the scout;
- 144-192 locked games is the confirmation;
- 400+400 remains the promotion gate.

Use paired differences, not independent binomial win counts. Two consecutive reads on the same 48 cells do not control multiple checkpoint selection and are strongly correlated.

### 8.5 Rank the next lever if i2 holds but does not climb

1. **Finish the diagnostics first**: fixed-state gradient decomposition, independent critic calibration, raw-advantage/terminal-bootstrap census.
2. **Same-seed staged entropy ablation**: `entropy_coef=0`, nothing else changed. This directly tests the observed softening.
3. **True long-horizon staged credit**: longer/episodic rollouts plus lambda 1, not lambda 1 alone.
4. **Separate or detach the value trunk** if the value-only counterfactual materially changes actions; separately clip/optimize plan and critic if the staged logs show critic domination.
5. **Restore target commitment or previous-target matching**, then retrain/continue the plan head.
6. **Only then attempt a tiny-rate joint fine-tune**, with a fixed replay behaviour-cloning loss on TROLL rows so executor retention is a hard objective, not only an on-policy KL.
7. Reward reshaping, margin clipping or win bonuses come last: they change the objective and can be gamed.

Do not unfreeze from I@1000 merely because it scored 10/48. That reading is within scout noise and full-parameter PPO has repeatedly destroyed the executor.

### 8.6 Does the data or clone cap the ceiling?

The highest-priority data/representation issue is the plan target, not MOVE:

- 67% "nothing" makes headline plan accuracy misleading;
- only 106 of 400 targets appear in teachers;
- four teachers contribute incompatible styles without a style variable;
- there is no held-out-game calibration on this first clone;
- previous-target matching is absent at PPO PLAN time;
- sampled plan exploration can leave the teacher-supported set.

Before another clone, report:

- plan accuracy/calibration conditional on "a purchase remains";
- per-teacher and held-out-game metrics;
- support frequency of PPO-selected plans;
- top-1 margin and entropy;
- purchase-target switch rate.

A useful cheap clone comparison is strongest-teacher-only versus mixed-teacher, with a game-level holdout and the same external bench.

The 400-way vocabulary itself is not obviously too large; the problem is unrestricted exploration and weak supervision over most entries. Reached-cell MOVE labels are a reasonable one-turn imitation target for a policy that replans every turn. They discard long-range intent, but they rank below plan consistency and credit assignment.

---

## 9. Recommended immediate amendments to the experiment record

Change these claims before the dossier is treated as the causal summary:

```text
OLD: terminal credit reaches a move 50 turns earlier at weight about .077.
NEW: that coefficient assumes an uninterrupted trace; the implementation truncates at 32 mini-steps and bootstraps through the critic beyond roughly 6-16 turns.

OLD: run I drifted as the anchor approached .05.
NEW: run I drifted while the anchor remained about .099 -> .095; decay is not established as the cause.

OLD: one 48-game bench has about +/-2-win noise.
NEW: the independent-binomial SD is 2.7 wins and an approximate 95% half-width is 5.3; use paired cell-level analysis for checkpoint comparisons.

OLD: only two explanations remain.
NEW: short-rollout bootstrap credit, normalized TD noise, entropy/plan-mode drift, on-policy anchor weakness and shared-trunk value gradients all remain open.
```

## Bottom line

The staged architecture is the right direction, and the full-parameter collapse is real. The next job should not be another broad PPO recipe sweep.

The strongest current causal order is:

```text
short rollout + critic bootstrap
        -> noisy advantages
        -> per-minibatch normalization gives them full policy scale
        -> entropy and PPO move a soft 400-way plan distribution
        -> on-policy KL near .1 is insufficient to preserve the deployed argmax mode
        -> in full scope, value gradients additionally move the executor trunk
```

That chain is consistent with every recorded run and makes several cheap, one-factor predictions. Test those predictions before joint fine-tuning or reward redesign.

No trainer, environment, checkpoint, dataset, YT operation, platform, Arena or ladder state was changed by this review.
