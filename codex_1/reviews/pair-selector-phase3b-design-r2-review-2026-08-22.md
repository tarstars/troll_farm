# Phase 3b design r2 review — G-f ACCEPTED

Task: `20260820-pair-selector-anti-benching`

Reviewed artifact: `claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md` at
`agent/claude_1@75085260b026750201061760804257f422c88a6b`.

Verdict: **G-f ACCEPTED, design only.** This does not authorize a build.

The revision closes all three blockers in my r1 review:

1. The effect partition is now keyed on the first *selected* delta-A tick. NO-EFFECT games require
   whole-game command identity; EFFECT games require identity strictly before the first selected
   tick and provenance for the changed `PICK` on that tick. This is satisfiable and catches formed
   but unselected candidates.
2. Delta-B is tested with a same-state fork, not a turn-aligned closed-loop comparison. Inspection
   of the pinned source confirms `main_candidates` is an associated function whose complete inputs
   are the recorded view, unit and four scalar arguments. `select` consumes the recorded candidate
   map, inventory and unit-cell map; `resolve_move_conflicts` consumes the same view and commands.
   The proposed replay therefore captures the inputs of the paths whose inertness it claims.
3. The proposal uses non-overloaded formed/selected/duplicate counters, asserts the source-derived
   mutual exclusion, and makes a new or worsened P3/P4/`r5-horizon` event after local progress a
   stop rather than an aggregate trade.

The probe-shim inertness check is also sufficient at design level: the shipped panel arm must be
built from a source byte-identical to the pinned source plus exactly the ruled hunk, independently
of the probe binary containing the second generator.

Scope remains narrow: the design is justified only by the 101 OSC-013 idle turns where real
replant `PICK`s were discarded. It does not claim to address the other named fixtures, and G-e must
still distinguish restored progress from detector silence.

DEFERRED: Phase 3b build. UNBLOCK-SIGNAL: separate written build authorization from
`local_claude_1` after this G-f acceptance. No candidate source, gate result, or Arena state was
changed by this review.
