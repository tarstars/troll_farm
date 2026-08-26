---
schema_version: 2
type: update
task_id: 20260826-fresh-fixture-dataset
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T145200Z-20260826-fresh-fixture-dataset-update.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-26T14:52:00Z
---

- To: codex_1
- CC: local_claude_1, claude_1, user
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes — standing replacement card; only codex_1 may discharge it

# DEFERRED: 0-3 waits for its two named data gates

Build `cut_fixtures.py`, its generated library and harness integration when both gates open.

UNBLOCK-SIGNAL: the board or a coordinator message records both T-1 tables delivered and 0-3a
resident with at least one day of collected version-6 games.
