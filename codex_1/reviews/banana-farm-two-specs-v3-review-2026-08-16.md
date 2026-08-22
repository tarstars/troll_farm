# Banana-farm Spec A/B v3 re-review — 2026-08-16

Verdict: **REVISION_REQUIRED**, limited to two correctness claims.  The owner-selected
state-machine shape and score-delta sensor are not being reopened.

## What is now sound

- The live designs implement the five owner rulings and remove denial-during-FARM from
  the live path.
- The COLLECT/DENY behavioral reconciliation and the COLLECT-time third-troll latch
  divergence are disclosed rather than hidden.
- Sections 3–8 are shared text and section 9 isolates the doorway distinction.
- M-1 arithmetic is correct as written: at n=5,
  `SE = 1.501*sqrt(2/5) = 0.9493`, so the 95% decision bar is 1.8606 (about 1.9).

## Blocking corrections

1. **The score-delta bias is not one-way safe.**  Section 7 says both distortions push
   toward aborting too often.  Total score also includes wood and all other banked
   stock (wood is worth four points while banana is worth one).  Our trained troll's
   wood production can therefore mask enemy banana gain or theft and make the abort
   fire too late or never.  Keep the ruled sensor, but characterize false positives
   *and false negatives*, and make measurement report both.  The current “safe
   direction” assurance is false.
2. **K_futility=10 is not justified by the stated bound.**  Ten non-decreasing turns do
   span the base regrowth cooldown, but the spec has not bounded travel plus chopping
   time below ten.  It therefore cannot claim the window spans “more than one in-flight
   chop” or proves the enemy is sustaining the species at our chopping rate.  Retain
   K=10 if the owner freezes it, but label it a heuristic and add a constructed case
   where a legitimate long in-flight denial chop must not be mistaken for futility (or
   provide the missing bound).

After those textual/test-gate corrections, the specification is ready for owner
approval; no new design decision is required from this review.

