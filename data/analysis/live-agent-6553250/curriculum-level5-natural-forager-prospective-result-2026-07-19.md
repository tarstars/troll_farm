# Curriculum Level 5 natural-forager prospective result — 2026-07-19

## Verdict

**Pass; accept the isolated natural-forager interaction abstraction.**  The unchanged accepted
Level-4 checkpoint clears every frozen prospective gate on exact seeds
2,019,000--2,020,999.  No behavior cloning, PPO, checkpoint selection, or parameter change occurs.

This result establishes robustness to an active opponent starter that moves, harvests reset-time
natural fruit, and banks.  It does not establish robustness to opponent planting, training,
created-crop interaction, multiworker compounding, field opponents, or Arena transfer.

## Control validity

| Control measure | Result | Frozen requirement | Verdict |
|---|---:|---:|---|
| Teacher overall | **1,999/2,000 = 99.95%** | >=99% | pass |
| Teacher nontrivial | **99.91%** | >=98% | pass |
| Teacher worst recipe | **99.61%** | >=95% | pass |
| Teacher worst height | **99.80%** | >=95% | pass |
| Teacher crop / renewable | **100% / 99.95%** | >=99% / >=99% | pass |
| Illegal teacher selections | **0** | 0 | pass |
| Positive opponent score | **100%** | >=95% | pass |
| Opponent above one worker | **0/2,000** | 0 | pass |
| Random-legal overall | **0/2,000** | <=5% | pass |

The teacher's median training/completion turns are 14/51.  The forager averages 34.23 score.  It
is materially active in every episode while obeying the no-growth boundary exactly.

## Fixed-actor prospective gate

| Actor measure | Result | Frozen requirement | Margin |
|---|---:|---:|---:|
| Overall success | **1,994/2,000 = 99.70%** | 95% | +4.70 pp |
| Nontrivial success | **1,170/1,175 = 99.57%** | 93% | +6.57 pp |
| Worst recipe success | **99.19%** | 90% | +9.19 pp |
| Worst height success | **99.60%** | 93% | +6.60 pp |
| Tracked crop creation | **99.80%** | 97% | +2.80 pp |
| Renewable harvest | **99.75%** | 97% | +2.75 pp |
| Paired-teacher median delay | **0 turns** | <=10 turns | 10 turns |
| Material opponent activation | **100%** | >=95% | +5 pp |
| Opponent above one worker | **0/2,000** | 0 | pass |

The weakest recipe is `level1-anchor` at 245/247 = 99.19%; three recipes are 100%.  Height buckets
range from 99.60% to 99.80%.  Median training/completion turns are 14/52, median own score gain is
15, and the opponent's mean/median score is 34.56/34.

## Multi-level conclusion

### Action and representation

The accepted observation already represents opponent position, inventory, score, workforce, and
shared plant state sufficiently for this level.  Active movement and natural-fruit depletion do
not require a new network, memory, action vocabulary, or teacher bootstrap.

### Curriculum

The stark boundary between the natural forager (99.7% actor) and complete baseline (51.8% actor,
57.4% teacher) localizes the next gap.  It is not generic opponent presence; it begins with dynamic
crop-site invalidation and then rival planting/training compounding.

### Project and transfer

No new model was created, so there is nothing new to package or submit.  The value is information:
skip a needless PPO run for initial contention and focus the next curriculum on dynamic target
recovery.  The exact resident and live Arena agent remain unchanged.

## Decision

Close natural-forager Level 5 as accepted.  The next single mechanism should test **dynamic crop
site recovery** on fresh development data before reintroducing the rejected complete opponent.
Do not reopen forager training, tune its policy, or call this result field qualification.

## Reproducibility anchors

- prospective protocol:
  `7722c85b6e9196aa49b9a3aefc067e30d4487ebeab9536bb6b20f86cc2a7f035`;
- teacher control:
  `fc46b9cd5da299c8c879db2c6787d1290241520b162c5113e4d5c018a74e6777`;
- random-legal control:
  `58ea23604ea64e5e628cfe4820a0f28761d568b0b74cd2e35027cc87c08bc06d`;
- fixed-actor replay:
  `c3ab34aa99792ae8a62349a671643101bd5480a273c41428f3419b0d7ca3d811`;
- unchanged actor checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
