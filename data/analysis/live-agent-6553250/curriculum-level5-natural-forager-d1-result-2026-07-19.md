# Curriculum Level 5 natural-forager D1 — result, 2026-07-19

## Verdict

**Pass D1 readiness.**  The deterministic no-growth natural forager is both materially active and
fully feasible for the unchanged Level-4 teacher.  The accepted Level-4 actor transfers at 99.6%
zero-shot, so behavior cloning or PPO is not justified before a prospective exact-bank test.

## Frozen teacher gates on seeds 500--999

| Measure | Result | D1 requirement | Verdict |
|---|---:|---:|---|
| Overall success | **500/500 = 100%** | >=90% | pass |
| Nontrivial success | **306/306 = 100%** | >=85% | pass |
| Worst recipe | **100%** | >=75% | pass |
| Worst height | **100%** | >=80% | pass |
| Tracked crop creation | **100%** | >=90% | pass |
| Renewable harvest | **100%** | >=85% | pass |
| Positive opponent score | **100%** | >=50% | pass |
| Opponent above one worker | **0/500** | 0 | pass |

The unchanged teacher emits zero illegal actions.  Median training/completion turns are 16/52,
median own score gain is 15, and the forager's mean/median score is 34.17/34.  The interaction is
not behaviorally equivalent to waiting even though opponent growth is excluded.

Random legal solves 0/500, creates the tracked crop in 20.8%, and completes a renewable harvest in
2.6%.  The task remains discriminative.

## Accepted-Level-4 zero-shot diagnostic

The frozen Level-4 confirmation checkpoint reaches:

- **498/500 = 99.60%** overall;
- **305/306 = 99.67%** nontrivial;
- **98.18%** worst recipe and **98.43%** worst height;
- **99.80%** crop creation and **100%** renewable harvest;
- median training/completion turns 16/53; and
- zero paired-teacher median delay.

Only seeds 541 and 879 fail.  They are recorded but not inspected or used for a fix.  Forager mean
score is 34.57, close to the teacher's 34.17, so the actor does not pass merely by suppressing the
opponent through a simulator artifact.

## Interpretation

Natural-resource depletion and active movement are already within the Level-4 actor's learned
robustness.  The complete-opponent D0 failure is therefore localized beyond initial contention:
dynamic crop-site occupation, rival planting/training, and compounded multiworker production are
the missing abstractions.  Spending labels or PPO decisions on the forager would add cost without
an observed capability deficit.

## Decision

Freeze exact prospective teacher/random controls and one zero-shot replay on seeds
2,019,000--2,020,999.  No learning stream is authorized.  A pass accepts this isolated interaction
level and advances to the next opponent mechanism; a failure closes zero-shot transfer and must be
diagnosed on the complete bank before any training protocol.

## Reproducibility anchors

- D1 protocol:
  `bf305e38fecfaccc54bbedaf418faef4b8b3884aefa5f7c46da3c2b16261af44`;
- teacher:
  `696917f90ff830c3b21a12b79c86061c7eef2e6ffcb96d5652768abe29171cbf`;
- random legal:
  `b51ca94464faed5b5e6c95158577c97755d564119b8bfc519d20c1bf2906ab7e`;
- Level-4 zero-shot:
  `860948a71cef9079a9cc946e506cbffe71583b59a86abb0ccbc9d0e2abb7d588`.
