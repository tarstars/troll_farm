---
schema_version: 2
type: <kind: claim|progress|question|blocker|policy|stop|takeover|ack|release|integrated|correction>
task_id: <task-id>
from: <agent-id>
to: <agent-id or user>
cc: []
message_id: coordination/messages/<agent-id>/<YYYYMMDDTHHMMSSZ>-<task-id>-<kind>.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: <YYYY-MM-DDTHH:MM:SSZ>
---

# <kind>: <task-id>

<!--
v2 rules (coordination/multi-agent-protocol.md §4):
- message_id must equal the repository-relative path of this file; from must equal the
  sender namespace in that path.
- ack_for / supersedes are single-line JSON arrays of exact immutable message paths
  (parsed with json.loads) — never task ids or timestamps.
- an `ack` must list every path it covers in ack_for; it covers nothing not listed.
- a `correction` must list the superseded message path(s) in supersedes; the superseded
  message stays immutable and visible.
- for a handoff use templates/handoff.md instead.
- sweep exit codes: 0 healthy, 1 unacknowledged messages, 2 transport/schema/delivery
  error.
-->

- Branch: agent/<agent-id>
- Head: <full SHA>

## Summary
<What changed or what response is needed.>

## Evidence
- `<commit, command, measurement, or path>`

## Requested action
<Concrete next action, or none.>
