# Curriculum Level 5 sustained funded-trio D8 result — 2026-07-20

## Verdict

**Stop D8 at fresh controls.**  On fresh seeds 4,000--4,499 the turn-180 teacher solves 499/500
and random legal solves 0/500.  The player objective, recipes, heights, legality, funding receipts,
worker cap, rival harvest, and bounded destruction all pass.  Two frozen opponent-activation gates
fail:

- feeder productivity is **87.60% (438/500)** versus 88%; and
- rival crop creation is **76.60% (383/500)** versus 80%.

Per protocol, the accepted actor, learning, prospective seeds, deployment, YT, and Arena remain
closed.  D8 establishes neither actor success nor a learning deficit.

## Frozen control decision

| Measure | Teacher result | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **99.80% / 99.67%** | >=90% / >=90% | pass |
| Worst recipe / height | **98.36% / 99.20%** | >=85% / >=88% | pass |
| Player crop / renewable harvest | **100% / 99.80%** | >=90% / >=95% | pass |
| Illegal selected actions | **0** | 0 | pass |
| Success before turn 180 | **0** | 0 | pass |
| Median success turn | **180** | >=180 | pass |
| First-worker training | **100%** | >=98% | pass |
| Third-worker training | **92.60%** | >=92% | pass |
| Fresh receipt before both training events | **100%** | 100% | pass |
| Standard-chopper productivity | **100%** | >=98% | pass |
| Feeder productivity | **87.60%** | >=88% | **fail** |
| Maximum opponent workers | **3** | <=3 | pass |
| Opponent crop creation | **76.60%** | >=80% | **fail** |
| Opponent own-crop harvest | **66.20%** | >=65% | pass |
| Confirmed player-crop destruction | **99.80%** | >=95% | pass |
| Destruction above one | **0** | 0 | pass |
| Random-legal overall | **0/500** | <=5% | pass |

The feeder miss is two episodes and the crop miss is seventeen, but both thresholds were frozen
before opening the bank.  Neither is rounded upward or waived.

## Conditional activation decomposition

Worker three trains in 463 episodes.  Within those episodes:

- the feeder is productive in 438/463 = **94.60%**;
- a rival crop is created in 383/463 = **82.72%**; and
- the rival harvests its own crop in 331/463 = **71.49%**.

None of the 37 untrained episodes creates a rival crop or activates the feeder.  The unconditional
gates therefore combine two serial probabilities: completing the second funding/training epoch,
then establishing the planter/feeder loop.

| Opponent mechanism | D6 median-64 | D7 turn-120 | D8 turn-180 |
|---|---:|---:|---:|
| Third-worker training | 55.20% | 85.80% | **92.60%** |
| Feeder productivity | 43.40% | 80.00% | **87.60%** |
| Rival crop creation | 32.80% | 68.60% | **76.60%** |
| Rival own-crop harvest | 13.40% | 50.60% | **66.20%** |

Longer observation continues to help, but crop creation lags third-worker training by 16 percentage
points at turn 180.  This is no longer explained solely by early terminal censoring.

## Root-cause analysis at different abstraction levels

### Command

The planter and feeder both seek remaining natural fruit after worker three appears.  The feeder
can consume the last usable seed while the starter is still trying to establish its crop.  The
commands are individually productive but compete for a prerequisite.

### Scheduler

At two workers the D6/D7/D8 controller immediately redirects the starter from the already accepted
D5 planting loop into the second funding epoch.  Crop establishment is postponed until after worker
three is paid.  This is backwards for a compounding economy: scale is purchased before its
renewable supply source is secured.

### Workforce economics

The second transaction is affordable in 92.60%; affordability is not the main failure.  The
remaining gap is sequencing.  A strong workforce is profitable when its producer/funder cycle is
established before expansion and workers do not steal each other's prerequisites.

### Curriculum

Another blind horizon extension would mix the same two serial events and retain the scheduler
defect.  The next isolated test should preserve D5's two-worker planting behavior until one crop is
actually created, then begin the unchanged second funding transaction.  This changes one ordering
decision while retaining natural payment, talents, cap, post-scale roles, and the turn-180 task.

### Learning and compute

The accepted actor was correctly not evaluated.  No actor failure means no clone/PPO task and no
profitable YT workload.  Local controls still complete in about three seconds; YT remains reserved
for a multi-million-transition run after a control-valid actor deficit.

### Goal and transfer

D8 creates no submission candidate and no Arena evidence.  It does produce a useful economic
conclusion: workforce count is downstream of renewable-supply sequencing, not a purchase heuristic
in isolation.

## Next hypothesis

At exactly two rival workers, retain the D5 regenerative planter plus standard chopper until the
rival has created one crop.  Only then may the starter begin the unchanged fresh-receipt funding
epoch for worker three.  After training, retain the same three roles.  Test this crop-before-scale
scheduler at the already justified turn-180 horizon on a separately frozen seed bank.

## Reproducibility anchors

- D8 protocol:
  `a38d899798c60feed4cec5085588b6373e6523a18301a938506a9bfdd9403d07`;
- readiness record:
  `004eefd177cf9a40bda9cc678c4c57a3eb06256417d1ba40c2dcb39e5fae3d12`;
- teacher artifact:
  `a7edfa18e7d1c1751dfc30b784cb3e228b74940cdb2a54c616be16013ffd1e61`;
- random-legal artifact:
  `9adcd31bed806693ad563567968abbd80e0963982428bb42037945dc647a8a64`;
- Rust source:
  `fbda7052ca1bdf842dbadc32bb0fcf619b89b4cee79d680255e5ecead29946e4`;
- release shared library:
  `a4ce9d5460afc13fa2e288e7b9cdd15198481daa877db975b2b38fe114facf81`;
  and
- accepted checkpoint, deliberately not evaluated:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
