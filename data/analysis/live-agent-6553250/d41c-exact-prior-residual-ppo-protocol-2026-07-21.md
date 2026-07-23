# D41c exact-prior residual PPO — frozen protocol (2026-07-21)

## Question and authorization

D41b preserves D40 exactly while exposing a 737-parameter residual action scorer. D41c asks whether
one conservative, outcome-optimized PPO run can improve full-game margin without eroding the
teacher's complete workforce and renewable economy.

This protocol authorizes rank-aware batch infrastructure, fresh D40/random development baselines,
one fixed local PPO run, final development evaluation, a conditional exact repeat, analysis, and
written artifacts. It does **not** authorize confirmation maps, inference-weight integration,
candidate construction, TestSession, submission, or Arena.

## Frozen environment and splits

Retain the exact corrected complete-macro environment, nine action planes, 44 candidate features,
D40 teacher, two seats, and eight opponents. Episode reward is the existing telescoping change in
score margin divided by 100; gamma is 1.0. No asset bonus, opponent identity input, curriculum
termination, or shaped workforce/crop reward is allowed.

- PPO training stream begins at map seed **9,730,000**.
- Development baselines and final evaluation use maps **9,740,000--9,740,031**: 512 tasks.
- Generate D40 and random-legal baselines on that development block before training.
- D41a confirmation maps 9,720,000--9,720,031 remain sealed.
- D37--D41b selection, validation, and development maps remain forbidden for outcome evaluation.

## Rank-aware infrastructure gate

Expose the Rust exact-prior rank of every legal candidate through the existing batch ABI. Padding
ranks must be an invalid sentinel; rank zero must equal both the independent D41b kernel and D40's
teacher index. Parallelizing independent environment slots is allowed, but task enumeration,
terminal ordering, actions, rewards, features, ranks, and hashes must remain exactly identical to
the pre-parallel implementation on an A/A corpus.

Before training require:

1. Rust/Python shape, uniqueness, finite-value, legal-label, rank-permutation, and padding checks;
2. exact rank-zero/D40 agreement across at least one complete direct episode and two identical
   4,096-decision streams;
3. exact terminal/action/state parity with the existing D41b development artifact on a smoke block;
4. finite rewards whose undiscounted episode sum equals terminal margin/100 within `1e-4`; and
5. measured throughput/CPU use with 16 and 64 environments. Choose 64 only if it preserves all
   hashes and improves effective decisions/second; otherwise retain 16 without changing training
   transitions or seeds.

## Frozen actor/critic

For candidate rank `r`, actor logit is

`-4.0 * r + residual(candidate)`.

The residual is the D41b `44 -> 16 -> 1` ReLU scorer. Initialize the first layer orthogonally under
model seed **411** and initialize the final weight and bias to exactly zero. Thus deterministic
argmax is D40 before the first update; the rank-softmax assigns approximately 98.17% probability to
rank zero before finite-set normalization while concentrating exploration on rank one. Only these
737 actor parameters are deployable.

The training-only critic consumes the 17 global features from candidate zero plus masked mean and
masked maximum of all 44 candidate features, then uses `105 -> 64 -> 32 -> 1` with ReLU. It has
8,897 parameters and is never exported.

## Frozen PPO run

- exactly **1,048,576 transitions**;
- selected vector width from the infrastructure gate, rollout length chosen so each update contains
  exactly 4,096 transitions, hence 256 updates;
- four optimization epochs, minibatch 1,024;
- Adam learning rate `2.5e-4`, linearly decayed to zero, epsilon `1e-5`;
- gamma 1.0, GAE lambda 0.95, PPO clip 0.10, value coefficient 0.5;
- entropy coefficient 0.001, D40 teacher cross-entropy coefficient 0.02;
- advantage normalization, gradient norm 0.5, target approximate KL 0.01; and
- 20 Torch threads on local CPU, with no intermediate development evaluation or checkpoint choice.

Train the single final model from seed 411. Record sampled rank frequencies, D40 disagreement rate,
branch frequencies, completed episode margin/workforce/crops, reward identity, losses, entropy, KL,
clip fraction, explained variance, parameter drift, wall/CPU time, and integrity counters. Abort on
NaN, illegal action, rank drift, reward-identity failure, decision loop, or worker-cap violation.

YT/GPU is not authorized for this pilot: the simulator/rank generator is CPU-bound and this exact
parallel ABI has no remote parity result.

## Final development gate

Evaluate deterministic masked argmax only for the final checkpoint on all 512 development tasks.
Compare paired terminal rows with the pre-training D40 and random baselines. The checkpoint passes
only if all hold:

1. mean margin is at least **+5** above D40 and at least **+150** above random;
2. at least five of eight opponent-family mean margins improve over D40, and no family regresses by
   more than 15 points;
3. mean own score is no more than 5 below D40;
4. worker-two rate is at least 95%, worker-three at least 88%, and crop creation at least 97%;
5. invalid direct commands, provenance failures, relevant prediction failures, illegal argmaxes,
   decision loops, and worker-cap errors are zero;
6. deterministic action disagreement with D40 is greater than zero but no more than 15% of visited
   decisions; and
7. a conditional independent repeat has identical action/state hashes and terminal rows.

There is one seed and one final checkpoint: no two-of-three selection, threshold revision, or
post-result hyperparameter rerun. A pass opens generated Rust residual weights plus the still-sealed
confirmation block. A failure closes this PPO recipe; use exact one-deviation continuation analysis
to distinguish harmful proposals from compounding before proposing another learner.
