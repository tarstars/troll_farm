# Curriculum Level 5 one-shot crop reaper D4 protocol — frozen 2026-07-20

## Question

Does one confirmed destruction of player 0's renewable crop require new control learning after the
accepted regenerative-planter abstraction, when the opponent still has exactly one worker and
workforce growth remains forbidden?

D3 established that opponent movement, natural-resource contention, planting, and one-worker
self-renewal transfer prospectively without learning.  D4 adds only a bounded crop-loss event on
fresh development seeds 2,000--2,499.

## Frozen opponent and player-0 lifecycle

Player 1 starts from the D3 deterministic regenerative-planter policy and retains exactly its
starter worker.  Before any confirmed destruction, once player 0's tracked BANANA crop exists, the
worker moves to that crop and emits `CHOP` while standing on it.  A destruction is counted only
when the exact state transition confirms that the targeted tracked crop no longer exists.  The
opponent then permanently returns to its D3 planting/harvesting loop.  It may destroy at most one
player-0 crop in an episode and may never `PICK`, `MINE`, or `TRAIN`.

The retained D2 pre-creation recovery invariant still replans an occupied player-0 crop site.  The
player-0 teacher additionally has one crop-loss lifecycle invariant frozen before this protocol:
after its tracked crop is destroyed, it banks any unrelated carried load before fetching a
replacement BANANA seed.  This changes no actor input, action mask, reward, checkpoint, or player-0
task.

## Consumed-bank calibration disclosure

Opponent construction and lifecycle diagnosis used only already-consumed seeds 0--1,999.  Before
the lifecycle invariant, the teacher solved 1,957/2,000 and emitted 137 illegal stale selections;
clearing the destroyed crop removed the illegal selections but did not change those outcomes.  A
trace localized the remaining failure to a farmer indefinitely carrying unrelated full cargo
after crop loss.  The frozen bank-before-reseed invariant raised the teacher to 2,000/2,000 with
zero illegal selections.

On that same consumed interval:

- random legal solved 0/2,000;
- the unchanged accepted Level-4 actor solved 1,966/2,000 = 98.30%;
- confirmed destruction occurred in 80.35% of teacher and 85.00% of actor episodes;
- the opponent created its own crop in 86.20% of teacher and 80.35% of actor episodes;
- it harvested its own crop renewably in 53.00% of teacher and 52.35% of actor episodes; and
- it remained at one worker in every episode.

Across the 1,500 seeds shared with the D3 consumed actor artifact, D3 solved 1,493 and D4 solved
1,473.  Twenty-three D3 successes became D4 failures, three D3 failures became D4 successes, and
24 of D4's 27 failures followed a confirmed destruction.  Thus the new mechanism is active and
causally harder without approaching the complete-opponent workforce jump.

No seed at or above 2,000 informed the opponent, lifecycle invariant, thresholds, or decision.

## Integrity gates before opening the bank

- repeated D4 batches are deterministic;
- every prior waiting, complete, recovery, forager, and planter regression remains passing;
- observation and action dimensions remain 104x11x22 and 13x11x22;
- destruction telemetry is terminal-only and never an actor input;
- the opponent has exactly one worker, never trains, and records at most one destruction; and
- the release shared library and accepted checkpoint match the hashes below.

Failure of an integrity gate stops D4 before fresh execution.

## Fresh D4 controls

Run teacher and random legal exactly once on every seed 2,000--2,499 with 100 environments, a
240-turn horizon, and random seed 89.  The teacher must reach:

- at least 99% overall and 99% nontrivial success;
- at least 98% in every recipe and every height;
- at least 99% player-0 crop presence and renewable harvest;
- zero illegal selected actions;
- at least 95% positive opponent score;
- at least 75% opponent crop creation and 45% opponent own-crop harvest;
- at least 70% confirmed player-0 crop destruction, with no episode above one; and
- exactly one opponent worker in every episode.

Random legal must remain at or below 5% overall success.  Failure stops D4 before actor replay,
training, or prospective seeds.

## Fixed-actor zero-shot gate

If both controls pass, evaluate exactly once on the same 500 seeds using accepted Level-4
checkpoint
`b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882` and the teacher artifact
from this bank as the paired-turn baseline.  No weight, seed, threshold, or action rule may change.
The actor must reach:

- at least 95% overall and 93% nontrivial success;
- at least 90% in every recipe and 93% in every height;
- at least 97% player-0 crop presence and renewable harvest;
- paired-teacher median completion delay no greater than 10 turns; and
- the same opponent score, crop, harvest, destruction, and one-worker gates as the teacher.

A pass authorizes one separately frozen prospective bank without learning.  A teacher pass plus
actor failure permits diagnosis and design of a new learning protocol, but D4 itself authorizes no
behavior clone, PPO transition, checkpoint selection, deployment, or Arena action.

## Reproducibility anchors before execution

- lifecycle-corrected consumed teacher:
  `45676eb4629abd85e8eff4230bce78e9884c0200071c6efe3486c9ad30861768`;
- consumed random legal:
  `d79e2bd1f0b4e17665777ead4ea7ab190a32e0d5186150a91e75fb0a678698eb`;
- consumed fixed actor:
  `143955eb2d3cf1dbfefa49f03f25c382f429567abb007b20d5533960947ba5d0`;
- Level-5 checkpoint evaluator:
  `10ea4a6733161c7318b2714b1831a978fcf721ce505d12493a193ba85e6c44fb`;
- Level-5 Python environment:
  `4755d98bbcca527f96dc153824320532d62e3cc699e763a7d1bb3031432818be`;
- Rust Level-5 source:
  `bc3f6e3caa2ffe49b3e26a7c35bf08559c7ecf6c01a69c6e9a08cc615993601d`;
- release shared library:
  `a8865a1bf9f3f483f8b8060605e1a0ee0e8cb690a171f938af87f4e0c90f35a4`; and
- accepted Level-4 checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
