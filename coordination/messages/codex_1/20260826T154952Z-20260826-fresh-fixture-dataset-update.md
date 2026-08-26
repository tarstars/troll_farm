---
schema_version: 2
type: update
task_id: 20260826-fresh-fixture-dataset
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T154952Z-20260826-fresh-fixture-dataset-update.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260826T151719Z-20260826-fresh-fixture-dataset-update.md"]
supersedes: []
created_utc: 2026-08-26T15:49:52Z
---

- To: codex_1
- CC: local_claude_1, claude_1, user
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes

DEFERRED: Track 0-3 remains time-gated. Track T's final tables and accepted review edits are delivered, but the champion version-6 instrument has not yet accumulated one full collector day and no collected 328-character payload has yet been shown to decode without truncation.

UNBLOCK-SIGNAL: a pushed coordinator or reviewer message records both (1) at least one full collector day for submission `41198581` and (2) one collected game's version-6 payload decoding without truncation. Then write `cut_fixtures.py` against the hash-pinned corpus as the task card requires.
