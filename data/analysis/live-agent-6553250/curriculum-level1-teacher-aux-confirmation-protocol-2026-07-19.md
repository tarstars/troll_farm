# Curriculum Level 1 teacher-auxiliary confirmation protocol — frozen 2026-07-19

## Objective

Test whether the coefficient-0.10 online teacher auxiliary transfers to an independent model,
training stream, and exact evaluation bank. This is the only fresh confirmation for the current
Level 1 formulation. It is not a submission gate.

## Frozen behavior-clone stage

- model seed: 53;
- online teacher-label stream begins at 4,000,000;
- exactly 100,000 labels, 100 environments, ten steps per 1,000-row chunk;
- two shuffled epochs, minibatch 1,000, Adam `1e-3`, cosine decay to `1e-4`;
- 14 Torch threads;
- sanity evaluation uses the consumed exact debug bank 5,000--5,999.

The clone must pass the original sanity thresholds: 80% overall, 75% nonzero-deficit, 65% height
floor, and teacher median +15 turns or better. Failure stops before fresh evaluation controls or
learned evaluation are opened.

## Frozen PPO stage

Conditional on clone success:

- initialize from that exact checkpoint;
- model seed 53 and PPO training seed base 4,100,000;
- 100 environments x 100 rollout steps;
- 250,000-transition Stage A; one million maximum;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale
  0.01, gradient norm 0.5, target KL 0.03;
- constant online teacher auxiliary coefficient 0.10;
- exact fresh learned-evaluation bank 2,002,000--2,002,999;
- teacher and random-legal controls for that exact bank are generated and hashed before learned
  evaluation; random-control RNG seed is 53.

Stage A requires at least 70% overall, 65% nonzero-deficit, 55% height floor, and teacher median
+25 turns or better. Failure stops. Passing continues without changes to one million.

Final acceptance requires at least 85% overall, 80% nonzero-deficit, 75% height floor, and teacher
median +15 turns or better. The exact post-run action audit must additionally select HARVEST on at
least 60% of legal HARVEST opportunities and emit no more than 20,000 `MOVE current` waits across
the 1,000 episodes.

## Decision rule

- Passing every gate establishes Level 1 reproducibility and authorizes randomized-worker Level 2.
- Failure closes coefficient 0.10 and the current auxiliary formulation; do not tune on the fresh
  bank.
- Neither result changes the resident or authorizes Arena submission.
- All later curricula still require exact-engine and layered field transfer before deployment.

