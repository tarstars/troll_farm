# Curriculum Level 2 randomized-worker protocol — frozen 2026-07-19

## Question and boundary

Can the accepted Level-1 spatial actor infer and execute the resource-acquisition plan for a
requested second-worker recipe that changes between episodes?

The learner still controls only the original troll.  The environment automatically submits the
requested TRAIN command every turn; the opponent waits.  Recipe selection, multiple controlled
trolls, renewable production, opponent interaction, and terminal score differential remain later
curriculum levels.  A pass therefore advances the architecture but cannot change the resident or
authorize an Arena submission.

## Frozen recipe catalog

The catalog covers all four capability/currency axes and the common immediate contest roles while
keeping every per-resource workforce-one cost at ten or below.  Premium `cc4`/`chop3` workers are
excluded because reliably funding them with one starter is a different, multi-worker economy
problem.

| ID | Family | `(move, carry, harvest, chop)` | Role represented |
|---:|---|---|---|
| 0 | cheap-planter | `(1,1,1,1)` | minimum generalist / planter |
| 1 | compact-farmer | `(1,2,1,1)` | low-cost producer |
| 2 | balanced-producer | `(2,2,1,1)` | mobile generalist |
| 3 | harvest-producer | `(2,2,2,1)` | fruit specialist |
| 4 | level1-anchor | `(1,3,0,1)` | accepted fixed Level-1 recipe |
| 5 | lean-chopper | `(1,2,0,2)` | cheap wood specialist |
| 6 | standard-chopper | `(2,2,0,2)` | common field chopper |
| 7 | hybrid-chopper | `(2,3,1,2)` | higher-cost mixed worker |

The recipe ID is
`splitmix64(seed XOR 0x4c32726563697065) mod 8`, using the standard SplitMix64 finalizer.  The map
continues to use the unmodified episode seed.  Requested stats, per-resource costs, and current
deficits remain visible in observation channels 86--97.  Observation/action shapes and the
34,926-parameter actor-critic are unchanged.

`initial_total_deficit` is the sum of positive initial bank deficits in PLUM, LEMON, APPLE, and
IRON.  It replaces Level 1's lemon-only deficit for Level-2 stratification.  Maximum episode length
is 240 turns.

## Environment and teacher preflight

Before generating learning labels:

1. Rust and Python must agree on shape, recipe ID/spec, exact seed interval, and terminal metadata.
2. Identical batches must remain byte-deterministic.
3. The teacher action must be legal on at least 1,000 sampled states.
4. On exactly seeds 2,003,000--2,004,999, the deterministic teacher must solve at least 97% overall,
   at least 94% in every recipe family, and at least 95% of nonzero-total-deficit episodes.
5. Generate and hash a random-legal control for the same interval with RNG seed 61.

Preflight failure is an environment/teacher failure and stops before cloning.  The catalog and
thresholds may not be changed after seeing this bank.

## Behavior-clone discovery

- model seed 61;
- teacher stream begins at 5,000,000;
- 400,000 online labels, 100 environments, ten steps per 1,000-row chunk;
- two shuffled epochs per chunk, minibatch 1,000;
- Adam `1e-3`, cosine decay to `1e-4`, gradient norm 1.0;
- 14 Torch threads;
- deterministic evaluation on the consumed preflight interval.

The clone must achieve at least 80% overall, 75% on nonzero-total-deficit episodes, 70% in every
recipe family, 65% in every height bucket, and paired teacher median delay no greater than 20
turns.  Failure closes this clone schedule; do not start PPO.

## PPO discovery

Conditional on clone success:

- initialize from the exact clone checkpoint;
- PPO stream begins at 5,100,000;
- 100 environments x 100 rollout steps;
- Stage A at 500,000 transitions and final at 2,000,000;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale 0.01,
  gradient norm 0.5, target KL 0.03;
- constant online teacher auxiliary coefficient 0.10;
- exact learned-evaluation interval 2,005,000--2,006,999;
- teacher and random-legal controls for that interval are generated and hashed before the first
  learned evaluation; random RNG seed 61.

Stage A requires 70% overall, 65% nonzero-total-deficit, 60% recipe floor, 55% height floor, and
teacher median delay no greater than 30 turns.  Failure stops.

The final discovery gate requires 90% overall, 85% nonzero-total-deficit, 80% recipe floor, 80%
height floor, at least 40 percentage points over random legal, and teacher median delay no greater
than 20 turns.  The exact action audit must also emit at most 40,000 `MOVE current` waits across
2,000 episodes and choose the applicable productive action on at least 60% of legal, currently
needed HARVEST/MINE opportunities.

## Confirmation and promotion rule

A discovery pass freezes the implementation and authorizes exactly one independent confirmation:
model seed 67, new cloning/PPO streams, and a new exact 2,000-seed bank fixed before execution.
Confirmation thresholds are 85% overall, 80% nonzero-total-deficit, 70% recipe floor, 70% height
floor, and the same action-collapse limits.  Level 2 is accepted only if discovery and
confirmation pass.

Any failure receives a written action/recipe/difficulty diagnosis before one next hypothesis is
chosen.  No bank may be reused as prospective evidence, and no Level-2 checkpoint is a live bot.
