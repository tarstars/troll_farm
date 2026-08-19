# D2 Phase-1 viewer implementation review — 2026-08-15

Task: `20260815-oscillation-deep-dive`  
Reviewer: `codex_1`  
Subject artifact: `423b87a1be7d06c6c8fe4f29b35650fb5a896a3a`

## Verdict

**REVISION_REQUIRED.** The build is deterministic, offline/self-contained, loader-verified, and
its fact-vs-inference styling has meaningful negative controls. It does not yet implement several
owner-approved Phase-1 requirements, and one displayed data schema is wrong.

## Reproduced strengths

- `--self-test`: 11/11 pass; each declared guard is observed rejecting.
- Fresh generation produces exactly 35 files (34 situations + index) and is byte-identical to
  the committed output.
- Frozen library, `rust/`, and `cgauto/` have no artifact-commit diff; sacred SHA remains exact.
- Pages contain no external asset dependency; keyboard/button controls and entry-snapshot labels
  are present.
- Map alphabet and single-cell stall cases generate without error.

The author's browser caveat is correct: structure is tested, pixels are not. Human visual
inspection remains an acceptance item after the code blockers below are fixed.

## Blocking findings

### V1 — six-slot item labels are wrong

`CARRY_SLOTS` is `PLUM, APPLE, LEMON, BANANA, ORANGE, WOOD`. The authoritative parser order is
`PLUM, LEMON, APPLE, BANANA, IRON, WOOD` (`trace_detectors.py:96–97`). The viewer therefore swaps
LEMON/APPLE and labels IRON as nonexistent ORANGE in both inventory headings and the implied unit
carry display. This is exactly the kind of plausible-looking wrong state the viewer must prevent.

Add a negative control that derives or asserts the authoritative order; a self-test sourced only
from the same local constant would repeat the error.

### V2 — required adjudication evidence is absent

The approved scope requires the side panel to show `classification` mechanism/blocker analysis,
`mechanism_evidence`, `unresolved`, and provenance so the session does not need raw JSON. None of
those fields is rendered. The stuck troll and blocking troll also are not specially marked, and
opponent unit ids are absent from the board. These are not polish: L1–L4 adjudication needs the
case identity and uncertainty visible beside the board.

### V3 — the first board frame is not the exact entry state

For OSC-001, `world_state_at_entry.turn == window.turn_start == 6`. `derived_positions()` seeds
the exact entry positions, immediately applies turn 6's MOVE, then appends frame 6. Thus the page
never shows the exact entry position it claims as its only exact board state; the first displayed
board is already the post-command target assumption.

Represent an explicit entry frame before the first command, or define the board as pre-command
state for each turn and apply each command only when advancing. Keep exact-entry and inferred
post-command states visually and semantically distinct.

### V4 — command target and inferred position are spatially conflated

The approved contract distinguishes the command target (ground truth) from inferred own position.
The page prints the target only as text and draws the dashed inferred unit at that same target.
There is no separate solid target marker on the board. A viewer cannot tell spatially which mark
is the recorded order and which is the assumption. Add an explicit target marker/arrow that is
not a unit-position glyph, while keeping the inferred position hollow/dashed.

## Additional acceptance gaps

- Board-level unit stats/cargo hover or click behavior is absent (a table exists, but the approved
  interaction does not).
- The known-cycle requirement is only structurally asserted; no browser/pixel execution exists.
  After revision, open at least OSC-006 and OSC-033 in a browser before the first owner session.
- Add a generated-output completeness check for all required side-panel fields; current tests can
  pass while the entire adjudication context is omitted.

## Boundary

No viewer, library, source, candidate, TestSession, or Arena artifact was changed by this review.
