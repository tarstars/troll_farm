# Curriculum Level 5 regenerative-planter prospective result — 2026-07-19

## Verdict

**Pass; accept isolated one-worker opponent planting and self-renewal.**  The unchanged accepted
Level-4 checkpoint clears every frozen gate on exact unopened seeds 2,021,000--2,022,999.  No
behavior clone, PPO decision, model selection, or parameter change occurs.

This result does not cover opponent chopping, picking, mining, training, multiworker production,
field transfer, deployment, or Arena play.

## Control validity

| Control measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Teacher overall / nontrivial | **100% / 100%** | >=99% / >=99% | pass |
| Teacher worst recipe / height | **100% / 100%** | >=98% / >=98% | pass |
| Teacher crop / renewable harvest | **100% / 100%** | >=99% / >=99% | pass |
| Illegal teacher selections | **0** | 0 | pass |
| Opponent crop creation | **100%** | >=99% | pass |
| Opponent own-crop harvest | **90.15%** | >=80% | pass |
| Positive opponent score | **100%** | >=95% | pass |
| Opponent above one worker | **0/2,000** | 0 | pass |
| Random-legal overall | **0/2,000** | <=5% | pass |

The teacher trains/completes at median turns 14/52.  The opponent averages 34.02 score, creates
1.008 crops, and records 6.662 own-crop harvests per episode.  Random episodes run longer, allowing
the same one worker to demonstrate the renewable loop in all 2,000 controls without making the
player-0 task trivial.

## Fixed-actor prospective gate

| Actor measure | Result | Requirement | Margin |
|---|---:|---:|---:|
| Overall success | **1,994/2,000 = 99.70%** | >=95% | +4.70 pp |
| Nontrivial success | **1,167/1,171 = 99.66%** | >=93% | +6.66 pp |
| Worst recipe | **99.11%** | >=90% | +9.11 pp |
| Worst height | **99.40%** | >=93% | +6.40 pp |
| Player-0 crop presence | **99.85%** | >=97% | +2.85 pp |
| Player-0 renewable harvest | **99.80%** | >=97% | +2.80 pp |
| Paired-teacher median delay | **0 turns** | <=10 | 10 turns |
| Opponent crop creation | **100%** | >=99% | +1 pp |
| Opponent own-crop harvest | **89.90%** | >=80% | +9.90 pp |
| Opponent above one worker | **0/2,000** | 0 | pass |

The weakest recipe is `lean-chopper` at 223/225.  Three recipes are 100%.  Actor median
training/completion turns are 14/52, median score gain is 15, and opponent mean/median score is
34.47/34.  Six failures remain sealed from diagnosis because all gates pass.

## Multi-level conclusion

### Representation and action

The existing observation already exposes enough shared plant, opponent position, inventory,
score, and workforce state for this interaction.  A new channel, memory module, or action grammar
is not needed merely because the rival creates and harvests a persistent crop.

### Curriculum

Accepted opponent mechanisms now include movement, natural-resource depletion, planting, and
one-worker renewable harvesting.  Combining those mechanisms still leaves the actor at 99.7%, so
the complete-baseline collapse cannot be attributed to self-renewal alone.

### Next causal boundary

D2 failures and the complete-opponent terminal pattern point next to **crop destruction**: allow one
opponent worker to chop while still forbidding training.  Workforce growth must remain a later,
separate experiment so destruction cost and multiworker compounding are not conflated again.

## Decision

Accept the regenerative-planter abstraction without producing a new checkpoint.  Freeze a new
development protocol for one-worker crop destruction on unused consumed/development seeds before
changing the opponent.  No deployment or Arena submission is authorized.

## Reproducibility anchors

- prospective protocol:
  `64bda249311c906b00dc5952fa4e85044df34b4a76be7fcc30306961455fb74a`;
- teacher control:
  `6a6ed625fe0ddd0145d5436a78a48cfa486254e126487fb32b5787824b1bacd0`;
- random-legal control:
  `b50e725c06b291751c2d39dca48e717e6be994597d5a7e65deba5af308acbc35`;
- fixed-actor replay:
  `b7f38645ffe1c74890ae7ae70e235ac049203ab22e433fbbc9c91d19b9e45d7a`;
- unchanged actor checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
