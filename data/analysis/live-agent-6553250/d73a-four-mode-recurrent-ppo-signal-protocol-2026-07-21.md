# D73a four-mode recurrent PPO signal preflight — frozen protocol (2026-07-21)

## Question

D72 proves that recurrent state at natural job-batch boundaries contains large crop-safe
whole-game choice headroom, while explicit deposited-seed actions miss their matched breadth gate.
Can one compact recurrent policy over the retained four ordinary modes learn a deterministic,
crop-safe fixed policy that improves prospectively over exact balanced control?

D73a is a short local optimization/signal preflight. It does not select an intermediate
checkpoint, consume D72 oracle labels, train explicit source actions, construct a submission,
open confirmation, call TestSession, or touch the platform.

## Frozen environment and parity

Expose D71's exact 72-feature observation through a batched Rust/ctypes environment, but expose
only the ordinary actions in order `balanced`, `harvest`, `renew`, `fell`. Preserve D62's exact
renewable-safe mask and option semantics. D71 lifecycle features continue to record own
generations, receipts, deaths, reinvestment, and live sources; explicit-attempt fields remain zero.

Before training, on seed 9,810,999, both seats, and all eight D40 opponents, run each constant mode
through both the existing 56-feature D62 ABI and the new 72-feature ABI. Require exact terminal
equality in scores, workers, trains, crops, action hash, state hash, and all failure counters;
require reward telescoping below `1e-4` and repeat equality. This mechanics-only map is not used for
training or value.

## Frozen recurrent actor and critic

The actor exactly follows D72's ordinary recurrent form with 12 hidden units:

`h_t = tanh(W_x x_t + W_h h_(t-1) + b_h)`

`logits_t = W_o h_t + b_o`

Use NumPy PCG64 seed 7301. Initialize `W_x ~ Normal(0,0.35)`, initialize `W_h` by QR and multiply
by 0.70, draw `b_h ~ Normal(0,0.10)`, `W_o ~ Normal(0,0.50)`, and
`b_o ~ Normal(0,0.15)`, then round every actor value to eight decimal places before float32
assignment. Hidden state starts at zero and resets after terminal.

Use a separate feed-forward critic `Linear(72,64)` / tanh / `Linear(64,32)` / tanh /
`Linear(32,1)`, orthogonally initialized with Torch seed 7301. The actor has exactly 1,072
parameters. The actor and critic see no opponent identity, nickname, map seed, future result,
D72 winner, or terminal-only feature.

## Frozen recurrent PPO run

- training stream starts at official seed 9,810,000;
- 64 vector environments x 64 decisions per rollout;
- exactly 131,072 transitions = 32 updates;
- four sequence PPO epochs; minibatches contain 16 complete 64-step environment sequences;
- recompute recurrent states through each complete sequence, resetting after terminal;
- Adam `2.5e-4`, epsilon `1e-5`, no schedule;
- gamma 1.0, GAE lambda 0.95, clip 0.15;
- entropy coefficient 0.01, value coefficient 0.5;
- gradient norm 0.5 and target approximate KL 0.02;
- exact margin-delta reward, without shaping, teacher/oracle labels, curriculum, auxiliary loss,
  source-action loss, or checkpoint selection; and
- 20 Torch/Rayon threads, saving only the final checkpoint.

Retain the first 512 distinct unlocked `(feature, incoming-hidden, mask)` tuples from the first
rollout before optimization. On this immutable probe, require final deterministic action to differ
from initial in at least 64 rows and require at least three final deterministic modes. Require
actor L2 drift at least 0.10. These are optimization-signal gates, not value selection.

## Frozen prospective evaluation

After training, evaluate exact balanced, the reconstructed untrained actor, and the single final
actor deterministically on official seeds 9,811,000--9,811,015, both seats, and all eight unchanged
D40 opponent modes: 256 paired tasks per policy. Run the complete evaluation twice and require
byte-identical rows. No evaluation outcome may alter training, weights, or gates.

Require all mechanics and safety conditions:

1. exact transition/update budget, final-only checkpoint, finite tensors, zero illegal actions,
   at least 1,500 completed training episodes, reward identity below `1e-4`, and zero direct,
   provenance, or deposit-prediction failures;
2. all four actions sampled in training at least 2% of unlocked decisions;
3. final deterministic evaluation uses at least three modes and non-balanced modes in at least 25%
   of unlocked decisions;
4. final evaluation creates a crop in exactly 256/256 tasks and reaches worker three in at least
   90%;
5. evaluation repeats are byte-identical; and
6. throughput at least 400 transitions/s with at least 12 effective CPU cores.

Then require the single final policy to pass every prospective value gate:

- mean margin at least +5 above balanced and at least +5 above the untrained actor;
- strict paired margin improvement over balanced in at least 45% of tasks;
- every opponent-family mean delta versus balanced at least -5 and at least six of eight positive;
- mean own-score delta nonnegative or mean opponent-score delta nonpositive; and
- no post-result checkpoint, threshold, seed, action, or opponent selection.

## Decision rule

- **Full pass:** retain the final checkpoint only as a development seed and open one longer
  recurrent PPO development run plus a separately frozen held-map qualification. It is not yet a
  submission candidate.
- **Mechanics/recurrent-integrity failure:** quarantine value and repair only that defect before
  repeating unchanged.
- **Optimization/signal failure:** close this recurrent PPO recipe without extending budget or
  tuning initialization, width, entropy, rate, truncation, or seed.
- **Signal passes but fixed-policy value/safety fails:** keep D71/D72 as representation evidence,
  close this PPO recipe, and move to paired online option values rather than another PPO retry.

No branch authorizes confirmation access, candidate construction, Arena, submission, or resident
replacement.
