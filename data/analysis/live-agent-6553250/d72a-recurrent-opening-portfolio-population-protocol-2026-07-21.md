# D72a recurrent opening-portfolio population protocol (2026-07-21)

## Question

Does a compact recurrent policy class over D71's lifecycle memory contain robust crop-safe
whole-game value, and do the explicit species actions add value beyond the same recurrent policies
restricted to D61's four ordinary modes?

D72a is a consumed random-function-class/upper-bound gate. It does not select a deployable policy,
train PPO, inspect field data, construct a candidate, or perform a platform action.

## Frozen tasks

Use official seeds 9,804,000--9,804,007, both seats, and all eight unchanged D40 opponent modes:
128 tasks. These maps are disjoint from D61--D71 and become consumed for representation selection.
Run the complete matrix twice with 20 threads and require byte identity.

## Frozen recurrent population

Generate 32 immutable policies `rnn_00`--`rnn_31` with NumPy PCG64 seed 7201 before any outcome.
Each policy has 12 tanh hidden units:

`h_t = tanh(W_x x_t + W_h h_(t-1) + b_h)`

`logits_t = W_o h_t + b_o`

where `x_t` is D71's exact 72-feature vector. Draw `W_x ~ Normal(0, 0.35)`, initialize `W_h`
as a QR-orthogonal matrix multiplied by 0.70, draw `b_h ~ Normal(0, 0.10)`,
`W_o ~ Normal(0, 0.50)`, and `b_o ~ Normal(0, 0.15)`. Freeze values to eight decimal places.
Hidden state starts at zero each game. Choose maximum legal logit with action-order tie-break.

Evaluate each frozen weight set in two matched families:

- `portfolio_rnn`: D71's full eight-action mask;
- `ordinary_rnn`: the same features, recurrence, and weights, but source actions 4--7 are masked.

Also run exact `balanced` and the unchanged D71 `cyclic` mechanics probe. The population therefore
contains 66 policies x 128 tasks = 8,448 rows. Controls and individual random policies cannot be
selected as candidates.

## Frozen telemetry and integrity

Record D71's terminal, lifecycle, mask, action, and source telemetry plus family, policy label,
hidden/logit finiteness, recurrent decision hash, and maximum hidden magnitude. Require:

1. complete byte-identical 2 x 8,448 matrices and exact matched task/policy identity;
2. exact balanced behavior across repeats and zero mechanical, mask, assignment, boundary,
   recurrent-finite, reward-identity, action-count, or source-count failure;
3. ordinary policies execute zero source actions and retain the D62 pre-crop lock;
4. at least 24/32 portfolio policies use at least four actions globally and issue a source action
   in at least 25% of tasks;
5. every one of eight actions occurs at least 256 times across portfolio policies;
6. at least 24/32 portfolio policies create a crop in every task; and
7. portfolio-policy mean margins span at least 30 points.

Environmental job invalidation is lifecycle state, not a mechanical failure, and is reported
separately.

## Frozen crop-safe population oracles

For each task and family, choose maximum terminal margin among policies that create at least one
crop, breaking ties by higher own score, lower opponent score, then policy label. Compare the
portfolio oracle to exact balanced. All must pass:

- mean margin gain at least +30;
- strict improvement in at least 70% of tasks;
- every opponent-family mean gain at least +10;
- mean own-score delta nonnegative and mean opponent-score delta nonpositive;
- selected worker-three reach at least 85%; and
- selected crop creation exactly 100%.

Then compare the portfolio oracle to the matched ordinary oracle. All must pass:

- mean margin gain at least +8;
- strict improvement in at least 40% of tasks;
- mean own-score delta nonnegative or mean opponent-score delta nonpositive;
- portfolio winners issue at least one explicit source action in at least 32 tasks;
- those winners span at least eight recurrent policies and at least three source species; and
- every opponent-family mean gain is nonnegative.

Oracle choices are consumed representation evidence only. They do not nominate weights, labels,
thresholds, or a checkpoint.

## Decision rule

- **Full pass:** freeze D71/D72 as the recurrent controller substrate and open one short recurrent
  optimization/signal preflight on a new stream. It must demonstrate deterministic action movement
  and universal feasible establishment before any value budget.
- **Portfolio vs balanced passes but explicit-action ablation fails:** retain recurrent ordinary
  options but close explicit deposited-seed actions for learning.
- **Function-class/headroom failure:** close this recurrent random class and move to paired online
  option values; do not tune dimensions, scales, population seed, gates, or consumed maps.
- **Integrity failure:** quarantine outcomes and repair only the defect before repeating unchanged.

No branch authorizes long PPO, confirmation access, TestSession, Arena, submission, or resident
replacement.
