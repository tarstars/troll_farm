# D62a batch-option PPO mechanical preflight — frozen protocol (2026-07-21)

## Question

D61 proves that a renewable-safe state-conditioned linear population contains +57.586 crop-safe
whole-game oracle margin and that fixed modes all lose. Can a compact four-action actor receive
dense enough semi-Markov credit to learn state-dependent batch choices, avoiding D43's nearly
uniform sparse residual update, before any expensive policy run or field evaluation?

D62a is a local mechanics and learning-signal preflight. It does not select a checkpoint by game
outcome, open development/confirmation, construct a candidate, call TestSession, submit, or inspect
Arena.

## Frozen batch environment

Implement a batched Rust/ctypes environment with exactly the D61 option semantics:

- one decision at each `CompleteMacroEnv` Train-stage/free-worker-batch boundary;
- four actions in order `balanced`, `harvest`, `renew`, `fell`;
- exact D40 TRAIN, positive-deficit, evacuation, candidate order, provenance, and persistent job
  execution beneath the option;
- the selected option applies to every Rate worker assignment in that batch;
- when no live own-provenance crop exists, only `balanced` is legal;
- a Rate candidate that fells the last live own crop is masked by scanning to the next safe
  requested or D40-prior candidate; and
- gamma-one batch reward is the sum of exact margin deltas over all underlying macro decisions and
  referee turns advanced by that batch.

Every step must end terminal or at the next Train-stage boundary. Auto-reset streams official maps
through both seats and all eight D40 opponents in the same deterministic task order as
`MacroVecEnv`.

Before training, require constant balanced/harvest/renew/fell complete episodes to match the
corrected D61 matrix on a frozen 16-task seed prefix in terminal scores, workers, crops, action
hash, and state hash. Reward sums must telescope to terminal margin within `1e-4` points.

## Frozen observation and mask

Use D61's exact 56 finite deployable features and no others. The actor and critic receive the same
vector. The legal mask is `[1,0,0,0]` while no own crop is live and `[1,1,1,1]` otherwise. No
opponent identity, nickname, seed, future action, rollout result, random-population winner, or
terminal feature is exposed.

## Frozen actor/critic and initialization

Use model seed 6201 and CPU float32:

- actor: `Linear(56,16)`, ReLU, `Linear(16,4)`;
- critic: `Linear(56,64)`, ReLU, `Linear(64,32)`, ReLU, `Linear(32,1)`;
- orthogonal hidden initialization;
- actor output weights zero; and
- actor output biases `log([0.85,0.05,0.05,0.05])`.

Thus every unlocked state begins with the same 85% balanced / 5% per semantic alternative
distribution and deterministic argmax is balanced. Locked states are exactly balanced. The actor
has 980 parameters, compatible with a small Rust export.

## Frozen PPO preflight

- training map stream begins at 9,802,000;
- 64 vector environments x 64 batch decisions per rollout;
- exactly 131,072 transitions = 32 updates;
- four PPO epochs, minibatch 1,024;
- Adam `2.5e-4`, epsilon `1e-5`, no schedule;
- gamma 1.0, GAE lambda 0.95, clip 0.15;
- entropy coefficient 0.005, value coefficient 0.5;
- gradient norm 0.5 and target approximate KL 0.02; and
- exact margin-delta reward, with no shaping, assets, workforce bonus, crop bonus, teacher loss,
  random-population labels, curriculum, early stopping, or checkpoint selection.

Use 20 Torch/Rayon worker threads. Save only the final checkpoint.

## Frozen state-dependent movement probe

Before the first optimizer update, retain the first 512 distinct unlocked feature rows encountered
in stream order. Evaluate initial and final masked probabilities on those exact rows. Require:

- mean non-balanced probability changes by at least 0.02 in absolute value;
- final non-balanced probability standard deviation across states is at least 0.01;
- at least 16/512 final deterministic actions are non-balanced; and
- at least two distinct non-balanced modes appear among final deterministic actions.

These are learning-signal gates, not value gates. No probe state or intermediate checkpoint may be
selected.

## Frozen mechanical gates

All must hold:

1. exact transition/update budget and final-only checkpoint;
2. constant-policy D61 parity on all 16 frozen prefix tasks;
3. at least 20% of transitions are unlocked and at least 5% sample non-balanced actions;
4. zero illegal/masked actions, nonfinite observations, losses, parameters, or rewards;
5. at least 1,500 complete episodes;
6. maximum terminal reward-identity error below `1e-4`;
7. actor parameter L2 drift at least 0.05;
8. every completed episode creates a crop, worker-three reach at least 85%, and no mechanical
   failure counter is nonzero;
9. all four state-dependent movement gates pass; and
10. throughput at least 400 batch transitions/s with at least 12 effective CPU cores.

Episode mean margin is descriptive only and cannot pass or fail D62a.

## Decision rule

- **Full pass:** freeze the environment/checkpoint only as infrastructure and open a separate
  D62b prospective development protocol with disjoint maps, balanced control, fixed final
  checkpoint, full score/tail/family gates, and current-field transfer dependency.
- **Mechanics/parity failure:** quarantine training and repair only the exact environment or ABI
  defect before repeating unchanged.
- **Optimization moves but conditional probe fails:** close this feed-forward PPO recipe; do not
  extend training or tune initialization, entropy, width, or learning rate.
- **Conditional movement passes but safety/coverage fails:** reject before value evaluation and
  diagnose mask/reward interaction only.

No result authorizes candidate construction or platform action.
