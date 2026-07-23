# Curriculum Level 5 active-opponent development protocol — frozen 2026-07-19

## Question

Can the accepted randomized-recipe, two-role renewable controller remain feasible and learnable
when the other player executes one fixed deterministic closed-loop economy instead of waiting?

Level 4 established requested worker funding, farmer/chopper coordination, crop renewal, and score
flow in isolation.  Level 5 changes exactly one environmental axis: player 1 receives commands
from the deterministic FastState baseline embedded in `rhea_bot`.  That baseline gathers, banks,
plants, chops, and may train through its existing fixed constants.  Player 0's recipe catalog,
automatic requested TRAIN, two controlled roles, objective, reward, episode horizon, observation
and action ABI, network, and teacher remain unchanged.

This is a curriculum/mechanism test, not a local opponent-zoo promotion oracle and not a live
candidate qualification.

## Opponent-abstraction selection

| Abstraction | Isolation | Transfer value | Decision |
|---|---|---|---|
| Waiting opponent | exact control | none beyond Level 4 | accepted control only |
| One no-growth natural forager | very high | tests collisions/depletion but can be strategically trivial | reserve only if the selected abstraction is infeasible on fresh development data |
| Scripted crop thief/denier | narrow | repeats a family already rejected by field and Arena evidence | reject |
| One deterministic complete FastState baseline | one opponent-policy toggle | tests movement, shared supply, banking, growth, and observed opponent state without stochasticity | **select** |
| Opponent mixture, self-play, or field replay | low | higher eventual transfer value but confounds the first interaction step | defer |

The selected opponent is the existing fixed Rhea/SchedBot baseline, not the RHEA search itself.
No constants may be tuned from Level-5 outcomes.  A reusable command wrapper may expose the exact
existing action and greedy training cascade to the curriculum environment.

## Phase D0: implementation and consumed readiness bank

Development seeds 0--499 are consumed for tooling and readiness.  They may expose implementation
defects, but may not tune opponent constants, teacher targets, reward, success milestones, model,
or thresholds.  The phase requires:

1. unchanged Level-4 tests and byte-deterministic waiting-opponent behavior;
2. Level-5 repeatability under identical seeds/actions for observations, masks, rewards, terminal
   records, opponent score, and opponent workforce;
3. the active baseline issues only referee-legal FastState commands and changes opponent state;
4. on 500 teacher episodes, at least 90% overall success, 85% nontrivial success, 75% in every
   recipe, 80% in every height, 90% tracked-crop creation, and 85% renewable harvest;
5. at least 50% of episodes end with positive opponent score or more than one opponent worker,
   establishing that this is not behaviorally equivalent to `WAIT`; and
6. a random-legal control and accepted-Level-4 zero-shot replay are recorded as diagnostics.  They
   do not change D0 teacher feasibility.

Failure of command legality, determinism, waiting regression, or teacher feasibility rejects this
complete-baseline abstraction before any prospective bank.  It may not be weakened or retuned on
seeds 0--499.  A narrower opponent would require a new written question and fresh development
seeds.

## Conditional prospective preflight

Only a complete D0 pass opens exact seeds 2,019,000--2,020,999.  Before evaluating a learned actor:

- generate and hash deterministic teacher and random-legal controls on all 2,000 seeds;
- require the same teacher floors as D0 and at least 50% material opponent activation;
- record per-recipe, per-height, deficit, crop, harvest, completion, opponent-score, and
  opponent-workforce distributions; and
- replay the accepted Level-4 final checkpoint zero-shot exactly once.

The zero-shot result decides only whether direct PPO is safe or a training-only online behavior
clone is required.  It cannot accept Level 5.  Any clone/PPO streams, gates, confirmation bank,
and waiting-opponent regression floor must be frozen in a separate protocol after this preflight,
not inferred from individual prospective failures.

## Scope exclusions

Level 5 does not add autonomous recipe selection, a third controlled worker, opponent mixtures,
stochastic policies, combat objectives, explicit denial reward, crop theft reward, terminal margin
optimization, recurrence, model-size changes, Rust neural inference, or Arena writes.  The exact
resident remains the live fallback.  Success permits the next curriculum decision; it does not
establish field transfer or rank progress by itself.
