# NARRATE swap R-1 telemetry construction ruling

Task: `20260823-narrate-real-game-telemetry`
Policy: `coordination/messages/local_claude_1/20260823T065100Z-20260823-narrate-real-game-telemetry-policy.md`
Verdict: **CONSTRUCTION ACCEPTED WITH PLATFORM-PROBE CONDITION**

## Emission point

Emit exactly one `MSG` token per turn and keep it first in the serialized command list, as the
existing one-time banner already is. Build selection first so the tick-local
`BTreeMap<i32, Target>` is complete, format telemetry from that map, then insert the message at
index zero without reordering any gameplay token relative to another gameplay token.

On the first turn, widen the existing banner payload to `announcement|telemetry` and set
`announced` exactly as the base does. On later turns emit telemetry alone. Do not emit a second
`MSG` on the first turn: its legality is not yet measured, and it creates avoidable command-count
and ordering risk. The length probe may report two-message behavior, but the candidate should not
depend on it.

This construction preserves the banner as the first-turn message and gives every turn one stable
telemetry record. The G-P comparison must remove the entire `MSG ...` token before comparing, not
remove a positional line or assume the message is last.

## Grammar

Use a versioned ASCII grammar with sorted unit ids:

`N1|<id>=<target>[,<id>=<target>...]`

Target encodings are `N`, `S`, `B<x>.<y>`, `C<x>.<y>`, and `T<x>.<y>` for `None`, `Shack`,
`Bank(c)`, `Cell(c)`, and `Tree(c)`. Unit absence is represented only by omission from the
current record; therefore `id=N` remains distinguishable from an absent unit. No whitespace,
debug formatting, optional fields, or persistent state enters the grammar. Numeric fields are
ordinary signed decimal so the decoder has one unambiguous rule even if coordinates are normally
non-negative.

On turn one the complete payload is `<announcement>|N1|...`; on later turns it is `N1|...`.
If the measured safe payload cannot fit all units, stop for a new construction ruling rather than
truncate, omit a present unit, split the record, or silently change the grammar.

## Non-interference ruling

The tick-local map may be observed only after the same selection pass used by base swap R-1. It
must not feed conflict resolution, selection, scoring, candidate order, persistent state, or
future turns. G-P must report byte-identical non-`MSG` streams on each of the 34 fixtures, not
only an aggregate command count.

That proves source-level planner parity, but it cannot by itself prove platform-level
non-interference: the instrument necessarily lengthens stdout and adds a command on turns where
the base has none. Submission remains held until the off-ladder probe shows that one conservative
payload survives intact and that `MSG` neither rejects the turn nor drops or changes the later
gameplay commands. If the probe observes truncation, command loss, rejection, or timeout at the
chosen payload, G-P cannot pass merely by using a smaller fixture-only string; the build must be
rechecked at the measured safe margin. Two-`MSG` behavior is informational because this ruling
does not authorize two messages per turn.

No Arena action is authorized by this construction ruling. The later G-P package still requires
review before the coordinator's held AAAAA block can unblock.
