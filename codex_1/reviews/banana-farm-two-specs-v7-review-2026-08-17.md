# Banana-farm two-spec v7 review — 2026-08-17

Verdict: **REVISION_REQUIRED**.

Pinned artifact: `96b5828da5f080f890093d6e61ba6fc2258e26fa`.

V7 closes the exact excluded-conversion-tree counterexample and supplies a built-now
generation contract for own planted focus trees. One population-identity ambiguity
still permits the same class of false round completion.

## Blocking counterexample: post-census tree advances a snapshot census

The round says a completion is eligible iff its tree “was part of the census
population,” but operationally reduces that to “NOT standing on an excluded
own-planted cell.” Those are not equivalent: a non-excluded tree may appear after the
census.

1. `C_i = 1`, consisting of one census-time target tree that remains standing.
2. After the census, the enemy plants a new accessible focus-species tree.
3. We chop that new tree. It is not on an excluded-own cell, so the current text counts
   it as a census-eligible completion and reaches the round quota 1.
4. The original census tree still stands; recount `C_{i+1} = 1`, so the rule falsely
   fires futility even though we did not chop the tree counted in `C_i`.

The same mismatch can arise when an own-tree exclusion is conservatively lost during a
round: the generation re-enters the live population but was not in the frozen census
denominator.

Freeze the round's target population as the generation identities counted in `C_i`, and
advance progress only when one of those census-time generations receives a confirmed
completion. New or newly re-entered generations affect `C_{i+1}` but cannot pay the
current round's work quota. Specify fail-closed lifecycle handling for the target set,
and add the four-step enemy-new-tree case as another GK must-not-fire arm.

That rule matches the owner's sequence literally: count the trees, chop *them*, then
recount. No objection remains to the own-exclusion contract itself.

