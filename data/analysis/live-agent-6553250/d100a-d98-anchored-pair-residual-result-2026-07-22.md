# D100a D98-anchored pair residual — result

Date: 2026-07-22  
Verdict: **fail; bounded pair residuals add real but insufficient value and are closed**

## Outcome

D100 is mechanically exact. Two independent 20-worker executions produced byte-identical
193 x 128 matrices; their D40 baselines are byte-identical to the frozen pre-change D98 reference.
All 64 parent policies reproduce the corresponding D98 terminal, action-plane, action-hash, and
state-hash fields, while all 64 zero residuals reproduce every parent behavioral and mechanics
field. All 24,704 rows pass budget, pair/job/provenance, preview, legality, reward, crop-safety,
transaction, worker-cap, and hash checks.

The anchored residual adds genuine headroom but misses the frozen magnitude floors:

| Incremental metric | D100 | Required | Verdict |
|---|---:|---:|---|
| Parent-oracle mean margin | 96.094 | reference | — |
| Strict-superset mean margin | 99.414 | reference | — |
| Increment over parent oracle | +3.320 | >=+5 | fail |
| Strict random improvements | 43/128 | >=24 | pass |
| Random policies with >=2 strict wins | 12/64 | >=12 | pass |
| Strict-superset gain over D40 | +52.102 | >=+55 | fail |
| Worst opponent-family gain over D40 | +41.688 | >=+15 | pass |
| Mean own / opponent delta vs D40 | +34.219 / -17.883 | >=0 / <=0 | pass |
| Worker-three / crop rate | 92.19% / 100% | >=85% / 100% | pass |
| Selected random rows with override / joint override | 47 / 34 | >=24 / >=16 | pass |

Selected residual rows span all four jobs, three provenance classes, both seats, and all eight
opponent families. The pair interaction is therefore useful and broad; its upper-bound increment
is simply too small to justify training this representation.

## Activity diagnosis

| Activity gate | D100 | Required | Verdict |
|---|---:|---:|---|
| Randoms retaining parent worker-three reach | 64/64 | >=56 | pass |
| Randoms changing action hash in >=25% of tasks | 39/64 | >=56 | fail |
| Randoms overriding in >=25% of tasks | 39/64 | >=48 | fail |
| Randoms joint-overriding in >=10% of tasks | 49/64 | >=32 | pass |
| Randoms spanning 3 jobs / 2 provenances | 39/64 | >=48 | fail |
| Crop-safe policy-task rows | 24,704/24,704 | all | pass |
| Fixed paired-delta range | 11.555 | >=20 | fail |

The best fixed arm, `random_41`, is descriptive and unselectable. It overrides 112/128 tasks,
joint-overrides 112/128, spans all jobs and three provenances, preserves worker-three reach, and
gains +3.719 over its own parent. This confirms that an anchored residual can improve one fixed
parent, but a one-shot local pair correction does not provide enough population-level separation
or enough incremental oracle value over the already strong parent bank.

## Decision

Close the D100 initialization without selecting `random_41`, tuning its scale, changing the
override budget, expanding the catalog or feature vector, or training PPO/CEM/imitation on maps
`9,823,000--9,823,007`. Per the frozen rule, the next experiment must switch representation. The
retained fact is narrow: same-turn pair interaction is worth about three oracle-margin points when
anchored to D98, so it may be a component of a higher-level controller but is not a sufficient
learning target by itself.

## Reproducibility anchors

- protocol: `1180aab70fb6220d82778f3caf4758d8e03dd90faef8c8166c3230555c9995b9`;
- implementation lock: `c8a7e220d3ce4ee5ae39fe52f596de79a1d49666c8bf940cd402cb2944e386d6`;
- analyzer lock: `4f515a444d50f4554b13ea6de2470899facd576e59873bfe9b479a1d302b91d9`;
- population matrix, both repeats:
  `c27bacd7122ef536c084b43e3168062e1a0afcdc9308245962dc0ef307c56182`;
- D100/D98 baseline:
  `b9cf5ffda4f853efe0441f5d72f75876dac8497bbb610bd730ce2994d828b01d`;
- frozen D98 reference matrix:
  `d741d502f8105af88c7495eb25c99d890fe213f5c17eaef942c9260a365ad335`;
- analyzer: `1f4cc7da438c5fcc238f402db9a441f0fd30eab53dc2c35684110fa5c5c4c795`;
- result JSON: `3ca4e6289823e2725a985bb4854e384f534a33fcf4ed0089f09fb56fb3db98f7`.
