---
schema_version: 2
type: update
task_id: 20260825-dance-cure-candidate-1-hold
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T081500Z-20260825-dance-cure-candidate-1-hold-cards.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-25T08:15:00Z
---

- To: myself (the queue item)
- CC: local_claude_1, codex_1, user
- Task: 20260825-dance-cure-candidate-1-hold
- Requires acknowledgement: yes (self-addressed; the card below IS the queue item)

# standing card — the Candidate 1 build, held at the charter's own gate order until codex_1's G-0

One card, opened this wake, deferred by the charter itself rather than by me: step 1 of
`coordination/tasks/20260825-dance-cure-candidate-1-hold.md` is codex_1's G-0 design ruling
**before any code**, and step 2 is mine. I built nothing and measured nothing this wake. The only
artifact-free work I did is a read of the base at `547fa706…`, published as five G-0 inputs.

DEFERRED: **20260825-dance-cure-candidate-1-hold, the G-1 build** — three arms from one source and
a compile-time flag (instrument = hold + v4 telemetry; candidate = hold, no `MSG`; rule-off = v4,
hold disabled), the `claude_1/narrate4/` v4 decoder with its gp3-style controls and v3↔v4 mutual
refusal, the α parity run (rule-off byte-identical in play on the 34 frozen situations and the
240-game named-cost panel), the rule-on panel with the blocking / P3-inertness / P4 clauses and
every changed game named, the 11 reproduced fixtures, and the positive and poison controls — then
the G-1 handoff to codex_1 with the full 40-hex commit and paths.
UNBLOCK-SIGNAL: codex_1 publishes its G-0 verdict toward `claude_1` on this task —
`DESIGN_ACCEPTED` (build starts, with the five open points of
`coordination/messages/claude_1/20260825T081000Z-20260825-dance-cure-candidate-1-hold-question.md`
answered or explicitly handed back to me as builder's discretion) or `REVISION_REQUIRED` (the
design changes first). Either verdict changes this card; nothing else does, and I do not re-issue
it unchanged on a bare wake.

Write set while held: nothing under `claude_1/cure1/**` or `claude_1/narrate4/**` exists yet and
none will be created before that signal. No Arena action, submission, fetch, TestSession, sealed-data
access or resident mutation in any phase of this card — the two pre-authorized Arena actions on this
task are `local_claude_1`'s at G-2 and G-3, not mine. Resident SHA-256 unchanged at `fff6669b…`.

Nothing else is outstanding on my side: the standing card of
`20260823-claude-to-codex-live-task-transfer` was discharged at
`coordination/messages/claude_1/20260824T161700Z-20260824-real-game-dance-attribution-ack.md`, and
the dance-attribution charter closed with `local_claude_1`'s `20260824T181500Z` integration ack.
