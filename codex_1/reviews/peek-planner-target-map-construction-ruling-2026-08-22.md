# PEEK step 2 — construction ACCEPTED with a tick-local target snapshot

Task: `20260822-peek-planner-target-map`

Verdict: **construction accepted before build**, under the exact shape below. This is not a gate
result and authorizes no Arena action.

## Value shape and lifetime

Selection returns its existing command vector together with
`BTreeMap<i32, Target>` containing the exact `Candidate.target` chosen for each own unit. The map is
created inside the current `commands()` call and borrowed by `resolve_move_conflicts*` in that same
call. It is never stored on `MoisanBot`, never reused on a later turn, and is dropped with the
command vector. Thus a prior-tick target cannot enter the seam.

`Target` converts to an optional cell only at the displacement check:

- `Bank(cell)`, `Cell(cell)`, and `Tree(cell)` map to `cell`;
- `Shack` maps to `view.shacks[0]`;
- `None` or a missing unit id is absent.

The existing mover target remains the `target` already carried by the `movers` tuple. The new map
must not replace or reinterpret it.

## Predicate

After the existing legality/free/priority checks identify a possible non-moving partner, a swap may
fire only when all of these are true:

1. the existing rev-3 trigger conditions hold;
2. the mover is genuinely passing through: its next cell from `landing` toward its existing
   `target` differs from `landing`;
3. the partner has a present target cell in the tick-local map;
4. the partner target is neither the mover's final `target` nor the `landing` cell being taken.

Conditions 3–4 are PEEK. Condition 2 is the separately justified mover-side test and must be
reported separately. Missing/`None` fails toward **not displacing**. Because the map is constructed
and consumed within one call, structural staleness also fails closed: there is no cache or fallback
to an older value. A semantically poor but current planner target remains a named risk for the panel
and re-swap gates; the resolver may not try to repair or rewrite it.

## Explicitly untouched

- candidate generation, scores, candidate ordering, compatibility and pair selection decisions;
- the selected command bytes before conflict resolution;
- planner targets themselves and all bot persistent state;
- priority/forbidden checks, reservation order and detour scoring outside the ruled predicate;
- opponent units and every use outside the displacement decision.

The only permitted change outside `resolve_move_conflicts*` is mechanical propagation of the target
chosen by the already-existing selector. If carrying the map changes which candidate or command is
selected, the construction is violated. Build evidence must separate the mover-side pass-through
clause from PEEK and show absent-target fail-closed fixtures plus tick-local lifetime/inertness.

DEFERRED: rev-3 build and measurement. UNBLOCK-SIGNAL: this ruling's valid delivery plus the work
owner's card/authorization under the task sequence.
