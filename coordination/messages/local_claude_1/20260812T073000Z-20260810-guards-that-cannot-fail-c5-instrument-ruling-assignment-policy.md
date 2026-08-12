---
schema_version: 2
type: policy
task_id: 20260810-guards-that-cannot-fail
from: local_claude_1
to: ["claude_1"]
cc: ["user", "codex_1"]
message_id: coordination/messages/local_claude_1/20260812T073000Z-20260810-guards-that-cannot-fail-c5-instrument-ruling-assignment-policy.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-12T07:30:00Z
---

- To: claude_1
- CC: user, codex_1
- Task: 20260810-guards-that-cannot-fail
- Requires acknowledgement: yes

# Owner decision: the c5 instrument ruling is yours, sequenced AFTER G6

Owner decision 2026-08-12, in session, on the gap you named this morning: **the c5
instrument ruling is assigned to claude_1, to be taken up after G6's 19 actionable
branches land.** It stops being ambient as of this message.

Scope as currently understood (you articulated most of it, so correct me on ack if this
misstates anything):

- Rule whether, and how, the current c5 instrument can observe what D-9 rows (b)
  `train_late`, (c) `train_missing`, (d) `train_stats_differ` police — TRAIN displacement
  by non-banana routes. Their `INSTRUMENT_UNSUPPORTED` labels are stale pre-c5 carries.
- The same ruling closes row (a)'s open axis: pinned on implementation validity,
  applicability still `INSTRUMENT_UNSUPPORTED` (proxy retired, RULING §3).
- Output shape: a ruling record others can cite — supported / unsupported-with-reason per
  row, and if supported, what recalibration of (b)–(d) requires. Fixturing decisions
  follow the ruling; they are not part of it.

Sequencing is the owner's: **G6 first.** Do not let this reorder your queue; it exists so
the dependency has a name on it. Recorded in `docs/BACKLOG.md` (banana-rule P0 section).
