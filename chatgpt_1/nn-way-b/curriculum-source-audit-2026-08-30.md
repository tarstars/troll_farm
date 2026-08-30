# Curriculum source audit and next-stage recommendation

Date: 2026-08-30
Agent: `chatgpt_1`
Programme: `20260829-nn-bot-way-b`
Reviewed main: `e02e88c8afadc31dc16109ed85eb3c547913943e`
First-hand source: `local_claude_1/reconstructions/sources/delineate-gist.github.com-2026-05-25.md`

## Verdict

The card's proposed next lever — **short games and small maps first, implemented as a training-time episode cap** — is not delineate's recorded curriculum.

It can be tested as a project invention, but it must not be attributed to the winner, and it is not the closest next step to the mechanism described in his first-hand write-up.

The closest source-backed next stage is **parameter- and task-staged training**:

1. verify or train the troll-action policy as an executor of an externally supplied build target;
2. freeze that executor while training the plan selector and a value head on the real endgame objective;
3. only then fine-tune all parameters together.

Our current Phase 3 jumps directly from imitation into joint end-to-end PPO over the trunk, spatial actor, and plan head. That is closer to delineate's unsuccessful initial attempt than to the staged procedure he says made the final bot work.

## What delineate actually reports

The first-hand source describes:

### Level 1 — one specified target troll

The environment specifies a unit target, such as `3/4/0/1`. The policy receives dense positive/negative reward when its estimated number of turns to collect the missing resources decreases/increases.

### Level 2 — random assigned targets, automatic TRAIN

When no target exists, the environment samples one. The target and resource deficits are visible in the observation. When resources become sufficient, the environment automatically executes the corresponding TRAIN and assigns another target. The policy still does not choose the plan.

### Level 3 — random target troll count and real score

The environment samples a target number of trolls between 2 and 5, retains the build-target shaping, adds actual endgame score difference, and temporarily helps discover chopping. At the end of this level, the movement/action policy can execute an assigned build order and use the resulting units.

### Level 4 — freeze movement, train plan selector

The action/movement network is frozen. A new plan-selector policy head and a different value head are trained using actual endgame score difference with no shaping. The explicit reason is to prevent the target-completion shaping from being gamed by selecting cheap targets.

### Level 5 — fine-tune everything

Only after the executor and plan selector work separately are all parameters fine-tuned together on the real endgame objective.

The source does not describe a small-map curriculum, a short-game curriculum, or a training-time episode cap.

## Why this matters for the present failure

The observed failure is unusually consistent:

- purchases often remain;
- chopping survives longer;
- `PICK` / `PLANT` / `HARVEST` / `DROP` chains decay;
- changing opponent mix, shaping, gamma, warm-up, and actor learning rate has delayed but not removed the decay.

That is compatible with destructive updates to the shared executor, especially because the current PPO stage updates:

- the shared convolution trunk;
- the spatial action head;
- the plan head;
- the value head;

at the same time after critic warm-up.

The clone already supplies something like a Level-3 executor, but this has not been isolated and protected. A KL anchor is not the same as freezing it: at the exact clone the anchor KL has zero gradient, while the PPO and entropy terms can immediately move the shared policy. As the anchor decays, it protects even less.

## Risk in an episode-cap-only curriculum

A training-time episode cap can be a useful independent experiment, but its semantics must be chosen explicitly:

- Treating the cap as a terminal and scoring the partial board changes the objective toward short-horizon play.
- Treating it as a truncation requires a value bootstrap, exactly where the current value estimate is unstable.
- Sampling only small maps changes the state distribution and may not transfer to the full 300-turn, mixed-size gate.
- A cap supplies no target decomposition and no resource-distance breadcrumbs, so it does not reproduce the mechanism that taught delineate to mine and build advanced units.

Therefore an episode cap should not be the unexamined default meaning of “delineate's curriculum.”

## Recommended next diagnostic, before another long run

### A. Assigned-plan executor gate

Freeze the clone checkpoint. On real maps and both seats, externally supply a diverse target plan and use the existing target/deficit observation during troll mini-steps. Do not let the plan head choose the target.

Measure:

- fraction reaching affordability;
- turns to affordability and TRAIN;
- estimated resource-distance progress;
- illegal/stall rate;
- command mix and completion split by target talents, map size, and iron requirement.

Compare the unchanged clone with one early eroded PPO checkpoint. This tells us whether the executor itself is the object being destroyed.

### B. Offline gradient decomposition

On one saved post-warm-up minibatch, measure policy-parameter gradient norms and cosine similarities separately for:

- PPO clipped policy loss;
- entropy bonus;
- clone-anchor KL;
- plan rows versus troll rows;
- fruit-chain action rows versus all others.

This is read-only and identifies which objective term is moving the executor away from the clone.

## Recommended next training stage if the executor gate passes

### Plan-only PPO

Start again from the clone and:

- freeze the convolution trunk and spatial actor;
- keep troll commands exactly clone-equivalent;
- train the plan-selector MLP and value head on the champion-only environment and real end score;
- retain the existing full-game bench;
- stop if plan-only changes cannot improve while command execution is fixed.

This is the closest analogue of delineate Level 4 available in the present architecture.

If plan-only PPO improves, proceed to a tightly bounded Level-5-like fine-tune:

- unfreeze in stages;
- keep an explicit behaviour-cloning or fixed-reference loss on troll rows, not only a decaying KL;
- use lower learning rate for trunk/spatial parameters than for the plan/value heads;
- gate fruit-chain retention directly.

If the assigned-plan executor gate fails, then build the actual Level-1-to-3 analogue: assigned targets, automatic TRAIN, and distance-to-resource shaping. That is a larger environment amendment but is source-backed.

## Recommendation

```text
CORRECT the attribution: episode cap/small maps are a project idea, not delineate's stated curriculum.
DO the assigned-plan executor gate and offline gradient decomposition first.
PREFER plan-only PPO with the executor frozen before another all-parameter fine-tune.
KEEP episode-cap experiments optional and define truncation semantics explicitly.
```

No environment, trainer, checkpoint, dataset, YT operation, platform, or Arena state was changed by this audit.
