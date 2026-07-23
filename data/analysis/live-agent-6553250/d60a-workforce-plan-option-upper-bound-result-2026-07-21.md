# D60a workforce-plan option upper bound — result (2026-07-21)

## Verdict

**Reject the fixed workforce-phase plan interface, but retain semantic batch options as the next
representation.** D60 is exact, highly active, outcome-sensitive, and has a large heterogeneous
hindsight upper bound. It nevertheless fails the frozen crop-safety conjunction: oracle-selected
episodes create a crop in 226/256 tasks (**88.28%**) rather than the required 95%.

The failure is informative rather than marginal. In 30 tasks, the margin oracle deliberately
chooses a no-crop liquidation trajectory. The fixed `pre3`/`post3` pair has no way to re-enter
investment after profitable felling begins. Per protocol, no fixed plan is selected and D61 is not
the originally proposed fixed-plan selector. The next eligible representation is a renewable-safe,
state-conditioned option chosen at natural job-batch boundaries.

No candidate, TestSession, submission, or Arena action opens.

## Integrity and activation

- Both 17 x 256 matrices contain 4,352 complete rows and are byte-identical.
- `pre3_balanced__post3_balanced` matches the independent direct-D40 arm in every terminal,
  action-plane, action-hash, state-hash, and telemetry field.
- All rows have zero illegal commands, provenance failures, deposit-prediction failures, worker-cap
  violations, return-identity errors, action-count errors, or option-accounting errors.
- All 15 non-anchor plans change at least 10% of action hashes; observed change rates span 62.89%
  to 99.22%.
- Every semantic mode overrides D40 in both workforce phases. Across the catalog, `harvest`,
  `renew`, and `fell` issue 7,652/32,588, 1,468/9,622, and 2,820/9,056 eligible pre3/post3
  overrides respectively.
- Non-anchor mean margins span **69.168** points, from -24.488 to +44.680.

## Whole-game headroom

The per-task hindsight oracle clears every value/diversity gate:

| Metric | Result | Frozen gate |
|---|---:|---:|
| Mean margin gain vs D40 | **+47.398** | >=+20 |
| Strictly improved tasks | **226/256 (88.28%)** | >=30% |
| Mean own-score delta | **+8.977** | >=0 |
| Mean opponent-score delta | **-38.422** | <=0 |
| Worst opponent-family gain | **+20.781** | >=+8 |
| Non-anchor plans with >=4 strict gains | **11** | >=4 |
| Worker-three reach | **89.84%** | >=85% |
| Crop creation | **88.28%** | >=95% — **fail** |

All eight opponent families gain, from +20.781 against `silver_boss` to +75.875 against
`legend_balanced`. The oracle uses all 16 plans; no single plan or phase mode explains the value.
This validates the semantic action vocabulary and whole-game objective while rejecting the frozen
two-clock temporal interface.

## Fixed-plan warning

The best fixed plan on this consumed bank is `pre3_fell__post3_fell`, with +9.348 mean margin over
D40. That apparent gain is achieved by losing 55.500 own points while suppressing 64.848 opponent
points, and it creates a crop in only **53.52%** of tasks. It is therefore neither a candidate nor a
plan to confirm. Selecting it would reproduce the exact safety failure caught by the protocol.

## Post-result crop diagnosis

The following calculations are explicitly exploratory and do not alter the failed gate:

- every one of the 30 no-crop oracle selections is a strict margin improvement; the oracle's 30
  ties all use crop-producing trajectories;
- restricting hindsight selection separately in each task to crop-producing rows still leaves
  +44.469 mean margin, +10.777 own score, -33.691 opponent score, 218 strict improvements, and a
  +17.875 worst-family gain; and
- restricting to the six plans that happened to create crops in all 256 tasks still leaves
  +30.844 oracle margin headroom, but its worst-family gain falls to +2.406.

Thus the value is not an artifact of crop extinction, but a deployable controller must know when
to stop liquidation and resume renewal. A terminal crop filter cannot be deployed and may not be
used to rescue D60.

## Multilevel conclusion

- **Action vocabulary:** pass. Harvest/materialize, renew/invest, and fell/liquidate all cause
  broad, distinct complete-game outcomes while exact D40 mechanics remain intact.
- **Temporal abstraction:** fail. One persistent mode for the entire two-worker or post-three
  phase cannot express investment, capitalization, liquidation, and reinvestment in sequence.
- **Objective:** terminal margin contains a genuine suppression signal, but without a renewable
  state constraint its oracle rationally accepts irreversible no-crop trajectories.
- **Learning implication:** do not train a selector over the 16 fixed plans. Move the four semantic
  choices to complete free-worker batch boundaries, keep exact D40 underneath, and make renewable
  establishment/preservation part of the legal option state. First test a deterministic random
  state-conditioned population for crop-safe headroom; PPO remains sealed until that richer
  representation passes.

## Evidence

- protocol SHA-256:
  `5e204108ca6fef181aa16e5b8479895815564eac75c517853c34fb18e83497b9`;
- repeated matrix SHA-256:
  `00416deba0b37c3c81de4db9fce9c2665f4617ae4f2dac9d2ee14ce350794aed`;
- result JSON SHA-256:
  `87c80cf68422a6630a6a57909042fc4b061ba5e097a2c1c90dcbd678207465ee`;
- runner SHA-256:
  `b6031b1f809b95cdc4a69597b908a8efefcb7504750ca165dd3cd3834ec86dad`;
- analyzer SHA-256:
  `a9948eaf20d91676d3e329c46af27a8c2d0d217c9fa995d10251db37866c25f6`;
- focused verification: four Rust runner tests and two analyzer tests pass.
