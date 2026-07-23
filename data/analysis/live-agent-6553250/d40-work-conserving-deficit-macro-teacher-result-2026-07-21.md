# D40 work-conserving deficit macro teacher — result (2026-07-21)

## Verdict

**Pass all 14 frozen gates and open a separate behavior-learning protocol.** D40 is the first
complete macro initializer in this cycle with positive mean margin and broad causal advantage. It
is not itself a submission candidate: no model has been trained, no deployable policy has been
qualified, and no TestSession, submission, or Arena action is authorized by this result.

## Integrity

Each arm contains the complete 16-seed x 2-seat x 8-opponent = **256-cell** grid for official seeds
9,670,000--9,670,015. All three policies have zero missing/duplicate keys, policy errors,
margin/return identity errors, invalid direct commands, provenance failures, worker-cap errors,
empty episodes, action-count errors, TRAIN-relevant deposit-prediction failures, or runner loops.

Independent teacher replicas are byte-identical:
`653dee375b1922bd43b74e6e9aa1b27503d8017350f3b8dcf3baed197827b8a5`.

## Outcome

| metric | work-conserving | D39 ablation | random |
|---|---:|---:|---:|
| mean own score | **211.914** | 126.543 | 69.320 |
| mean opponent score | **179.887** | 189.137 | 204.031 |
| mean margin | **+32.027** | -62.594 | -134.711 |
| worker-two rate | 97.66% | 97.66% | 55.08% |
| worker-three rate | **92.58%** | 49.61% | 1.56% |
| own renewable-crop rate | 99.61% | 94.53% | 96.48% |
| median non-idle jobs | **81** | 27.5 | 24 |
| total idle selections | **929** | 31,211 | 912 |
| catastrophes | **22** | 107 | 146 |
| negative-margin mass | **6,673** | 23,800 | 35,109 |

Mean paired margin improves **+94.621 versus D39** and **+166.738 versus random**. D40 improves
178/256 cells versus D39 (six tie, 72 regress) and 241/256 versus random (two tie, 13 regress).
Against D39, it adds 85.371 own score and removes 9.250 opponent score. Against random, it adds
142.594 own score and removes 24.145 opponent score.

Every opponent family improves over random, with large headroom over the -10 floor:

- `compact_gold` +250.750;
- `gold_adaptive` +233.281;
- `script_boss` +207.719;
- `silver_boss` +176.844;
- `mybot` +162.406;
- `legend_balanced` +132.875;
- `norx_native_three` +102.500; and
- `resident` +67.531.

## Mechanism conclusion

D39 already trained worker two, so D40's gain isolates work conservation after the first expansion.
When no job can immediately reduce the reserved TRAIN bill, the frozen D37 production/provenance
order now runs instead of `IDLE_ONE_TURN`.

- Idle selections fall by **97.02%** versus D39 (ratio 0.0298).
- Worker-three completion rises by **42.97 percentage points**.
- Mean non-idle jobs rises from 50.16 to 79.94.
- Own score rises much more than opponent score falls, while both move favorably.

The result resolves the earlier “extra workers are unaffordable” paradox. Workers are not valuable
because TRAIN alone is cheap; they become affordable and valuable when the scheduler continues
renewable/competitive production during temporary funding gaps. Exact resource priority and broad
productive work are complementary, not competing policies.

## Frozen gates

All pass:

- complete clean teacher, D39 ablation, and random grids;
- byte-identical teacher repeat;
- paired margin >=+50 versus random (observed +166.738);
- paired margin >=+20 versus D39 (observed +94.621);
- worker two >=90% (97.66%);
- worker three >=50% (92.58%) and improvement >=15 points (+42.97);
- idle count <=half D39 (2.98% of D39);
- crop and non-idle activity gates; and
- all opponent-family breadth/tail gates.

## Authorized next step

Freeze D40 as a teacher and open D41 behavior learning. D41 must:

1. export every macro decision with legal mask, observation, selected action, stage, return target,
   map/seat/opponent provenance, and episode hash on disjoint training/validation/confirmation
   seeds;
2. train behavior cloning first, then use PPO only from the cloned initializer;
3. evaluate learned policies closed-loop against the exact D40 teacher and independent opponents;
4. require deterministic Rust/Python inference parity and a 100k-compatible deployment estimate;
   and
5. keep confirmation, candidate construction, TestSession, and Arena sealed until a learned policy
   passes a separately frozen D41 gate.

## Reproducibility

- protocol: `5c0190f86fe88bbe869f45f530aaea960c8301572dae383f831ac674387fed82`
- macro environment: `1397d8b8c783fe6732a0b8f8f4a3b9b1c263281fb59cd4fd69d221cdcf8aa1be`
- panel runner: `6aa1e26fe759990e5cc7933871c05e9fe2d06e36730d3edd16c5e421756dc2ae`
- analyzer: `e92a29f7edcd6b9f3940cf0b201c3dadbfdd90a857ad40b5a87c62e68a80c3a5`
- analyzer tests: `7e1477dbaedc76b335cd716cfa0452e69333e7af7e4ce1fe4f07d3305c8fb5eb`
- D39 ablation: `47474b7ac52151ae86159bbd392485b3c1f32cb0e6ae2fd1010ac834442a13a6`
- random control: `d56d09a3e4b6822c2f047ec0c06eb914ece9a31ccf1e2f10c9f53a830f436536`
- analyzer JSON: `dab4bb75f7ad2af8a8e4d69828dd6b80954d897c7e03cfd089ef8a2edc012c65`

Focused verification: 13 Rust macro tests and five D40 analyzer tests pass. Existing unrelated
compiler warnings remain unchanged.
