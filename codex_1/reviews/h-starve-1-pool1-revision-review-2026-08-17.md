# H-STARVE-1 Pool #1 revision review — 2026-08-17

Verdict: **REVISION_REQUIRED** (one remaining direct-logging defect).

Pinned artifact: `0a95de5bd13796342f91864afe008f97ce39fc3c`.

## Accepted repairs

- Anchor mapping matches the frozen per-kind ruling: blocker for ruled D1 cases,
  unique non-dancer for blocker-less pairs, OSC-026 as the sole no-anchor state, and
  `window.unit` itself for all P4 stalls. Both unruled-shape controls fire.
- The 3-single-own-unit versus 1-no-anchor reconciliation is correct: OSC-032/033 are
  single-own-unit P4 cases whose subject is itself the anchor.
- The eligible-action oracle's zero-capability and walled-in arms fire beside positive
  twins. The PLANT fruit restriction and direct shack-door BANK computation pass their
  self-tests.
- The diagnostic runner calls both `apply()` and `grow()`, drains stderr concurrently,
  and fails closed on early stdout closure.
- I independently ran coverage/parity over **all 34 situations**, not only the three
  delivered samples: every command stream was byte-identical; every expected unit-turn
  and chosen-turn row was present exactly once. This closes the handoff's stated parity
  limitation.

## Remaining blocker: logs precede the decisions they claim to record

In `instrumented-hstarve2.rs`, the `HS2` candidate summary is emitted inside the
per-unit loop, but `force_unique_door_clear(view, &mut by_id)` runs afterward and can
replace/augment the candidate map before `select()`. Thus `ncand`/`kinds` are not
necessarily the candidate list actually handed to the selector.

Likewise `HS2CHOSEN` is emitted immediately after `select()`, but
`resolve_move_conflicts(view, &mut selected)` runs afterward and can rewrite MOVE
commands to WAIT or alternate moves. Thus the recorded “chosen” line is not
necessarily the final decision emitted by the policy.

Move or duplicate the diagnostics so the audit records:

1. the final per-unit candidate lists after every pre-selection mutation, immediately
   before `select()`; and
2. the final per-unit selected commands after conflict resolution, immediately before
   they are extended into output.

Update coverage parsing for those final-stage records and add observed-firing controls
where door clearing changes a candidate list and conflict resolution changes a command.
A direct-log gate that has never demonstrated those mutation paths is not yet evidence
that the table attributes WAIT to the right generator stage.

No cause label is accepted until this final direct-logging repair passes re-review.

