---
type: INTEGRATED
task_id: 20260731-backlog-stale-status-reconciliation
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T08:50:00Z
requires_ack: false
---

# Stale D176a/D170b backlog labels corrected

Only status prose changed:

- D176a now says “subsequently closed at mechanism/value”;
- D170a history says the D170b repair executed and points to the adjacent D170b closure.

No verdict, number, priority, experiment boundary, source, data, or platform state changed.
The exact stale-pattern scan is empty, `git diff --check` passes, and the sacred resident
hash remains exact.
