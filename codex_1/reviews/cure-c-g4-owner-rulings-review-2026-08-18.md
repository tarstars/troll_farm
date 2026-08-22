# Cure C G4 review under owner rulings — 2026-08-18

Verdict: **GATE_ACCEPTED / G4 GREEN** under the owner policy published at
`coordination/messages/local_claude_1/20260818T041052Z-20260817-cure-c-owner-rulings.md`.
G5 may proceed through the serialized controller path. This verdict supersedes the
qualification conclusion, but not the measurements, in my earlier
`REVISION_REQUIRED` review.

Candidate and handoff identity are unchanged: candidate SHA-256
`ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1`, pinned
handoff `f7c159a9eac6b2f34597b236ec6b856b56064521` on `agent/claude_1`.

## Owner-ruling verification

### OSC-009: explained and verified

The four resident `NO_GOAL_ASSIGNED` attributions are for unit 2 on turns 80--83.
Under Cure C, unit 2 first changes command on turn 1, travels to harvest by turn 9,
and banks on turn 12. By turns 77--83 the candidate world is different: unit 2 is
waiting while unit 0 cycles CHOP/DROP/PICK/PLANT, and the accepted classifier labels
unit 2 `CANNOT_USE_WORK`, not `NO_GOAL_ASSIGNED`. Thus 4 to 0 is a closed-loop
trajectory and attribution change caused by the earlier supplied work, not evidence
that the frozen positive-residual turns survived unchanged.

### OSC-031: explained and verified, with its limit retained

The resident has 189 `NO_GOAL_ASSIGNED` turns for stalled unit 0; the candidate has
89. The reduction does not mean unit 0 began working: its action totals, final cell,
and final cargo are unchanged, and P4 remains. The exact classifier mechanism is:

- at turns 18, 34, 50, 66, 82, and 98, the candidate's changed unit-2 movement makes
  unit 0 classify as `GOAL_SPLIT_WRONG` rather than `NO_GOAL_ASSIGNED`;
- after the peer's resulting world divergence, turns 106 onward are predominantly
  `CANNOT_USE_WORK` for unit 0 rather than `NO_GOAL_ASSIGNED`.

This accounts for all 100 removed no-goal attributions. It is an explained favorable
movement in the registered metric, but not a claim that OSC-031's underlying stall is
cured. The registry remains frozen and its turn-local positive-residual rule remains
invalid for whole-game prediction.

### m061 seat 0: both exception prongs verified

Prong (a) reproduces directly: final score is 75 for Cure C versus 48 for the matched
floor.

The implementer's original byte-identical-tail argument was insufficient by itself:
reviewer instrumentation showed that the diagnostic variant's alternate-tail branch
is never entered on m061. I therefore probed the resident
`endgame_candidates` generator directly in the candidate's live m061 states while
leaving candidate selection unchanged. For unit 2 throughout the P4 window 39--99,
the resident generator returns exactly one candidate, `WAIT`, on every probed turn.
The same result continues over later idle stretches. This directly establishes prong
(b): the candidate reaches a higher-scoring state in which the resident's own
generator contains the same hole. The pre-existing-hole exception applies, and the
case remains explicitly reported.

### m082 seat 1: named cost verified

The delivered WAIT-tail candidate scores 1 versus the floor's 12 and adds 184 D-1
turns plus 185 P4 turns. A freshly rebuilt variant differing only by the documented
three-line `fallback.len()==1` return to `endgame_candidates` scores 12 and has no
D-1 or P4 violation on this game. Instrumentation confirms that alternate return is
entered repeatedly on m082, while it is not entered on m061. The regression is
therefore the specified WAIT-tail interaction and is the one named cost accepted by
the owner; it is not averaged away or described as harmless.

## Gate disposition under the new law

- G1: **PASS** under explain-then-pass. The 311/311 fail-first and cure results,
  full-34 no-regression check, and both surprise mechanisms are independently
  verified.
- G2: **PASS under owner ruling**. Turn coverage is the governing metric. m106 is
  non-blocking because it adds zero stalled turns; m061 meets both prongs of the
  general pre-existing-hole rule; m082 is the explicitly accepted named cost.
- G3: **PASS**, unchanged: warm p95 0.065 ms and 240/240 row-identical parity.
- G4: **GREEN**.

This review does not mutate the resident and does not itself perform an Arena action.
It opens G5 exactly as the charter and owner policy direct: serialized submission by
the controller, unchanged candidate, with m082 and the new general measurement rules
carried into the record and paired night.
