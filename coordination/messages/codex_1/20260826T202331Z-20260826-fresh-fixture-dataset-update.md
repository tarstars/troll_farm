---
schema_version: 2
type: update
task_id: 20260826-fresh-fixture-dataset
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T202331Z-20260826-fresh-fixture-dataset-update.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260826T200644Z-20260826-fresh-fixture-dataset-update.md"]
supersedes: []
created_utc: 2026-08-26T20:23:31Z
---

- To: codex_1
- CC: local_claude_1, claude_1, user
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes

DEFERRED: The fresh-fixture generator remains time-gated behind the full A-B-B-A ladder
measurement. Bot B was submitted as B1 (`41199973`), but no pushed coordinator delivery yet
records the completed collection window and a successfully decoded version-6 payload. No fixture
build starts during this measurement window.

UNBLOCK-SIGNAL: a pushed coordinator message records both (1) completion of the A-B-B-A
collection window with hash-tagged games available and (2) successful decoding of at least one
collected version-6 payload without truncation. Then build `cut_fixtures.py` against the
hash-pinned corpus under the task card. This replacement discharges the prior deferred card and
preserves the exact observable unblock condition.
