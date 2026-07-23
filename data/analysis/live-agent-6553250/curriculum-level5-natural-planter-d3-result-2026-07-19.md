# Curriculum Level 5 one-worker regenerative planter D3 — result, 2026-07-19

## Verdict

**Pass D3 readiness without learning.**  The isolated one-worker regenerative planter is active,
deterministic, and feasible.  On fresh seeds 1,500--1,999 the teacher solves 500/500, random legal
solves 0/500, and the unchanged accepted Level-4 actor solves 496/500 = 99.20%.  No clone, PPO
transition, checkpoint selection, or parameter change is justified.

## Integrity and calibration

The opponent may only move, harvest, drop, and plant.  It never chops, picks, mines, or trains.  Its
crop creation and own-crop harvest are tracked as terminal telemetry but are not exposed to the
actor.  Ten Rust and 26 Python curriculum regressions pass; observation/action dimensions remain
unchanged.

An explicitly disclosed consumed-bank preflight first found 742 stale player-0 teacher selections.
Enabling the already-tested D2 pre-creation recovery invariant removed all of them and raised the
teacher from 99.73% to 100% on consumed seeds.  This adjustment occurred before the D3 protocol and
before any seed at or above 1,500 was opened.

## Frozen D3 controls

| Measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Teacher overall / nontrivial | **100% / 100%** | >=99% / >=99% | pass |
| Teacher worst recipe / height | **100% / 100%** | >=98% / >=98% | pass |
| Teacher crop / renewable harvest | **100% / 100%** | >=99% / >=99% | pass |
| Illegal teacher selections | **0** | 0 | pass |
| Opponent crop creation | **100%** | >=99% | pass |
| Opponent own-crop harvest | **89.60%** | >=80% | pass |
| Positive opponent score | **100%** | >=95% | pass |
| Opponent above one worker | **0/500** | 0 | pass |
| Random-legal overall | **0/500** | <=5% | pass |

The teacher completes at median turn 52 after training at turn 14.  The opponent averages 34.05
score, creates 1.008 crops, and records 6.986 own-crop harvests per episode.  This is a persistent
renewable loop rather than a one-time planting marker.

## Accepted-Level-4 zero-shot gate

| Measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **496/500 = 99.20%** | >=95% | pass |
| Nontrivial success | **99.00%** | >=93% | pass |
| Worst recipe | **98.15%** | >=90% | pass |
| Worst height | **98.37%** | >=93% | pass |
| Player-0 crop / renewable harvest | **99.40% / 99.40%** | >=97% / >=97% | pass |
| Paired-teacher median delay | **0 turns** | <=10 | pass |
| Opponent crop / own-crop harvest | **100% / 88.40%** | >=99% / >=80% | pass |
| Opponent above one worker | **0/500** | 0 | pass |

The actor's median completion turn is 54 and median score gain is 15.  Its four failures are
recorded but are not inspected or used for a repair.

## Interpretation

### Interaction level

Opponent self-renewal alone does not explain the complete-baseline collapse.  The accepted actor
already reacts adequately to a rival crop and the shared plant field; its chopper can interact with
that crop without losing the player-0 production contract.

### Curriculum level

Natural movement/resource contention and one-worker planting/self-renewal are now separately
feasible.  The remaining complete-opponent gap is narrowed to opponent crop destruction and/or
workforce compounding, not generic opponent planting.

### Learning level

The actor trails the teacher by only four episodes and zero median turns.  Training on this level
would spend labels and PPO decisions to relearn a capability already above every frozen gate.

## Decision

Freeze one exact prospective confirmation on seeds 2,021,000--2,022,999 using the same teacher,
random policy, checkpoint, opponent, and gates.  No learning is authorized.  A prospective pass
accepts the regenerative-planter abstraction and advances to isolated crop destruction; it does
not authorize deployment or Arena submission.

## Reproducibility anchors

- D3 protocol:
  `16efc9b0a064cf7e920503a99f9886c1e07b5168a6e54b3fbf72545d4c26c7e1`;
- teacher:
  `6fea50e8053c8d15b996b9cf88f03ba67a95d757d65f5f2a881e4271fccfc2f9`;
- random legal:
  `424d0e72f3b355c9b1abece5f0a5d9f02cbf224c71b59cacde17350a145eb039`;
- fixed actor:
  `e3f1786ed6fba79893e1f176b1876e89ee1be63d178730c728aff8d256a3f243`.
