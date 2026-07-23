# Curriculum Level 5 naturally funded third-worker D6 readiness — 2026-07-20

## Verdict

**Implementation-ready; fresh activation remains unproven.**  The D6 two-epoch transaction and
three-role controller satisfy every code-level integrity gate, so the frozen seeds 3,000--3,499
may be opened.  The allowed consumed replay warns that the fresh activation gates may fail; no
command, role, target, threshold, or interval was changed in response.

## Integrity evidence

- 13 focused release Rust tests pass;
- 22 focused Python environment/PPO tests pass;
- identical D6 batches reproduce all observations, masks, rewards, and 29 terminal ABI fields;
- the first trained worker is exactly `(2,2,0,2)`, the third is exactly `(1,1,1,0)`, and the roster
  never exceeds three;
- each successful transition increments a distinct funding-backed training-event count, so the
  second transaction cannot reuse the first epoch's receipt;
- standard-chopper and feeder productivity are state-confirmed separately; and
- the player observation/action contract and accepted checkpoint are unchanged.

## Consumed-seed warning

The deterministic teacher remains 500/500 on consumed seeds 0--499, but scale activation is
materially slower than D5:

| Measure | Consumed result | Frozen fresh floor |
|---|---:|---:|
| First-worker training | **95.40%** | >=90% |
| Third-worker training | **49.20%** | >=55% |
| Median third-worker training turn | **38** | record only |
| Fresh receipt before trained third worker | **100%** | 100% |
| Standard-chopper productivity | **92.40%** | >=75% |
| Feeder productivity | **40.00%** | >=45% |
| Opponent crop creation | **32.40%** | >=45% |
| Opponent own-crop harvest | **10.00%** | >=15% |
| Confirmed player-crop destruction | **91.40%** | >=60% |
| Maximum opponent workers | **3** | <=3 |

The mechanism is real—246 episodes train worker three and the feeder is productive in 200—but its
funding phase displaces the starter's crop work and often outlasts player-0 completion.  These
consumed rates are not protocol decisions.  The exact fresh controls decide whether the D6
abstraction is sufficiently active and feasible; failure stops actor replay rather than inviting
post-hoc threshold or policy repair.

## Execution anchors

- D6 protocol:
  `19b8eeb106dbf44f12db30a5ca5803e42c4837d1a00a0eb9c364005215a2fc39`;
- consumed readiness artifact:
  `648ab75ae69d6f6b0ccaca4b86c3cab6567d8398804a0d5c9e1a545dfc70b1cf`;
- Rust source / release shared library:
  `b8ea3c32b20701efeaffbb4fde10cc3693756e48038581ff4bf3a73bbb435d70` /
  `cc19b5dc81889bc8a4603fe3bcfb57cb69330e1ed954b39516ada5adcbbc772f`;
- Level-5 Python environment:
  `f34bd40e3c85dd5857501adf78e376b506dc68319d8c849fce5cbdde26d888f2`;
- PPO/evaluation selector:
  `06cdf9aaf7a3df6fca99cb5ad8d197b6e9d6b5a1ff1024f9ed75108a3099350d`;
- Level-5 evaluator:
  `33dd1578da2714cfb6585de62a303c912b824892545354f6e7fc7d1ef0bd530b`;
- focused Python tests:
  `29eefd80d2e361e1419dcc2a7ca4bda05c60131261fb5703ff580d5806a6c604`; and
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
