# Curriculum Level 2 PPO discovery result — 2026-07-19

## Verdict

**Pass.**  The frozen seed-61 teacher-anchored PPO run clears every outcome and action-quality
gate on exactly seeds 2,005,000--2,006,999.  This authorizes the one independently seeded Level-2
confirmation specified by the protocol.  It does not alter the resident or authorize an Arena
submission.

## Frozen final gate

| Metric | Required | Observed | Result |
|---|---:|---:|---|
| Overall success | >=90% | 98.15% | pass |
| Nonzero-total-deficit success | >=85% | 97.98% | pass |
| Recipe-family floor | >=80% | 95.58% | pass |
| Height floor | >=80% | 97.40% | pass |
| Advantage over random legal | >=40 pp | +57.90 pp | pass |
| Paired teacher median delay | <=20 turns | 0 turns | pass |
| `MOVE current` waits | <=40,000 | 2,377 | pass |
| Needed productive choice rate | >=60% | 93.87% | pass |

The policy solves 1,963/2,000 maps.  Family success in catalog order is 98.72%, 100%, 100%,
98.14%, 99.60%, 97.77%, 95.58%, and 95.69%.  Every height bucket is at least 97.40%.  The exact
action audit finds 4,402 states where a legal HARVEST or MINE directly satisfies a remaining
worker-cost deficit; the policy chooses a productive action in 4,132 of them.

## Analysis at three abstraction levels

At the action level, the online teacher auxiliary prevents the deterministic MOVE collapse seen
in pure PPO.  It preserves useful HARVEST/MINE probability throughout optimization while the value
head learns a strong closed-loop signal (final explained variance 0.633).

At the plan level, one unchanged 34,926-parameter policy handles eight distinct four-resource
recipes.  The harder standard and hybrid choppers remain the error floor, which is consistent with
their coupled APPLE/IRON deficits rather than with loss of the accepted Level-1 behavior: the
Level-1 anchor family is 99.60% successful.

At the architecture level, this result answers the narrow question positively: a compact spatial
actor can condition resource acquisition on a requested worker specification and execute the plan
closed-loop.  It does not yet choose the recipe, control the trained worker, operate a renewable
economy, or react to an opponent.  Those are the transfer boundary, so embedding this checkpoint
in the live bot would be premature.

Training completed 2,000,000 transitions in 2,643.15 wall seconds and 35,854.54 CPU-seconds,
equivalent to 67.83% aggregate capacity on the 20-core host.  Final late-rollout success is 99.8%,
teacher-action accuracy 94.0%, entropy 0.199, and approximate KL 0.000110.

## Frozen artifacts

- final checkpoint: `2321ad43aff2a175ae50f693940f9bf2ddd3d5506f1d1bfc8ccf41696a0aa270`;
- exact evaluation: `524f88836daeb1bcb0f9f4ac60bc564450d888023d4c8213cac54bd1536f846c`;
- exact action audit: `116d1c408588d8a378778be466eef86df36b431876396c97f0158aaae72033cf`;
- training summary: `f2f78912393924a8f06fcf86956d19187352adde0d46007370830fb123691948`;
- teacher control: `a442a23b5e6603d89097923980aa800cb4af85582d2278fa846ceac0b604d605`;
- random-legal control: `b5e18106f5fed9fd807d1eb66b0269fd9e6705beff14f3737735fff2759e36a8`.

## Next move

Run exactly one confirmation with model seed 67, disjoint teacher/PPO streams, and a new exact
2,000-seed bank frozen before label generation.  Accept Level 2 only if that run clears the lower
confirmation floors and the identical action-collapse limits.
