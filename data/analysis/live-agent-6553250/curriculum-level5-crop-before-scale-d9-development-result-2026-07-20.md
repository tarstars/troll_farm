# Curriculum Level 5 crop-before-scale D9 development result — 2026-07-20

## Verdict

**Pass D9 development and authorize one separately frozen prospective confirmation without
learning.**  On fresh seeds 4,500--4,999, teacher/random are 500/500 and 0/500.  The unchanged
accepted Level-4 actor is 477/500 = **95.40%** and passes every frozen player and opponent gate.

No clone or PPO step is justified: the actor already transfers to the first control-valid
sustained, naturally funded three-worker interaction.  No new checkpoint or submission candidate
is created.

## Fresh controls

| Measure | Teacher | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **100% / 100%** | >=90% / >=90% | pass |
| Worst recipe / height | **100% / 100%** | >=85% / >=88% | pass |
| Player crop / renewable harvest | **100% / 100%** | >=90% / >=95% | pass |
| Illegal selections / success before 180 | **0 / 0** | 0 / 0 | pass |
| First / third-worker training | **100% / 95.80%** | >=98% / >=85% | pass |
| Fresh receipt before both transactions | **100%** | 100% | pass |
| Standard-chopper / feeder productivity | **100% / 91.20%** | >=98% / >=80% | pass |
| Rival crop creation / own-crop harvest | **100% / 88.00%** | >=95% / >=80% | pass |
| Player-crop destruction / above one | **99.80% / 0** | >=95% / 0 | pass |
| Maximum rival workers | **3** | <=3 | pass |
| Random legal | **0/500** | <=5% | pass |

The Rust transition invariant verifies crop creation before every worker-three training event.  All
recorded transactions have fresh funding receipts and ordinary costs.

## Fixed actor

| Measure | Actor | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **95.40% (477/500)** | >=75% | pass |
| Nontrivial success | **95.02% (286/301)** | >=72% | pass |
| Worst recipe | **93.44%** | >=60% | pass |
| Worst height | **93.60%** | >=65% | pass |
| Player crop presence | **95.40%** | >=85% | pass |
| Renewable player harvest | **99.20%** | >=90% | pass |
| Paired-teacher median delay | **0 turns** | <=30 | pass |
| Third-worker training / feeder productivity | **96.80% / 92.20%** | >=85% / >=80% | pass |
| Rival crop creation / own-crop harvest | **100% / 89.40%** | >=95% / >=80% | pass |
| Player-crop destruction / above one | **99.00% / 0** | >=95% / 0 | pass |
| Fresh funding / cap | **100% / 3** | 100% / <=3 | pass |

The actor's failures are not concentrated in a recipe or map height: every recipe remains above
93% and every height above 93%.  The opponent is at least as active under the actor as under the
teacher, so the pass is not caused by evading the intended interaction.

## Analysis at different abstraction levels

### Command and role

No role required learning.  Once the rival's seed prerequisite is reserved by ordering, the
accepted actor retains its crop, renewable loop, and requested worker behavior under destruction
and three active rival roles.

### Scheduler

Crop-before-scale is the decisive causal change.  Relative to D8 fresh controls, rival crop
creation rises from 76.60% to 100% and harvest from 66.20% to 88.00%, while third training rises
from 92.60% to 95.80% despite the deliberate planting delay.  Securing supply first improves both
production and later scale rather than trading one away.

### Workforce economics

This resolves the apparent contradiction between “extra workers are unaffordable” and strong bots
using many workers.  A third worker is profitable after the two-worker economy has created a
renewable source and can fund expansion without starving its own prerequisite.  Worker count alone
was never the policy.

### Learning and compute

The accepted actor's 95.40% pass means there is no D9 learning deficit.  A YT training allocation
would fit behavior the checkpoint already performs; it is not profitable.  YT remains relevant for
the later first-move selector or a future control-valid opponent scope that actually fails.

### Goal and transfer

D9 is curriculum evidence, not an Arena candidate.  It still supplies the requested recipe and
does not implement autonomous macro selection or compact deployment.  One prospective exact bank
is required before accepting this abstraction.

## Reproducibility anchors

- D9 protocol:
  `b8e68069388cb9a88866d5c29b8ffb0155cd01d0240702138554d0a1cba68193`;
- readiness record:
  `bbbdbadd788f7eb7da3aa1409ed6de4009b0d2fcabe630b8d851f304232c9b6b`;
- teacher artifact:
  `7ac430db5adf57be14184f38bfc1cf7b813c537e90bcf39753bee3b7cde8afcb`;
- random artifact:
  `761924245345a3709d5f7925ac733c1c8160f278a921e2f012f9e6ef1c9e3d90`;
- fixed-actor artifact:
  `cfcd84d09b778e0eb17cebf02a0700d4af26cc2dd576a31ec914dbc7499c7d3e`;
- implementation source:
  `73f7659abf7114a5cfe33bddd6825c6518b9192cb6e3b60d0bcc80fda30633fb`;
  and
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
