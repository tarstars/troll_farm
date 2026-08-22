---
schema_version: 2
type: <kind: claim|progress|question|blocker|policy|stop|takeover|ack|release|integrated|correction>
task_id: <task-id>
from: <agent-id>
to: <agent-id or user>
cc: []
message_id: coordination/messages/<agent-id>/<YYYYMMDDTHHMMSSZ>-<task-id>-<kind>.md
requires_ack: <true|false — MUST be false for progress, ack, release, integrated (protocol §4)>
ack_for: []
supersedes: []
created_utc: <YYYY-MM-DDTHH:MM:SSZ>
---

- To: <recipient>
- CC: <cc, or omit>
- Task: <task-id>
- Requires acknowledgement: <yes|no — must agree with requires_ack above>

# <kind>: <task-id>

<!--
The four bullets above are the MANDATORY legacy block (protocol §10.0). Do not delete
them. Every message must carry BOTH the v2 front matter and the legacy block, because
peers do not all run the same sweep version and a front-matter-only message is invisible
to an older reader. That is not hypothetical: one agent saw zero messages for ten days.

requires_ack above is a placeholder on purpose. It used to be hardcoded `true`, so
copying this template for a progress note manufactured a permanent, immutable
acknowledgement obligation that protocol §4 explicitly exempts. requires_ack() ORs the
flag with the kind, so the template's default silently overrode the protocol's exemption.
-->


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
