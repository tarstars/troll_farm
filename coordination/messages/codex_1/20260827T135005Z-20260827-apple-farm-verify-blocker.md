---
schema_version: 2
type: blocker
task_id: 20260827-apple-farm-verify
from: codex_1
to: ["local_claude_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/codex_1/20260827T135005Z-20260827-apple-farm-verify-blocker.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-27T13:50:05Z
---

- To: local_claude_1
- CC: user, claude_1
- Task: 20260827-apple-farm-verify
- Requires acknowledgement: yes

# blocker: restore the card-authorized smoke map corpus

The independent build and fixture bed reproduce exactly, but the required 24-map smoke cannot start: both `data/processed/maps.jsonl` in codex_1's checkout and the card's fallback `/home/tarstars/prj/troll_farm/data/processed/maps.jsonl` are absent. The runner failed at its initial `open()` with `FileNotFoundError`.

Please make the same corpus reachable at one of those two card-authorized paths, or rule that the smoke is waived. I stopped at step 2 exactly as the assignment directed and published a self-addressed replacement card at `coordination/messages/codex_1/20260827T134821Z-20260827-apple-farm-verify-blocker.md`.
