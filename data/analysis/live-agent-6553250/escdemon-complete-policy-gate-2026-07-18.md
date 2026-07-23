# Escdemon complete-policy gate — Phase 9, 2026-07-18

## Verdict

**Recover the first-affordability trigger and the pure wood-worker role, but reject an Escdemon
candidate. Park exact imitation and move to Norxondor's multi-worker architecture.**

Escdemon is coherent at the objective level, but its small 26-game opening sample does not support
held-game selection of the eventual worker stats, and its exact tree layer does not survive the
complete autoregressive gate. No live source, submit default, sealed map block, or arena state was
changed.

## TRAIN decomposition

Escdemon trains exactly one harvest-0 worker in all 26 games. Given the eventual chosen spec, the
trigger is simple and stable: train on its first affordable turn. This is exact in 25/26 games,
with mean absolute timing error 0.308 turns; the sole exception waits eight turns. The worker is
the maximum-affordable movement/carry/chop vector at the actual train turn in 26/26 games.

The deployable problem is selecting that eventual spec from the opening. A fixed grid of 2,750
Yamo opening policies collapses to 334 distinct prediction signatures:

| Spec selector | Exact | Mean talent L1 | Maximum L1 |
|---|---:|---:|---:|
| Existing `TUNED_CARRY` plan | 14/26 | 0.538 | 2 |
| Best in-sample grid policy | 15/26 | 0.500 | 2 |
| Nested leave-one-game-out selection | **8/26** | **0.846** | 2 |
| Nested five-fold selection | **9/26** | **0.769** | 2 |

The one-game in-sample improvement is unstable and reverses badly when policy selection excludes
the evaluated game. Therefore retain the resident planner as a descriptive baseline, not as an
Escdemon clone, and do not tune another opening formula on these 26 games.

## Assignment and target persistence

The exact command dataset has 11,009 unit-turns. Assignment is unusually clean: the trained
worker's 5,341 turns contain only MOVE, CHOP, DROP, and WAIT, with zero non-wood cargo turns. The
starter owns all harvesting, mining, seed picking, and planting. This confirms a two-role
architecture: flexible starter plus pure wood converter.

Of 6,328 MOVE commands, 4,761 (75.24%) repeat the unit's previous target. Prior commitments plus
singleton semantic targets recover 5,415 moves (85.57%) under teacher forcing. The remaining 913
new targets are sharply localized:

- 633 tree choices (`MOVE_TREE` or `MOVE_TREE_RIPE`);
- 270 open-cell/collision waypoints;
- 10 iron targets.

With five-fold held-game objective prediction and only its own recovered commitments, the
autoregressive renderer reaches 63.95% exact unit commands, 43.13% exact MOVE targets, and 41.97%
all-worker exact turns. The exact-layer gate fails.

## Conditional tree ranker and complete integration

A deterministic 20-epoch averaged ranking perceptron was trained only on non-repeated,
non-singleton tree choices. Candidate features use geometry, travel/chop/return cycle, wood rate,
tree state/type, water, territory, opponent/partner distance, worker ordinal, and phase. Every
prediction excludes the evaluated game's fold.

| Tree selector | Exact accuracy | Worst held fold |
|---|---:|---:|
| Nearest unit | 42.18% | — |
| Minimum conversion cycle | 45.97% | — |
| Held-game ranker | **56.08%** | **50.62%** |

The conditional component clears its isolated gate. Once integrated into the autoregressive
policy skeleton, however, objective errors and wrong new commitments compound:

| Renderer | Unit-command exact | MOVE-target exact | All-worker turn exact |
|---|---:|---:|---:|
| Commitment + singleton baseline | 63.95% | 43.13% | 41.97% |
| Plus held-game tree ranker | **69.12%** | **52.12%** | **48.38%** |

The integrated gate required 55% MOVE accuracy, a 10-point MOVE gain, and at least 50% in every
fold. It achieves only a 9.0-point gain and the worst fold is 46.92%, so it fails despite passing
the unit and whole-turn global thresholds. This is exactly why component and complete gates must
remain separate.

## Existing-policy shortcut audit

Twelve persistent local controllers were run teacher-forced over all 5,668 official decision
states. SilverBoss is the closest raw skeleton, but only at 61.16% objective accuracy, 50.66%
unit-command agreement, and 52.23% MOVE-target agreement. It matches zero of the 26 actual TRAIN
specs on their turns and emits TRAIN on 276 other turns. The resident family matches 14 actual
TRAIN specs but emits 107 false-positive training turns under the divergent trajectory. No local
policy passes the shortcut gate; Gold, Yamo, Moisan, or Silver cannot substitute for the learned
complete controller.

## Decision and next direction

Close the Escdemon exact-imitation branch unless new independent games become available. Keep two
recovered ideas as architectural evidence, not code changes:

1. choose a worker objective first, then train on first affordability;
2. separate a flexible starter from a persistent pure wood converter.

The next coherent target is rank-4 Norxondor. It passed the within-agent objective gate and uses a
genuinely worker-rich controller: 0–4 successful trains, mean 2.07, median first train turn 6.
Analyze its workforce-count/timing/role controller before exact commands. This directly tests the
strong-bot worker architecture that isolated first-worker rollouts could not represent.

## Evidence

- `escdemon-training-trigger-study-2026-07-18.json`
- `escdemon-target-assignment-study-2026-07-18.json`
- `escdemon-tree-target-study-2026-07-18.json`
- `escdemon-policy-skeleton-study-2026-07-18.json`
- `escdemon-local-policy-command-audit-2026-07-18.json`
- `cgauto/escdemon_training_trigger_study.py`
- `cgauto/escdemon_target_assignment_study.py`
- `cgauto/escdemon_tree_target_study.py`
- `cgauto/escdemon_policy_skeleton_study.py`
- `cgauto/agent_trajectory_command_audit.py`
