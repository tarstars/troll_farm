# H-STARVE-1 Pool #3 incidence-revision review — 2026-08-17

Verdict: **GATE_ACCEPTED**. Pool #3 is closed; Pool #5 is authorized.

Pinned artifact: `fff7045bcc80a75efcb004222b71bd0e97d3cedc`.

## Accepted aggregation

The revision preserves every accepted per-turn attribution and replaces the lossy
plurality label with two explicit axes:

- non-exclusive cause incidence: `NO_GOAL_ASSIGNED` in 8 situations (521 WAIT
  turns), `GOAL_SPLIT_WRONG` in 24 (2,240), `CANNOT_USE_WORK` in 2 (349), and
  `WORLD_INTERACTION` in 0; and
- status: 29 `PARKED`, 4 `NOT_STARVED`, plus OSC-026 as the token-less
  `NO_ANCHOR_SINGLE_UNIT` coverage state.

I independently reran the table and WORLD_INTERACTION control. The committed JSON
was reproduced byte-for-byte. The explicit Pool #5 set is complete:
OSC-001, OSC-005, OSC-008, OSC-009, OSC-028, OSC-031, OSC-032, and OSC-033.

## Token-semantics ruling

The definitions in `cause_table.py` are accepted for this diagnostic table:

- `CANNOT_USE_WORK`: final WAIT on a turn where the accepted eligible-action oracle
  finds no reachable usable action for that unit;
- `NO_GOAL_ASSIGNED`: usable work exists, but the generator-stage candidate list is
  WAIT-only;
- `GOAL_SPLIT_WRONG`: usable work and a real selector-input candidate exist, but the
  joint selector emits WAIT for this unit;
- `WORLD_INTERACTION`: usable work and a real earlier command exist, but door clearing
  or conflict resolution produces the final WAIT; and
- `NOT_STARVED`: fewer than half of window turns are WAIT, reported only as status.

`GOAL_SPLIT_WRONG` is a frozen serialization for **where** the WAIT arose. It does not
establish that the joint-score choice was suboptimal, harmful, or curable. Likewise,
non-exclusive incidence is descriptive: a situation can and does exhibit multiple
causes.

## Gate consequence

Pool #5 may produce mechanism notes for all eight situations containing at least one
`NO_GOAL_ASSIGNED` turn, preserving mixed-cause counts. This authorizes diagnosis
only. No cure code, resident mutation, Arena action, or spec implementation is
authorized.
