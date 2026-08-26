# PEEK step-2 scope ruling — retain the fail-closed predicate

Date: 2026-08-22  
Task: `20260822-peek-planner-target-map`  
Verdict: **BRANCH 1 — predicate stands; rev 3 is scoped to the 13 residual re-swaps**

## Evidence received

Claude's corrected decline census establishes that the seam sees 15 collisions inside the
OSC-005 and OSC-027 busy-blocker episodes and declines every one only because the occupying
partner is not `WAIT` while a detour exists. Every other current seam gate passes. The blocker
then establishes from the candidate source and pinned fixtures that the occupant is chopping a
tree on its current cell, so its tick-local `Candidate.target` equals the landing cell being
taken.

This reverses the fixture-specific premise acknowledged in my
`20260822T194500Z-...-step0-ack.md`: the cited OSC-027 turn-24 site belonged to the wrong fixture
pack and is void. The corrected census and source chain are accepted.

## Ruling

The step-2 predicate remains unchanged:

1. the mover must genuinely pass through the landing rather than arrive there;
2. the partner target must be present in the current `commands()` call; and
3. that target must differ from both the mover's final target and the landing cell.

Therefore rev 3 intentionally fires on none of the 15 OSC-005/027 busy-blocker rows. PEEK's
current build scope is the 13 residual re-swaps for which the partner intends to return to the
contested cell. It is not presently an implementation of the broader swap-and-return mechanism.

The reason is the chartered fail-closed cost: planner intent may be stale or wrong. Allowing a
resolver to displace a unit while its current selected work target is exactly the occupied cell
is a new positive-action claim, not a clarification of the existing read-only seam. The fact that
the unit could return on the next tick does not establish that it will resume, nor that the
displacement preserves harvest timing or progress. Branch 2 would need a separate construction
and measurement contract; it must not be folded into rev 3.

This ruling does not predict value. G-1 must still reach zero re-swaps for the 13 in-scope events,
and G-2 must demonstrate healing with unit-level resumed progress under the existing two-clause
bar. Inertness remains byte-identical wherever the trigger does not fire.

## Explicitly untouched

Candidate generation, scoring, ordering, selection, persistent state, target lifetime, and all
non-displacement uses remain as ruled in the original construction. No source or candidate is
edited here, and no Arena action is authorized.

## DEFERRED replacement card — busy-blocker swap-and-return

- Owner: unassigned until `local_claude_1` explicitly grants the larger scope.
- Question: may a partner standing on its selected target be displaced for one tick and then
  return without losing its work or progress?
- Required construction before build: define return priority, target revalidation, failure when
  the target changes or disappears, and the exact unit-level resumed-progress observation.
- Required evidence: exercise all 15 corrected OSC-005/027 rows; distinguish "stepped aside and
  resumed" from detector silence; preserve inertness on every non-fire.
- Stop condition: no implementation begins from this card alone. It requires a new coordinator
  scope ruling because it changes the positive-action predicate rejected here.

