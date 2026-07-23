# Curriculum Level 5 naturally funded two-worker D5 protocol — frozen 2026-07-20

## Question

Does naturally financing and productively operating exactly one additional opponent worker cause a
new control failure after natural contention, regenerative planting, and one bounded player-crop
destruction have already transferred prospectively without learning?

D1, D3, and D4 all retain one opponent worker.  The rejected complete D0 opponent trains multiple
workers in 100% of episodes but bundles that growth with an unrestricted economy.  D5 isolates the
first workforce transition on fresh development seeds 2,500--2,999.

## Frozen opponent

Player 1 begins with the generated map, ordinary symmetric starting inventory, and one ordinary
starter.  No resource, worker, talent, crop, score, cooldown, or position may be gifted or edited.
The second-worker specification is fixed to the standard chopper `(2,2,0,2)`, whose one-worker
training cost is 5 PLUM, 5 LEMON, 1 APPLE, and 5 IRON when iron exists.

Before training, the starter deterministically gathers and banks missing cost resources from
natural plants or iron.  Even when the starting wallet is already sufficient, training is blocked
until the starter has harvested or mined and successfully banked at least one external cost item.
Carried funding is banked before another acquisition.  Candidate resources are ordered by current
deficit first, then exact navigation distance, resource type, row, and column.  A depleted required
plant may be camped until fruit appears.  The opponent requests `TRAIN 2 2 0 2` only after the
external-funding receipt exists and the ordinary bank can pay the full referee cost.

Training is permanently disabled after the second worker appears.  The opponent may never exceed
two workers.  After training:

- the original starter follows the accepted regenerative-planter lifecycle, using natural fruit,
  one tracked home crop, renewable harvest, and banking;
- the trained chopper first targets player 0's tracked BANANA crop until at most one destruction is
  state-confirmed, then chops only plants that existed at episode start, excluding both players'
  tracked crops, and banks wood; and
- neither worker uses `PICK`, and no command is supplied by the complete baseline or RHEA search.

This necessarily adds funding work, a normal TRAIN transaction, role parallelism, and sustained
natural-plant chopping.  It does not add a third worker, repeated player-crop destruction,
unrestricted opponent policy selection, stochasticity, or a reward change.

## Required telemetry and integrity gates

Before opening fresh development seeds:

- identical seeds and player-0 actions must reproduce every observation, mask, reward, and terminal
  field byte-for-byte;
- all prior waiting, complete, recovery, forager, planter, and reaper tests must pass;
- the observation/action contract remains 104x11x22 and 13x11x22;
- terminal telemetry must expose opponent training turn, external-funding receipts, and confirmed
  productive actions by the trained worker without adding actor inputs;
- every observed training follows at least one verified external-funding receipt and ordinary
  affordability, no opponent exceeds two workers, and no episode records more than one player-crop
  destruction; and
- the accepted checkpoint remains byte-identical to the anchor below.

Implementation diagnosis and determinism tests may use only already-consumed seeds 0--2,499.  The
opponent specification, action priority, thresholds, fresh interval, actor, and player-0 lifecycle
may not be tuned from those outcomes.

## Fresh D5 development controls

Run teacher and random legal exactly once on every seed 2,500--2,999 with 100 environments, a
240-turn horizon, and random seed 89.  The teacher must reach:

- >=90% overall and >=88% nontrivial success;
- >=82% in every recipe and >=88% in every height;
- >=92% player-0 crop presence and >=95% renewable harvest;
- zero illegal selected actions;
- exactly two terminal opponent workers in >=75% of episodes and never more than two;
- a verified external-funding receipt before 100% of successful opponent training events;
- at least one confirmed trained-worker productive action in >=60% of all episodes;
- >=65% opponent crop creation and >=25% opponent own-crop renewable harvest; and
- >=50% confirmed player-crop destruction, with no episode above one.

Random legal must remain <=5% overall.  Any integrity or control failure stops D5 before fixed-actor
replay, learning, prospective seeds, deployment, or Arena transfer.

## Fixed-actor zero-shot gate

If both controls pass, evaluate the unchanged accepted Level-4 checkpoint exactly once on the same
500 seeds against the exact teacher artifact.  It must reach:

- >=85% overall and >=82% nontrivial success;
- >=75% in every recipe and >=80% in every height;
- >=90% player-0 crop presence and renewable harvest;
- paired-teacher median completion delay <=20 turns; and
- the same workforce, funding-receipt, trained-worker activation, opponent-crop, harvest, and
  destruction gates as the teacher.

A pass permits one separately frozen prospective confirmation without learning.  A valid teacher
plus actor failure permits diagnosis and a separately frozen clone/PPO protocol.  Neither outcome
authorizes source integration or Arena submission.

## Compute decision

The 500-seed controls and actor replay remain local because comparable D4 runs complete in seconds;
YT orchestration would dominate their cost.  If D5 authorizes a multi-million-transition learning
run, benchmark 100,000 end-to-end transitions on the validated YT GPU path before choosing local
or YT execution.  No YT write or operation is authorized by this protocol alone.

## Pre-implementation anchors

- accepted D4 prospective result:
  `b3f4b4ea89e84a6f860f1cbb65f1e6fa0caba0fc4efe2b1b6cae49b57f9b892b`;
- Level-5 checkpoint evaluator:
  `10ea4a6733161c7318b2714b1831a978fcf721ce505d12493a193ba85e6c44fb`;
- Level-5 Python environment:
  `4755d98bbcca527f96dc153824320532d62e3cc699e763a7d1bb3031432818be`;
- Rust Level-5 source:
  `bc3f6e3caa2ffe49b3e26a7c35bf08559c7ecf6c01a69c6e9a08cc615993601d`;
- focused Python tests:
  `28612512f06ade95269f32fa86a06b905623822464384fceef52e4c2608d39dc`;
- release shared library:
  `a8865a1bf9f3f483f8b8060605e1a0ee0e8cb690a171f938af87f4e0c90f35a4`; and
- accepted Level-4 checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
