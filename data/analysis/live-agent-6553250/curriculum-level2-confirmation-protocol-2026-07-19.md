# Curriculum Level 2 independent confirmation protocol — frozen 2026-07-19

## Purpose and immutability

This is the single confirmation authorized by the passing seed-61 discovery.  The Level-2
environment, teacher, observation/action contract, recipe catalog, network, optimizer schedule,
and coefficient-0.10 online teacher auxiliary are frozen at their discovery implementations.
No failed seed may be inspected or used to alter this run.

## Independent streams

- model and random-control seed: 67;
- behavior-clone teacher stream: seeds beginning at 5,200,000, 400,000 online labels;
- PPO environment stream: seeds beginning at 5,300,000, 2,000,000 transitions;
- exact prospective confirmation bank: seeds 2,007,000--2,008,999 inclusive;
- maximum episode length: 240 turns.

The behavior clone uses the discovery schedule: 100 environments, ten steps per 1,000-row chunk,
two shuffled epochs per chunk, minibatch 1,000, Adam `1e-3` cosine-decayed to `1e-4`, gradient
norm 1.0, and 14 Torch threads.  Its evaluation on the already-consumed preflight bank
2,003,000--2,004,999 is a launch-sanity diagnostic only.  It must clear the original clone floors
(80% overall, 75% nontrivial, 70% recipe, 65% height, and no more than 20 turns paired teacher
delay) before PPO may start; it contributes no confirmation evidence.

Before PPO starts, deterministic-teacher and random-legal controls for the new exact bank are
generated and hashed.  PPO uses 100 environments by 100 rollout steps, four epochs, minibatch
1,000, Adam `2.5e-4` linearly decayed to zero, gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01,
value coefficient 0.5, reward scale 0.01, gradient norm 0.5, target KL 0.03, 14 Torch threads, and
teacher auxiliary coefficient 0.10.  The 500,000-transition read is diagnostic and cannot stop the
run; only the frozen final confirmation decision applies.

## Final acceptance

On exactly the prospective bank, the deterministic final policy must achieve:

- at least 85% overall success;
- at least 80% success on nonzero-total-deficit starts;
- at least 70% success in every recipe family;
- at least 70% success in every board-height bucket;
- at most 40,000 `MOVE current` waits across the 2,000-episode exact action audit; and
- a productive HARVEST/MINE choice in at least 60% of legal, currently needed opportunities.

Teacher delay and advantage over random legal are recorded as diagnostics but do not add gates
that were absent from the parent confirmation rule.  A full pass accepts curriculum Level 2 and
opens design of the next curriculum abstraction.  It still cannot change the live resident or
authorize an Arena submission.
