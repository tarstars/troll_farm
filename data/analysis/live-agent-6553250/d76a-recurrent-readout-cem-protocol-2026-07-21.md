# D76a recurrent-readout whole-policy CEM — frozen protocol (2026-07-21)

## Question

D73's recurrent PPO moves policy but misprices own production, while D74--D75 reject short local
option labels. Can derivative-free, complete-episode optimization produce one robust fixed policy
inside a smaller recurrent controller, without an action critic or local hindsight teacher?

D76a is a whole-policy optimization preflight. It does not reuse D73 trained weights, inspect
D75's sealed oracle, tune a sequence horizon, construct a submission, open confirmation, call
TestSession, or touch Arena.

## Frozen controller

Use D71's exact 72 observable lifecycle features and the four ordinary renewable-safe modes
`balanced`, `harvest`, `renew`, and `fell`. Hidden state resets at game start and updates as:

`h_t = tanh(W_x x_t + W_h h_(t-1) + b_h)`

`logits_t = W_o h_t + b_o`.

There are 12 hidden units. Freeze the reservoir once from NumPy PCG64 seed 7601 using D72's
unchanged construction: `W_x ~ Normal(0, 0.35)`, QR-orthogonal `W_h * 0.70`, and
`b_h ~ Normal(0, 0.10)`, rounded to eight decimal places. Only the 52 readout parameters
`W_o` (4 x 12) and `b_o` (4) evolve. The initial readout is exactly zero and therefore reproduces
balanced through action-order tie breaking and the existing pre-crop legality lock.

The compact fixed reservoir makes the search dimension explicit and deployable. No source action,
critic, stochastic inference, opponent label, seed, terminal feature, rollout, handcrafted mode
threshold, or recurrent-weight update is available.

## Frozen CEM search

Use NumPy PCG64 seed 7602. Run ten generations. At every generation evaluate 33 recurrent
readouts: the current mean plus 16 antithetic Gaussian pairs. Initial standard deviation is 0.50
for output weights and 0.15 for output biases.

Generation `g` uses four fresh official maps starting at `9,814,000 + 4*g`, both seats, and all
eight unchanged D40 opponents: 64 paired tasks per policy. Exact balanced runs in the same matrix.
Thus search consumes 40 maps but never a platform replay or validation map.

For a mechanically valid, crop-safe policy define paired task deltas from balanced and frozen
fitness:

`mean_margin_delta + 0.5 * minimum_opponent_family_mean_delta`

`+ 0.25 * p10_margin_delta + 0.5 * min(0, mean_own_score_delta)`.

A policy is ineligible and receives negative infinity if it has any command/provenance/deposit,
feature/recurrent/mask, reward, crop-creation, or action-count failure, or worker-three reach below
85% on that generation. Rank by fitness, then minimum-family delta, overall mean delta, and label.

Take the best eight recurrent readouts. Update the mean halfway toward their arithmetic mean.
Update standard deviation as `0.70 * old + 0.30 * elite_population_std`, with floors 0.03 for
weights and 0.01 for biases and ceiling 1.50. Clip readout means to [-4, 4]. All evaluated
readouts and the final mean are rounded to eight decimals. Do not retain a best sample or select
an intermediate generation; the sole final policy is generation ten's updated distribution mean.

Record every population, raw matrix, timing, elite identity, objective component, mean/std hash,
action use, and mechanical/safety count. Training outcomes may update only the stated CEM mean and
standard deviation.

## Frozen prospective validation

After the final readout is written immutably, evaluate exact balanced, the zero-readout initial
policy, and the final mean on official seeds 9,815,000--9,815,015, both seats, and all eight
opponents: 256 tasks per policy and 768 rows. Run the complete evaluation twice with 20 threads and
require byte identity. No validation result may alter the readout, objective, or threshold.

## Frozen gates

### Search integrity and activity

All must pass:

1. exactly ten complete 34-policy matrices (balanced plus 33 recurrent), with 64 tasks per policy;
2. immutable population hashes match logged inputs and every row has exact task/family identity;
3. zero command, provenance, deposit, feature/recurrent/mask, reward, crop, or action-count
   failures in search and validation;
4. final evaluation repeats are byte-identical and zero-readout initial matches balanced in every
   terminal/action/state field;
5. final readout L2 drift from zero is at least 0.50; and
6. on validation, non-balanced modes occupy at least 20% of unlocked decisions and at least two
   distinct non-balanced modes execute.

### Prospective fixed-policy value

The single final mean passes only if all hold against exact balanced on the 256 untouched tasks:

1. mean margin delta at least +5;
2. strict improvement in at least 55% of tasks;
3. at least six of eight opponent-family mean deltas positive and every family at least -5;
4. mean own-score delta at least -10;
5. paired margin-delta p10 at least -60;
6. worker-three reach at least 90%; and
7. crop creation exactly 100%.

Report opponent/seat/tail effects, own versus suppression decomposition, action frequencies,
recurrent magnitude, parameter/std trajectories, and search-to-validation change. The final mean
is one predeclared policy, not a selected population member.

## Decision rule

- **All gates pass:** preserve the final readout as a local candidate input and open D77 layered
  fresh-field qualification. It is not yet submission-authorized.
- **Search mechanics failure:** quarantine value and repair only the defect before repeating
  unchanged.
- **Activity failure:** close this fixed-reservoir readout representation without widening or
  changing seeds.
- **Prospective value failure:** close this CEM recipe and final policy. Do not extend generations,
  tune fitness/update scales, select an elite/intermediate member, or reuse validation maps. The
  next whole-policy branch may evolve recurrent representation or use a qualitatively different
  controller, but cannot retry this readout search.

No branch authorizes candidate export to Arena, confirmation access, submission, or resident
replacement.
