# Curriculum Level 1 exact replication protocol — frozen 2026-07-19

## Purpose

Independently replicate the BFS-distance, behavior-cloning, and PPO result after correcting the
completion-order evaluation flaw.  The replicate tests run-to-run and seed-stream stability.  It
does not tune the architecture and does not authorize a submission.

## Frozen implementation and controls

- observation: 104x11x22 with selected-worker BFS proximity in channel 2 and own-home BFS
  proximity in channel 103;
- model: the unchanged 34,926-parameter spatial actor-critic;
- exact-seed invariant: every evaluation must contain each seed in the requested half-open
  interval exactly once, irrespective of completion order;
- exact debug teacher SHA-256:
  `43a5ef18618353dd60568be821755008791242afdfdcb76b435fb5fcaef84dde`;
- exact official teacher SHA-256:
  `934261b115321b0a81331824b2547b6939cdaf9fdadc1ed20aa6b37efe8bbe5f`;
- exact official random-legal SHA-256:
  `3fbd41a3b0482cd8f9b57c1d24f7c3436c60c6d5185def6f7f9cc0414a7a4de5`.

The original run-one protocol and thresholds remain authoritative where this addendum does not
change seed accounting.

## Part R1 — behavior-clone replicate

- model seed: 47;
- teacher-label seeds begin at 3,000,000;
- exactly 100,000 online labels;
- 100 environments, ten steps per 1,000-row chunk;
- two shuffled cross-entropy epochs per chunk, minibatch 1,000;
- Adam `1e-3`, cosine decay to `1e-4`;
- 14 Torch threads;
- sanity evaluation uses the already consumed exact debug bank 5,000--5,999.

The sanity gate is the original debug gate: at least 80% overall, 75% nonzero-deficit, 65% height
floor, and no more than 15 median turns behind the exact teacher.  Failure stops before the fresh
replicate evaluation bank is opened.

## Part R2 — PPO replicate

Conditional on R1 passing:

- initialize from the frozen R1 checkpoint;
- PPO training seeds begin at 3,100,000;
- 100 environments x 100 rollout steps;
- one million total transitions; Stage A at 250,000;
- four epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale
  0.01, gradient norm 0.5, target KL 0.03;
- exact fresh evaluation bank: 2,001,000--2,001,999.

Stage A is the first opening of the fresh bank and must reach 70% overall, 65% nonzero-deficit,
55% height floor, and teacher median +25 turns or better.  Failure stops the run.  If it passes,
the schedule continues unchanged to one million transitions.  Final acceptance requires 85%
overall, 80% nonzero-deficit, 75% height floor, and teacher median +15 turns or better.

## Interpretation and stop rules

- Both run one and the exact replicate must pass their frozen final gates before Level 2 opens.
- Run-one scores do not strengthen replicate thresholds after the fact.
- The fresh replicate bank may be used only for the predeclared Stage A and final checks; no
  hyperparameter or checkpoint selection may be fitted to it.
- Failure after a strong R1 clone makes a teacher auxiliary loss eligible on consumed debug data;
  it does not authorize repeated fresh-bank trials.
- Success authorizes randomized-worker Level 2 only.  The resident, Arena agent, and current
  submission remain unchanged.

