# H-STARVE-1 Pool #5 mechanism review — 2026-08-17

Verdict: **REVISION_REQUIRED** (semantic drift plus one omitted gate).

Pinned artifact: `7cc7876edb33e43b38124cacefac7a70ebbba7bf`.

## Accepted evidence

I independently reran `mechanism.py`; its committed JSON is byte-reproducible and the
521-turn reconciliation is exact:

- 325 turns have at least one plant that would pass every clause of the resident's
  `idle_harvest_candidates` filter;
- 28 harvest-eligible turns are rejected by the resident's opponent-occupancy clause;
- 167 OSC-031 turns remain localized only to the chop generator's per-plant filters;
  and
- one OSC-005 full-capacity turn returns before the chop/endgame fall-through.

The principal code-path finding is supported. On the 325 turns, a WAIT-only
`main_candidates` result proves the empty-chop fall-through into
`endgame_candidates`, while the harvest helper is added only under the distinct
top-level `endgame` flag. The helper would have emitted at least one candidate if
called. This is a deliberate condition mismatch/composition gap, not an accidental
failure of either individual clause.

Leaving OSC-031's 167 chop-only turns unresolved is correct; the artifact does not
contain evidence sufficient to choose among its prediction/filter clauses.

## 1. The 28 opponent-occupancy turns are not oracle over-count under the reviewed semantics

Pool #3's accepted definition is stage attribution against the accepted eligible-action
oracle. That oracle deliberately mirrors the resident's occupancy-blind navigation and
tests capability, plant state, reachable geometry, and sinks; opponent occupancy was
not a clause. Therefore these 28 turns remain valid `NO_GOAL_ASSIGNED` turns: usable
work exists under the reviewed oracle, and the generator emits only WAIT because its
own opponent-occupancy gate declines it.

The mechanism note may and should identify that gate. It may not retroactively call the
oracle wrong, say the token is over-counted, remove OSC-009 from the incidence, or call
the behavior “correct.” Those are new semantic/value rulings unsupported by this
artifact. The table remains 521 `NO_GOAL_ASSIGNED` turns in eight situations. Pool #6
may decide whether the opponent-occupancy gate is desirable.

Likewise, replace “wrong scope” with a neutral measured description such as
“deliberate phase-gate composition gap.” Whether its scope is wrong or worth widening
is the owner's Pool #6 decision.

## 2. The mechanism rerun omits exact coverage validation

`mechanism.py` calls parity and `check_final_stage` but not `check_coverage`, although it
re-parses a fresh diagnostic run. Add `C.check_coverage(sit, err)` before consuming each
situation, matching the accepted Pool #3 pipeline. The prior all-34 run makes a current
failure unlikely, but a downstream evidence artifact must not silently weaken its input
gate.

Revise the note/JSON interpretation and add the coverage call; no new measurement or
owner decision is required. Pool #6 remains gated.

No cure code, resident mutation, Arena action, or spec implementation is authorized.
