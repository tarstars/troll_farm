# H-STARVE-1 Pool #5 revision review — 2026-08-17

Verdict: **GATE_ACCEPTED**. Pool #5 is closed; the Pool #6 owner session is ready.

Pinned artifact: `46e16b0e31f3fda0db527c1e01a3a33a655bff8a`.

## Accepted revision

The revised mechanism artifact:

- retains all 521 accepted `NO_GOAL_ASSIGNED` stage attributions, including the 28
  turns where the resident's opponent-occupancy clause declines a plant;
- withdraws “oracle over-count,” “correct behavior,” “OSC-009 explained,” and “wrong
  scope” as unsupported judgments;
- describes the measured 325-turn finding neutrally as a deliberate phase-gate
  composition gap whose value/scope decision belongs to the owner; and
- runs parity, post-mutation-stage validation, and exact coverage before consuming
  each of the eight fresh diagnostic streams.

I independently reran `mechanism.py`. All eight streams passed the gates and the
committed JSON reproduced byte-for-byte.

## Accepted mechanism package

- 325 turns: at least one fruiting plant passes every clause of the resident's own
  harvest helper, but the mid-game empty-chop fall-through routes through
  `endgame_candidates` while the helper remains gated on the distinct top-level
  `endgame` flag.
- 28 turns: the resident's opponent-occupancy clause declines the harvest. These
  remain valid stage attributions; desirability is unruled.
- 1 OSC-005 turn: full capacity returns before the chop/endgame fall-through and
  `bank_candidates` is empty.
- 167 OSC-031 turns: chop is eligible under the reviewed oracle but every plant is
  rejected inside the chop generator. The specific clause remains unresolved and no
  proxy-based cause is asserted.

The totals reconcile exactly to 521. Nothing in this acceptance prices a cure or
declares either gate harmful. Owner preference for candidate C remains a preference,
not a ruling or implementation authorization.

The Pool #6/session materials must use the neutral accepted wording. The integrator's
discovery note was separately flagged as still containing the struck “wrong scope”
phrase; that record should be aligned before it is used in the session, but it does
not invalidate this artifact.

No cure code, resident mutation, Arena action, or spec implementation is authorized.
