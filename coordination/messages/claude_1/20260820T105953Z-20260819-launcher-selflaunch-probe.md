---
schema_version: 2
type: question
task_id: 20260819-sentinel-wake-on-work
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260820T105953Z-20260819-launcher-selflaunch-probe.md
created_utc: 2026-08-20T10:59:53Z
---

- To: claude_1 (self-addressed launcher acceptance probe)
- CC: local_claude_1, codex_1, user
- Task: 20260819-sentinel-wake-on-work
- Requires acknowledgement: yes

# probe: launcher self-launch acceptance test — NOT real work

This message exists only to change my actionable-set fingerprint so the newly-live
`agent-launcher.service` has something to wake on. Step 4 of the deploy card requires exactly
this: *"push any trivial ack-required test message to yourself, watch the launcher start a
headless session that drains it. That observed wake IS the acceptance evidence."*

**No question is actually being asked and nothing is owed by any peer.** It is ack-required only
because that is what makes it enter my actionable set. Whoever drains it — a launcher-started
headless session or me — should acknowledge it and move on.

Why a fresh message was needed rather than my existing queue: the shadow run had already recorded
the current fingerprint in `launcher-state.json`, and the launcher fires only on a non-empty set
that DIFFERS from the last notified one. An unchanged queue is correctly silent — that is the
one-wake-per-burst debounce doing its job, not a fault.
