# D11 recipe-7 funding fallback — development result (2026-07-20)

## Decision

**Close fixed-deadline fallback.  No deadline passes the frozen rule.  Retain recipe 6 as the
accepted integration fixture and move the PPO actor into a layered resident/PPO experiment.**

The deadline-60 policy is an informative research control, not a prospective candidate.  No
holdout, resident, submission, or Arena state changes.

## Complete execution

All 768 planned games completed on reused seeds 0--7, both seats, the six frozen opponents, and
deadlines 40, 60, 80, 100, 120, 150, 180, and 210.  V6 recorded the final worker spec, so a
successful recipe-7 build and an applied recipe-6 fallback are directly distinguishable.

| Deadline | Mean margin | Delta vs fixed 6 | Delta vs fixed 7 | Training completion | Eligible |
|---:|---:|---:|---:|---:|---|
| 40 | -27.09 | +2.05 | -14.19 | 95/96 | no |
| 60 | **-4.61** | **+24.53** | **+8.29** | 95/96 | no |
| 80 | -6.14 | +23.01 | +6.77 | 95/96 | no |
| 100 | -9.81 | +19.33 | +3.09 | 94/96 | no |
| 120 | -11.00 | +18.15 | +1.91 | 93/96 | no |
| 150 | -12.77 | +16.38 | +0.14 | 93/96 | no |
| 180 | -13.23 | +15.92 | -0.32 | 92/96 | no |
| 210 | -12.60 | +16.54 | +0.30 | 92/96 | no |

Deadline 60 is globally strong and nonnegative by opponent: its worst opponent mean delta from
fixed recipe 6 is +12.63.  It switches 28/96 games to recipe 6, retains recipe 7 in 67, and
leaves one game untrained.  These gains prove that dynamic target switching is behaviorally
usable by the actor; they do not satisfy the safety rule.

## Why no deadline passes

Every deadline fails 96/96 training completion.  The same seed-4/seat-0 resident cell remains a
deadlock even after a turn-40 switch; by then the recipe-7 opening has changed the bank and path
enough that the recipe-6 worker never becomes affordable.  Later deadlines additionally retain
some seed-0/seat-1 deadlocks.

More importantly, every deadline is negative relative to choosing recipe 6 from turn one in all
five known fixed-recipe-7 failure cells.  Deadline 60 improves those cells by +36.0 versus the
failed fixed recipe 7, but remains -31.4 versus fixed recipe 6.  In contrast, it gains +27.60
over recipe 6 in the 91 cells where recipe 7 had trained.  The mechanism is therefore clear:

> target switching can rescue part of a bad trajectory, but it cannot refund the opening turns
> spent pursuing an unfundable worker.

The frozen rule required positive recipe-6 delta in both partitions, so no deadline is eligible.
The rule is not relaxed after seeing the attractive aggregate deadline-60 result.

## Higher-level implication

Recipe selection is no longer the main bottleneck.  Even fixed recipe 7, the best actor-only
policy, averaged -68.31 against the current resident continuation and won only 4/16 head-to-head
development games.  Improving its recipe can move local margin materially, but it does not turn
the narrow PPO curriculum into a complete Legend strategy.

The profitable next abstraction is composition:

- retain the resident's macro opening, funding, and broad task allocation;
- test PPO control only for the worker or phase matching its trained renewable-crop/pressure
  competence;
- decompose gains between forced worker spec, resident funding, and PPO tactical actions.

This avoids asking a specialist actor to replace the entire resident and directly tests whether
the learned behavior adds value as a layer.

## Evidence

- protocol: `d11-recipe-fallback-development-protocol-2026-07-20.md`;
- rows: `d11-recipe-fallback-development-seeds0-7.tsv`, SHA-256
  `da3615953fc7d5063d92485e448242e9feccbdad06f330d282c51a89d791cfe7`;
- analysis: `d11-recipe-fallback-development-2026-07-20.json`, SHA-256
  `e5d3079209b80e7054f342e707a9d37e83564d64724bb31d0493b7f372059539`.

