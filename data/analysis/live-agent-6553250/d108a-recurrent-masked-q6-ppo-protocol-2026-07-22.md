# D108a recurrent masked q6 PPO — frozen protocol

Date: 2026-07-22  
Status: frozen before training or evaluation on D108 maps

## Question

D107a proves that q6 supplies deterministic, broad, repeated whole-game headroom, while D106a
shows that an offline static regressor cannot abstain safely. Can a small recurrent shared scorer,
trained directly on paired whole-episode return, learn a fixed policy that improves exact D40 on
untouched maps without sacrificing crops, workers, or opponent-family robustness?

D108a is a bounded optimization-signal and held-value preflight. It is not candidate construction.
No D107 population-oracle winner, D106 terminal arm, held D108 outcome, platform replay, or Arena
result may enter training or selection.

## Immutable inputs

- q6 expert bank:
  `87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8`;
- Rust q6 environment:
  `739fa02c00d92ba271f7a7a15fca893f18fffa258c02ba39c4a4cb08eaba2af1`;
- Python vector wrapper:
  `8f102e1eca5a1bcc49ea932170b100eacea5848d7af097c0b21689229dc68911`;
- parity validator and result:
  `95566b45a1f0ddf1218bc776f162397762b2d66417ef5b8fad3b9030f64c3848` and
  `92c6cda4049885ec54fc27f155c5be148cade5fb69c145bdd7f1a38670299818`;
- release library used by parity:
  `90284b35574e78740bdd1b1f81ea6ba5fdf03265a5ef029f1667a676748835cf`.

The consumed D107 parity panel is environment validation only. Across two runs, action zero exactly
reproduces all 128 D40 terminals, action/state hashes, 647 eligible boundaries, proposal sums,
per-task minima and maxima, and zero paired reward. The 379-feature stream repeats with SHA-256
`9b8597c825841e2a099b2afc74cd49132012c1557298a49f684246cdd40bd740`.

## Frozen environment contract

At each D107-eligible two-worker boundary expose 65 actions. Action zero is exact D40. Each
noncontrol action index is one plus the smallest q6 expert index endorsing a unique paired proposal;
all duplicate representatives are masked. Action features are D106's exact 379-value
arm-minus-control vector. The 64 state values comprise D107's 56 batch fields plus live turn,
boundary ordinal, live own crops, remaining authority, and previous proposal-kind one-hot fields.

After the chosen pair, auto-advance exact D40 to the next eligible boundary. A noncontrol batch
consumes one of four authority units; abstention does not. Reward is zero before terminal and at
terminal equals `(policy margin - same-task D40 margin) / 100`. Precompute exact D40 baselines for
the finite map pool and reuse them deterministically. Task indices continue monotonically while
training scenarios cycle through the pool. Reset recurrent state only at terminal.

## Frozen model

Use PyTorch CPU and seed `10801`. The actor has:

1. a 64-to-12 state projection plus a bias-free 12-to-12 recurrent transform scaled to spectral
   initialization 0.70, followed by `tanh`;
2. a bias-free 379-to-8 shared proposal projection and 12-to-8 recurrent query, both followed by
   `tanh`;
3. their scaled dot product plus a zero-initialized direct 379-to-1 term for noncontrol logits; and
4. a separate zero-initialized 12-to-1 control logit.

Mask illegal actions before a categorical distribution. The critic is an independent
64-to-64-to-32-to-1 `tanh` MLP. Store only this final model; no intermediate checkpoint, lineage,
elite selection, restart, seed sweep, or hyperparameter branch is allowed.

## Frozen training

- training maps: untouched `9,833,000--9,833,063`, both seats and all eight opponents;
- map pool: 64 maps / 1,024 scenarios, cycled outcome-blindly;
- 20 vector environments and 20 Rayon/PyTorch threads;
- 20 recurrent steps per rollout, 400 transitions per update;
- 16,000 total transitions / exactly 40 updates;
- three PPO epochs, five environment sequences per minibatch;
- Adam learning rate `3e-4`, epsilon `1e-5`;
- `gamma=1`, GAE lambda `0.95`, clip `0.20`, entropy `0.02`, value coefficient `0.5`;
- gradient norm `0.5`, target KL `0.03`; and
- a frozen 256-row live-state/action/mask/recurrent probe captured before the first update.

No early stopping by score. Target KL may shorten epochs exactly as implemented. Training may print
mechanics and loss logs but cannot change the run.

## Frozen held evaluation

Use untouched seeds `9,834,000--9,834,015`, both seats and all eight opponents: 256 tasks. Evaluate
exact control, the initialized actor, and the final actor deterministically twice from new vector
environments. Require the two complete TSVs to be byte-identical before interpreting value.

## Gates

### Mechanics

Require exactly 16,000 transitions and 40 updates; finite losses and parameters; zero masked
actions; at least 2,500 complete training episodes; paired reward identity below `1e-4`; zero
training mechanical failures; at least 32 distinct representative actions explored; 20%--95%
training noncontrol actions; complete repeated held matrices; held reward identity below `1e-4`;
zero held mechanical failures; and at least 20 transitions/s including baseline initialization.

### Optimization signal

Require at least 40/256 probe choices to change, at least eight distinct final probe actions, actor
L2 drift at least `0.10`, at least eight aggregate final held representatives, 20%--95% held task
intervention, and repeated intervention on at least 10% of held tasks.

### Safety

Require 100% final held crop creation and worker-three reach no more than five percentage points
below exact held D40.

### Fixed-policy value

Require final mean held gain at least `+1` over exact D40, strict improvement on at least 25% of
tasks, worst opponent-family mean at least `-5`, at least five positive families, nonnegative own
score or nonpositive opponent score, and at least `+1` mean paired improvement over the initialized
actor.

## Decision

- **Mechanics failure:** repair only and repeat the unchanged run under a measurement amendment.
- **Signal failure:** close this optimizer/model combination and diagnose gradients/action entropy;
  do not inspect alternate held-selected checkpoints.
- **Safety or value failure:** close D108a as a submission path; use the frozen failure class to
  define one new-map experiment, without threshold or seed tuning.
- **Full pass:** open D108b, a longer single-seed run followed by an entirely new held confirmation
  panel and deployable-size audit. D108a held maps become consumed diagnostics.

No branch authorizes TestSession, Arena, candidate construction, submission, or resident change.
