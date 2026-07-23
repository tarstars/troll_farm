# D77a full recurrent lineage whole-policy search — frozen protocol (2026-07-21)

## Question

D76's direct whole-episode objective repeatedly finds profitable active policies, but CEM averaging
maps incompatible readouts back to balanced. Can an actual-policy lineage optimizer retain that
signal, while evolving both recurrent representation and readout, and produce one fixed policy
that transfers prospectively?

D77a is a new representation and optimizer on fresh maps. It cannot select any D76 elite, reuse
D76 weights, retry fixed-reservoir CEM, inspect D75's sealed oracle, construct a submission, open
confirmation, call TestSession, or touch Arena.

## Frozen complete recurrent controller

Use D71's exact 72 features, the four ordinary renewable-safe modes, 12 tanh hidden units, and
deterministic legal argmax:

`h_t = tanh(W_x x_t + W_h h_(t-1) + b_h)`

`logits_t = W_o h_t + b_o`.

All 1,072 parameters evolve: 864 input weights, 144 recurrent weights, 12 hidden biases, 48 output
weights, and 4 output biases. Hidden state resets each game. Source actions, a critic, stochastic
inference, opponent labels, map seeds, terminal features, local rollouts, and handcrafted mode
thresholds are unavailable.

## Frozen lineage search

Use NumPy PCG64 seed 7701. Population size is 32, with `mu=8` survivors and `lambda=24` children.

Generation one contains 32 independent networks. For each, construct `W_x`, `W_h`, and `b_h` by
D72's frozen Normal/QR recipe (`0.35`, orthogonal `*0.70`, `0.10`) and draw `W_o ~ Normal(0,0.50)`
and `b_o ~ Normal(0,0.15)`, rounded to eight decimals. Founder zero retains its independently
drawn reservoir but replaces its readout by exact zero, providing a recurrent balanced anchor.

After each generation retain the best eight actual vectors unchanged. Each survivor creates three
children with independent additive Gaussian mutation:

- input and recurrent weights: sigma 0.02;
- hidden biases: sigma 0.02;
- output weights: sigma 0.10;
- output biases: sigma 0.05.

Round children to eight decimals. Clip input/output weights to [-3,3], recurrent weights to
[-1.5,1.5], and all biases to [-2,2]. There is no crossover, averaging, adaptive sigma, restart,
novelty bonus, opponent specialization, or post-result mutation change. Preserve lineage IDs and
parent IDs.

Run ten generations. Generation `g` uses four fresh official maps beginning at
`9,816,000 + 4*g`, with `g=0..9`, both seats, and all eight D40 opponents: 64 paired tasks per
policy. Exact balanced runs in every matrix.

## Frozen fitness and safety

For each policy calculate paired task deltas from within-matrix balanced and use D76's unchanged
robust fitness:

`mean_margin_delta + 0.5 * minimum_opponent_family_mean_delta`

`+ 0.25 * p10_margin_delta + 0.5 * min(0, mean_own_score_delta)`.

A policy is ineligible for that generation if any mechanics/crop invariant fails or if its
worker-three reach is more than five percentage points below paired balanced. This replaces D76's
invalid absolute development cutoff: on a hard map batch, safety is degradation relative to the
same task control, not an assumption that balanced itself always exceeds 85%.

Rank eligible policies by fitness, then minimum family delta, mean delta, p10 delta, and lineage
label. Ineligible policies rank after every eligible policy by the same descriptive tuple. Retain
exactly the first eight actual policies. Record every population, matrix, timing, objective,
ranking, mutation/parent identity, parameter hash, and mechanics result.

## Frozen champion selection and validation

After generation ten, reevaluate its eight retained parents plus balanced on a separate selection
panel: seeds 9,816,040--9,816,047, both seats, all opponents (128 tasks each). Select the highest
policy by the same eligibility and ordering. This one champion is the algorithm's training output;
no earlier member can be selected.

Write the champion immutably, then evaluate balanced, founder zero, and champion on untouched
seeds 9,817,000--9,817,015, both seats, all opponents: 256 tasks per policy. Repeat the full
768-row matrix with 20 threads and require byte identity. Validation cannot alter the champion.

## Frozen gates

### Search integrity and activity

All must pass:

1. ten complete 33-policy generation matrices and one complete nine-policy selection matrix;
2. seed-derived founders, every parent copy, every mutation, population hash, lineage edge,
   objective, ranking, and survivor set reconstruct exactly;
3. zero command, provenance, deposit, feature/recurrent/mask, reward, crop, or action-count failure;
4. founder zero matches balanced exactly and validation repeats byte-for-byte;
5. selected champion is eligible and has selection-panel robust fitness at least +2; and
6. on validation, champion non-balanced modes occupy at least 20% of unlocked decisions and at
   least two distinct non-balanced modes execute.

### Prospective fixed-policy value

The one frozen champion passes only if all hold against balanced over 256 validation tasks:

1. mean margin delta at least +5;
2. strict improvement in at least 55% of tasks;
3. at least six of eight opponent-family mean deltas positive and every family at least -5;
4. mean own-score delta at least -10;
5. paired margin-delta p10 at least -60;
6. worker-three reach at least 85% and no more than five points below balanced; and
7. crop creation exactly 100%.

Report lineage depth/diversity, mutation survival, generation and selection objectives, action
frequencies, hidden magnitude, opponent/seat/tail effects, and own-versus-suppression decomposition.

## Decision rule

- **All gates pass:** preserve the champion as a local candidate input and open layered fresh-field
  qualification. It is not yet submission-authorized.
- **Mechanics/reconstruction failure:** quarantine value and repair only the defect before an
  unchanged repeat.
- **Activity failure:** close this full recurrent lineage representation and optimizer without
  selecting another member, increasing mutation, or extending generations.
- **Prospective value failure:** close the champion and exact recipe. Do not choose another parent,
  retune fitness/safety/mutation, or reuse selection/validation maps.

No branch authorizes source export to Arena, confirmation access, submission, or resident
replacement.
