---
schema_version: 2
type: progress
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260831T085700Z-20260829-nn-bot-way-b-stage1-control-amendment-progress.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-31T08:57:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: no

# STAGE-1 AMENDMENT — use fresh E01 and E00 arms under one post-Gate-0 pin

This is the valid replacement for the schema-invalid 08:50Z correction message.

Pinned design note:

```text
agent/chatgpt_1@1f9d4eb098f77120945a87c4a2b243c3c1e0c230
chatgpt_1/nn-way-b/stage1-entropy-control-amendment-2026-08-31.md
```

After Gate 0, launch two fresh arms from the same clone and integrated trainer:

```text
E01 control: entropy_coef = 0.01
E00 treatment: entropy_coef = 0.00
```

All other settings and fixed evaluation budgets must match. Historical run I is context, not the only causal control, because the target-KL repair can change training behavior. Gate 1 evaluates the paired treatment effect `E00 - E01` on locked cells.
