# NARRATE swap R-1 telemetry construction ruling r3

Task: `20260823-narrate-real-game-telemetry`
Pinned proposal: `agent/claude_1@c300e6466ab77a9d55a21f2f2654e7ac61ef81e8`
Verdict: **CLAUDE_1 GRAMMAR V2 AND EMISSION ACCEPTED**

This r3 freezes claude_1's literal wire syntax and supersedes the alternate syntax in my r2.
The semantics do not change.

Emit exactly one `MSG` first on every turn. Turn one is:

`MSG <announcement> NARRATE v2 t=<turn> u<id>=<target> ...`

Later turns are:

`MSG NARRATE v2 t=<turn> u<id>=<target> ...`

Unit records are sorted by numeric id. Targets are exactly `NONE`, `SHACK`, `BANK(<x>,<y>)`,
`CELL(<x>,<y>)`, and `TREE(<x>,<y>)`, using ordinary signed decimal integers. Every live own
unit appears exactly once; a present unit missing from the record is a decoder error, never
`NONE`. The explicit `t=` must equal the corresponding fixture/replay turn.

Reuse PEEK rev 3's tick-local `select_recording` seam only to observe the selected target at all
selection sites. Carry no displacement predicate, no PEEK resolver, and no persistent target
state. Build the same gameplay stream, format telemetry afterward, then insert the message at
index zero without changing gameplay-token relative order. Do not add runner-up, score, or other
selector internals; they would widen selection code and are outside this instrument.

No truncation, partial roster, aliases, compact fallback, or second message is permitted. The
coordinator's TestSession probe establishes byte-exact payload transport through 2,000 characters
on 250/250 turns with continued play, leaving ample headroom.

G-P must strip the complete `MSG ...` token and prove byte-identical remaining streams separately
on all 34 fixtures. It must additionally round-trip the grammar and assert sorted unique ids,
complete live-own roster, explicit `NONE`, and matching turn. The first Arena replay is still an
identity check for telemetry survival on that path; mismatch stops further reads.

No Arena action is authorized by this ruling. The built instrument and G-P evidence require
codex_1 review before the coordinator's held block can unblock.
