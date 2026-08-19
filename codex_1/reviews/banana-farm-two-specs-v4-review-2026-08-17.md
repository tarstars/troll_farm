# Banana-farm two-spec v4 review — 2026-08-17

Verdict: **REVISION_REQUIRED**.

Pinned artifact: `96f1b400ac53ea7b86738deb2ee5646456d45cba`.

## Accepted corrections

The two v3 blockers are substantively corrected:

- the score-delta abort is now honestly characterized as failing in both directions,
  with wood masking identified and both abort/no-abort outcomes included in reporting;
- `K_futility = 10` is labelled a heuristic, the false in-flight bound is withdrawn,
  and gate GK contains the required long-in-flight negative arm plus a replacement
  positive twin.

Sections 3–8 remain byte-identical between Specs A and B. The completion gate is a
reasonable minimal mechanism for making the negative arm pass, but it is a new design
decision and therefore must be specified and approved as such.

## Remaining blockers

1. The handoff and §4 say the completion gate is flagged for the owner alongside the
   `K_futility` freeze, but neither spec's §14 OWNER-DECISION register contains that
   decision. Add a separate shared item asking the owner to approve/reject the new
   completion-gate mechanism; do not fold it invisibly into approval of the constant.
2. “Confirmed focus-species chop completion” is not operationally defined. Issuing our
   `CHOP` command is not proof that our chop felled the tree, and a tree disappearing
   after simultaneous actions can be ambiguous. Specify the pre/post observation and
   command evidence that sets the boolean, its ordering relative to the count-decrease
   reset, and fail-closed handling for ambiguous removal. Gate GK must exercise that
   exact definition. This is necessary to make the mechanism implementable and to
   support the text's claim that the completion belongs to “ours.”

The score-decomposition reporting requirement is implementable from the visible
per-player inventories and score state; no further correction is requested there.

