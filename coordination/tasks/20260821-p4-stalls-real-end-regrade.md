# 20260821-p4-stalls-real-end-regrade — re-grade the recorded standing-troll stalls against the real end-of-game rule

- Status: **OPEN — coordinator-chartered 2026-08-21 ~09:30Z** (announced to the owner
  beforehand, no objection), from the OSC-032/033 ruling's harness lesson.
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: **codex_1**
  (instrument-first; the adapter is the accepted G-3 one, so the review may be short)
  · Integrator: local_claude_1
- Area: oscillation investigation residue (CLOSED 2026-08-21) — fixture-harness fidelity
- Base: champion `547fa706…`, diagnostic copy only; frozen library
  `claude_1/banana-restoration-r2/oscillation-library-98628e98/library/`. No resident,
  dev-copy or Arena touch.
- Created UTC: 2026-08-21T09:30:00Z

## THE QUESTION

The fixture harness plays a fixed 200-turn horizon and ignores the referee's end
condition (`Board.hasStalled`; frozen port `sim.engine.has_stalled`). OSC-032/033 turned
out to be entirely past the real game's end. **Which other recorded windows extend past
the turn the real game would have ended — and by how much?**

## Deliverables (measurement only)

1. For **every one of the 34** frozen cases, on the champion re-run: the turn the real
   referee would have ended the game (both the full rule and the opponent-independent
   grace-only bound), or "never (reaches the horizon)"; the recorded window; the number
   of window turns that fall past the real end. Reuse the accepted G-3 stall adapter
   (`claude_1/cause1/g3_finding.py`) unchanged — its per-turn identity control stays.
2. A one-table summary naming the cases whose windows are **wholly** or **partly**
   artifact. OSC-031 and OSC-034 (the remaining P4 stalls) reported first; any
   D1 dance window that straddles a real end is reported the same way.
3. A statement of what this does NOT change: rulings already made (the 18, the six, the
   8 FIXED) stand; this card only annotates them with the real-end turn. Any proposal to
   re-open a ruling goes to the owner as a question, not as a finding.
4. Recommendation, as a question to the coordinator: should the grader (`sweep34`) and
   the harness apply `has_stalled` by default from now on.

## Gates

- G-1 codex_1: adapter reuse verified unmodified (digest), or the delta reviewed.
- G-2: per-turn identity control on every fixture (as G-3 did); non-vacuity (the
  predicate seen False on a plant-bearing turn and True on a bare one somewhere in the
  corpus); fail-closed on any fixture the adapter cannot build.
- G-3: the table + the statement of what is not changed.

## Out of scope

No fix, no candidate, no re-ruling, no class-wide claim beyond the 34, no Arena action.
