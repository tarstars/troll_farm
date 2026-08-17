# Banana-farm two-spec v8 review — 2026-08-17

Verdict: **REVISION_REQUIRED**.

Pinned artifact: `1958a0bca995c3d03ab1ab9476c767189e0be65b`.

The fourth owner ruling is recorded consistently, and deleting the own-plant exclusion
machinery is valid for the specific conversion-blip hazard: the machine can no longer
create a new focus tree during DENY. It does not, however, close the census identity
defect raised in the v7 review, because the opponent can still plant.

## Blocker 1: enemy post-census trees still pay a frozen census quota

The v8 round again counts every confirmed focus-chop completion. The counterexample is
unchanged except that the new tree is enemy-planted:

1. `C_i = 1`, containing one census-time target tree that remains standing.
2. The enemy plants a new accessible focus tree during the round.
3. We chop that new tree; the generic completion counter reaches 1 and ends the round.
4. The census-time tree remains, so recount `C_{i+1} = 1` and futility fires falsely.

Our PLANT suppression has no bearing on enemy planting. Freeze the round target set to
the generation identities counted in `C_i`; only their confirmed completions advance
the current round. New generations affect the next census but cannot pay the old work
quota. Add this exact must-not-fire arm to GK.

## Blocker 2: suppression can turn a commitment route into starvation

The readable resident routes a unit with a regeneration commitment through the endgame
generator. A committed fruit carrier whose decisive candidate is PLANT can retain the
commitment while v8 removes that candidate throughout DENY, potentially leaving a
MOVE/WAIT-only route indefinitely. That would introduce the precise parked-worker
failure currently under H-STARVE audit.

Specify the DENY-entry and DENY-time disposition of existing/new regeneration
commitments: prevent or clear commitments whose terminal action is forbidden, or prove
a non-PLANT fallback gives the unit usable work and terminates the commitment. Extend
the suppression twins with a committed fruit carrier and require both:

- no PLANT while DENY holds; and
- no persistent WAIT-only commitment route caused by suppression.

The owner's no-planting ruling remains untouched; these corrections make its round
accounting and liveness consequences explicit.

