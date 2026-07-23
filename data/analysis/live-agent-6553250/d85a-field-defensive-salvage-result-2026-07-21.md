# D85a current-field one-turn defensive salvage result (2026-07-21)

## Verdict

**Reject and close on-crop one-turn defensive salvage.**  The current resident already issues a
joint `CHOP` at every observed opportunity where the opponent's visible chop is lethal.  Replacing
its action with `HARVEST` when ripe fruit is present changes only 18/196 validation triggers and
gains just +0.051 immediate liquid margin per trigger, below the frozen +0.25 floor.  Four of the
18 changes regress, own liquid value is slightly negative, and one opponent-account mean is
negative.

This result creates no candidate and authorizes no sealed-replay read, TestSession, submission, or
resident replacement.

## Replay and causal integrity

- The open D61p snapshot supplies 293 resident-owned crop-contact triggers from 165 resident games:
  97 discovery and 196 validation.
- Independent extraction with 20 workers and one worker produces byte-identical 1,172-row matrices
  and manifests.
- All 293 four-arm sets are complete.  There are zero arm-accounting, parity, command, or
  unavailable-arm failures.
- Control replay is materially exact for all triggers: 274 transitions are fully exact and 19
  differ only in movement RNG.  Target-local state is exact in 293/293.
- The public replay's already-present opponent command is held fixed.  Confirmation products are
  not read.

All frozen integrity gates pass.

## Support and observability

The visible attacker-on-crop condition is a good attack detector.  It confirms 84/97 discovery
triggers (86.60%) and 181/196 validation triggers (92.35%), across both seats and 15 opponent
accounts in each partition.  The frozen 85% validation precision gate passes.

The semantic support audit is more revealing:

| Response | Available triggers | Changed interventions | Mean available liquid-margin gain |
|---|---:|---:|---:|
| harvest ripe fruit first | 72 | 35 | +0.097 |
| joint chop if visible opponent chop is lethal | 221 | **0** | +0.000 |

Every joint-chop opportunity is unchanged because the resident already chooses `CHOP`.  The
missing defense is therefore not at this command layer.

## Frozen salvage result

| Validation measure | Result | Gate | Pass |
|---|---:|---:|:---:|
| Changed interventions | 18/196 (9.18%) | at least 8 | yes |
| Mean liquid-margin gain, complete validation | **+0.051** | at least +0.25 | no |
| Strict improvements among changes | 14/18 (77.78%) | at least 50% | yes |
| Regressions among changes | **4/18 (22.22%)** | at most 5% | no |
| Mean own liquid delta | **-0.010** | nonnegative | no |
| Mean opponent liquid delta | -0.061 | nonpositive | yes |
| Nonnegative opponent accounts / worst mean | 14/15 / **-0.0526** | at least 4 / nonnegative | no |
| Treatment-only crop deaths | 0 | 0 | yes |

Even the hindsight immediate oracle gains only +0.112 per validation trigger and selects control
182 times versus harvest 14 times.  There is not enough one-turn value for a deployable rule.

## Why harvest regresses

Across the complete corpus, the 35 changed harvest substitutions have liquid-margin deltas
`26 x +1`, `7 x -3`, `1 x -7`, and `1 x +9`.  The four validation regressions are all APPLE crops
with one fruit and one or two health.  The resident's actual `CHOP` and the treatment's `HARVEST`
both leave the crop dead after the simultaneous commands; harvesting merely trades away one wood
unit worth four points for one fruit worth one point, producing the common -3 result.

There are no treatment-only premature deaths.  The failure is opportunity cost, not an unsafe
simulator edge case.  False-positive attack classification is not the cause either: both changed
validation false positives gain +1, while the regressions occur among confirmed attacks.

## What the result closes

D78's imminent-attack signal is observable, but there is no missing high-confidence current-crop
command to install.  The resident already coordinates lethal chopping; unconditional ripe-fruit
salvage is too sparse and too costly.  Do not tune attack precision, fruit priority, crop health,
or the lethal threshold on these consumed rows, and do not reopen a terminal continuation model
from D82--D84.

The next experiment must move to a different abstraction: a complete economic transition or
target-allocation mechanism, not another one-turn defense at the attacked crop.

## Evidence

- protocol SHA-256: `87c4b0fecba10ba5b8aa1d2c870376a31b6762bdbf494e5c23c0ca59c746c655`;
- analyzer SHA-256: `980c40fa3ad8e58349dd12e538b6a31721e0c04c71e0f6be48fa56d88113287b`;
- repeat row SHA-256: `2964b523202e6e808b58f3f5cb1e80341e040a98cbd335671870b2a20c56696c`;
- repeat manifest SHA-256: `9945a3464119207456013b0769d96d0c9c383969684ffa570c777dfc6ffd0548`;
- result JSON SHA-256: `0fbee1905fd3869e8e06bf98d39085bc119c1a7f48119c66e50f1e055bef2dac`.
