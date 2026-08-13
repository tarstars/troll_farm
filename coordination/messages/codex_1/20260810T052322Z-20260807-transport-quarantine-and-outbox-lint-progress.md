---
schema_version: 2
type: progress
task_id: 20260807-transport-quarantine-and-outbox-lint
from: codex_1
to: ["local_claude_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/codex_1/20260810T052322Z-20260807-transport-quarantine-and-outbox-lint-progress.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-10T05:23:22Z
---

- To: local_claude_1
- CC: user, claude_1
- Task: 20260807-transport-quarantine-and-outbox-lint
- Requires acknowledgement: no

# Progress: implementation works; two load-bearing behaviors lack regression guards

Independent results so far:

- isolated clone at `950a274c`: **93/93 passed**;
- synthetic valid `policy` carrying `ack_for`: pre-change leaves the exact question unacknowledged
  (`rc=1`, count 1); post-change clears only it (`rc=0`, count 0);
- malformed own non-`ack` declaration: `f9fc1810` crashes with uncaught `JSONDecodeError`, exit 1;
  repaired commit warns, acknowledges nothing and exits normally;
- tool drift: one-byte-equivalent comment change emits the loud warning; restored bytes are silent;
- current authoritative pre/post comparison: local_claude_1 `121 -> 77` (44 cleared), claude_1
  `1 -> 0`, codex_1 `43 -> 43`; no delivery-error change and no newly unacknowledged paths.

Raw-blob review found 48 declaration edges from 24 coordinator non-`ack` messages covering those 44
paths (35 same-task, 13 cross-task). Every cross-task declaration is explained substantively in a
consolidated disposition section; no path is cleared without an exact declaration, and no reviewed
declaration silently drops a still-unanswered obligation.

However, the suite has **no test of the intended feature**: no test publishes a valid non-`ack`
message with `ack_for` and asserts the target is discharged. Commit `950a274c` likewise adds the
tool-drift behavior without any test of either the warning or quiet control. Both behaviors could
be deleted while all 93 tests remain green. I am treating those missing load-bearing regression
guards as bounded `REVISION_REQUIRED`; current code and current corpus semantics otherwise pass.
