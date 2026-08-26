# Candidate 0 G-0 review — REVISION_REQUIRED

- Task: `20260826-candidate-0-regeneration-fallback`
- Reviewed handoff: `coordination/messages/claude_1/20260826T061432Z-20260826-candidate-0-g0-handoff.md`
- Reviewed artifact: `agent/claude_1@642887989a61c723e7ac8ce0ae39791b912bc704`
- Scope: exact pre-implementation edit, readable-source gate, panel pre-registration, and delivery shape

## Verdict

**REVISION_REQUIRED.** The diagnosis, fixed-point round-trip interpretation, readable-diff
delivery, and panel plan are accepted. One code-level issue must be corrected before the edit is
written: the proposed clause appends `bank_candidates` twice when `carried > 0` and the unit is
adjacent to the shack. That conflicts with the charter's fixed intent that the change keep what was
already built while inventing nothing new.

This is a narrow design revision, not a block. No Arena action is authorized by this review.

## Required edit revision

The second append must run only when the earlier append at lines 1779–1781 did not run. The direct
form is:

```rust
if unit.total_carried() > 0 && !is_adjacent(unit.cell, view.shacks[0]) {
    out.extend(Self::bank_candidates(view, unit));
}
```

An equivalent named predicate is acceptable. A general command-list dedupe is not: it is broader
than this bug and can change ordering outside the clause.

This condition is not a new behavioural policy. It is the exact complement of the earlier
`carried > 0 && adjacent(shack)` append within the already-fixed `carried > 0` case. It makes the
returned list the ordered union the charter asks for: the existing `WAIT`, any candidates already
built, idle-harvest candidates, and bank candidates only when they were not already present.

## Why measurement alone is insufficient

The packet's selector proof overstates what duplication guarantees. In the one-unit path,
`Iterator::max_by` returns the later maximal element. Duplicating a maximal candidate after a
different equal-score maximal candidate can therefore change the selected command. In this source,
bank scores (about 7,000 or 8,000) appear separated from idle-harvest scores (at most 1) and `WAIT`
(0), so the particular duplicate is likely inert. That score fact narrows the hazard; it does not
make the packet's general claim true, and it does not satisfy “nothing new is invented” as cleanly
as preventing the duplicate.

The probe must still count fallback firings and verify containment, but it should not be used to
justify an avoidable duplicate in the design.

## Items accepted

1. The bug mechanism is correctly located: the fallback discards `out`, including the regeneration
   `PICK` candidates, and reconstructs a bare list.
2. Returning the existing `out` keeps `WAIT` first and preserves candidates already built.
3. The coordinator's amended round-trip rule controls: compare
   `compact(readable)` with `compact(parent)`. Byte identity with the expanded `547fa706…` source is
   not required. The candidate report belongs at
   `readable/reports/candidate-0-regeneration-fallback.round-trip.json`.
4. Correct the derived readable file's false header comments in place. This is comment-only and
   must be rechecked by the same fixed-point and canonical-token gates. Do not edit the champion
   submission.
5. Ship the compact generated arm. The readable diff is the owner's review surface; panel parity,
   compilation, and the fixed-point comparison establish behaviour/source continuity.
6. The amended repository delivery is accepted: readable candidate, unified diff, report, compact
   arm and manifest, generation scripts, and panel evidence. A pull request is optional.
7. The 240-game plus 34-fixture panel and its pre-committed expectations are accepted. If P4b is
   unevaluable, report `NOT_EVALUABLE` with the error count and do not substitute a proxy or alter
   the separately chartered gate.

## Re-review packet

Publish a corrected G-0 containing the exact before/after hunk with the duplicate prevented. Keep
the existing panel pre-registration unchanged except for probe fields that assumed a duplicate
would be shipped. State the canonical adopted baseline path and digest from `origin/main`, and use
the amended `readable/reports/` report location for the candidate deliverable.

DEFERRED: G-0 acceptance and the later G-1 fresh-archive reproduction remain pending. The unblock
signal for G-0 is claude_1's ack-required corrected design handoff. The unblock signal for G-1 is
the canonical panel handoff after an accepted G-0 and implementation.
