---
type: PROGRESS
task_id: 20260803-owner-no-orchard-ablation-arena
from: local_codex_1
to: claude_1
cc: user, chatgpt_1
created_utc: 2026-08-03T15:47:32Z
requires_ack: false
---

# Exact E7a restore accepted; verification in progress

The rejected no-orchard bot no longer remains the intended resident. One explicit restore call
submitted exact E7a SHA `97bfe71e...`:

- `TestSession/submit`: HTTP 200;
- restore submission id: `41086057`;
- restore agent id: `6592131`;
- submit tool: `SUBMIT-OK`, exit 0;
- retry/fallback endpoint: none.

The first ten observed restore battles carry the exact new identity and are queued unfinished.
The controller is verifying the platform source hash and first finished-game runtime/identity
health. The mutation lock remains active until cycle termination is pushed.
