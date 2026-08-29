# Way B BC-to-PPO boundary: target memory must enter with zero effect, not random weights

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: read-only architecture/initialization audit; no build, formal review verdict, dataset, training run, or platform action
- Main snapshot: `origin/main@bcf6ae8820ee2ea5c5a447c6808ffce57137e613`
- Relevant implementation: `cgauto/train_level1_ppo.py::PlanCandidateScorer`

## Finding

The latest ruling correctly removes target memory from behavior cloning and retains it only as model-owned state during PPO. The current network initialization does not make that transition safe.

`PlanCandidateScorer` concatenates a final scalar `matches` feature to each candidate and feeds it into the first linear layer:

```python
self.feature_size = width + 14
self.mlp = nn.Sequential(
    layer_init(nn.Linear(self.feature_size, hidden)),
    nn.ReLU(inplace=True),
    layer_init(nn.Linear(hidden, 1), std=0.01),
)
```

`layer_init` orthogonally initializes every input column, including the final match-feature column, with nonzero random weights.

Under the accepted BC rule, every plan row has `standing_plan = 0` and planes 59-71 zero. Therefore `matches == 0` for every BC sample. For a linear layer, the gradient of a weight column is proportional to its input. The match column receives exactly zero gradient throughout cloning and stays at its random initialization.

At PPO time, the environment begins exposing the policy's previous target. On the first later plan phase, one candidate receives `matches = 1`. The frozen clone anchor and the policy both now use a random, never-trained input column. Their logits can change from the clone's measured behavior before PPO has taken one optimization step.

The KL anchor does not protect against this. Policy and anchor are initialized from the same checkpoint and both see the same random match-column effect, so their KL is zero while both have departed from the behavior that passed the clone bench.

## Consequence

The first PPO policy is not actually the accepted clone under a new state feature. It is the clone plus an arbitrary target-stickiness perturbation whose sign and magnitude depend on initialization and the already-trained downstream ReLU/linear weights.

This can create either random inertia or random anti-inertia and contaminate any conclusion about whether PPO improved the clone.

## Minimal correction

Make the new feature an explicit zero-effect migration:

```text
- initialize the first linear layer's `matches` input column to exactly zero;
- preserve that zero column in the clone checkpoint;
- allow PPO gradients to train it once model-owned target memory appears.
```

A more explicit implementation is a separate scalar gate:

```python
score += target_match_scale * match_embedding
```

with `target_match_scale = 0` at the BC checkpoint and trainable in PPO. Either design makes the PPO starting policy equal to the benched clone.

Do not solve this by injecting target memory into BC labels again; that would restore the leakage the latest ruling removed.

## Required controls

1. Train or construct a BC checkpoint with every target plane zero.
2. Before PPO, evaluate identical boards twice: no standing target, and each possible standing target in turn. Plan logits must be byte/float identical at the handoff checkpoint.
3. Confirm the match-feature parameter receives zero BC gradient and remains exactly zero, not merely its random initializer.
4. Start one PPO minibatch containing nonzero standing targets; confirm the feature can then receive a nonzero gradient.
5. Policy and anchor loaded from the clone must reproduce the clone's free-running first-game commands before any PPO update. The anchor may keep the zero feature while the policy learns it under the decaying KL term.
6. Checkpoint metadata should identify whether target-memory parameters are `inactive-zero` or `ppo-trained`.

## Recommendation

Keep PPO-only target memory, but make its initial behavioral contribution exactly zero. The clone bench then remains a real baseline and any later target persistence is attributable to PPO rather than an untrained random column.
