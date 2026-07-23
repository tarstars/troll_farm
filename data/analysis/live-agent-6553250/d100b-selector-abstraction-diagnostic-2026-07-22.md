# D100b static-selector abstraction diagnostic

Date: 2026-07-22  
Scope: post-result diagnosis on the consumed D100 maps; this is not a candidate-selection result.

## Inputs and reproducibility

- D100 parent population: `c27bacd7122ef536c084b43e3168062e1a0afcdc9308245962dc0ef307c56182`
- D100 independent D40 baselines: `b9cf5ffda4f853efe0441f5d72f75876dac8497bbb610bd730ce2994d828b01d`
- D100 result: `3ca4e6289823e2725a985bb4854e384f534a33fcf4ed0089f09fb56fb3db98f7`
- Analyzer: `9ec75e0bd86b5fff748bb9641d2441840c6f7083f3ad2d93491219c6da59a08f`
- Machine-readable result: `3dc11e8b5652949ef0acc8615ef0486403e823a5dbe3236df0fabc1db5afa809`

The matrix contains 65 policies and 128 paired tasks. D40's mean margin is `47.3125`; the
per-task D98-parent oracle reaches `96.09375`, a gain of `+48.78125`.

## Abstraction ceilings

All in-sample groupings below are optimistic: the same outcomes choose and score the policy.
They measure an upper ceiling, not selectable performance.

| Information used to choose one parent | Gain over D40 | Task-oracle gain captured | Worst family gain |
|---|---:|---:|---:|
| One global policy | +6.578 | 13.5% | -9.375 |
| Seat | +8.664 | 17.8% | -6.312 |
| Opponent identity | +13.203 | 27.1% | +5.000 |
| Map | +15.070 | 30.9% | -4.938 |
| Opponent identity + seat | +19.633 | 40.2% | +7.875 |
| Map + seat | +20.203 | 41.4% | +5.500 |
| Map + opponent identity | +36.289 | 74.4% | +25.438 |
| Full task hindsight | +48.781 | 100.0% | +39.375 |

The apparently large map-plus-opponent ceiling is hindsight on the exact evaluated outcome. Its
held analogues collapse:

- leave-one-map-out global selection gains only `+3.094`, captures 6.3% of the oracle, and loses
  `-9.938` in its worst family;
- leave-one-map-out opponent-identity selection loses `-1.422` overall and `-17.562` in its worst
  family;
- choosing from the opposite seat of the same map/opponent gains only `+2.070`, captures 4.2%, and
  loses `-11.000` in its worst family.

Policy ordering is correspondingly unstable. Mean Spearman correlation is `0.217` between maps
and `0.103` across seats for the same map/opponent; individual correlations extend below zero.

## Decision

Close static selection over the D98 bank. A first-move, map, seat, or opponent-family selector is
not a credible route to the parent oracle, and the consumed-map hindsight ceilings must not be
used to nominate a candidate. The useful value is mostly trajectory-specific: it requires online
state ownership or a different coherent scheduling architecture, not a larger static classifier.

The next iteration therefore returns to immutable public-replay evidence and tests a specific
architectural hypothesis: whether leading agents sustain their own renewable production while a
separate worker suppresses opponent-created crops. No resident, submission, or platform action is
opened by D100b.
