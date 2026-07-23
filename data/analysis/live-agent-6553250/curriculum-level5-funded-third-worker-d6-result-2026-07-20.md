# Curriculum Level 5 naturally funded third-worker D6 result — 2026-07-20

## Verdict

**Stop D6 at fresh controls.**  Teacher and random legal solve 500/500 and 0/500 on fresh seeds
3,000--3,499, and paid worker three appears in 55.20%, but the frozen opponent-activation gates
fail: feeder productivity is 43.40% versus 45%, opponent crop creation is 32.80% versus 45%, and
opponent own-crop harvest is 13.40% versus 15%.  Per protocol, the accepted actor, learning,
prospective seeds, deployment, YT, and Arena are not opened.

This rejects D6 as a sufficiently active discriminator under the current early-terminal task.  It
does not show that the actor handles three workers, and it does not show that a third worker is
unaffordable.

## Frozen control decision

| Measure | Teacher result | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **100% / 100%** | >=85% / >=82% | pass |
| Worst recipe / height | **100% / 100%** | >=75% / >=80% | pass |
| Player crop / renewable harvest | **100% / 100%** | >=80% / >=85% | pass |
| Illegal selected actions | **0** | 0 | pass |
| First-worker training | **97.20%** | >=90% | pass |
| Third-worker training | **55.20%** | >=55% | pass |
| Fresh receipt before both training events | **100%** | 100% | pass |
| Standard-chopper productivity | **94.00%** | >=75% | pass |
| Feeder productivity | **43.40%** | >=45% | **fail** |
| Maximum opponent workers | **3** | <=3 | pass |
| Opponent crop creation | **32.80%** | >=45% | **fail** |
| Opponent own-crop harvest | **13.40%** | >=15% | **fail** |
| Confirmed player-crop destruction | **92.40%** | >=60% | pass |
| Destruction above one | **0** | 0 | pass |
| Random-legal overall | **0/500** | <=5% | pass |

The teacher completes at median turn 64.  Among trained episodes worker three arrives at median turn
48, leaving only about 16 turns before the environment terminates.  The result narrowly clears the
training-rate floor but fails to give the new feeder and post-training planter enough exposure to
be a valid scale test.

## Long-episode diagnostic already contained in the random control

Random player-0 episodes last to the 240-turn timeout.  Without any opponent change, those same
fresh seeds yield:

- 96.20% third-worker training at median turn 74;
- 89.20% feeder productive activation;
- 79.80% opponent crop creation; and
- 73.60% opponent own-crop harvest.

This comparison is not evidence about actor quality, because the player policies and episode
lengths differ.  It is strong evidence that D6's controller and resources can produce a three-role
economy when given time.  The failed teacher activation is caused by observation-window truncation,
not a broken transaction or permanently unaffordable third worker.

## Analysis at different abstraction levels

### Transaction

Worker three is paid in 276/500 teacher episodes after a distinct post-worker-two funding receipt.
The ordinary transaction is possible on a majority of fresh games.  Its median completion at turn
48 makes clear why “can pay” and “profitable before the current objective ends” are different
questions.

### Scheduling

Funding worker three temporarily redirects the only harvest-capable starter away from crop
establishment.  The standard chopper continues working, but planting and harvesting begin only
after the second transaction.  This is the real opportunity cost of workforce scale that a gifted
worker or immediate `TRAIN` test would miss.

### Curriculum

The current objective was designed to prove one training transaction and one renewable loop.  It
terminates near turn 64—far earlier than a 300-turn Arena economy—and therefore censors late
opponent compounding.  Adding stronger late-game opponents to this objective now measures whether
they activate before early termination, not whether the actor survives them.

### Learning and compute

No actor observation exists, so no clone/PPO deficit is established and no YT benchmark is useful.
Training against a control-invalid task would fit an undefined comparison.

### Goal and transfer

D6 creates no submission candidate and no live-rank evidence.  Its value is redirecting the
curriculum from increasingly elaborate early-terminal opponents toward sustained closed-loop
operation, which is necessary for a real 300-turn controller.

## Next hypothesis

Retain the exact D6 opponent but introduce a fixed minimum evaluation turn before success may
terminate—initially turn 120, still within the 240-turn safety horizon.  Player 0 must keep the same
trained recipe, crop presence, renewable harvest, and score-flow milestones valid at or after that
turn.  This tests whether the accepted actor can sustain its economy through a fully activated paid
third-worker opponent without changing the opponent after seeing D6.

## Reproducibility anchors

- D6 protocol:
  `19b8eeb106dbf44f12db30a5ca5803e42c4837d1a00a0eb9c364005215a2fc39`;
- readiness record:
  `feacd6bedfd6dafcdb991480584e7283b2c13315732151ce7ba7b4507db9a31e`;
- teacher artifact:
  `7bcb2becff967f34bf805e99c331dcbf6e8d60efe8cf5f6117cd1c5a03e48656`;
- random-legal artifact:
  `302cb13934f323a673db997d7127089ee95754c920db9373a3257b44842cb7b5`; and
- accepted checkpoint, deliberately not evaluated:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
