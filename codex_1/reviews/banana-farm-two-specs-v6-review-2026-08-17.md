# Banana-farm two-spec v6 review — 2026-08-17

Verdict: **REVISION_REQUIRED**.

Pinned artifact: `d153277632f815a2b66ec26b49fb2d55e3bc3837`.

The owner rulings are recorded consistently: B-1 has no floor, `K_futility` is
retired, and the sequence design replaces the turn counter. The completed-work clock
also correctly prevents an in-flight/unreachable round from firing. Sections 3–8 remain
shared between the specs.

## Blocking counterexample: excluded work advances an included census

The census excludes own confirmed focus-species plants, but round progress counts every
confirmed focus-chop completion. Those populations must be identical. As written:

1. `C_i = 1` for one census-eligible target tree.
2. Our endgame conversion creates an own focus-species tree, correctly excluded from
   the live census.
3. We chop that excluded own tree. This is a confirmed focus-chop completion, so the
   cumulative completion count reaches the census value 1 and ends the round.
4. The eligible target tree is untouched, so the recount is still 1. The rule sees
   `C_{i+1} == C_i` and falsely sets `futility_reached`, with no work completed against
   the censused population and no enemy replacement.

This recreates exactly the conversion-blip false trigger the exclusion claims to close.
Define round progress to count only completions of census-eligible generations (or use
an equivalent rule that proves excluded trees cannot advance the round), and add this
four-step case as a must-not-fire arm in GE/GK.

## Focus-plant generation contract

“Section 7-style reconciliation” is not yet an operational contract for this built
tracker: §7's detailed tracked-crop contract is banana-specific and belongs to a named
future abort variant, while the sequence rule must track lemon/plum generations during
DENY. Specify the focus-plant lifecycle used by both census exclusion and eligible
completion: how our focus `PLANT` creation is confirmed, when its generation identity
is removed/replaced, and how ambiguity fails closed. The census and completion counter
must consult the same identity so the counterexample cannot arise through drift.

No objection is raised to the owner's sequence comparison itself once its census and
work populations are made coherent.

