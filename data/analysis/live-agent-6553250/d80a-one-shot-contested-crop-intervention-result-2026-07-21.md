# D80a one-shot contested-crop intervention result (2026-07-21)

## Verdict

**Reject and close the one-shot contested top-four rule at Stage A.** The rule is mechanically
exact and changes only one decision in an active game, but it intervenes in **253/256 tasks
(98.83%)**, above the frozen maximum of 230 tasks and 90%. Per protocol, paired score and outcome
value remain unopened.

Do not relax the task corridor, expand or shrink the challenger ranks, inspect D80 outcome deltas,
or reuse maps 9,910,000--9,910,015. D80 produces no policy, candidate, TestSession, submission, or
Arena action.

## Accepted execution and integrity

- The two accepted 512-row matrices are byte-identical at SHA-256
  `fbf3b4e2106b8db604edf3aa5c914e82f205f02ba2741591c2c191aa31a21c30`.
- Both complete 20-thread runs use about 20 CPU cores and finish in 9.777 and 10.178 seconds.
- There are zero invalid commands, provenance failures, deposit-prediction failures, worker-cap
  violations, reward-identity errors, nonfinite features, illegal selections, exact-prior fallback
  mismatches, action-count errors, or intervention-accounting failures.
- The three nonintervention candidate tasks match control exactly in every terminal, action-plane,
  action-hash, and state-hash field.
- Every intervention changes the action hash: 253 interventions and 253 changed tasks.
- Both seats, all eight opponents, challenger ranks one/two/three, and `FELL_BANK`/`RENEW` execute.

Before accepted execution, two no-output diagnostic launches exposed first a result-mutex scope
bug and then a stale release executable. The written amendment documents the one-line lock repair,
the explicit release rebuild, the absence of any output/outcome, and the unchanged experiment.

## Frozen Stage A gates

Seven of nine gates pass. The two failures describe the same saturation:

| Gate | Result | Requirement | Verdict |
|---|---:|---:|---|
| Intervention tasks | **253/256** | 32--230 | **fail** |
| Changed-task rate | **98.83%** | 10%--90% | **fail** |
| Intervention equals changed tasks | 253 = 253 | exact | pass |
| Opponent/seat breadth | 8/8, both | >=6, both | pass |
| Challenger rank/plane breadth | ranks 1/2/3, planes 5/7 | >=2, >=2 | pass |
| Repeat/integrity/parity | exact | exact | pass |

Because Stage A fails, Stage B is not computed. The result JSON intentionally contains no paired
margin, own-score, opponent-score, crop, workforce, catastrophe, or negative-mass comparison.

## Multilevel interpretation

1. **Geometry:** an opponent within two steps of one of D40's top four crop jobs is nearly
   universal over a whole game. Proximity is predictive of commitment at a state, but it is not a
   selective episode-level trigger.
2. **Interface:** limiting a controller to one intervention solves D79's thousands-of-overrides
   problem, yet the fixed blind challenger still replaces almost every trajectory.
3. **Measurement:** a task-level action hash is hypersensitive: one changed decision makes an
   entire task “active.” It cannot distinguish D79's thousands of overrides from D80's single
   override. Future protocols should retain exact action hashes for parity while measuring
   authority with decisions per episode and an explicit intervention budget.
4. **Causality:** D80 supplies no value result. It is invalid to infer benefit or harm from the
   serialized outcome columns after the frozen Stage A stop.
5. **Next abstraction:** stop blind spatial promotion. First establish the upper bound of choosing
   among the anchor and a small contested concrete-job set at one frozen boundary through complete
   counterfactual rollouts. Only a sufficiently valuable action set justifies learning or
   approximating a value selector.

## Next experiment

Freeze D81 on new official maps as a one-boundary exact-rollout action-set audit. Follow D40 to the
first frozen contested boundary, independently execute control and each available top-four
contested challenger, then continue exact D40 to terminal. A crop/workforce-safe hindsight oracle
tests representation headroom; all arms remain nondeployable. Activity is counted as one evaluated
boundary per eligible episode and no longer uses a changed-task upper ceiling as a proxy for
decision-level sparsity.

If the action-set upper bound fails, close contested concrete challengers. If it passes, the next
step is a bounded Monte-Carlo/value controller on fresh maps—not another blind rule, post-result
D80 threshold, or D79 network.

## Evidence

- protocol SHA-256: `4c9670bfcddcbf2f7c39740c7db2c18daea12aefce4345bca42f99fb43c7f58e`;
- result JSON SHA-256: `aed00d1c02969f14f8f5d707f617d086f68b2d91b4c09abd30b182a1825093b6`;
- repeated matrix SHA-256: `fbf3b4e2106b8db604edf3aa5c914e82f205f02ba2741591c2c191aa31a21c30`;
- accepted runner SHA-256: `11c1807772f5062a0301785b3ddcb08fd8b1f20f46ae443a6a7a206f0ff36456`;
- analyzer SHA-256: `005facc8a08d69b016a6466b5d529d4825a3f5236a8aff155cec7152531cac8b`.
