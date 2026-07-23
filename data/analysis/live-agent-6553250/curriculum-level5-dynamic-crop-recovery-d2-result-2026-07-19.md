# Curriculum Level 5 dynamic crop-site recovery D2 — result, 2026-07-19

## Verdict

**Reject pre-creation crop-site replanning as the missing complete-opponent mechanism.**  It is
deterministic and eliminates every stale illegal teacher selection, but on the frozen paired bank it
changes only one of 500 outcomes.  The dynamic arm reaches 61.6% versus 61.4% for the unchanged
fixed-site control, far below both the 90% absolute gate and the required +25 percentage-point
paired improvement.  No random, accepted-actor, training, or prospective run is authorized.

## Integrity and paired execution

- Both arms use seeds 1,000--1,499, the same eight recipes, the same complete deterministic
  FastState opponent, the same teacher, and the unchanged 104x11x22 observation / 13x11x22 action
  contract.
- The candidate changes only `planned_crop`: while no player-0 crop has yet been created, an
  occupied planned cell is replaced by the unchanged deterministic free-home-cell selector.
- The fixed control retains all 366 stale illegal selections; the candidate emits zero.
- The opponent is material and has more than one worker in 500/500 episodes in both arms.
- Nine Level-3/4/5 Rust regression tests and 24 Python curriculum tests pass, including byte
  determinism and explicit fixed-versus-recovery behavior.

## Frozen D2 gates

| Measure | Fixed control | Dynamic recovery | D2 requirement | Verdict |
|---|---:|---:|---:|---|
| Overall success | 307/500 = 61.40% | **308/500 = 61.60%** | >=90% and +25 pp | fail |
| Nontrivial success | 63.19% | **63.52%** | >=85% | fail |
| Worst recipe | 41.94% | **41.94%** | >=75% | fail |
| Worst height | 54.40% | **54.40%** | >=80% | fail |
| Crop present at terminal | 61.60% | **61.80%** | >=90% and +25 pp | fail |
| Renewable harvest | 66.60% | **66.80%** | >=85% | fail |
| Illegal teacher selections | 366 | **0** | 0 | pass |
| Material opponent | 100% | **100%** | >=95% | pass |
| Opponent above one worker | 100% | **100%** | >=95% | pass |

The exact paired outcome table is 307 both-success, one dynamic-only success (seed 1,403), and 192
both-fail.  No fixed-only regression occurs.  Recipe assignments and opponent activation are
unchanged.

## Failure decomposition

Of the 192 dynamic failures:

- 191 finish without the tracked crop present;
- 166 never record a renewable harvest;
- 25 record a renewable harvest but finish without the crop; and
- one has both the crop and a renewable harvest but misses another terminal condition.

The complete opponent averages 154.82 score in dynamic failures versus 36.18 in successes.  The 25
harvest-then-no-crop episodes prove that at least part of the terminal crop deficit is crop loss
after a useful loop, not failure to find a legal first planting cell.  The other 166 rows do not by
themselves distinguish pre-harvest destruction from broader resource and timing competition.

## Interpretation at three levels

### Command level

Stale site commands were a real correctness defect: replanning removes all 366 of them.  Their
removal has almost no terminal value, so command legality was a symptom rather than the governing
bottleneck.  The original D0 postmortem over-attributed failure to fixed-site invalidation.

### Interaction level

The full opponent still plants, chops, banks, and grows to multiple workers.  A one-time legal site
cannot keep a fragile renewable asset alive or guarantee a harvest before the opponent's economy
compounds.  Successful episodes end while opponent score is low; long failed episodes let the
opponent reach roughly four times the successful score.

### Curriculum level

The experiment again confirms that the complete baseline bundles too many interaction mechanisms
for a first adversarial step.  The accepted natural forager solved movement and initial-resource
competition, while D2 shows that adding a local recovery rule does not bridge directly to full
planting, chopping, and workforce growth.

## Decision and next eligible question

Close this exact pre-creation replanning rule on seeds 1,000--1,499.  Retain the recovery harness as
a legality regression, not as a training environment or candidate.

The next experiment should isolate **one-worker opponent planting and renewable supply** while
still forbidding opponent chopping and training.  That separates site occupation/self-renewal from
crop destruction and multiworker compounding.  It needs a fresh deterministic opponent policy, an
activation preflight, and a frozen protocol on unused development seeds before execution.

## Reproducibility anchors

- frozen D2 protocol:
  `7137fcbea93b7338c690ad2b0d8a7b90de25bcf5925f343537803f0e7ab08597`;
- fixed-site teacher control:
  `cef8445f9c8d49baecd5f3e66d004684b3b0b38bb7af65ddc18be460103488cc`;
- dynamic-recovery teacher candidate:
  `d0de5bfd4415d9d9d24424ba8e2387aada0e5b1c9d6127bf47d6871d5b4a91c9`.
