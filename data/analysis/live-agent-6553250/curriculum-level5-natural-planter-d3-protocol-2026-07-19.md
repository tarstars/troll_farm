# Curriculum Level 5 one-worker regenerative planter D3 protocol — frozen 2026-07-19

## Question

Does adding opponent planting and one renewable production loop require new control learning after
the accepted natural-forager level, when opponent chopping and workforce growth remain excluded?

D2 proved that legal pre-creation site recovery does not bridge directly to the complete opponent.
It also established replanning as a correctness invariant.  D3 now isolates the next economic
mechanism on fresh development seeds 1,500--1,999.

## Frozen opponent policy

Player 1 retains exactly its starter and may emit only `MOVE`, `HARVEST`, `DROP`, or `PLANT`:

1. while it has no tracked crop, it harvests fruit only from plants present at reset;
2. after acquiring a fruit, it moves to a deterministic free cell within radius three of its own
   shack, preferring water adjacency and then `(radius, y, x)`, and plants that species;
3. while its crop exists, it banks carried fruit, harvests the tracked crop whenever ripe, and may
   forage reset-time natural plants while waiting; and
4. if its crop disappears, it repeats the same acquisition and planting cycle.

The policy may never `CHOP`, `PICK`, `MINE`, or `TRAIN`.  It receives no inventory, unit, score, or
map modification.  Player 0 uses the unchanged randomized-recipe teacher/task plus the D2
pre-creation recovery invariant: if its uncreated planned crop cell becomes occupied, it reruns the
unchanged player-0 selector.  Recovery still stops after the tracked player-0 crop is created.

## Pre-freeze calibration disclosure

Policy construction and activation used only already-consumed seeds 0--1,499.  Before enabling the
D2 invariant, the opponent planted in 100% but exposed 742 stale teacher selections.  With the
invariant, the teacher reached 1,500/1,500 with zero illegal selections; the opponent planted in
100%, harvested its own crop in 88.73%, scored in 100%, and never trained.  The frozen Level-4 actor
reached 99.53%, while random legal reached 0%.  No seed at or above 1,500 informed the policy or
gates.

## Integrity gates

- deterministic repeated batches are byte-identical;
- all prior waiting, complete, recovery, and natural-forager regressions remain passing;
- the observation remains 104x11x22 and the action mask 13x11x22;
- added opponent crop/harvest values are terminal telemetry only, never actor inputs; and
- the opponent has exactly one worker and emits only the four allowed verbs.

## Fresh D3 controls

Run teacher and random legal once on every seed 1,500--1,999.  The teacher must reach:

- at least 99% overall and 99% nontrivial success;
- at least 98% in every recipe and every height;
- at least 99% player-0 crop presence and renewable harvest;
- zero illegal selected actions;
- at least 99% opponent crop creation, 80% opponent own-crop harvest, and 95% positive opponent
  score; and
- exactly one opponent worker in every episode.

Random legal must remain at or below 5% overall success.  Failure stops D3 before actor replay,
training, or prospective seeds.

## Fixed-actor zero-shot gate

If both controls pass, evaluate exactly once on the same 500 seeds using the accepted Level-4
confirmation checkpoint
`b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
No weight, seed, threshold, or action rule may change.  It must reach:

- at least 95% overall and 93% nontrivial success;
- at least 90% in every recipe and 93% in every height;
- at least 97% player-0 crop presence and renewable harvest;
- paired-teacher median completion delay no greater than 10 turns; and
- the same opponent activation and one-worker gates as the teacher.

A pass authorizes a separately frozen prospective bank without learning.  A teacher pass plus actor
failure permits diagnosis and a new learning protocol, but D3 itself authorizes no behavior clone,
PPO transitions, prospective seed, deployment, or Arena action.

## Reproducibility anchors before execution

- corrected consumed teacher preflight:
  `b31323b7d7645cfabf17c92548841461b0f0f7dbb995177bf45439f2fb9b2ce2`;
- consumed random preflight:
  `ab0ba9314db667d155523fc770869b70239643e0722ccf7762448211db8a5c89`;
- consumed fixed-actor preflight:
  `ef65d6c3089e79d5489dcaa780d30373bb09c6d8091237d302a5c7eb11eae7bd`.
