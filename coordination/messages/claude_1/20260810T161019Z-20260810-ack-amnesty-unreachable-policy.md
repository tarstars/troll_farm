---
schema_version: 2
type: policy
task_id: 20260810-ack-amnesty-unreachable
from: claude_1
to: ["user"]
cc: []
message_id: coordination/messages/claude_1/20260810T161019Z-20260810-ack-amnesty-unreachable-policy.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-10T16:10:19Z
---

- To: user
- CC: none
- Task: 20260810-ack-amnesty-unreachable
- Requires acknowledgement: no

# Ack amnesty for unreachable and dormant senders

Owner-approved 2026-08-10 as part of the control-plane spec's P0
(`docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md` §6).

Acknowledgement obligations for messages whose sender is on the roster's `unreachable`
or `dormant` lists (`chatgpt_1`, `chatgpt_2`, `local_codex_1`) are administratively
closed. No acks will be published for them; the messages remain immutable history.
The sweep's `unacknowledged` count and exit 1 are expected and documented until the
ack mechanism retires at migration step P2. No message content is suppressed, deleted,
or quarantined by this policy.
