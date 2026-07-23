# Curriculum Level 5 one-shot crop reaper D4 — result, 2026-07-20

## Verdict

**Pass D4 development without learning.**  The isolated one-worker crop reaper is deterministic,
material, and feasible.  On fresh seeds 2,000--2,499 the lifecycle-corrected teacher solves
500/500, random legal solves 0/500, and the unchanged accepted Level-4 actor solves
488/500 = 97.60%.  No clone, PPO transition, checkpoint selection, or parameter change is
justified.

## Integrity and execution

Eleven Rust Level-3 tests and 18 focused Python Level-5/PPO tests pass.  The observation/action
contract is unchanged, destruction is terminal telemetry only, the opponent never exceeds one
worker, and no episode records more than one confirmed destruction.

The first shell launch used the script path and failed on `ModuleNotFoundError` before importing the
environment, constructing a state, or opening a seed.  The unchanged frozen controls were then run
once with module invocation.  This packaging correction produced no intermediate experimental
observation.

## Frozen D4 controls

| Measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Teacher overall / nontrivial | **100% / 100%** | >=99% / >=99% | pass |
| Teacher worst recipe / height | **100% / 100%** | >=98% / >=98% | pass |
| Teacher crop / renewable harvest | **100% / 100%** | >=99% / >=99% | pass |
| Illegal teacher selections | **0** | 0 | pass |
| Positive opponent score | **100%** | >=95% | pass |
| Opponent crop creation | **85.80%** | >=75% | pass |
| Opponent own-crop harvest | **55.00%** | >=45% | pass |
| Confirmed player-crop destruction | **79.40%** | >=70% | pass |
| Opponent above one worker / destruction above one | **0 / 0** | 0 / 0 | pass |
| Random-legal overall | **0/500** | <=5% | pass |

The teacher trains at median turn 14 and completes at median turn 62.  The opponent averages
30.376 score, creates 0.868 crops, records 4.18 own-crop harvests, and destroys 0.794 player crops
per episode.

## Accepted-Level-4 zero-shot gate

| Measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **488/500 = 97.60%** | >=95% | pass |
| Nontrivial success | **98.68%** | >=93% | pass |
| Worst recipe | **94.74%** | >=90% | pass |
| Worst height | **96.00%** | >=93% | pass |
| Player-0 crop / renewable harvest | **98.00% / 99.40%** | >=97% / >=97% | pass |
| Paired-teacher median delay | **0 turns** | <=10 | pass |
| Positive opponent score | **100%** | >=95% | pass |
| Opponent crop / own-crop harvest | **81.20% / 55.80%** | >=75% / >=45% | pass |
| Confirmed player-crop destruction | **86.60%** | >=70% | pass |
| Opponent above one worker / destruction above one | **0 / 0** | 0 / 0 | pass |

The actor completes at median turn 66 and gains a median 15 score.  Of its 12 failures, 11 follow
a confirmed destruction; only two failures finish with a replacement crop, while nine had already
completed a renewable harvest.  These are aggregate post-verdict diagnostics and did not alter the
gate or policy.

## Interpretation at multiple levels

### Interaction level

One rival crop-loss event is a real perturbation: on the 1,500 consumed seeds shared with D3 it
caused a net 20 additional actor failures, and it activates in 86.6% of fresh actor episodes.  It is
nevertheless bounded; the accepted actor retains 97.6% task success and 99.4% renewable-harvest
success.

### Curriculum level

Natural contention, opponent planting/self-renewal, and one confirmed destruction now compose
without new learning while workforce growth remains excluded.  The next unisolated mechanism in
the rejected complete opponent is therefore workforce/resource compounding rather than generic
crop interaction.

### Learning level

The actor remains 2.4 points below the teacher but clears every functional and stratified floor
with zero median paired delay.  Training on D4 now would spend fresh labels to repair a narrow tail
before prospective transfer establishes that the tail is stable.

## Decision

Freeze one exact prospective confirmation on seeds 2,023,000--2,024,999 using the same lifecycle,
opponent, teacher, random policy, checkpoint, and gates.  No learning is authorized.  A prospective
pass accepts the one-shot destruction abstraction and advances to an isolated workforce-growth
protocol; it does not authorize deployment or Arena submission.

## Reproducibility anchors

- D4 protocol:
  `befc99e81ed1cb4907fce9c4e2428984166bcfda16d09302067cf47b219d822e`;
- teacher:
  `69efc56362d766537b7134cbc42d9d31ec12d931945a521c1ff7f965a0a17bfb`;
- random legal:
  `86323667836b25b062fdbac6b615ff03cdd39ad5c2ff5702141e4c8ca005febb`; and
- fixed actor:
  `01a2d949dfc807465fe3f6988190fb092c62278e0117a461191a60ce747fbc9f`.
