# OSC-031 owner brief review — 2026-08-18

Verdict: **REVISION_REQUIRED** on one factual execution-order statement. The brief is
otherwise neutral, scoped, and faithful to the accepted aggregate.

Pinned artifact: `98f448589648257fe4d6db6de9550d9d42d4f386` on
`agent/claude_1`.

## Required correction

The brief says:

> Every other test in the checklist: zero. Not "rarely"; never reached, because the
> forecast step is earlier in the list and stopped each evaluation before them.

That is false for the tests preceding `PREDICT_TREE_NONE`. In every accepted chain, the
unit capacity/power gate is reached first and passes, then `DEAD_OR_UNREACHABLE` is
reached and passes, then `PREDICT_TREE_NONE` is the terminal rejection. Only the later
predicted-value, chop-outcome, clock, wood, and ACCEPT clauses are not reached.

The table correctly describes **terminal/deciding counts**, where every other clause is
zero. Repair the prose to distinguish:

- earlier clauses: reached and passed, zero terminal decisions;
- `PREDICT_TREE_NONE`: reached and terminal in 315/315 evaluations; and
- later clauses: not reached in this population.

Also make the trust bullet account explicitly for the two other zero-terminal rows:
the unit gate was observed both ways in the accepted fixtures, and ACCEPT was observed
on positive controls. The current phrase “the seven tests that show zero were each dealt
with separately” enumerates only two observed synthetic clauses plus three impossibility
proofs, leaving those two implicit.

No numeric result, attribution, scope boundary, or owner-choice language needs to
change. The accepted evidence remains 315/315 `PREDICT_TREE_NONE` terminals over the
pinned 167-turn population.
