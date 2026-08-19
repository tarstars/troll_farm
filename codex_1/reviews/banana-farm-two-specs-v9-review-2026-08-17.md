# Banana-farm two-spec v9 review — 2026-08-17

Verdict: **REVISION_REQUIRED**.

Pinned artifact: `d83a66f2828585cd9869cb4398dd6c8a70367b3f`.

The fifth owner ruling is a valid disposition of the suppression-corner risk: prevention
may be deferred if occurrences and consequences are observable and gated. The written
C1/C2/C3 mechanism correctly distinguishes the main/endgame PICK entries and recognizes
both dance and all-WAIT outcomes. Three specification gaps remain.

## 1. Independent census-identity blocker remains

V9 does not change the v8 census rule. Our PLANT suppression does not prevent the enemy
from planting after `C_i`. A newly planted enemy tree can still be chopped to satisfy
the generic completion quota while a census-time tree remains; recount equal to `C_i`
then falsely fires futility. This is independent of suppression-corner prevention.

Freeze the current round's target generation identities at census time and count only
confirmed completions of those targets. New generations enter `C_{i+1}` but cannot pay
the old quota. Add the enemy-post-census must-not-fire arm to GK.

## 2. The empirical backstop omits the park outcome

The spec says a manufactured dance fails the zero-de-novo D1 gate, but its own preceding
sentence also identifies an all-WAIT-at-0 outcome. That outcome is P4 liveness, not D1.
Make the mandatory panel gate explicitly zero de-novo **D1 and P4**, with both detector
arms run and reported. Otherwise one of the two predicted regressions passes the stated
backstop.

## 3. Five future commands are not a persistence record

Logging only the next five emitted commands cannot adjudicate whether a regeneration
commitment remains stuck beyond that horizon. A WAIT-only or adjacent-cell loop may
outlive five turns, and the schema does not name commitment state/target or routing
branch.

For every suppression event, record at least situation/run identity, turn, unit and
cell, phase, routing branch, commitment kind/target before and after suppression,
pre/post-suppression candidate summaries, final selected command, and then commands plus
commitment state until the commitment clears, DENY exits, the unit dies, or the game
ends. A bounded preview may remain for convenience, but it cannot be the evidence used
to declare the corner harmless.

These changes preserve the owner's log-and-defer ruling while making its backstop capable
of observing both named failure modes.

