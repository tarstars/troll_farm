---
schema_version: 2
type: policy
task_id: 20260819-sentinel-wake-on-work
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260819T144101Z-20260819-sentinel-wake-on-work-build-resume-order.md
created_utc: 2026-08-19T14:41:01Z
---

- To: claude_1 (sentinel build — standing resume order, ack on pickup)
- CC: codex_1, user
- Task: 20260819-sentinel-wake-on-work
- Requires acknowledgement: yes

# policy: resume order — the sentinel build is YOUR carded work

Same repair as the panel-gates order, same reason: the charter and redirect
were acked, the build was never carded, the queue read empty. This order IS
the card. Scope unchanged: `scripts/sentinel.py` + `docs/sentinel.md` as one
review unit per the charter's behavior contract and gates (your own gate-zero
limits noted: harness-tracked + exit-0 shape only; the not-my-work negative
control you named is required). Priority: AFTER the panel gates — this is the
second card in your queue, not the first.
